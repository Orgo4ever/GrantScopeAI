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

  # Data preparation decision log

## 2026-08-01 to 2026-08-02 — CORDIS and NSF preparation

---

# Notebook 02 — CORDIS cleaning and preparation

## 1. Use the CORDIS bulk Horizon Europe datasets

**Decision:** Use the CORDIS bulk-download tables rather than collecting individual projects through repeated web or API requests.

**Rationale:** The bulk files provide structured project, programme, funding, and participant information and are more efficient and reproducible for large-scale analysis.

**Impact:** The notebook can rebuild the CORDIS dataset from the downloaded source tables without depending on repeated online requests.

---

## 2. Use one row per CORDIS project

**Decision:** Define the final analytical grain as one row per unique CORDIS project.

**Rationale:** Organisation and participation tables contain multiple rows for the same project because a project may involve several institutions, countries, and participant roles. Keeping these rows separately would cause project counts and funding totals to be duplicated.

**Impact:** Project-level information is retained once, while consortium information is aggregated into project-level fields.

---

## 3. Aggregate consortium participants and organisation roles

**Decision:** Combine participating organisations, countries, and roles into consolidated consortium fields before merging them with the project table.

**Rationale:** A single CORDIS project may have a coordinator and many partner organisations. This information remains analytically useful, but it must not change the one-project-per-row structure.

**Impact:** GrantScopeAI can analyse project coordinators and consortium composition without double-counting projects or funding.

---

## 4. Investigate duplicate project identifiers before consolidation

**Decision:** Review repeated project IDs before removing or aggregating rows.

**Rationale:** Repeated project IDs were primarily caused by the one-to-many relationship between projects and participating organisations rather than duplicated grant records.

**Impact:** Duplicate handling was based on the structure of the source data rather than automatically deleting repeated rows.

---

## 5. Standardize CORDIS dates and funding amounts

**Decision:** Convert project dates and financial values into consistent analytical formats while retaining the original source fields where useful.

**Rationale:** CORDIS bulk tables contain values that require explicit parsing before they can be filtered, compared, or visualized reliably.

**Impact:** Project start years, end dates, durations, and EU funding values can be used consistently in Python, Tableau, and Streamlit.

---

## 6. Use the 2021–2025 project start-date scope

**Decision:** Define the project period using the project start year and retain projects beginning from 2021 through 2025.

**Rationale:** This matches the common time window selected for NSF, CORDIS, and OpenAlex.

**Impact:** Of the 23,278 enriched CORDIS projects, 17,931 fall within the selected date range.

Only 30 CORDIS projects in the enriched data began in 2021, and none of those passed the AI and chemistry/materials relevance filters. As a result, relevant CORDIS candidates begin in 2022, but the 2021 boundary remains part of the documented project scope.

---

## 7. Create direct CORDIS source links

**Decision:** Generate a project URL for every CORDIS record.

**Rationale:** GrantScopeAI should allow users to verify project information and access the original funding record.

**Impact:** All cleaned CORDIS projects contain a traceable link back to their source page.

---

## 8. Use a tiered CORDIS relevance methodology

**Decision:** Use broad and refined keyword filters to identify projects combining AI with chemistry or materials research.

**Rationale:** A broad filter improves discovery coverage but can capture projects where keywords are incidental. A refined filter uses more specific AI and domain terminology to identify higher-confidence projects.

**Impact:** The final CORDIS candidate dataset contains:

- 416 `core_match` projects;
- 259 `broad_match` projects;
- 675 total candidate projects.

The broad tier remains available for discovery and manual review rather than being discarded.

---

## 9. Keep the full enriched CORDIS dataset local

**Decision:** Exclude the full enriched CORDIS file from GitHub and commit only the smaller candidate output.

**Rationale:** The enriched dataset contains more than 23,000 projects and over 60 columns and exceeds GitHub’s 100 MB file-size limit.

**Impact:** The large enriched file remains available locally, while the 675-project candidate dataset is version-controlled and suitable for later integration.

The following pattern was added to `.gitignore`:

```text
Data/Processed_Data/CORDIS/cordis_projects_enriched_*.csv

---

## 2026-08-02 — OpenAlex publication-context preparation

### 1. Keep OpenAlex separate from grant-level records

**Decision:** Store OpenAlex as a separate topic-year dataset rather than combining its rows directly with individual NSF or CORDIS grants.

**Rationale:** OpenAlex measures publication activity, while NSF and CORDIS contain individual funding awards. These sources have different analytical grains and should not be treated as equivalent records.

**Impact:** OpenAlex will provide publication-context and research-momentum indicators alongside, but separate from, the combined funding dataset.

---

### 2. Use one row per topic-year

**Decision:** Define the OpenAlex analytical grain as one row per research topic and publication year.

**Rationale:** The source contains eight selected topics across the five-year period from 2021 through 2025.

**Impact:** The final cleaned dataset contains 40 unique topic-year records with no duplicates or missing annual coverage.

---

### 3. Measure publication momentum within each topic

**Decision:** Calculate annual publication counts, year-over-year growth, a 2021 baseline index, total growth, and compound annual growth rate.

**Rationale:** These metrics describe how publication activity changes over time within each topic.

**Impact:** GrantScopeAI can compare research momentum across the selected fields while accounting for differences in starting publication volume.

---

### 4. Do not sum publication counts across topics

**Decision:** Compare publication trends within topics rather than adding the eight topic counts into a single publication total.

**Rationale:** The OpenAlex search queries may overlap, meaning the same publication could be counted under more than one topic.

**Impact:** Topic-level results remain interpretable without presenting potentially duplicated totals.

---

### 5. Treat publication growth as context rather than proof

**Decision:** Use OpenAlex growth metrics as indicators of research activity, not as direct measures of research quality, novelty, or future funding availability.

**Rationale:** A growing publication count shows increased activity but does not establish scientific importance or guarantee corresponding grant opportunities.

**Impact:** OpenAlex metrics will support GrantScopeAI recommendations without determining them on their own.

---

### 6. OpenAlex validation results

The cleaned OpenAlex dataset contains:

- 40 topic-year records;
- eight research topics;
- five years of complete coverage from 2021 through 2025;
- no duplicate topic-year combinations;
- no missing topic labels, years, or publication counts;
- no negative publication counts;
- eight expected missing year-over-year values for the 2021 baseline records.

Three processed outputs were created:

- `openalex_topic_year_clean_2021_2025.csv`;
- `openalex_topic_momentum_summary_2021_2025.csv`;
- `openalex_cleaning_validation_summary.csv`.

All OpenAlex outputs are small enough to remain under version control.