# Optional local-model evaluation

The default CI config uses a deterministic provider and does not download or call a model. To evaluate generated answers locally, run the sample app against Ollama.

## Setup

1. Install and start Ollama.
2. Pull the 3B assistant model and the 7B grader model:

   ```shell
   ollama pull qwen2.5:7b
   ollama run llama3.2:3b
   ```

   Keep Ollama running; the command pulls the model on first use and starts its local server.
3. In another terminal, from the repository root, run:

   ```shell
   npm ci
   npx promptfoo eval --no-share -c promptfooconfig.ollama.yaml
   ```

The target calls the local Ollama chat API at `http://localhost:11434` by default. The assistant uses `llama3.2:3b` and `qwen2.5:7b` grades its answers. The 3B model was not a reliable grader: it failed correct answers (TC-302 on every run, all six red-team answers on 18 Nov). To change either model, update the target model in `promptfooconfig.ollama.yaml` or the grader in `defaultTest.options.provider.text.id`. Promptfoo does not need a hosted model key for this configuration.

Two response-quality cases (`TC-301` and `TC-305`) use an LLM rubric because a model may express a correct answer in different words. `TC-302` checks for "Forgot password" and "30 minutes" directly: the small local grader failed its correct answer on every run, so the rubric was testing the grader, not the assistant. `TC-306` asks about returns, password reset and support hours in one question and checks for each fact directly. Security refusal and unsupported-answer checks remain direct assertions. Component tests mock the Ollama HTTP response, so the required CI job stays deterministic and does not need the Ollama service. The `model-evals.yml` workflow runs this suite weekly on GitHub, outside the required check.

## Limitations

The sample uses keyword overlap to select articles and a small local model to phrase the answer. The model path sends every article that reaches the retrieval score (up to three), so a question with several parts gets each fact; with only the top article, the 18 Nov red team showed the model calling the other facts "not specified". The deterministic `answer()` baseline still returns the top article only. It does not represent a production vector database, and the rubric grader can make mistakes. Treat a model-graded score as a review signal, not proof that an answer is correct.
