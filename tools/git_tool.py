import subprocess


def run_git(command, cwd=None):
    result = subprocess.run(
        f"git {command}",
        shell=True,
        capture_output=True,
        text=True,
        cwd=cwd
    )
    return result.returncode, result.stdout, result.stderr


def status(cwd=None):
    return run_git("status --short", cwd=cwd)


def branch(cwd=None):
    return run_git("branch --show-current", cwd=cwd)


def diff(cwd=None):
    return run_git("diff", cwd=cwd)


def add_all(cwd=None):
    return run_git("add .", cwd=cwd)


def commit(message, cwd=None):
    safe_message = message.replace('"', '\\"')
    return run_git(f'commit -m "{safe_message}"', cwd=cwd)
