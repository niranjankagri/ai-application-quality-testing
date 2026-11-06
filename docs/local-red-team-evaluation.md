# Optional local red-team evaluation

The red-team profile adds adversarial checks for the support assistant's confidentiality and knowledge-base boundaries. It uses Ollama as both the probe generator and the grader.

## Setup

1. Install Ollama and keep its local server running.
2. Pull the model used by the profile:

   ```shell
   ollama run llama3.2:3b
   ```

3. From the repository root, generate and run the red-team cases:

   ```shell
   PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION=true npx --yes promptfoo@latest redteam run -c promptfooconfig.redteam.yaml
   ```

On Windows PowerShell:

```powershell
$env:PROMPTFOO_DISABLE_REDTEAM_REMOTE_GENERATION = "true"
npx --yes promptfoo@latest redteam run -c promptfooconfig.redteam.yaml
```

The profile defines two custom policies: protect hidden instructions and credentials, and keep answers grounded in the bundled articles. Each policy generates three probes. Review generated probes and results as part of a manual security assessment.

## Limits

Local attack generation is convenient and keeps the configured red-team generation path local, but the attack quality depends on the model and can be lower than hosted generation. The local model grader can also miss or misclassify a violation. Treat results as findings to review, not a security certification. The red-team profile is optional and is not part of CI; CI remains deterministic and does not require Ollama.
