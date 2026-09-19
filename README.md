# Digital Identity Intelligence System

**NEURAX Hackathon 3.0 | Domain 3: AI in Cybersecurity**
**Problem Statement: Public Profile & Digital Footprint Intelligence**

A software-only AI system that takes an organizer-provided, consented image and limited context, then discovers, correlates and verifies publicly available information about the most likely matching person. Every finding is backed by a source and a confidence score.

---

## 1. Problem Understanding

A person's public presence is scattered across many independent platforms: Instagram, X/Twitter, YouTube, LinkedIn, GitHub, personal websites, company pages, event platforms and publications. The same person may use different usernames, photos, aliases or name variants on each. Common names, incomplete profiles and look-alike identities make manual correlation slow and error-prone.

This is **not** a reverse-image search tool or a generic web scraper. The goal is a **digital identity intelligence system** that:

- Identifies the most likely public identity for a consented image
- Discovers public social and professional profiles
- Finds affiliations, roles, events, projects, publications and patents
- Resolves names, aliases and usernames that belong to the same person
- Correlates information across sources
- Builds a timeline and relationship graph of public activity
- Attaches evidence and confidence to every material finding
- Clearly flags uncertain, conflicting or insufficient information

**Constraints we follow:** only organizer-approved, consented, public or synthetic data. No private-account access, leaked data, credential-based methods or access-control bypassing.

**Input assumption:** no training or reference dataset is required. The system runs on a single consented image plus limited context (for example a name hint, event or organization), and gathers everything else from approved public sources at run time, using pretrained models.

---

## 2. Architecture

```
 Consented image + limited context
                |
                v
 +------------------------------+
 | 1. Input validation          |
 +------------------------------+
                |
                v
 +------------------------------+
 | 2. Candidate hypothesis      |
 |    generation                |
 +------------------------------+
                |
                v
 +------------------------------+
 | 3. Cross-platform discovery  |
 +------------------------------+
                |
                v
 +------------------------------+
 | 4. Entity resolution         |
 +------------------------------+
                |
                v
 +------------------------------+
 | 5. Information extraction    |
 +------------------------------+
                |
                v
 +------------------------------+
 | 6. Evidence + confidence     |
 |    scoring                   |
 +------------------------------+
                |
                v
 +------------------------------+
 | 7. Conflict detection        |
 +------------------------------+
                |
                v
 +------------------------------+
 |     Evidence-backed          |
 |     knowledge graph          |
 +------------------------------+
        |              |              |
        v              v              v
   Relationship     Timeline      Evidence
      graph                        report
```

### Stage descriptions

| Stage | Purpose |
|---|---|
| Input validation | Confirms the image and context are organizer-provided and consented |
| Candidate hypothesis generation | Uses the image and context to produce a ranked set of possible identities, each treated as a hypothesis |
| Cross-platform discovery | Searches approved public sources for profiles matching each hypothesis |
| Entity resolution | Merges names, aliases and usernames only when multiple signals agree |
| Information extraction | Structures organizations, roles, events, projects, publications and patents |
| Evidence and confidence scoring | Attaches source, evidence type and confidence to every claim |
| Conflict detection | Flags contradictions between sources instead of silently choosing one |
| Output generation | Builds the graph, timeline and evidence report from one shared knowledge graph |

---

## 3. Approach

### Core idea
We treat identification as a **hypothesis-testing problem**, not a lookup. The system generates candidate identities, gathers evidence for and against each, and ranks them. All findings are stored in one evidence-backed knowledge graph, and both the timeline and the final report are generated from it.

### Working without a dataset
- Pretrained models handle image embeddings and text extraction, so no training data is needed.
- Candidates and their public footprint are gathered live from approved public sources, guided by the image and context.
- Where a source is unavailable or rate-limited, the system records the gap and lowers confidence instead of guessing.

### Candidate hypotheses
Each candidate identity is a hypothesis: "this person is X". Each hypothesis holds its supporting evidence, contradicting evidence and an overall confidence score. Multiple hypotheses stay alive and ranked instead of being collapsed early.

### Entity resolution
Aliases, usernames and name variants are merged into one identity only when several independent signals agree, for example:
- Name similarity and known variants
- Links between profiles (a GitHub page linking to a personal site, and so on)
- Bio and description overlap
- Image similarity
- Shared affiliations, events or projects

Weak matches remain as separate, unmerged nodes.

### Relationship graph
The graph is the central data structure. Each pipeline stage adds to it.

- **Nodes:** Person, Account, Alias/Username, Organization, Role, Event, Project, Publication, Patent, Source
- **Edges:** `has_account`, `also_known_as`, `held_role`, `works_at`, `participated_in`, `authored`, `contributed_to`, `invented`, `supported_by`
- **Edge attributes:** confidence, source URL, retrieval date, status (confirmed, uncertain, conflicting)

The timeline is produced by sorting the dated nodes in the graph, so both outputs come from one consistent source of truth.

### Evidence and confidence scoring
Every material finding is linked to at least one public source. Confidence combines:
- Reliability of the source
- Number of independent corroborating sources
- Strength of the matching signal
- Any contradicting evidence

### Handling ambiguity and false matches
- Multiple hypotheses are ranked, not forced into one answer
- Low-confidence candidates stay unmerged
- Conflicting evidence is displayed next to the finding it affects
- When evidence is insufficient, the system reports "insufficient evidence" instead of guessing

---

## 4. Responsible Design and Privacy

- Uses only organizer-provided, consented, public or synthetic data
- No private-account access, leaked data, credential-based methods or access-control bypassing
- No inference of sensitive personal attributes
- Every output is traceable to a public source
- Input images and results are not stored beyond the session unless needed for evaluation

---

## 5. Tech Stack

| Area | Tools |
|---|---|
| Language | Python 3.10+ |
| Image matching | Pretrained face/image embedding model |
| Text and entity extraction | NLP / LLM-based extraction |
| Entity resolution | Fuzzy string matching plus embedding similarity |
| Public source access | Approved public search and platform APIs |
| Graph | NetworkX |
| Visualization | PyVis |
| Interface | Streamlit |

---

## 6. Setup Instructions

### Prerequisites
- Python 3.10 or higher
- pip
- API keys for any approved search or LLM services you use

### Installation
```bash
git clone <repository-url>
cd digital-identity-intelligence
python -m venv venv
source venv/bin/activate      # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Environment variables
Copy `.env.example` to `.env` and fill in the values. Never commit real keys.

```
SEARCH_API_KEY=<your-key>
LLM_API_KEY=<your-key>
```

### Running the project
```bash
python main.py --image <path-to-consented-image> --context "<limited context>"
```

Or launch the interface:
```bash
streamlit run app.py
```

*(Commands show the planned interface and will be updated as implementation progresses.)*

---

## 7. Planned Extensions (stretch goals)

- Interactive graph exploration
- Automated explanation of why one hypothesis ranked above others
- Additional source connectors, as approved by organizers

---

## 8. Team

| Name | Role |
|---|---|
| <Member 1> | <Role> |
| <Member 2> | <Role> |
| <Member 3> | <Role> |
| <Member 4> | <Role> |

---

## 9. Status

- [x] Problem analysis and architecture design
- [ ] Core pipeline implementation
- [ ] Graph and timeline generation
- [ ] Evaluation and testing

---

## 10. License

This project is licensed under the MIT License. See the LICENSE file for details.
