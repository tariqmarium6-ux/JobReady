import streamlit as st
import asyncio
import json
import os
import hashlib
from datetime import datetime

try:
    from agents_config import study_assistant_agent
except Exception as _agent_import_err:
    import logging
    logging.warning(f"[JobReady] agents_config import failed: {_agent_import_err}. AI Study Assistant will be disabled.")
    # Create a minimal stub so the rest of the app loads normally
    class _StubAgent:
        name = "study_assistant_agent"
    study_assistant_agent = _StubAgent()
from sqlite_provider import SQLiteProvider
from firestore_provider import FirestoreProvider
from oauth_handler import is_oauth_configured, get_google_auth_url, handle_oauth_callback
from quiz_generator import generate_weekly_quiz, get_weekly_quiz_sync
from badges import evaluate_badges, BADGE_DESCRIPTIONS, COMPLETION_BADGES

try:
    from src.resource_validator import verify_and_get_resource
    from src.check_resources import get_health_stats
except ModuleNotFoundError:
    from resource_validator import verify_and_get_resource
    from check_resources import get_health_stats

# Choose database provider
if os.getenv("PRODUCTION_MODE", "false").lower() == "true":
    db_provider = FirestoreProvider()
else:
    db_provider = SQLiteProvider()

# Pre-seed demo user account if it does not exist
demo_email = "demo@jobready.org"
existing_demo = db_provider.get_user_by_email(demo_email)
if not existing_demo:
    demo_hash = hashlib.sha256("password123".encode("utf-8")).hexdigest()
    db_provider.create_email_user(
        email=demo_email,
        password_hash=demo_hash,
        name="Demo User",
        picture_url="https://api.dicebear.com/7.x/adventurer/svg?seed=DemoUser"
    )

# Helper to load database JSON files
def load_db_file(filename):
    path = os.path.join("database", filename)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

DOMAINS = load_db_file("domains.json")
ROLES = load_db_file("roles.json")
SKILL_BLOCKS = load_db_file("skill_blocks.json")
CURRICULUM = load_db_file("curriculum.json")
RESOURCES = load_db_file("resources.json")
SKILLS = load_db_file("skills_network.json")

# Initialize session state variables
if "current_screen" not in st.session_state:
    st.session_state.current_screen = 1
if "selected_domain" not in st.session_state:
    st.session_state.selected_domain = None
if "selected_role" not in st.session_state:
    st.session_state.selected_role = None
if "completed_weeks" not in st.session_state:
    st.session_state.completed_weeks = set()
if "completed_projects" not in st.session_state:
    st.session_state.completed_projects = set()
if "completed_materials" not in st.session_state:
    st.session_state.completed_materials = set()
if "bookmarks" not in st.session_state:
    st.session_state.bookmarks = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "main_nav_choice" not in st.session_state:
    st.session_state.main_nav_choice = "Learning Paths"
if "selected_explorer_skill" not in st.session_state:
    st.session_state.selected_explorer_skill = "Python"
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "study_hours" not in st.session_state:
    st.session_state.study_hours = 0.0
if "search_query_input" not in st.session_state:
    st.session_state.search_query_input = ""
if "study_history" not in st.session_state:
    st.session_state.study_history = [0.0] * 7
if "completed_weeks_notified" not in st.session_state:
    st.session_state.completed_weeks_notified = set()

# Set page config
st.set_page_config(
    page_title="JobReady - Become Job-Ready",
    page_icon="🚀",
    layout="wide"
)

# ---------------------------------------------------------
# Google OAuth Redirection Check & Persistence Sync
# ---------------------------------------------------------
oauth_user = handle_oauth_callback(db_provider)
if oauth_user:
    st.session_state.current_user = oauth_user

# Sync Session State values from DB if user is logged in
user = st.session_state.current_user
if user:
    google_id = user["google_id"]
    active_role = st.session_state.selected_role or ""
    
    # Load profile data
    profile = db_provider.get_user_profile(google_id)
    if profile:
        st.session_state.current_user = profile
        
    # Load course progress metrics
    if active_role:
        progress = db_provider.get_progress(google_id, active_role)
        st.session_state.completed_weeks = set(progress.get("completed_weeks", []))
        st.session_state.completed_projects = set(progress.get("completed_projects", []))
        st.session_state.completed_materials = set(progress.get("completed_materials", []))
        st.session_state.bookmarks = progress.get("bookmarks", {})
        st.session_state.study_hours = float(progress.get("study_hours", 0.0))

def trigger_progress_save():
    """Commit active learning state back to SQLite or Firestore database."""
    if st.session_state.current_user and st.session_state.selected_role:
        uid = st.session_state.current_user["google_id"]
        role = st.session_state.selected_role
        db_provider.save_progress(uid, role, {
            "completed_weeks": list(st.session_state.completed_weeks),
            "completed_projects": list(st.session_state.completed_projects),
            "completed_materials": list(st.session_state.completed_materials),
            "bookmarks": st.session_state.bookmarks,
            "study_hours": st.session_state.study_hours
        })

# Custom dynamic theme accents helper
def get_domain_accent(d_name):
    d_lower = d_name.lower()
    if any(kw in d_lower for kw in ["artificial intelligence", "machine learning", "large language", "deep learning", "nlp"]):
        return "#6C63FF" # Purple
    elif any(kw in d_lower for kw in ["data", "analytics", "business intelligence", "bi"]):
        return "#06B6D4" # Cyan
    elif any(kw in d_lower for kw in ["software", "backend", "fullstack", "full-stack", "system design"]):
        return "#F59E0B" # Amber
    elif any(kw in d_lower for kw in ["web", "frontend", "mobile", "android", "ios", "react"]):
        return "#10B981" # Green
    elif any(kw in d_lower for kw in ["security", "devsecops", "cloud", "devops", "aws", "gcp"]):
        return "#8B5CF6" # Violet
    else:
        return "#F43F5E" # Rose

def get_domain_accent_by_index(index):
    colors = [
        "#6C63FF",  # Purple
        "#06B6D4",  # Cyan
        "#F59E0B",  # Amber
        "#10B981",  # Green
        "#8B5CF6",  # Violet
        "#F43F5E"   # Rose
    ]
    return colors[index % len(colors)]

# Kaggle-style metallic badges helper
def get_badge_styling(b_name):
    b_lower = b_name.lower()
    if "quick" in b_lower or "novice" in b_lower or "bronze" in b_lower:
        bg = "linear-gradient(135deg, #A87C53 0%, #CD7F32 100%)"
        glow = "rgba(205, 127, 50, 0.4)"
    elif "builder" in b_lower or "intermediate" in b_lower or "silver" in b_lower:
        bg = "linear-gradient(135deg, #E0E0E0 0%, #B0B0B0 100%)"
        glow = "rgba(176, 176, 176, 0.4)"
    elif "architect" in b_lower or "expert" in b_lower or "gold" in b_lower:
        bg = "linear-gradient(135deg, #FFF099 0%, #D4AF37 100%)"
        glow = "rgba(212, 175, 55, 0.4)"
    elif "cloud" in b_lower or "practitioner" in b_lower or "platinum" in b_lower:
        bg = "linear-gradient(135deg, #FFFFFF 0%, #9E9E9E 100%)"
        glow = "rgba(158, 158, 158, 0.4)"
    else:
        bg = "linear-gradient(135deg, #E0F7FA 0%, #00B0FF 100%)"
        glow = "rgba(0, 176, 255, 0.4)"
    return bg, glow

# Injected CSS for Premium Dark Theme (Linear.app / Coursera Inspired)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Inter:wght@400;500;600;700&display=swap');
    
    /* Remove Streamlit default header and footers */
    header {visibility: hidden !important;}
    [data-testid="stHeader"] {background-color: rgba(0,0,0,0) !important; height: 0px !important;}
    footer {visibility: hidden !important;}
    
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 0rem !important;
        padding-left: 3rem !important;
        padding-right: 2rem !important;
        max-width: 100% !important;
    }
    
    /* Core Dark theme setup */
    .stApp {
        background-color: #0D0F1A !important;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar styling overrides — Coursera-style wide nav */
    [data-testid="stSidebar"] {
        min-width: 220px !important;
        max-width: 220px !important;
        background-color: #0A0C17 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
        padding-top: 0 !important;
    }
    [data-testid="stSidebarCollapseButton"] {
        display: none !important;
    }
    /* Override default Streamlit sidebar button look */
    [data-testid="stSidebar"] button {
        background-color: transparent !important;
        color: rgba(255, 255, 255, 0.65) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        text-transform: none !important;
        letter-spacing: 0 !important;
        transition: background 0.18s ease, color 0.18s ease !important;
        width: 100% !important;
        margin-bottom: 2px !important;
        display: flex !important;
        flex-direction: row !important;
        align-items: center !important;
        justify-content: flex-start !important;
        text-align: left !important;
    }
    [data-testid="stSidebar"] button:hover {
        background-color: rgba(108, 99, 255, 0.1) !important;
        color: #C4B5FD !important;
        border: none !important;
    }
    /* Sidebar nav item active state */
    .sidebar-nav-active button {
        background-color: rgba(108, 99, 255, 0.18) !important;
        color: #A78BFA !important;
    }
    
    /* Content Margin Wrapper */
    .content-wrapper {
        padding: 40px 60px 40px 110px !important;
        max-width: 1200px;
        margin: 0;
    }
    
    /* Visible border and glow for Search input */
    div[data-testid="stTextInput"] div[data-baseweb="input"] {
        border: 1px solid rgba(108, 99, 255, 0.45) !important;
        background-color: rgba(21, 24, 39, 0.8) !important;
        border-radius: 10px !important;
        box-shadow: 0 4px 12px rgba(108, 99, 255, 0.1) !important;
        transition: all 0.2s ease-in-out !important;
    }
    div[data-testid="stTextInput"] div[data-baseweb="input"]:focus-within {
        border-color: #A78BFA !important;
        box-shadow: 0 4px 20px rgba(108, 99, 255, 0.25) !important;
    }
    
    /* Typography hierarchy */
    h1, h2, h3, h4 {
        color: #FFFFFF !important;
        font-family: 'Outfit', sans-serif;
        font-weight: 600;
        letter-spacing: -0.02em;
    }
    
    body, p, span, li, label, div {
        font-family: 'Inter', sans-serif;
        font-weight: 400;
        line-height: 1.6;
        color: rgba(255, 255, 255, 0.75);
    }
    
    /* Section Eyebrow metadata */
    .eyebrow {
        text-transform: uppercase !important;
        letter-spacing: 0.08em !important;
        font-size: 12px !important;
        color: #6C63FF !important;
        font-weight: 600 !important;
        display: block;
        margin-bottom: 8px;
    }
    
    /* Visual Hierarchy: Primary Cards (#151827) */
    .premium-card, .premium-card div, .premium-card p, .premium-card span {
        background-color: transparent !important;
    }
    .premium-card {
        background-color: #151827 !important;
        border: 1px solid #252837 !important;
        border-radius: 14px !important;
        padding: 20px !important;
        margin-bottom: 24px !important;
        transition: transform 0.25s cubic-bezier(0.16, 1, 0.3, 1), border-color 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }
    
    /* All stButton containers must be transparent — no white backgrounds */
    div.stButton {
        background: transparent !important;
        background-color: transparent !important;
    }
    /* Domain explore buttons — small, dark, pill-shaped */
    .domain-explore-btn > div.stButton > button {
        background: transparent !important;
        border: 1px solid rgba(255,255,255,0.12) !important;
        color: rgba(255,255,255,0.5) !important;
        border-radius: 8px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        padding: 6px 16px !important;
        margin-top: 2px !important;
        width: 100% !important;
        min-width: 0 !important;
        box-shadow: none !important;
        transition: background 0.2s, color 0.2s !important;
    }
    .domain-explore-btn > div.stButton > button:hover {
        background: rgba(108,99,255,0.15) !important;
        border-color: rgba(108,99,255,0.5) !important;
        color: #A78BFA !important;
    }
    
    /* Muted text sizes */
    .muted-desc {
        color: rgba(255, 255, 255, 0.45) !important;
        font-size: 13px !important;
        line-height: 1.6;
    }
    .hint-desc {
        color: rgba(255, 255, 255, 0.3) !important;
        font-size: 11px !important;
    }

    /* Interactive Sections: Inputs & Text Inputs (#20233A) */
    div[data-testid="stTextInput"] input {
        background-color: #20233A !important;
        border: 1px solid #353852 !important;
        color: #FFFFFF !important;
        border-radius: 10px !important;
        padding: 10px 14px !important;
    }
    div[data-testid="stTextInput"] input::placeholder {
        color: rgba(255, 255, 255, 0.45) !important;
    }
    
    /* Pill shaped filter chips style */
    .filter-chips-container div.stButton > button {
        background-color: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        color: rgba(255, 255, 255, 0.7) !important;
        border-radius: 24px !important;
        font-size: 13px !important;
        padding: 6px 18px !important;
        box-shadow: none !important;
        width: auto !important;
        min-width: 0 !important;
        display: inline-block !important;
        margin-right: 8px !important;
        margin-bottom: 8px !important;
    }
    .filter-chips-container div.stButton > button:hover {
        background-color: rgba(108, 99, 255, 0.2) !important;
        border-color: #6C63FF !important;
        color: #A78BFA !important;
    }
    div[data-testid="column"] div.stButton > button:hover {
        background-color: rgba(108, 99, 255, 0.2) !important;
        border-color: #6C63FF !important;
        color: #A78BFA !important;
    }
    
    /* Visual Hierarchy: Secondary Cards (#1A1D2E) */
    .resource-card {
        background-color: #1A1D2E !important;
        border: 1px solid #2B2E42 !important;
        border-radius: 12px;
        padding: 16px 20px;
        margin-right: 12px;
        margin-bottom: 12px;
        display: inline-block;
        min-width: 250px;
        vertical-align: top;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    .resource-card:hover {
        border-color: rgba(108, 99, 255, 0.3) !important;
    }
    .resource-provider {
        font-weight: 600;
        font-size: 12px;
        color: #FFFFFF;
        display: block;
    }
    
    /* Primary buttons styled as elegant Action buttons */
    /* ── BUTTON STYLING ── */
    /* Primary Buttons */
    div.stButton > button[kind="primary"], 
    div.stButton > button[kind="primary"]:hover, 
    div.stButton > button[kind="primary"]:focus, 
    div.stButton > button[kind="primary"]:active {
        background: linear-gradient(90deg, #6C63FF, #8B5CF6) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        width: 100% !important;
        box-shadow: none !important;
    }
    div.stButton > button[kind="primary"] p, 
    div.stButton > button[kind="primary"]:hover p, 
    div.stButton > button[kind="primary"] span, 
    div.stButton > button[kind="primary"]:hover span {
        color: #FFFFFF !important;
    }
    
    /* Secondary Buttons */
    div.stButton > button[kind="secondary"], 
    div.stButton > button[kind="secondary"]:hover, 
    div.stButton > button[kind="secondary"]:focus, 
    div.stButton > button[kind="secondary"]:active {
        background: transparent !important;
        color: #A78BFA !important;
        border: 1px solid rgba(108,99,255,0.4) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        width: 100% !important;
        box-shadow: none !important;
    }
    div.stButton > button[kind="secondary"] p, 
    div.stButton > button[kind="secondary"]:hover p, 
    div.stButton > button[kind="secondary"] span, 
    div.stButton > button[kind="secondary"]:hover span {
        color: #A78BFA !important;
    }
    
    /* Popover Button overrides to prevent white/blank box on hover */
    div[data-testid="stPopover"] button,
    div[data-testid="stPopover"] button:hover,
    div[data-testid="stPopover"] button:focus,
    div[data-testid="stPopover"] button:active {
        background: #151827 !important;
        color: #A78BFA !important;
        border: 1px solid rgba(108,99,255,0.4) !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
        width: 100% !important;
        box-shadow: none !important;
    }
    div[data-testid="stPopover"] button p,
    div[data-testid="stPopover"] button:hover p,
    div[data-testid="stPopover"] button span,
    div[data-testid="stPopover"] button:hover span {
        color: #A78BFA !important;
    }
    
    /* Navigation tabs styling */
    div.stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: transparent !important;
        border-bottom: 1px solid rgba(255,255,255,0.08) !important;
        overflow-x: auto;
        flex-wrap: nowrap;
    }
    div.stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 12px;
        color: rgba(255, 255, 255, 0.5) !important;
        background: transparent !important;
        border-bottom: 2px solid transparent;
        padding: 8px 14px !important;
        white-space: nowrap;
    }
    div.stTabs [aria-selected="true"] {
        color: #A78BFA !important;
        border-bottom-color: #6C63FF !important;
        background: transparent !important;
    }
    /* Kill white background on tab content panel */
    div.stTabs [data-baseweb="tab-panel"] {
        background: transparent !important;
        background-color: transparent !important;
        padding-top: 20px !important;
    }
    div.stTabs [data-baseweb="tab-panel"] > div {
        background: transparent !important;
    }


    /* Secondary Card: Capstone Project Card (#1A1D2E) */
    .capstone-card {
        background-color: #1A1D2E !important;
        border: 1px solid #2B2E42 !important;
        border-radius: 16px;
        padding: 32px;
        margin-top: 24px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    /* Kaggle-style Circular Badges */
    .badge-medal {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0 auto 10px auto;
        font-size: 2.2rem;
    }
    .badge-locked {
        filter: grayscale(1);
        opacity: 0.25;
        background: rgba(255, 255, 255, 0.1) !important;
        box-shadow: none;
    }
    
    /* Responsive Brand Logo styling */
    .brand-logo-container {
        display: flex;
        align-items: center;
        transition: all 0.2s ease;
    }
    .brand-logo-box {
        width: 42px !important;
        height: 42px !important;
        border-radius: 10px !important;
        background: #20233A !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin-right: 12px !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        flex-shrink: 0 !important;
    }
    .brand-logo-text {
        font-size: 22px !important;
        font-weight: 700 !important;
        color: #FFFFFF !important;
        font-family: "Outfit", sans-serif !important;
        white-space: nowrap !important;
    }
    
    @media (max-width: 1024px) {
        .brand-logo-text {
            font-size: 20px !important;
        }
        .brand-logo-box {
            width: 38px !important;
            height: 38px !important;
        }
    }
    @media (max-width: 768px) {
        .brand-logo-text {
            font-size: 18px !important;
        }
        .brand-logo-box {
            width: 34px !important;
            height: 34px !important;
        }
    }
    
    /* ── KILL ALL WHITE BOXES ─────────────────────────── */
    /* Streamlit stVerticalBlock and block-container inside cards */
    [data-testid="stVerticalBlock"] > div > [data-testid="stMarkdownContainer"] {
        background: transparent !important;
    }
    /* Expander (accordion week rows) */
    [data-testid="stExpander"] {
        background-color: #151827 !important;
        border: 1px solid #252837 !important;
        border-radius: 12px !important;
        margin-bottom: 8px !important;
        overflow: hidden !important;
    }
    [data-testid="stExpander"]:has([aria-expanded="true"]) {
        border-color: rgba(108,99,255,0.5) !important;
        background-color: #1A1D2E !important;
    }
    [data-testid="stExpander"] summary {
        color: #FFFFFF !important;
        font-size: 14px !important;
        padding: 14px 16px !important;
        background-color: transparent !important;
        background: transparent !important;
    }
    [data-testid="stExpander"] summary:hover {
        background-color: transparent !important;
        background: transparent !important;
        color: #A78BFA !important;
    }
    [data-testid="stExpander"] summary:focus,
    [data-testid="stExpander"] summary:active {
        background-color: transparent !important;
        background: transparent !important;
        color: #FFFFFF !important;
    }
    [data-testid="stExpander"] summary::-webkit-details-marker {
        color: #FFFFFF !important;
    }
    [data-testid="stExpander"] summary:hover span,
    [data-testid="stExpander"] summary:hover p,
    [data-testid="stExpander"] summary:hover div {
        color: #A78BFA !important;
    }
    
    /* Popover (Weekly Quiz box) & Radio text visibility */
    [data-testid="stPopoverBody"],
    div[data-baseweb="popover"] > div,
    [data-testid="stDialog"] > div {
        background-color: #151827 !important;
        border: 1px solid #252837 !important;
        border-radius: 12px !important;
        color: #FFFFFF !important;
    }
    [data-testid="stPopoverBody"] *,
    [data-testid="stRadio"] label,
    [data-testid="stRadio"] label p,
    [data-testid="stRadio"] label span,
    [data-testid="stRadio"] div,
    div[role="radiogroup"] * {
        color: #FFFFFF !important;
    }
    div[data-testid="stRadio"] label:hover p,
    div[data-testid="stRadio"] label:hover span {
        color: #A78BFA !important;
    }
    /* Expander content area — transparent so inner divs show */
    [data-testid="stExpander"] > div > div:last-child {
        background: transparent !important;
        padding: 0 16px 16px 16px !important;
    }
    
    /* Chat Bubble Typography Fix */
    .chat-bubble p, .chat-bubble li, .chat-bubble div, .chat-bubble strong {
        font-size: 13px !important;
        line-height: 1.6 !important;
    }
    .chat-bubble ol, .chat-bubble ul {
        margin-top: 4px !important;
        margin-bottom: 8px !important;
        padding-left: 20px !important;
    }

    /* Any iframe or widget background */
    .stMarkdownContainer, [data-testid="stMarkdownContainer"] {
        background: transparent !important;
    }
    /* Kill white backgrounds on stVerticalBlock wrappers (Streamlit component containers) */
    [data-testid="stVerticalBlock"] {
        background: transparent !important;
    }
    /* Main block elements */
    section.main > div, .main .block-container > div {
        background: transparent !important;
    }
    /* Override any white-background widget frame */
    iframe {
        background: transparent !important;
    }
    /* Progress bars by type */
    [data-testid="stProgress"] > div > div {
        background-color: rgba(255,255,255,0.08) !important;
    }
    /* Sidebar inputs - comprehensive override */
    [data-testid="stSidebar"] [data-baseweb="input"] > div,
    [data-testid="stSidebar"] [data-baseweb="base-input"],
    [data-testid="stSidebar"] [data-baseweb="input"],
    [data-testid="stSidebar"] input[type="text"],
    [data-testid="stSidebar"] input[type="password"],
    [data-testid="stSidebar"] input[type="email"] {
        background-color: rgba(255, 255, 255, 0.05) !important;
        color: #FFFFFF !important;
        border-color: rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Option 1: Floating Chat Widget CSS */
    .floating-chat-button-wrapper {
        position: fixed !important;
        bottom: 24px !important;
        right: 24px !important;
        z-index: 99999 !important;
    }
    .floating-chat-button-wrapper div.stButton > button {
        width: 56px !important;
        height: 56px !important;
        border-radius: 50% !important;
        background: linear-gradient(135deg, #6C63FF 0%, #8B5CF6 100%) !important;
        color: #FFFFFF !important;
        font-size: 24px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        border: none !important;
        box-shadow: 0 4px 16px rgba(108,99,255,0.4) !important;
        cursor: pointer !important;
        padding: 0 !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease !important;
    }
    .floating-chat-button-wrapper div.stButton > button:hover {
        transform: scale(1.05) !important;
        box-shadow: 0 6px 20px rgba(108,99,255,0.6) !important;
        background: linear-gradient(135deg, #6C63FF 0%, #8B5CF6 100%) !important;
    }
    .floating-chat-button-wrapper div.stButton > button p,
    .floating-chat-button-wrapper div.stButton > button span {
        color: #FFFFFF !important;
        font-size: 24px !important;
        margin: 0 !important;
        line-height: 56px !important;
    }

    .floating-chat-window-wrapper {
        position: fixed !important;
        bottom: 92px !important;
        right: 24px !important;
        width: 380px !important;
        height: 480px !important;
        background-color: #151827 !important;
        border: 1px solid #252837 !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.5) !important;
        z-index: 99998 !important;
        display: flex !important;
        flex-direction: column !important;
        padding: 20px !important;
        overflow: hidden !important;
    }
    .floating-chat-history {
        flex: 1 !important;
        overflow-y: auto !important;
        margin-bottom: 12px !important;
        padding-right: 4px !important;
        display: flex !important;
        flex-direction: column !important;
        gap: 8px !important;
    }
    
    /* Style all Streamlit selectbox / dropdowns to match the dark theme */
    div[data-baseweb="select"] > div {
        background-color: #151827 !important;
        background: #151827 !important;
        border: 1px solid #252837 !important;
        color: #FFFFFF !important;
        border-radius: 8px !important;
    }
    div[data-baseweb="select"] * {
        color: #FFFFFF !important;
    }
    div[data-baseweb="menu"] {
        background-color: #151827 !important;
        background: #151827 !important;
        border: 1px solid #252837 !important;
        color: #FFFFFF !important;
    }
    div[data-baseweb="menu"] li {
        background-color: #151827 !important;
        background: #151827 !important;
        color: #FFFFFF !important;
    }
    div[data-baseweb="menu"] li:hover {
        background-color: #7c3aed !important;
        background: #7c3aed !important;
        color: #FFFFFF !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# Sidebar Navigation & Authentication (Redesigned)
# ---------------------------------------------------------

# Define the Auth Modal Dialog
@st.dialog("🔑 Sign In to JobReady")
def show_auth_dialog():
    auth_tab1, auth_tab2 = st.tabs(["🔑 Sign In", "📝 Register"])
    with auth_tab1:
        login_email = st.text_input("Email", key="dialog_login_email")
        login_password = st.text_input("Password", type="password", key="dialog_login_password")
        if st.button("Log In", key="dialog_login_btn", type="primary", use_container_width=True):
            user_record = db_provider.get_user_by_email(login_email)
            if user_record and user_record.get("password_hash") == hashlib.sha256(login_password.encode("utf-8")).hexdigest():
                st.session_state.current_user = user_record
                st.success("Successfully logged in!")
                st.rerun()
            else:
                st.error("Invalid credentials.")
    with auth_tab2:
        reg_name = st.text_input("Full Name", key="dialog_reg_name")
        reg_email = st.text_input("Email", key="dialog_reg_email")
        reg_password = st.text_input("Password", type="password", key="dialog_reg_password")
        if st.button("Create Account", key="dialog_reg_btn", type="primary", use_container_width=True):
            new_hash = hashlib.sha256(reg_password.encode("utf-8")).hexdigest()
            pic = f"https://api.dicebear.com/7.x/adventurer/svg?seed={reg_name.replace(' ', '')}"
            db_provider.create_email_user(reg_email, new_hash, reg_name, pic)
            st.session_state.current_user = db_provider.get_user_by_email(reg_email)
            st.success("Account registered!")
            st.rerun()

# Define the Settings Modal Dialog
@st.dialog("⚙️ Account Settings")
def show_settings_dialog():
    u = st.session_state.current_user
    st.write(f"Logged in as **{u.get('name')}** ({u.get('email')})")
    st.write(f"🔥 **{u.get('streak_count', 0)} day streak**")
    pace_val = st.slider("Study Intensity (hours/week):", min_value=5, max_value=45, value=int(u.get("study_pace", 15)), step=5, key="dialog_pace_slider")
    if st.button("Save Settings", key="dialog_save_settings_btn", type="primary", use_container_width=True):
        u["study_pace"] = pace_val
        db_provider.save_user_profile(u)
        st.success("Settings saved!")
        st.rerun()
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Sign Out", key="dialog_logout_btn", type="secondary", use_container_width=True):
        st.session_state.current_user = None
        st.session_state.completed_weeks = set()
        st.session_state.completed_projects = set()
        st.session_state.completed_materials = set()
        st.session_state.bookmarks = {}
        st.session_state.study_hours = 0.0
        st.rerun()

# ── Coursera-style Sidebar Navigation ──────────────────────────

# Brand logo at top of sidebar
st.sidebar.markdown("""
<div style='
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 22px 16px 18px 16px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 8px;
'>
    <div style='
        width: 34px; height: 34px; border-radius: 8px;
        background: linear-gradient(135deg, #6C63FF 0%, #A78BFA 100%);
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0;
    '>
        <svg width="18" height="18" viewBox="0 0 32 32" fill="none">
            <path d="M16 4C16 4 11 9 11 16C11 19.3 12.5 21.5 14 23H18C19.5 21.5 21 19.3 21 16C21 9 16 4 16 4Z" fill="white"/>
            <ellipse cx="16" cy="13" rx="3" ry="3" fill="#C4B5FD"/>
        </svg>
    </div>
    <span style='
        font-family: Outfit, sans-serif;
        font-size: 17px;
        font-weight: 700;
        color: #FFFFFF;
        letter-spacing: -0.02em;
    '>Job<span style="color:#A78BFA;">Ready</span></span>
</div>
""", unsafe_allow_html=True)

# Section label
st.sidebar.markdown("""
<div style='padding: 6px 16px 4px 16px; font-size: 10px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em; color: rgba(255,255,255,0.3);'>
    Main Menu
</div>
""", unsafe_allow_html=True)

# Navigation items
_nav_choice = st.session_state.main_nav_choice

_paths_active = "sidebar-nav-active" if _nav_choice == "Learning Paths" else ""
st.sidebar.markdown(f"<div class='{_paths_active}'>", unsafe_allow_html=True)
if st.sidebar.button("🎯  Learning Paths", key="sidebar_nav_paths", use_container_width=True):
    st.session_state.main_nav_choice = "Learning Paths"
    st.rerun()
st.sidebar.markdown("</div>", unsafe_allow_html=True)



if st.session_state.current_user:
    _badges_active = "sidebar-nav-active" if _nav_choice == "👤 Profile & Badges Showcase" else ""
    st.sidebar.markdown(f"<div class='{_badges_active}'>", unsafe_allow_html=True)
    if st.sidebar.button("🏅  Badges & Profile", key="sidebar_nav_badges", use_container_width=True):
        st.session_state.main_nav_choice = "👤 Profile & Badges Showcase"
        st.rerun()
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

# Spacer pushes user section to bottom
st.sidebar.markdown("""
<div style='flex: 1; min-height: 40px;'></div>
<div style='border-top: 1px solid rgba(255,255,255,0.06); margin: 8px 0;'></div>
""", unsafe_allow_html=True)

# User section at bottom
if st.session_state.current_user:
    u = st.session_state.current_user
    name_parts = u.get('name', 'User').split()
    initials = (name_parts[0][0] + (name_parts[-1][0] if len(name_parts) > 1 else '')).upper()
    user_name = u.get('name', 'Learner')
    user_email = u.get('email', '')
    st.sidebar.markdown(f"""
    <div style='
        display: flex; align-items: center; gap: 10px;
        padding: 12px 16px 6px 16px;
    '>
        <div style='
            width: 36px; height: 36px; border-radius: 50%;
            background: linear-gradient(135deg, #6C63FF 0%, #A78BFA 100%);
            display: flex; align-items: center; justify-content: center;
            font-weight: 700; font-size: 13px; color: white; flex-shrink: 0;
        '>{initials}</div>
        <div style='overflow: hidden;'>
            <div style='color: #FFFFFF; font-size: 13px; font-weight: 600;
                white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>{user_name}</div>
            <div style='color: rgba(255,255,255,0.4); font-size: 11px;
                white-space: nowrap; overflow: hidden; text-overflow: ellipsis;'>Learner</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if st.sidebar.button("⚙️  Settings & Sign Out", key="sidebar_settings_trigger", use_container_width=True):
        show_settings_dialog()

# ---------------------------------------------------------
# Dynamic Top Navigation Bar spanning full width
# ---------------------------------------------------------
step = st.session_state.current_screen


step = st.session_state.current_screen
step_num = 1 if step == 1 else (2 if step == 2 else 3)

nav_col_logo, nav_col_progress, nav_col_auth = st.columns([3, 5, 2])

with nav_col_logo:
    st.markdown("""
    <div class='brand-logo-container' style='padding: 15px 0 15px 16px;'>
        <div class='brand-logo-box' style='width:46px !important; height:46px !important; border-radius:12px !important;'>
            <svg width="26" height="26" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <ellipse cx="16" cy="22" rx="5" ry="3" fill="#6C63FF" opacity="0.5"/>
                <ellipse cx="16" cy="22" rx="3" ry="1.5" fill="#A78BFA" opacity="0.7"/>
                <path d="M16 4C16 4 11 9 11 16C11 19.3 12.5 21.5 14 23H18C19.5 21.5 21 19.3 21 16C21 9 16 4 16 4Z" fill="white"/>
                <ellipse cx="16" cy="13" rx="3" ry="3" fill="#60A5FA"/>
                <ellipse cx="16" cy="13" rx="1.8" ry="1.8" fill="#DBEAFE"/>
                <path d="M12 20L10 23L13 22L12 20Z" fill="#A78BFA"/>
                <path d="M20 20L22 23L19 22L20 20Z" fill="#A78BFA"/>
                <circle cx="10" cy="9" r="1" fill="white" opacity="0.6"/>
                <circle cx="22" cy="7" r="0.7" fill="white" opacity="0.5"/>
                <circle cx="20" cy="11" r="0.5" fill="white" opacity="0.4"/>
            </svg>
        </div>
        <span class='brand-logo-text' style='font-size:26px !important;'>Job<span style='color: #A78BFA;'>Ready</span></span>
    </div>
    """, unsafe_allow_html=True)
    
if step == 4:
    with nav_col_progress:
        st.markdown(f"""
        <div style='display: flex; align-items: center; gap: 12px; padding: 20px 0;'>
            <span style='color:rgba(255,255,255,0.4); font-size:16px;'>🏠</span>
            <span style='color:rgba(255,255,255,0.4); font-size:12px;'>&gt;</span>
            <span style='color:rgba(255,255,255,0.6); font-size:14px; font-weight:500;'>Learning Paths</span>
            <span style='color:rgba(255,255,255,0.4); font-size:12px;'>&gt;</span>
            <span style='color:#FFFFFF; font-size:14px; font-weight:600;'>{st.session_state.selected_role}</span>
        </div>
        """, unsafe_allow_html=True)
    with nav_col_auth:
        u = st.session_state.current_user or {}
        name = u.get('name', 'Learner')
        initials = (name.split()[0][0] + (name.split()[-1][0] if len(name.split()) > 1 else '')).upper()
        st.markdown(f"""
        <div style='padding: 10px 40px 10px 0; display: flex; justify-content: flex-end; align-items: center; gap: 12px;'>
            <div style='text-align: right;'>
                <div style='color: #FFFFFF; font-size: 14px; font-weight: 600; line-height: 1.2;'>{name}</div>
                <div style='color: rgba(255,255,255,0.5); font-size: 12px;'>Learner</div>
            </div>
            <div style='width: 38px; height: 38px; border-radius: 50%; background: linear-gradient(135deg, #6C63FF 0%, #A78BFA 100%); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 14px; color: white;'>{initials}</div>
        </div>
        """, unsafe_allow_html=True)
else:
    step1_circle = "background: #6C63FF; color: white;" if step_num == 1 else "background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.6);"
    step2_circle = "background: #6C63FF; color: white;" if step_num == 2 else "background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.6);"
    step3_circle = "background: #6C63FF; color: white;" if step_num == 3 else "background: rgba(255,255,255,0.1); color: rgba(255,255,255,0.6);"

    step1_text = "color: #A78BFA; font-weight: 600;" if step_num == 1 else "color: rgba(255,255,255,0.6);"
    step2_text = "color: #A78BFA; font-weight: 600;" if step_num == 2 else "color: rgba(255,255,255,0.6);"
    step3_text = "color: #A78BFA; font-weight: 600;" if step_num == 3 else "color: rgba(255,255,255,0.6);"

    with nav_col_progress:
        st.markdown(f"""
        <div style='display: flex; align-items: center; justify-content: center; gap: 15px; padding: 20px 0;'>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <div style='width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; {step1_circle}'>1</div>
                <span style='font-size: 13px; {step1_text}'>Choose domain</span>
            </div>
            <div style='width: 20px; height: 1px; background-color: rgba(255,255,255,0.15);'></div>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <div style='width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; {step2_circle}'>2</div>
                <span style='font-size: 13px; {step2_text}'>Choose role</span>
            </div>
            <div style='width: 20px; height: 1px; background-color: rgba(255,255,255,0.15);'></div>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <div style='width: 22px; height: 22px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 11px; font-weight: bold; {step3_circle}'>3</div>
                <span style='font-size: 13px; {step3_text}'>Start learning</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with nav_col_auth:
        st.markdown("<div style='padding: 15px 40px 15px 0; display: flex; justify-content: flex-end; align-items: center;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Login Gate: Split-panel auth screen (no-scroll, viewport-locked)
# ---------------------------------------------------------

# ---------------------------------------------------------
# Main Page Content wrapped in content-wrapper (authenticated users only)
# ---------------------------------------------------------
st.markdown("<div class='content-wrapper'>", unsafe_allow_html=True)

if st.session_state.main_nav_choice == "👤 Profile & Badges Showcase" and st.session_state.current_user:
    # ---------------------------------------------------------
    # USER PROFILE & BADGE SHOWCASE SCREEN
    # ---------------------------------------------------------
    u = st.session_state.current_user
    st.markdown(f"<h2>👤 {u['name']}'s Achievements</h2>", unsafe_allow_html=True)
    
    # Calculate overall stats
    badges = db_provider.get_user_badges(u["google_id"])
    active_role = st.session_state.selected_role or ""
    
    # Calculate quiz average
    quiz_scores = []
    if active_role:
        role_info = ROLES.get(active_role, {})
        syllabus = role_info.get("weekly_learning_sequence", [])
        total_weeks = len(syllabus)
        for wk in range(1, total_weeks + 1):
            rec = db_provider.get_quiz_record(u["google_id"], active_role, wk)
            if rec.get("attempt_count", 0) > 0:
                quiz_scores.append(rec.get("best_score", 0))
    quiz_avg = (sum(quiz_scores) / len(quiz_scores)) * 20 if quiz_scores else 0.0

    col_p1, col_p2, col_p3 = st.columns(3)
    with col_p1:
        st.markdown(f"""
        <div class='premium-card' style='text-align: center; border-top: 3px solid #FF9F43;'>
            <h4 style='margin: 0; color: #FF9F43;'>🔥 Active Streak</h4>
            <h1 style='margin: 10px 0; color: #FFFFFF;'>{u.get('streak_count', 0)} Days</h1>
        </div>
        """, unsafe_allow_html=True)
    with col_p2:
        st.markdown(f"""
        <div class='premium-card' style='text-align: center; border-top: 3px solid #06B6D4;'>
            <h4 style='margin: 0; color: #06B6D4;'>🏅 Badges Earned</h4>
            <h1 style='margin: 10px 0; color: #FFFFFF;'>{len(badges)} Earned</h1>
        </div>
        """, unsafe_allow_html=True)
    with col_p3:
        st.markdown(f"""
        <div class='premium-card' style='text-align: center; border-top: 3px solid #10B981;'>
            <h4 style='margin: 0; color: #10B981;'>📝 Quiz Performance</h4>
            <h1 style='margin: 10px 0; color: #FFFFFF;'>{quiz_avg:.1f}%</h1>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("### Badge Collection")
    badge_cols = st.columns(4)
    all_possible_badges = list(BADGE_DESCRIPTIONS.keys())
    for b_idx, b_name in enumerate(all_possible_badges):
        b_col = b_idx % 4
        b_desc = BADGE_DESCRIPTIONS.get(b_name, "")
        is_earned = b_name in badges
        bg_gradient, b_glow = get_badge_styling(b_name)
        
        with badge_cols[b_col]:
            badge_style = f"background: {bg_gradient}; box-shadow: 0 0 20px {b_glow};" if is_earned else "background: rgba(255, 255, 255, 0.1);"
            text_color = "#FFFFFF" if is_earned else "rgba(255,255,255,0.3)"
            st.markdown(f"""
            <div class='premium-card' style='text-align: center;'>
                <div class='badge-medal {"" if is_earned else "badge-locked"}' style='{badge_style}'>🏅</div>
                <strong style='color: {text_color}; font-size: 14px;'>{b_name}</strong>
            </div>
            """, unsafe_allow_html=True)

else:
    # ---------------------------------------------------------
    # LEARNING PATH SYLLABUS SCREEN FLOW
    # ---------------------------------------------------------
    
    # SCREEN 1: Technology Domain Browser Selection
    if st.session_state.current_screen == 1:
        st.markdown("<span class='eyebrow'>STEP 1 OF 3</span>", unsafe_allow_html=True)
        st.markdown("""
        <h1 style='color: #FFFFFF; font-size: 2.8rem; font-family: "Outfit", sans-serif; font-weight: 700; line-height: 1.2; margin-bottom: 15px;'>
            Where do you want to<br>
            <span style='background: linear-gradient(90deg, #6C63FF 0%, #A78BFA 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>go in your career?</span>
        </h1>
        """, unsafe_allow_html=True)
        st.markdown("<p class='muted-desc' style='font-size: 15px; margin-bottom: 25px;'>Master the world's most in-demand AI & tech roles — curated from the top 3 global learning platforms, compiled so you land high-paying jobs faster.</p>", unsafe_allow_html=True)
        
        # Glass Search Bar input using clean direct state (no double-rerun sync loops)
        search_query = st.text_input(
            "Search technology domains", 
            placeholder="🔍 Search roles, skills, or technologies...", 
            key="domain_search_input", 
            label_visibility="collapsed"
        )
        
        # Keep filter chip state initialized for backwards compatibility (chips removed from UI)
        if "selected_filter_chip" not in st.session_state:
            st.session_state.selected_filter_chip = "All"

        st.markdown("<br><span class='eyebrow'>Available tech domains</span>", unsafe_allow_html=True)
        
        # Filter domains list using text search & filter chips
        selected_chip = st.session_state.selected_filter_chip
        filtered_domains = {}
        for d_name, d_data in DOMAINS.items():
            # Check text query match
            domain_roles = [r_name for r_name, r_data in ROLES.items() if r_data.get("domain") == d_name]
            roles_match = any(search_query.lower() in r.lower() for r in domain_roles)
            text_match = not search_query or search_query.lower() in d_name.lower() or search_query.lower() in d_data["desc"].lower() or roles_match
            
            # Check chip filter match
            chip_match = True
            if selected_chip == "High Demand":
                chip_match = d_data.get("outlook") in ["Extremely high demand", "High demand"]
            elif selected_chip == "Beginner":
                domain_roles_info = [r_data for r_name, r_data in ROLES.items() if r_data.get("domain") == d_name]
                chip_match = any(r.get("role_difficulty_tier") == "Beginner" for r in domain_roles_info)
            elif selected_chip == "Under 100 hrs":
                domain_roles_info = [r_data for r_name, r_data in ROLES.items() if r_data.get("domain") == d_name]
                chip_match = any(int(r.get("estimated_learning_hours", 200)) < 100 for r in domain_roles_info)
                
            if text_match and chip_match:
                filtered_domains[d_name] = d_data

        # Render Domain Cards Grid in 3 columns
        domain_names = list(filtered_domains.keys())

        # Domain icon map
        DOMAIN_ICONS = {
            "Artificial Intelligence": "🧠",
            "Agentic AI": "🤖",
            "Machine Learning": "📈",
            "Deep Learning": "🔬",
            "Large Language Models": "💬",
            "Natural Language Processing": "📝",
            "Data Science": "📊",
            "Data Analytics": "📉",
            "Business Intelligence": "💡",
            "Software Engineering": "⚙️",
            "Backend Engineering": "🖥️",
            "Full Stack Development": "🔧",
            "Web Development": "🌐",
            "Frontend Development": "🎨",
            "Mobile Development": "📱",
            "Android Development": "🤖",
            "iOS Development": "🍎",
            "Cloud Computing": "☁️",
            "DevOps": "🔄",
            "Cybersecurity": "🔒",
            "DevSecOps": "🛡️",
        }

        if domain_names:
            for row_idx in range(0, len(domain_names), 3):
                row_cols = st.columns(3, gap="medium")
                for col_offset in range(3):
                    idx = row_idx + col_offset
                    if idx < len(domain_names):
                        d_name = domain_names[idx]
                        d_data = filtered_domains[d_name]
                        accent = get_domain_accent_by_index(idx)
                        
                        h = accent.lstrip('#')
                        rgb = tuple(int(h[i:i+2], 16) for i in (0, 2, 4))
                        rgba_icon_bg  = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.15)"
                        rgba_badge_bg = f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, 0.12)"
                        domain_roles_count = sum(1 for r_name, r_data in ROLES.items() if r_data.get("domain") == d_name)
                        domain_roles_hours = [int(r_data.get("estimated_learning_hours", 40)) for r_name, r_data in ROLES.items() if r_data.get("domain") == d_name]
                        total_domain_hours = sum(domain_roles_hours)
                        avg_domain_hours = int(total_domain_hours / len(domain_roles_hours)) if domain_roles_hours else 0
                        domain_icon = DOMAIN_ICONS.get(d_name, "💼")
                        
                        with row_cols[col_offset]:
                            st.markdown(f"""
<style>
    .dcard-{h} {{
        background: #111827;
        border: 1px solid rgba(255,255,255,0.07);
        border-top: 3px solid {accent};
        border-radius: 16px;
        padding: 24px 22px 16px 22px;
        min-height: 270px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        cursor: default;
        transition: transform 0.22s cubic-bezier(0.16,1,0.3,1), box-shadow 0.22s ease, border-color 0.22s ease;
        box-shadow: 0 4px 24px rgba(0,0,0,0.3);
        margin-bottom: 0px;
    }}
    .dcard-{h}:hover {{
        transform: translateY(-3px);
        box-shadow: 0 12px 36px rgba(0,0,0,0.4), 0 0 18px rgba({rgb[0]},{rgb[1]},{rgb[2]},0.25);
        border-color: {accent};
        border-top-color: {accent};
    }}
    .dcard-{h} * {{ background: transparent !important; }}
</style>
<div class="dcard-{h}">
    <div>
        <div style="width:46px; height:46px; border-radius:10px; background:{rgba_icon_bg} !important; border:1px solid rgba({rgb[0]},{rgb[1]},{rgb[2]},0.3); display:flex; align-items:center; justify-content:center; font-size:24px; margin-bottom:16px;">{domain_icon}</div>
        <div style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom:12px;">
            <div style="display:inline-block; background:{rgba_badge_bg} !important; border:1px solid rgba({rgb[0]},{rgb[1]},{rgb[2]},0.5); color:{accent}; font-size:10px; font-weight:700; padding:4px 8px; border-radius:20px; letter-spacing:0.02em;">{d_data['outlook']}</div>
            <div style="display:inline-block; background:rgba(255,255,255,0.05) !important; border:1px solid rgba(255,255,255,0.15); color:rgba(255,255,255,0.85); font-size:10px; font-weight:700; padding:4px 8px; border-radius:20px; letter-spacing:0.02em;">📁 {domain_roles_count} Roles</div>
            <div style="display:inline-block; background:rgba(255,255,255,0.05) !important; border:1px solid rgba(255,255,255,0.15); color:rgba(255,255,255,0.85); font-size:10px; font-weight:700; padding:4px 8px; border-radius:20px; letter-spacing:0.02em;">⏱ {avg_domain_hours} hrs avg</div>
        </div>
        <h3 style="margin:0 0 10px 0; font-size:1.2rem; font-weight:700; color:#FFFFFF; font-family:'Outfit',sans-serif; line-height:1.3;">{d_name}</h3>
        <p style="margin:0; font-size:12.5px; color:rgba(255,255,255,0.5); line-height:1.6;">{d_data['desc']}</p>
    </div>
    <div style="display:flex; justify-content:space-between; align-items:center; margin-top:16px; padding-top:14px; border-top:1px solid rgba(255,255,255,0.06);">
        <span style="font-size:12px; color:rgba(255,255,255,0.38); font-weight:500;">Curated Career Roadmaps</span>
    </div>
</div>
<div class="domain-explore-btn">""", unsafe_allow_html=True)
                            if st.button(f"Explore {d_name} →", key=f"domain_btn_{d_name}", use_container_width=True):
                                st.session_state.selected_domain = d_name
                                st.session_state.current_screen = 2
                                st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.info("No technology domains matched your query.")


    # SCREEN 2: Role Detail selection
    elif st.session_state.current_screen == 2:
        domain_name = st.session_state.selected_domain
        roles_in_domain = {r_name: r_data for r_name, r_data in ROLES.items() if r_data.get("domain") == domain_name}
        
        col_role_back, col_role_spacer = st.columns([2, 8])
        with col_role_back:
            if st.button("⬅ Back to Domains", key="back_to_dom_btn"):
                st.session_state.current_screen = 1
                st.rerun()
                
        st.markdown("<br>", unsafe_allow_html=True)
        
        if roles_in_domain:
            for role_name, role_info in roles_in_domain.items():
                hours_val = int(role_info.get("estimated_learning_hours", 40))
                weeks_val = int(hours_val / 10)
                hours_breakdown = f"{hours_val} hours (~{weeks_val} weeks at 10 hrs/week)"
                
                role_header_col1, role_header_col2 = st.columns([8, 2])
                with role_header_col1:
                    st.markdown(f"""
                    <div style='display: flex; align-items: center; gap: 15px;'>
                        <div style='width: 52px; height: 52px; border-radius: 12px; background: rgba(108, 99, 255, 0.15); display: flex; align-items: center; justify-content: center; font-size: 26px; border: 1px solid rgba(108, 99, 255, 0.25);'>
                            🤖
                        </div>
                        <div>
                            <h2 style='margin: 0; color: #FFFFFF; font-size: 22px; font-weight: 700;'>{role_name}</h2>
                            <div style='display: flex; gap: 8px; margin-top: 8px;'>
                                <span style='background-color: rgba(108,99,255,0.15); color:#A78BFA; border: 1px solid rgba(108,99,255,0.25); padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;'>{role_info.get("role_difficulty_tier", "Intermediate")}</span>
                                <span style='background-color: rgba(108,99,255,0.15); color:#A78BFA; border: 1px solid rgba(108,99,255,0.25); padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;'>{hours_breakdown}</span>
                                <span style='background-color: rgba(108,99,255,0.15); color:#A78BFA; border: 1px solid rgba(108,99,255,0.25); padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 600;'>Extremely high demand</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                with role_header_col2:
                    st.markdown("""
                    <style>
                    .choose-role-btn-container div.stButton > button {
                        width: fit-content !important;
                        padding: 10px 20px !important;
                        background-color: #7c3aed !important;
                        background: #7c3aed !important;
                        color: #ffffff !important;
                        border-radius: 8px !important;
                        border: none !important;
                        display: block !important;
                        margin-left: auto !important;
                    }
                    .choose-role-btn-container div.stButton > button p,
                    .choose-role-btn-container div.stButton > button span {
                        color: #ffffff !important;
                    }
                    </style>
                    """, unsafe_allow_html=True)
                    st.markdown('<div class="choose-role-btn-container">', unsafe_allow_html=True)
                    if st.button("Start roadmap ➔", key=f"choose_role_{role_name}", use_container_width=False):
                        st.session_state.selected_role = role_name
                        st.session_state.completed_weeks = set()
                        st.session_state.completed_projects = set()
                        st.session_state.completed_materials = set()
                        st.session_state.bookmarks = {}
                        st.session_state.chat_history = []
                        st.session_state.current_screen = 4
                        trigger_progress_save()
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)
                        
                st.markdown("<br>", unsafe_allow_html=True)
                
                tab_overview, tab_edu, tab_outcomes = st.tabs([
                    "Overview & competencies", 
                    "Curriculum", 
                    "What you'll build"
                ])
                
                with tab_overview:
                    col_overview_left, col_overview_right = st.columns(2)
                    responsibilities = role_info.get("daily_responsibilities") or role_info.get("responsibilities", [])
                    objectives = role_info.get("learning_objectives") or []
                    
                    resp_bullets = "".join([f"<li style='margin-bottom:8px; display:flex; align-items:flex-start;'><span style='color:#6C63FF; margin-right:8px;'>➔</span> {r}</li>" for r in responsibilities])
                    obj_bullets = "".join([f"<li style='margin-bottom:8px; display:flex; align-items:flex-start;'><span style='color:#6C63FF; margin-right:8px;'>➔</span> {o}</li>" for o in objectives])
                    
                    with col_overview_left:
                        st.markdown(f"""
                        <div class='premium-card' style='min-height: 250px;'>
                            <strong class='eyebrow' style='font-size:12px; margin-bottom:12px;'>DAILY RESPONSIBILITIES</strong>
                            <ul style='list-style:none; padding-left:0; font-size:13px; color:rgba(255,255,255,0.75);'>{resp_bullets}</ul>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    with col_overview_right:
                        st.markdown(f"""
                        <div class='premium-card' style='min-height: 250px;'>
                            <strong class='eyebrow' style='font-size:12px; margin-bottom:12px;'>PRIMARY LEARNING OBJECTIVES</strong>
                            <ul style='list-style:none; padding-left:0; font-size:13px; color:rgba(255,255,255,0.75);'>{obj_bullets}</ul>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    core_list = role_info.get("core_competencies", [])
                    core_chips = "".join([f"<span style='background-color: rgba(108,99,255,0.15); color:#A78BFA; border: 1px solid rgba(108,99,255,0.25); padding: 6px 12px; border-radius: 8px; font-size:12px; font-weight:600; margin-right:8px; margin-bottom:8px; display:inline-block;'>{comp}</span>" for comp in core_list])
                    st.markdown(f"""
                    <div class='premium-card'>
                        <strong class='eyebrow' style='font-size:12px; margin-bottom:12px;'>CORE COMPETENCIES REQUIRED</strong>
                        <div style='display:flex; flex-wrap:wrap;'>{core_chips}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with tab_edu:
                    edu_meta = role_info.get("educational_metadata", {})
                    if edu_meta:
                        st.markdown(f"<div class='premium-card'>", unsafe_allow_html=True)
                        st.markdown(f"<p style='font-size: 14px;'><strong>👤 Typical Learner Profile:</strong> {edu_meta.get('typical_learner_profile', 'Developers/Learners looking to expand their skills.')}</p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='font-size: 14px;'><strong>⏱️ Recommended Weekly Study:</strong> {edu_meta.get('recommended_weekly_study_hours', '10-12')} hours/week</p>", unsafe_allow_html=True)
                        st.markdown(f"<p style='font-size: 14px;'><strong>📅 Completion Time:</strong> {edu_meta.get('estimated_completion_time_weeks', '12')} weeks</p>", unsafe_allow_html=True)
                        st.markdown("</div>", unsafe_allow_html=True)
                    else:
                        st.info("Profile data compiles in seed database.")
                        
                with tab_outcomes:
                    outcomes = role_info.get("role_learning_outcomes", [])
                    if outcomes:
                        out_bullets = "".join([f"<li style='margin-bottom:8px; display:flex; align-items:flex-start;'><span style='color:#6C63FF; margin-right:8px;'>➔</span> {outcome}</li>" for outcome in outcomes])
                        st.markdown(f"""
                        <div class='premium-card'>
                            <strong class='eyebrow' style='font-size:12px; margin-bottom:12px;'>KEY LEARNING OUTCOMES</strong>
                            <ul style='list-style:none; padding-left:0; font-size:13px; color:rgba(255,255,255,0.75);'>{out_bullets}</ul>
                        </div>
                        """, unsafe_allow_html=True)
                        


    # SCREEN 3: Learner Dashboard + Syllabus Page
    elif st.session_state.current_screen == 4:
        role_name = st.session_state.selected_role
        role_info = ROLES.get(role_name, {})
        syllabus = role_info.get("weekly_learning_sequence", [])
        
        if not syllabus:
            curriculum_item = next((item for item in CURRICULUM if item.get("role") == role_name), None)
            if curriculum_item:
                syllabus = curriculum_item.get("weeks", [])
                
        total_weeks = len(syllabus)
        completed_count = len(st.session_state.completed_weeks)
        progress_pct = int((completed_count / total_weeks) * 100) if total_weeks > 0 else 0
        
        # ── Dashboard heading
        st.markdown("""
<h1 style='font-size:1.9rem; font-weight:800; color:#FFFFFF; margin:0 0 24px 0;
   letter-spacing:-0.5px; font-family:"Outfit",sans-serif;'>LEARNER DASHBOARD</h1>
""", unsafe_allow_html=True)

        # ── Stat cards row: 3 columns aligned side-by-side
        stat_col1, stat_col2, stat_col3 = st.columns([1, 1, 1.2], gap="medium")
        
        with stat_col1:
            st.markdown(f"""
<div style='background:#151827; border:1px solid #252837; border-radius:14px; padding:24px 28px; height:150px; display:flex; flex-direction:column; justify-content:space-between;'>
    <span style='font-size:12px; color:#FFFFFF; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;'>COURSE PROGRESS</span>
    <div style='display:flex; align-items:center; gap:20px; margin-top:20px;'>
        <div style='flex:1; background:rgba(255,255,255,0.08); border-radius:6px; height:8px;'>
            <div style='width:{progress_pct}%; background:linear-gradient(90deg,#6C63FF,#A78BFA); border-radius:6px; height:8px;'></div>
        </div>
        <span style='font-size:2.2rem; font-weight:700; color:#FFFFFF; line-height:1;'>{progress_pct}%</span>
    </div>
    <span style='font-size:12px; color:rgba(255,255,255,0.4); margin-top:10px;'>{completed_count} of {total_weeks} weeks complete</span>
</div>
""", unsafe_allow_html=True)

        with stat_col2:
            bars = []
            for hrs in st.session_state.study_history:
                color = "#A78BFA" if hrs > 0 else "rgba(255,255,255,0.08)"
                height = max(4, min(20, int(hrs * 5)))
                bars.append(f"<div style='width: 12px; height: {height}px; background: {color}; border-radius: 2px;' title='{hrs} hrs'></div>")
            bars_html = "".join(bars)
            
            st.markdown(f"""
<div style='background:#151827; border:1px solid #252837; border-radius:14px; padding:20px 24px; height:150px; display:flex; flex-direction:column; justify-content:space-between;'>
    <div style='display:flex; justify-content:space-between; align-items:flex-start;'>
        <div>
            <span style='font-size:11px; color:#FFFFFF; font-weight:700; text-transform:uppercase; letter-spacing:0.08em;'>STUDY HOURS</span>
            <div style='margin-top:6px;'>
                <span style='font-size:2rem; font-weight:700; color:#A78BFA; line-height:1;'>{st.session_state.study_hours:.1f}</span>
                <span style='font-size:12px; color:rgba(255,255,255,0.5); margin-left:4px;'>hrs</span>
            </div>
        </div>
        <div style='display:flex; flex-direction:column; align-items:flex-end;'>
            <span style='font-size:9px; color:rgba(255,255,255,0.4); font-weight:700; letter-spacing:0.03em;'>LAST 7 DAYS</span>
            <div style='display:flex; gap:3px; align-items:flex-end; height:20px; margin-top:4px;'>{bars_html}</div>
        </div>
    </div>
    <span style='font-size:11px; color:rgba(255,255,255,0.4); margin-top:2px;'>Goal: 2 hrs today</span>
</div>
""", unsafe_allow_html=True)
            st.markdown("<div style='margin-top:-50px; padding: 0 24px; position:relative; z-index:10;'>", unsafe_allow_html=True)
            if st.button("🕒 Log 1 Hour Study", key="add_study_hr_btn", use_container_width=True, type="primary"):
                st.session_state.study_hours += 1.0
                st.session_state.study_history[-1] += 1.0
                trigger_progress_save()
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with stat_col3:
            st.markdown(f"""
<div style='background:#151827; border:1px solid #252837; border-radius:14px; padding:20px 24px; height:150px; display:flex; flex-direction:column; justify-content:space-between;'>
    <div style='display:flex; align-items:center; gap:10px;'>
        <div style='width:32px; height:32px; border-radius:8px; background:rgba(108,99,255,0.15); display:flex; align-items:center; justify-content:center; font-size:16px;'>🤖</div>
        <span style='font-size:11px; font-weight:700; color:#A78BFA; text-transform:uppercase; letter-spacing:0.08em;'>AI STUDY ASSISTANT</span>
    </div>
    <div style='font-size:12px; color:rgba(255,255,255,0.7); margin-top:4px; line-height:1.4;'>Ask questions about this week's goals, concepts, or practice tasks.</div>
</div>
""", unsafe_allow_html=True)
            st.markdown("<div style='margin-top:-50px; padding: 0 20px; position:relative; z-index:10;'>", unsafe_allow_html=True)
            with st.popover("💬 Chat with AI Assistant", use_container_width=True):
                st.markdown("**🤖 AI Study Assistant**")
                if st.session_state.chat_history:
                    for chat in st.session_state.chat_history[-6:]:
                        if chat["role"] == "user":
                            st.markdown(f"**You:** {chat['text']}")
                        else:
                            st.markdown(f"**AI:** {chat['text']}")
                q_text = st.text_input("Ask a question...", key="ai_top_chat_input", label_visibility="collapsed")
                if st.button("Send Query ✈", key="ai_top_send_btn", use_container_width=True, type="primary"):
                    if q_text.strip():
                        st.session_state.chat_history.append({"role": "user", "text": q_text})
                        context_summary = f"Role: {role_name}. Completed weeks: {list(st.session_state.completed_weeks)}."
                        with st.spinner("Thinking..."):
                            try:
                                if hasattr(study_assistant_agent, "ask"):
                                    reply = study_assistant_agent.ask(q_text, context_summary)
                                else:
                                    reply = "AI Assistant ready."
                                st.session_state.chat_history.append({"role": "assistant", "text": reply})
                            except Exception as ex:
                                st.session_state.chat_history.append({"role": "assistant", "text": f"Error: {ex}"})
                        st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # Render quiet success banners for completed weeks
        newly_completed = st.session_state.completed_weeks - st.session_state.completed_weeks_notified
        for cw_idx in list(newly_completed):
            st.markdown(f"""
<div style='background:rgba(16,185,129,0.08); border:1px solid rgba(16,185,129,0.25); border-radius:12px; padding:16px 20px; margin-bottom:20px; display:flex; align-items:center; justify-content:space-between; gap:16px;'>
    <div style='display:flex; align-items:center; gap:12px;'>
        <span style='font-size:22px;'>🏆</span>
        <div>
            <div style='font-size:14px; font-weight:700; color:#10B981;'>Week {cw_idx + 1} Fully Completed!</div>
            <div style='font-size:12px; color:rgba(255,255,255,0.65); margin-top:2px;'>Fantastic job! You've completed all study materials, weekly projects, and passed the quiz. Keep up the great momentum!</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
            if st.button(f"Dismiss Notification for Week {cw_idx + 1}", key=f"dismiss_notify_{cw_idx}"):
                st.session_state.completed_weeks_notified.add(cw_idx)
                st.rerun()
            
        if completed_count == 0 and st.session_state.study_hours == 0.0:
            has_bookmark = len(st.session_state.bookmarks) > 0
            has_materials = len(st.session_state.completed_materials) > 0
            
            bookmark_check = "✔" if has_bookmark else "○"
            materials_check = "✔" if has_materials else "○"
            
            bookmark_style = "text-decoration: line-through; color: rgba(255,255,255,0.4);" if has_bookmark else "color: #FFFFFF;"
            materials_style = "text-decoration: line-through; color: rgba(255,255,255,0.4);" if has_materials else "color: #FFFFFF;"
            
            st.markdown(f"""
<div style='background: rgba(108,99,255,0.03); border: 1px dashed rgba(108,99,255,0.3); border-radius: 14px; padding: 20px 24px; margin-bottom: 24px;'>
    <h3 style='margin: 0 0 10px 0; font-size: 15px; color: #A78BFA; font-family: "Outfit", sans-serif; font-weight: 700;'>🚀 Your Journey Starts Here: Onboarding Checklist</h3>
    <p style='font-size: 12px; color: rgba(255,255,255,0.6); margin: 0 0 16px 0; line-height: 1.4;'>Complete these quick onboarding steps to kick off your custom roadmap and build learning habits!</p>
    <ul style='list-style: none; padding-left: 0; margin: 0; font-size: 13px; display: flex; flex-direction: column; gap: 8px;'>
        <li style='display: flex; align-items: center; gap: 10px; text-decoration: line-through; color: rgba(255,255,255,0.4);'>
            <span style='background: rgba(16,185,129,0.15); border: 1px solid rgba(16,185,129,0.3); color: #10B981; border-radius: 50%; width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: bold;'>✔</span>
            Select your career path ({role_name})
        </li>
        <li style='display: flex; align-items: center; gap: 10px; {bookmark_style}'>
            <span style='background: {"rgba(16,185,129,0.15)" if has_bookmark else "rgba(255,255,255,0.04)"}; border: 1px solid {"rgba(16,185,129,0.3)" if has_bookmark else "rgba(255,255,255,0.12)"}; color: {"#10B981" if has_bookmark else "rgba(255,255,255,0.4)"}; border-radius: 50%; width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: bold;'>{"✔" if has_bookmark else "○"}</span>
            Bookmark Week 1 to save it to your bookmarks
        </li>
        <li style='display: flex; align-items: center; gap: 10px; {materials_style}'>
            <span style='background: {"rgba(16,185,129,0.15)" if has_materials else "rgba(255,255,255,0.04)"}; border: 1px solid {"rgba(16,185,129,0.3)" if has_materials else "rgba(255,255,255,0.12)"}; color: {"#10B981" if has_materials else "rgba(255,255,255,0.4)"}; border-radius: 50%; width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: bold;'>{"✔" if has_materials else "○"}</span>
            Explore Week 1 and mark study materials completed
        </li>
        <li style='display: flex; align-items: center; gap: 10px;'>
            <span style='background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.12); color: rgba(255,255,255,0.4); border-radius: 50%; width: 18px; height: 18px; display: flex; align-items: center; justify-content: center; font-size: 9px; font-weight: bold;'>○</span>
            Log your first 1 Hour Study session to start a habit tracker
        </li>
    </ul>
</div>
""", unsafe_allow_html=True)

            # ── Course Timeline accordion
            st.markdown("""
<span style='font-size:13px; font-weight:700; color:rgba(255,255,255,0.55); text-transform:uppercase; letter-spacing:0.1em;'>Course Timeline</span>
""", unsafe_allow_html=True)
            st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)

            if not syllabus:
                st.info("Curriculum is still being generated. Please wait...")
            else:
                active_week_idx = len(st.session_state.completed_weeks)
                if active_week_idx >= len(syllabus):
                    active_week_idx = len(syllabus) - 1

                for w_idx, week_mod in enumerate(syllabus):
                    week_num      = week_mod.get("week", w_idx + 1)
                    week_goal     = week_mod.get("goal", "Weekly Goal")
                    objectives    = week_mod.get("objectives", [])
                    resources     = week_mod.get("resources", [])

                    is_done   = w_idx in st.session_state.completed_weeks
                    is_active = (w_idx == active_week_idx)

                    # Row styling
                    if is_done:
                        row_icon  = "✅"
                        row_label = f"WEEK {week_num} - COMPLETED"
                        label_color = "#10B981"
                    elif is_active:
                        row_icon  = "🔵"
                        row_label = f"WEEK {week_num} - IN PROGRESS"
                        label_color = "#A78BFA"
                    else:
                        row_icon  = "⭕"
                        row_label = f"WEEK {week_num} - UPCOMING"
                        label_color = "rgba(255,255,255,0.35)"

                    # Collapsed rows (completed & upcoming) — use st.expander
                    expander_label = f"{row_icon}  **{row_label}** — {week_goal}"
                    
                    with st.expander(expander_label, expanded=is_active):
                        # ── Week heading
                        st.markdown(f"""
<div style='margin-bottom:16px;'>
    <span style='font-size:11px; font-weight:700; color:{label_color}; text-transform:uppercase; letter-spacing:0.09em;'>{row_label}</span>
    <h2 style='margin:6px 0 0 0; font-size:1.35rem; font-weight:700; color:#FFFFFF; font-family:"Outfit",sans-serif;'>{week_goal}</h2>
</div>
""", unsafe_allow_html=True)

                        # ── Two-column: objectives + resources
                        obj_col, res_col = st.columns([1, 1], gap="large")

                        with obj_col:
                            bullets_html = "".join([
                                f"<li style='margin-bottom:8px; display:flex; align-items:flex-start; gap:8px;'>"
                                f"<span style='color:#6C63FF; flex-shrink:0; margin-top:2px;'>•</span>"
                                f"<span style='color:rgba(255,255,255,0.75); font-size:13px;'>{obj}</span></li>"
                                for obj in objectives
                            ])
                            st.markdown(f"""
<div>
    <span style='font-size:10px; font-weight:700; color:#6C63FF; text-transform:uppercase; letter-spacing:0.1em;'>Learning Objectives</span>
    <ul style='list-style:none; padding:0; margin:10px 0 0 0;'>{bullets_html}</ul>
</div>
""", unsafe_allow_html=True)

                        with res_col:
                            st.markdown("""
<span style='font-size:10px; font-weight:700; color:#6C63FF; text-transform:uppercase; letter-spacing:0.1em;'>Curated Learning Resources</span>
""", unsafe_allow_html=True)
                            type_icons = {"video": "▶", "book": "📗", "article": "📄", "lab": "🧪", "course": "📚", "docs": "📘", "documentation": "📘"}
                            for r_idx, res in enumerate(resources):
                                # Call our validation layer
                                v_res = verify_and_get_resource(res, week_goal, objectives)
                                
                                res_title = v_res.get("title", "Resource")
                                res_url   = v_res.get("url", "#")
                                res_prov  = v_res.get("provider", "")
                                res_type  = v_res.get("type", "course").lower()
                                type_icon = type_icons.get(res_type, "📚")
                                
                                # Extra curation/metadata fields
                                trust_score = v_res.get("trust_score", 9.5)
                                difficulty  = v_res.get("difficulty", "Beginner")
                                duration    = v_res.get("estimated_duration", "45 min")
                                prov_type   = v_res.get("provider_type", "Community")
                                version     = v_res.get("version", "v1")
                                is_fallback = v_res.get("is_fallback", False)
                                is_emergency = v_res.get("is_emergency", False)
                                change_log  = v_res.get("change_log", "")
                                
                                # Sequence Badge
                                seq_num = r_idx + 1
                                
                                st.markdown(f"""
<div style='background:#1A1D2E; border:1px solid #252837; border-radius:12px; padding:16px; margin:12px 0;'>
    <div style='display:flex; align-items:center; gap:12px;'>
        <div style='width:36px; height:36px; border-radius:8px; background:rgba(108,99,255,0.15); display:flex; align-items:center; justify-content:center; font-size:16px; flex-shrink:0;'>{type_icon}</div>
        <div style='flex:1; min-width:0;'>
            <div style='font-size:13.5px; font-weight:700; color:#FFFFFF; line-height:1.4; word-wrap:break-word; white-space:normal; overflow-wrap:break-word; word-break:break-word;'>#{seq_num} {res_title}</div>
            <div style='font-size:11.5px; color:rgba(255,255,255,0.45); margin-top:2px;'>{res_prov} • {res_type.capitalize()}</div>
        </div>
        <a href='{res_url}' target='_blank' style='background:rgba(108,99,255,0.2); border:1px solid rgba(108,99,255,0.4); color:#A78BFA; text-decoration:none; font-size:11.5px; font-weight:600; padding:6px 12px; border-radius:6px; white-space:nowrap;'>Start Learning →</a>
    </div>
</div>
""", unsafe_allow_html=True)



                        # ── Weekly Progression Checklist
                        st.markdown("""
<div style='margin-top:16px; margin-bottom:8px;'>
    <span style='font-size:10px; font-weight:700; color:rgba(255,255,255,0.4); text-transform:uppercase; letter-spacing:0.1em;'>Weekly Progression Checklist</span>
</div>
""", unsafe_allow_html=True)

                        is_materials_done = w_idx in st.session_state.completed_materials
                        is_proj_done      = w_idx in st.session_state.completed_projects

                        chk_col1, chk_col2, bk_col = st.columns([2, 2, 2])
                        with chk_col1:
                            chk_m = st.checkbox("Mark materials completed", value=is_materials_done, key=f"chk_mat_v10_{w_idx}")
                            if chk_m != is_materials_done:
                                if chk_m: st.session_state.completed_materials.add(w_idx)
                                else: st.session_state.completed_materials.discard(w_idx)
                                trigger_progress_save(); st.rerun()
                        with chk_col2:
                            chk_p = st.checkbox("Mark weekly project completed", value=is_proj_done, key=f"chk_proj_v10_{w_idx}")
                            if chk_p != is_proj_done:
                                if chk_p: st.session_state.completed_projects.add(w_idx)
                                else: st.session_state.completed_projects.discard(w_idx)
                                trigger_progress_save(); st.rerun()
                        with bk_col:
                            b_name     = f"Week {week_num}: {week_goal}"
                            is_bm_saved = b_name in st.session_state.bookmarks
                            if st.button("⭐ Bookmark Week" if not is_bm_saved else "⭐ Bookmarked", key=f"bm_btn_v10_{w_idx}", use_container_width=True):
                                if not is_bm_saved:
                                    purl = resources[0].get("url", "https://www.freecodecamp.org/learn/") if resources else "https://www.freecodecamp.org/learn/"
                                    st.session_state.bookmarks[b_name] = purl
                                    trigger_progress_save(); st.rerun()

                        # ── Quiz popover
                        user_id    = st.session_state.current_user["google_id"] if st.session_state.current_user else "guest_learner"
                        quiz_record = db_provider.get_quiz_record(user_id, role_name, week_num)
                        attempts    = quiz_record.get("attempt_count", 0)
                        best_score  = quiz_record.get("best_score", 0)

                        st.markdown("<div style='height:8px;'></div>", unsafe_allow_html=True)
                        if attempts > 0:
                            st.markdown(f"<div style='margin-bottom:6px;'><span style='font-size:12.5px; color:#10B981; font-weight:600;'>🏆 Quiz Score: {best_score}/5 ({attempts}/3 attempts)</span></div>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<div style='margin-bottom:6px;'><span style='font-size:12.5px; color:rgba(255,255,255,0.4);'>📝 Quiz not started</span></div>", unsafe_allow_html=True)
                        with st.popover("📝 Open Weekly Quiz", use_container_width=False):
                            if attempts >= 3:
                                st.warning(f"Max attempts reached. Best score: {best_score}/5.")
                            else:
                                st.markdown(f"**Attempt {attempts+1}/3 — Week {week_num}: {week_goal}**")
                                quiz_data = get_weekly_quiz_sync(role_name, week_num, week_goal, objectives, db_provider)
                                questions    = quiz_data.get("questions", [])
                                user_answers = []
                                for q_idx, q_item in enumerate(questions):
                                    st.write(f"**Q{q_idx+1}: {q_item.get('question')}**")
                                    ans = st.radio("", q_item.get("options", []), key=f"quiz_ans_v10_{w_idx}_{q_idx}")
                                    user_answers.append(ans)
                                if st.button("Submit Answers", key=f"quiz_sub_v10_{w_idx}"):
                                    score = sum(
                                        1 for q_idx, q_item in enumerate(questions)
                                        if user_answers[q_idx] == q_item.get("options", [])[q_item.get("correct_answer_index", 0)]
                                    )
                                    db_provider.save_quiz_record(user_id, role_name, week_num, {
                                        "attempt_count": attempts + 1,
                                        "best_score": max(best_score, score),
                                        "last_attempt_date": datetime.utcnow().strftime("%Y-%m-%d")
                                    })
                                    st.success(f"Score: {score}/5")
                                    st.rerun()

                        # Auto-complete week
                        is_week_fully_done = (is_materials_done and is_proj_done and attempts > 0)
                        if is_week_fully_done and w_idx not in st.session_state.completed_weeks:
                            st.session_state.completed_weeks.add(w_idx)
                            trigger_progress_save()
                            if st.session_state.current_user:
                                evaluate_badges(st.session_state.current_user["google_id"], role_name, total_weeks, db_provider)
                            st.rerun()
                        elif not is_week_fully_done and w_idx in st.session_state.completed_weeks:
                            st.session_state.completed_weeks.discard(w_idx)
                            trigger_progress_save()
                            st.rerun()

            st.markdown("<br><hr style='border-color:rgba(255,255,255,0.07);'><br>", unsafe_allow_html=True)
            if st.button("🔙 Change Selected Role", key="change_role_dash_btn"):
                st.session_state.current_screen = 2
                st.rerun()

            st.markdown("<div style='height:24px;'></div>", unsafe_allow_html=True)
            with st.expander("📊 Platform Resource Health Dashboard", expanded=False):
                stats = get_health_stats()
                if stats:
                    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
                    m_col1.metric("Total Resources", stats.get("total", 0))
                    m_col2.metric("Verified & Active", stats.get("working", 0))
                    m_col3.metric("Auto Replaced", stats.get("replaced", 0))
                    m_col4.metric("Avg Trust Score", f"{stats.get('avg_trust', 0.0):.2f}")
                    
                    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
                    st.markdown("**Resource Provenance Distribution:**")
                    pcts = stats.get("percentages", {})
                    st.markdown(f"""
- 🎓 **University Sources**: {pcts.get('University', 0)}%
- 🏛 **Official Docs**: {pcts.get('Official Docs', 0)}%
- 💼 **Industry Providers**: {pcts.get('Industry', 0)}%
- 👥 **Community Resources**: {pcts.get('Community', 0)}%
""")





st.markdown("</div>", unsafe_allow_html=True)
