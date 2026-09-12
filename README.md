# 🔎 ARGUS

### Adaptive Research & Grounded Understanding System

**ARGUS is a web-based evidence investigation system that turns open-web research into a traceable, evidence-backed investigation.**

Instead of simply generating an answer, ARGUS searches the live web, collects source material, extracts factual claims, compares claims across independent sources, detects potentially contradictory evidence, and assigns a deterministic verification status and confidence level.

> **Search the web. Extract the evidence. Compare the claims. Verify the conclusion.**

---

## 🎯 Why ARGUS?

Web research often produces a collection of links without making it easy to understand:

* Which sources actually contain useful evidence?
* Which claims are supported by multiple sources?
* Do different sources disagree?
* How strong is the available evidence?
* Where did a particular conclusion come from?

ARGUS addresses this by building an **evidence trail** from the original question all the way to the sources supporting or contradicting each claim.

---

## 🚀 What ARGUS Does

Given a research question, ARGUS performs the following workflow:

```text
User Question
      ↓
Anakin Search
      ↓
Source Selection
      ↓
Anakin Scraper
      ↓
Claim Extraction
      ↓
Contradiction Detection
      ↓
Cross-Source Claim Matching
      ↓
Evidence Verification
      ↓
Verification Tasks
      ↓
Streamlit Dashboard + Evidence Graph
```

The result is not just an answer — it is an **inspectable evidence structure**.

---

## ✨ Key Features

### 🌐 Live Web Research

ARGUS uses **Anakin Search** to discover current web sources relevant to the investigation question.

This allows investigations to work with live web information instead of relying on a static knowledge base.

---

### 🎯 Source Selection

ARGUS selects sources for investigation while limiting excessive dependence on a single domain.

This helps create a more diverse evidence set and makes cross-source comparison meaningful.

The investigation loop currently limits:

* Total scraped sources
* Search results processed
* Sources per domain

---

### 📄 Web Scraping

Selected sources are retrieved using **Anakin Scraper**.

ARGUS stores the source metadata and scraped content so that extracted claims can always be traced back to their originating source.

---

### 🧩 Claim Extraction

ARGUS identifies candidate factual statements from scraped source content.

Each extracted claim maintains a relationship with its source, allowing the dashboard to display:

```text
Claim
  ↓
Evidence excerpt
  ↓
Original source
```

This makes individual claims inspectable instead of treating an entire webpage as a single piece of evidence.

---

### 🔗 Cross-Source Claim Matching

ARGUS identifies similar claims appearing across independent sources.

The deterministic matcher combines:

* Word normalization
* Stop-word filtering
* Topic grouping
* Word-based similarity
* Topic-based similarity
* Source independence checks
* Evidence consolidation

For example:

```text
Source A:
"AI-enabled attacks affected 89% of companies."

Source B:
"Nearly nine in ten companies experienced AI-related attacks."

             ↓

       Matched evidence
```

Claims from the same source are not incorrectly treated as independent confirmation.

---

### ⚠️ Contradiction Detection

ARGUS searches for potentially conflicting claims across sources.

The detector considers:

* Topic similarity
* Opposing language patterns
* Source independence

Examples of opposing patterns include:

```text
increasing ↔ decreasing
increase   ↔ decrease
higher     ↔ lower
more       ↔ less
effective  ↔ ineffective
confirmed  ↔ disputed
```

Contradicting evidence is preserved rather than silently discarded.

---

### 🔬 Evidence Verification

ARGUS assigns a verification status and confidence level based on the available evidence.

Current deterministic heuristic:

| Evidence                            | Status              | Confidence |
| ----------------------------------- | ------------------- | ---------: |
| No supporting sources               | Unverified          |         0% |
| 1 supporting source                 | Supported           |        60% |
| 2 supporting sources                | Supported           |        75% |
| 3+ supporting sources               | Supported           |        90% |
| Contradicting evidence dominates    | Contradicted        |     15–30% |
| Supporting + contradicting evidence | Partially supported |     35–65% |

**Important:** These values are evidence-strength heuristics, not statistical probabilities.

---

### 🔍 Verification Tasks

When a claim contains contested or insufficient evidence, ARGUS can create a follow-up verification task requesting additional independent evidence.

This allows the investigation to identify areas where the current evidence is not strong enough.

---

### 🕸️ Evidence Graph

ARGUS generates an evidence graph showing how the investigation connects to claims and sources.

```text
                 Investigation
                       │
                       ▼
                    Claims
                  /        \
             supports    contradicts
               /              \
              ▼                ▼
           Sources           Sources
```

The graph makes the evidence chain visually inspectable:

```text
Question
   ↓
Claim
   ↓
Supporting / Contradicting Source
```

---

### 📊 Streamlit Dashboard

The interactive dashboard provides visibility into the complete investigation:

* Sources discovered
* Sources scraped
* Extracted claims
* Evidence excerpts
* Verification status
* Confidence scores
* Contradictions
* Verification tasks
* Evidence relationships
* Evidence graph

---

# 🏗️ Architecture

```text
                         USER QUESTION
                               │
                               ▼
                    ┌───────────────────┐
                    │   Anakin Search   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Source Selection  │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │  Anakin Scraper   │
                    └─────────┬─────────┘
                              │
                              ▼
                    ┌───────────────────┐
                    │ Claim Extraction  │
                    └─────────┬─────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │    Contradiction Detection    │
              └───────────────┬───────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ Cross-Source Claim Matching   │
              └───────────────┬───────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │     Evidence Verification     │
              └───────────────┬───────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │      Verification Tasks       │
              └───────────────┬───────────────┘
                              │
                              ▼
              ┌───────────────────────────────┐
              │ Streamlit Dashboard + Graph   │
              └───────────────────────────────┘
```

---

# 🧠 Design Philosophy

ARGUS is designed around **evidence traceability** rather than answer generation.

A conventional research workflow often looks like:

```text
Question → Search → Read → Answer
```

ARGUS instead builds:

```text
Question
   ↓
Sources
   ↓
Evidence
   ↓
Claims
   ↓
Cross-source comparison
   ↓
Verification
   ↓
Traceable result
```

Every major conclusion is connected to the evidence that produced it.

This makes the investigation easier to inspect, audit, and extend.

---

# ⚙️ Technical Approach

ARGUS currently uses a **deterministic evidence-processing pipeline**.

The core workflow does not require an LLM.

This provides:

* Reproducible processing
* Predictable matching behavior
* Explainable verification rules
* No dependency on LLM-generated reasoning for the core pipeline
* Easier testing of individual investigation components

The main reasoning components are implemented through deterministic algorithms and heuristics.

---

# 📁 Project Structure

```text
argus/
│
├── agents/
│   ├── claim_extractor.py
│   ├── claim_matcher.py
│   ├── contradiction_detector.py
│   ├── evidence_graph.py
│   ├── investigator.py
│   ├── investigator_loop.py
│   ├── planner.py
│   ├── reasoning.py
│   ├── state.py
│   ├── synthesizer.py
│   ├── verification_planner.py
│   └── verifier.py
│
├── models/
│   ├── claims.py
│   ├── investigation.py
│   └── sources.py
│
├── tools/
│   ├── anakin_search.py
│   └── anakin_scraper.py
│
├── ui/
│   ├── components.py
│   ├── dashboard.py
│   └── evidence_graph.py
│
├── run_search_test.py
├── run_claim_matching_test.py
├── run_contradiction_test.py
├── run_evidence_graph_test.py
├── run_full_pipeline_test.py
├── run_planner_test.py
├── run_verifier_test.py
│
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 🛠️ Requirements

* Python 3.10+
* Anakin API access
* Anakin Search
* Anakin Scraper
* Streamlit

---

# 🚀 Getting Started

## 1. Clone the repository

```bash
git clone https://github.com/shashank2602s/argus.git
cd argus
```

## 2. Create a virtual environment

```bash
python -m venv .venv
```

## 3. Activate the environment

### Windows PowerShell

```powershell
.venv\Scripts\Activate.ps1
```

## 4. Install dependencies

```powershell
pip install -r requirements.txt
```

---

# 🔐 Configuration

Create a `.env` file in the project root using `.env.example` as a template.

```env
ANAKIN_API_KEY=your_api_key_here
```

Keep API credentials local.

**Never commit `.env` or API keys to the repository.**

The repository ignores sensitive/local files including:

```text
.env
.venv/
__pycache__/
*.pyc
.vscode/
```

---

# ▶️ Running ARGUS

From the project root:

```powershell
$env:PYTHONPATH = (Get-Location).Path
streamlit run ui\dashboard.py
```

The Streamlit dashboard will open in your browser.

Example investigation:

```text
What are the major cybersecurity trends in 2026?
```

ARGUS will then execute the investigation pipeline and display the resulting evidence.

---

# 🧪 Testing

ARGUS includes deterministic tests for its core components.

### Claim Matching

```powershell
python run_claim_matching_test.py
```

Tests:

* Similar claims
* Unrelated claims
* Same-source claims
* Multiple independent supporting sources

**Result: 4/4 PASS**

---

### Contradiction Detection

```powershell
python run_contradiction_test.py
```

Tests:

* Contradicting claims
* Supporting claims
* Unrelated claims

**Result: 3/3 PASS**

---

### Verification

```powershell
python run_verifier_test.py
```

Tests:

* One supporting source
* Two supporting sources
* Three supporting sources
* No supporting evidence
* Contradicting evidence

**Result: 5/5 PASS**

---

### Evidence Graph

```powershell
python run_evidence_graph_test.py
```

Validates:

* Investigation nodes
* Claim nodes
* Source nodes
* Supporting relationships
* Contradicting relationships

---

### Planner

```powershell
python run_planner_test.py
```

Tests the research planning component.

---

### Full Pipeline

```powershell
python run_full_pipeline_test.py
```

The full pipeline test performs a live investigation using the configured Anakin services.

**Note:** This test consumes Anakin API usage.

---

# ✅ Validation

The deterministic component test suite currently passes:

```text
Claim Matching          4/4 PASS
Contradiction Detection 3/3 PASS
Verification            5/5 PASS
Evidence Graph          PASS
```

The complete live pipeline has also been successfully executed across:

```text
Search
  ↓
Source Selection
  ↓
Scraping
  ↓
Claim Extraction
  ↓
Contradiction Detection
  ↓
Cross-Source Matching
  ↓
Evidence Verification
```

---

# ⚠️ Current Limitations

ARGUS is an evolving research system.

Current limitations include:

### Deterministic claim extraction

Claim extraction currently relies on deterministic patterns and heuristics. It may occasionally extract irrelevant factual statements from otherwise useful pages.

### Deterministic semantic matching

Claim similarity is based on lexical and topic-level similarity rather than a deep semantic model.

### Rule-based contradiction detection

The contradiction detector relies on predefined opposing-language patterns and therefore cannot identify every possible form of disagreement.

### Heuristic confidence

Confidence values represent evidence-strength levels and are **not calibrated statistical probabilities**.

### Web accessibility

Some pages may fail to scrape because of:

* Dynamic rendering
* Access restrictions
* Anti-bot systems
* Page structure
* Temporary network failures

These limitations are intentionally documented rather than hidden because ARGUS is designed around transparent evidence processing.

---

# 🔮 Future Improvements

Potential future development includes:

* LLM-assisted claim extraction
* Stronger semantic claim matching
* Advanced contradiction reasoning
* Source-quality and reliability scoring
* Temporal claim tracking
* Richer evidence graph visualization
* Automatic research-plan refinement
* Additional verification agents
* Calibrated confidence scoring
* Better handling of noisy web content

---

# 🔒 Security

ARGUS keeps API credentials outside the source code.

API keys should be stored locally in `.env` and excluded from Git.

Never:

```text
❌ hard-code API keys
❌ commit .env
❌ publish credentials
```

Use:

```text
.env.example
```

as the safe configuration template.

---

# 🏆 Hackathon Context

ARGUS was developed for the **Anakin Forge Hackathon**.

The project uses Anakin's live web capabilities as the data acquisition layer and builds an evidence reasoning and verification workflow on top of it.

The core idea is:

> **Anakin provides the live web intelligence layer. ARGUS turns that information into structured, traceable evidence.**

---

# 📌 Repository

**GitHub:**
https://github.com/shashank2602s/argus

---

# 📄 License

This project is provided for hackathon and educational purposes.
