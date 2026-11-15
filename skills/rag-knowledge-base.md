---
name: rag-knowledge-base
description: Build a retrieval-augmented knowledge base that actually answers correctly - ingestion, chunking, embeddings, hybrid search, reranking, citation, evaluation and drift monitoring.
version: 1.0.0
license: MIT
tags: [rag, ai, retrieval, embeddings, search, llm, evaluation]
---

# RAG Knowledge Base

Most "RAG is bad" complaints are chunking problems wearing a model costume. Fix retrieval and the answer quality follows.

## When to use this skill

- Answering questions over a private corpus: docs, tickets, contracts, policies, product manuals.
- Building an internal assistant, support bot or docs search.
- Adding citations to an LLM answer so it can be trusted.

Do NOT use for: tasks needing the whole document at once (summarise this 200-page report - use long context), or data that changes per second (query the API instead).

## Stage 1 - Corpus audit

1. **What is the source of truth** - which files, which system, who owns them?
2. **Volume** - number of documents, pages, tokens. Under ~2,000 pages, retrieval beats fine-tuning.
3. **Structure** - are documents prose, tables, FAQs, code, scanned PDFs? Each needs a different parser.
4. **Freshness** - how often does it change, and how will re-indexing trigger?
5. **Permissions** - does every user get every document? If not, filter at query time, never post-filter the answer.
6. **Question inventory** - collect 50 real questions people actually ask. This becomes your evaluation set before you write any code.

## Stage 2 - Ingestion and parsing

- PDFs: extract text with layout awareness; run OCR only on pages with under 50 characters of text. Tables need a dedicated extractor, not a text dump.
- Keep structure: headings become metadata, not just text. A chunk that knows it sits under "Refund policy > International" retrieves far better.
- Strip boilerplate: nav, footers, cookie banners, page numbers.
- Attach metadata to every chunk: `doc_id`, `title`, `section_path`, `url`, `updated_at`, `source_type`, `tenant`.
- Deduplicate near-identical documents (MinHash or embedding similarity > 0.95). Duplicates crowd the top-k and halve answer quality.

## Stage 3 - Chunking (spend your time here)

- **Semantic chunking on headings first**, then split long sections. 300-600 tokens with 10-15% overlap is a sane default.
- Never split a table, a code block, a numbered procedure or a single sentence across chunks.
- Prepend context to each chunk before embedding: `"{doc title} > {section} : {chunk text}"`. This one line is worth more than a model upgrade.
- Keep a `parent_id` so you can expand a retrieved chunk to its full section for the final answer.
- Store the raw text; embed a cleaned version. Never embed what you cannot display as a citation.

## Stage 4 - Retrieval

Use **hybrid search**, always:

1. **Dense** vector search (embeddings) for meaning.
2. **Sparse** BM25 for exact terms: SKUs, error codes, names, acronyms. Dense search fails on these and they are usually the query.
3. Fuse with reciprocal rank fusion.
4. **Rerank** the top 30-50 with a cross-encoder to the top 5-8. This is the single highest-value upgrade after chunking.
5. Apply metadata filters (tenant, date, doc type) *inside* the query, before ranking.

Vector store choice: pgvector if you already run Postgres (simplest, transactional, one backup story). A dedicated store only when scale or features demand it.

## Stage 5 - Answering

- Give the model the retrieved chunks with explicit `[1] [2]` markers and instruct it to cite them inline.
- Instruct: answer only from the provided context; if the context does not contain the answer, say so and suggest what to search. Do not guess.
- Include the section path and URL with each chunk so citations are clickable.
- Long answers: quote the decisive sentence, then paraphrase.
- Cap context at 6-8 chunks. More context measurably lowers accuracy and raises cost.

## Stage 6 - Evaluation (do this before tuning anything)

Build a 100-question set with the correct answer and the correct source document for each. Measure:

| Metric | Meaning | Target |
|---|---|---|
| Recall@k | correct doc in retrieved k | > 0.9 |
| MRR | how high the correct doc ranks | > 0.7 |
| Faithfulness | answer supported by context | > 0.95 |
| Answer correctness | matches the reference answer | > 0.85 |
| Refusal rate on unanswerable | correctly says "not in the docs" | > 0.9 |

Run it on every change. A prompt tweak that feels better but drops recall is a regression. Add every real failure to the set permanently.

## Stage 7 - Failure diagnosis table

| Symptom | Real cause | Fix |
|---|---|---|
| Answer ignores the right doc | Chunking split the fact | Semantic chunking, add context header |
| Retrieves similar but wrong topic | No reranking | Add cross-encoder rerank |
| Fails on part numbers, codes | Dense-only search | Add BM25 + RRF |
| Confident wrong answer | No refusal instruction | Grounding prompt + low-temperature + eval |
| Good answer, bad citation | Citation not tied to chunk id | Numbered chunks, require inline markers |
| Slow | Large k, no cache | Rerank fewer, cache embeddings and results |
| Different answer per user | Permission post-filtering | Filter inside the retrieval query |

## Stage 8 - Operations

- Re-index on source change (webhook or nightly diff), not on a timer that re-embeds everything.
- Log every query, retrieved ids, answer, citation clicks and thumbs. The clicks are the strongest signal you have.
- Monitor: retrieval latency, empty-result rate, refusal rate, thumbs-down clusters.
- Version the index and the prompt together; a rollback must restore both.
- Cost: cache embeddings by content hash, cache frequent answers with a short TTL.

## Quality checklist

- [ ] 50-question eval set built before coding
- [ ] Metadata on every chunk, filters applied pre-ranking
- [ ] Semantic chunks, tables and procedures never split
- [ ] Hybrid dense + BM25 with RRF and reranking
- [ ] Prompt forces citations and permits refusal
- [ ] Recall@5 above 0.9 on the eval set
- [ ] Permissions enforced inside retrieval
- [ ] Incremental re-index and query logging live

## Copy-ready agent prompt

> Read the skill at the URL above. Ask me for the corpus, the users and 50 real questions first. Then design the ingestion schema, the chunking strategy with context headers, hybrid retrieval with reranking, and the grounded answering prompt with inline citations and an explicit refusal path. Give me the eval script with recall@k, MRR and faithfulness, and run it against my sample set before you call it done.
