#!/usr/bin/env bash
# term_help.sh - adds the `say` command to your shell (runs main.py in the same folder).
#
# Setup: add this line to ~/.bashrc, then open a new terminal:
#   source /path/to/term_help.sh
#
# Usage:
#   say what is the use of help command
#   say how do i find files bigger than 100M

_term_help_dir="$(dirname "$(readlink -f "${BASH_SOURCE[0]}")")"
TERM_HELP_PY="${TERM_HELP_PY:-$_term_help_dir/main.py}"
unset _term_help_dir

say() {
    if [ "$#" -eq 0 ]; then
        echo "usage: say <your question>" >&2
        return 2
    fi
    if [ ! -f "$TERM_HELP_PY" ]; then
        echo "say: can't find $TERM_HELP_PY" >&2
        return 1
    fi
    python3 "$TERM_HELP_PY" "$@"
}

# Also works when run directly (e.g. symlinked as ~/.local/bin/say)
if [ "${BASH_SOURCE[0]}" = "$0" ]; then
    say "$@"
fi
