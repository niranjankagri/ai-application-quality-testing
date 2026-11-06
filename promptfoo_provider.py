"""Promptfoo adapter for the deterministic local support assistant."""

from ai_quality_lab.assistant import answer


def call_api(prompt, options, context):
    variables = (context or {}).get("vars", {})
    question = str(variables.get("question", prompt))
    return {"output": answer(question)}
