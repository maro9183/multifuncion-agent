from agent.orchestrator import Orchestrator


def main() -> None:
    agent = Orchestrator()
    print("Asistente Multifunción V3 iniciado. Escribí 'salir' para terminar.\n")

    while True:
        user_input = input("Vos: ").strip()
        if user_input.lower() in ["salir", "exit", "quit"]:
            print("Fin.")
            break

        if not user_input:
            continue

        response = agent.handle(user_input)
        print(f"\nAsistente:\n{response}\n")


if __name__ == "__main__":
    main()
