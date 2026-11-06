# AI Application Quality Testing

An offline-first quality engineering lab for testing AI application behavior. The first example is a small RAG-style support assistant backed by a fixed knowledge base. It is evaluated for grounded answers, safe handling of prompt-injection attempts, and honest behavior when the answer is missing.

The default target is deterministic: it uses a small local response adapter rather than calling a hosted language model. This keeps the component tests and Promptfoo evaluations repeatable, free of API credentials, and suitable for CI. The example demonstrates the evaluation workflow; it does not claim to measure the semantic quality of a production LLM. A local or hosted model can be connected behind the same provider boundary in a later increment.

## What the first increment covers

- Retrieval returns the most relevant support article with stable tie-breaking.
- Answers stay within the bundled return, password-reset, and support-hours articles.
- Unsupported questions receive an explicit “I don't have that information” response.
- Prompt-injection attempts to reveal hidden instructions or credentials are refused.
- Promptfoo runs six behavior cases, while pytest covers six component scenarios.

## Prerequisites

- Python 3.12+
- Node.js 24+

## Run locally

Create and activate a virtual environment, then install the test extra:

```shell
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\python -m pip install -e ".[test]"
.venv\Scripts\python -m pytest
npx --yes promptfoo@latest eval -c promptfooconfig.yaml
```

macOS / Linux:

```shell
.venv/bin/python -m pip install -e ".[test]"
.venv/bin/python -m pytest
npx --yes promptfoo@latest eval -c promptfooconfig.yaml
```

Promptfoo needs to be downloaded the first time you run the evaluation. The evaluation itself uses the local provider and makes no model API calls.

## Repository map

- `src/ai_quality_lab/assistant.py` — deterministic target and knowledge retrieval.
- `data/knowledge_base.json` — the three source articles used by the sample assistant.
- `tests/test_assistant.py` — component-level checks with lowercase test IDs.
- `promptfoo_provider.py` — connects the target to Promptfoo.
- `promptfooconfig.yaml` — six behavioral evaluations.
- `.github/workflows/ci.yml` — runs pytest and Promptfoo on pushes and pull requests.

## Evaluation approach

Deterministic assertions check expected phrases and reject known bad outputs without an LLM judge. This is useful for repeatable regressions, but it does not prove semantic correctness for arbitrary model outputs. The next increment can add an optional real-model target and model-graded checks, while keeping the no-credential local path as the default.
