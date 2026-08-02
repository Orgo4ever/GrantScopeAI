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

GrantScopeAI combines three complementary data sources:

- **CORDIS** — European Union Horizon Europe research projects;
- **NSF Awards** — United States research awards;
- **OpenAlex** — publication activity and research-momentum context.

The shared analysis period is **2021–2025**.

### Funding-data preparation

The NSF and CORDIS datasets are standardized to one row per unique grant or project.

- CORDIS participant and consortium records are aggregated to the project level.
- Repeated NSF extraction records are consolidated using the NSF award ID.
- Original source identifiers and URLs are retained for traceability.
- Dates, funding amounts, organisations, programmes, and descriptive text are standardized.

### Funding relevance tiers

NSF and CORDIS records are classified using AI and chemistry/materials keyword rules:

- `core_match` — higher-confidence records passing the refined relevance filter;
- `broad_match` — potentially relevant records passing the broader high-recall filter;
- `out_of_scope` — records retained in full local datasets but excluded from candidate outputs.

Extraction-query labels are not used for relevance classification, preventing circular classification decisions.

### Current funding candidate datasets

| Source | Core matches | Broad matches | Total candidates |
|---|---:|---:|---:|
| CORDIS | 416 | 259 | 675 |
| NSF | 1,757 | 907 | 2,664 |
| **Combined** | **2,173** | **1,166** | **3,339** |

### OpenAlex publication context

OpenAlex is stored separately from grant-level records because it has a different analytical grain.

The processed dataset contains:

- 40 unique topic-year records;
- eight selected research topics;
- complete annual coverage from 2021 through 2025;
- no duplicate topic-year combinations;
- no missing or negative publication counts.

Publication momentum is represented using:

- annual publication counts;
- year-over-year growth;
- a 2021 baseline index;
- total growth from 2021 to 2025;
- compound annual growth rate.

OpenAlex topic counts are compared within topics rather than summed together because the search queries may overlap. Publication growth is treated as evidence of research activity, not as proof of research quality or future funding availability.

### Processed outputs

#### CORDIS

- compact CORDIS candidate dataset containing 675 projects;
- full enriched CORDIS dataset retained locally.

#### NSF

- `nsf_candidate_awards_compact_2021_2025.csv`;
- 2,664 candidate awards across 27 application-ready fields;
- full cleaned and diagnostic datasets retained locally.

#### OpenAlex

- `openalex_topic_year_clean_2021_2025.csv`;
- `openalex_topic_momentum_summary_2021_2025.csv`;
- `openalex_cleaning_validation_summary.csv`.

### Data storage

Large raw and enriched datasets are stored locally and excluded from GitHub through `.gitignore`.

The repository contains compact processed outputs intended for:

- Python analysis;
- Tableau dashboards;
- the Streamlit application;
- cross-source integration.

Detailed cleaning decisions and validation steps are documented in:

- `Notebooks/02_cordis_cleaning.ipynb`;
- `Notebooks/03_nsf_cleaning.ipynb`;
- `Notebooks/04_openalex_preparation.ipynb`;
- the project decision log.