## Project Status

Completed:

- NSF data extraction and cleaning
- CORDIS data cleaning
- OpenAlex topic-year publication data
- cross-source integration and validation
- exploratory data analysis
- Tableau-ready analytical outputs
- TF-IDF similarity model
- context-aware hybrid ranking
- manual benchmark and generalization testing
- exported and validated model package
- working Streamlit similarity-search MVP
- source, topic, year, and recommendation-count filters
- explainable recommendation cards

In progress:

- final interface refinement
- Tableau dashboard completion
- final documentation and screenshots
- presentation development
- deployment preparation

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

## Integrated data model

The processed NSF and CORDIS candidate datasets have been standardized into a shared grant-level structure.

The integrated funding table contains:

- **3,339 unique funding records**;
- **675 CORDIS projects**;
- **2,664 NSF awards**;
- **25 application-ready columns**;
- no duplicate global grant identifiers;
- complete coverage within the 2021–2025 project period.

NSF and CORDIS are appended rather than joined because they represent separate funded activities and do not share identifiers.

Source-prefixed grant keys are used to maintain global uniqueness:

- `CORDIS_<project_id>`;
- `NSF_<award_id>`.

### Funding definitions

The primary funding amount depends on the source:

- **CORDIS:** maximum EU contribution, reported in EUR;
- **NSF:** estimated total award value, reported in USD.

Additional source-specific financial fields are retained:

- CORDIS total project cost;
- NSF obligated funding.

EUR and USD values remain separate. No cross-currency totals are calculated because an exchange-rate methodology has not been defined.

## Shared research-topic taxonomy

Funding records are mapped to the same eight research topics used in the OpenAlex publication dataset:

1. Autonomous laboratories
2. Reaction prediction
3. AI-enabled catalysis
4. Materials informatics
5. Cheminformatics
6. Molecular machine learning
7. AI-enabled materials
8. AI-enabled chemistry

Topic assignments use transparent keyword rules applied to grant titles, abstracts, programmes, and funding-mechanism text where available.

Each grant contains:

- a priority-based `primary_topic`;
- all matched topics in `matched_topics`;
- the number of named topic matches.

Final topic coverage includes:

- **2,239 grants** assigned to at least one named topic;
- **3,245 grant-topic relationships**;
- **1,100 grants** retained under `Other AI-enabled chemistry/materials`.

The fallback category prevents weak or unsupported topic assignments.

Because individual grants may match multiple topics, counts and funding totals across topics should not be added together as unique-grant totals.

## Topic-year analytical tables

Two topic-year structures support later analysis and dashboarding.

### Funding topic-year summary

The complete funding grid contains:

- eight topics;
- five years from 2021 through 2025;
- two funding sources;
- **80 source-topic-year rows**.

Combinations with no observed grants are represented explicitly with zero grant counts and zero total funding.

### Three-source context table

The funding summaries are aligned with OpenAlex at the topic-year level.

The resulting **40-row context table** contains:

- CORDIS grant counts and EUR funding;
- NSF grant counts and USD funding;
- OpenAlex publication counts and growth metrics.

OpenAlex remains separate from individual grant records because it measures publication activity rather than funding awards.

## Data quality and documentation

The integrated quality report contains **20 validation rules** covering:

- source row-count reconciliation;
- unique grant identifiers;
- field completeness;
- valid dates, amounts, currencies, and URLs;
- relevance-tier values;
- grant-topic relationship uniqueness;
- OpenAlex topic-year completeness;
- taxonomy alignment across sources.

Results:

- **19 rules passed**;
- **1 informational rule requires review**.

The review result represents grants intentionally retained in the fallback topic category and does not indicate failed processing.

A formal data dictionary and schema crosswalk document:

- column definitions;
- source availability;
- data types;
- transformation logic;
- nullability;
- interpretation limitations.

## Integrated processed outputs

The following files are stored in:

```text
Data/Processed_Data/Integrated/

## EDA summary

The exploratory analysis identified several useful research-intelligence patterns:

- AI-enabled materials and chemistry have the largest funding and publication footprints.
- AI-enabled catalysis combines strong publication momentum with substantial grant activity.
- Autonomous laboratories shows the fastest relative publication growth but remains small in absolute funding volume.
- Materials informatics and reaction prediction show publication growth alongside lower recent grant activity.
- NSF and CORDIS differ in their programme, organisation, geographic, and award-value structures.
- Status fields are useful as source-specific filters but are not directly comparable.

A manually reviewed demonstration set was created for the similarity model, and ten validated EDA outputs were exported for Tableau, Streamlit, and Notebook 07.

The next step is to build and evaluate the explainable project-similarity model.

## 2026-08-03 — Select context-aware hybrid similarity model

### Decision

GrantScopeAI will use a context-aware hybrid recommendation model combining:

- normalized, title-weighted TF-IDF;
- cosine similarity;
- scientific-domain evidence;
- broader chemistry and reaction context;
- research-workflow coverage;
- a small penalty for clearly unrelated application areas;
- project-title diversification to prevent collaborative award families from dominating the results.

The model searches 2,943 unique modelling documents while preserving links to all 3,339 original grant records.

### Rationale

A simple keyword-overlap baseline was transparent but gave equal importance to common and distinctive terms.

The initial TF-IDF model improved term weighting, but its ranking did not align sufficiently with the manually reviewed benchmark. Several relevant chemistry projects ranked below a weaker drug-discovery example.

Successive model versions were evaluated:

1. Initial TF-IDF
2. Normalized, title-weighted TF-IDF
3. Concept-aware hybrid
4. Field-aware hybrid
5. Context-aware hybrid

The context-aware hybrid produced the clearest separation between relevant and off-domain projects:

- 3 of 7 relevant projects ranked in the top 25;
- 5 of 7 ranked in the top 50;
- the best strong match improved from rank 54 to rank 14;
- the weak drug-discovery comparison fell to rank 212;
- all 7 relevant projects ranked above the weak comparison.

### Validation

The final model was tested with three distinct research concepts:

- machine-learning-guided catalyst discovery;
- sustainable polymer materials;
- autonomous reaction laboratories.

Each query returned five unique project families with explainable shared terms.

The exported catalogue, vectorizer, sparse matrix, configuration, and evaluation files were independently reloaded. All 8 validation checks passed.

### Limitations

The eight-project manual benchmark is small and query-specific. It is used as a qualitative retrieval check rather than a formal accuracy estimate.

The model identifies similar funded research projects. It does not predict funding success or proposal acceptance because rejected-proposal data are not available.

Further tuning against the same benchmark was avoided to reduce overfitting.

### Consequences

The selected model is explainable, computationally lightweight, and suitable for deployment in Streamlit.

Each recommendation can display:

- similarity and final ranking scores;
- shared scientific terms;
- domain, context, and workflow evidence;
- source, programme, organisation, year, and funding metadata;
- links back to the original grant record.