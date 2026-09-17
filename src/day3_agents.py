from src.agents import OrchestratorAgent


def print_trace(trace):
    print("\n")
    print("=" * 70)
    print("AGENT EXECUTION TRACE")
    print("=" * 70)

    for item in trace:

        iteration = item.get(
            "iteration",
            "",
        )

        phase = item.get(
            "phase",
            "",
        )

        agent = item.get(
            "agent",
            "",
        )

        message = item.get(
            "message",
            "",
        )

        if phase == "ACT":

            print(
                f"[Iteration {iteration}] "
                f"{phase} -> {agent}"
            )

        elif phase:

            print(
                f"[Iteration {iteration}] "
                f"{phase} -> {agent}: "
                f"{message}"
            )

        else:

            print(
                f"[Iteration {iteration}] "
                f"{agent}"
            )


def main():

    print("=" * 70)
    print("AIRPORT OPERATIONS AI COPILOT")
    print("DAY 3 - MULTI-AGENT SYSTEM")
    print("=" * 70)

    print(
        "Agents:"
    )

    print(
        "1. Orchestrator"
    )

    print(
        "2. Operations Investigator"
    )

    print(
        "3. Policy & Compliance Agent"
    )

    print(
        "4. Resolution Agent"
    )

    print(
        "ReAct iterations:",
        5,
    )

    print("=" * 70)

    print(
        "Type 'exit' or 'quit' to stop."
    )

    print("=" * 70)

    orchestrator = OrchestratorAgent()

    while True:

        try:

            user_query = input(
                "\nUSER: "
            ).strip()

        except (
            KeyboardInterrupt,
            EOFError,
        ):

            print(
                "\nExiting..."
            )

            break

        if not user_query:
            continue

        if user_query.lower() in {
            "exit",
            "quit",
        }:

            print(
                "Exiting..."
            )

            break

        print(
            "\nPROCESSING..."
        )

        print(
            "-" * 70
        )

        try:

            result = orchestrator.run(
                user_query
            )

            print(
                "\nFINAL ANSWER"
            )

            print(
                "-" * 70
            )

            print(
                result.get(
                    "answer",
                    "No answer generated.",
                )
            )

            trace = result.get(
                "trace",
                [],
            )

            if trace:

                print_trace(
                    trace
                )

        except Exception as e:

            print(
                "\nERROR:"
            )

            print(
                str(e)
            )


if __name__ == "__main__":
    main()
