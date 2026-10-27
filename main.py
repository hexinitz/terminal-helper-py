#!/usr/bin/env python3
"""One-shot terminal help: term_help.py <question words...>

Sends the question to a single Ollama cloud model and streams back a short
plain-text answer. No chat history, no extra dependencies.
"""

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

HOST = "https://ollama.com"
MODEL = os.environ.get("OLLAMA_MODEL", "gpt-oss:20b")
TIMEOUT = 60
ATTEMPTS = 2
RETRY_CODES = {408, 429, 500, 502, 503, 504}

# Low temperature + narrow sampling keeps answers factual and repeatable.
# num_predict also covers the model's hidden reasoning, so don't set it too low.
OPTIONS = {
    "temperature": 0.3,
    "top_p": 0.85,
    "top_k": 30,
    "num_predict": 1500,
}

PROMPT = """\
You are a command-line teacher and help tool. System: {os_name}. Shell: {shell}.

Scope: the terminal, shell, Linux, command-line tools, and general computing questions (system, files, processes, networking, packages, scripting, permissions, how things work). If a question is clearly unrelated to computing, reply only: "I only answer terminal and computing questions."

Output format: plain text only. No markdown, no ** or #, no tables. Use the section labels below as plain lines. Put commands and flags indented by two spaces.

If the user asks about a specific command or tool, answer in this order:
What it does: one or two sentences.
Common uses: the 2 to 4 most practical uses, each with a real example command.
Common flags: the 4 to 8 flags people use most, one per line as "  -x   meaning".
Precautions: only real pitfalls (data loss, permissions, needing sudo, behaviour that surprises people). Skip this section if there are none.

If the user asks a general question (how something works, how to do a task, what a concept means), answer directly: the short explanation first, then the command(s) to do it with a line on what each part does. Use only as many lines as the answer needs.

Accuracy rules:
- State only what you are sure of. Never invent commands, flags, options, packages or file paths.
- Do not list a flag unless you are certain it exists and does what you say. A shorter correct list beats a longer doubtful one.
- If you are not sure about something, say "Not sure about this part." and tell the user how to check (man, --help, tldr).
- Behaviour differs between tools (GNU vs BSD, versions). If it matters, say so in one line.
- Give commands that work on this system. Use its own package manager for installs.
- If the question is too vague to answer well, ask one short question instead of guessing.
- Warn clearly before anything that deletes, overwrites, formats or changes permissions or ownership recursively.

Style: no greetings, no repeating the question, no closing remarks, no filler. Keep it compact but complete.
"""


def load_env():
    """Read KEY=VALUE lines from a .env next to this script or in the current folder."""
    for folder in (Path(__file__).resolve().parent, Path.cwd()):
        try:
            lines = (folder / ".env").read_text(encoding="utf-8").splitlines()
        except OSError:
            continue
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, _, value = line.partition("=")
            name = name.strip().removeprefix("export ").strip()
            os.environ.setdefault(name, value.strip().strip("\"'"))


def os_name():
    try:
        for line in Path("/etc/os-release").read_text().splitlines():
            if line.startswith("PRETTY_NAME="):
                return line.partition("=")[2].strip("\"'")
    except OSError:
        pass
    return "Linux"


def build_request(key, question):
    body = {
        "model": MODEL,
        "stream": True,
        # gpt-oss can't switch reasoning off, only lower it; other models can.
        "think": "low" if MODEL.startswith("gpt-oss") else False,
        "options": OPTIONS,
        "messages": [
            {
                "role": "system",
                "content": PROMPT.format(
                    os_name=os_name(),
                    shell=Path(os.environ.get("SHELL", "bash")).name,
                ),
            },
            {"role": "user", "content": question},
        ],
    }
    return urllib.request.Request(
        f"{HOST}/api/chat",
        data=json.dumps(body).encode(),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {key}",
        },
        method="POST",
    )


def pieces(req):
    """Yield answer text as it streams in."""
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        for raw in resp:
            raw = raw.strip()
            if not raw:
                continue
            chunk = json.loads(raw)
            if chunk.get("error"):
                raise RuntimeError(chunk["error"])
            text = (chunk.get("message") or {}).get("content")
            if text:
                yield text
            if chunk.get("done"):
                return


def retryable(exc):
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code in RETRY_CODES
    return isinstance(exc, OSError)  # timeouts, dropped connections


def explain(exc):
    if isinstance(exc, urllib.error.HTTPError):
        if exc.code in (401, 403):
            return "Auth failed. Check OLLAMA_API_TERMINAL in your .env file."
        if exc.code == 404:
            return f"Model '{MODEL}' not found."
        if exc.code == 429:
            return "Rate or usage limit reached. Try again later."
        return f"Server error {exc.code}."
    if isinstance(exc, TimeoutError):
        return "Request timed out."
    if isinstance(exc, OSError):
        return "Can't reach ollama.com. Check your connection."
    return str(exc) or type(exc).__name__


def main():
    question = " ".join(sys.argv[1:]).strip()
    if not question:
        print("usage: say <your question>", file=sys.stderr)
        return 2

    load_env()
    key = os.environ.get("OLLAMA_API_TERMINAL") or os.environ.get("OLLAMA_API_KEY")
    if not key:
        print(
            "No API key. Put OLLAMA_API_TERMINAL=your_key in a .env next to term_help.py.",
            file=sys.stderr,
        )
        return 1

    req = build_request(key.strip(), question)
    show_status = sys.stderr.isatty()
    printed = False
    last = ""

    if show_status:
        sys.stderr.write("\033[2m...\033[0m")
        sys.stderr.flush()

    try:
        for attempt in range(1, ATTEMPTS + 1):
            try:
                for text in pieces(req):
                    if not printed:
                        if show_status:
                            sys.stderr.write("\r\033[K")
                            sys.stderr.flush()
                        text = text.lstrip()
                        if not text:
                            continue
                        printed = True
                    sys.stdout.write(text)
                    sys.stdout.flush()
                    last = text
                break
            except (OSError, RuntimeError, ValueError) as exc:
                if not printed and attempt < ATTEMPTS and retryable(exc):
                    time.sleep(1.5)
                    continue
                if show_status:
                    sys.stderr.write("\r\033[K")
                print(explain(exc), file=sys.stderr)
                return 1
    except KeyboardInterrupt:
        if show_status:
            sys.stderr.write("\r\033[K")
        if printed:
            print()
        return 130

    if not printed:
        if show_status:
            sys.stderr.write("\r\033[K")
        print("Empty reply. Try rephrasing.", file=sys.stderr)
        return 1
    if not last.endswith("\n"):
        print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
