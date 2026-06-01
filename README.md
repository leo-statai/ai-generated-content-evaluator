# Automated Quality Assessment of AI-Generated Educational Content

A proof-of-concept pipeline that uses generative AI to **produce** a long-form technical report and then uses another generative AI to **evaluate** it — turning subjective document review into a reproducible, multi-metric, LLM-driven workflow.

> Generation: **Google NotebookLM** &nbsp;•&nbsp; Evaluation: **Google Gemini API** &nbsp;•&nbsp; Orchestration: **Python**

---

## Why this project

LLMs can draft a polished technical document in seconds — but how do you know if it is actually *correct*, *deep*, and *well-structured*? Manual review does not scale. This project demonstrates a practical answer: a second LLM, equipped with carefully engineered evaluator personas, scores the generated content against the source-of-truth transcript and reports both quantitative metrics and qualitative justifications.

The use case is educational content (a technical report on the architecture and philosophy of modern generative AI), but the same pattern applies to any AI-assisted content workflow — documentation, summaries, research briefs, training material.

## Pipeline overview

```
┌──────────────────────┐     ┌──────────────────┐     ┌─────────────────────────┐
│  Seminar transcript  │ ──▶ │   NotebookLM     │ ──▶ │  Technical report (MD)  │
└──────────────────────┘     │  (generation)    │     └────────────┬────────────┘
                             └──────────────────┘                  │
                                                                   ▼
                             ┌──────────────────┐     ┌─────────────────────────┐
                             │   Gemini API     │ ◀── │  evaluate_report.py     │
                             │  (evaluation)    │     │  (4 evaluator personas) │
                             └────────┬─────────┘     └─────────────────────────┘
                                      │
                                      ▼
                          ┌──────────────────────────┐
                          │  evaluation_results.md   │
                          │  scores + justifications │
                          └──────────────────────────┘
```

### Phase 1 — Content generation (NotebookLM)

The full transcript of an academic seminar ("Talking to Machines: A Practical Introduction to Generative AI") is loaded as a source into NotebookLM and synthesized into a structured technical report using a single engineered prompt (see [`data/notebooklm_generation_prompt.txt`](data/notebooklm_generation_prompt.txt)). The output is [`data/technical_report_notebooklm.md`](data/technical_report_notebooklm.md).

### Phase 2 — Automated evaluation (Gemini API)

[`evaluate_report.py`](evaluate_report.py) sends the generated report to the Gemini API once per metric. Each call uses a different **evaluator persona** and returns a strict JSON response with a 1–10 score and a written justification:

| Metric                  | Evaluator persona       | Uses transcript? |
| ----------------------- | ----------------------- | :--------------: |
| Clarity and Coherence   | Academic Reviewer       |        —         |
| Factual Accuracy        | Fact-Checker            |        Yes       |
| Depth of Analysis       | University Professor    |        —         |
| Structural Adherence    | Academic Journal Editor |        —         |

Only the *Factual Accuracy* check is grounded against the source transcript; the others assess intrinsic qualities of the document.

## Example results

The full evaluation of the included report is in [`data/evaluation_results.md`](data/evaluation_results.md). Summary:

| Metric                | Score |
| --------------------- | :---: |
| Clarity and Coherence | 10/10 |
| Factual Accuracy      |  5/10 |
| Depth of Analysis     |  8/10 |
| Structural Adherence  |  6/10 |
| **Overall average**   | **7.25/10** |

A representative finding: the *Factual Accuracy* evaluator caught that the generated report misidentified the seminar speaker's name and gender — an error a human skimming the document could plausibly miss. This is the kind of regression an automated, transcript-grounded check is designed to surface.

## Repository layout

```
.
├── evaluate_report.py        # Main evaluation script
├── requirements.txt
├── .env.example              # Template for the API key
├── data/
│   ├── source_transcript.txt              # Ground-truth seminar transcript
│   ├── notebooklm_generation_prompt.txt   # Prompt used to generate the report
│   ├── technical_report_notebooklm.md     # AI-generated report (input to evaluator)
│   ├── evaluation_results.md              # Sample output from a real run
│   └── script_design_plan.md              # Original design doc for the script
└── paper/
    ├── automated_quality_assessment_report.pdf   # Full technical report (PDF)
    ├── Main.tex                                  # LaTeX source
    └── Sections/                                 # LaTeX sections + bibliography
```

## Getting started

### Prerequisites

- Python 3.10+
- A [Google AI Studio](https://aistudio.google.com/) API key (free tier works)

### Install

```bash
git clone https://github.com/<your-username>/ai-generated-content-evaluator.git
cd ai-generated-content-evaluator
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### Configure

```bash
cp .env.example .env
# edit .env and paste your key into GOOGLE_API_KEY
```

### Run the evaluation

```bash
.venv/bin/python evaluate_report.py \
    data/technical_report_notebooklm.md \
    data/source_transcript.txt
```

The script prints a summary to the console and writes a detailed Markdown report to `evaluation_results.md` in the current directory.

> Note: there is a 60-second sleep between API calls to stay within Gemini's free-tier rate limits. A full run takes roughly 4 minutes.

### Use your own content

The script is content-agnostic. To evaluate a different document:

1. Drop your Markdown report and its source-of-truth transcript anywhere on disk.
2. Pass their paths as the two positional arguments.

The four evaluation prompts live inline at the top of `main()` in [`evaluate_report.py`](evaluate_report.py) and can be edited to fit a different domain (e.g., legal briefs, medical summaries, code documentation).

## Technical write-up

The full academic report — methodology, prompts, results, and analysis — is available as a PDF: [`paper/automated_quality_assessment_report.pdf`](paper/automated_quality_assessment_report.pdf). The LaTeX source is included for reproducibility; rebuild with:

```bash
cd paper
pdflatex Main.tex && bibtex Main && pdflatex Main.tex && pdflatex Main.tex
```

## Tech stack

- **Python 3** — orchestration and I/O
- **`google-generativeai`** — Gemini API client
- **`python-dotenv`** — environment-variable management
- **Google NotebookLM** — content generation (no SDK; used interactively)
- **Gemini `gemini-pro-latest`** — automated evaluator
- **LaTeX (IEEEtran)** — final report typesetting

## Context

Developed as the final project for the graduate course **IA382 — Seminars in Computer Engineering** at the School of Electrical and Computer Engineering (FEEC), **UNICAMP**, 2025/S2. Inspired by the seminar *"Talking to Machines: A Practical Introduction to Generative AI"* by Gabriel Sude.

## License

[MIT](LICENSE) © Leonardo Rangel Alves
