"""Promptfoo adapter for the optional local Ollama-backed support assistant."""

import os

from ai_quality_lab.assistant import answer_with_ollama
from ai_quality_lab.redteam_regrade import REPLAY_FILE_VARIABLE, recorded_answer


def call_api(prompt, options, context):
    variables = (context or {}).get("vars", {})
    config = (options or {}).get("config", {})
    question = str(variables.get("question", prompt))
    # Second red-team grade: return the recorded answer, so only the grade can differ
    replay_file = os.environ.get(REPLAY_FILE_VARIABLE)
    if replay_file:
        try:
            return {"output": recorded_answer(replay_file, question)}
        except KeyError as missing:
            return {"error": str(missing)}
    output = answer_with_ollama(
        question,
        model=config.get("model"),
        host=config.get("host"),
    )
    return {"output": output}
