import streamlit as st

from src.similarity_search import (
    load_model_assets,
    search_similar_projects,
)


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

if search_button:
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
                rank = int(project["rank"])

                result_title = (
                    f"#{rank} — {project['title']}"
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