import streamlit as st
import pandas as pd

from src.similarity_search import (
    load_model_assets,
    search_similar_projects,
)
if "shortlist" not in st.session_state:
    st.session_state.shortlist = []

if "search_results" not in st.session_state:
    st.session_state.search_results = None

# ---------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------

st.set_page_config(
    page_title="GrantScopeAI",
    page_icon="🔬",
    layout="wide",
)


# ---------------------------------------------------
# MODEL LOADING
# ---------------------------------------------------

@st.cache_resource
def get_model_assets():
    """Load model assets once per Streamlit session."""

    return load_model_assets()


# ---------------------------------------------------
# PAGE HEADER
# ---------------------------------------------------

st.title("🔬 GrantScopeAI")

st.subheader(
    "Discover funded research projects related to your scientific concept"
)

st.write(
    """
    GrantScopeAI compares a research concept with funded NSF and CORDIS
    projects using an explainable similarity-search model.
    """
)

st.info(
    "GrantScopeAI identifies similar funded projects. "
    "It does not predict whether a proposal will receive funding."
)


# ---------------------------------------------------
# LOAD AND VALIDATE MODEL ASSETS
# ---------------------------------------------------

try:
    model_assets = get_model_assets()

except (FileNotFoundError, ValueError) as error:
    st.error(
        "The GrantScopeAI model could not be loaded."
    )
    st.exception(error)
    st.stop()

except Exception as error:
    st.error(
        "An unexpected model-loading error occurred."
    )
    st.exception(error)
    st.stop()


catalog_df = model_assets["catalog"]
vectorizer = model_assets["vectorizer"]
tfidf_matrix = model_assets["matrix"]
configuration = model_assets["configuration"]


# ---------------------------------------------------
# MODEL SUMMARY
# ---------------------------------------------------

st.success(
    "GrantScopeAI model assets loaded and validated successfully."
)

metric_1, metric_2, metric_3 = st.columns(3)

metric_1.metric(
    label="Search documents",
    value=f"{len(catalog_df):,}",
)

metric_2.metric(
    label="TF-IDF features",
    value=f"{tfidf_matrix.shape[1]:,}",
)

metric_3.metric(
    label="Data sources",
    value=catalog_df["source"].nunique(),
)

st.caption(
    "Active model: "
    f"{configuration.get(
        'model_name',
        'GrantScopeAI similarity model',
    )}"
)


# ---------------------------------------------------
# SEARCH FORM
# ---------------------------------------------------

st.divider()

st.header(
    "Search funded research projects"
)

example_query = (
    "Machine-learning-guided discovery of stable heterogeneous "
    "catalysts using automated experimentation and closed-loop "
    "optimisation."
)

research_concept = st.text_area(
    "Describe your research concept",
    value=example_query,
    height=140,
    help=(
        "Include the scientific area, research approach, "
        "and intended application."
    ),
)

# ---------------------------------------------------
# SIDEBAR FILTERS
# ---------------------------------------------------

with st.sidebar:
    st.header("Search filters")

    # Source filter
    source_options = [
        "All",
        *sorted(
            catalog_df["source"]
            .dropna()
            .unique()
            .tolist()
        ),
    ]

    selected_source = st.selectbox(
        "Funding source",
        options=source_options,
        index=0,
    )

    # Limit topic options to the selected source
    if selected_source == "All":
        filter_catalog_df = catalog_df.copy()

    else:
        filter_catalog_df = catalog_df.loc[
            catalog_df["source"] == selected_source
        ].copy()

    topic_options = [
        "All",
        *sorted(
            filter_catalog_df["primary_topic"]
            .dropna()
            .unique()
            .tolist()
        ),
    ]

    selected_topic = st.selectbox(
        "Primary topic",
        options=topic_options,
        index=0,
    )

    # Award-year filter
    minimum_year = int(
        catalog_df["award_year"].min()
    )

    maximum_year = int(
        catalog_df["award_year"].max()
    )

    selected_year_range = st.slider(
        "Award-year range",
        min_value=minimum_year,
        max_value=maximum_year,
        value=(minimum_year, maximum_year),
        step=1,
    )

    # Recommendation-count control
    number_of_results = st.slider(
        "Number of recommendations",
        min_value=1,
        max_value=20,
        value=10,
        step=1,
    )

    st.divider()

    st.caption(
        "Filters narrow the available grant catalogue "
        "before the final ranking is displayed."
    )

search_button = st.button(
    "Find similar funded projects",
    type="primary",
)


# ---------------------------------------------------
# RUN SEARCH
# ---------------------------------------------------

if search_button or st.session_state.search_results is not None:
    try:
        with st.spinner(
            "Comparing your concept with funded projects..."
        ):
                search_results_df = search_similar_projects(
                query=research_concept,
                catalog_df=catalog_df,
                vectorizer=vectorizer,
                tfidf_matrix=tfidf_matrix,
                configuration=configuration,
                top_n=number_of_results,
                source=selected_source,
                topic=selected_topic,
                year_min=selected_year_range[0],
                year_max=selected_year_range[1],
            )
                st.session_state.search_results = search_results_df
        if search_results_df.empty:
            st.warning(
                "No matching projects were found."
            )

        else:
            st.success(
                f"Found {len(search_results_df)} "
                "similar project families."
            )

            # ---------------------------------------
            # RESULT CARDS
            # ---------------------------------------
            for _, project in search_results_df.iterrows():

                project_key = (
                f"{project['source']}|"
                f"{project['title']}|"
                f"{project['award_year']}"
                )

                rank = int(project["rank"])

                already_saved = any(
                    item["project_key"] == project_key
                    for item in st.session_state.shortlist
                )

                result_title = (
                    f"#{rank}: {project['title']}"
                )

                with st.expander(
                    result_title,
                    expanded=rank <= 3,
                ):
                    # Main result metrics
                    score_col, source_col, year_col = st.columns(3)

                    score_col.metric(
                        "Relevance score",
                        f"{project['final_score_pct']:.1f}%",
                    )

                    source_col.metric(
                        "Source",
                        project["source"],
                    )

                    year_col.metric(
                        "Award year",
                        int(project["award_year"]),
                    )

                    st.caption(
                        "This score measures similarity to the "
                        "research concept. It is not a funding probability."
                    )
                    if already_saved:
                        st.success("✓ Saved to shortlist")

                    else:
                        if st.button(
                            "☆ Add to shortlist",
                            key=f"save_{project_key}",
                        ):
                            saved_project = project.to_dict()
                            saved_project["project_key"] = project_key

                            st.session_state.shortlist.append(
                                saved_project
                            )

                            st.rerun()

                    # Topic
                    st.markdown(
                        f"**Topic:** {project['primary_topic']}"
                    )

                    # Explanation
                    st.markdown(
                        f"**Why it matched:** "
                        f"{project['why_it_matched']}"
                    )

                    shared_terms = project.get(
                        "shared_terms",
                        [],
                    )

                    if shared_terms:
                        st.markdown(
                            "**Shared terms:** "
                            + " · ".join(shared_terms)
                        )

                    # Organisation
                    organisation = str(
                        project.get(
                            "organisation_name",
                            "",
                        )
                    ).strip()

                    if (
                        organisation
                        and organisation.lower() != "nan"
                    ):
                        st.markdown(
                            f"**Organisation:** {organisation}"
                        )

                    # Programme
                    programme = str(
                        project.get(
                            "programme_name",
                            "",
                        )
                    ).strip()

                    if (
                        programme
                        and programme.lower() != "nan"
                    ):
                        st.markdown(
                            f"**Programme:** {programme}"
                        )

                    # Funding amount
                    amount = project.get(
                        "amount_native",
                        None,
                    )

                    currency = str(
                        project.get(
                            "currency",
                            "",
                        )
                    ).strip()

                    if (
                        amount is not None
                        and str(amount).lower() != "nan"
                    ):
                        try:
                            funding_amount = float(amount)

                            funding_text = (
                                f"{currency} "
                                f"{funding_amount:,.0f}"
                            ).strip()

                            st.markdown(
                                f"**Award amount:** {funding_text}"
                            )

                        except (TypeError, ValueError):
                            pass

                    # Project abstract
                    abstract = str(
                        project.get(
                            "abstract",
                            "",
                        )
                    ).strip()

                    if (
                        abstract
                        and abstract.lower() != "nan"
                    ):
                        st.markdown(
                            "**Project summary**"
                        )

                        st.write(abstract)

                    # Original source link
                    source_url = str(
                        project.get(
                            "source_url",
                            "",
                        )
                    ).strip()

                    if (
                        source_url
                        and source_url.lower() != "nan"
                    ):
                        st.link_button(
                            "Open original grant record",
                            source_url,
                        )

    except ValueError as error:
        st.warning(
            str(error)
        )

    except Exception as error:
        st.error(
            "The search could not be completed."
        )
        st.exception(error)
# -----------------------------
# SHORTLIST DISPLAY
# -----------------------------

st.divider()
st.subheader("⭐ Saved Project Shortlist")
selected_compare_keys = []

if not st.session_state.shortlist:
    st.info("No projects saved yet.")

else:
    st.write(
        f"You have saved {len(st.session_state.shortlist)} project(s)."
    )
    shortlist_df = pd.DataFrame(
        st.session_state.shortlist
    )

    st.download_button(
        "⬇ Download full shortlist",
        data=shortlist_df.to_csv(index=False),
        file_name="grantscope_shortlist.csv",
        mime="text/csv",
    )
    project_lookup = {
        item["project_key"]: item
        for item in st.session_state.shortlist
    }

    selected_compare_keys = st.multiselect(
        "Select up to 3 projects to compare",
        options=list(project_lookup.keys()),
        format_func=lambda key: project_lookup[key].get(
            "title",
            "Untitled project",
        ),
        max_selections=3,
    )
if selected_compare_keys:
        st.markdown("### Project Comparison")

        compare_projects = [
            project_lookup[key]
            for key in selected_compare_keys
        ]

        compare_columns = st.columns(
            len(compare_projects)
        )

        for column, compare_project in zip(
            compare_columns,
            compare_projects,
        ):
            with column:
                st.markdown(
                    f"#### {compare_project.get('title', 'Untitled project')}"
                )

                st.metric(
                    "Relevance",
                    f"{compare_project.get('final_score_pct', 0):.1f}%",
                )

                st.markdown(
                    f"**Source:** "
                    f"{compare_project.get('source', '')}"
                )

                st.markdown(
                    f"**Year:** "
                    f"{compare_project.get('award_year', '')}"
                )

                st.markdown(
                    f"**Topic:** "
                    f"{compare_project.get('primary_topic', '')}"
                )

                organisation = str(
                    compare_project.get(
                        "organisation_name",
                        "",
                    )
                ).strip()

                if (
                    organisation
                    and organisation.lower() != "nan"
                ):
                    st.markdown(
                        f"**Organisation:** {organisation}"
                    )

                amount = compare_project.get(
                    "amount_native",
                    None,
                )

                currency = str(
                    compare_project.get(
                        "currency",
                        "",
                    )
                ).strip()

                if (
                    amount is not None
                    and str(amount).lower() != "nan"
                ):
                    try:
                        funding_amount = float(amount)

                        st.markdown(
                            f"**Funding:** {currency} "
                            f"{funding_amount:,.0f}"
                        )

                    except (TypeError, ValueError):
                        pass

                st.markdown("**Why it matched:**")

                st.write(
                    compare_project.get(
                        "why_it_matched",
                        "",
                    )
                )
        compare_df = pd.DataFrame(
            compare_projects
        )

        st.download_button(
            "⬇ Download comparison as CSV",
            data=compare_df.to_csv(index=False),
            file_name="grantscope_project_comparison.csv",
            mime="text/csv",
        )
for saved_project in st.session_state.shortlist:

    shortlist_title = (
        f"{saved_project.get('title', 'Untitled project')}"
    )

    with st.expander(shortlist_title):

        st.caption(
            f"{saved_project.get('source', '')} · "
            f"{saved_project.get('award_year', '')}"
        )

        st.markdown(
            f"**Topic:** "
            f"{saved_project.get('primary_topic', '')}"
        )

        organisation = str(
            saved_project.get(
                "organisation_name",
                "",
            )
        ).strip()

        if organisation and organisation.lower() != "nan":
            st.markdown(
                f"**Organisation:** {organisation}"
            )

        abstract = str(
            saved_project.get(
                "abstract",
                "",
            )
        ).strip()

        if abstract and abstract.lower() != "nan":
            st.markdown("**Project summary**")
            st.write(abstract)

        source_url = str(
            saved_project.get(
                "source_url",
                "",
            )
        ).strip()

        if source_url and source_url.lower() != "nan":
            st.link_button(
                "Open original grant record",
                source_url,
            )

        if st.button(
            "Remove from shortlist",
            key=f"remove_{saved_project.get('project_key')}",
        ):
            st.session_state.shortlist = [
                item
                for item in st.session_state.shortlist
                if item.get("project_key")
                != saved_project.get("project_key")
            ]

            st.rerun()
# -----------------------------
# RECOMMENDED STARTING POINTS
# -----------------------------

st.divider()

st.header("🧭 Recommended Starting Points")

st.caption(
    "Use your current research concept to identify organisations, "
    "funding programmes, related topics, and funded projects worth exploring."
)

if st.session_state.search_results is None:
    st.info(
        "Run a research concept search above to generate recommendations."
    )

else:
    recommendation_results = (
        st.session_state.search_results.copy()
    )

    st.subheader("🏛 Relevant Research Organisations")

    organisation_results = recommendation_results[
        recommendation_results["organisation_name"].notna()
    ].copy()

    organisation_results["organisation_name"] = (
        organisation_results["organisation_name"]
        .astype(str)
        .str.strip()
    )

    organisation_results = organisation_results[
        organisation_results["organisation_name"] != ""
    ]

    organisation_results["final_score_pct"] = pd.to_numeric(
        organisation_results["final_score_pct"],
        errors="coerce",
    )

    top_organisations = (
        organisation_results
        .groupby("organisation_name")
        .agg(
            matched_projects=("title", "count"),
            average_relevance=("final_score_pct", "mean"),
        )
        .reset_index()
        .sort_values(
            by=[
                "matched_projects",
                "average_relevance",
            ],
            ascending=False,
        )
        .head(5)
    )

    for _, organisation in top_organisations.iterrows():
        st.markdown(
            f"**{organisation['organisation_name']}**"
        )

        st.caption(
            f"{int(organisation['matched_projects'])} matched project(s) · "
            f"{organisation['average_relevance']:.1f}% average relevance"
        )
    st.subheader("💰 Relevant Funding Programmes")

    programme_results = recommendation_results[
        recommendation_results["programme_name"].notna()
    ].copy()

    programme_results["programme_name"] = (
        programme_results["programme_name"]
        .astype(str)
        .str.strip()
    )

    programme_results = programme_results[
        programme_results["programme_name"] != ""
    ]

    programme_results["final_score_pct"] = pd.to_numeric(
        programme_results["final_score_pct"],
        errors="coerce",
    )

    top_programmes = (
        programme_results
        .groupby("programme_name")
        .agg(
            matched_projects=("title", "count"),
            average_relevance=("final_score_pct", "mean"),
        )
        .reset_index()
        .sort_values(
            by=[
                "matched_projects",
                "average_relevance",
            ],
            ascending=False,
        )
        .head(5)
    )

    for _, programme in top_programmes.iterrows():
        st.markdown(
            f"**{programme['programme_name']}**"
        )

        st.caption(
            f"{int(programme['matched_projects'])} matched project(s) · "
            f"{programme['average_relevance']:.1f}% average relevance"
        )
    st.subheader("🧩 Related Research Areas")

    topic_results = recommendation_results[
        recommendation_results["primary_topic"].notna()
    ].copy()

    topic_results["primary_topic"] = (
        topic_results["primary_topic"]
        .astype(str)
        .str.strip()
    )

    topic_results = topic_results[
        topic_results["primary_topic"] != ""
    ]

    topic_results["final_score_pct"] = pd.to_numeric(
        topic_results["final_score_pct"],
        errors="coerce",
    )

    related_topics = (
        topic_results
        .groupby("primary_topic")
        .agg(
            matched_projects=("title", "count"),
            average_relevance=("final_score_pct", "mean"),
        )
        .reset_index()
        .sort_values(
            by=[
                "matched_projects",
                "average_relevance",
            ],
            ascending=False,
        )
        .head(5)
    )

    for _, topic in related_topics.iterrows():
        st.markdown(
            f"**{topic['primary_topic']}**"
        )

        st.caption(
            f"{int(topic['matched_projects'])} matched project(s) · "
            f"{topic['average_relevance']:.1f}% average relevance"
        )

    st.subheader("🚀 Suggested Places to Start")

    best_topic = None
    best_programme = None
    best_organisation = None

    if not related_topics.empty:
        best_topic = related_topics.iloc[0][
            "primary_topic"
        ]

    if not top_programmes.empty:
        best_programme = top_programmes.iloc[0][
            "programme_name"
        ]

    if not top_organisations.empty:
        best_organisation = top_organisations.iloc[0][
            "organisation_name"
        ]

    recommendation_parts = []

    if best_topic:
        recommendation_parts.append(
            f"explore **{best_topic}** as the strongest related research area"
        )

    if best_programme:
        recommendation_parts.append(
            f"review **{best_programme}** because it has funded similar work"
        )

    if best_organisation:
        recommendation_parts.append(
            f"look at work from **{best_organisation}** for relevant funded examples"
        )

    if recommendation_parts:
        st.info(
            "Based on your research concept, a useful starting strategy is to "
            + "; ".join(recommendation_parts)
            + "."
        )

    st.markdown("#### Funded projects worth reviewing first")

    top_starting_projects = (
        recommendation_results
        .sort_values(
            "final_score_pct",
            ascending=False,
        )
        .head(3)
    )

    for _, project in top_starting_projects.iterrows():

        with st.container(border=True):

            st.markdown(
                f"**{project['title']}**"
            )

            st.caption(
                f"{project['source']} · "
                f"{int(project['award_year'])} · "
                f"{project['final_score_pct']:.1f}% relevance"
            )

            st.markdown(
                f"**Topic:** {project['primary_topic']}"
            )

            st.write(
                project.get(
                    "why_it_matched",
                    "",
                )
            )

            project_url = str(
                project.get(
                    "source_url",
                    "",
                )
            ).strip()

            if (
                project_url
                and project_url.lower() != "nan"
            ):
                st.link_button(
                    "View funded project",
                    project_url,
                )

    st.caption(
        "These recommendations are based on historical funded projects "
        "in the GrantScopeAI dataset and do not indicate that a programme "
        "is currently accepting applications."
    )