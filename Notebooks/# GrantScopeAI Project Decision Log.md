# GrantScopeAI Project Decision Log

This document records major scope, data, modelling, and implementation
decisions made during the GrantScopeAI project.

## 2026-08-01 — Revised project schedule

- Project work began on 1 August 2026.
- Final submission remains 14 August 2026.
- Core functionality remains protected.
- Secondary features will move to stretch status only when necessary.

## 2026-08-01 — Project problem and user confirmed

- Primary users are researchers and university research-support
  professionals.
- GrantScopeAI will help users assess how an AI-enabled chemistry or
  materials proposal fits within recent funding and publication activity.
- The system will support research intelligence and proposal positioning.
- It will not predict funding success or write complete grant proposals.

## 2026-08-01 — Scientific scope confirmed

Initial scope:

- AI-enabled chemistry
- AI-enabled materials research
- Machine learning and artificial intelligence
- Materials informatics
- Molecular modelling
- Reaction prediction
- Catalysis
- Autonomous or self-driving laboratories

The initial analytical period is 2021–2025.

## 2026-08-01 — Primary data sources selected

The project will use:

1. NSF Award Search for United States research grants.
2. CORDIS for European Union-funded research projects.
3. OpenAlex for publication momentum and scholarly context.

NIH RePORTER remains a fallback source rather than a required fourth
source.

## 2026-08-01 — NSF acquisition strategy

- A complete unrestricted NSF extraction was rejected because it was too
  broad and slow.
- Multiple targeted candidate queries were used instead.
- The extraction produced 33,125 candidate rows and 70 source columns.
- Duplicate award IDs and false-positive records will be handled in the
  NSF cleaning notebook.
- The full raw file will remain local and will not be committed to GitHub.

## 2026-08-01 — OpenAlex acquisition strategy

- The first OpenAlex dataset contains publication counts by topic and year.
- The summary covers eight topic categories across 2021–2025.
- Publication-level extraction is deferred until it is shown to be needed.
- Topic categories may overlap and should not be summed as unique works.

## 2026-08-01 — CORDIS acquisition strategy

- EURIO SPARQL access was successfully validated.
- Horizon Europe bulk CSV files were selected for the main acquisition.
- `project.csv` is the central one-row-per-project table.
- Supporting tables contain organisations, EuroSciVoc classifications,
  funding topics, legal-basis information, and web links.
- Supporting tables will be aggregated before merging to avoid
  many-to-many row multiplication.
- A standardized `project_id_clean` field will be used for CORDIS joins.
- Horizon 2020 remains available for later integration if needed.

## 2026-08-01 — Funding comparison rule

- NSF funding will remain reported in USD.
- CORDIS funding will remain reported in EUR.
- EUR and USD totals will not be directly combined unless a documented
  currency-conversion method is introduced.

## 2026-08-01 — Recommendation model

- A keyword-overlap method will be used as the baseline.
- TF-IDF and cosine similarity will be the primary recommendation model.
- Sentence embeddings and more advanced semantic search remain stretch
  features.

## 2026-08-01 — Grant-publication integration

- Grants and publications will remain in separate source-level tables.
- OpenAlex will provide aggregate topic and publication-momentum context.
- The project will not force unreliable row-level matches between grants
  and publications.

## 2026-08-01 — Streamlit MVP

The protected Streamlit MVP will contain:

1. Project overview
2. Funding landscape
3. Similar funded projects
4. Methods, data quality, and limitations

## 2026-08-01 — Repository data policy

- Raw datasets will be stored locally in `Data/Raw_Data`.
- Large raw datasets are excluded through `.gitignore`.
- Acquisition notebooks, queries, documentation, and small processed
  outputs will be committed.
- Sensitive or unnecessary contact fields will not be exposed in the
  application.