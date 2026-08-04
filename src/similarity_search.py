from pathlib import Path
import json
import re

import joblib
import numpy as np
import pandas as pd
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity


# Resolve paths from the repository root
PROJECT_ROOT = Path(__file__).resolve().parents[1]

CATALOG_PATH = (
    PROJECT_ROOT
    / "Data"
    / "Processed_Data"
    / "Model"
    / "grant_search_catalog.csv"
)

CONFIGURATION_PATH = (
    PROJECT_ROOT
    / "Data"
    / "Processed_Data"
    / "Model"
    / "model_configuration.json"
)

VECTORIZER_PATH = (
    PROJECT_ROOT
    / "Models"
    / "tfidf_vectorizer.joblib"
)

MATRIX_PATH = (
    PROJECT_ROOT
    / "Models"
    / "grant_tfidf_matrix.npz"
)
def normalize_model_text(text):
    """Normalize terminology before TF-IDF transformation."""

    text = str(text).lower()

    text = re.sub(
        r"machine[-\s]learning",
        "machine learning",
        text,
    )
    text = re.sub(
        r"closed[-\s]loop",
        "closed loop",
        text,
    )
    text = re.sub(
        r"self[-\s]driving",
        "self driving autonomous",
        text,
    )
    text = re.sub(
        r"data[-\s]driven",
        "data driven",
        text,
    )
    text = re.sub(
        r"ai[-\s]guided",
        "ai guided",
        text,
    )

    # British/American spelling
    text = re.sub(
        r"\boptimisation\b",
        "optimization",
        text,
    )
    text = re.sub(
        r"\boptimise\b",
        "optimize",
        text,
    )
    text = re.sub(
        r"\boptimised\b",
        "optimized",
        text,
    )
    text = re.sub(
        r"\bmodelling\b",
        "modeling",
        text,
    )

    # Related scientific word forms
    text = re.sub(
        r"\b(catalysts|catalytic|catalysis)\b",
        "catalyst",
        text,
    )
    text = re.sub(
        r"\b(automated|automating|automation)\b",
        "automation",
        text,
    )
    text = re.sub(
        r"\b(robotic|robotics|robot-mediated)\b",
        "robot",
        text,
    )
    text = re.sub(
        r"\b(experiments|experimental)\b",
        "experimentation",
        text,
    )

    text = re.sub(
        r"[^a-z0-9\s]",
        " ",
        text,
    )
    text = re.sub(
        r"\s+",
        " ",
        text,
    ).strip()

    return text


def contains_term(text, term):
    """Check whether a normalized word or phrase occurs in text."""

    pattern = rf"\b{re.escape(term)}\b"

    return bool(
        re.search(
            pattern,
            str(text),
        )
    )


def detect_query_concepts(
    query,
    concept_lexicon,
):
    """Identify controlled concepts represented in a query."""

    normalized_query = normalize_model_text(query)

    return [
        concept_name
        for concept_name, terms in concept_lexicon.items()
        if any(
            contains_term(
                normalized_query,
                term,
            )
            for term in terms
        )
    ]


def calculate_concept_coverage(
    document_text,
    active_concepts,
    concept_lexicon,
):
    """Calculate the share of query concepts found in a document."""

    if not active_concepts:
        return 0.0

    matched_concepts = 0

    for concept_name in active_concepts:
        concept_terms = concept_lexicon[
            concept_name
        ]

        if any(
            contains_term(
                document_text,
                term,
            )
            for term in concept_terms
        ):
            matched_concepts += 1

    return matched_concepts / len(active_concepts)


def count_matching_term_occurrences(
    text,
    active_concepts,
    concept_lexicon,
):
    """Count occurrences of controlled terms in normalized text."""

    term_counts = {}

    for concept_name in active_concepts:
        for term in concept_lexicon[concept_name]:
            count = len(
                re.findall(
                    rf"\b{re.escape(term)}\b",
                    str(text),
                )
            )

            if count > 0:
                term_counts[term] = count

    return term_counts


def binary_concept_match(
    text,
    active_concepts,
    concept_lexicon,
):
    """Return 1 when any active concept appears in the text."""

    if not active_concepts:
        return 0.0

    return float(
        any(
            contains_term(text, term)
            for concept_name in active_concepts
            for term in concept_lexicon[concept_name]
        )
    )


def calculate_off_domain_penalty(
    title,
    query,
    application_lexicon,
    application_penalties,
):
    """Penalize unrelated application areas expressed in a title."""

    active_applications = detect_query_concepts(
        query,
        application_lexicon,
    )

    title_applications = detect_query_concepts(
        title,
        application_lexicon,
    )

    unrelated_applications = [
        application
        for application in title_applications
        if application not in active_applications
    ]

    return min(
        sum(
            application_penalties.get(
                application,
                0.0,
            )
            for application in unrelated_applications
        ),
        1.0,
    )

def load_model_assets():
    """Load and validate the exported GrantScopeAI model assets."""

    required_paths = [
        CATALOG_PATH,
        CONFIGURATION_PATH,
        VECTORIZER_PATH,
        MATRIX_PATH,
    ]

    missing_paths = [
        path
        for path in required_paths
        if not path.exists()
    ]

    if missing_paths:
        missing_names = ", ".join(
            str(path)
            for path in missing_paths
        )

        raise FileNotFoundError(
            f"Missing model assets: {missing_names}"
        )

    catalog_df = pd.read_csv(
        CATALOG_PATH
    )

    vectorizer = joblib.load(
        VECTORIZER_PATH
    )

    tfidf_matrix = load_npz(
        MATRIX_PATH
    )

    with open(
        CONFIGURATION_PATH,
        "r",
        encoding="utf-8",
    ) as configuration_file:
        configuration = json.load(
            configuration_file
        )

    if len(catalog_df) != tfidf_matrix.shape[0]:
        raise ValueError(
            "Catalogue rows do not match TF-IDF matrix rows."
        )

    if (
        tfidf_matrix.shape[1]
        != len(vectorizer.vocabulary_)
    ):
        raise ValueError(
            "TF-IDF matrix columns do not match "
            "the vectorizer vocabulary."
        )

    return {
        "catalog": catalog_df,
        "vectorizer": vectorizer,
        "matrix": tfidf_matrix,
        "configuration": configuration,
    }
def get_shared_tfidf_terms(
    query,
    model_row_id,
    vectorizer,
    tfidf_matrix,
    top_k=6,
):
    """Return the strongest TF-IDF terms shared by query and project."""

    normalized_query = normalize_model_text(query)

    query_vector = vectorizer.transform(
        [normalized_query]
    )

    document_vector = tfidf_matrix[
        int(model_row_id)
    ]

    shared_vector = query_vector.multiply(
        document_vector
    ).tocsr()

    if shared_vector.nnz == 0:
        return []

    feature_names = vectorizer.get_feature_names_out()

    ignored_terms = {
        "research",
        "project",
        "projects",
        "study",
        "studies",
        "method",
        "methods",
        "development",
        "develop",
        "using",
        "use",
        "new",
        "work",
    }

    ranked_features = sorted(
        zip(
            shared_vector.indices,
            shared_vector.data,
        ),
        key=lambda item: item[1],
        reverse=True,
    )

    selected_terms = []

    for feature_index, _ in ranked_features:
        term = feature_names[feature_index]

        if term in ignored_terms:
            continue

        if term not in selected_terms:
            selected_terms.append(term)

        if len(selected_terms) == top_k:
            break

    return selected_terms


def search_similar_projects(
    query,
    catalog_df,
    vectorizer,
    tfidf_matrix,
    configuration,
    top_n=10,
    source=None,
    topic=None,
    year_min=None,
    year_max=None,
):
    """Rank funded projects against a user-entered research concept."""

    if not str(query).strip():
        raise ValueError(
            "Please enter a research concept."
        )

    normalized_query = normalize_model_text(query)

    query_vector = vectorizer.transform(
        [normalized_query]
    )

    if query_vector.nnz == 0:
        raise ValueError(
            "The query does not contain terms recognized by the model."
        )

    similarity_scores = cosine_similarity(
        query_vector,
        tfidf_matrix,
    ).ravel()

    results_df = catalog_df.copy()
    results_df["similarity_score"] = similarity_scores

    # Apply optional filters
    if source and source != "All":
        results_df = results_df.loc[
            results_df["source"] == source
        ].copy()

    if topic and topic != "All":
        results_df = results_df.loc[
            results_df["primary_topic"] == topic
        ].copy()

    if year_min is not None:
        results_df = results_df.loc[
            results_df["award_year"] >= year_min
        ].copy()

    if year_max is not None:
        results_df = results_df.loc[
            results_df["award_year"] <= year_max
        ].copy()

    results_df = results_df.loc[
        results_df["similarity_score"] > 0
    ].copy()

    if results_df.empty:
        return results_df

    domain_lexicon = configuration[
        "domain_concept_lexicon"
    ]

    workflow_lexicon = configuration[
        "workflow_concept_lexicon"
    ]

    context_lexicon = configuration[
        "context_concept_lexicon"
    ]

    domain_context_expansion = configuration[
        "domain_context_expansion"
    ]

    application_lexicon = configuration[
        "application_lexicon"
    ]

    application_penalties = configuration[
        "application_penalties"
    ]

    ranking_weights = configuration[
        "ranking_weights"
    ]

    query_domain_concepts = detect_query_concepts(
        query,
        domain_lexicon,
    )

    query_workflow_concepts = detect_query_concepts(
        query,
        workflow_lexicon,
    )

    query_context_concepts = sorted(
        {
            context_concept
            for domain_concept in query_domain_concepts
            for context_concept in domain_context_expansion.get(
                domain_concept,
                [],
            )
        }
    )

    results_df["tfidf_relative_score"] = (
        results_df["similarity_score"]
        / results_df["similarity_score"].max()
    )

    # Specific domain score
    if query_domain_concepts:
        results_df["title_domain_match"] = (
            results_df["normalized_title"].apply(
                lambda text: binary_concept_match(
                    text,
                    query_domain_concepts,
                    domain_lexicon,
                )
            )
        )

        results_df["abstract_domain_density"] = (
            results_df["normalized_abstract"].apply(
                lambda text: min(
                    (
                        sum(
                            count_matching_term_occurrences(
                                text,
                                query_domain_concepts,
                                domain_lexicon,
                            ).values()
                        )
                        / max(
                            len(str(text).split()),
                            1,
                        )
                        * 100
                    ),
                    1.0,
                )
            )
        )

        results_df["specific_domain_score"] = np.where(
            results_df["title_domain_match"] == 1,
            1.0,
            0.50
            * results_df["abstract_domain_density"],
        )

    else:
        results_df["specific_domain_score"] = 0.0

    # Broader scientific context
    if query_context_concepts:
        results_df["context_score"] = (
            0.75
            * results_df["normalized_title"].apply(
                lambda text: calculate_concept_coverage(
                    text,
                    query_context_concepts,
                    context_lexicon,
                )
            )
            + 0.25
            * results_df["normalized_abstract"].apply(
                lambda text: calculate_concept_coverage(
                    text,
                    query_context_concepts,
                    context_lexicon,
                )
            )
        )

    else:
        results_df["context_score"] = 0.0

    # Research-workflow score
    if query_workflow_concepts:
        results_df["workflow_score"] = (
            0.60
            * results_df["normalized_title"].apply(
                lambda text: calculate_concept_coverage(
                    text,
                    query_workflow_concepts,
                    workflow_lexicon,
                )
            )
            + 0.40
            * results_df["normalized_abstract"].apply(
                lambda text: calculate_concept_coverage(
                    text,
                    query_workflow_concepts,
                    workflow_lexicon,
                )
            )
        )

    else:
        results_df["workflow_score"] = 0.0

    results_df["off_domain_penalty"] = (
        results_df["normalized_title"].apply(
            lambda title: calculate_off_domain_penalty(
                title,
                query,
                application_lexicon,
                application_penalties,
            )
        )
    )

    # Redistribute unavailable rule weights to TF-IDF
    tfidf_weight = ranking_weights["tfidf"]
    domain_weight = ranking_weights["specific_domain"]
    context_weight = ranking_weights["context"]
    workflow_weight = ranking_weights["workflow"]

    if not query_domain_concepts:
        tfidf_weight += domain_weight
        domain_weight = 0.0

    if not query_context_concepts:
        tfidf_weight += context_weight
        context_weight = 0.0

    if not query_workflow_concepts:
        tfidf_weight += workflow_weight
        workflow_weight = 0.0

    results_df["final_score"] = (
        tfidf_weight
        * results_df["tfidf_relative_score"]
        + domain_weight
        * results_df["specific_domain_score"]
        + context_weight
        * results_df["context_score"]
        + workflow_weight
        * results_df["workflow_score"]
        - ranking_weights["off_domain_penalty"]
        * results_df["off_domain_penalty"]
    )

    results_df = (
        results_df.sort_values(
            [
                "final_score",
                "similarity_score",
                "award_year",
                "grant_key",
            ],
            ascending=[False, False, False, True],
        )
        .drop_duplicates(
            subset="project_title_key",
            keep="first",
        )
        .head(top_n)
        .reset_index(drop=True)
    )

    results_df.insert(
        0,
        "rank",
        range(1, len(results_df) + 1),
    )

    results_df["similarity_pct"] = (
        results_df["similarity_score"]
        * 100
    ).round(1)

    results_df["final_score_pct"] = (
        results_df["final_score"]
        * 100
    ).round(1)

    results_df["similarity_pct"] = (
        results_df["similarity_score"]
        * 100
    ).round(1)

    results_df["final_score_pct"] = (
        results_df["final_score"]
        * 100
    ).round(1)

    results_df["shared_terms"] = (
        results_df.apply(
            lambda row: get_shared_tfidf_terms(
                query=query,
                model_row_id=row["model_row_id"],
                vectorizer=vectorizer,
                tfidf_matrix=tfidf_matrix,
                top_k=6,
            ),
            axis=1,
        )
    )

    results_df["similarity_pct"] = (
        results_df["similarity_score"] * 100
    ).round(1)

    results_df["final_score_pct"] = (
        results_df["final_score"] * 100
    ).round(1)

    results_df["shared_terms"] = results_df.apply(
        lambda row: get_shared_tfidf_terms(
            query=query,
            model_row_id=row["model_row_id"],
            vectorizer=vectorizer,
            tfidf_matrix=tfidf_matrix,
            top_k=6,
        ),
        axis=1,
    )

    results_df["why_it_matched"] = results_df.apply(
        lambda row: (
            "Shared concepts: "
            + ", ".join(row["shared_terms"])
            + ". "
            + "Scientific-domain evidence: "
            + f"{row['specific_domain_score']:.2f}; "
            + f"context: {row['context_score']:.2f}; "
            + f"workflow: {row['workflow_score']:.2f}."
        ),
        axis=1,
    )

    return results_df