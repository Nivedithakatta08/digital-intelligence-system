import os
import streamlit as st

from modules.discovery import discover_from_inputs
from modules.resolver import (
    resolve,
    get_best_resolved_identity
)
from modules.scorer import score
from modules.conflict import detect_conflicts
from modules.graph_builder import build_graph
from modules.evidence import create_evidence
from modules.timeline import build_timeline


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Digital Identity Intelligence System",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ============================================================
# SESSION STATE
# ============================================================

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if "graph_path" not in st.session_state:
    st.session_state.graph_path = None

if "graph_error" not in st.session_state:
    st.session_state.graph_error = None


# ============================================================
# HEADER
# ============================================================

st.title("🔍 Digital Identity Intelligence System")

st.caption(
    "Public-source identity discovery, identity resolution, "
    "evidence correlation and knowledge-graph visualization."
)

st.divider()


# ============================================================
# SEARCH PANEL
# ============================================================

st.header("🎯 Identity Search")

st.write(
    "Enter a username to discover publicly available identity "
    "information. Organization can be used as supporting information."
)

col1, col2 = st.columns(2)

with col1:
    username = st.text_input(
        "Username",
        placeholder="Example: tanaypratap"
    )

with col2:
    organization = st.text_input(
        "Organization",
        placeholder="Optional"
    )

uploaded_image = st.file_uploader(
    "Identity image (optional)",
    type=["png", "jpg", "jpeg", "webp"],
    help="Optional image input for identity matching."
)


# ============================================================
# SETTINGS
# ============================================================

with st.expander("⚙️ Demo Settings"):

    use_mock_data = st.checkbox(
        "Use demonstration data",
        value=True
    )

    st.caption(
        "Demo mode allows the prototype to operate without "
        "requiring every external source to be available."
    )


# ============================================================
# ANALYZE
# ============================================================

if st.button(
    "🔎 Analyze Identity",
    type="primary",
    use_container_width=True
):

    if not username.strip() and uploaded_image is None:

        st.error(
            "Enter a username or upload an identity image."
        )

        st.stop()

    # Reset previous results
    st.session_state.analysis = None
    st.session_state.graph_path = None
    st.session_state.graph_error = None

    # --------------------------------------------------------
    # 1. DISCOVERY
    # --------------------------------------------------------

    with st.status(
        "Running identity investigation...",
        expanded=True
    ):

        st.write("🔎 Discovering public-source profiles...")

        try:

            discovery = discover_from_inputs(
                username=username.strip() or None,
                organization=organization.strip() or None,
                image=uploaded_image,
                include_mock=use_mock_data
            )

        except Exception as error:

            st.error(
                f"Discovery failed: {error}"
            )

            st.stop()

        profiles = discovery.get(
            "profiles",
            []
        )

        publications = discovery.get(
            "publications",
            []
        )

        image_candidates = discovery.get(
            "image_candidates",
            []
        )

        st.write(
            f"Found {len(profiles)} profile records."
        )

        # ----------------------------------------------------
        # 2. RESOLUTION
        # ----------------------------------------------------

        st.write("🧩 Resolving identity candidates...")

        try:

            resolved_profiles = resolve(
                profiles,
                username_input=username.strip() or None,
                organization_input=organization.strip() or None,
                image_candidates=image_candidates
            )

        except Exception as error:

            st.error(
                f"Identity resolution failed: {error}"
            )

            st.stop()

        if not resolved_profiles:

            st.warning(
                "No identity candidates were resolved."
            )

            st.stop()

        st.write(
            f"Resolved {len(resolved_profiles)} candidate identities."
        )

        # ----------------------------------------------------
        # 3. BEST IDENTITY
        # ----------------------------------------------------

        candidate = get_best_resolved_identity(
            resolved_profiles
        )

        if not candidate:

            st.error(
                "No primary identity candidate was available."
            )

            st.stop()

        # ----------------------------------------------------
        # 4. EVIDENCE
        # ----------------------------------------------------

        st.write("🧾 Correlating evidence...")

        try:

            evidence = create_evidence(
                candidate
            )

        except Exception:

            evidence = []

        # ----------------------------------------------------
        # 5. CONFLICTS
        # ----------------------------------------------------

        st.write("⚠️ Checking for conflicts...")

        try:

            conflicts = detect_conflicts(
                candidate
            )

        except Exception:

            conflicts = []

        if conflicts is None:
            conflicts = []

        # ----------------------------------------------------
        # 6. SCORING
        # ----------------------------------------------------

        st.write("📊 Calculating identity confidence...")

        try:

            scored_profiles = score(
                resolved_profiles,
                evidence=evidence,
                conflicts=conflicts,
                username_input=username.strip() or None,
                organization_input=organization.strip() or None
            )

        except Exception:

            scored_profiles = resolved_profiles

        if scored_profiles:

            candidate = scored_profiles[0]

        # ----------------------------------------------------
        # 7. TIMELINE
        # ----------------------------------------------------

        st.write("🕒 Building activity timeline...")

        try:

            timeline = build_timeline(
                resolved_profiles,
                publications
            )

        except Exception:

            timeline = []

        # ----------------------------------------------------
        # 8. KNOWLEDGE GRAPH
        # ----------------------------------------------------

        st.write("🕸️ Building knowledge graph...")

        try:

            graph_path = build_graph(
                candidate,
                publications=publications,
                profiles=resolved_profiles,
                discovered_profiles=profiles
            )

            st.session_state.graph_path = graph_path

        except Exception as error:

            st.session_state.graph_path = None
            st.session_state.graph_error = str(error)

        # ----------------------------------------------------
        # SAVE
        # ----------------------------------------------------

        st.session_state.analysis = {
            "candidate": candidate,
            "profiles": resolved_profiles,
            "discovered_profiles": profiles,
            "publications": publications,
            "evidence": evidence,
            "conflicts": conflicts,
            "timeline": timeline,
            "image_candidates": image_candidates
        }

    st.success("Identity analysis completed.")


# ============================================================
# RESULTS
# ============================================================

analysis = st.session_state.analysis

if analysis:

    candidate = analysis["candidate"]
    profiles = analysis["profiles"]
    discovered_profiles = analysis["discovered_profiles"]
    publications = analysis["publications"]
    evidence = analysis["evidence"]
    conflicts = analysis["conflicts"]
    timeline = analysis["timeline"]


    # ========================================================
    # IDENTIFIED PERSON
    # ========================================================

    st.divider()

    st.header("👤 Identified Person")

    name = (
        candidate.get("resolved_name")
        or candidate.get("name")
        or candidate.get("display_name")
        or "Unknown"
    )

    candidate_username = (
        candidate.get("username")
        or candidate.get("login")
        or username
        or "Unknown"
    )

    st.subheader(name)

    st.write(
        f"Username: **@{candidate_username}**"
    )

    st.caption(
        "Identity candidate resolved from available public-source evidence."
    )


    # ========================================================
    # METRICS
    # ========================================================

    confidence = (
        candidate.get("confidence")
        or candidate.get("score")
        or candidate.get("confidence_score")
        or 0
    )

    try:
        confidence = float(confidence)
    except:
        confidence = 0.0

    if confidence <= 1:
        confidence_percentage = confidence * 100
    else:
        confidence_percentage = confidence

    confidence_percentage = max(
        0,
        min(100, confidence_percentage)
    )

    # Count platforms
    platforms = set()

    for profile in discovered_profiles:

        if not isinstance(profile, dict):
            continue

        platform = (
            profile.get("platform")
            or profile.get("platform_name")
            or profile.get("source")
            or profile.get("site")
        )

        if isinstance(platform, list):

            for item in platform:
                platforms.add(str(item))

        elif platform:

            platforms.add(str(platform))

    metric1, metric2, metric3, metric4, metric5 = st.columns(5)

    metric1.metric(
        "Sources",
        len(platforms)
    )

    metric2.metric(
        "Profiles",
        len(profiles)
    )

    metric3.metric(
        "Publications",
        len(publications)
    )

    metric4.metric(
        "Evidence",
        len(evidence)
    )

    metric5.metric(
        "Confidence",
        f"{confidence_percentage:.1f}%"
    )


    # ========================================================
    # SOURCE COVERAGE
    # ========================================================

    st.header("🌐 Source Coverage")

    if platforms:

        st.write(
            "Platforms detected in the discovered records:"
        )

        cols = st.columns(
            min(len(platforms), 4)
        )

        for index, platform in enumerate(sorted(platforms)):

            cols[index % len(cols)].info(
                f"**{platform}**"
            )

    else:

        st.warning(
            "No platform metadata was returned by the discovery module."
        )


    # ========================================================
    # KNOWLEDGE GRAPH
    # ========================================================

    st.header("🕸️ Knowledge Graph")

    st.write(
        "The graph connects the resolved identity to actual "
        "platforms, usernames, profiles and discovered entities."
    )

    graph_path = st.session_state.graph_path

    if graph_path and os.path.isfile(graph_path):

        st.image(
            graph_path,
            caption="Cross-platform identity relationship graph",
            use_container_width=True
        )

        st.success(
            "Knowledge graph generated successfully."
        )

    else:

        st.error(
            "Knowledge graph image was not generated."
        )

        if st.session_state.graph_error:

            st.code(
                st.session_state.graph_error
            )


    # ========================================================
    # GRAPH LEGEND
    # ========================================================

    with st.expander("🎨 Graph Legend", expanded=False):

        st.write("🔵 Person")
        st.write("🔷 Username")
        st.write("🟢 Platform")
        st.write("🟩 Profile")
        st.write("🟠 Organization")
        st.write("🟡 Role")
        st.write("🟣 Project")
        st.write("🌸 Event")
        st.write("🟪 Publication")
        st.write("🟦 Location")
        st.write("⚪ Source")


    # ========================================================
    # IDENTITY TIMELINE
    # ========================================================

    st.header("🕒 Identity Timeline")

    if timeline:

        for event in timeline:

            if isinstance(event, dict):

                event_date = (
                    event.get("date")
                    or event.get("timestamp")
                    or event.get("year")
                    or "Unknown date"
                )

                event_title = (
                    event.get("title")
                    or event.get("event")
                    or event.get("description")
                    or "Activity"
                )

                st.write(
                    f"**{event_date}**  |  {event_title}"
                )

            else:

                st.write(event)

    else:

        st.info(
            "No dated activity was available for this identity."
        )


    # ========================================================
    # CONFIDENCE
    # ========================================================

    st.header("📊 Confidence Assessment")

    st.write(
        "Confidence reflects the strength and agreement "
        "of the available evidence."
    )

    st.progress(
        int(confidence_percentage)
    )

    st.metric(
        "Overall Confidence",
        f"{confidence_percentage:.1f}%"
    )

    if confidence_percentage >= 80:

        st.success(
            "High confidence"
        )

    elif confidence_percentage >= 60:

        st.warning(
            "Moderate confidence"
        )

    else:

        st.warning(
            "Low confidence"
        )


    # ========================================================
    # EVIDENCE COMPONENTS
    # ========================================================

    st.subheader("Evidence Components")

    evidence_fields = {
        "Username Match": candidate.get("username_score"),
        "Image Match": candidate.get("image_score"),
        "Source Agreement": candidate.get("source_agreement"),
        "Record Linkage": candidate.get("record_linkage"),
        "Evidence": candidate.get("evidence_score"),
        "Organization Match": candidate.get("organization_score")
    }

    displayed_evidence = False

    for label, value in evidence_fields.items():

        if value is None:
            continue

        displayed_evidence = True

        try:

            value = float(value)

            if value <= 1:
                value *= 100

            value = max(0, min(100, value))

            st.write(
                f"**{label}:** {value:.1f}%"
            )

            st.progress(
                int(value)
            )

        except:

            st.write(
                f"**{label}:** {value}"
            )

    if not displayed_evidence:

        st.info(
            "Detailed evidence component scores were not returned."
        )


    # ========================================================
    # CONFLICT DETECTION
    # ========================================================

    st.header("⚠️ Conflict Detection")

    if conflicts:

        for conflict in conflicts:

            if isinstance(conflict, dict):

                message = (
                    conflict.get("description")
                    or conflict.get("message")
                    or conflict.get("reason")
                    or str(conflict)
                )

            else:

                message = str(conflict)

            st.warning(
                message
            )

    else:

        st.success(
            "No conflicting information was detected."
        )


    # ========================================================
    # RESOLVED PROFILE
    # ========================================================

    st.header("👤 Resolved Profile")

    profile_col1, profile_col2 = st.columns(2)

    with profile_col1:

        st.write(
            "**Name**"
        )

        st.write(
            candidate.get("name")
            or candidate.get("resolved_name")
            or candidate.get("display_name")
            or "Not available"
        )

        st.write(
            "**Username**"
        )

        st.write(
            candidate.get("username")
            or candidate.get("login")
            or "Not available"
        )

        st.write(
            "**Organization**"
        )

        st.write(
            candidate.get("organization")
            or "Not available"
        )

    with profile_col2:

        st.write(
            "**Location**"
        )

        st.write(
            candidate.get("location")
            or "Not available"
        )

        st.write(
            "**Bio**"
        )

        st.write(
            candidate.get("bio")
            or "Not available"
        )

        st.write(
            "**Sources**"
        )

        source_value = (
            candidate.get("sources")
            or candidate.get("source")
            or candidate.get("platform")
            or "Not available"
        )

        st.write(
            source_value
        )


    # ========================================================
    # OTHER CANDIDATES
    # ========================================================

    if len(profiles) > 1:

        st.header("👥 Other Candidates")

        for index, profile in enumerate(
            profiles[1:],
            start=1
        ):

            if not isinstance(profile, dict):
                continue

            other_name = (
                profile.get("resolved_name")
                or profile.get("name")
                or profile.get("display_name")
                or "Unknown"
            )

            other_username = (
                profile.get("username")
                or profile.get("login")
                or "Unknown"
            )

            other_score = (
                profile.get("confidence")
                or profile.get("score")
                or profile.get("confidence_score")
                or ""
            )

            st.write(
                f"**{index}. {other_name}** "
                f"@{other_username}"
                + (
                    f" • Score: {other_score}"
                    if other_score != ""
                    else ""
                )
            )


    # ========================================================
    # SUPPORTING EVIDENCE
    # ========================================================

    st.header("🧾 Supporting Evidence")

    if evidence:

        for item in evidence:

            if isinstance(item, dict):

                for key, value in item.items():

                    st.write(
                        f"**{key}:** {value}"
                    )

                st.divider()

            else:

                st.write(item)

    else:

        st.info(
            "No supporting evidence records were returned."
        )


    # ========================================================
    # PUBLICATIONS
    # ========================================================

    if publications:

        st.header("📚 Publications")

        for publication in publications:

            if isinstance(publication, dict):

                title = (
                    publication.get("title")
                    or publication.get("name")
                    or "Untitled"
                )

                st.write(
                    f"**{title}**"
                )

                venue = (
                    publication.get("venue")
                    or publication.get("journal")
                    or publication.get("source")
                )

                if venue:
                    st.caption(
                        str(venue)
                    )

            else:

                st.write(
                    publication
                )


    # ========================================================
    # DEMO NOTICE
    # ========================================================

    if use_mock_data:

        st.info(
            "Demo mode is enabled. Some results may come from "
            "demonstration/mock data rather than live external sources."
        )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "Digital Identity Intelligence System • "
    "Public-source discovery • Identity resolution • "
    "Evidence correlation • Knowledge graph"
)