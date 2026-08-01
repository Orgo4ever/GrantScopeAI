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
