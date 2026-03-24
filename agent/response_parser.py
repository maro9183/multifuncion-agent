import re

FILE_RE = re.compile(r"<<<FILE:(.*?)\n(.*?)\n<<<END_FILE", re.DOTALL)
CMD_RE = re.compile(r"<<<CMD\n(.*?)\n<<<END_CMD", re.DOTALL)
READ_RE = re.compile(r"<<<READ:(.*?)\n<<<END_READ", re.DOTALL)
LS_RE = re.compile(r"<<<LS:(.*?)\n<<<END_LS", re.DOTALL)


def extract_files(text):
    return [(a.strip(), b) for a, b in FILE_RE.findall(text)]


def extract_commands(text):
    return [a.strip() for a in CMD_RE.findall(text)]


def extract_reads(text):
    return [a.strip() for a in READ_RE.findall(text)]


def extract_ls(text):
    return [a.strip() for a in LS_RE.findall(text)]
