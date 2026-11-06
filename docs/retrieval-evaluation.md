# Retrieval quality evaluation

The retrieval evaluation uses a small labeled set in `data/retrieval_eval.json`. Each answerable question lists the article IDs that should be retrieved; unanswerable questions use an empty list.

Run it from the repository root after installing the project:

```shell
python -m pip install -e ".[test]"
python -m ai_quality_lab.retrieval_eval
```

The evaluator reports:

- **Recall@1** — the fraction of relevant articles ranked first.
- **Recall@3** — the fraction of relevant articles found in the top three candidates.
- **MRR** — mean reciprocal rank of the first relevant article.
- **No-answer accuracy** — the fraction of unanswerable questions for which retrieval returns no article.

The CI quality gate requires Recall@1 of at least 0.90 and no-answer accuracy of 1.00. The evaluation is deterministic and does not call Ollama or a hosted model. Update the labeled questions when the knowledge base changes, and review the relevance labels as part of that change.
