import shlex
import subprocess
from pathlib import Path

ALLOWED_PREFIXES = {
    "python", "python3", "pip", "php", "node", "npm", "npx",
    "git", "ls", "cat", "pwd", "mkdir", "cp", "mv", "find",
    "grep", "sed", "touch"
}

DANGEROUS_PATTERNS = [
    "rm -rf /",
    "rm -rf *",
    "shutdown",
    "reboot",
    "mkfs",
    "dd if=",
]


def is_dangerous(command):
    c = command.lower().strip()
    return any(p in c for p in DANGEROUS_PATTERNS)


def is_allowed(command):
    if not command.strip():
        return False

    try:
        first = shlex.split(command)[0]
    except Exception:
        first = command.split()[0]

    return Path(first).name.lower() in ALLOWED_PREFIXES


def run(command, cwd=None):
    result = subprocess.run(
        command,
        shell=True,
        capture_output=True,
        text=True,
        cwd=cwd
    )
    return result.returncode, result.stdout, result.stderr
