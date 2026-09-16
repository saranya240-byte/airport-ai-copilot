from src.function_calling import run_agent


def main():

    print("=" * 70)
    print("AIRPORT OPERATIONS AI COPILOT")
    print("=" * 70)
    print("Type your question below.")
    print("Type 'exit' or 'quit' to stop.")
    print("=" * 70)

    while True:

        user_question = input("\nUSER: ").strip()

        if user_question.lower() in ["exit", "quit"]:

            print("\nExiting Airport Operations AI Copilot.")
            break

        if not user_question:

            print("Please enter a question.")
            continue

        print("\nPROCESSING...")
        print("-" * 70)

        try:

            result = run_agent(user_question)

            print("\nFINAL ANSWER")
            print("-" * 70)

            print(
                result.get(
                    "answer",
                    "No answer returned."
                )
            )

            if result.get("tool_called"):

                print("\nTOOL EXECUTION")
                print("-" * 70)

                for tool in result.get("tools", []):

                    print(
                        "Tool:",
                        tool.get("tool_name")
                    )

                    print(
                        "Arguments:",
                        tool.get("arguments")
                    )

                    print(
                        "Result:",
                        tool.get("result")
                    )

        except Exception as e:

            print("\nERROR")
            print("-" * 70)

            print(
                f"Agent execution failed: {e}"
            )


if __name__ == "__main__":
    main()