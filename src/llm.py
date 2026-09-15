import json

from langchain_ollama import ChatOllama


# --------------------------------------------------
# Ollama Configuration
# --------------------------------------------------

MODEL_NAME = "llama3.2"


# --------------------------------------------------
# Create Ollama LLM
# --------------------------------------------------

llm = ChatOllama(
    model=MODEL_NAME,
    temperature=0,
    format="json"
)


# --------------------------------------------------
# Generate Answer Using RAG Context
# --------------------------------------------------

def generate_answer(question, context):

    prompt = f"""
You are an Airport Operations Policy Analyst.

Your job is to answer the user's question using ONLY the
retrieved airport policy context.

IMPORTANT RULES:

1. The POLICY CONTEXT is the only source of truth.
2. Do NOT use your general knowledge.
3. Do NOT say that you cannot verify something when the
   answer is explicitly present in the POLICY CONTEXT.
4. Find the answer directly from the POLICY CONTEXT.
5. Do NOT invent any policy.
6. Do NOT change any policy value.
7. Always identify the policy document used as the source.
8. The answer must be concise.
9. Return ONLY valid JSON.
10. Do not return Markdown.
11. Do not return ```json.
12. Do not add explanations outside the JSON.

==================================================
POLICY CONTEXT
==================================================

{context}

==================================================
USER QUESTION
==================================================

{question}

==================================================
REQUIRED JSON FORMAT
==================================================

Return exactly these four fields:

{{
    "answer": "direct answer based only on the policy context",
    "policy_reasoning": "brief explanation of the policy rule",
    "source": "policy document name",
    "grounded": true
}}

==================================================
IMPORTANT EXAMPLE
==================================================

If the context says:

"The maximum permitted surge multiplier at SFO is 1.5x."

and the question is:

"What is the maximum surge multiplier allowed at SFO?"

you MUST return:

{{
    "answer": "The maximum permitted surge multiplier at SFO is 1.5x.",
    "policy_reasoning": "The SFO pricing policy defines 1.5x as the maximum permitted surge multiplier.",
    "source": "sfo_pricing.md",
    "grounded": true
}}

==================================================
IF THE ANSWER IS NOT IN THE CONTEXT
==================================================

Only when the POLICY CONTEXT genuinely does not contain
the answer, return:

{{
    "answer": "The available policy documents do not provide enough information.",
    "policy_reasoning": "The retrieved policy context does not contain the required information.",
    "source": "Unknown",
    "grounded": false
}}

Now answer the USER QUESTION using ONLY the POLICY CONTEXT.
"""


    # --------------------------------------------------
    # Send Prompt to Ollama
    # --------------------------------------------------

    print("\nPROMPT SENT TO OLLAMA")
    print("=" * 60)
    print(prompt)

    response = llm.invoke(prompt)

    response_text = response.content.strip()


    # --------------------------------------------------
    # Display Raw Response
    # --------------------------------------------------

    print("\nRAW OLLAMA RESPONSE")
    print("=" * 60)
    print(response_text)


    # --------------------------------------------------
    # Parse JSON Response
    # --------------------------------------------------

    try:

        answer = json.loads(response_text)

    except json.JSONDecodeError:

        # Remove Markdown code fences if the model
        # accidentally returns them.

        cleaned_response = (
            response_text
            .replace("```json", "")
            .replace("```JSON", "")
            .replace("```", "")
            .strip()
        )

        try:

            answer = json.loads(
                cleaned_response
            )

        except json.JSONDecodeError:

            return {
                "answer": response_text,
                "policy_reasoning": (
                    "Ollama did not return valid JSON."
                ),
                "source": "Unknown",
                "grounded": False
            }


    # --------------------------------------------------
    # Validate Required Fields
    # --------------------------------------------------

    required_fields = [
        "answer",
        "policy_reasoning",
        "source",
        "grounded"
    ]

    for field in required_fields:

        if field not in answer:

            return {
                "answer": answer.get(
                    "answer",
                    "Invalid response from Ollama."
                ),
                "policy_reasoning": answer.get(
                    "policy_reasoning",
                    "Required field missing."
                ),
                "source": answer.get(
                    "source",
                    "Unknown"
                ),
                "grounded": False
            }


    # --------------------------------------------------
    # Return Final Structured Answer
    # --------------------------------------------------

    return {
        "answer": answer["answer"],
        "policy_reasoning": answer["policy_reasoning"],
        "source": answer["source"],
        "grounded": bool(answer["grounded"])
    }