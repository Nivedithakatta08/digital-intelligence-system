# Digital Identity Intelligence System

**NEURAX Hackathon 3.0 | Domain 3: AI in Cybersecurity**

**Problem Statement:** Public Profile & Digital Footprint Intelligence

---

## Problem Understanding

A person's public digital presence is fragmented across platforms (Instagram, X/Twitter, YouTube, LinkedIn, websites, event pages, GitHub). Different usernames, aliases and incomplete profiles make manual correlation slow and error-prone.

Our system is an **AI-driven identity intelligence system** that:

* Generates the most likely public identity hypotheses from a consented image and limited context
* Discovers public social and professional profiles using approved public sources
* Uses the GitHub API for live public profile and repository discovery
* Uses Gemini for AI-assisted query generation, entity extraction and information structuring
* Resolves aliases and usernames across sources
* Identifies companies, roles, affiliations, events, projects and technical contributions
* Correlates information across multiple independent sources
* Builds a timeline and relationship graph
* Attaches evidence and confidence to important findings
* Flags uncertain, conflicting or insufficient information
* Uses a small synthetic dataset for testing, validation and false-match handling

---

## Architecture

```text
Consented image + limited context
        |
        v
Candidate hypotheses
        |
        v
Public source discovery
   /         |          \
  v          v           v
GitHub    Gemini API   Approved
 API                   public sources
   \         |          /
    \        |         /
     v       v        v
       Entity resolution
              |
              v
    Information extraction
              |
              v
    Evidence + confidence
              |
        +-----+-----+
        |           |
        v           v
   Conflict      Timeline
   detection        |
        |           |
        +-----+-----+
              |
              v
      Knowledge graph
              |
              v
    Graph + Report + UI
```

---

## Project Structure

```text
digital_identity_intelligence/
│
├── app.py
├── config.py
├── requirements.txt
│
├── connectors/
│   ├── github_connector.py
│   └── mock_connector.py
│
├── modules/
│   ├── discovery.py
│   ├── resolver.py
│   ├── extractor.py
│   ├── scorer.py
│   ├── conflict.py
│   ├── graph_builder.py
│   └── timeline.py
│
├── data/
│   └── mock_profiles.json
│
└── outputs/
    ├── report.json
    └── graph.html
```

---

## Approach

* **Hypothesis Generation:** Each candidate identity is treated as a hypothesis and evaluated using supporting and contradicting evidence.
* **Discovery:** GitHub API, Gemini-assisted query generation and organizer-approved public sources are used to discover relevant profiles and information.
* **Entity Resolution:** Names, aliases and usernames are correlated using multiple signals such as name, bio, organization, role, location and cross-source information.
* **Information Extraction:** Gemini converts relevant public-source text into structured entities such as organizations, roles, events, projects and publications.
* **Knowledge Graph:** Findings are represented as nodes (Person, Account, Organization, Event, Project, Publication, Source) and edges with confidence and source information.
* **Confidence Scoring:** Scores are based on match strength, source agreement, independent confirmations and detected contradictions.
* **Conflict Detection:** Contradictory information is explicitly identified instead of being silently discarded.
* **False Match Handling:** Weak matches remain separate, alternative candidates are retained and insufficient evidence is reported instead of forcing an identity.
* **Synthetic Validation:** A small synthetic dataset is used to test true matches, false matches, duplicate names, ambiguous candidates and conflict scenarios.

---

## Data Sources and AI

### GitHub API

The GitHub API provides live access to authorized public information such as:

* Public profiles
* Usernames
* Public repositories
* Organizations
* Profile metadata

### Gemini API

Gemini is used for:

* Query generation
* Entity extraction
* Alias normalization
* Information structuring
* Public-source text analysis
* Evidence summarization

Gemini-generated results are treated as analysis of source information. The original public source remains the evidence for a finding.

### Approved Public Sources

The architecture supports additional organizer-approved public sources through modular connectors. The system does not depend on a paid general-purpose search API.

### Synthetic Dataset

`data/mock_profiles.json` contains a small synthetic dataset used for:

* Testing
* Validation
* False-match handling
* Duplicate-name scenarios
* Confidence calibration

Synthetic records are never presented as real evidence.

---

## Privacy & Responsible Design

* Only consented and authorized input is used
* Public information is collected only from approved sources
* Synthetic data is clearly separated from real public-source evidence
* No private accounts, leaked data or credential-based access
* No access-control bypassing
* Every important finding is traceable to its source
* Uncertainty and conflicting information are explicitly reported
* No sensitive attribute inference
* An image alone is not treated as proof of identity

---

## Tech Stack

* **Python**
* **GitHub REST API**
* **Gemini API**
* **Streamlit**
* **RapidFuzz**
* **NetworkX**
* **PyVis**
* **JSON**
* **HTML**

---

## Outputs

The system generates:

* Identity candidates with confidence scores
* Public profile information
* Organizations and roles
* Events and projects
* Source-backed evidence
* Conflict information
* Chronological timeline
* Interactive relationship graph
* Structured JSON report

---

## Team

* Niveditha Katta
* Meghana Kammari
* Kokonda Sravya
