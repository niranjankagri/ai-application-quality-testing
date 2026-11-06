# AI Application Quality Testing

A hands-on quality engineering lab for testing AI application behavior. The first example is a small support assistant backed by a fixed knowledge base, evaluated for grounded answers, safe handling of prompt-injection attempts, and honest behavior when the answer is missing.

The repository is designed to make evaluation repeatable and reviewable. Its default checks use a deterministic local provider, so contributors can run the suite and CI without model credentials or inference costs. The provider boundary can later be connected to a real local or hosted model.

## Planned test layers

- **Component checks:** retrieval and response behavior for the sample assistant.
- **Behavior evaluations:** Promptfoo cases for expected answers, unsupported claims, and adversarial inputs.
- **CI quality gate:** run the unit checks and behavior evaluations on every pull request.

## Local setup

The implementation will document the exact Python and Node.js versions, install steps, and commands when the first runnable evaluation harness is added.

## Project principles

- Keep default evaluation deterministic and inexpensive.
- Make each case traceable from a test ID to its expected behavior.
- Treat security and refusal behavior as testable requirements.
- Keep model integration optional so a contributor can start without secrets or paid APIs.
