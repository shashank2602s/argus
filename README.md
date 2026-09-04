# ARGUS

## Adaptive Research & Grounded Understanding System

ARGUS is a web-based evidence investigation system that helps users research questions using live web sources, extract factual claims, compare evidence across sources, detect contradictions, and assign evidence-based verification confidence.

ARGUS is currently implemented as a deterministic evidence-processing pipeline and does not require an LLM for its core investigation workflow.

---

## What ARGUS Does

Given a research question, ARGUS:

1. Searches the live web using Anakin Search.
2. Selects relevant sources while limiting excessive dependence on a single domain.
3. Scrapes selected source pages using Anakin Scraper.
4. Extracts candidate factual claims from the collected content.
5. Detects potentially contradictory claims across independent sources.
6. Matches similar claims across different sources.
7. Consolidates evidence from matching sources.
8. Assigns verification status and confidence based on supporting and contradicting evidence.
9. Creates follow-up verification tasks for contested claims.
10. Visualizes the investigation through a Streamlit dashboard and evidence graph.

---

## Architecture

```text
User Question
      |
      v
+-----------------+
|  Anakin Search  |
+--------+--------+
         |
         v
+-----------------+
| Source Selection|
+--------+--------+
         |
         v
+-----------------+
| Anakin Scraper  |
+--------+--------+
         |
         v
+-----------------+
| Claim Extraction|
+--------+--------+
         |
         v
+----------------------+
| Contradiction        |
| Detection            |
+----------+-----------+
           |
           v
+----------------------+
| Cross-Source Claim   |
| Matching             |
+----------+-----------+
           |
           v
+----------------------+
| Evidence Verification|
+----------+-----------+
           |
           v
+----------------------+
| Verification Tasks   |
+----------+-----------+
           |
           v
+----------------------+
| Streamlit Dashboard  |
| + Evidence Graph     |
+----------------------+
```

---

## Key Features

### Live Web Research

ARGUS uses Anakin Search to discover current web sources relevant to the user's question.

### Source Selection

The investigation loop ranks discovered sources and limits the number of sources scraped from the same domain.

### Claim Extraction

ARGUS extracts candidate factual statements from scraped source content and associates them with their originating sources.

### Cross-Source Claim Matching

Similar claims from different sources are matched using deterministic text and topic similarity.

The matcher uses:

* word normalization
* stop-word filtering
* topic grouping
* word-based similarity
* topic-based similarity
* independent-source checking
* evidence consolidation

### Contradiction Detection

ARGUS identifies potentially opposing claims by comparing:

* whether claims discuss the same topic
* predefined opposing language patterns
* source independence

Examples include:

```text
increasing <-> decreasing
higher <-> lower
more <-> less
increase <-> decrease
effective <-> ineffective
confirmed <-> disputed
```

### Evidence Verification

Claims are assigned a verification status and confidence based on their supporting and contradicting evidence.

Current confidence model:

| Evidence                            | Status              | Confidence |
| ----------------------------------- | ------------------- | ---------: |
| 0 supporting sources                | Unverified          |         0% |
| 1 supporting source                 | Supported           |        60% |
| 2 supporting sources                | Supported           |        75% |
| 3+ supporting sources               | Supported           |        90% |
| Contradicting evidence dominates    | Contradicted        |     15–30% |
| Supporting + contradicting evidence | Partially supported |     35–65% |

These values are deterministic heuristics intended to communicate evidence strength. They are not statistical probabilities.

### Verification Tasks

When ARGUS detects a contested claim, it creates a follow-up task requesting additional independent evidence.

### Evidence Graph

ARGUS generates an evidence graph connecting investigations, claims, and sources.

```text
Investigation
      |
      v
    Claims
    /    \
support  contradict
  /          \
Sources     Sources
```

This allows users to inspect which sources support or contradict each claim.

### Streamlit Dashboard

The dashboard provides an interactive interface for inspecting:

* discovered sources
* scraped evidence
* extracted claims
* verification status
* confidence
* contradictions
* verification tasks
* evidence relationships

---

## Project Structure

```text
argus/
|
+-- agents/
|   +-- claim_extractor.py
|   +-- claim_matcher.py
|   +-- contradiction_detector.py
|   +-- evidence_graph.py
|   +-- investigator.py
|   +-- investigator_loop.py
|   +-- planner.py
|   +-- reasoning.py
|   +-- state.py
|   +-- synthesizer.py
|   +-- verification_planner.py
|   +-- verifier.py
|
+-- models/
|   +-- claims.py
|   +-- investigation.py
|   +-- sources.py
|
+-- tools/
|   +-- anakin_search.py
|   +-- anakin_scraper.py
|
+-- ui/
|   +-- components.py
|   +-- dashboard.py
|   +-- evidence_graph.py
|
+-- run_search_test.py
+-- run_claim_matching_test.py
+-- run_contradiction_test.py
+-- run_evidence_graph_test.py
+-- run_full_pipeline_test.py
+-- run_planner_test.py
+-- run_verifier_test.py
|
+-- .env.example
+-- .gitignore
+-- requirements.txt
+-- README.md
```

---

## Requirements

* Python 3.10+
* Anakin API access
* Anakin Search
* Anakin Scraper
* Streamlit

---

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/shashank2602s/argus.git
cd argus
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## Configuration

Create a `.env` file in the project root based on `.env.example`.

Add your Anakin API key:

```env
ANAKIN_API_KEY=your_api_key_here
```

Never commit the `.env` file.

The repository's `.gitignore` excludes:

```text
.env
.venv/
__pycache__/
*.pyc
.vscode/
```

---

## Running ARGUS

From the project root:

```powershell
$env:PYTHONPATH = (Get-Location).Path
streamlit run ui\dashboard.py
```

The Streamlit dashboard will open in your browser.

Enter a research question and start an investigation.

Example:

```text
What are the major cybersecurity trends in 2026?
```

---

## Testing

ARGUS includes deterministic tests for its core investigation components.

### Claim Matching

```powershell
python run_claim_matching_test.py
```

Tests:

* similar claims
* unrelated claims
* same-source claims
* three independent matching sources

### Contradiction Detection

```powershell
python run_contradiction_test.py
```

Tests:

* opposing claims
* supporting claims
* unrelated claims

### Verification

```powershell
python run_verifier_test.py
```

Tests:

* one supporting source
* two supporting sources
* three supporting sources
* no evidence
* contradicting evidence

### Evidence Graph

```powershell
python run_evidence_graph_test.py
```

### Planner

```powershell
python run_planner_test.py
```

### Full Pipeline

```powershell
python run_full_pipeline_test.py
```

The full pipeline test performs a live investigation using the configured Anakin services and therefore consumes API usage.

---

## Test Results

The deterministic component tests currently pass:

### Claim Matching

```text
4/4 tests PASS
```

### Contradiction Detection

```text
3/3 tests PASS
```

### Verification

```text
5/5 tests PASS
```

The full live pipeline has also been successfully executed, completing the flow from search through scraping, claim extraction, contradiction detection, claim matching, and verification.

---

## Design Philosophy

ARGUS focuses on evidence traceability rather than simply generating an answer.

Instead of treating a generated response as the final result, ARGUS maintains relationships between:

```text
Question
   |
   v
Sources
   |
   v
Evidence
   |
   v
Claims
   |
   v
Verification
```

This makes the investigation easier to inspect and audit.

---

## Current Limitations

ARGUS currently uses deterministic heuristics for:

* claim extraction
* claim similarity
* topic matching
* contradiction detection
* confidence scoring

The system does not currently use an LLM as part of its core verification pipeline.

The contradiction detector relies on predefined opposing-language patterns and therefore cannot identify every possible form of contradiction.

The confidence values represent heuristic evidence-strength levels rather than calibrated probabilities.

Some web pages may fail to scrape depending on their structure, accessibility, or anti-bot protections.

---

## Security

API credentials are stored locally in `.env` and are excluded from Git using `.gitignore`.

Do not place API keys directly in source code or commit them to the repository.

---

## Hackathon Context

ARGUS was developed for the Anakin Forge Hackathon.

The project uses Anakin's web capabilities to build an investigation workflow around live web information, evidence collection, claim analysis, and verification.

---

## Future Improvements

Potential future improvements include:

* LLM-assisted claim extraction
* stronger semantic claim matching
* more advanced contradiction reasoning
* source-quality scoring
* temporal claim tracking
* richer evidence graph visualization
* automatic research-plan refinement
* additional verification agents
* calibrated confidence scoring

---

## License

This project is provided for hackathon and educational purposes.
