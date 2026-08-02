# GrantScopeAI
GrantScopeAI is a Streamlit research-intelligence tool that combines CORDIS, NSF, and OpenAlex data to explore funding trends, assess research momentum, and recommend similar funded projects using TF-IDF text similarity.

## Project Problem

Researchers and research-support teams often search grant databases, funder websites, and publication indexes separately. This makes it difficult to see how a topic is funded across regions, which institutions are active, whether research activity is growing, and which funded projects are most comparable to a new concept. GrantScopeAI consolidates those signals into one exploratory interface.

## Intended User

GrantScopeAI is designed for a researcher or university research-support professional assessing how to position an early grant concept.

## Primary User Story

As a researcher developing an AI-enabled chemistry or materials proposal, I want to compare my concept with recent funded projects and publication trends so that I can identify relevant funders, refine my positioning, and document the evidence behind my choices.

## Core Decision Supported

Where does a proposed AI-enabled chemistry or materials topic fit within recent funding and publication activity?
# Raw Data

Raw source datasets are stored locally and are not committed to GitHub
because of their size.

Expected sources:

- NSF Award Search API
- OpenAlex API
- CORDIS Horizon Europe and Horizon 2020 data

The acquisition process is documented in the source-validation notebook.

## Data preparation

GrantScopeAI currently combines funding data from:

- **CORDIS** — European Union Horizon Europe projects;
- **NSF Awards** — United States research awards;
- **OpenAlex** — publication activity and research momentum.

The main analysis period is **2021–2025**.

### Processing approach

Each funding source is standardized to one row per unique grant or project.

- CORDIS participant and consortium records are aggregated to the project level.
- Repeated NSF extraction records are consolidated using the NSF award ID.
- Original source identifiers and URLs are retained for traceability.
- Funding amounts, dates, organisations, programmes, and descriptive text are standardized.

### Relevance tiers

Funding records are classified using AI and chemistry/materials keyword rules:

- `core_match` — higher-confidence records passing the refined relevance filter;
- `broad_match` — potentially relevant records passing the high-recall filter;
- `out_of_scope` — records retained in full local datasets but excluded from the candidate datasets.

Extraction-query labels are not used for classification, preventing circular relevance decisions.

### Current funding candidate datasets

| Source | Core matches | Broad matches | Total candidates |
|---|---:|---:|---:|
| CORDIS | 416 | 259 | 675 |
| NSF | 1,757 | 907 | 2,664 |
| **Combined** | **2,173** | **1,166** | **3,339** |

### Data storage

Large raw and enriched datasets are stored locally and excluded from GitHub using `.gitignore`.

The repository contains compact processed datasets intended for:

- Python analysis;
- Tableau dashboards;
- the Streamlit application;
- cross-source integration.

Detailed cleaning decisions and validation steps are documented in:

- `Notebooks/02_cordis_cleaning.ipynb`
- `Notebooks/03_nsf_cleaning.ipynb`
- the project decision log
