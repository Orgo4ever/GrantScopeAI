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
---

## 2026-08-02 — Funding integration, topic mapping, and quality reporting

### 1. Combine NSF and CORDIS at the grant level

**Decision:** Standardize NSF and CORDIS into a shared schema and append them into one integrated funding table.

**Rationale:** Both sources describe individual funded research activities, even though their original field names and metadata structures differ. They do not share identifiers, so the records are appended rather than joined to one another.

**Impact:** The integrated funding table contains:

- 675 CORDIS projects;
- 2,664 NSF awards;
- 3,339 total funding records;
- 25 final analytical columns;
- no duplicate global grant keys.

Source-prefixed identifiers are used:

- `CORDIS_<project_id>`;
- `NSF_<award_id>`.

---

### 2. Use explicit source-to-standard field mappings

**Decision:** Create a documented schema crosswalk before integrating the funding sources.

**Rationale:** Fields are combined only when their analytical meanings are sufficiently comparable.

Important mappings include:

- CORDIS `objective` and NSF `abstract` → `abstract`;
- CORDIS `coordinator_name` and NSF `organisation_name` → `organisation_name`;
- CORDIS `call_topic_title` and NSF `programme_name` → `programme_name`;
- source start dates → standardized `start_date`;
- start-date year → standardized `award_year`.

**Impact:** Shared fields can be analysed consistently while source-specific fields remain available separately.

---

### 3. Use maximum EU contribution as the primary CORDIS funding amount

**Decision:** Use `ecMaxContribution` as the CORDIS `amount_native`.

**Rationale:** `ecMaxContribution` represents the maximum EU funding contribution and is complete across the 675 candidate projects.

The alternative `totalCost` field was not selected as the primary amount because:

- some projects report a total cost of zero;
- EU contribution exceeds reported total cost for 270 projects;
- the field is not sufficiently consistent for use as the main award value.

**Impact:** CORDIS funding is represented using EU contribution, while `totalCost` remains available separately as `project_total_cost`.

---

### 4. Preserve source-specific funding concepts

**Decision:** Retain funding fields that do not have direct equivalents rather than forcing them into one definition.

**Rationale:** The sources report different financial concepts:

- CORDIS provides maximum EU contribution and total project cost;
- NSF provides estimated total award value and obligated funding.

**Impact:** The integrated table preserves:

- `amount_native` for the selected primary source amount;
- `project_total_cost` for CORDIS;
- `amount_obligated` for NSF.

These fields must be interpreted according to their source definitions.

---

### 5. Keep EUR and USD separate

**Decision:** Preserve all funding values in their native currencies.

**Rationale:** No exchange-rate source, reference date, or currency-conversion methodology has been defined.

**Impact:**

- CORDIS values remain in EUR;
- NSF values remain in USD;
- funding summaries are grouped by source and currency;
- no combined EUR–USD funding total is calculated.

---

### 6. Do not infer missing source-specific classifications

**Decision:** Leave unavailable fields missing rather than deriving them from loosely related metadata.

**Rationale:** The CORDIS `nature` field is missing for all 675 candidate projects. CORDIS funding schemes are not equivalent to the NSF activity categories.

NSF also has no directly comparable equivalent for the CORDIS funding-scheme field.

**Impact:**

- `activity_type` is available for NSF but remains missing for CORDIS;
- `source_activity_type` remains missing for CORDIS;
- `funding_mechanism` is available for CORDIS but remains missing for NSF.

---

### 7. Use a shared eight-topic research taxonomy

**Decision:** Classify NSF and CORDIS grants using the same eight topics represented in OpenAlex:

1. Autonomous laboratories;
2. Reaction prediction;
3. AI-enabled catalysis;
4. Materials informatics;
5. Cheminformatics;
6. Molecular machine learning;
7. AI-enabled materials;
8. AI-enabled chemistry.

**Rationale:** A shared topic vocabulary is required to compare funding activity with publication momentum.

**Impact:** Topic labels align exactly across NSF, CORDIS, and OpenAlex.

---

### 8. Use transparent rule-based topic assignment

**Decision:** Assign topics using documented keyword rules applied to:

- title;
- abstract;
- programme name;
- funding mechanism where available.

**Rationale:** A transparent rule-based approach is easier to inspect, explain, and reproduce than an opaque classifier at this project stage.

**Impact:** Each grant receives:

- all valid matches in `matched_topics`;
- the number of named matches in `topic_match_count`;
- one priority-based `primary_topic`.

Narrower categories are prioritized over broader umbrella categories.

---

### 9. Refine the broad materials and chemistry rules after review

**Decision:** Expand the `AI-enabled materials` and `AI-enabled chemistry` rules after reviewing a reproducible sample of unclassified grants.

**Rationale:** The initial rules missed relevant projects involving:

- polymers and composites;
- coatings and thin films;
- semiconductors;
- additive manufacturing;
- fracture and deformation;
- chemical-process engineering;
- molecular simulation and spectroscopy.

Unrelated robotics, cybersecurity, astronomy, and general biomedical terminology was not added.

**Impact:**

- 403 additional grants received a named topic;
- named-topic coverage increased to 2,239 grants;
- 1,100 grants remained in the fallback category.

---

### 10. Retain a documented fallback topic

**Decision:** Keep unmatched candidate grants under:

`Other AI-enabled chemistry/materials`

**Rationale:** The eight named topics are intentionally narrower than the complete funding-candidate scope. Forcing every grant into a named topic would create weak or misleading classifications.

**Impact:** The 1,100 fallback grants remain usable in GrantScopeAI without being presented as stronger topic matches than their text supports.

---

### 11. Preserve multi-topic relationships

**Decision:** Create a separate grant-topic bridge with one row per valid grant–topic relationship.

**Rationale:** Many interdisciplinary grants legitimately match more than one topic. Using only the primary topic would discard useful information.

**Impact:** The bridge contains:

- 3,245 grant-topic relationships;
- 2,239 unique grants;
- all eight named topics;
- no duplicate grant-topic pairs.

Because grants may occur under several topics, topic totals must not be added together and interpreted as unique-grant totals.

---

### 12. Create a complete topic-year funding grid

**Decision:** Represent all topic-year-source combinations, including combinations with no observed grants.

**Rationale:** Missing combinations should not disappear from charts or comparisons.

The complete grid contains:

- eight topics;
- five years from 2021 through 2025;
- two funding sources.

**Impact:** The funding summary contains 80 rows.

For zero-grant combinations:

- grant counts are set to zero;
- total funding is set to zero;
- mean and median award values remain missing because no award distribution exists.

Nineteen of the 80 combinations contain zero grants.

---

### 13. Keep OpenAlex separate from grant-level data

**Decision:** Integrate OpenAlex only at the shared topic-year level.

**Rationale:** OpenAlex represents publication activity rather than individual funding awards.

**Impact:** OpenAlex is not merged directly into individual NSF or CORDIS records.

Instead, a 40-row topic-year context table presents:

- CORDIS grant counts and EUR funding;
- NSF grant counts and USD funding;
- OpenAlex publication counts and growth metrics.

---

### 14. Build a machine-readable integrated quality report

**Decision:** Consolidate integration checks into one structured quality-report table.

**Rationale:** Quality evidence should be reproducible and usable outside the notebook.

Each rule records:

- source;
- processing stage;
- validation rule;
- records checked;
- failures and failure rate;
- severity;
- status;
- required action;
- example identifiers where relevant.

**Impact:** The report contains 20 quality rules:

- 19 rules returned `PASS`;
- one informational rule returned `REVIEW`.

The review result represents grants retained in the fallback topic category and does not indicate failed processing.

---

### 15. Create formal integration documentation

**Decision:** Export both a schema crosswalk and a data dictionary.

**Rationale:** The integrated table contains fields with different source availability and interpretation constraints.

**Impact:** The data dictionary documents all 25 final grant columns, including:

- data type;
- analytical definition;
- source availability;
- nullability;
- transformation method;
- interpretation limitations.

---

### 16. Export and independently verify all integrated outputs

**Decision:** Export the integration outputs to:

`Data/Processed_Data/Integrated/`

The outputs are:

- `grants_clean_2021_2025.csv`;
- `grant_topic_bridge_2021_2025.csv`;
- `grant_topic_year_summary_2021_2025.csv`;
- `topic_year_context_2021_2025.csv`;
- `data_quality_report.csv`;
- `data_dictionary.csv`;
- `funding_schema_crosswalk.csv`;
- `topic_mapping.csv`.

**Rationale:** The outputs support separate analytical needs, including grant-level analysis, many-to-many topic analysis, Tableau, Streamlit, and quality review.

**Impact:** All eight files were reloaded successfully after export and matched their expected row and column counts.

---

### Day 5 completion status

The three processed sources have now been integrated into a documented analytical structure.

Final outputs include:

- 3,339 integrated funding records;
- 2,239 grants with at least one named topic;
- 3,245 grant-topic relationships;
- 1,100 fallback-topic grants;
- an 80-row complete funding topic-year grid;
- a 40-row funding-and-publication context table;
- a 20-rule integrated quality report;
- a 25-column data dictionary.

**Next step:** Conduct exploratory data analysis using the integrated grant table, topic bridge, and topic-year context outputs.