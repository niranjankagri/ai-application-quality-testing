# Retrieval quality evaluation

The retrieval evaluation uses a small labeled set in `data/retrieval_eval.json`. Each answerable question lists the article IDs that should be retrieved; unanswerable questions use an empty list.

Run it from the repository root after installing the project:

```shell
python -m pip install -e ".[test]"
python -m ai_quality_lab.retrieval_eval
```

Scoring is simple: a keyword scores 1, an anchor scores 2, and an article needs at least 2. An anchor is a word or phrase that is enough alone, such as `refund` or `log in`. A keyword isn't, so "return on investment" doesn't retrieve the returns policy. The questions `rq12` to `rq21` were added because the first version of retrieval failed most of them, and `rq22` and `rq23` guard two answers that an early version of this fix broke.

The evaluator reports:

- **Recall@1** — the fraction of relevant articles ranked first.
- **Recall@3** — the fraction of relevant articles found in the top three candidates.
- **MRR** — mean reciprocal rank of the first relevant article.
- **No-answer accuracy** — the fraction of unanswerable questions for which retrieval returns no article.

The CI quality gate requires Recall@1 of at least 0.90 and no-answer accuracy of 1.00. The evaluation is deterministic and does not call Ollama or a hosted model. Update the labeled questions when the knowledge base changes, and review the relevance labels as part of that change.

## Known limits

A score of 1.000 here doesn't mean retrieval is good: the labeled set was used to build the anchors. Fresh questions that were never used for tuning show the real level. Keyword matching can't see meaning, so these still fail:

| Question | Result | Why |
|---|---|---|
| How do I change the email on my account? | Password article | Two keywords match, on a different topic |
| What is the delivery window for my product? | Returns article | Three keywords match, on a different topic |
| Does the password manager app work on my phone? | Password article | One anchor is enough |
| Can I send this back? | No answer | No word from the returns article |
| Are you open on Saturday? | No answer | No word from the support article |

Adding each of these as an anchor would raise the score without improving retrieval. The real fix is meaning-based retrieval, such as embeddings, measured against this same set.
