from google import genai
from config.settings import GEMINI_API_KEY, MODEL_NAME, WORKSPACE, PROJECT_ROOT
from tools.git_tool import status as git_status, branch as git_branch, diff as git_diff, add_all as git_add_all, commit as git_commit
from agent.response_parser import (
    extract_files,
    extract_commands,
    extract_reads,
    extract_ls,
)
from tools.filesystem_tool import create_file, read_file, list_dir
from tools.command_tool import run, is_allowed, is_dangerous


SYSTEM_PROMPT = f"""
Sos un asistente de desarrollo que trabaja dentro de este workspace:

{WORKSPACE}

Podés responder normalmente, pero cuando necesites acciones usá estos bloques exactos:

Crear archivos:
<<<FILE:relative/path.ext
contenido
<<<END_FILE

Leer archivos:
<<<READ:relative/path.ext
<<<END_READ

Listar carpetas:
<<<LS:relative/path-or-dot
<<<END_LS

Proponer comandos:
<<<CMD
comando
<<<END_CMD

Reglas:
- Siempre explicá primero qué vas a hacer.
- Nunca uses rutas absolutas.
- Si necesitás contexto antes de modificar, pedí READ o LS.
- Preferí soluciones mínimas pero ejecutables.
"""


class Orchestrator:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ValueError("Falta GEMINI_API_KEY")

        self.plan_mode = False

        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.chat = self.client.chats.create(
            model=MODEL_NAME,
            config={"system_instruction": SYSTEM_PROMPT}
        )

    def handle(self, user_input):
        if user_input.strip().lower() == "/plan on":
            self.plan_mode = True
            return "Modo plan activado."

        if user_input.strip().lower() == "/plan off":
            self.plan_mode = False
            return "Modo plan desactivado."

        if user_input.strip().lower() == "/status":
            return f"plan_mode={self.plan_mode}"


        if user_input.strip().lower() == "/git status":
            code, out, err = git_status(cwd=PROJECT_ROOT)
            return out if out else err

        if user_input.strip().lower() == "/git branch":
            code, out, err = git_branch(cwd=PROJECT_ROOT)
            return out if out else err

        if user_input.strip().lower() == "/git diff":
            code, out, err = git_diff(cwd=PROJECT_ROOT)
            return out if out else err

        if user_input.strip().lower() == "/git add":
            code, out, err = git_add_all(cwd=PROJECT_ROOT)
            return out if out else err if err else "git add ejecutado"

        if user_input.strip().lower().startswith("/git commit "):
            message = user_input.strip()[12:]
            code, out, err = git_commit(message, cwd=PROJECT_ROOT)
            return out if out else err if err else "commit realizado"


        response = self.chat.send_message(user_input)
        text = response.text or ""

        # Leer archivos solicitados
        reads = extract_reads(text)
        read_outputs = []
        for path in reads:
            try:
                content = read_file(WORKSPACE, path)
                read_outputs.append(f"READ {path}:\n{content}")
            except Exception as e:
                read_outputs.append(f"READ {path} ERROR: {e}")

        # Listar carpetas solicitadas
        listings = extract_ls(text)
        ls_outputs = []
        for path in listings:
            try:
                items = list_dir(WORKSPACE, path)
                ls_outputs.append(f"LS {path}:\n" + "\n".join(items))
            except Exception as e:
                ls_outputs.append(f"LS {path} ERROR: {e}")

        # Aplicar archivos
        files = extract_files(text)
        file_outputs = []
        for filename, content in files:
            try:
                path = create_file(WORKSPACE, filename, content)
                file_outputs.append(f"Archivo creado/modificado: {path}")
            except Exception as e:
                file_outputs.append(f"ERROR creando {filename}: {e}")

        # Ejecutar comandos
        command_outputs = []
        commands = extract_commands(text)
        for cmd in commands:
            if self.plan_mode:
                command_outputs.append(f"[PLAN MODE] No ejecutado:\n{cmd}")
                continue

            if is_dangerous(cmd):
                command_outputs.append(f"[BLOQUEADO peligroso]\n{cmd}")
                continue

            if not is_allowed(cmd):
                command_outputs.append(f"[BLOQUEADO fuera de whitelist]\n{cmd}")
                continue

            confirm = input(f"¿Ejecutar este comando?\n{cmd}\n[s/n]: ").strip().lower()
            if confirm not in ["s", "si", "y", "yes"]:
                command_outputs.append(f"[Omitido]\n{cmd}")
                continue

            code, out, err = run(cmd, cwd=WORKSPACE)
            command_outputs.append(
                f"[EXIT {code}]\nCMD: {cmd}\nSTDOUT:\n{out}\nSTDERR:\n{err}"
            )

        visible_parts = [text]

        if read_outputs:
            visible_parts.append("\n".join(read_outputs))

        if ls_outputs:
            visible_parts.append("\n".join(ls_outputs))

        if file_outputs:
            visible_parts.append("\n".join(file_outputs))

        if command_outputs:
            visible_parts.append("\n".join(command_outputs))

        return "\n\n".join(part for part in visible_parts if part.strip())
