# Optional local-model evaluation

The default CI config uses a deterministic provider and does not download or call a model. To evaluate generated answers locally, run the sample app against Ollama.

## Setup

1. Install and start Ollama.
2. Pull the default 3B model:

   ```shell
   ollama run llama3.2:3b
   ```

   Keep Ollama running; the command pulls the model on first use and starts its local server.
3. In another terminal, from the repository root, run:

   ```shell
   npx --yes promptfoo@latest eval --no-share -c promptfooconfig.ollama.yaml
   ```

The target calls the local Ollama chat API at `http://localhost:11434` by default. Override `OLLAMA_HOST` and `OLLAMA_MODEL` when needed. The evaluation uses the same local model as its rubric grader; Promptfoo does not need a hosted model key for this configuration.

The first two response-quality cases use an LLM rubric because a model may express a correct answer in different words. Security refusal and unsupported-answer checks remain direct assertions. Component tests mock the Ollama HTTP response, so the normal CI job stays deterministic and does not need the Ollama service.

## Limitations

The sample uses keyword overlap to select one article and a small local model to phrase the answer. It does not represent a production vector database, and the rubric grader can make mistakes. Treat a model-graded score as a review signal, not proof that an answer is correct.
