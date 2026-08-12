Manual transcription from: https://www.youtube.com/watch?v=9vM4p9NN0Ts
Stanford CS229 I Machine Learning I Building Large Language Models (LLMs)

> **How to read this file.** Plain sections are the lecture notes as transcribed.
> Sections marked **⊕ Complement** are added material: derivations, missing definitions,
> failure modes, and a **In practice** line giving the engineering/business consequence.
> Notation: $L$ = sequence length, $\mathcal{L}$ = loss, $|V|$ = vocabulary size,
> $d$ = hidden size, $N$ = number of parameters, $D$ = number of training tokens.

---

## The whole pipeline in one picture

```
        ┌──────────────── PRETRAINING ────────────────┐   ┌──── POST-TRAINING ────┐
                                                          
  web ──► filter ──► tokenize ──► next-token ──► BASE ──► SFT ──► RM ──► RLHF ──► ALIGNED
  data     dedup      (BPE)       prediction     MODEL   (demos) (prefs) (PPO/DPO)  MODEL
            │                          │           │        │       │        │         │
         ~1% kept              cross-entropy   knowledge  format  taste   optimize   product
                                   loss        + skills   /style  model  for taste
                                                                                        
  cost:  ~10^23-10^25 FLOPs, months, $1M-$1B          ~1% of pretraining compute
  data:  10^12-10^13 tokens                          10^3-10^6 examples
```

Everything in the lecture is a box in this diagram. The two halves answer different
questions: pretraining asks *"what does the model know?"*, post-training asks
*"how does it behave?"*.

---

# Language modeling
LM: Probability distribution over sequences of tokens/words p(x_1, ..., x_L)
P(the, mouse, ate, the,  cheese) = 0.02
P(the, the, mouse, ate, the, cheese) = 0.00001 -> Syntactic knowledge 
P(the, cheese, ate, the, mouse) = 0.001 -> Semantic knowledge

LMs are generative models: $x_{1:L} \sim p(x_1, \dots, x_L)$

Autoregressive (AR) language models:
$$
p(x_1, ..., x_L) = p(x_1)p(x_2|x_1)p(x_3|x_2,x_1)... = \prod_i p(x_i|x_{1:i-1})
$$
No approx: chain rule of probability

In essence, you only need a model that can predict the next token given past context!
> Recall Bayes theorem and conditional probability

At the high level the Task is predict the next word
Steps:
1. Tokenize
2. Forward
3. Predict the probability of the next token
4. Sample
5. Detokenize

Step 4. and Step 5. are only important for inference. The training fits the probability distribution, not the actual sample. Tokenization is basically convert text/words into numbers. Tokenization will be discussed further in the course

The process follows:
The words is converted to tokends using an input word embeddings
This vectorized input is passed to a Neural Network whose output vector $h$ represents a context. Encodes information
Then $h$ is transformed linearly from size $d$ to $|V|$ -  the vocabulary size using a linear layer.
To encounter the distribution, the output layer has one softmax activation function to get the probability distribution for the next context
This output is fed into the previous history or process context to repeat the process

### ⊕ Complement: why *this* factorization, and what it buys you

**The chain rule is exact — the modeling choice is the ordering.** Any permutation of the
variables gives a valid factorization. Left-to-right is chosen for two reasons:

1. It matches how we want to *use* the model (generate a continuation of a prompt).
2. It allows **causal masking**, which makes training embarrassingly parallel: one forward
   pass over a sequence of length $L$ produces $L$ training signals simultaneously
   (predict $x_2$ from $x_1$, $x_3$ from $x_{1:2}$, …). This is **teacher forcing** — during
   training the model always conditions on the *ground-truth* prefix, never on its own
   samples, so there is no sampling loop.

Contrast with masked LMs (BERT): masking 15% of tokens gives ~7× less learning signal per
forward pass. That efficiency gap is a large part of why generative AR models won.

**Finite context.** Classical n-gram models *approximated* $p(x_i|x_{1:i-1}) \approx p(x_i|x_{i-n+1:i-1})$
(Markov assumption). Transformers make no such approximation *within* their context window
$W$, but $W$ is finite, so in practice you still get $p(x_i \mid x_{i-W:i-1})$. "Long context"
work is about making $W$ large without paying $O(W^2)$.

**Shapes of the forward pass** (worth memorizing):

| Step | Object | Shape |
|---|---|---|
| token IDs | $x$ | $L$ integers in $[0,\|V\|)$ |
| embedding lookup | $E$ | $\|V\| \times d$ |
| transformer output | $h_i$ | $d$ |
| unembedding / LM head | $W_{out}$ | $\|V\| \times d$ |
| logits | $z = W_{out}h_i$ | $\|V\|$ |
| probabilities | $p = \mathrm{softmax}(z)$ | $\|V\|$, sums to 1 |

$E$ and $W_{out}$ are often **weight-tied** (same matrix) to save parameters. Note that
$|V|\cdot d$ can be huge: with $|V|=128\text{k}$ and $d=4096$ that is 524M parameters *just for
the embedding* — a real design constraint for small models.

**Sampling (step 4).** Not part of the loss, but it determines everything the user sees:
- *Temperature* $T$: $p_i \propto \exp(z_i / T)$. $T\to 0$ = greedy (argmax), $T=1$ = the
  learned distribution, $T\to\infty$ = uniform.
- *Top-k*: keep the $k$ most likely tokens, renormalize.
- *Top-p (nucleus)*: keep the smallest set whose cumulative probability $\ge p$.

**In practice:** use $T=0$ (greedy) for extraction, classification, code and anything you will
parse — it makes outputs reproducible. Use $T \approx 0.7$–$1.0$ with top-p $\approx 0.9$ for
drafting/brainstorming. "The model is non-deterministic" is usually a decoding setting, not a
property of the model.

---

Loss
The loss is given to classify the next tokens' index, using typically a cross-entropy loss
The target is normally a one-hot encoded distribution. 

This is equivalent to maximize text's log-likelihood
$$
\max \prod_i p(x_i|x_{1:i-1}) \;=\; \min \left(-\sum_i \log p(x_i|x_{1:i-1})\right) = \min \mathcal{L}(x_{1:L})
$$

### ⊕ Complement: the loss, three ways of seeing it

Write the per-token loss with $z_t$ the logits at position $t$ and $x_t$ the true next token:

$$
\mathcal{L} = -\frac{1}{L}\sum_{t=1}^{L} \log p_\theta(x_t \mid x_{1:t-1}), \qquad
p_\theta(\cdot) = \mathrm{softmax}(z_t)
$$

**(1) As classification.** Cross-entropy $H(q,p) = -\sum_v q_v \log p_v$ with a one-hot target
$q = e_{x_t}$ collapses to a single term: $-\log p_{x_t}$. So "cross-entropy with one-hot
target" and "negative log-likelihood" are literally the same number.

**(2) As distribution matching.** Averaged over the data distribution,
$$
\mathbb{E}_{p_{\text{data}}}[\mathcal{L}] = H(p_{\text{data}}, p_\theta) = \underbrace{H(p_{\text{data}})}_{\text{constant, irreducible}} + \underbrace{D_{KL}(p_{\text{data}} \,\|\, p_\theta)}_{\text{what you minimize}}
$$
Two consequences: (a) the loss **cannot reach 0** — there is an entropy floor set by the
inherent unpredictability of text; this is exactly the constant $E$ that appears in the scaling
laws later. (b) You are minimizing the *forward* KL, which is **mode-covering**: the model is
penalized infinitely for assigning zero probability to something that occurs, but barely
penalized for putting mass on things that never occur. This is one structural root of
hallucination — the pretraining objective never asks the model to say "I don't know".

**(3) As compression.** $-\log_2 p(x)$ is the optimal code length in bits (Shannon). Training an
LM *is* fitting a lossless compressor of the corpus. A 2 bits/token model compresses text ~8×
better than raw ASCII.

**The gradient is beautifully simple.** For softmax + cross-entropy, the gradient w.r.t. the
logits is
$$
\frac{\partial \mathcal{L}_t}{\partial z_t} = p_t - e_{x_t}
$$
i.e. *predicted minus observed*. Bounded in $[-1,1]$, no vanishing gradient from the output
layer — which is why this pairing is used essentially everywhere.

**In practice:** loss is reported in **nats/token** (natural log). A well-trained modern model
sits around **1.7–2.2 nats/token** on general web text. Loss curves are the single most
informative artifact of a training run: a spike usually means a bad data shard or an
optimizer/precision instability, not "the model got confused".

---

# Tokenizer
* Simpler and more general than words (eg typos or other languages like Thai, where there are no spacing or no words as concept)
* The complexity of the prediction works quadratically respect to the lenght of the phrase -> shorter sequences than with characters
* Idea: tokens as common subsequences -> In average, each token is 3-4 letters
* Eg: Byte Pair Encoding (BPE). -> One of the most common tokenizers. Process
1. Take a large corpus of text
2. Start with one token per character
3. Merge common pairs of tokens into a token 
4. Repeat until desired vocab size or all merged

Normally because of computation optimization, the punctuation and spacing are often ignored or excluded from the tokenizer.
Some preprocessing could be applied before tokenizer: pretokenizer
However sometimes it's included the raw data so that typo errors are recognized as well -> typo becomes part of the model's input
It's based primarly on frequency/statistical regularity

> A tokenizer usually does not understand linguistics, morphology, etymology, or semantics. It discovers or is given statistical patterns in text.

             RAW INPUT
                 │
                 ▼
        ┌─────────────────┐
        │    tokenizer    │
        └─────────────────┘
                 │
                 ▼
          token sequence
                 │
                 ▼
          integer IDs
                 │
                 ▼
            Transformer



                  TOKENIZER
                      │
       ┌──────────────┼───────────────┐
       │              │               │
    spelling       spaces        punctuation
       │              │               │
       └──────────────┼───────────────┘
                      ▼
                    TOKENS
                      │
                      ▼
                 TRANSFORMER
                      │
       ┌──────────────┼───────────────┐
       │              │               │
    syntax        morphology       semantics
       │              │               │
       └──────────────┼───────────────┘
                      ▼
                  CONTEXT
                      │
                      ▼
             meaning / prediction

### ⊕ Complement: the cost argument, made quantitative

Per transformer layer, the FLOPs are roughly
$$
\underbrace{\;\sim 4Ld^2\;}_{\text{projections, linear in } L} \;+\; \underbrace{\;\sim 2L^2d\;}_{\text{attention, quadratic in } L}
$$
So the choice of tokenizer directly scales $L$. If the average token is 4 characters and you
switch to character-level, $L$ grows 4× → the linear term grows 4×, the attention term grows
**16×**. That is the whole justification for subword tokenization: it is a *compression* step
that buys compute.

The trade-off runs in both directions:

| Larger vocabulary | Smaller vocabulary |
|---|---|
| Shorter sequences → cheaper forward pass | Longer sequences → more compute |
| More embedding/softmax parameters ($\|V\|d$) | Fewer parameters |
| Rare tokens get few updates | Every token well-trained |
| Better multilingual coverage | Non-English fragments into many tokens |

Typical values: GPT-2 = 50,257 · Llama 2 = 32,000 · Llama 3 = 128,256 · Gemma = 256,000.

**BPE, worked micro-example.** Corpus `low low lower lowest`, start from characters:

```
l o w _ l o w _ l o w e r _ l o w e s t
merge 1: ("l","o") → "lo"      (4 occurrences, most frequent pair)
merge 2: ("lo","w") → "low"    (4)
merge 3: ("low","e") → "lowe"  (2)
...
```
Merges are stored **as an ordered list**; encoding new text replays them greedily. That
ordering is why the tokenization of a string is deterministic but non-obvious — and why
`123456` and `123457` can segment differently, as noted below.

**Byte-level BPE** (GPT-2 onwards) starts from the 256 possible *bytes* rather than Unicode
characters. Consequence: **there is no out-of-vocabulary input, ever** — any emoji, any script,
any binary blob is representable. This is why modern models degrade gracefully on garbage
input instead of erroring.

**Pre-tokenization** is a regex split applied *before* BPE (e.g. never merge across a
space→letter boundary, never merge letters with digits). It is what prevents pathological
tokens like `" the end."` becoming one unit, and it is where digit-grouping rules live.

**Known failure modes traceable to tokenization:**
- *Arithmetic* — see the number example below. Modern tokenizers mitigate this by forcing
  digits into groups of ≤3 (GPT-4, Llama 3) or single digits (Llama 2).
- *Character-level tasks* — "how many r's in strawberry" is hard because the model never sees
  characters, only the opaque IDs of `str`/`aw`/`berry`.
- *Glitch tokens* — tokens that exist in the vocabulary but barely occur in training data (the
  famous `SolidGoldMagikarp`). Their embeddings stay near-random → bizarre outputs.
- *Code* — indentation and tab handling is a tokenizer design decision with real effects on
  code quality.

**In practice (business):** ≈ **4 characters ≈ 0.75 words ≈ 1 token** in English. But token
*fertility* is 2–4× higher for Thai, Hindi, Finnish, or Arabic than for English on many
tokenizers. That means, for the exact same content, non-English users pay **2–4× more per API
call** and get **2–4× less usable context**. When benchmarking vendors for a multilingual
product, measure token counts on *your* language, not on English samples. The tokenizer is also
frozen at training time — you cannot swap it without retraining.

---

> **A tokenizer does not inherently understand that `123456789` is a number. It tokenizes the character/byte sequence according to its vocabulary.**

So a long number could become one token, several chunks, individual digits, or something in between.

### Example

Imagine the text:

```text
123456789
```

A tokenizer might produce something conceptually like:

```text
["123", "456", "789"]
```

or:

```text
["1234", "5678", "9"]
```

or:

```text
["1", "234", "567", "89"]
```

or even:

```text
["1", "2", "3", "4", "5", "6", "7", "8", "9"]
```

The exact behavior depends on the tokenizer and its vocabulary.

The really interesting problem: `123456` vs `123457`

Suppose the tokenizer learned:

```text
123
456
```

Then:

```text
123456
```

could be:

```text
["123", "456"]
```

But:

```text
123457
```

might become:

```text
["123", "45", "7"]
```

because `457` might not exist as a useful token.

So two extremely similar numbers can receive **different tokenizations**.

This is one reason language models can have surprising difficulties with arithmetic and exact numerical manipulation.

> **⊕ Consequence:** two numbers that are adjacent on the number line can be *far apart* in
> representation space, and the model must learn digit alignment (units under units, tens under
> tens) through an encoding that actively scrambles it. **In practice:** never trust an LLM for
> exact arithmetic or ID/reference-number manipulation — give it a calculator/code tool. This is
> a representational limitation, not a "the model isn't smart enough" problem.

---

# LLM evaluation: Perplexity

* Idea: Validation loss

$$
PPL(x_{1:L}) = 2^{\;\mathcal{L}(x_{1:L})} = \prod_i p(x_i|x_{1:i-1})^{-1/L}
\qquad \text{with } \mathcal{L} = -\tfrac{1}{L}\sum_i \log_2 p(x_i|x_{1:i-1})
$$

* To be more interpretable: use perplexity
    * avg per token (~independent of length)
    * Exponentiate -> units independent of log base

Perplexity is not used anymore for academic benchmark but still important for development
Range is from 1 to vocabulary size
1 means the best

### ⊕ Complement: reading perplexity, and its one big trap

**Interpretation: average branching factor.** $PPL = k$ means the model is, on average, as
uncertain as if it were choosing uniformly among $k$ equally likely tokens. Bounds:
- $PPL = 1$: perfect prediction (probability 1 on every true token).
- $PPL = |V|$: uniform guessing, i.e. the model learned nothing.

**Base consistency matters.** Use $2^{\mathcal{L}}$ if $\mathcal{L}$ is in bits, $e^{\mathcal{L}}$ if in nats.
Either way you get the same perplexity — that is the point of exponentiating. Reference points:
$\mathcal{L} = 2.0$ nats → $PPL \approx 7.4$; $\mathcal{L} = 3.0$ nats → $PPL \approx 20$.

**⚠ The trap: perplexity is not comparable across tokenizers.** A model with a larger vocabulary
predicts fewer, longer tokens per sentence, which *mechanically* changes per-token perplexity
without any change in modeling quality. Comparing PPL across models with different tokenizers is
meaningless. The fix is a tokenizer-independent metric, **bits-per-byte**:
$$
\text{BPB} = \frac{N_{\text{tokens}}}{N_{\text{bytes}}} \cdot \frac{\mathcal{L}_{\text{nats}}}{\ln 2}
$$
Same for bits-per-character. Use this whenever you compare two different model families.

**Why it fell out of academic use, and why you still need it.** It measures likelihood of text,
not usefulness: it cannot tell you if the model follows instructions, reasons, or refuses
harmful requests. But it remains the workhorse *internally* because it is dense, cheap, and
low-variance — one number per batch instead of a benchmark run. Real uses:
- comparing data-cleaning ablations and data mixes;
- fitting scaling laws (you need a smooth metric, and downstream accuracy is not smooth);
- detecting training divergence early;
- **contamination detection** — anomalously low perplexity on a benchmark's test set is
  evidence the model saw it during training.

**In practice:** for a vendor/model selection decision, perplexity is the wrong metric — use
task evals. For a *training or data-pipeline* decision, it is usually the right one.

---

# LLM evaluation: eg MMLU
Question + Answer
Multiple choice questions
Collegue topics
The model is constraint so that it can generate the likelihood of the tokens or the answer. Given the sentences what is the likelihood to generate the sentence p(answer | question)

### ⊕ Complement: what MMLU actually is, and why scores move

**MMLU** (Massive Multitask Language Understanding, Hendrycks et al. 2021): ~15.9k 4-way
multiple-choice questions across **57 subjects** (law, medicine, math, history, …). Random
baseline = **25%**. Standard protocol = **5-shot**.

**Three different ways to score the same benchmark** — and they give different numbers:

1. **Letter likelihood:** compare $p(\text{"A"}), p(\text{"B"}), p(\text{"C"}), p(\text{"D"})$ directly.
   Cheap, but conflates knowledge with the model's prior over letters (models have real
   position/letter biases).
2. **Full-answer likelihood:** score $p(\text{answer text} \mid \text{question})$. Needs
   normalization, because longer answers have lower probability by construction:
   - *length-normalized*: divide by the number of tokens;
   - *PMI / unconditional-normalized*: $\log p(a\mid q) - \log p(a \mid \text{"Answer:"})$, which
     removes the model's prior preference for the answer string itself.
3. **Free generation:** just let a chat model emit "A" and parse it. What most modern
   evaluations do — but then formatting and refusals become part of the score.

Reported MMLU can shift by **several points** between these protocols on the *same* model. This
is the concrete mechanism behind the "sensitivity to prompting" bullet in the next section.

**In practice:** MMLU is now saturated at the frontier (>88%) and heavily contaminated; it has
largely been replaced by MMLU-Pro (10 options), GPQA (expert-level, Google-proof), and
task-specific harder sets. Treat a single-number MMLU claim in a vendor deck as weak evidence.

---

# Evaluation: challenges
* Sensitivity to prompting/inconsistencies
* Train & test contamination

### ⊕ Complement: the four ways benchmarks lie

1. **Prompt sensitivity.** Few-shot example *order*, answer-option order, whitespace, and
   template wording all move scores by multiple points. Mitigation: fix a template, report
   variance over several seeds/orderings, randomize option order.
2. **Contamination.** The test set is on the internet, and the internet is the training set.
   Detection: n-gram overlap between benchmark and corpus, canary strings embedded in benchmark
   files, and the perplexity signal mentioned above. Structural fixes: benchmarks with
   continuously refreshed questions (LiveBench, dynamic arenas), or private held-out sets.
3. **Goodhart's law.** Once a benchmark is a target — for funding, for a launch, for a
   leaderboard — data mixes get tuned toward it and it stops measuring what it measured.
4. **Construct validity.** MMLU accuracy is not "usefulness at your task". The correlation
   between public leaderboards and internal task performance is real but far from 1.

**In practice (this is the important one):** the highest-ROI thing an applied team can build is
a **private eval set of 100–300 real tasks from your own users**, with a fixed grading protocol.
It costs a few days, cannot be contaminated, and it is what actually decides whether a model
swap, a prompt change, or a fine-tune helped. Public benchmarks tell you which models to *try*;
your eval set tells you which one to *ship*.

---

# Data
* Idea: use all the information from internet
* Note: internet is dirty & not representative of what we want. Practice:
1. Download all the internet. Common crawl: 250 billion pages. > 1PB
2. Text extraction from HTML. Challenges: math, boiler plate
3. Filter underisable content (e.g. NSFW, harmful content, PII)
4. Deduplicates (url/document/line). E.g. all the headers/footers/menu in forums are always same
5. Heuristic filtering. Remove low quality documents (e.g. # words, word length, outlier tokens, dirty tokens)
6. Model based filtering. 
7. Data mix. Classify data categories (code/books/entertainment). Reweight domains using scaling laws to get high downstream performance

Also: learning rate annealing on high-quality data, continual pretraining with longer context

### ⊕ Complement: what each step actually does, and the survival rate

The headline number: **roughly 1% of raw Common Crawl survives to the final token set.**
FineWeb, for example, processed 96 CC snapshots (petabytes) into ~15T tokens.

| Step | Technique in practice | Why it matters |
|---|---|---|
| 2. Extraction | Reprocess **WARC** (raw HTML) with trafilatura/resiliparse rather than using CC's own **WET** text dumps — WET extraction is crude and loses structure. Math (LaTeX/MathML) and tables are the hardest cases. | Extraction quality is one of the largest single levers on final model quality. |
| 3. Content filtering | URL blocklists, NSFW/toxicity classifiers, PII detection + redaction (emails, phone numbers, keys). | Legal exposure (GDPR) and safety are decided here, not at post-training. |
| 4. Dedup | Exact: hashing. Near-dup: **MinHash + LSH** over n-gram shingles (Jaccard ≥ ~0.8). Substring: suffix arrays. Line-level for boilerplate. | Deduplication reduces memorization/regurgitation *and* improves loss per FLOP — duplicated data wastes compute. |
| 5. Heuristics | Gopher rules: document length, mean word length, symbol-to-word ratio, fraction of lines ending in "…", stopword presence. | Cheap, removes the obvious garbage before expensive steps. |
| 6. Model-based | A fast classifier (fastText) scoring "looks like Wikipedia/reference text" vs random CC; or KenLM perplexity filtering (CCNet); or an LLM scoring *educational value* (FineWeb-Edu). | The step that most distinguishes good corpora from mediocre ones. |
| 7. Mix | Reweight domains (web/code/books/math/multilingual). Learned approaches: **DoReMi**. Upsample code and math. | Code and math data measurably improve *general* reasoning, not just coding. |

**Annealing / mid-training** (the last bullet) deserves emphasis: in the final ~10–20% of
training, as the learning rate decays toward zero, you swap in a much higher-quality mix (math,
code, curated text, instruction-like data). The gains are disproportionate to the token count —
the model is taking its last, smallest, most careful steps, so what it sees then matters most.

**Long-context extension** is usually *continual pretraining*: take the finished model, extend
the RoPE position-encoding base, and train further on a smaller corpus of long documents. Far
cheaper than pretraining at long context from scratch.

**In practice (business):** three things follow. (a) **Data work, not architecture, is where
frontier labs spend their differentiating effort** — architectures are largely public and
similar. (b) **Provenance and licensing are procurement questions** — for a regulated buyer,
"what was this trained on?" is a due-diligence item, and the answer is often "we can't fully
say". (c) If you are building a domain model, the same pipeline applies at 1/1000th scale, and
the same ordering holds: extraction quality → dedup → quality filter → mix.

---

# Research on the Data domain
* How do you process well and efficiently?
* How do you balance domains?
* Synthetic data?
* Multi-modal data?

> **⊕ On synthetic data.** Three distinct meanings, often conflated: (1) **distillation** — a
> stronger model generates training data for a weaker one (effective, but check the provider's
> terms of use); (2) **self-improvement** — a model generates data, a filter/verifier keeps the
> good parts, the model trains on it (works well when a *verifier* exists: math, code, unit
> tests); (3) **textbook-style generation** — synthesize clean pedagogical text (Phi models).
> The open risk is **model collapse**: training repeatedly on unfiltered model output degrades
> distribution tails. The filter is what makes the difference between improvement and collapse.

---

# Scaling laws
* Empiritcally: more data and larger models -> better performances
* Overfitting normally doesn't happens in LLMs
* Idea: predict model performance based on amount of data & parameters 

### ⊕ Complement: the actual equations, and how they are used to sign a budget

**The functional form** (Hoffmann et al. 2022, "Chinchilla"):
$$
\mathcal{L}(N, D) = \underbrace{E}_{\text{entropy of text}} + \underbrace{\frac{A}{N^{\alpha}}}_{\text{model too small}} + \underbrace{\frac{B}{D^{\beta}}}_{\text{data too small}}
$$
with fitted values $E \approx 1.69$, $A \approx 406.4$, $B \approx 410.7$, $\alpha \approx 0.34$,
$\beta \approx 0.28$ (nats/token). Note $E$: this is the irreducible entropy floor from the KL
decomposition earlier — no amount of scale removes it.

**The compute constraint.** For a dense transformer, training FLOPs are
$$
C \approx 6ND
$$
(2 FLOPs/parameter forward, 4 backward, per token). Minimizing $\mathcal{L}(N,D)$ subject to
$6ND = C$ gives $N_{opt} \propto C^{0.5}$ and $D_{opt} \propto C^{0.5}$ — both scale equally,
hence the famous rule of thumb:
$$
\boxed{D \approx 20 \times N \quad \text{tokens per parameter (compute-optimal)}}
$$

**This corrected an earlier error.** Kaplan et al. (2020) concluded model size should grow much
faster than data; GPT-3 followed it (175B params, only 300B tokens → $D/N \approx 1.7$) and was
therefore *badly under-trained*. Chinchilla (70B params, 1.4T tokens) beat models 4× its size.

**And then practice moved past Chinchilla.** Chinchilla optimizes *training* compute only. If
you will serve the model to millions of users, **inference cost dominates total cost**, and a
smaller model trained far past the optimum is the better business decision:

| Model | $N$ | $D$ | $D/N$ | |
|---|---|---|---|---|
| GPT-3 | 175B | 300B | 1.7 | under-trained (pre-Chinchilla) |
| Chinchilla | 70B | 1.4T | 20 | compute-optimal |
| Llama 3 8B | 8B | 15T | ~1875 | deliberately over-trained for cheap inference |

**Why overfitting doesn't appear.** Pretraining is roughly single-epoch over a corpus vastly
larger than model capacity, so train and validation loss track each other. When you *must*
repeat data, up to ~4 epochs is nearly as good as fresh data; beyond that returns collapse
(Muennighoff et al. 2023).

**How scaling laws are actually used:** fit the curve on a ladder of small, cheap runs
(e.g. 10M → 1B parameters), then extrapolate to choose $N$, $D$, learning rate and batch size
for the single large run — *before* spending the money. Hyperparameters are chosen by
extrapolation, not by tuning at full scale.

**Worked cost example (useful for a business case).** Train a 7B model on 2T tokens:
$$
C = 6 \times 7\times10^9 \times 2\times10^{12} = 8.4 \times 10^{22} \text{ FLOPs}
$$
An H100 delivers ~$10^{15}$ FLOP/s peak in bf16; at a realistic **40% MFU** that is
$4\times10^{14}$ FLOP/s. So $8.4\times10^{22} / 4\times10^{14} \approx 2.1\times10^{8}$
GPU-seconds $\approx$ **58,000 H100-hours** ≈ 3 weeks on 128 GPUs ≈ **$120k–200k** of compute at
$2–3/GPU-hour. That is the number to compare against fine-tuning ($10^2$–$10^3$ $) and against
just calling an API. **Inference**, by contrast, costs ~$2N$ FLOPs per generated token — which
is why the $N$ you choose is a permanent tax on every request you will ever serve.

**Caveat:** scaling laws predict *loss*, smoothly. They do not cleanly predict *downstream
capabilities*, which often look discontinuous — though much of that apparent "emergence" is an
artifact of thresholded metrics (exact-match accuracy) rather than the underlying continuous
improvement.

---

# Post-training
Language modeling is not the same as assisting users

Task: aligment
Goal: LLM follows user instructions and designer's desires (e.g moderation)

* Background:
    * data of desired behaviors is what we want but scarce and expensive
    * pretraining data scales but is not what we want

* Idea: finetune pretrained LLM on a little desired data -> "post-"training

> **⊕ Framing.** A base model completes documents. Ask it "What is the capital of France?" and a
> plausible continuation is *another exam question*, not an answer — because that is what such
> text looks like on the internet. Alignment is largely about **selecting a mode** that already
> exists in the pretrained distribution ("helpful expert assistant") rather than teaching new
> content. Post-training typically costs **<1% of pretraining compute** yet accounts for most of
> the perceived difference between a research artifact and a product.

---

# Supervised finetuning (SFT)
* Idea: finetune the LLM with language modeling (Next word prediction) of the desired answers (desired behaviors)
* How do we collect the data? Ask humans -> Human in Loop or Reinforcement learning with human feedback

### ⊕ Complement: SFT mechanics people get wrong

- **Same loss, different masking.** SFT uses the identical cross-entropy objective. The only
  change: the loss is computed **only on assistant tokens**; prompt/system tokens are masked out.
  Training on the prompt tokens teaches the model to *generate user turns* — a classic bug.
- **Chat template.** Structure is imposed with special tokens
  (`<|user|> … <|assistant|> … <|end|>`). At inference you must use *exactly* the same template
  the model was trained with; mismatched templates are a very common cause of "this open model
  is bad" reports.
- **Hyperparameters.** Small LR ($10^{-6}$–$10^{-5}$, i.e. 10–100× below pretraining), 1–3
  epochs. Over-training causes **catastrophic forgetting** of pretrained ability.
- **LoRA / PEFT.** Train low-rank adapters $\Delta W = BA$ with rank $r \ll d$ instead of full
  weights: ~0.1–1% of the parameters trained, one base model serving many adapters. This is what
  makes per-customer fine-tuning economically viable.

---

# Scalable data for SFT: eg Alpaca
* Problem: human data is slow to collect and expensive
* Idea: use LLMs to scale data collection
* Synthetic data generation is an open research topic

> **⊕** Alpaca (Stanford, 2023): 175 seed instructions → 52k instruction/response pairs generated
> by an existing strong model (self-instruct) → fine-tuned a 7B base model **for ~$600**. This is
> the result that made instruction-tuning accessible to everyone. Caveats worth knowing: the
> student inherits the teacher's errors, the outputs' style improves faster than the underlying
> factuality, and the teacher's terms of service may prohibit training competitors.

---

# Scalable data for SFT: quantity?
* You need very little data for SFT! ~few thousands
* Just learns the format of desired answers (length, bullet points, style, etc...)
    * The knowledge is already in the pretrained LLM!
    * Specializes to one "type of user"

> **⊕ The Superficial Alignment Hypothesis** (LIMA, Zhou et al. 2023): 1,000 carefully curated
> examples were enough to reach competitive assistant quality. Knowledge and capabilities come
> from pretraining; SFT teaches *format and register*. **Quality and diversity beat quantity** —
> 1k excellent examples outperform 50k mediocre ones.
>
> **⚠ Do not over-generalize this.** "A few thousand examples suffice" holds for *style and
> format*. It does **not** hold for teaching genuinely new knowledge or a new skill the base
> model lacks — those need either far more data, RL, or a different tool entirely.
>
> **In practice — the decision table teams actually need:**
>
> | Symptom | Right tool |
> |---|---|
> | Model lacks *facts* (your docs, your data) | **RAG** — not fine-tuning |
> | Wrong *format/tone/schema* | Few-shot prompt first; **SFT** if the prompt gets long or latency matters |
> | Needs a *new skill/behavior* | Large SFT set + preference optimization |
> | Task is *verifiable* (code, math, SQL) | RL with a verifier/unit tests |
> | Too slow / too expensive | Distill a large model into a small fine-tuned one |
>
> The single most common and most expensive mistake in applied projects is fine-tuning to inject
> knowledge that should have been retrieved.

---

# RL from Human Feedback (RLHF)
* Problem: SFT is behavior cloning of humans
    1. Bound by human abilities: humans may prefer things that they are not able to generate
    2. Hallucination: cloning correct answer teaches LLM to hallucinate if it didn't know about it!
    3. Price: collecting ideal answer is expensive

* Idea: maximize human preference rather than clone their behavior
* Pipeline:
    1. For each instruction: generate 2 answers from a pretty good model (SFT)
    2. Ask labelers to select their preferred answers
    3. Finetune the model to generate more preferred answers

> **⊕ Why point 2 is the deep one.** If an SFT target contains a fact the model does not know,
> gradient descent cannot make it "know" it — it can only make it *more likely to state
> confident facts it has no support for*. SFT on correct-but-unknown answers therefore actively
> trains hallucination. Preference learning avoids this because it scores what the model
> *actually produced*, so "I'm not sure" can be rewarded. Also note the asymmetry that makes the
> whole approach work: **judging is easier than generating** — annotators can reliably rank two
> summaries they could not have written.

---

# How? RLHF: PPO
* Idea: use reinforcement learning -> But is it modelled as an MDP? How?
* What is the reward?
    * Option 1: whether the model's output is preferred to some baseline
        * Issue: binary reward doesn't have much information -> sparse
    * Option 2: train a reward model R using a logistic regression loss to classify preferences (Bradley-Terry model 1952):
        $$
        p(i>j) = \frac{exp(R(x, \hat{y}_i))}{exp(R(x, \hat{y}_i))+exp(R(x, \hat{y}_j))}
        $$
        * Use logits R(...) as reward -> continuous information -> rich information
* Optimize $\mathbb{E}_{\hat{y}\sim p_\theta(\hat{y}|x)} [R(x, \hat{y})-\beta \log \frac{p_\theta(\hat{y}|x)}{p_{ref}(\hat{y}|x)}]$ using PPO -> regularization avoids overoptimization

### ⊕ Complement: the MDP, the reward model, and why the KL term is not optional

**The MDP formulation.** State $s_t = (x, y_{1:t-1})$ = prompt plus tokens generated so far.
Action $a_t = y_t$ = the next token, so the action space *is* the vocabulary. Transitions are
deterministic (append the token). The episode ends at EOS. Reward is **terminal only** — you
learn whether the answer was good after the whole thing is written. That extreme sparsity is
precisely why a value function / advantage estimation is needed.

**Bradley–Terry, simplified.** Dividing numerator and denominator by $\exp(R_i)$:
$$
p(y_i \succ y_j) = \sigma\big(R(x,y_i) - R(x,y_j)\big), \qquad \sigma(z)=\frac{1}{1+e^{-z}}
$$
so the reward-model training loss is just logistic regression on the reward *difference*:
$$
\mathcal{L}_{RM} = -\mathbb{E}_{(x,y_w,y_l)}\left[\log \sigma\big(R(x,y_w)-R(x,y_l)\big)\right]
$$
Two things follow. (a) Only *differences* are identified — $R$ is defined up to an additive
constant per prompt, so absolute reward values are meaningless. (b) Architecturally, $R$ is
usually the SFT model with the LM head replaced by a scalar head, trained for ~1 epoch.

**Why the KL penalty.** The reward model is a *learned approximation* valid only near the
distribution it was trained on. Optimize against it hard enough and the policy finds its
blind spots — **reward hacking**. Observed in the wild: exploding response length, excessive
markdown headers and bullet points, flattery/sycophancy, hedging boilerplate. The term
$-\beta \log\frac{p_\theta}{p_{ref}}$ is a per-token leash keeping the policy near the SFT
model, where the reward model is still trustworthy. $\beta$ is *the* central knob: too high →
nothing changes; too low → a confident, verbose, useless model.

**In practice:** monitor mean KL from the reference model and mean response length during RLHF
the way you monitor loss during pretraining. Both rising fast = reward hacking, not progress.

---

# RLHF. PPO Challenges
* Problem: RL in theory simple, in practice messy (clipping, rollouts, outer loops, ...)
* Instead of reward, we use advantages
$$
\hat{A}_t^{GAE(\gamma, \lambda)} \coloneq \sum_{l=0}^\infty (\gamma \lambda)^l \delta_{t+l}^V \quad \text{where } \delta_{t+l}^V = r_{t+l} + \gamma V(s_{t+l+1})-V(s_{t+l})
$$
> GAE -> Generalized Advantage Estimation

### ⊕ Complement: advantages, clipping, and the engineering cost

**Why advantage instead of reward.** $A(s,a) = Q(s,a) - V(s)$ answers "was this token better
than what I'd normally do here?" rather than "was the reward large?". Subtracting the baseline
$V(s)$ leaves the gradient unbiased but **drastically reduces its variance** — without it,
policy-gradient training on sparse terminal rewards is hopeless.

**What GAE's $\lambda$ does.** It interpolates between two estimators:
- $\lambda = 0$: $\hat{A}_t = \delta_t$ — one-step TD. Low variance, high bias (trusts $V$).
- $\lambda = 1$: $\hat{A}_t = \sum \gamma^l r_{t+l} - V(s_t)$ — Monte Carlo. Unbiased, high variance.

$\lambda \approx 0.95$ is the usual bias-variance compromise. For LLMs $\gamma = 1$ is typical
(a response is one short episode; there is no reason to discount the end of an answer).

**PPO's clipped objective** — the part that makes it stable:
$$
\mathcal{L}^{CLIP} = \mathbb{E}_t\Big[\min\big(\rho_t \hat{A}_t,\; \mathrm{clip}(\rho_t, 1-\epsilon, 1+\epsilon)\hat{A}_t\big)\Big], \qquad \rho_t = \frac{\pi_\theta(a_t|s_t)}{\pi_{\theta_{old}}(a_t|s_t)}
$$
The clip removes the incentive to move the policy far from the data-collecting policy in a
single update, which is what lets you reuse each batch of rollouts for several gradient steps.

**Why this is painful in practice — the memory bill.** PPO holds **four** models: policy
(trained), reference (frozen), reward model (frozen), value model (trained). Roughly 2× the
memory of SFT plus a generation server for rollouts, and a training loop where generation,
scoring, and optimization must be pipelined. This engineering burden — not the theory — is the
real reason DPO took over open-source.

---

# RLHF: DPO
* Idea: maximize probability of preferred output, minimize the other
$$
\mathcal{L}(\pi_\theta; \pi_{ref}) = - \mathbb{E}_{(x, y_w, y_l) \sim \mathcal{D}} \left[\log \sigma \left(\beta \log \frac{\pi_\theta (y_w|x)}{\pi_{ref} (y_w|x)} - \beta \log \frac{\pi_\theta (y_l|x)}{\pi_{ref} (y_l|x)}\right) \right]
$$
DPO: Direct Preference Optimization
* This is ~equivalent (same global minima) to RLHF/PPO
* Much simpler than PPO and performs as well -> standard in open source community

### ⊕ Complement: where that loss comes from (3 lines), and its known failure modes

**Step 1 — solve the KL-regularized objective in closed form.** Maximizing
$\mathbb{E}_{y\sim\pi}[R(x,y)] - \beta D_{KL}(\pi \| \pi_{ref})$ over *all* distributions $\pi$ has
the exact solution
$$
\pi^*(y|x) = \frac{1}{Z(x)}\pi_{ref}(y|x)\exp\!\left(\frac{R(x,y)}{\beta}\right)
$$
(a Gibbs/Boltzmann distribution — reward tilts the reference distribution).

**Step 2 — invert it.** Solve for the reward:
$$
R(x,y) = \beta \log\frac{\pi^*(y|x)}{\pi_{ref}(y|x)} + \beta \log Z(x)
$$

**Step 3 — substitute into Bradley–Terry.** BT only depends on the *difference*
$R(x,y_w) - R(x,y_l)$, so the intractable $\beta\log Z(x)$ **cancels exactly**. What remains is
the DPO loss above. The insight: *the language model is secretly its own reward model*, with
implicit reward $\hat{r}_\theta(x,y) = \beta\log\frac{\pi_\theta(y|x)}{\pi_{ref}(y|x)}$. No reward
model, no rollouts, no value network — just a supervised-style loss over preference pairs.

**Reading the gradient:**
$$
\nabla_\theta \mathcal{L}_{DPO} = -\beta\,\mathbb{E}\Big[\underbrace{\sigma\big(\hat{r}_\theta(y_l)-\hat{r}_\theta(y_w)\big)}_{\text{how wrong the current ranking is}}\big(\nabla\log\pi_\theta(y_w) - \nabla\log\pi_\theta(y_l)\big)\Big]
$$
Pairs the model already ranks correctly contribute almost nothing; misranked pairs dominate.
Automatic curriculum, for free.

**Known failure modes (worth knowing before using it):**
- DPO optimizes the *margin*, so it can **decrease the probability of both** $y_w$ and $y_l$ —
  the model gets better at ranking while getting worse at generating. Common fix: add an NLL term
  on $y_w$ (RPO/CPO).
- **Off-policy staleness**: DPO trains on a fixed preference dataset, whereas PPO samples from
  the current policy. This gap is the main reason PPO still wins at the frontier. *Iterative /
  online DPO* (regenerate pairs from the current model each round) largely closes it.
- **Length bias**: preferred answers in human data tend to be longer → DPO amplifies verbosity.
  SimPO (length-normalized, reference-free) targets this.
- Variants worth knowing: **IPO** (regularizes the margin against overfitting), **KTO** (needs
  only good/bad labels, no pairs — much cheaper to collect).

**In practice:** DPO is the default for any team without dedicated RL infrastructure — two
models in memory, a standard training loop, and it runs on the same stack as SFT. Budget the
effort where it belongs: **collecting good preference data is the hard part; the optimizer is
not.**

---

### ⊕ Complement: what came after this lecture (2024 → today)

The lecture ends at PPO/DPO. Three developments have since reshaped post-training:

1. **RLVR — RL with Verifiable Rewards.** For math, code and other checkable domains, replace
   the learned reward model with a *program*: unit tests, a symbolic checker, exact-match on a
   final answer. No reward model means **no reward-model hacking**, and the signal is exact.
   This is the engine behind modern reasoning models.
2. **GRPO (Group Relative Policy Optimization).** Drop the value network entirely: sample $G$
   answers per prompt and use the group as its own baseline,
   $\hat{A}_i = (r_i - \mu_r)/\sigma_r$. Four models become two, and the memory problem that
   made PPO painful largely disappears.
3. **Test-time compute as a second scaling axis.** Training a model to produce long
   chain-of-thought before answering means accuracy now scales with *inference* tokens, not just
   with $N$ and $D$. **In practice** this changes the cost model: quality becomes a per-request
   dial you can trade against latency and price, rather than a property fixed at training time.

Also relevant: **Constitutional AI / RLAIF**, where an AI generates the preference labels
against a written set of principles — cheaper than human labeling and far easier to audit and
version, since the "constitution" is a document you can read and diff.

---

# Evaluation: aligned LLM
* How do we evaluate something like ChatGPT?
* Challenges:
    * There is no single correct answer
    * Large diversity (Generation, Open QA, Brainstorming, Chat, Summarization, Classification, Closed QA, Extract, etc)
    * Open-ended tasks -> hard to automate
* Idea: ask for annotator preference between answers

# Human evaluation: eg ChatBot Arena
* Idea: have users interact (blinded) with two chatbots, rate which is better
* Problem: cost & speed

> **⊕ Note the loop closing.** Chatbot Arena aggregates pairwise votes into ratings using the
> **same Bradley–Terry model** used to train the reward model. Reward modeling and leaderboard
> ranking are the same mathematics applied at two different points of the pipeline — that is why
> the arena score is, in effect, a giant externally-held reward model.
>
> Caveats: thousands of votes are needed for tight confidence intervals; ratings are **not**
> comparable across time as the user population shifts; and votes are confounded by **style**
> (length, formatting, confidence), which is why style-controlled leaderboards now exist.

---

# LLM evaluation: eg AlpacaEval
* Idea: use LLM instead of human
* Steps:
    * For each instruction: generate output by baseline and model to eval
    * Ask GPT-4 which output is better
    * Average win-probability -> win rate

* Benefits:
    * 98% correlation with ChatBot Arena -> similar to human preferences

### ⊕ Complement: LLM-as-a-judge — biases and how to neutralize them

AlpacaEval: 805 instructions, a fixed baseline model, win rate judged by a strong LLM. The 0.98
correlation with Chatbot Arena refers to the **length-controlled** version (AlpacaEval 2.0 LC) —
the uncontrolled version was gameable to the point that *a model that simply always answered at
length* could climb the leaderboard.

| Bias | Mitigation |
|---|---|
| **Position** — judges favor the first (or second) option | Evaluate both orderings, average |
| **Length/verbosity** — longer looks better | Length-controlled scoring, or cap output length |
| **Self-preference** — a judge prefers its own family's outputs | Use a judge from a different family than the model under test |
| **Style over substance** — formatting and confidence beat correctness | Rubric-based grading with explicit criteria; require a reference answer |

Other standard harnesses: **MT-Bench** (multi-turn, 1–10 absolute scoring), **Arena-Hard**
(harder prompts mined from real arena traffic).

**In practice:** LLM-as-judge is ~1000× cheaper and faster than human evaluation and, once
de-biased, correlates well enough to drive day-to-day decisions. The production recipe:
*pairwise* comparison (not absolute scores — they are poorly calibrated), *both orderings*,
a *different model family* as judge, a *fixed rubric*, and a small human-labeled subset used
periodically to verify the judge still agrees with humans. Then wire it into CI so every prompt
or model change is scored automatically before it ships.

---

## ⊕ Numbers worth memorizing

| Quantity | Value |
|---|---|
| Token ↔ text (English) | 1 token ≈ 4 chars ≈ 0.75 words |
| Training compute | $C \approx 6ND$ FLOPs |
| Inference compute | $\approx 2N$ FLOPs per generated token |
| Compute-optimal data | $D \approx 20N$ tokens (Chinchilla) |
| Inference-optimized | $D/N$ in the hundreds–thousands (Llama-3 style) |
| Perplexity range | $[1, \|V\|]$; good web-text loss ≈ 1.7–2.2 nats |
| Common Crawl yield | ~1% of raw data survives filtering |
| SFT dataset size | $10^3$–$10^5$ examples; quality ≫ quantity |
| Post-training compute | <1% of pretraining |
| MMLU random baseline | 25% (4 options) |
| Typical vocab size | 32k–256k |

## ⊕ Key references

- **Transformer** — Vaswani et al. 2017, *Attention Is All You Need*
- **BPE** — Sennrich et al. 2016 (Gage 1994 for the original compression algorithm)
- **Byte-level BPE** — Radford et al. 2019 (GPT-2)
- **Scaling laws** — Kaplan et al. 2020; **Hoffmann et al. 2022** (Chinchilla, the corrected one)
- **Data** — Gopher (Rae et al. 2021), RefinedWeb (Penedo et al. 2023), FineWeb (2024),
  Deduplication (Lee et al. 2021), DoReMi (Xie et al. 2023)
- **InstructGPT / RLHF** — Ouyang et al. 2022 (the canonical SFT → RM → PPO paper)
- **PPO / GAE** — Schulman et al. 2017 / 2015
- **DPO** — Rafailov et al. 2023
- **LIMA** — Zhou et al. 2023 (Superficial Alignment Hypothesis)
- **Constitutional AI** — Bai et al. 2022
- **Chatbot Arena** — Chiang et al. 2024; **AlpacaEval LC** — Dubois et al. 2024
- **GRPO / RLVR** — DeepSeekMath (Shao et al. 2024), DeepSeek-R1 (2025)
