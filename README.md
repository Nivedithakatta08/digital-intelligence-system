# Digital Identity Intelligence System

NEURAX Hackathon 3.0 | Domain 3: AI in Cybersecurity
Problem: Public Profile & Digital Footprint Intelligence

An AI system that takes a consented image and limited context, then finds, links and verifies the person's public digital footprint. Every finding comes with a source and a confidence score.

## Problem

A person's public presence is split across platforms (Instagram, X, YouTube, LinkedIn, GitHub, websites, event pages) under different usernames, photos and name variants. Common names and incomplete profiles make manual matching slow and error-prone.

We are building an identity intelligence system, not a reverse-image search or a scraper. It must:
- Identify the most likely person
- Find public profiles, affiliations, events, projects, publications and patents
- Resolve aliases and usernames
- Build a timeline and relationship graph
- Attach evidence and confidence to every finding
- Flag uncertain or conflicting information

Only consented, public or synthetic data is used. No private accounts, leaked data or credential-based access.

## Architecture

```
Consented image + context
        |
Candidate hypotheses
        |
Cross-platform discovery
        |
Entity resolution
        |
Information extraction
        |
Evidence + confidence scoring
        |
Conflict detection
        |
Knowledge graph -> Graph | Timeline | Evidence report
```

## Approach

- **Hypotheses:** each candidate identity is a hypothesis, ranked by supporting and contradicting evidence.
- **Discovery:** search approved public sources for profiles matching each hypothesis.
- **Entity resolution:** merge aliases and usernames only when several signals agree (name, linked profiles, bio, image, shared affiliations).
- **Knowledge graph:** all findings are stored as nodes (Person, Account, Organization, Event, Project, Publication, Patent, Source) and edges with confidence and source. The timeline is built from the dated nodes.
- **Confidence:** based on source reliability, number of independent sources, match strength and contradictions.
- **False matches:** weak matches stay unmerged, conflicts are flagged, and "insufficient evidence" is reported instead of guessing.
- **No dataset needed:** pretrained models plus live public sources.

## Privacy

Consented and public data only. No sensitive attribute inference. Every output is traceable to a public source.

## Tech Stack

Python, pretrained face/image embeddings, LLM-based extraction, fuzzy matching, NetworkX, PyVis, Streamlit

## Setup

```bash
git clone <repo-url>
cd digital-identity-intelligence
pip install -r requirements.txt
cp .env.example .env   # add your API keys
streamlit run app.py
```

## Team

Niveditha Katta
Meghana Kammari
Kokonda Sravya
