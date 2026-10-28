# Terminal Helper

A lightweight, AI-powered command-line assistant that helps you understand Linux commands, troubleshoot problems, and learn your way around the terminal — without leaving the shell.

Terminal Helper sends your questions to [Ollama Cloud](https://ollama.com/) and streams the response directly into your terminal. It is designed to give practical, system-aware explanations, useful command examples, and clear warnings when an operation could modify or delete important data.

## Features

- **Command explanations** — understand what commands do, how to use them, and which flags matter.
- **Practical examples** — get commands for everyday tasks involving files, processes, networking, packages, permissions, and scripting.
- **System-aware answers** — includes your Linux distribution and shell information in the AI prompt to help tailor instructions to your environment.
- **Streaming responses** — see the answer as it arrives instead of waiting for the entire response.
- **Safety-conscious guidance** — emphasizes warnings for destructive operations, recursive permission changes, and other potentially risky actions.
- **Accuracy-focused prompts** — instructs the model to avoid inventing commands or flags and to suggest checking `man`, `--help`, or `tldr` when uncertain.
- **Simple shell integration** — ask questions using `say` directly from Bash.
- **Configurable model** — uses `gpt-oss:20b` by default, with support for selecting another model through an environment variable.

## Requirements

- Linux
- Python 3.12
- [uv](https://docs.astral.sh/uv/) for project setup
- Bash, if you want the `say` shell command
- An Ollama Cloud API key with access to your selected model

An internet connection is required to communicate with Ollama Cloud. Model availability, usage limits, and API access depend on your Ollama account.

## Installation

Clone the repository:

```bash
git clone https://github.com/hexinitz/terminal-helper-py.git
cd terminal-helper-py
```

Install the project environment and dependencies:

```bash
uv sync
```

## Configuration

Create a `.env` file in the project directory:

```bash
nano .env
```

Add your Ollama Cloud API key:

```dotenv
OLLAMA_API_TERMINAL=your_ollama_api_key
```

Replace `your_ollama_api_key` with your actual API key.

The application also recognizes `OLLAMA_API_KEY` as a fallback. The `OLLAMA_API_TERMINAL` variable takes precedence when both are set.

Keep your API key private. Do not commit your `.env` file or publish your credentials.

## Usage

### Run the assistant

From the project directory, ask a question using the installed project command:

```bash
uv run term-help "What does the find command do?"
```

More examples:

```bash
uv run term-help "How do I find files larger than 100 MB?"
uv run term-help "Explain grep with practical examples"
uv run term-help "How can I check which process is using a port?"
uv run term-help "Explain Linux file permissions"
```

You can ask general computing questions or request explanations of specific commands and their options.

### Use the `say` command in Bash

Terminal Helper includes a shell integration script that defines a `say` function.

Open your Bash configuration:

```bash
nano ~/.bashrc
```

Add the following line, replacing `/path/to/terminal-helper-py` with the actual absolute path to your cloned repository:

```bash
source /path/to/terminal-helper-py/term_help.sh
```

Reload your Bash configuration:

```bash
source ~/.bashrc
```

You can now ask questions directly:

```bash
say what does chmod do
say how do I find large files
say explain the difference between grep and ripgrep
say how can I check disk usage
```

The shell function forwards your question to the Python application. It does not execute the commands suggested by the AI.

## Model configuration

By default, Terminal Helper uses `gpt-oss:20b`.

To select a different model, set `OLLAMA_MODEL` in your environment before launching the application:

```bash
export OLLAMA_MODEL="your-model-name"
```

For example, to use the default model explicitly:

```bash
export OLLAMA_MODEL="gpt-oss:20b"
```

The selected model must be available to your Ollama Cloud account.

## How it works

1. You enter a question using `term-help` or `say`.
2. The application reads your question and loads API configuration from a `.env` file, if present.
3. It builds a request containing your question, system information, and instructions for generating accurate, practical terminal guidance.
4. The request is sent to the Ollama Cloud chat API.
5. The response is streamed to your terminal as it arrives.

The application uses Python's standard library for HTTP requests, JSON handling, environment access, and streaming. It does not require a separate Python HTTP client dependency.

## Project structure

```text
terminal-helper-py/
├── src/
│   └── term_help/       # Installable Python package
├── main.py              # Application entry point
├── term_help.sh         # Bash integration for the say command
├── pyproject.toml       # Project metadata and CLI entry point
├── uv.lock              # Locked project dependencies
├── .python-version      # Python version configuration
└── README.md
```

## Security and limitations

- Terminal Helper sends your questions to a cloud service. Do not include passwords, API keys, private keys, or other sensitive information in prompts.
- AI-generated commands can be incorrect or unsuitable for your system. Review commands before running them, particularly those involving `sudo`, deletion, formatting, or recursive changes.
- The assistant provides guidance; it does not automatically execute the commands it suggests.
- Answers depend on the selected model and may not always be accurate.
- Internet access and valid API credentials are required.

## Why I built this

This project is a practical exploration of Python, command-line tooling, API integration, and AI-assisted computing. The goal is to make terminal commands easier to understand and everyday Linux tasks easier to approach, while keeping the interface simple and entirely terminal-based.

## Author

**hexinitz**

GitHub: [@hexinitz](https://github.com/hexinitz)

## Contributing

Suggestions, bug reports, and improvements are welcome. Feel free to open an issue or submit a pull request.

---

*Built with Python and Ollama Cloud.*
