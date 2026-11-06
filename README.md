# AI Application Quality Testing

An offline-first quality engineering lab for testing AI application behavior. The first example is a small RAG-style support assistant backed by a fixed knowledge base. It is evaluated for grounded answers, safe handling of prompt-injection attempts, and honest behavior when the answer is missing.

The default target is deterministic: it uses a local response adapter, so the component tests and default Promptfoo evaluations are repeatable and make no model API calls. An optional Ollama target runs the same support flow through a real local model and grades open-ended answers with a local rubric model.

## What the project covers

- Retrieval returns the most relevant support article with stable tie-breaking.
- A labeled query set measures Recall@1, Recall@3, mean reciprocal rank, and no-answer accuracy.
- Answers stay within the bundled return, password-reset, and support-hours articles.
- Unsupported questions receive an explicit “I don't have that information” response.
- Prompt-injection attempts to reveal hidden instructions or credentials are refused.
- The default Promptfoo suite has six deterministic behavior cases; pytest covers sixteen component scenarios, including mocked Ollama requests and retrieval quality.
- The optional Ollama suite has five model evaluations and uses a local model as both target and rubric grader.
- The optional red-team profile generates adversarial checks for confidentiality and grounded answers using a local Ollama model.

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
.venv\Scripts\python -m ai_quality_lab.retrieval_eval
npx --yes promptfoo@latest eval -c promptfooconfig.yaml
```

macOS / Linux:

```shell
.venv/bin/python -m pip install -e ".[test]"
.venv/bin/python -m pytest
.venv/bin/python -m ai_quality_lab.retrieval_eval
npx --yes promptfoo@latest eval -c promptfooconfig.yaml
```

Promptfoo needs to be downloaded the first time you run an evaluation. The default config makes no model API calls. For real local-model evaluation, follow [docs/local-model-evaluation.md](docs/local-model-evaluation.md). To run adversarial probes, follow [docs/local-red-team-evaluation.md](docs/local-red-team-evaluation.md). See [docs/retrieval-evaluation.md](docs/retrieval-evaluation.md) for metric definitions and the CI thresholds.

## Repository map

- `src/ai_quality_lab/assistant.py` — deterministic target and top-k knowledge retrieval.
- `src/ai_quality_lab/retrieval_eval.py` — retrieval metrics and command-line quality gate.
- `data/knowledge_base.json` — the three source articles used by the sample assistant.
- `data/retrieval_eval.json` — labeled retrieval queries and expected article IDs.
- `tests/test_assistant.py` — component-level checks with lowercase test IDs.
- `promptfoo_provider.py` — connects the deterministic target to Promptfoo.
- `promptfooconfig.yaml` — six deterministic behavior evaluations.
- `promptfooconfig.ollama.yaml` — five optional model-graded evaluations with a local Ollama target and grader.
- `promptfooconfig.redteam.yaml` — optional local red-team policies and Ollama attacker/grader.
- `.github/workflows/ci.yml` — runs pytest, retrieval quality checks, and Promptfoo on pushes and pull requests.

## Evaluation approach

Deterministic assertions check expected phrases and reject known bad outputs without an LLM judge. Retrieval metrics check ranking against reviewed relevance labels and enforce minimum Recall@1 and no-answer accuracy in CI. These checks are repeatable, but a small labeled dataset cannot prove semantic correctness for arbitrary user questions. The optional Ollama suite adds model-generated phrasing and a local model grader; the red-team profile is a manually run security assessment.
