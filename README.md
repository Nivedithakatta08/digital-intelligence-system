# Digital Identity Intelligence System

**NEURAX Hackathon 3.0 | Domain 3: AI in Cybersecurity**
**Problem Statement:** Public Profile & Digital Footprint Intelligence

---

## Problem Understanding
A person's public digital presence is fragmented across platforms (Instagram, X/Twitter, YouTube, LinkedIn, GitHub, websites, event pages). Different usernames, aliases and incomplete profiles make manual correlation slow and error-prone.

Our system is **not** a reverse-image search or a generic scraper. It is an **AI-driven identity intelligence system** that:
- Identifies the most likely public identity from a consented image and context
- Discovers social and professional profiles, affiliations, events, projects, publications and patents
- Resolves aliases and usernames
- Builds a timeline and relationship graph
- Attaches evidence and confidence to every finding
- Flags uncertain or conflicting information

---

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

---

## Approach

- **Hypothesis Generation:** Each candidate identity is treated as a hypothesis, ranked by supporting and contradicting evidence.
- **Discovery:** Search approved public sources for matching profiles.
- **Entity Resolution:** Merge aliases and usernames only when multiple signals agree (name, bio, image, affiliations).
- **Knowledge Graph:** Findings are stored as nodes (Person, Account, Organization, Event, Project, Publication, Patent, Source) and edges with confidence and source. The timeline is built from the dated nodes.
- **Confidence Scoring:** Based on source reliability, independent confirmations, match strength and contradictions.
- **False Match Handling:** Weak matches remain unmerged, conflicts are flagged, and insufficient evidence is reported instead of guessing.

---

## Privacy & Responsible Design
- Only consented, public or synthetic data is used
- No private accounts, leaked data or credential-based access
- Every output is traceable to a public source
- No sensitive attribute inference

---

## Tech Stack
- **Python**
- **Pretrained face/image embeddings**
- **LLM-based extraction**
- **Fuzzy matching**
- **NetworkX, PyVis** (graph and visualization)
- **Streamlit** (UI)

---

## Setup & Execution

```bash
# Clone repo
git clone <repo-url>
cd digital-identity-intelligence

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env   # add API keys

# Run Streamlit app
streamlit run app.py
```

---

## Team
- Niveditha Katta
- Meghana Kammari
- Kokonda Sravya
