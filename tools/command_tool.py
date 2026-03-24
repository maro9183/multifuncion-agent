import subprocess

def status():
    return subprocess.run("git status", shell=True, capture_output=True, text=True).stdout
