from pathlib import Path


def safe_path(base_path, relative_path):
    base = Path(base_path).resolve()
    target = (base / relative_path.strip()).resolve()

    if not str(target).startswith(str(base)):
        raise ValueError(f"Ruta fuera del workspace: {relative_path}")

    return target


def create_file(base_path, relative_path, content):
    path = safe_path(base_path, relative_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path)


def read_file(base_path, relative_path):
    path = safe_path(base_path, relative_path)
    if not path.exists():
        return f"[no existe] {relative_path}"
    return path.read_text(encoding="utf-8")


def list_dir(base_path, relative_path="."):
    path = safe_path(base_path, relative_path)
    if not path.exists():
        return [f"[no existe] {relative_path}"]
    if path.is_file():
        return [f"[es archivo] {relative_path}"]

    items = []
    for child in sorted(path.iterdir()):
        suffix = "/" if child.is_dir() else ""
        items.append(str(child.relative_to(base_path)) + suffix)
    return items
