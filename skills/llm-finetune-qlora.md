---
name: llm-finetune-qlora
description: Fine-tune a 7B-8B model on one 24 GB GPU with QLoRA - dataset construction, split hygiene, baseline eval, training config, merge and quantised export, serving, and a rollback path.
version: 1.0.0
license: MIT
tags: [ai, fine-tuning, qlora, gpu, training, inference]
---

# LLM Fine-Tune With QLoRA

Fine-tuning is the right answer to exactly one question: the model must behave in a way a prompt cannot hold - a fixed output dialect, a domain vocabulary of hundreds of terms, or a tone that has to survive every input. For knowledge, use retrieval. For format, use a schema.

You finish with an adapter trained on one 24 GB GPU, a before/after win rate on a held-out set, a merged quantised model you can serve, and a documented rollback.

## When to use this skill

- The prompt is 2,000 tokens of style rules and still drifts on 20% of outputs.
- Output must match a house format exactly, on thousands of items a day.
- You need a small model to match a large one on one narrow task, to cut cost or latency.
- Domain vocabulary is unusual (legal, medical, Indic-language transliteration) and the base model mangles it.

Do NOT use for: adding fresh facts (use retrieval), teaching a model a new skill it has no basis for (use a bigger model), or when you have under 300 good examples - write more data first.

## Stage 1 - Decide whether fine-tuning is the right tool

1.1 Write the failure you are fixing as one sentence with a rate: "the model produces the wrong date format on 18% of invoices".

1.2 Run the decision table before spending a rupee on GPU time:

| Symptom | Right tool | Why |
|---|---|---|
| Missing facts | Retrieval | Facts change; weights are frozen at training time |
| Wrong output shape | Schema-constrained decoding | Cheaper and exact |
| Wrong tone on 20% of outputs | Fine-tune | Style is hard to hold with instructions |
| Too slow or too costly | Distillation fine-tune | Small model learns one task |
| Multi-step reasoning gaps | Bigger model | Fine-tuning rarely adds reasoning |
| Rare domain tokens | Fine-tune or tokeniser extension | Base vocabulary may not cover it |

1.3 Estimate the ceiling honestly: a 7B fine-tuned on one task can match a 70B on that task and will lose badly off-task. Plan for a router, not a replacement.

1.4 Check the tokeniser covers your domain: count how many of your 200 most important terms split into 4 or more tokens. Above 30% and you should consider a vocabulary extension before training.

1.5 Cost the run before you rent anything. At a typical rented 24 GB GPU rate, a 3-epoch run over 1,000 examples at 2,048 tokens is 4-8 GPU hours; multiply by your hourly rate and add 30% for failed runs and eval passes.

1.6 Compare the fine-tune against the two alternatives on the same 150-item test set: the base model with a better prompt, and a retrieval setup. If the prompt closes 70% of the gap, ship the prompt this week and fine-tune next quarter.

Gate: the failure is a style, format or narrow-task failure, not a knowledge gap.

## Stage 2 - Build the dataset

2.1 Collect 500-3,000 examples of input and the exact output you want. Below 500 the model memorises; above 3,000 the marginal gain per example falls fast (estimate).

2.2 Write every example as a chat-format JSON line, one conversation per line:

```json
{"messages":[{"role":"system","content":"You convert invoices to JSON."},{"role":"user","content":"Invoice INV-2291, dated 14/11/2026, total Rs 11,800 incl 18% GST."},{"role":"assistant","content":"{\"invoice_no\":\"INV-2291\",\"date\":\"2026-11-14\",\"total\":11800,\"tax_rate\":18}"}]}
```

2.3 Keep the system prompt identical across examples unless you deliberately want the model to handle several system prompts. Mixed system prompts need 3x the data.

2.4 Include 5-10% negative examples: inputs that should be refused or answered "not an invoice". Without them the model invents output for garbage input.

2.5 Balance difficulty: 60% typical, 25% edge cases (missing fields, odd currency, Indic digits), 15% hard. A dataset of only clean examples trains a model that fails on real traffic.

2.6 If you generate examples with a larger model, label them as synthetic in the dataset card and cap them at 50% of the total. A dataset of pure synthetic data teaches the student to imitate the teacher's mistakes, including its verbosity.

2.7 Write the labelling rule down before labelling 500 items, and check 30 items labelled by two people for agreement. Below 85% agreement the rule is ambiguous, and the model will learn the ambiguity.

Gate: a JSONL file that parses, every line with at least 2 messages, no empty assistant turn.

## Stage 3 - Split, dedupe and audit the data

3.1 Split 90/5/5 train/validation/test by a hash of the input, never by line order, so near-duplicates cannot straddle the split.

3.2 Dedupe on normalised input: lowercase, strip whitespace, remove digits. Duplicate inputs with different outputs are label noise and will teach the model to guess.

3.3 Check for leakage: any test input that appears in the training set, even paraphrased, invalidates the eval. Use 5-gram overlap above 0.7 as the flag.

3.4 Count token length per example and set `max_seq_len` to the 95th percentile, rounded up to 1,024 or 2,048. Truncating 30% of examples silently destroys the task.

| Dataset size | Train / val / test | Minimum viable |
|---|---|---|
| 500 | 450 / 25 / 25 | 300 |
| 1,000 | 900 / 50 / 50 | 600 |
| 3,000 | 2,700 / 150 / 150 | 1,500 |

3.5 Write a `data_card.md`: source, collection date, who labelled it, known gaps, PII handling. If the data came from user traffic, strip names, phone numbers and addresses before training, and record that you did.

3.6 Check the class balance. If 80% of examples are one category, the model learns that category and treats the rest as noise. Cap any single category at 50% of the dataset by downsampling, not by discarding your only hard examples.

Gate: zero 5-gram leakage between train and test, dataset card written.

## Stage 4 - Establish the baseline before training

4.1 Score the base model on the 150-item test set with the exact prompt you use in production. Save the outputs to `baseline.jsonl`.

4.2 Score three ways: exact match for structured output, a rubric 1-5 for free text, and a task-specific check (does the JSON parse, is the date valid).

4.3 Have one human grade 30 items blind. Automated judges drift; a human anchor catches the drift.

4.4 Record the base model's failure rate per category, so the post-training comparison is per category and not just an average.

4.5 Save the exact decoding settings used for the baseline: temperature, top_p, max tokens, stop sequences. The comparison later is only valid at identical settings.

4.6 Note the base model's failure examples verbatim in a file. After training, read the same examples again; if the fine-tune fails on the same three, the data does not cover that case and no amount of epochs will fix it.

Gate: `baseline.jsonl` with per-category scores and 30 human-graded items.

## Stage 5 - Configure QLoRA for one GPU

5.1 Start from this config, which fits a 7B-8B model in 4-bit on 24 GB with a 2,048-token sequence:

```python
from peft import LoraConfig
lora = LoraConfig(
    r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
    task_type="CAUSAL_LM",
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
)
train = dict(
    per_device_train_batch_size=1, gradient_accumulation_steps=16,
    learning_rate=2e-4, lr_scheduler_type="cosine", warmup_ratio=0.03,
    num_train_epochs=3, optim="paged_adamw_8bit", bf16=True,
    max_grad_norm=0.3, logging_steps=10, save_strategy="epoch",
)
```

5.2 Set `r=16` and `alpha=32` to start. `r=8` is enough for format tasks; `r=32` helps style transfer and doubles adapter size and overfitting risk.

5.3 Keep the effective batch size at 16 (batch 1 x accumulation 16). On a single 24 GB card, batch 2 x 8 also works and trains slightly faster.

5.4 Use `paged_adamw_8bit`; plain AdamW adds about 2 GB of optimiser state and is what pushes a 7B run into out-of-memory.

5.5 Watch memory: a 7B at 4-bit is about 4.5 GB, activations at 2,048 tokens about 3-6 GB, optimiser and gradients 1-3 GB. If you see OOM at step 1, cut `max_seq_len` to 1,024 before cutting batch size.

5.6 Turn on gradient checkpointing (`gradient_checkpointing=True`) when you need the memory. It costs 20-30% more compute time and saves 30-40% of activation memory, which is the right trade when the alternative is a shorter sequence.

5.7 Set `save_total_limit=2`. Three epochs at 2,048 tokens produce adapters plus optimiser states that fill a 40 GB disk faster than most people expect.

Gate: a dry run of 20 steps with loss printing and no OOM.

## Stage 6 - Train and read the curve

6.1 Run 3 epochs first. Loss should fall and then flatten; a validation loss that rises after epoch 2 means stop at 2.

6.2 Read the loss shape, not the final value:

| Curve | Meaning | Action |
|---|---|---|
| Train falls, val falls | Healthy | Continue |
| Train falls, val rises after epoch 2 | Overfitting | Stop early, add dropout, cut r to 8 |
| Loss flat from step 1 | LR too low or data not formatted | Check the chat template is applied |
| Loss spikes then recovers | LR too high | Drop to 1e-4, keep warmup 3% |
| Loss goes to 0 fast | Data duplicated or outputs trivially short | Dedupe, check label masking |

6.3 Mask the loss on the prompt tokens so the model learns to produce the answer, not to reproduce the question. In TRL this is `train_on_responses_only`; without it, quality drops noticeably on short outputs.

6.4 Save a checkpoint per epoch and one adapter per run named with the date, config hash and dataset size.

6.5 A 1,000-example, 3-epoch run on a 7B at 2,048 tokens takes roughly 40-90 minutes on a 24 GB card (estimate; depends on the card and the packing setting).

6.6 Log the learning rate alongside the loss; a cosine schedule that never warms up produces the flat-loss failure in the table above and wastes an hour of GPU time.

6.7 Pack short examples into full sequences (`packing=True`) when most examples are under 400 tokens. It cuts a 3-epoch run on short data by 40-60% and changes nothing about quality, provided you mask across example boundaries.

Gate: adapter saved, training log kept, epoch chosen by validation loss.

## Stage 7 - Evaluate against the baseline

7.1 Generate on the same 150 test items with the same decoding settings. Different temperature invalidates the comparison.

7.2 Score per category and overall. Ship only if the win rate is 60% or better on a blind pairwise comparison, and no category regressed by more than 5 points.

7.3 Run 30 general prompts outside your task (small talk, arithmetic, an unrelated question) to measure collateral damage. Fine-tuning on one task degrades general ability; know how much.

7.4 Check the negative cases: does it still refuse garbage input at the same rate?

7.5 Compare latency and cost per 1,000 calls between the base model and the fine-tune. A 7B that is 4x cheaper per token is the whole business case on a high-volume route, and it is worth stating as a number in the report.

| Metric | Baseline | Target |
|---|---|---|
| Exact match, structured | record | +25 points or better |
| Rubric mean (1-5) | record | +0.8 or better |
| Refusal rate on negatives | record | within 3 points |
| Off-task prompts still sane | 30/30 | 27/30 or better |

Gate: pairwise win rate 60%+ and no category regression over 5 points.

## Stage 8 - Merge and export

8.1 Merge the adapter into the base weights for serving, or keep it separate if you serve with vLLM's multi-LoRA support.

8.2 Merge in bf16 on the same GPU, then quantise for deployment:

```bash
# merge adapter into base, then export GGUF q4_k_m for llama.cpp
python -m peft.merge_adapter --base meta-llama/Llama-3.1-8B-Instruct \
  --adapter ./out/run-2026-11-15 --out ./out/merged-bf16
python convert_hf_to_gguf.py ./out/merged-bf16 --outfile ./out/model-f16.gguf
./llama-quantize ./out/model-f16.gguf ./out/model-q4_k_m.gguf Q4_K_M
```

8.3 Quantisation costs 1-3 points on most tasks. Re-run the test set on the quantised artefact - the artefact you deploy is the only one that matters.

8.4 Record the licence of the base model and whether it permits commercial use before you ship anything.

8.5 Keep the merged bf16 weights and the adapter. The adapter is 20-200 MB and lets you retrain, re-merge or change quantisation later without another training run.

8.6 Test the quantised artefact's context length, not just its quality. A model trained at 2,048 tokens degrades past that even if the serving config allows 8,192.

Gate: the quantised artefact scored on the same 150 items, with the delta written down.

## Stage 9 - Serve and watch

9.1 Serve with vLLM for throughput or llama.cpp for a single small box. Set `max_model_len` to your trained sequence length plus 256.

9.2 Keep the old prompt-only path behind a flag for 14 days. Route 5% of traffic to the new model first, then ramp.

9.3 Log input, output, latency and a task-specific validity check (JSON parses, date valid) on every call. The validity rate is your production eval.

9.4 Watch for drift: a fine-tuned model fails quietly on inputs outside its training distribution. Alert when the validity rate falls 3 points below the test-set rate.

9.5 Cost the run and the serving honestly: training hours x GPU rate, plus per-token serving, compared with the big-model path it replaced.

9.6 Set a per-request timeout and a fallback to the base model. A fine-tuned model served on one GPU is a single point of failure, and the fallback path costs 20 lines.

9.7 Keep a sample of 50 production inputs a week, labelled, as a living test set. The frozen 150-item set protects the release; the weekly sample catches drift.

Gate: 5% ramp for 48 hours with validity within 2 points of the test set.

## Stage 10 - Document and keep the rollback

10.1 Write `finetune.md`: base model, adapter path, dataset hash, config, eval table, serving command, rollback command.

10.2 Rollback is one config flip to the previous model, tested before you need it.

10.3 Retrain cadence: only when the failure rate in production rises 3 points, or the format changes. Not on a schedule for its own sake.

10.4 Never train on production traffic without consent and PII stripping; in India, the DPDP Act treats training data as personal data processing, so record purpose and retention.

10.5 Hand the run to whoever serves it: adapter path, base model revision hash, config file, eval table. A model nobody can reproduce is a model nobody can fix.

Gate: rollback executed once in staging and timed under 5 minutes.

## Second worked example - Hindi-English support replies

A support team writes in Hinglish and the base model answers in formal English. The failure rate on tone is 34%.

| Item | Value |
|---|---|
| Examples collected from approved replies | 1,400 |
| Split | 1,260 / 70 / 70 |
| Sequence length (95th percentile) | 1,180, rounded to 1,536 |
| Base model | 8B instruct, 4-bit |
| r / alpha / epochs | 16 / 32 / 3 |
| GPU hours on a 24 GB card | 3.4 |
| Tone failure rate after | 9% |
| Off-task sanity prompts still sane | 29/30 |

The lesson: 1,400 examples of a house tone is enough; 400 would not have been, and the first run at 400 examples produced a model that parodied the style instead of using it.

## Quality checklist

- [ ] Failure written as one sentence with a rate
- [ ] Decision table says fine-tune, not retrieval
- [ ] 500+ examples in chat JSONL, every line valid
- [ ] 5-10% negative examples included
- [ ] Split by input hash, 90/5/5
- [ ] Zero 5-gram leakage between train and test
- [ ] Dataset card written with PII handling
- [ ] Baseline scored on 150 items before training
- [ ] 30 items human-graded blind
- [ ] Loss masked on prompt tokens
- [ ] Epoch chosen by validation loss, not by default
- [ ] Pairwise win rate 60%+ on blind comparison
- [ ] Off-task prompts still sane at 27/30
- [ ] Quantised artefact re-scored, delta recorded
- [ ] Base model licence checked for commercial use
- [ ] 5% traffic ramp for 48 hours
- [ ] Fallback to the base model on timeout, rollback tested and timed
- [ ] Training and serving cost compared with the path it replaced

## Failure modes

| Symptom | Real cause | Fix |
|---|---|---|
| Loss falls to near zero in 50 steps | Duplicate rows or one-token outputs | Dedupe on normalised input, check output lengths |
| Model repeats the question in its answer | Loss not masked on prompt tokens | Enable response-only training |
| Great on test, bad in production | Test set built from the same distribution as train and nothing else | Add 15% hard and out-of-distribution items, re-split |
| OOM at step 1 | Sequence length too long for the card | Drop to 1,024 tokens, then batch 1 |
| Adapter trains but output format drifts | System prompt differed between train and serve | Use the exact training system prompt in production |
| Quantised model much worse | Re-scored on nothing, shipped on faith | Score the GGUF artefact on the same 150 items |
| Model refuses everything after training | Too many negatives, or refusals labelled inconsistently | Cap negatives at 10%, relabel with one rule |
| General ability visibly degraded | Single-task training with no general data mixed in | Mix 5-10% general instruction data, or route off-task traffic to the base model |
| Eval improves every run | The test set is being read during development | Freeze the test file, hash it, and only run it at the end |
| Model parodies the style instead of using it | Under 500 examples, so it memorised the few it had | Collect 3x more data before training again |
| Training is 6x slower than the estimate | No packing on short examples | Enable packing and mask across example boundaries |
| Adapter loads but answers like the base model | Wrong target modules for the architecture, so nothing trained | Print the trainable parameter count and confirm it is above 0.5% of total |

## Copy-ready agent prompt

> Read the skill at the URL above and help me fine-tune a model. Ask me first: the exact failure I am fixing, how many examples I have, the GPU I can rent, and the base model I want. Then run the decision table and tell me if fine-tuning is even right. If it is, walk me through dataset format, split and leakage checks, baseline scoring, and the QLoRA config with r, alpha, learning rate and epochs justified. Give me the training command, the export commands, and the eval table with before and after numbers. Finish with the serving command, the 5% ramp plan, the rollback command and the cost comparison. Do not invent benchmark numbers - use my measured results.
