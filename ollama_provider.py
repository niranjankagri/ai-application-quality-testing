"""Promptfoo adapter for the optional local Ollama-backed support assistant."""

from ai_quality_lab.assistant import answer_with_ollama


def call_api(prompt, options, context):
    variables = (context or {}).get("vars", {})
    config = (options or {}).get("config", {})
    question = str(variables.get("question", prompt))
    output = answer_with_ollama(
        question,
        model=config.get("model"),
        host=config.get("host"),
    )
    return {"output": output}
