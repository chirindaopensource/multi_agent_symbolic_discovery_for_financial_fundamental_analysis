# Rigorous Summary and Critical Appraisal

## *Self-Evolving Multi-Agent Symbolic Discovery for Financial Fundamental Analysis* (MUFASA)

---

## 0. Bibliographic Record and Scope of This Review

| Item | Detail |
|---|---|
| **Title** | *Self-Evolving Multi-Agent Symbolic Discovery for Financial Fundamental Analysis* |
| **Authors** | Kelvin J. L. Koa (NUS; Asian Institute of Digital Finance), Filip Orestav (KTH Royal Institute of Technology), Shengqiong Wu (Oxford), Michael J. Wooldridge (Oxford), Ke-Wei Huang (NUS; AIDF) |
| **Identifier** | arXiv:2609.32746v1 [cs.MA], 26 September 2026 |
| **Length** | 22 pages: 7 pages of main text, 1 page of references, 14 pages of appendices (A–H) |
| **Framework name** | **MUFASA** — *M*ulti-agent *U*nderstanding of *F*undamental *A*nalysis with *S*ymbolic *A*daptive learning (rendered in the paper as "Multi-Agent Fundamental Analysis with Symbolic Adaptive learning") |

**Scope.** This document summarises the paper's motivation, formal problem statement, architecture, experimental protocol, empirical findings (main and appendix), and theoretical claims, and then subjects the evidence to an econometric and methodological audit. All numbers quoted are transcribed from the paper's tables and re-verified arithmetically; every reproduction I performed is documented in **Appendix A**, and every discrepancy I found is flagged explicitly and kept distinct from the authors' own claims. Where the paper is silent, ambiguous, or internally inconsistent, I say so rather than inferring.

---

# EXECUTIVE SUMMARY

**The central thesis.** The paper argues that *financial valuation is not an ordinary symbolic regression (SR) problem*, and that off-the-shelf SR — including state-of-the-art LLM-driven SR developed for the physical sciences — is **structurally misaligned** with it. The authors identify three defining properties of the financial setting that break the assumptions of scientific SR:

1. **Multiple valid perspectives (equifinality).** There is no single ground-truth equation. Several valuation philosophies — earnings-based, cash-flow-based, growth-based, book-value-based, quality/residual-income-based — can each be simultaneously valid descriptions of asset prices. A search for one universal expression therefore under-explores the hypothesis space and generalises poorly across regimes.
2. **Non-stationary environments.** The mapping from accounting signals to outcomes varies by market regime (bull/bear) and by firm sector, so a fixed action yields a context-dependent reward and past experience does not transfer cleanly.
3. **Noisy, continuous feedback.** Candidate expressions are scored on continuous, noisy performance measures rather than binary correctness, so memory systems that distil lessons from pass/fail signals risk attributing success to noise.

The authors stress that these three properties **compound** along the self-evolving loop, each making the others harder (Figure 1).

**The proposal.** **MUFASA** is a hierarchical, self-evolving multi-agent framework with three coupled components, one per challenge:

- **(i) Disentangled symbolic discovery.** A pool of LLM agents, each *constrained to a distinct valuation philosophy* (inductive bias over variables and functional structure), independently proposes, retrieves data for, executes, optimises, and scores symbolic expressions. Evaluated equations are executable programs, coefficients are fitted numerically by **differential evolution**, and fitness is MAPE against look-ahead prices. Literature-anchored priors thus replace the single universal search space.
- **(ii) Hierarchical-level reasoning.** A **meta-coordinator agent** conditions on context $C(i,t) = (s(i), r(t))$ — sector and market regime — to select a subset of specialist agents and assign them weights $\tilde{w}_{C(i,t)}$ via **SLSQP constrained optimisation**, producing an aggregated valuation $\hat{y}_{i,t+1} = \tilde{w}_{C(i,t)}^\top \hat{y}_{i,t+1}$. This is a context-conditional, constrained **forecast combination** layer.
- **(iii) Statistical performance memory.** Each agent's memory stores, alongside each explored equation, a seven-category *statistical profile* — accuracy (mean/median MAPE), stability (SD, IQR, CV), tail risk (p90/p95 error, worst-decile mean), complexity (variable/operator counts, coverage), bias (mean signed percentage error, MSPE), ranking (Spearman correlation), and calibration (signed error by actual-price quartile). Distilled learnings $\mathcal{Z}^{(a)}$ are then used to condition subsequent hypothesis generation, so the loop learns from *distributional* rather than *binary* feedback.

**Headline empirical result.** Across five equity markets (S&P 500, Russell 2000, STOXX 600, FTSE Asia Pacific ex-Japan, CSI 300), MUFASA attains the lowest MAPE of all seventeen reported competitors, with an all-market average MAPE of **0.5081** versus **0.6351** for the strongest baseline on average (PySR). Verbatim headline numbers from the paper:

| Market | MUFASA MAPE | Best competing model | Margin (absolute) | Margin (relative) |
|---|---|---|---|---|
| S&P 500 | **0.4465** | LLM-SR 0.4761 | 0.0296 | 6.22% |
| Russell 2000 | **0.5718** | FinVision 0.5842 | 0.0124 | 2.12% |
| STOXX 600 | **0.5064** | EV/EBIT 0.6099 | 0.1035 | 16.97% |
| FTSE Asia Pacific | **0.5814** | FinCon 0.6358 | 0.0544 | 8.56% |
| CSI 300 | **0.4343** | PySR 0.5215 | 0.0872 | 16.72% |
| **Average** | **0.5081** | best all-market average: PySR 0.6351 | 0.1270 | 20.00% |

*(Relative margins in the table above are my own computation from Table 2, not the authors'; see Appendix A. Mean relative gain over the best per-market baseline is 10.12%.)*

**What the paper adds beyond raw accuracy.** (a) **Economic interpretability**: the discovered S&P 500 expressions recover adapted forms of the earnings multiple, discounted cash flow, book multiple, relative valuation, and residual income models (Table 4), whereas baselines either reproduce a single textbook formula (Fin-R1) or produce opaque expressions (PySR). (b) **Statistical robustness**: Diebold–Mariano tests with Newey–West HAC and Harvey–Leybourne–Newbold small-sample corrections show MUFASA's loss differential is negative (better) in all 60 reported pairwise comparisons, 58 of them at $p<0.001$ (Table 5). (c) **Released artifacts**: discovered equations for every market, meta-coordinator weights, and the distilled learnings $\mathcal{Z}^{(a)}$ from all five agent types.

**My overall assessment (stated up front, defended in §8).** The paper is a coherent, well-engineered *systems* contribution with an unusually honest articulation of *why* the finance domain differs from scientific SR, and its ablations are designed to isolate each architectural component. The empirical case is, however, **weaker than the framing suggests** in four specific respects: (i) the target is a **price level**, an integrated, right-skewed variable, and no naive random-walk/last-price benchmark, no log-price specification, and no out-of-sample $R^2$ are reported, so the economic magnitude of a MAPE of 0.45 is uninterpretable; (ii) the Diebold–Mariano entries in Table 5 **cannot be reconciled** with the MAPE values in Table 2; (iii) the claimed **19.65% average improvement** is not reproducible from the published tables (I obtain 19.47% or 20.00% under two natural definitions); (iv) the search loop's **sample discipline** (whether agents and the meta-coordinator ever see held-out data) is never stated, and ex-post regime labelling is a real leakage channel. These are fixable reporting gaps, not falsifications, but they matter for a paper whose central claim is *forecasting* superiority. Full details in §8 and Appendix A.

---

# BODY

## 1. Step One — Reconstructing the Problem Statement Precisely

The paper's formal setup (§*Problem Formulation*) is a **context-conditional, variable-selecting, interpretable regression** problem:

> Given a universe of companies and an accounting information database $X_t$ at time $t$, produce valuations for each company $i$ evaluated against look-ahead stock prices $y_{i,t+1}$, by identifying an interpretable symbolic expression $\tilde f$ that explains how valuations derive from accounting data.

Formally, the model seeks explanatory variables $\hat x_{i,t}$ and context-dependent expressions $\tilde f_{C(i,t)}$ such that

$$\tilde f_{C(i,t)}\big(\hat x_{i,t}\big) \approx y_{i,t+1}, \qquad \forall i,t, \tag{1}$$

with $C(i,t) = \big(s(i),\, r(t)\big)$ denoting company sector and market regime.

**Three departures from textbook SR** are made explicit and are the paper's sharpest conceptual contribution:

- **Endogenous variable selection.** Unlike SR benchmarks where inputs are given, the relevant regressors $x_{i,t} \subseteq X_t$ are *not specified a priori*; they must be discovered from a large accounting database during the search. This makes the hypothesis space a product of (variable subset) × (functional form) × (coefficients), and it introduces retrieval failure as a first-class error mode.
- **Context dependence of the law itself.** $\tilde f$ may vary with $C(i,t)$; equivalently, the paper relaxes the assumption of a single invariant governing equation to a *family* $\{\tilde f_c\}_{c}$ indexed by context.
- **Triple objective.** Goodness of fit, **out-of-sample generalisability**, and **interpretability** are jointly required — an explicit rejection of pure predictive machine learning in the tradition of Shmueli's *To Explain or to Predict?* (2010).

**Econometric reading.** In my assessment this is best understood as estimation of a **non-linear, context-dependent pricing kernel over accounting characteristics**, i.e., a generalisation of cross-sectional characteristic-based return prediction (Fama–French 1992; Asness–Liew–Stevens 1997) in which (a) the functional form is not imposed linearly, (b) the characteristic set is selected, and (c) the combination weights are conditioned on regime and sector. Note the crucial difference from standard asset-pricing practice: the target is the **price level**, not the return. That choice has material consequences (§8.3), and the paper does not discuss them.

---

## 2. Step Two — Positioning Against Prior Work

The paper organises three literatures and identifies a precise gap in each.

**2.1 Financial fundamental analysis.** Traditional FA estimates intrinsic value from accounting information (Bauman 1996; Graham–Dodd 1951; Graham 2003) with competing schools — value investing (Buffett–Cunningham 2001), factor investing (Fama–French 1992; Asness et al. 1997), macro-trend investing (Dalio 2018) — whose analyses use different information and can yield different outcomes. Deep learning approaches (Xu–Cohen 2018; Hu et al. 2018; Lin et al. 2021) sacrifice interpretability, whereas finance practice prizes economic interpretability (Shmueli 2010). Recent financial LLMs (Fin-R1, Fino1) provide interpretable reasoning over structured accounting data but **perform financial QA, not forecasting or valuation**. *Gap: no framework both forecasts and yields economically interpretable valuation relationships.*

**2.2 Symbolic regression.** Classical SR uses evolutionary/genetic programming over expression trees (Schmidt–Lipson 2009a,b) and suffers from enormous search spaces and computational inefficiency. LLM-guided SR (Grayeli et al. 2024; Shojaee et al. 2025, LLM-SR) and program-search methods (Romera-Paredes et al. 2024, FunSearch; Novikov et al. 2025, AlphaEvolve; Xie et al. 2026) inject learned scientific priors and excel at **rediscovering physical laws**. *Gap: all of these assume a single, stable, objectively correct governing equation, and none encodes multiplicity of valid perspectives, non-stationarity, or continuous noisy feedback.*

**2.3 Self-evolving LLM agents.** From tool-using agents (ReAct, Toolformer) through self-reflection (Reflexion, STaR) and agent memory (ReasoningBank, MemEvolve) to self-evolving multi-agent systems (EvoAgentX, AgentEvolver, Agent0, AgentOrchestra, Alita). *Gap: existing memories distil lessons from **binary** success/failure or scalar rewards; in finance the signal is continuous, heavy-tailed, and confounded by the environment, so such memories misattribute success to spurious patterns.*

**Assessment.** The positioning is accurate and well-cited; the claim that *"scientific priors encoded by LLMs may be less useful in finance, where relationships are context-dependent and lack stable governing laws"* is, in my view, the most intellectually interesting hypothesis in the paper, and — importantly — the authors later corroborate it empirically by reporting that **PySR beats both FunSearch and LLM-SR on average** (0.6351 vs 0.7991 and 0.7271), i.e., the LLM-prior advantage that holds in physics does not transfer to finance. That is a genuine, falsifiable, and falsified prediction about method transfer.

---

## 3. Step Three — Component (i): Disentangled Multi-Perspective Discovery

**Mechanism.** Instead of one agent searching one space, a set of **valuation philosophies** $a$ is defined, each constraining the hypothesis space and inducing inductive biases over preferred variables and structural patterns — explicitly to *"prevent the collapse of expression diversity."* Each philosophy is embodied in an LLM agent $\pi_\theta$ that operates autonomously with four capabilities.

- **Hypothesis generation (Eq. in §*Disentangled Symbolic Discovery*).** A new hypothesis is sampled as
 $\tilde f^{(a)} \sim \pi_\theta\big(\cdot \mid p^{(a)}\big)$,
 where the prompt $p^{(a)}$ encodes both the investing philosophy $a$ and the **accumulated learnings** $\mathcal{Z}^{(a)}$ distilled from historical interactions and statistical feedback. Note that this is where Components (i) and (iii) couple: the perspective constrains the prior, the memory shapes the posterior over structures.
- **Tool use — data retrieval.** The candidate expression implicitly names variables; the agent queries a **semantic retrieval** mechanism over the accounting database for candidate variable names/descriptions, then selects and retrieves the corresponding series. Failures (unavailability, insufficient coverage) return **structured feedback** (Toolformer-style) into the prompt, and the agent adapts either the variable set or the expression.
- **Tool use — code evaluation.** Each expression is an **executable program** evaluated as $\hat y^{(a)}_{i,t+1} = \tilde f^{(a)}\big(x^{(a)}_{i,t}\big)$ (Eq. 2). Execution failures — syntax errors, invalid operations, non-finite outputs — return structured feedback (PAL/Gao et al. 2023) and trigger revision.
- **Hypothesis optimisation and assessment.** Following LLM-SR, any **scalar multipliers or parameters are treated as continuous variables and fitted directly on the training data by differential evolution** (Storn–Price 1997). This **decouples structure discovery from parameter fitting**: the LLM defines the functional form; a numerical routine fits its constants. Fitness is
 $$\mathcal{L}^{(a)} = \mathrm{MAPE}\big(\hat y^{(a)}_{i,t+1},\, y_{i,t+1}\big). \tag{3}$$
 Critically, fitness is measured against **the common look-ahead price target**, not against a philosophy-specific proxy — so agents are not rewarded for internal consistency, but for generalisable predictive value. The full loop is Algorithm 1 (Appendix A).

**Econometric reading.** Each philosophy is a **constrained function class** $\mathcal{F}_a \subset \mathcal{F}$; the LLM acts as a *structure-proposing* prior, and differential evolution performs **non-linear least squares on the continuous parameters**. Maximising MAPE-fitness is equivalent to a **relative-loss** (multiplicative-error) criterion, implicitly positing $y = \tilde f(x)\cdot(1+\varepsilon)$ — a specification consistent with price-level targets but one whose statistical consequences (§8.3) go undiscussed. The disentanglement argument is essentially a **Rashomon/equifinality** argument: restricting each learner to a coherent sub-hypothesis-space improves the conditioning and interpretability of the search while preserving diversity across learners.

---

## 4. Step Four — Component (ii): Hierarchical-Level Reasoning

**Problem addressed.** Non-stationarity makes the *solution-to-reward mapping* unstable: the same structural move can help in a bull market and hurt in a bear market, so experience fails to accumulate and naive reuse is harmful.

**Mechanism.** A **meta-coordinator** $\pi_\phi$ reasons at a **higher hierarchical level** than the specialists. For each context $C(i,t)$, it constructs a prompt $p_{\text{meta}}$ containing (i) the current context, (ii) the agent-level performances $\mathcal{L}^{(a)}$, and (iii) its own accumulated learnings $\mathcal{Z}_{\text{meta}}$; it **selects a subset of agents**, then computes the weight vector $\tilde w_{C(i,t)}$ by **SLSQP-based constrained optimisation** (Kraft 1988). Aggregation is a weighted combination:

$$\hat y_{i,t+1} = \tilde w_{C(i,t)}^\top \cdot \hat y_{i,t+1}, \tag{4}$$

where $\hat y_{i,t+1}$ on the right is the vector stacking $\hat y^{(a)}_{i,t+1}$ over the selected agents (the paper reuses the same symbol on both sides; see §8.5). Its own quality is scored $\mathcal{L}_{\text{meta}} = \mathrm{MAPE}(\hat y_{i,t+1}, y_{i,t+1})$ (Eq. 5), and the loop is Algorithm 2.

**Econometric reading.** Equation (4) is a **constrained linear forecast combination** — a stacked ensemble in the Bates–Granger / Stock–Watson tradition — with the crucial twist that the combination weights are **conditioned on sector × regime**. SLSQP on a constrained least-squares problem is the computational embodiment of the standard constraint set for combination weights (typically non-negativity and summation to one; the paper does not state the constraints used — see §8.5). The hierarchical design thereby converts a single non-stationary regression into a **regime-/sector-indexed family of combination problems**, which is the standard econometric remedy for parameter instability (analogous to threshold or state-dependent weighting schemes).

---

## 5. Step Five — Component (iii): Statistical Performance Memory

**Problem addressed.** Binary success/failure memory cannot distinguish a genuinely robust expression from one that scored well by luck on a noisy sample; a scalar loss discards precisely the information needed to tell them apart.

**Mechanism.** Memory stores each hypothesis **together with a structured statistical summary** (Table 1). The seven categories are:

| Category | What is stored | Why it matters (paper's rationale) |
|---|---|---|
| **Accuracy** | Mean MAPE, Median MAPE | Overall accuracy, robust to outliers and skew |
| **Stability** | Standard deviation, IQR, coefficient of variation | Consistency of performance across samples/time |
| **Tail risk** | p90/p95 error, worst-decile mean | Exposes extreme failure modes hidden by averages |
| **Complexity** | Variable + operator count, prediction coverage | Interpretability and numerical reliability |
| **Bias** | Mean Signed Percentage Error (MSPE) | Systematic over-/under-prediction vs isolated errors |
| **Ranking** | Spearman rank correlation | Cross-sectional ordering, beyond absolute scale |
| **Calibration** | Signed percentage error by actual-price quartile | Systematic mispricing of cheap vs expensive stocks |

These profiles are distilled into learnings $\mathcal{Z}^{(a)}$ that condition hypothesis generation. The paper's justification is statistical: *"by aggregating outcomes across repeated evaluations, the system can recover more reliable estimates of relative performance, including properties such as variance and tail behavior that are not observable from isolated observations."*

**Assessment.** This is, in my view, the strongest *idea* in the paper. It is a principled response to weak supervision: it replaces a point estimate of quality with a **risk profile of the estimator**. Including Spearman and by-quartile MSPE is econometrically well-motivated, because for a cross-sectional valuation model the *ranking* and the *directional bias by price tier* matter more than the level error. Appendix E shows the mechanism working in practice: the agents autonomously discover facts such as *"SECTOR_MEDIAN_EV_EBITDA is unstable in asset-light companies due to denominator effects"* and *"ignoring negative cash flow via `max()` leads to systematic underestimation in early-stage firms"* — exactly the kind of denominator-induced instability an econometrician would anticipate, recovered without explicit instruction.

---

## 6. Step Six — Experimental Design

**6.1 Data.** Five equity markets, with quarterly resolution (justified by the long-horizon nature of fundamental analysis, per Graham 2003):

| Market | Period (as stated) | Role |
|---|---|---|
| S&P 500 | 1990 Q1 – 2023 Q2 (primary) | US large cap |
| Russell 2000 | 1990 – 2025 | US small cap |
| STOXX 600 | 1995 – 2025 | Europe |
| FTSE Asia Pacific ex-Japan | 1996 – 2025 | Asia-Pacific |
| CSI 300 | 2002 – 2021 | China |

Fundamentals from **Bloomberg**, macro data primarily from **FactSet**, index prices for regime labelling from **Yahoo Finance**. Three design choices deserve credit: (i) **constituent entry/exit dates are included to prevent survivorship bias**; (ii) **only original quarterly filings are used, preventing look-ahead bias from subsequent restatements** — a point-in-time discipline that many empirical asset-pricing papers neglect; (iii) the **target is the stock price at the end of the fiscal quarter immediately following each filing period**, which respects the information release calendar.

**6.2 Splits and regimes.** Chronological splits — first **80% of quarters train, remaining 20% test** — which is the correct discipline for time-series. Bull/bear regimes follow the standard practitioner convention (Pagan–Sossounov 2003): **bull = index risen ≥20% from most recent trough; bear = fallen ≥20% from most recent peak**, computed at index level.

**6.3 Baselines (five families, 17 models).**
1. **Traditional ML**: Random Forest (Breiman 2001), HistGBM (Ke et al. 2017, LightGBM), Neural Net (Rumelhart–Hinton–Williams 1986).
2. **Symbolic regression**: PySR (Cranmer 2023), FunSearch (Romera-Paredes et al. 2024), LLM-SR (Shojaee et al. 2025).
3. **Financial reasoning LLMs**: Fin-R1 (Liu et al. 2025), Fino1 (Qian et al. 2025).
4. **Classical valuation**: sector-median P/E, EV/EBIT, EV/EBITDA, P/B; Dividend Discount Model; FCFE; FCFF (Damodaran 2012).
5. **Financial agentic frameworks**: FinCon (Yu et al. 2024), FinVision (Fatemi–Hu 2024).

*Note:* the paper says "three categories" in the text but enumerates five (and numbers them 1–5). A typographical slip.

**6.4 Implementation.** All LLMs served locally with **vLLM** on **NVIDIA RTX A5000** GPUs; **Qwen3-4B-Thinking** for all agents; temperature **0.7** for agents and **0.3** for memory components; context window **32,768** tokens; maximum generation **16,384** tokens; **~10 minutes per agent per GPU**; metric **MAPE** (lower is better).

**Assessment of the design.** Coverage is genuinely broad: five markets on three continents, five baseline *families* (so the comparison is not a strawman against one method class), and chronological splits. The inclusion of the classical valuation models, specified exactly as practitioners would specify them, is the right control for the central claim. Two gaps stand out and are developed in §8: the absence of a **naive persistence benchmark** on a price-level target, and the absence of any **run-to-run variance** (single seed per configuration).

---

## 7. Step Seven — Empirical Findings

### 7.1 Main forecasting comparison (Table 2, MAPE)

| Model | S&P 500 | Russell 2000 | STOXX 600 | FTSE APAC | CSI 300 | All-data avg | Δ vs MUFASA avg |
|---|---|---|---|---|---|---|---|
| Random Forest | 0.4812 | 0.6551 | 0.7490 | 0.8436 | 0.5605 | 0.6579 | 0.1498 |
| HistGBM | 0.5916 | 0.8121 | 0.9774 | 1.3771 | 0.6041 | 0.8725 | 0.3644 |
| Neural Net | 0.6130 | 1.0302 | 0.8963 | 1.5292 | 0.5242 | 0.9186 | 0.4105 |
| Fino1 | 1.0230 | 2.1244 | 1.0958 | 1.2587 | 1.3388 | 1.3681 | 0.8600 |
| Fin-R1 | 0.5263 | 0.7324 | 0.7437 | 0.8862 | 0.8095 | 0.7396 | 0.2315 |
| P/E | 0.5127 | 0.8450 | 0.6209 | 0.7439 | 0.6035 | 0.6652 | 0.1571 |
| EV/EBIT | 0.5580 | 0.9907 | 0.6099 | 0.9150 | 0.6698 | 0.7487 | 0.2406 |
| EV/EBITDA | 0.5558 | 1.1589 | 0.6808 | 0.9314 | 0.6472 | 0.7948 | 0.2867 |
| P/B | 0.7177 | 0.8727 | 2.3048 | 0.8371 | 0.8401 | 1.1145 | 0.6064 |
| DDM | 0.7991 | 0.9370 | 1.0324 | 0.8691 | 0.6358 | 0.8547 | 0.3466 |
| FCFE | 0.9865 | 1.1827 | 1.3975 | 0.8700 | 0.8196 | 1.0513 | 0.5432 |
| FCFF | 1.2434 | 1.4313 | 1.5155 | 0.9097 | 0.8412 | 1.1882 | 0.6801 |
| PySR | 0.6394 | 0.5892 | 0.6741 | 0.7514 | 0.5215 | 0.6351 | 0.1270 |
| FunSearch | 0.7146 | 1.1524 | 0.7693 | 0.7855 | 0.5735 | 0.7991 | 0.2910 |
| LLM-SR | 0.4761 | 0.7822 | 0.8269 | 0.9534 | 0.5967 | 0.7271 | 0.2190 |
| FinCon | 0.9581 | 0.9746 | 1.1822 | 0.6358 | 0.5784 | 0.8658 | 0.3577 |
| FinVision | 0.8203 | 0.5842 | 1.2521 | 0.9974 | 0.9956 | 0.9299 | 0.4218 |
| **MUFASA (ours)** | **0.4465** | **0.5718** | **0.5064** | **0.5814** | **0.4343** | **0.5081** | — (avg 0.3702) |

**Verified facts.** Every "All Data Avg" and every Δ entry reproduces exactly from the per-market columns (Appendix A.1). MUFASA is the column minimum in all five markets. The second-best model differs by market, and no single baseline is consistently second: LLM-SR on S&P 500 (0.4761), FinVision on Russell 2000 (0.5842), EV/EBIT on STOXX 600 (0.6099), FinCon on FTSE APAC (0.6358), PySR on CSI 300 (0.5215).

The authors' five interpretive observations, each of which I judge to be supported by their table:

- **Fin-R1 > Fino1 consistently**, attributed to Fin-R1's greater emphasis on generalisation/transfer; both still underperform most specialised baselines. (Consistent with the data: Fin-R1's average 0.7396 vs Fino1's 1.3681.)
- **Simple valuation ratios (P/E, EV/EBIT) are competitive** across most markets. The authors' explanation — that their simple structure is robust to estimation error — is economically sensible; the marked cross-regional variation (e.g., P/B ranges from 0.7177 on S&P 500 to 2.3048 on STOXX 600) suggests, correctly in my view, that **markets price different fundamental signals**.
- **Complex DCF variants (FCFF, FCFE) perform worse**, because they require noisy inputs (growth rates, discount factors). The authors honestly attribute part of this to their own implementation choice of the **single-stage Gordon Growth Model** with constant growth, and concede better parameter estimation could improve them.
- **PySR outperforms the LLM-based SR baselines on average** — the paper's most interesting negative result, and a direct challenge to the assumption that LLM-encoded scientific priors transfer to finance. The proposed mechanism (evolutionary search better suits empirically effective but atheoretical expressions) is plausible, though the paper does not test it directly.
- **MUFASA wins everywhere**, and beats the *better* of the two financial agentic baselines (FinCon, FinVision) in every market by **27.67% on average** (reproduced exactly in Appendix A.2). Note the sizeable heterogeneity in margins: 2.12% on Russell 2000 versus 16.97% on STOXX 600.

### 7.2 Statistical significance (Table 5, Appendix B)

The authors apply the **Diebold–Mariano test** (2002) under **absolute percentage error loss** with two corrections: (i) a **Newey–West HAC** variance estimator (1987) with **Bartlett kernel** and bandwidth by **Andrews' (1991) rule**, $L = \lfloor 4(T/100)^{2/9}\rfloor$, justified by persistent autocorrelation in loss differentials across adjacent quarters; and (ii) the **Harvey–Leybourne–Newbold (1997)** small-sample correction, referring the statistic to a $t_{T-1}$ distribution rather than the standard normal — a well-chosen pair of fixes given short test windows.

Results: 60 pairwise comparisons (12 baselines × 5 markets), all with **negative** loss differentials (MUFASA better). **58 are significant at $p<0.001$**; the two exceptions are **DDM on CSI 300** and **FCFE on FTSE Asia Pacific**, both at $p<0.01$. The pattern is coherent with the point estimates: the smallest margins (Russell 2000 vs FinVision/Fin-R1/P-E/PySR, all ≈0.01–0.04) are nonetheless significant, while the two $p<0.01$ cases occur where MUFASA's margin is modest (CSI 300 vs DDM: 0.4343 vs 0.6358, margin 0.20; FTSE vs FCFE: 0.5814 vs 0.8700, margin 0.29) but the loss-differential series is evidently noisier.

**However — and this is a substantive audit finding — the magnitudes in Table 5 are not reconcilable with Table 2** (see §8.4 and Appendix A.4). Signs are consistent; magnitudes are not.

### 7.3 Component ablation (Table 3)

| Variant | S&P 500 | Russell 2000 | STOXX 600 | FTSE APAC | CSI 300 |
|---|---|---|---|---|---|
| Single-perspective agent (S.P) | 0.4971 | 0.8994 | 0.7608 | 0.6095 | 0.5928 |
| Multi-perspective, equal weights (M.P-EW) | 0.4652 | 0.8768 | 0.5448 | 0.6442 | 0.5309 |
| M.P + meta-coordinator, **no** stats memory | 0.4702 | 0.7525 | 0.5398 | 0.5852 | 0.4852 |
| M.P + memory, **best single agent only** | 0.4676 | 1.9173 | 0.5256 | 0.5833 | 0.4739 |
| **MUFASA (full)** | **0.4465** | **0.5718** | **0.5064** | **0.5814** | **0.4343** |

**Verified monotonicity** (Appendix A.3): S.P is worse than M.P-EW in **4 of 5** markets (exception: FTSE APAC); M.P-EW is worse than the meta-coordinator without memory in **4 of 5** (exception: S&P 500); and the no-memory variant is worse than full MUFASA in **5 of 5**. Full MUFASA is the column minimum in every market. The paper's four component-wise conclusions therefore hold arithmetically as stated.

The most instructive row is **"best single agent only"**: it is second-best in three markets (STOXX 600, FTSE APAC, CSI 300) but collapses on Russell 2000 to **1.9173** — nearly four times MUFASA's error. Because the identity of the best agent is not knowable in advance, this row is the paper's cleanest evidence for **combination over selection** under regime uncertainty, echoing the classical forecast-combination result that weights estimated with error underperform robust combinations.

### 7.4 Memory ablation (Table 10, Appendix F)

The extended ablation crosses four architectural settings with three memory regimes: **Binary** (pass/fail signals only), **MAPE-only**, and **Full statistical memory**. For the full meta-coordinator configuration:

| Memory regime | Mean MAPE across five markets |
|---|---|
| Binary (pass/fail) | 0.5601 |
| MAPE-only | 0.5666 |
| **Full statistical** | **0.5081** |

Full statistical memory is best in **all five markets** (a claim I verified configuration-by-configuration). The aggregate gain over binary memory is ≈9.3% in relative MAPE. Interestingly, **binary memory slightly beats MAPE-only on the S&P 500 (0.4646 vs 0.4702) and on Russell 2000 (0.6445 vs 0.7525)**, so a scalar MAPE is not uniformly more informative than pass/fail — consistent with the paper's thesis that what matters is *which* statistics are conditioned on, not merely how many bits of feedback are retained. The paper's own summary claim ("full statistical memory typically results in the strongest performance") is correctly hedged with "typically."

### 7.5 Self-evolution dynamics and discovered equations

**Trajectories (Figure 3).** Per-agent best-error trajectories decline over iterations for every perspective agent, and the general single agent's terminal error remains above those of the specialised agents — consistent with the claim that disentanglement improves conditioning of the search.

**Discovered equations (Table 4, S&P 500; Tables 6–9 for other markets).** The mapping between learned expressions and canonical theory is the paper's interpretability evidence. Reproduced faithfully where the extraction is clean:

| Agent | Learned expression (S&P 500) | Closest theory form |
|---|---|---|
| Earnings | $NI_{ps}\cdot(1+0.01\,g_{EPS})\cdot PE\cdot 0.88$ | Gordon growth $\dfrac{EPS}{r-g}$ |
| Cash flow | $FCF_{ps}\cdot \dfrac{EV}{EBITDA}\cdot$ calibration constant | DCF $\sum_t \dfrac{FCF_t}{(1+r)^t}$ |
| Asset | $BVPS\cdot\left(1+1.01\frac{R\&D}{Assets}\right)\left(1-13829.10\frac{R\&D}{Assets}\right)\cdot PB-7.24\times10^{-4}$ | Book multiple $BVPS\cdot PB$ |
| Growth | $(P/FCF)_{mkt}\left(FCF_{ps}+0.29\frac{P/FCF}{(P/FCF)_{mkt}}\right)\left(1-14.80\cdot\mathbb{1}\{FCF_{ps}<1.08\}\right)\cdot 0.01$ | Relative valuation |
| Quality | $NI_{ps}\cdot P/FCF\cdot\left(1+\log(1+ROE/100)\cdot 0.87\right)$ | Residual income $BV+\sum_t \frac{(ROE_t-r)BV_{t-1}}{(1+r)^t}$ |

**Assessment.** Three things stand out. First, each agent independently recovers a *structurally correct* anchor (earnings×multiple, cash flow scaled by a multiple, book value times P/B, price relative to a market multiple, income×P/FCF), which is non-trivial and supports the disentanglement hypothesis. Second, the learned forms deviate from canonical theory through **multiplicative or piecewise correction terms** (growth caps, interaction terms, indicator functions), which the authors defend as data-driven refinements to simplifying assumptions rather than overfitting artifacts — a defensible position, though see §8.3 for the counter-argument on the very large constants (e.g., 13829.10, 852.52, 809734.00) appearing in some variants. Third, the paper reports **consistent structural patterns across markets** (Table 6–9), which is the strongest available evidence against dataset-specific artifacts; e.g., the Earnings agent recovers the Gordon-type form in all five markets, and the Quality agent recovers residual-income-like structures in all five.

**Contrast with baselines is stark and correctly characterised:** Fin-R1 essentially reproduces $EPS_{TTM}\cdot PE$ (a fixed form, one perspective only); PySR produces high-accuracy but financially opaque expressions (e.g., nested radicals of $BVPS$, $Tax$, $EPS$, $Y_{30}$); FunSearch and LLM-SR produce additive/linear weighting schemes (resembling a linear factor model) that cannot express the multiplicative structure of valuation.

### 7.6 Learned context weighting (Appendix D, Figure 4)

Heatmaps of meta-coordinator weights over sector × regime exhibit three patterns the authors highlight: (i) **sector-specific differentiation** — asset- and cash-flow-based signals receive more weight in balance-sheet-heavy sectors such as real estate, earnings-based signals in sectors with stable profitability; (ii) **regime shifts** — growth/earnings perspectives receive relatively more weight in some bullish settings, asset/cash-flow in some bearish ones; (iii) **cross-market recurrence** — similar tendencies appear in the US, European, and Asian samples, supporting generalisability over dataset-specific artifacts. The authors are appropriately careful ("not uniform… context-dependent reallocation"). Without the underlying weight matrices in numeric form, however, these are qualitative readings of heatmaps and cannot be independently verified from the text.

### 7.7 Distributional and robustness diagnostics (Appendix G)

- **Rank correlation (Figure 5).** Because learned expressions are non-linear and multiplicative, MAPE alone is an incomplete criterion — a mis-scaled multiplier inflates MAPE while preserving the true ordering. On S&P 500, **PySR achieves lower MAPE than FunSearch but lower rank correlation**, suggesting its heuristic search fits average values without preserving structure; MUFASA achieves the **highest Spearman correlation**.
- **Error percentiles (Figure 7).** Aggregate APE distributions:

| Model | 25th pct | Median | 75th pct |
|---|---|---|---|
| PySR | 0.4103 | 0.6249 | 0.8322 |
| FunSearch | 0.6136 | 0.7500 | 0.8283 |
| LLM-SR | 0.2663 | 0.4475 | 0.6086 |
| **MUFASA** | **0.1725** | **0.3382** | **0.5556** |

 MUFASA dominates at every reported quantile — which, given that its mean (0.5081) far exceeds its median (0.3382), indicates a **right-skewed error distribution**, i.e., a minority of severe misses drives the mean. This is exactly what a tail-aware memory should target, and it is consistent with the design rationale.

- **Sectoral errors (Figure 6).** MUFASA is strongest where error distributions are low *and* concentrated — **Utilities, Industrials, Real Estate, Consumer Staples** — sectors whose value is well-anchored in accounting fundamentals. It shows slightly higher upper- and lower-percentile errors in **Communication Services and Consumer Discretionary**, plausibly because these are driven by forward-looking expectations, intangibles, and sentiment rather than reported fundamentals — and the paper candidly notes news-driven jumps are outside its information set.
- **Directional bias (Figure 8, MSPE by price quartile).** Across all markets, MUFASA **overestimates cheap stocks (Q1) and underestimates expensive ones (Q4)** — i.e., it exhibits *compression toward the mean*, the classic attenuation signature of a valuation model with imperfect signal. Importantly, MUFASA's bias is **closer to zero and more stable across markets than any baseline**, and the authors correctly link this to the memory's explicit tracking of MSPE.

### 7.8 Distilled learnings (Appendix E)

Five agents' learnings are released: **Earnings, Cash Flow, Asset, Growth, Quality**. Each is structured as Summary / Key Insights / Statistical Diagnostics / What Works / What Fails / Important Variables (with observed role) / Agent Adaptation Behavior / Design Principle. Representative content:

- **Earnings agent**: needs *capped* growth; raw PE and uncapped `IS_EPS_GROWTH_YOY` cause systematic overprediction, especially a persistent Technology-sector gap; best structure $NI_{ps}\cdot PE$ with sector-aware growth cap.
- **Cash flow agent**: `SECTOR_MEDIAN_EV_EBITDA` is unstable in asset-light firms (denominator effects); truncating negative cash flow via `max()` causes systematic *underestimation* of early-stage firms; sector-adjusted EV/EBITDA with growth scaling and explicit negative-cash-flow handling works best.
- **Asset agent**: R&D intensity relative to assets is high-impact but prone to overuse; **log-based adjustments produce invalid predictions**; `BS_CUR_LIAB` as denominator breaks in asset-light firms; bounded multiplicative structures (`max(1,·)`) required.
- **Growth agent**: piecewise growth structures beat min/max formulations; `EBITDA_YOY` as standalone multiplier fails; FCF per share as a *denominator* produces invalid predictions.
- **Quality agent**: income × P/FCF with sector-agnostic growth caps; fixed PE thresholds are unstable in growth regimes; `RETURN_COM_EQY` produces invalid predictions in asset-light companies.

**The four cross-cutting conclusions the authors draw are, in my view, the paper's most transferable contribution:** (a) many formulations fail not on average accuracy but on **instability or invalid behaviour in identifiable subpopulations** — invisible to scalar loss; (b) instability is **conditional on firm type and sector**, not global, which motivates context-dependent aggregation; (c) **systematic directional bias is sector-structured** (Technology over-predicted; Consumer Discretionary extreme under-prediction), justifying regime- and sector-aware weighting; (d) high-impact variables are **rarely discarded but require structured use** (anchoring, bounding, interaction), showing that the diagnostics guide *composition*, not just elimination.

---

## 8. Step Eight — Critical Appraisal: An Econometric and Methodological Audit

This section separates (8.1) genuine strengths, (8.2) specification concerns about the target variable, (8.3) internal-consistency findings from my own re-computation, (8.4) threats to validity and unidentified design choices, and (8.5) expositional defects. I have tried to be maximally truth-seeking: praise where earned, and explicit arithmetic where the paper and its tables disagree.

### 8.1 Genuine strengths, stated precisely

1. **A correct and non-trivial problem typology.** The three-property taxonomy (multiplicity, non-stationarity, continuous noisy feedback) is not decorative: each is operationalised in a distinct architectural component, with an ablation isolating each. This is the structure of a good paper.
2. **Point-in-time discipline.** Original filings only (no restatements) and constituent entry/exit dates (no survivorship) are exactly the controls that separate credible from non-credible empirical finance, and they are implemented, not merely asserted.
3. **Chronological train/test split, with the correct direction of time.**
4. **Econometrically appropriate inference.** DM + Newey–West HAC + Andrews bandwidth + HLN small-sample correction is the right toolkit for a short-window, autocorrelated loss-differential series; many ML papers would have reported a bare t-test.
5. **An honest negative result.** Reporting that PySR beats the LLM-SR baselines on average, with a mechanistic hypothesis, is the kind of result that advances the field and is often suppressed.
6. **Baseline breadth across five distinct method families**, including the practitioner-standard valuation models specified as practitioners specify them.
7. **Interpretability demonstrated, not claimed.** Table 4's correspondence between learned expressions and canonical valuation theory is the paper's strongest evidence that the constraint structure does real work.
8. **Substantial artifact release** (equations across all markets, weights, distilled learnings), which materially lowers the cost of replication.

### 8.2 The target variable: a price level, and the missing benchmark

This is my most serious methodological reservation, and it is worth stating precisely.

- **Non-stationarity of the target.** $y_{i,t+1}$ is a *stock price level*, whereas the paper's entire framing is about non-stationary *relationships*. A price level is (near) $I(1)$. Regressing a level on accounting levels/ratios is a **balanced relationship** at best; MAPE on a level is dominated by the level's persistence rather than by the cross-sectional signal. The econometric default in this literature is to predict **returns** or **log-price changes**, or at minimum to report $R^2_{OOS}$ against a no-change forecast (Campbell–Thompson). None is reported.
- **Absence of a naive benchmark.** For a price-level target one quarter ahead, the obvious null is $\hat y_{i,t+1} = y_{i,t}$ (last observed price). No such benchmark appears anywhere in Table 2 or Table 5. Without it, a MAPE of 0.4465 cannot be judged: it may be excellent or may be *worse than doing nothing*, and the reader cannot tell. This is the single most consequential omission in the paper.
- **MAPE's properties on a skewed, bounded-below variable.** MAPE is (i) asymmetric — under-prediction is capped at 100% while over-prediction is unbounded — which biases any optimiser toward over-prediction; (ii) scale-dependent, weighting penny stocks far more heavily than high-priced stocks; (iii) undefined at $y=0$ and unstable near it. The paper reports **no winsorisation, no trimming, no median-based loss (e.g., MAE on log price), no QLIKE/MSE**, and no sensitivity to these choices. Notably, the paper's own finding that MUFASA *overestimates cheap (Q1) stocks and underestimates expensive (Q4) stocks* is exactly the directional signature that MAPE-optimisation predicts — yet it is interpreted purely as attenuation, not as a loss-function artifact. Both explanations are plausible; the paper does not distinguish them.
- **Economic translation absent.** No portfolio sort, no long-short spread, no transaction-cost analysis, no information coefficient beyond Spearman. The paper claims *valuation* rather than *strategy*, which is defensible — but then the practical significance of a 10% relative MAPE gain rests entirely on the metric's own units.

**Recommendation.** Report (a) MAPE against the random-walk benchmark, (b) MAE/RMSE on log price, (c) $R^2_{OOS}$ relative to no-change, and (d) a decile long-short return spread. Any one of these would convert the paper's central claim from plausible to established.

### 8.3 Internal-consistency findings from independent recomputation

I re-derived all aggregates from the per-market columns. Results:

- ✅ **All 17 "All Data Avg" entries and all 17 Δ entries in Table 2 reproduce exactly** (mean absolute deviation 0.00).
- ✅ **The "27.67% average reduction versus the better agentic baseline" reproduces exactly** to two decimals.
- ⚠️ **The claimed "average improvement of 19.65%" does not reproduce.** Under the natural definition — mean over markets of relative MAPE reduction versus the best SR baseline, PySR — I obtain **19.47%**; versus PySR's all-market average, **20.00%**. Under "versus the average of all baselines," **42.15%**; versus the *best* baseline per market, **10.12%**. The figure 19.65% corresponds to none of these four natural definitions. This is a reporting error, not a result reversal, but it should be corrected.
- ⚠️ **Table 5 (Diebold–Mariano) is not reconcilable with Table 2.** Because DM is applied under absolute-percentage-error loss, the mean loss differential should equal the difference of the MAPEs computed on the same observations. Comparing reported entries with implied differences from Table 2, magnitudes diverge by factors ranging from **0.14× to 3.72×** across the 25 cells I checked (signs are consistent throughout). For example, the S&P 500 versus Fino1 entry is $-0.7283$ while Table 2 implies $-0.5765$; the S&P 500 versus LLM-SR entry is $-0.1101$ while Table 2 implies $-0.0296$. Possible legitimate explanations exist — a different evaluation sample, a per-observation paired loss rather than a ratio-of-means, winsorisation, or currency/unit adjustments — but **none is stated**, and as printed the two tables describe different quantities under the same name. This must be resolved for the significance claim to be auditable.
- ⚠️ **Minor cross-table drift in Table 3 vs Table 10** for the same nominal configuration, all confined to the Russell 2000 column: S.P agent 0.8994 vs 0.8987; M.P equal weights 0.8768 vs 0.8831; M.P best-single 1.9173 vs 1.9170. Differences are ≤0.0063 and do not affect rankings, but identical runs should produce identical numbers.
- ⚠️ **The DM battery's coverage claim is overstated.** The text says *"across all pairwise comparisons, MUFASA achieves statistically significant improvements"*, but Table 5 omits **Random Forest, HistGBM, Neural Net, FinCon, and FinVision** — including the two most relevant agentic competitors, whose per-market margins on Russell 2000 (0.0124) and FTSE APAC (0.0544) are the smallest in the study. Significance should be reported for those comparisons, which are precisely the ones at risk.

### 8.4 Threats to validity and unidentified design choices

1. **Sample discipline of the self-evolving loop (critical, unresolved).** The paper never states that hypothesis generation, evaluation, and memory updates are confined to the **training window**. Algorithm 1 evaluates $\mathcal{L}^{(a)}$ against $y_{i,t+1}$ without restricting the index set; §*Disentangled Symbolic Discovery* is silent; and the meta-coordinator's weight estimation (§4, Algorithm 2) is likewise unrestricted. If the search loop can observe held-out quarters, the reported test MAPE is not an out-of-sample quantity. Given that agentic search over many iterations is a powerful adaptive procedure, this is the single most important thing to clarify, and it is a one-sentence fix.
2. **Ex-post regime labelling.** Bull/bear states are defined by the 20%-from-peak/trough rule applied to index prices. If peak/trough dates are identified with full-sample information (standard in Pagan–Sossounov implementations), the **regime label at time $t$ encodes future information**, which then flows into the meta-coordinator's weights. The paper does not state whether the labelling is point-in-time filtrated. This is a real leakage channel that would inflate the hierarchical component's contribution — note that the hierarchical component's marginal gain (M.P-EW → no-memory meta-coordinator) is the smallest of the three ablations.
3. **Context-cell proliferation.** Weights are estimated per $(sector, regime)$ cell. With ~11 GICS sectors × 2 regimes ≈ 22 cells and, e.g., ~27 test quarters per market, each cell contains very few effective observations. No shrinkage, no regularisation, and no reporting of cell sizes or of weight stability across folds. This is precisely the setting in which forecast-combination weights are known to be poorly estimated, and the "best single agent" row's catastrophic Russell 2000 result (1.9173) demonstrates how unstable selection can be in this dataset.
4. **Single run, no variance decomposition.** One configuration per model, no seeds, no error bars for the MAPE estimates themselves. The DM tests bound sampling uncertainty *conditional on the fitted model*, but there is no estimate of **search** variance — which for an LLM-driven loop at temperature 0.7 is likely substantial. Reporting 3–5 seeds would be cheap and decisive.
5. **Hyperparameter and budget sensitivity unaddressed.** Number of perspectives (5), iterations, agent selection subset size, and the iters × 10 min/agent compute budget are all fixed without sensitivity analysis. Comparability of compute across MUFASA and the SR baselines is also unreported, which matters because SR performance is strongly compute-dependent.
6. **CSI 300 sample-period anomaly.** The paper states the CSI 300 series begins in **2002**, but the index was launched in April 2005 (base date 31 December 2004). A 2002 start therefore requires index-provider back-fill or reconstructed constituents, which reintroduces the selection/survivorship concern the authors were careful to avoid elsewhere. This should be documented.
7. **"US, UK, China" oversimplification.** The introduction says experiments cover companies from "the US, UK, China." The actual universes are two US indices, a pan-European index (STOXX 600 — which includes UK firms but is not a UK index), a pan-Asia-Pacific ex-Japan index, and CSI 300. The UK is not separately identifiable in the design.
8. **Number and identity of perspectives never explicitly enumerated in the method section.** Section 3 speaks abstractly of "a set of valuation philosophies"; the five (Earnings, Cash Flow, Asset, Growth, Quality) appear only in Figure 2, Tables 4/6–9, and Appendix E. A reader of the method section alone cannot know the design's size.
9. **Constraints in the SLSQP step unstated.** Non-negativity? Summation to one? The subset-selection rule (how many agents, on what criterion) is also unspecified. Since combination weights are a central object of the contribution — and one the paper releases — the constraint set should be stated.

### 8.5 Expositional and formal defects

- **Notational collision in Eq. (4):** $\hat y_{i,t+1} = \tilde w^\top_{C(i,t)}\cdot \hat y_{i,t+1}$ uses the same symbol for the scalar aggregate (LHS) and the stacked vector of agent forecasts (RHS). It should be, e.g., $\hat y_{i,t+1} = \tilde w^\top_{C(i,t)}\,\hat{\mathbf y}_{i,t+1}$.
- **Algorithm 1, line 19** applies `Optimize` to the *prediction* $\hat y$ rather than to the coefficient vector; the intended operation (and the text's description) is optimisation of the expression's scalar parameters.
- **Cross-reference errors:** §*Error Percentiles* cites "Table 7" for the aggregate percentile results, which appear in **Figure 7**. The Experiments section says "three categories" of baselines and then lists five.
- **Symbol-heavy equations in Tables 4 and 6–9** are rendered with quantisation artifacts (superscripts/subscripts fused, e.g., "10088.38", "£ 13829.10"). The *structure* of each expression is legible, but exact constants cannot be reliably transcribed from the PDF; the released artifact should be treated as authoritative.
- **Appendix A's pseudocode does not show the meta-coordinator's subset-selection step**, though the prose mentions it.
- **No test-set size is reported** (number of companies × quarters in each split). Deriving from stated periods, test windows span roughly **16–28 quarters** per market (≈20% of 78–142 quarters), i.e., 4–7 years — small enough that HLN correction was clearly necessary, and small enough that per-sector×regime weight estimation is thinly supported.

---

## 9. Step Nine — What the Paper Establishes, and What It Does Not

To be maximally truth-seeking, I separate these explicitly.

**Established (subject to the reporting caveats above):**
- Within the authors' own evaluation protocol, MUFASA attains the lowest MAPE in all five markets among 17 competitors spanning five method families; the ordering is stable across markets and appears at every error quantile.
- Disentangling the search across perspective-constrained agents improves over a single unified search in 4/5 markets, and the improvement is not merely "pick the best agent" — combination beats post-hoc selection, dramatically so on Russell 2000.
- Combining perspectives with a constraint (SLSQP) solution outperforms equal weighting in 4/5 markets, and a risk-aware statistical memory outperforms binary and MAPE-only memory in 5/5 markets.
- The learned expressions are structurally recognisable as earnings multiples, DCF, book multiples, relative valuation, and residual income models, with data-adaptive correction terms, and these structures recur across geographically distinct markets.
- Under the authors' stated DM specification, the loss differentials are negative everywhere, at conventional significance levels for the 60 comparisons reported.

**Not established:**
- That MUFASA beats a **naive random-walk price forecast**. This is untested and is the most important open question.
- That the improvement is **economically** meaningful (no portfolio or return-based evaluation).
- That the gain survives **search variance** (single run, no seeds).
- That the improvement over the simpler baselines (Random Forest, P/E) is statistically significant — those DM comparisons are absent.
- That the self-evolving loop is **strictly out-of-sample** — the sample discipline is unstated.
- That the 19.65% headline and the Table 5 magnitudes are correct as printed — they are not reconcilable with the published tables.
- That "MUFASA" is an acronym expansion the authors intend (the paper defines "Multi-Agent Fundamental Analysis with Symbolic Adaptive learning"; the capitalization implies MUFASA, but it is not spelled out as an acronym).

---

# CONCLUSION

**Summary of the contribution.** The paper's intellectual core is a **reframing**: financial valuation is not a scientific-discovery problem with a single recoverable law, but a **multi-model, non-stationary, weakly-supervised** inference problem. From this reframing, three architectural requirements follow deductively, and the authors implement exactly three components against them — perspective-disentangled LLM agents with executable expression programs and differential-evolution coefficient fitting; a hierarchical meta-coordinator that learns sector- and regime-conditional combination weights by constrained optimisation; and a seven-dimensional statistical memory that replaces binary credit assignment with a risk profile per hypothesis. Empirically, MUFASA attains the best MAPE in all five markets (0.4465 / 0.5718 / 0.5064 / 0.5814 / 0.4343; average 0.5081, against 0.6351 for the strongest baseline on average), with statistically significant Diebold–Mariano loss differentials, and it produces expressions that map recognisably onto the earnings-multiple, DCF, book-multiple, relative-valuation, and residual-income traditions — a correspondence no baseline achieves.

**The most durable contributions, in my judgement, are three.** First, the **empirical falsification of method transfer**: LLM-encoded scientific priors, which are decisive in physics-style SR, do not dominate plain evolutionary search in finance (PySR's 0.6351 clearly beats LLM-SR's 0.7271 and FunSearch's 0.7991). Second, the **statistical-memory design** and its demonstration that the binding constraints in financial symbolic discovery are not average accuracy but *conditional instability* — denominator blow-ups in asset-light firms, log-transformations producing invalid outputs, growth terms amplifying tail risk — failure modes invisible to scalar loss and precisely the ones a distributional memory surfaces. Third, the **forecast-combination evidence**: "best single agent" reaches 1.9173 on Russell 2000 while principled combination reaches 0.5718, which is a clean, quantitative argument that under regime non-stationarity one should *combine perspectives rather than select them*.

**The binding caveats, ranked.** (1) The target is an integrated, right-skewed **price level** measured by MAPE, with **no naive persistence benchmark, no log-price specification, and no out-of-sample $R^2$** — so the economic significance of the headline accuracy is unknown. (2) The **sample discipline of the self-evolving loop is unstated**, and ex-post regime labelling is a plausible leakage channel into the very component (hierarchical coordination) whose marginal contribution is smallest. (3) The **Diebold–Mariano magnitudes and the 19.65% headline do not reconcile** with Tables 2 and 5 as printed, and five of the most relevant competitors are excluded from the significance battery. (4) Single-run results with no seed variance, and no sensitivity to loss function, winsorisation, or compute budget. None of these undermines the architecture; all of them bound what the current evidence licenses.

**Verdict.** A conceptually well-motivated and competently executed systems paper that identifies a real and under-appreciated mismatch between scientific symbolic regression and financial valuation, and supplies a modular architecture that addresses it with economically interpretable output. Its ablations are the strongest part of the evidence base; its forecasting evaluation is the weakest, chiefly for want of a trivial baseline and a stationary target. The recommended next step is not a new architecture but a **harder evaluation**: random-walk and log-return benchmarks, $R^2_{OOS}$, decile-spread returns net of costs, point-in-time regime labels, multiple seeds, and a recalculation of the significance battery over the full baseline set. Should those hold, the paper's central claim — that **disentangled, statistically self-aware, hierarchically coordinated symbolic discovery is the correct formalism for interpretable fundamental analysis** — would be well supported. As it stands, the claim is plausible, carefully engineered, and *not yet fully proven*.

---

# APPENDIX A — Numerical Verification Log

All computations performed directly on the values transcribed from the paper's tables.

### A.1 Table 2 aggregates — **all reproduce exactly**

For each of the 17 baseline rows, the "All Data Avg" equals the unweighted arithmetic mean of the five market MAPEs to four decimals (max deviation 0.0000), and every Δ entry equals (row average − 0.5081) to four decimals. Examples: Random Forest mean of (0.4812, 0.6551, 0.7490, 0.8436, 0.5605) = 0.6579 ✓; Fino1 mean = 1.3681 ✓; PySR mean = 0.6351 ✓; Δ for PySR = 0.6351 − 0.5081 = 0.1270 ✓. The mean of all 17 Δ entries = 0.3702, exactly the parenthetical "(Avg)" figure attached to MUFASA's own row.

### A.2 Relative margins (my computation, not the authors')

| Comparison | Definition | Result |
|---|---|---|
| vs. best baseline per market | mean of $(\text{best}_m - \text{MUFASA}_m)/\text{best}_m$ | **10.12%** |
| vs. PySR per market | mean of $(\text{PySR}_m - \text{MUFASA}_m)/\text{PySR}_m$ | **19.47%** |
| vs. PySR all-data averages | $(0.6351-0.5081)/0.6351$ | **20.00%** |
| vs. all-baseline mean | $0.3702/(0.5081+0.3702)$ | **42.15%** |
| vs. better of {FinCon, FinVision} per market | mean relative reduction | **27.67%** ✅ *matches paper exactly* |

**Paper's claim: "average improvement of 19.65%."** Closest reproductions are 19.47% (per-market vs. PySR) and 20.00% (aggregate vs. PySR). **19.65% is not reproducible under any definition I tested**; it should be restated with an explicit definition.

### A.3 Ablation monotonicity (Table 3) — verified

- S.P agent worse than M.P equal-weight in **4/5** markets (exception FTSE APAC: 0.6095 < 0.6442). Paper says "four of the five" ✓.
- M.P equal-weight worse than meta-coordinator-without-memory in **4/5** (exception S&P 500: 0.4652 < 0.4702). Paper says "four of the five" ✓.
- No-memory variant worse than full MUFASA in **5/5** ✓.
- Best-single-agent is second-best in exactly **three** markets (STOXX 600 0.5256, FTSE APAC 0.5833, CSI 300 0.4739) and worst overall on Russell 2000 (1.9173). Paper says "second-best on three markets but degrades substantially on Russell 2000" ✓.
- MUFASA is the column minimum in all five markets ✓.

### A.4 Table 5 vs Table 2 — **irreconcilable magnitudes**

Under APE loss, the DM mean loss differential should equal the difference of MAPEs on the same sample. Selected cells:

| Baseline | Market | Implied ($\text{MUFASA}-\text{baseline}$) | Reported | Ratio |
|---|---|---|---|---|
| LLM-SR | S&P 500 | −0.0296 | −0.1101 | 3.72× |
| P/E | Russell 2000 | −0.2732 | −0.0371 | 0.14× |
| Fino1 | Russell 2000 | −1.5526 | −0.4515 | 0.29× |
| PySR | CSI 300 | −0.0872 | −0.0956 | 1.10× |
| Fin-R1 | FTSE APAC | −0.3048 | −0.5919 | 1.94× |

Signs agree in all 25 cells checked; magnitudes diverge by a factor ranging from 0.14× to 3.72×. The two tables therefore report different quantities under a shared name.

### A.5 Memory ablation (Table 10) — verified

Meta-coordinator rows: Binary mean = **0.5601**; MAPE-only mean = **0.5666**; Full statistical mean = **0.5081**. Full statistical memory is the minimum in each of the five markets. Within market, binary beats MAPE-only on S&P 500 (0.4646 vs 0.4702) and Russell 2000 (0.6445 vs 0.7525), while MAPE-only wins on the remaining three — so the paper's use of "typically" is warranted, and the aggregate advantage of the full statistical profile is ≈9.3% in relative terms.

### A.6 Table 3 vs Table 10 cross-consistency

Russell 2000 only: S.P 0.8994 vs 0.8987; M.P-EW 0.8768 vs 0.8831; best-single 1.9173 vs 1.9170. All other cells identical. Max discrepancy 0.0063; no ranking implications.

### A.7 Unverifiable items

Figure 3 (trajectories), Figure 4 (weight heatmaps), Figures 5/6/8 (scatter, sector boxes, quartile bias) are presented graphically; only Figure 7's percentile values are tabulated. Appendix D's weight patterns and Appendix E's learnings can be checked for *internal coherence* but not against released data from the PDF alone; the paper's claimed public release of these artifacts is the appropriate verification channel.

---

# APPENDIX B — Transcription Cautions

1. The PDF extraction fuses superscripts and subscripts in the expressions of Tables 4 and 6–9 (e.g., "10088.38", "−7.24 × 10−41.34", "£ 13829.10"). Statements in §7.5 reproduce the **structural form** and the constants that are unambiguous; exact constants for the Asset and Growth agents should be taken from the released artifact rather than the typeset PDF.
2. The paper uses both "FTSE APAC" (tables) and "FTSE Asia Pacific ex-Japan" (prose) for the same series; they are treated as identical here.
3. The abstract renders the method name as "mufasa" in lowercase small caps; the body uses both "MUFASA" and "mufasa". I use MUFASA throughout.
4. The paper's own numbering cites "Table 7" for the aggregate percentile results, which are printed in **Figure 7**. I have used the figure's values.
