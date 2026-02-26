"""
Streamlit Dashboard for Personal AI Employee
Premium dark-themed dashboard with icon navigation, charts, analytics, and animations.
All 4 tiers: Bronze, Silver, Gold, Platinum — full feature coverage.
"""
import html as html_mod
import hashlib
import json
import random
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import streamlit as st
import yaml
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from streamlit_option_menu import option_menu

# ---------------------------------------------------------------------------
_SRC_DIR = Path(__file__).resolve().parent
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

import os  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

_project_root = _SRC_DIR.parent
_env_path = _project_root / ".env"
if _env_path.exists():
    load_dotenv(_env_path, override=True)

from config.settings import load_config  # noqa: E402

CONFIG = load_config()
_vault_raw = Path(CONFIG["VAULT_PATH"])
VAULT = _vault_raw.resolve() if _vault_raw.is_absolute() else (_SRC_DIR.parent / _vault_raw).resolve()

VAULT_DIRS = {
    "inbox": "Inbox", "needs_action": "Needs_Action",
    "pending_approval": "Pending_Approval", "approved": "Approved",
    "done": "Done", "rejected": "Rejected",
}
_SENSITIVE_PATTERNS = ("PASSWORD", "SECRET", "TOKEN", "API_KEY", "CREDENTIALS")

# Auth credentials from env (default: admin/admin for dev)
_AUTH_USER = os.getenv("DASHBOARD_USER", "admin")
_AUTH_PASS_HASH = hashlib.sha256(os.getenv("DASHBOARD_PASSWORD", "admin").encode()).hexdigest()

# ===================================================================
st.set_page_config(page_title="AI Employee", page_icon="🤖", layout="wide", initial_sidebar_state="expanded")

# ===================================================================
# MEGA CSS
# ===================================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap');
* { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer { display: none !important; }

/* ============ FORCE LIGHT MODE ============ */
.stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"],
[data-testid="stToolbar"], .main .block-container {
    background: #f8fafc !important; color: #1e293b !important;
}
h1, h2, h3, h4, h5, h6, p, span, label, li { color: #1e293b !important; }

/* ============ HAMBURGER ============ */
button[kind="header"] svg,
button[data-testid="stSidebarCollapseButton"] svg,
button[data-testid="collapsedControl"] svg { display: none !important; }
button[kind="header"]::before,
button[data-testid="stSidebarCollapseButton"]::before,
button[data-testid="collapsedControl"]::before {
    content: '\\2630'; font-size: 1.5rem; color: #6d28d9; display: block; line-height: 1;
}
button[data-testid="collapsedControl"] {
    background: rgba(109,40,217,0.08) !important;
    border: 1px solid rgba(109,40,217,0.2) !important;
    border-radius: 10px !important; width: 40px !important; height: 40px !important;
    display: flex !important; align-items: center !important; justify-content: center !important;
    margin: 8px !important; transition: all 0.3s ease !important;
}
button[data-testid="collapsedControl"]:hover {
    background: rgba(109,40,217,0.15) !important;
    box-shadow: 0 0 12px rgba(109,40,217,0.15) !important;
}

/* ============ SIDEBAR (light) ============ */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #ffffff 0%, #f8fafc 50%, #f1f5f9 100%) !important;
    border-right: 1px solid #e2e8f0;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown span,
section[data-testid="stSidebar"] .stCaption p { color: #475569 !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] h4 { color: #1e293b !important; }

/* ============ HERO ============ */
.hero {
    background: linear-gradient(135deg, #6d28d9, #4f46e5, #2563eb);
    background-size: 200% 200%; animation: gradientShift 6s ease infinite;
    border-radius: 16px; padding: 22px 26px; margin-bottom: 16px;
    border: none; position: relative; overflow: hidden;
    box-shadow: 0 4px 20px rgba(109,40,217,0.15);
}
@keyframes gradientShift { 0%{background-position:0% 50%} 50%{background-position:100% 50%} 100%{background-position:0% 50%} }
.hero::before {
    content:''; position:absolute; top:-60%; right:-20%; width:300px; height:300px;
    background:radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
    border-radius:50%; animation:float 6s ease-in-out infinite;
}
.hero::after {
    content:''; position:absolute; bottom:-50%; left:-15%; width:250px; height:250px;
    background:radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
    border-radius:50%; animation:float 8s ease-in-out infinite reverse;
}
@keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-15px)} }
.hero-t { font-size: 1.4rem; font-weight: 800; color: #fff !important; margin: 0; position: relative; z-index: 1; }
.hero-s { color: rgba(255,255,255,0.8) !important; font-size: 0.8rem; margin-top: 3px; position: relative; z-index: 1; }
.hero-greeting { font-size: 0.8rem; color: rgba(255,255,255,0.9) !important; font-weight: 600; margin-bottom: 4px; position: relative; z-index: 1; }

/* ============ KPI CARDS ============ */
.kpi-row { display: flex; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }
.kpi {
    flex: 1; min-width: 100px;
    background: #fff; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 14px 10px; text-align: center;
    position: relative; overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4,0,0.2,1);
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.kpi:hover { transform: translateY(-3px); border-color: var(--kpi-color, #6d28d9); box-shadow: 0 4px 16px var(--kpi-glow, rgba(109,40,217,0.12)); }
.kpi-bar { width: 100%; height: 3px; position: absolute; top: 0; left: 0; }
.kpi-em { font-size: 1.2rem; }
.kpi-n { font-size: 1.6rem; font-weight: 900; font-family: 'JetBrains Mono', monospace !important; line-height: 1; animation: countFade 0.6s ease-out; }
@keyframes countFade { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
.kpi-l { font-size: 0.65rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #64748b !important; margin-top: 4px; }
.kpi-blue { --kpi-color:#3b82f6; --kpi-glow:rgba(59,130,246,0.15); }
.kpi-blue .kpi-bar { background: linear-gradient(90deg,#3b82f6,#60a5fa); } .kpi-blue .kpi-n { color:#2563eb !important; }
.kpi-orange { --kpi-color:#f97316; --kpi-glow:rgba(249,115,22,0.15); }
.kpi-orange .kpi-bar { background: linear-gradient(90deg,#f97316,#fb923c); } .kpi-orange .kpi-n { color:#ea580c !important; }
.kpi-amber { --kpi-color:#eab308; --kpi-glow:rgba(234,179,8,0.15); }
.kpi-amber .kpi-bar { background: linear-gradient(90deg,#eab308,#facc15); } .kpi-amber .kpi-n { color:#ca8a04 !important; }
.kpi-purple { --kpi-color:#7c3aed; --kpi-glow:rgba(124,58,237,0.15); }
.kpi-purple .kpi-bar { background: linear-gradient(90deg,#7c3aed,#a78bfa); } .kpi-purple .kpi-n { color:#6d28d9 !important; }
.kpi-green { --kpi-color:#10b981; --kpi-glow:rgba(16,185,129,0.15); }
.kpi-green .kpi-bar { background: linear-gradient(90deg,#10b981,#34d399); } .kpi-green .kpi-n { color:#059669 !important; }
.kpi-red { --kpi-color:#ef4444; --kpi-glow:rgba(239,68,68,0.15); }
.kpi-red .kpi-bar { background: linear-gradient(90deg,#ef4444,#f87171); } .kpi-red .kpi-n { color:#dc2626 !important; }

/* ============ TIER CARDS ============ */
.tier-row { display: flex; gap: 8px; margin-bottom: 14px; flex-wrap: wrap; }
.tier-card {
    flex: 1; min-width: 130px; background: #fff;
    border-radius: 12px; padding: 12px 10px; text-align: center;
    border: 1.5px solid #e2e8f0; transition: all 0.3s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.tier-card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.tier-card.active { border-color: var(--glow-color); box-shadow: 0 2px 12px var(--glow-color); }
.tier-icon { font-size: 1.4rem; margin-bottom: 3px; }
.tier-name { font-weight: 800; font-size: 0.82rem; margin-bottom: 2px; }
.tier-desc { font-size: 0.62rem; color: #64748b !important; line-height: 1.3; }
.tier-status { display: inline-block; margin-top: 6px; padding: 2px 8px; border-radius: 10px; font-size: 0.58rem; font-weight: 700; text-transform: uppercase; }
.tier-bronze { border-color: rgba(180,120,50,0.3); --glow-color: rgba(180,120,50,0.2); }
.tier-bronze .tier-name { color: #92400e !important; } .tier-bronze .tier-status { background: #fef3c7; color: #92400e !important; }
.tier-silver { border-color: rgba(148,163,184,0.4); --glow-color: rgba(148,163,184,0.2); }
.tier-silver .tier-name { color: #475569 !important; } .tier-silver .tier-status { background: #f1f5f9; color: #475569 !important; }
.tier-gold { border-color: rgba(202,138,4,0.3); --glow-color: rgba(202,138,4,0.2); }
.tier-gold .tier-name { color: #a16207 !important; } .tier-gold .tier-status { background: #fef9c3; color: #a16207 !important; }
.tier-platinum { border-color: rgba(14,116,144,0.3); --glow-color: rgba(14,116,144,0.2); }
.tier-platinum .tier-name { color: #0e7490 !important; } .tier-platinum .tier-status { background: #cffafe; color: #0e7490 !important; }
.tier-inactive { opacity: 0.35; }

/* ============ GLASS (light) ============ */
.glass {
    background: #fff; border: 1px solid #e2e8f0;
    border-radius: 14px; padding: 20px; margin-bottom: 14px;
    transition: border-color 0.3s ease; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.glass:hover { border-color: rgba(109,40,217,0.25); }
.glass h4 { color: #1e293b !important; font-weight: 700; margin: 0 0 14px 0; font-size: 0.95rem; }

/* ============ STAT ROW ============ */
.stat-row { display: flex; gap: 10px; margin-bottom: 14px; flex-wrap: wrap; }
.stat-card {
    flex: 1; min-width: 90px; background: #fff; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 12px 10px; text-align: center;
    transition: all 0.3s ease; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.stat-card:hover { border-color: rgba(109,40,217,0.25); transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
.stat-n { font-size: 1.2rem; font-weight: 900; font-family: 'JetBrains Mono', monospace !important; color: #6d28d9 !important; animation: countFade 0.6s ease-out; }
.stat-l { font-size: 0.65rem; font-weight: 600; color: #64748b !important; text-transform: uppercase; letter-spacing: 0.5px; margin-top: 2px; }

/* ============ ACTIVITY ============ */
.act {
    display: flex; gap: 12px; padding: 10px 14px; border-radius: 10px;
    margin-bottom: 5px; background: #fff; border: 1px solid #e2e8f0;
    align-items: flex-start; transition: all 0.2s ease;
}
.act:hover { border-color: rgba(109,40,217,0.25); box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.act-d { width: 8px; height: 8px; border-radius: 50%; margin-top: 6px; flex-shrink: 0; }
.act-d-ok { background: #10b981; box-shadow: 0 0 6px rgba(16,185,129,0.4); }
.act-d-er { background: #ef4444; box-shadow: 0 0 6px rgba(239,68,68,0.4); }
.act-d-n { background: #94a3b8; }
.act-b { flex: 1; }
.act-a { font-weight: 600; color: #1e293b !important; font-size: 0.85rem; }
.act-m { font-size: 0.73rem; color: #64748b !important; margin-top: 1px; }
.act-bg { display: inline-block; padding: 1px 8px; border-radius: 6px; font-size: 0.68rem; font-weight: 600; margin-left: 6px; }
.act-bg-ok { background: #dcfce7; color: #16a34a !important; }
.act-bg-er { background: #fee2e2; color: #dc2626 !important; }

/* ============ INFO ROW ============ */
.irow { display: flex; justify-content: space-between; padding: 9px 0; border-bottom: 1px solid #e2e8f0; font-size: 0.85rem; }
.irow:last-child { border-bottom: none; }
.ik { color: #64748b !important; font-weight: 500; }
.iv { color: #1e293b !important; font-family: 'JetBrains Mono', monospace !important; font-size: 0.8rem; }

/* ============ PROGRESS BARS ============ */
.progress-wrap { margin-bottom: 12px; }
.progress-label { display: flex; justify-content: space-between; font-size: 0.8rem; margin-bottom: 4px; }
.progress-lk { color: #64748b !important; font-weight: 600; }
.progress-lv { color: #1e293b !important; font-family: 'JetBrains Mono', monospace !important; font-weight: 700; }
.progress-bar { background: #e2e8f0; border-radius: 8px; height: 8px; overflow: hidden; }
.progress-fill { height: 100%; border-radius: 8px; transition: width 1s ease; animation: barGrow 1s ease-out; }
@keyframes barGrow { from { width: 0 !important; } }
.pf-purple { background: linear-gradient(90deg,#7c3aed,#a78bfa); }
.pf-green { background: linear-gradient(90deg,#10b981,#34d399); }
.pf-amber { background: linear-gradient(90deg,#f59e0b,#fbbf24); }
.pf-blue { background: linear-gradient(90deg,#3b82f6,#60a5fa); }

/* ============ SERVER STATUS ============ */
.srv {
    display: flex; align-items: center; gap: 12px;
    padding: 12px 16px; background: #fff; border: 1px solid #e2e8f0;
    border-radius: 12px; margin-bottom: 8px; transition: all 0.2s;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.srv:hover { border-color: rgba(109,40,217,0.25); box-shadow: 0 3px 10px rgba(0,0,0,0.06); }
.srv-d { width: 10px; height: 10px; border-radius: 50%; flex-shrink: 0; }
.srv-d-g { background: #10b981; box-shadow: 0 0 8px rgba(16,185,129,0.4); }
.srv-d-o { background: #f59e0b; box-shadow: 0 0 8px rgba(245,158,11,0.4); }
.srv-d-r { background: #ef4444; box-shadow: 0 0 8px rgba(239,68,68,0.4); }
.srv-d-x { background: #94a3b8; }
@keyframes gl { 0%,100%{opacity:1} 50%{opacity:0.5} }
.srv-nm { font-weight: 700; color: #1e293b !important; flex: 1; }
.bdg { padding: 3px 10px; border-radius: 20px; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; }
.bdg-g { background: #dcfce7; color: #16a34a !important; border: 1px solid #bbf7d0; }
.bdg-o { background: #fef3c7; color: #d97706 !important; border: 1px solid #fde68a; }
.bdg-r { background: #fee2e2; color: #dc2626 !important; border: 1px solid #fecaca; }
.bdg-x { background: #f1f5f9; color: #64748b !important; border: 1px solid #e2e8f0; }

/* ============ APPROVAL META ============ */
.ameta { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 8px; margin-bottom: 16px; }
.am-i { background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 12px; }
.am-k { font-size: 0.65rem; color: #64748b !important; font-weight: 700; text-transform: uppercase; letter-spacing: 0.8px; }
.am-v { color: #1e293b !important; font-weight: 600; margin-top: 3px; font-size: 0.85rem; }

/* ============ SETTINGS ============ */
.sg { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 16px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); transition: border-color 0.3s; }
.sg:hover { border-color: rgba(109,40,217,0.2); }
.sg-t { font-weight: 800; color: #6d28d9 !important; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid #e2e8f0; }
.si { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; font-size: 0.82rem; }
.sk { color: #64748b !important; font-family: 'JetBrains Mono', monospace !important; font-size: 0.78rem; }
.sv { color: #1e293b !important; font-weight: 500; max-width: 55%; text-align: right; word-break: break-all; }
.sv-m { color: #94a3b8 !important; letter-spacing: 3px; }

/* ============ EMPTY STATE ============ */
.empty { text-align: center; padding: 50px 20px; }
.empty-i { font-size: 3rem; margin-bottom: 10px; animation: float 3s ease-in-out infinite; }
.empty-t { font-size: 1.1rem; font-weight: 700; color: #1e293b !important; }
.empty-s { color: #64748b !important; margin-top: 4px; }

/* ============ SIDEBAR STATS ============ */
.sb-s {
    background: #fff; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 10px; margin-bottom: 8px; text-align: center; transition: all 0.3s ease;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.sb-s:hover { border-color: rgba(109,40,217,0.3); }
.sb-n { font-size: 1.3rem; font-weight: 900; font-family: 'JetBrains Mono', monospace !important; color: #6d28d9 !important; }
.sb-l { font-size: 0.62rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; color: #64748b !important; margin-top: 1px; }

/* ============ HEALTH ============ */
.health-label { text-align: center; margin-top: -10px; margin-bottom: 16px; }
.health-text { font-size: 0.8rem; color: #64748b !important; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; }

/* ============ DIVIDER ============ */
.neon-line { height: 1px; margin: 18px 0; background: linear-gradient(90deg, transparent, #c4b5fd, #93c5fd, #c4b5fd, transparent); border: none; }

/* ============ PARTICLES ============ */
.hero-particles { position: absolute; top: 0; left: 0; width: 100%; height: 100%; overflow: hidden; z-index: 0; pointer-events: none; }
.hero-particles .dot { position: absolute; width: 3px; height: 3px; border-radius: 50%; background: rgba(255,255,255,0.3); animation: drift linear infinite; }
@keyframes drift { 0%{transform:translateY(100%) translateX(0);opacity:0} 10%{opacity:1} 90%{opacity:1} 100%{transform:translateY(-100%) translateX(40px);opacity:0} }

/* ============ SEARCH ============ */
.search-hit { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 14px 18px; margin-bottom: 8px; transition: all 0.3s; cursor: default; box-shadow: 0 1px 2px rgba(0,0,0,0.04); }
.search-hit:hover { border-color: rgba(109,40,217,0.3); box-shadow: 0 3px 12px rgba(0,0,0,0.06); transform: translateY(-1px); }
.search-hit-title { font-weight: 700; color: #1e293b !important; font-size: 0.9rem; }
.search-hit-dir { display: inline-block; background: #ede9fe; color: #6d28d9 !important; padding: 2px 10px; border-radius: 8px; font-size: 0.68rem; font-weight: 600; margin-left: 8px; }
.search-hit-snippet { color: #64748b !important; font-size: 0.82rem; margin-top: 6px; line-height: 1.5; }
.search-hit-snippet mark { background: #fef9c3; color: #a16207 !important; padding: 1px 3px; border-radius: 3px; font-weight: 600; }

/* ============ RISK ============ */
.risk-high { background: #fef2f2; border-left: 3px solid #ef4444; padding-left: 12px; }
.risk-medium { background: #fffbeb; border-left: 3px solid #f59e0b; padding-left: 12px; }
.risk-low { background: #f0fdf4; border-left: 3px solid #10b981; padding-left: 12px; }
.risk-badge { padding: 3px 10px; border-radius: 8px; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; }
.risk-badge-high { background: #fee2e2; color: #dc2626 !important; }
.risk-badge-medium { background: #fef3c7; color: #d97706 !important; }
.risk-badge-low { background: #dcfce7; color: #16a34a !important; }

/* ============ REPORT / FILE / UPLOAD ============ */
.report-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 12px; padding: 12px 16px; margin-bottom: 8px; transition: all 0.3s; box-shadow: 0 1px 2px rgba(0,0,0,0.04); cursor: default; }
.report-card:hover { border-color: rgba(109,40,217,0.25); transform: translateY(-1px); }
.report-card-title { font-weight: 700; color: #1e293b !important; font-size: 0.88rem; }
.report-card-date { font-size: 0.7rem; color: #64748b !important; margin-top: 2px; }

.file-card { background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 10px 14px; margin-bottom: 6px; transition: all 0.2s; display: flex; align-items: center; gap: 10px; }
.file-card:hover { background: #f5f3ff; border-color: rgba(109,40,217,0.2); }
.file-card-icon { font-size: 1.1rem; }
.file-card-name { font-weight: 600; color: #1e293b !important; font-size: 0.85rem; flex: 1; }

.upload-zone { background: #faf5ff; border: 2px dashed rgba(109,40,217,0.25); border-radius: 16px; padding: 20px 16px; text-align: center; transition: all 0.3s; }
.upload-zone:hover { border-color: rgba(109,40,217,0.5); background: #f5f3ff; box-shadow: 0 0 20px rgba(109,40,217,0.06); }
.upload-zone-icon { font-size: 1.8rem; margin-bottom: 4px; animation: float 3s ease-in-out infinite; }
.upload-zone-title { font-size: 0.9rem; font-weight: 700; color: #1e293b !important; margin-bottom: 2px; }
.upload-zone-desc { font-size: 0.7rem; color: #64748b !important; }
.upload-zone-hint { display: inline-block; margin-top: 6px; background: #ede9fe; color: #6d28d9 !important; padding: 2px 10px; border-radius: 8px; font-size: 0.65rem; font-weight: 600; }

/* Hide Streamlit 200MB label */
[data-testid="stFileUploader"] > section > div:first-child { display: none !important; }
[data-testid="stFileUploader"] label { display: none !important; }
[data-testid="stFileUploader"] small { display: none !important; }
[data-testid="stFileUploaderDropzone"] { background: #faf5ff !important; border: 1px dashed rgba(109,40,217,0.2) !important; border-radius: 12px !important; padding: 14px 10px !important; }
[data-testid="stFileUploaderDropzone"]:hover { border-color: rgba(109,40,217,0.4) !important; background: #f5f3ff !important; }
[data-testid="stFileUploaderDropzone"] span { color: #64748b !important; font-size: 0.75rem !important; }
[data-testid="stFileUploader"] [data-testid="stMarkdownContainer"] p { font-size: 0.72rem !important; color: #94a3b8 !important; }

/* ============ COMMAND CENTER (Create & Upload) ============ */
.cmd-center {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 16px;
    padding: 0; overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    transition: all 0.3s ease;
}
.cmd-center:hover { box-shadow: 0 4px 20px rgba(109,40,217,0.08); border-color: #c4b5fd; }
.cmd-header {
    background: linear-gradient(135deg, #6d28d9, #4f46e5);
    padding: 16px 20px; display: flex; align-items: center; gap: 12px;
}
.cmd-header-icon {
    width: 40px; height: 40px; background: rgba(255,255,255,0.2);
    border-radius: 12px; display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
}
.cmd-header-text { flex: 1; }
.cmd-header-title { font-size: 0.95rem; font-weight: 800; color: #fff !important; }
.cmd-header-desc { font-size: 0.7rem; color: rgba(255,255,255,0.75) !important; margin-top: 1px; }
.cmd-body { padding: 18px 20px; }
.cmd-stat { display: flex; gap: 8px; margin-bottom: 14px; }
.cmd-stat-item {
    flex: 1; background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 8px; text-align: center;
}
.cmd-stat-n { font-size: 1rem; font-weight: 900; font-family: 'JetBrains Mono', monospace !important; color: #6d28d9 !important; }
.cmd-stat-l { font-size: 0.58rem; color: #64748b !important; text-transform: uppercase; font-weight: 700; letter-spacing: 0.5px; }

/* Upload panel */
.upload-panel {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 16px;
    overflow: hidden; box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    transition: all 0.3s ease;
}
.upload-panel:hover { box-shadow: 0 4px 20px rgba(109,40,217,0.08); border-color: #c4b5fd; }
.upload-header {
    background: linear-gradient(135deg, #2563eb, #0891b2);
    padding: 16px 20px; display: flex; align-items: center; gap: 12px;
}
.upload-header-icon {
    width: 40px; height: 40px; background: rgba(255,255,255,0.2);
    border-radius: 12px; display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem;
}
.upload-header-text { flex: 1; }
.upload-header-title { font-size: 0.95rem; font-weight: 800; color: #fff !important; }
.upload-header-desc { font-size: 0.7rem; color: rgba(255,255,255,0.75) !important; margin-top: 1px; }
.upload-body { padding: 18px 20px; }
.upload-drop {
    border: 2px dashed #c4b5fd; border-radius: 14px; padding: 28px 16px;
    text-align: center; background: #faf5ff; transition: all 0.3s;
    cursor: pointer;
}
.upload-drop:hover { border-color: #6d28d9; background: #f5f3ff; }
.upload-drop-icon { font-size: 2.5rem; margin-bottom: 6px; animation: float 3s ease-in-out infinite; }
.upload-drop-title { font-size: 0.88rem; font-weight: 700; color: #1e293b !important; }
.upload-drop-sub { font-size: 0.7rem; color: #64748b !important; margin-top: 2px; }
.upload-formats {
    display: flex; gap: 6px; justify-content: center; margin-top: 10px;
}
.upload-fmt {
    background: #ede9fe; color: #6d28d9 !important; font-size: 0.6rem; font-weight: 700;
    padding: 2px 10px; border-radius: 6px; text-transform: uppercase;
}
.upload-or {
    display: flex; align-items: center; gap: 10px; margin: 14px 0;
}
.upload-or-line { flex: 1; height: 1px; background: #e2e8f0; }
.upload-or-text { color: #94a3b8 !important; font-size: 0.72rem; font-weight: 600; }

/* Quick template buttons */
.quick-templates { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: 12px; }
.qt-btn {
    background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px;
    padding: 6px 12px; font-size: 0.7rem; font-weight: 600; color: #475569 !important;
    transition: all 0.2s; cursor: pointer; display: inline-flex; align-items: center; gap: 4px;
}
.qt-btn:hover { background: #ede9fe; border-color: #c4b5fd; color: #6d28d9 !important; }

/* Keep old classes for backward compat */
.create-card { display: none; }
.upload-zone { display: none; }

.task-preview-header { display: flex; align-items: center; gap: 10px; padding-bottom: 12px; margin-bottom: 12px; border-bottom: 1px solid #e2e8f0; }
.task-preview-icon { font-size: 1.3rem; }
.task-preview-name { font-size: 1rem; font-weight: 700; color: #1e293b !important; flex: 1; }
.task-preview-badge { padding: 3px 10px; border-radius: 8px; font-size: 0.68rem; font-weight: 700; text-transform: uppercase; }
.tpb-inbox { background: #dbeafe; color: #2563eb !important; }
.tpb-needs_action { background: #ffedd5; color: #ea580c !important; }
.tpb-pending_approval { background: #fef9c3; color: #a16207 !important; }
.tpb-approved { background: #ede9fe; color: #7c3aed !important; }
.tpb-done { background: #dcfce7; color: #16a34a !important; }
.tpb-rejected { background: #fee2e2; color: #dc2626 !important; }

/* ============ TASK LIST ITEM (beautiful) ============ */
.task-item {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 14px 16px; margin-bottom: 8px; display: flex; align-items: center; gap: 12px;
    transition: all 0.25s cubic-bezier(0.4,0,0.2,1); cursor: default;
    box-shadow: 0 1px 2px rgba(0,0,0,0.03);
}
.task-item:hover { border-color: #c4b5fd; transform: translateX(4px); box-shadow: 0 4px 16px rgba(109,40,217,0.08); }
.task-item-icon {
    width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center;
    justify-content: center; font-size: 1.1rem; flex-shrink: 0;
}
.ti-inbox { background: #dbeafe; }
.ti-action { background: #ffedd5; }
.ti-pending { background: #fef9c3; }
.ti-approved { background: #ede9fe; }
.ti-done { background: #dcfce7; }
.ti-rejected { background: #fee2e2; }
.task-item-info { flex: 1; min-width: 0; }
.task-item-name { font-weight: 700; color: #1e293b !important; font-size: 0.85rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.task-item-meta { font-size: 0.68rem; color: #94a3b8 !important; margin-top: 2px; display: flex; gap: 6px; align-items: center; }
.task-item-cat {
    font-size: 0.6rem; font-weight: 700; padding: 1px 8px; border-radius: 6px;
    text-transform: uppercase; letter-spacing: 0.5px; flex-shrink: 0;
}
.tc-email { background: #dbeafe; color: #2563eb !important; }
.tc-linkedin { background: #dbeafe; color: #1d4ed8 !important; }
.tc-facebook { background: #dbeafe; color: #1d4ed8 !important; }
.tc-instagram { background: #fce7f3; color: #be185d !important; }
.tc-twitter { background: #e0f2fe; color: #0284c7 !important; }
.tc-whatsapp { background: #dcfce7; color: #16a34a !important; }
.tc-odoo { background: #fef3c7; color: #a16207 !important; }
.tc-social { background: #f3e8ff; color: #7c3aed !important; }
.tc-general { background: #f1f5f9; color: #475569 !important; }
.tc-other { background: #f1f5f9; color: #64748b !important; }

/* Task detail panel */
.task-detail {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 14px;
    padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* ============ BUTTONS / INPUTS / TABS ============ */
.stButton > button { border-radius: 10px !important; font-weight: 700 !important; transition: all 0.2s ease !important; }
.stButton > button:hover { transform: translateY(-1px) !important; }
.stTextInput > div > div > input, .stTextArea > div > div > textarea {
    background: #fff !important; border: 1px solid #e2e8f0 !important;
    border-radius: 10px !important; color: #1e293b !important;
    font-family: 'Inter', sans-serif !important; transition: border-color 0.3s !important;
}
.stTextInput > div > div > input:focus, .stTextArea > div > div > textarea:focus {
    border-color: rgba(109,40,217,0.4) !important; box-shadow: 0 0 10px rgba(109,40,217,0.08) !important;
}
.stTabs [data-baseweb="tab-list"] { gap: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px !important; padding: 8px 14px !important; font-weight: 600 !important; }
.stTabs [aria-selected="true"] { background: #ede9fe !important; border-bottom: 2px solid #6d28d9 !important; color: #6d28d9 !important; }

/* ============ AUTH LOGIN ============ */
.login-box { max-width: 400px; margin: 80px auto; padding: 36px; background: #fff; border: 1px solid #e2e8f0; border-radius: 20px; text-align: center; box-shadow: 0 4px 24px rgba(0,0,0,0.06); }
.login-logo { font-size: 3.5rem; margin-bottom: 8px; animation: float 3s ease-in-out infinite; }
.login-title { font-size: 1.4rem; font-weight: 800; color: #1e293b !important; margin-bottom: 4px; }
.login-sub { color: #64748b !important; font-size: 0.82rem; margin-bottom: 20px; }

/* ============ TIMELINE ============ */
.timeline { position: relative; padding-left: 28px; }
.timeline::before { content: ''; position: absolute; left: 10px; top: 0; bottom: 0; width: 2px; background: linear-gradient(180deg,#6d28d9,#2563eb,#10b981); border-radius: 2px; }
.tl-item { position: relative; margin-bottom: 12px; padding: 10px 14px; background: #fff; border: 1px solid #e2e8f0; border-radius: 10px; transition: all 0.3s; }
.tl-item:hover { border-color: rgba(109,40,217,0.25); transform: translateX(3px); box-shadow: 0 2px 8px rgba(0,0,0,0.04); }
.tl-dot { position: absolute; left: -23px; top: 14px; width: 10px; height: 10px; border-radius: 50%; border: 2px solid #fff; }
.tl-dot-inbox { background: #3b82f6; } .tl-dot-action { background: #f97316; }
.tl-dot-approval { background: #eab308; } .tl-dot-done { background: #10b981; } .tl-dot-rejected { background: #ef4444; }
.tl-title { font-weight: 700; color: #1e293b !important; font-size: 0.85rem; }
.tl-meta { font-size: 0.7rem; color: #64748b !important; margin-top: 2px; }

/* ============ WATCHER STATUS (FIXED - clean grid) ============ */
.watcher-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 12px; margin-bottom: 14px; }
.watcher-card {
    background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 16px; text-align: center;
    transition: all 0.3s; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.watcher-card:hover { border-color: rgba(109,40,217,0.25); transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
.watcher-icon { font-size: 1.6rem; margin-bottom: 4px; }
.watcher-name { font-weight: 700; color: #1e293b !important; font-size: 0.85rem; }
.watcher-status { font-size: 0.68rem; font-weight: 700; text-transform: uppercase; margin-top: 6px; padding: 2px 10px; border-radius: 8px; display: inline-block; }
.ws-active { background: #dcfce7; color: #16a34a !important; }
.ws-inactive { background: #f1f5f9; color: #94a3b8 !important; }
.ws-cloud { background: #cffafe; color: #0e7490 !important; }
.ws-local { background: #fef3c7; color: #d97706 !important; }

/* ============ SCHEDULER (FIXED - clean cards) ============ */
.sched-card {
    background: #fff; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 14px 16px; margin-bottom: 8px;
    display: flex; align-items: center; gap: 14px;
    transition: all 0.3s; box-shadow: 0 1px 3px rgba(0,0,0,0.04);
}
.sched-card:hover { border-color: rgba(109,40,217,0.25); box-shadow: 0 3px 10px rgba(0,0,0,0.06); }
.sched-icon { font-size: 1.5rem; }
.sched-info { flex: 1; }
.sched-name { font-weight: 700; color: #1e293b !important; font-size: 0.85rem; }
.sched-detail { font-size: 0.72rem; color: #64748b !important; margin-top: 2px; }
.sched-next { font-size: 0.72rem; font-weight: 600; padding: 3px 10px; border-radius: 8px; background: #ede9fe; color: #6d28d9 !important; white-space: nowrap; }

/* ============ SOCIAL ============ */
.social-card { background: #fff; border-radius: 14px; padding: 16px; border: 1px solid #e2e8f0; transition: all 0.3s; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
.social-card:hover { transform: translateY(-2px); border-color: var(--social-color, #6d28d9); box-shadow: 0 4px 12px rgba(0,0,0,0.06); }
.social-icon { font-size: 1.8rem; margin-bottom: 6px; }
.social-name { font-weight: 800; font-size: 0.9rem; color: #1e293b !important; margin-bottom: 3px; }
.social-stat { font-size: 0.72rem; color: #64748b !important; }
.social-linkedin { --social-color: #0a66c2; } .social-facebook { --social-color: #1877f2; }
.social-twitter { --social-color: #1da1f2; } .social-instagram { --social-color: #e4405f; } .social-whatsapp { --social-color: #25d366; }

/* ============ BADGES ============ */
.domain-personal { background: #dbeafe; color: #2563eb !important; padding: 2px 10px; border-radius: 8px; font-size: 0.68rem; font-weight: 600; }
.domain-business { background: #dcfce7; color: #16a34a !important; padding: 2px 10px; border-radius: 8px; font-size: 0.68rem; font-weight: 600; }
.domain-cross { background: #fef3c7; color: #d97706 !important; padding: 2px 10px; border-radius: 8px; font-size: 0.68rem; font-weight: 600; }
.pri-urgent { background: #fee2e2; color: #dc2626 !important; padding: 2px 10px; border-radius: 8px; font-size: 0.68rem; font-weight: 700; }
.pri-high { background: #ffedd5; color: #ea580c !important; padding: 2px 10px; border-radius: 8px; font-size: 0.68rem; font-weight: 700; }
.pri-normal { background: #dbeafe; color: #2563eb !important; padding: 2px 10px; border-radius: 8px; font-size: 0.68rem; font-weight: 700; }
.pri-low { background: #f1f5f9; color: #64748b !important; padding: 2px 10px; border-radius: 8px; font-size: 0.68rem; font-weight: 700; }
.tab-badge { display: inline-flex; align-items: center; justify-content: center; background: #ede9fe; color: #6d28d9 !important; min-width: 20px; height: 20px; border-radius: 10px; font-size: 0.68rem; font-weight: 700; padding: 0 6px; margin-left: 6px; }

/* ============ FOOTER ============ */
.footer { text-align: center; padding: 16px 0 8px; border-top: 1px solid #e2e8f0; margin-top: 30px; }
.footer-text { font-size: 0.72rem; color: #94a3b8 !important; font-weight: 500; }
.footer-brand { font-weight: 700; background: linear-gradient(135deg,#6d28d9,#2563eb); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }

/* ============ MOBILE ============ */
@media (max-width: 768px) {
    .kpi-row, .tier-row, .stat-row, .watcher-grid { flex-direction: column; grid-template-columns: 1fr; }
    .kpi, .tier-card, .stat-card, .watcher-card { min-width: 100% !important; }
    .hero { padding: 18px 14px; } .hero-t { font-size: 1.1rem; }
    .glass, .sg { padding: 14px; } .ameta { grid-template-columns: 1fr !important; }
}
@media (max-width: 480px) { .kpi-n { font-size: 1.3rem; } .hero-t { font-size: 1rem; } }
</style>
""", unsafe_allow_html=True)


# ===================================================================
# Authentication
# ===================================================================

def _check_auth():
    """Simple session-based authentication."""
    if st.session_state.get("authenticated"):
        return True
    st.markdown(
        '<div class="login-box">'
        '<div class="login-logo">🤖</div>'
        '<div class="login-title">AI Employee</div>'
        '<div class="login-sub">Enter credentials to access the dashboard</div>'
        '</div>', unsafe_allow_html=True
    )
    with st.form("login_form"):
        user = st.text_input("Username", placeholder="Enter username...")
        pwd = st.text_input("Password", type="password", placeholder="Enter password...")
        if st.form_submit_button("Login", type="primary", use_container_width=True):
            pwd_hash = hashlib.sha256(pwd.encode()).hexdigest()
            if user == _AUTH_USER and pwd_hash == _AUTH_PASS_HASH:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Invalid credentials. Default: admin / admin")
    return False


if not _check_auth():
    st.stop()


# ===================================================================
# Helpers (with caching)
# ===================================================================

@st.cache_data(ttl=10)
def get_vault_counts():
    counts = {}
    for key, dirname in VAULT_DIRS.items():
        d = VAULT / dirname
        counts[key] = len(list(d.glob("*.md"))) if d.exists() else 0
    return counts

def list_md_files(dirname):
    d = VAULT / dirname
    return sorted(d.glob("*.md")) if d.exists() else []

def read_file(path):
    try: return path.read_text(encoding="utf-8")
    except OSError: return ""

def load_log(log_date):
    p = VAULT / "Logs" / f"{log_date.isoformat()}.json"
    if not p.exists(): return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError): return []

def available_log_dates():
    d = VAULT / "Logs"
    if not d.exists(): return []
    dates = []
    for f in sorted(d.glob("*.json"), reverse=True):
        try: dates.append(date.fromisoformat(f.stem))
        except ValueError: pass
    return dates

@st.cache_data(ttl=10)
def load_integration_status():
    p = VAULT / "Business" / "integration_status.json"
    if not p.exists(): return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data.get("servers", {})
    except (json.JSONDecodeError, OSError): return {}

def parse_retry_queue():
    p = VAULT / "Business" / "retry_queue.md"
    if not p.exists(): return []
    content = read_file(p)
    if not content.strip(): return []
    sections = re.split(r"(?=## Retry:)", content)
    entries = []
    for sec in sections:
        sec = sec.strip()
        if not sec.startswith("## Retry:"): continue
        def _ex(lbl):
            m = re.search(rf"\*\*{lbl}\*\*:\s*(.+)", sec)
            return m.group(1).strip() if m else ""
        eid = re.search(r"## Retry:\s*(.+)", sec)
        entries.append({"id": eid.group(1).strip() if eid else "", "operation": _ex("Operation"), "mcp_server": _ex("MCP Server"), "retry_count": _ex("Retry Count"), "status": _ex("Status") or "queued", "error": _ex("Error"), "next_retry": _ex("Next Retry After")})
    return entries

def parse_frontmatter(text):
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            try: meta = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError: meta = {}
            return meta, parts[2].strip()
    return {}, text

def move_file(src, dest_dir_name):
    dest_dir = VAULT / dest_dir_name
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name
    if dest.exists():
        stem, suffix = src.stem, src.suffix
        dest = dest_dir / f"{stem}_{int(datetime.now().timestamp())}{suffix}"
    src.rename(dest)
    return dest

def is_sensitive(key):
    return any(p in key.upper() for p in _SENSITIVE_PATTERNS)

def search_vault(query):
    results = []
    q = query.lower()
    for dirname in VAULT_DIRS.values():
        d = VAULT / dirname
        if not d.exists(): continue
        for f in d.glob("*.md"):
            content = read_file(f)
            if q in f.name.lower() or q in content.lower():
                snippet = ""
                idx = content.lower().find(q)
                if idx >= 0:
                    s, e = max(0, idx - 40), min(len(content), idx + len(query) + 40)
                    snippet = "..." + content[s:e].replace("\n", " ") + "..."
                results.append({"file": f.name, "dir": dirname, "path": str(f), "snippet": snippet})
    return results

def get_all_logs_flat(days=30):
    entries = []
    for i in range(days):
        d = date.today() - timedelta(days=i)
        for e in load_log(d):
            e["_date"] = d.isoformat()
            entries.append(e)
    return entries

def compute_health_score():
    score = 100
    counts = get_vault_counts()
    score -= min(counts.get("pending_approval", 0) * 5, 20)
    score -= min(counts.get("needs_action", 0) * 3, 15)
    servers = load_integration_status()
    for info in servers.values():
        s = info.get("status", "unknown")
        if s == "degraded": score -= 10
        elif s == "unavailable": score -= 20
    score -= min(len(parse_retry_queue()) * 5, 15)
    return max(0, min(100, score))

def _get_active_tiers():
    gold = CONFIG.get("GOLD_TIER_ENABLED", False)
    platinum = CONFIG.get("DEPLOYMENT_MODE", "local") == "cloud"
    return {"bronze": True, "silver": True, "gold": gold, "platinum": platinum}

def get_greeting():
    h = datetime.now().hour
    if h < 12: return "Good Morning"
    elif h < 17: return "Good Afternoon"
    elif h < 21: return "Good Evening"
    else: return "Good Night"

def _esc(text):
    """HTML-escape user content to prevent XSS."""
    return html_mod.escape(str(text)) if text else ""

def list_plans():
    d = VAULT / "Plans"
    return sorted(d.glob("*.md"), reverse=True) if d.exists() else []

@st.cache_data(ttl=10)
def load_scheduler_state():
    p = VAULT / "Business" / "scheduler_state.json"
    if not p.exists(): return {}
    try: return json.loads(p.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError): return {}

def load_social_posts():
    """Scan Done/ for social media related tasks."""
    posts = []
    for d_name in ("Done", "Needs_Action", "Pending_Approval", "Approved"):
        d = VAULT / d_name
        if not d.exists(): continue
        for f in d.glob("*.md"):
            name_lower = f.stem.lower()
            for platform in ("linkedin", "facebook", "twitter", "instagram", "whatsapp"):
                if platform in name_lower:
                    meta, body = parse_frontmatter(read_file(f))
                    posts.append({"file": f.name, "platform": platform, "dir": d_name,
                                  "priority": meta.get("priority", "normal"),
                                  "domain": meta.get("domain", "business"), "path": str(f)})
                    break
    return posts

def load_accounting_files():
    """Load accounting-related files from Business/Accounting/."""
    d = VAULT / "Business" / "Accounting"
    if not d.exists(): return []
    files = []
    for f in sorted(d.glob("*.md"), reverse=True):
        meta, body = parse_frontmatter(read_file(f))
        files.append({"file": f.name, "meta": meta, "body": body, "path": str(f)})
    return files

def get_domain_stats():
    """Count tasks by domain from frontmatter."""
    stats = {"personal": 0, "business": 0, "cross-domain": 0, "unknown": 0}
    for d_name in VAULT_DIRS.values():
        d = VAULT / d_name
        if not d.exists(): continue
        for f in d.glob("*.md"):
            meta, _ = parse_frontmatter(read_file(f))
            domain = str(meta.get("domain", "unknown")).lower()
            if domain in stats: stats[domain] += 1
            else: stats["unknown"] += 1
    return stats

def get_priority_stats():
    """Count tasks by priority from frontmatter."""
    stats = {"urgent": 0, "high": 0, "normal": 0, "medium": 0, "low": 0}
    for d_name in VAULT_DIRS.values():
        d = VAULT / d_name
        if not d.exists(): continue
        for f in d.glob("*.md"):
            meta, _ = parse_frontmatter(read_file(f))
            pri = str(meta.get("priority", "normal")).lower()
            if pri in stats: stats[pri] += 1
            else: stats["normal"] += 1
    return stats

def get_watcher_info():
    """Return watcher definitions with status based on config."""
    is_cloud = CONFIG.get("DEPLOYMENT_MODE", "local") == "cloud"
    return [
        {"name": "File System", "icon": "📁", "location": "cloud" if is_cloud else "local",
         "active": True, "desc": "Monitors vault directories for changes"},
        {"name": "Gmail", "icon": "📧", "location": "cloud" if is_cloud else "local",
         "active": bool(CONFIG.get("GOOGLE_APPLICATION_CREDENTIALS")),
         "desc": "OAuth2 Gmail API polling"},
        {"name": "LinkedIn", "icon": "💼", "location": "cloud" if is_cloud else "local",
         "active": bool(CONFIG.get("LINKEDIN_ACCESS_TOKEN")),
         "desc": "LinkedIn REST API monitoring"},
        {"name": "WhatsApp", "icon": "💬", "location": "local",
         "active": CONFIG.get("WHATSAPP_MODE") in ("playwright", "api"),
         "desc": f"Mode: {CONFIG.get('WHATSAPP_MODE', 'off')}"},
    ]


# ===================================================================
# Reusable render functions
# ===================================================================

def render_kpis(counts):
    cards = [
        ("inbox","kpi-blue","📥","Inbox"), ("needs_action","kpi-orange","⚡","Needs Action"),
        ("pending_approval","kpi-amber","⏳","Pending"), ("approved","kpi-purple","✅","Approved"),
        ("done","kpi-green","🏆","Done"), ("rejected","kpi-red","❌","Rejected"),
    ]
    h = '<div class="kpi-row">'
    for key, cls, em, lbl in cards:
        v = counts.get(key, 0)
        h += f'<div class="kpi {cls}"><div class="kpi-bar"></div><div class="kpi-em">{em}</div><div class="kpi-n">{v}</div><div class="kpi-l">{lbl}</div></div>'
    h += '</div>'
    st.markdown(h, unsafe_allow_html=True)

def render_tier_cards():
    tiers_active = _get_active_tiers()
    tiers = [
        ("bronze", "🥉", "Bronze", "File watcher, vault processing, dashboard",
         ["File monitoring", "Dashboard updates", "Vault processing", "Markdown workflow"]),
        ("silver", "🥈", "Silver", "HITL approval, MCP servers, audit logs",
         ["Human-in-the-loop", "MCP integration", "Multi-watchers", "JSON audit logs"]),
        ("gold", "🥇", "Gold", "Autonomous processing, 7 integrations",
         ["Priority classification", "Domain routing", "Auto-approval", "Retry queue",
          "Weekly reports", "Odoo accounting", "Social media (5 platforms)"]),
        ("platinum", "💎", "Platinum", "24/7 cloud, local hybrid, health",
         ["GCP deployment", "Cloud/local split", "Git vault sync", "Health endpoint",
          "PM2 management", "Docker container"]),
    ]
    h = '<div class="tier-row">'
    for key, icon, name, desc, features in tiers:
        active = tiers_active.get(key, False)
        ac = "active" if active else "tier-inactive"
        status = "Active" if active else "Inactive"
        feat_html = "".join(f'<div style="font-size:0.58rem;color:#64748b;padding:1px 0">- {_esc(f)}</div>' for f in features[:4])
        extra = f'<div style="font-size:0.55rem;color:#475569">+{len(features)-4} more</div>' if len(features) > 4 else ""
        h += (f'<div class="tier-card tier-{key} {ac}"><div class="tier-icon">{icon}</div>'
              f'<div class="tier-name">{name}</div><div class="tier-desc">{_esc(desc)}</div>'
              f'{feat_html}{extra}<span class="tier-status">{status}</span></div>')
    h += '</div>'
    st.markdown(h, unsafe_allow_html=True)

def render_health_gauge(score):
    color = "#10b981" if score >= 80 else ("#f59e0b" if score >= 50 else "#ef4444")
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=score,
        number={"suffix": "%", "font": {"size": 44, "family": "JetBrains Mono", "color": color}},
        gauge={"axis": {"range": [0, 100], "tickwidth": 0, "tickcolor": "rgba(0,0,0,0)", "dtick": 25, "tickfont": {"color": "#64748b", "size": 10}},
               "bar": {"color": color, "thickness": 0.3}, "bgcolor": "#1e293b", "borderwidth": 0,
               "steps": [{"range": [0, 50], "color": "rgba(239,68,68,0.08)"}, {"range": [50, 80], "color": "rgba(245,158,11,0.08)"}, {"range": [80, 100], "color": "rgba(16,185,129,0.08)"}],
               "threshold": {"line": {"color": color, "width": 3}, "thickness": 0.8, "value": score}},
    ))
    fig.update_layout(height=190, margin=dict(l=20, r=20, t=25, b=5), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font={"color": "#64748b"})
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    label = "Excellent" if score >= 80 else ("Needs Attention" if score >= 50 else "Critical")
    st.markdown(f'<div class="health-label"><span class="health-text">{label}</span></div>', unsafe_allow_html=True)

def render_footer():
    st.markdown(
        '<div class="footer">'
        '<p class="footer-text">Powered by <span class="footer-brand">AI Employee v1.0</span> &mdash; Personal Automation Hub</p>'
        '</div>',
        unsafe_allow_html=True
    )


# ===================================================================
# Pages
# ===================================================================

def _hero(title, subtitle, particles=False, greeting_text=None):
    dots = ""
    if particles:
        for i in range(12):
            left = random.randint(5, 95)
            dur = round(random.uniform(4, 10), 1)
            delay = round(random.uniform(0, 5), 1)
            size = random.choice([2, 3, 4])
            dots += f'<div class="dot" style="left:{left}%;width:{size}px;height:{size}px;animation-duration:{dur}s;animation-delay:{delay}s"></div>'
    parts = f'<div class="hero">'
    if particles:
        parts += f'<div class="hero-particles">{dots}</div>'
    if greeting_text:
        parts += f'<p class="hero-greeting">{greeting_text}</p>'
    parts += f'<p class="hero-t">{title}</p><p class="hero-s">{subtitle}</p></div>'
    st.markdown(parts, unsafe_allow_html=True)
    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)

def page_dashboard():
  try:
    greeting = get_greeting()
    _hero(
        "🤖 AI Employee Dashboard",
        "Real-time system overview — tasks, approvals, integrations, and health",
        particles=True,
        greeting_text=f"👋 {greeting}!",
    )
    render_tier_cards()
    counts = get_vault_counts()
    render_kpis(counts)

    # Quick stats
    all_logs = get_all_logs_flat(30)
    total_30d = len(all_logs)
    days_data = len({e["_date"] for e in all_logs})
    avg = round(total_30d / max(days_data, 1), 1)
    total_done = counts.get("done", 0)
    total_all = sum(counts.values())
    comp_rate = round(total_done / max(total_all, 1) * 100, 1)
    servers = load_integration_status()
    healthy = sum(1 for s in servers.values() if s.get("status") == "healthy")
    plans_count = len(list_plans())

    st.markdown(
        f'<div class="stat-row">'
        f'<div class="stat-card"><div class="stat-n">{total_30d}</div><div class="stat-l">Actions (30d)</div></div>'
        f'<div class="stat-card"><div class="stat-n">{avg}</div><div class="stat-l">Avg / Day</div></div>'
        f'<div class="stat-card"><div class="stat-n">{comp_rate}%</div><div class="stat-l">Completion</div></div>'
        f'<div class="stat-card"><div class="stat-n">{healthy}/{len(servers)}</div><div class="stat-l">Integrations</div></div>'
        f'<div class="stat-card"><div class="stat-n">{plans_count}</div><div class="stat-l">Plans</div></div>'
        f'</div>', unsafe_allow_html=True
    )

    # Charts row
    ch1, ch2, ch3 = st.columns([2, 2, 1.5], gap="large")
    with ch1:
        history = []
        for i in range(13, -1, -1):
            d = date.today() - timedelta(days=i)
            history.append({"Date": d.strftime("%b %d"), "Actions": len(load_log(d))})
        df = pd.DataFrame(history)
        if df["Actions"].sum() > 0:
            fig = px.area(df, x="Date", y="Actions", title="📈 Activity Trend (14 Days)", color_discrete_sequence=["#7c3aed"])
            fig.update_layout(height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=40, b=0), font={"color": "#64748b"}, title_font={"size": 14, "color": "#1e293b"}, xaxis=dict(showgrid=False, color="#64748b"), yaxis=dict(showgrid=True, gridcolor="rgba(51,65,85,0.3)", color="#64748b"))
            fig.update_traces(fill='tozeroy', line_color="#7c3aed", fillcolor="rgba(124,58,237,0.15)")
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No activity data.")
    with ch2:
        pie_data = {k: v for k, v in counts.items() if v > 0}
        if pie_data:
            colors = {"inbox": "#3b82f6", "needs_action": "#f97316", "pending_approval": "#eab308", "approved": "#8b5cf6", "done": "#10b981", "rejected": "#ef4444"}
            labels = {"inbox": "Inbox", "needs_action": "Needs Action", "pending_approval": "Pending", "approved": "Approved", "done": "Done", "rejected": "Rejected"}
            fig = go.Figure(go.Pie(labels=[labels.get(k, k) for k in pie_data], values=list(pie_data.values()), hole=0.55, marker=dict(colors=[colors.get(k, "#64748b") for k in pie_data]), textinfo="label+value", textfont=dict(size=11, color="#1e293b")))
            fig.update_layout(title={"text": "📊 Task Distribution", "font": {"size": 14, "color": "#f1f5f9"}}, height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", margin=dict(l=0, r=0, t=40, b=0), font={"color": "#64748b"}, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No tasks.")
    with ch3:
        st.markdown("##### 🩺 System Health")
        render_health_gauge(compute_health_score())

    # Activity + Progress + Watcher/Scheduler
    col_l, col_r = st.columns([3, 2], gap="large")
    with col_l:
        st.markdown("#### 📋 Recent Activity")
        logs = load_log(date.today())
        if logs:
            for entry in reversed(logs[-8:]):
                ts = entry.get("timestamp", ""); ts = ts.split("T")[1][:8] if "T" in ts else ts
                action = _esc(entry.get("action_type", entry.get("action", "unknown")))
                result = _esc(entry.get("result", "done"))
                is_ok = result in ("success", "done", "approved")
                dot = "act-d-ok" if is_ok else ("act-d-er" if result in ("error","failed") else "act-d-n")
                bcls = "act-bg-ok" if is_ok else "act-bg-er"
                st.markdown(f'<div class="act"><div class="act-d {dot}"></div><div class="act-b"><div class="act-a">{action}<span class="act-bg {bcls}">{result}</span></div><div class="act-m">🕐 {ts}</div></div></div>', unsafe_allow_html=True)
        else:
            st.info("No activity today.")
    with col_r:
        st.markdown("#### 📊 Progress")
        pct_done = round(total_done / max(total_all, 1) * 100)
        pending_pct = round(counts.get("pending_approval", 0) / max(total_all, 1) * 100)
        inbox_pct = round(counts.get("inbox", 0) / max(total_all, 1) * 100)
        approved_pct = round(counts.get("approved", 0) / max(total_all, 1) * 100)
        for label, val, pct, color in [("Completed", f"{pct_done}%", pct_done, "pf-green"), ("Pending Approval", f"{pending_pct}%", pending_pct, "pf-amber"), ("In Inbox", f"{inbox_pct}%", inbox_pct, "pf-blue"), ("Approved", f"{approved_pct}%", approved_pct, "pf-purple")]:
            st.markdown(f'<div class="progress-wrap"><div class="progress-label"><span class="progress-lk">{label}</span><span class="progress-lv">{val}</span></div><div class="progress-bar"><div class="progress-fill {color}" style="width:{pct}%"></div></div></div>', unsafe_allow_html=True)

        tiers = _get_active_tiers()
        tier_str = " → ".join(n.title() for n, v in tiers.items() if v)
        dry = "✅ Yes" if CONFIG.get("DRY_RUN") else "❌ No"
        mode = CONFIG.get("DEPLOYMENT_MODE", "local").title()
        h = '<div class="glass"><h4>⚙️ Configuration</h4>'
        for k, v in [("Active Tiers", tier_str), ("Mode", f"🌐 {mode}"), ("Dry Run", dry), ("Auto-Approve", "✅" if CONFIG.get("AUTO_APPROVE_LOW_RISK") else "❌")]:
            h += f'<div class="irow"><span class="ik">{_esc(k)}</span><span class="iv">{_esc(v)}</span></div>'
        h += '</div>'
        st.markdown(h, unsafe_allow_html=True)

    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)

    # Watcher Status + Scheduler Status
    st.markdown("#### 📡 Watchers & Scheduler")
    w1, w2 = st.columns(2, gap="large")
    with w1:
        watchers = get_watcher_info()
        wh = '<div class="watcher-grid">'
        for w in watchers:
            status_cls = "ws-active" if w["active"] else "ws-inactive"
            loc_cls = "ws-cloud" if w["location"] == "cloud" else "ws-local"
            wh += (f'<div class="watcher-card"><div class="watcher-icon">{w["icon"]}</div>'
                   f'<div class="watcher-name">{_esc(w["name"])}</div>'
                   f'<div style="font-size:0.68rem;color:#64748b;margin:4px 0">{_esc(w["desc"])}</div>'
                   f'<span class="watcher-status {status_cls}">{"Online" if w["active"] else "Offline"}</span> '
                   f'<span class="watcher-status {loc_cls}">{_esc(w["location"])}</span></div>')
        wh += '</div>'
        st.markdown(wh, unsafe_allow_html=True)

    with w2:
        sched = load_scheduler_state()
        if sched:
            for sname, sdata in sched.items():
                icon = "📊" if "audit" in sname else "📋"
                status = _esc(sdata.get("status", "unknown"))
                last_run = sdata.get("last_run", "Never")
                if isinstance(last_run, str) and "T" in last_run:
                    last_run = last_run.split("T")[0]
                next_run = sdata.get("next_run", "Not scheduled")
                if isinstance(next_run, str) and "T" in next_run:
                    next_run = next_run.split("T")[0]
                st.markdown(
                    f'<div class="sched-card"><div class="sched-icon">{icon}</div>'
                    f'<div class="sched-info"><div class="sched-name">{_esc(sname.replace("_"," ").title())}</div>'
                    f'<div class="sched-detail">Last: {_esc(last_run)} | Status: {status}</div></div>'
                    f'<span class="sched-next">Next: {_esc(next_run)}</span></div>',
                    unsafe_allow_html=True)
        else:
            st.info("No scheduler data yet. Runs in Gold tier.")

    # Domain & Priority breakdown
    d1, d2 = st.columns(2, gap="large")
    with d1:
        st.markdown("#### 🏷️ Domain Distribution")
        domain_stats = get_domain_stats()
        domain_data = {k: v for k, v in domain_stats.items() if v > 0}
        if domain_data:
            d_colors = {"personal": "#3b82f6", "business": "#10b981", "cross-domain": "#f59e0b", "unknown": "#64748b"}
            fig = go.Figure(go.Pie(
                labels=[k.title() for k in domain_data],
                values=list(domain_data.values()), hole=0.5,
                marker=dict(colors=[d_colors.get(k, "#64748b") for k in domain_data]),
                textinfo="label+value", textfont=dict(size=11, color="#1e293b")))
            fig.update_layout(height=220, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              margin=dict(l=0, r=0, t=10, b=0), font={"color": "#64748b"}, showlegend=False)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No domain data available.")
    with d2:
        st.markdown("#### ⚡ Priority Distribution")
        pri_stats = get_priority_stats()
        pri_data = {k: v for k, v in pri_stats.items() if v > 0}
        if pri_data:
            p_colors = {"urgent": "#ef4444", "high": "#f97316", "normal": "#3b82f6", "medium": "#eab308", "low": "#64748b"}
            fig = go.Figure(go.Bar(
                x=[k.title() for k in pri_data], y=list(pri_data.values()),
                marker_color=[p_colors.get(k, "#64748b") for k in pri_data],
                text=list(pri_data.values()), textposition="outside",
                textfont=dict(color="#1e293b", size=12)))
            fig.update_layout(height=220, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                              margin=dict(l=0, r=0, t=10, b=30), font={"color": "#64748b"},
                              xaxis=dict(showgrid=False, color="#64748b"),
                              yaxis=dict(showgrid=True, gridcolor="rgba(51,65,85,0.3)", color="#64748b"))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No priority data available.")

    render_footer()
  except Exception as e:
    st.error(f"Dashboard error: {e}")


def page_tasks():
  try:
    _hero("📋 Task Management", "Browse, view, upload, and create tasks across all stages", particles=True)
    counts = get_vault_counts()

    # ── Summary stats ──
    total = sum(counts.values())
    st.markdown(
        f'<div class="stat-row">'
        f'<div class="stat-card"><div class="stat-n">{total}</div><div class="stat-l">Total Files</div></div>'
        f'<div class="stat-card"><div class="stat-n" style="color:#60a5fa">{counts.get("inbox",0)}</div><div class="stat-l">Inbox</div></div>'
        f'<div class="stat-card"><div class="stat-n" style="color:#fb923c">{counts.get("needs_action",0)}</div><div class="stat-l">Needs Action</div></div>'
        f'<div class="stat-card"><div class="stat-n" style="color:#fbbf24">{counts.get("pending_approval",0)}</div><div class="stat-l">Pending</div></div>'
        f'<div class="stat-card"><div class="stat-n" style="color:#34d399">{counts.get("done",0)}</div><div class="stat-l">Done</div></div>'
        f'</div>', unsafe_allow_html=True
    )

    # ── Priority filter ──
    pf1, pf2 = st.columns([3, 1])
    with pf2:
        pri_filter = st.selectbox("Filter Priority", ["All", "urgent", "high", "medium", "normal", "low"], key="task_pri_filter")

    # ── Tabs with counts (Pending_Approval added) ──
    tab_info = [
        ("Inbox", "📥", "inbox"), ("Needs_Action", "⚡", "needs_action"),
        ("Pending_Approval", "⏳", "pending_approval"),
        ("Approved", "✅", "approved"), ("Done", "🏆", "done"), ("Rejected", "❌", "rejected"),
    ]
    tab_labels = [f"{icon} {dn.replace('_',' ')} ({counts.get(key,0)})" for dn, icon, key in tab_info]
    tabs = st.tabs(tab_labels)
    for tab, (dirname, icon, key) in zip(tabs, tab_info):
        with tab:
            files = list_md_files(dirname)
            if not files:
                st.markdown(
                    f'<div class="empty">'
                    f'<div class="empty-i">📭</div>'
                    f'<div class="empty-t">No {_esc(dirname.replace("_"," "))} Tasks</div>'
                    f'<div class="empty-s">Files moved here will appear automatically</div>'
                    f'</div>', unsafe_allow_html=True)
                continue

            # Priority filter
            if pri_filter != "All":
                files = [f for f in files if str(parse_frontmatter(read_file(f))[0].get("priority", "normal")).lower() == pri_filter]
                if not files:
                    st.info(f"No {pri_filter} priority tasks in {dirname.replace('_',' ')}.")
                    continue

            search_q = st.text_input("🔎 Filter files...", key=f"search_{dirname}", placeholder="Type to filter by name or content...")
            if search_q:
                sq = search_q.lower()
                files = [f for f in files if sq in f.stem.lower() or sq in read_file(f).lower()]
            if not files:
                st.warning("No files match your filter.")
                continue

            # Category icons for beautiful task items
            _cat_icons = {"email": "📧", "linkedin": "💼", "facebook": "📘", "instagram": "📸",
                          "twitter": "🐦", "whatsapp": "💬", "odoo": "🧾", "social": "📱", "general": "📄", "other": "📁"}
            _icon_cls = {"Inbox": "ti-inbox", "Needs_Action": "ti-action", "Pending_Approval": "ti-pending",
                         "Approved": "ti-approved", "Done": "ti-done", "Rejected": "ti-rejected"}

            fc, pc = st.columns([1.3, 2.7], gap="large")
            with fc:
                st.caption(f"**{len(files)}** file(s)")
                # Render beautiful task item cards as preview
                for f in files:
                    fm, _ = parse_frontmatter(read_file(f))
                    cat = str(fm.get("category", "general")).lower()
                    pri = str(fm.get("priority", "normal")).lower()
                    cat_icon = _cat_icons.get(cat, "📄")
                    icon_bg = _icon_cls.get(dirname, "ti-inbox")
                    cat_cls = f"tc-{cat}" if cat in _cat_icons else "tc-general"
                    mod_short = datetime.fromtimestamp(f.stat().st_mtime).strftime("%b %d") if f.exists() else ""
                    st.markdown(
                        f'<div class="task-item">'
                        f'<div class="task-item-icon {icon_bg}">{cat_icon}</div>'
                        f'<div class="task-item-info">'
                        f'<div class="task-item-name">{_esc(f.stem.replace("_"," "))}</div>'
                        f'<div class="task-item-meta"><span>{_esc(mod_short)}</span>'
                        f'<span class="task-item-cat {cat_cls}">{_esc(cat)}</span></div>'
                        f'</div></div>', unsafe_allow_html=True)
                sel = st.radio("Select", files,
                    format_func=lambda p: p.stem.replace('_', ' '),
                    key=f"t_{dirname}", label_visibility="collapsed")
            with pc:
                if sel:
                    content = read_file(sel)
                    meta, body = parse_frontmatter(content)
                    sz = sel.stat().st_size if sel.exists() else 0
                    sz_str = f"{sz} B" if sz < 1024 else f"{sz/1024:.1f} KB"
                    mod = datetime.fromtimestamp(sel.stat().st_mtime).strftime("%b %d, %Y %I:%M %p") if sel.exists() else ""

                    pri = str(meta.get("priority", "normal")).lower()
                    domain = str(meta.get("domain", "")).lower()
                    cat = str(meta.get("category", "general")).lower()
                    pri_cls = f"pri-{pri}" if pri in ("urgent","high","normal","low") else "pri-normal"
                    domain_cls = f"domain-{domain}" if domain in ("personal","business","cross") else ""
                    cat_cls = f"tc-{cat}" if cat in _cat_icons else "tc-general"
                    cat_icon = _cat_icons.get(cat, "📄")

                    st.markdown(f'<div class="task-detail">', unsafe_allow_html=True)

                    # Header with badges
                    badges = f'<span class="{pri_cls}">{_esc(pri.upper())}</span> '
                    if domain_cls:
                        badges += f'<span class="{domain_cls}">{_esc(domain.upper())}</span> '
                    badges += f'<span class="task-item-cat {cat_cls}">{cat_icon} {_esc(cat.upper())}</span>'

                    st.markdown(
                        f'<div class="task-preview-header">'
                        f'<span class="task-preview-icon">{cat_icon}</span>'
                        f'<span class="task-preview-name">{_esc(sel.stem.replace("_"," "))}</span>'
                        f'<span class="task-preview-badge tpb-{key}">{_esc(dirname.replace("_"," "))}</span>'
                        f'</div>'
                        f'<div style="margin-bottom:12px">{badges}</div>', unsafe_allow_html=True
                    )

                    # File info
                    st.markdown(
                        f'<div class="stat-row" style="margin-bottom:12px">'
                        f'<div class="stat-card" style="padding:8px"><div class="stat-n" style="font-size:0.85rem">{_esc(sz_str)}</div><div class="stat-l">Size</div></div>'
                        f'<div class="stat-card" style="padding:8px"><div class="stat-n" style="font-size:0.85rem">{_esc(mod)}</div><div class="stat-l">Modified</div></div>'
                        f'</div>', unsafe_allow_html=True
                    )

                    if meta:
                        h = '<div class="ameta">'
                        for k, v in meta.items():
                            if isinstance(v, list): v = ", ".join(str(x) for x in v)
                            h += f'<div class="am-i"><div class="am-k">{_esc(k)}</div><div class="am-v">{_esc(v)}</div></div>'
                        h += '</div>'
                        st.markdown(h, unsafe_allow_html=True)

                    st.markdown(body)
                    st.markdown('</div>', unsafe_allow_html=True)

                    # Actions
                    if dirname not in ("Done", "Rejected"):
                        st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)
                        ac1, ac2, ac3, ac4, ac5 = st.columns([1, 1, 1, 1, 1])
                        with ac1:
                            if st.button("🏆 Done", key=f"done_{dirname}_{sel.name}", use_container_width=True):
                                move_file(sel, "Done"); st.rerun()
                        with ac2:
                            if dirname in ("Inbox", "Pending_Approval"):
                                if st.button("⚡ Action", key=f"act_{dirname}_{sel.name}", use_container_width=True):
                                    move_file(sel, "Needs_Action"); st.rerun()
                        with ac3:
                            if dirname in ("Inbox", "Needs_Action"):
                                if st.button("⏳ Approval", key=f"appr_{dirname}_{sel.name}", use_container_width=True):
                                    move_file(sel, "Pending_Approval"); st.rerun()
                        with ac4:
                            if dirname in ("Inbox", "Needs_Action", "Pending_Approval"):
                                if st.button("✅ Approve", key=f"appv_{dirname}_{sel.name}", use_container_width=True, type="primary"):
                                    move_file(sel, "Approved"); st.rerun()
                        with ac5:
                            if dirname in ("Inbox", "Needs_Action", "Pending_Approval"):
                                if st.button("❌ Reject", key=f"rej_{dirname}_{sel.name}", use_container_width=True):
                                    move_file(sel, "Rejected"); st.rerun()

    # ── Task Timeline ──
    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)
    st.markdown("#### 🕐 Task Lifecycle Timeline")
    timeline_files = []
    stage_order = {"Inbox": 0, "Needs_Action": 1, "Pending_Approval": 2, "Approved": 3, "Done": 4, "Rejected": 5}
    dot_cls_map = {"Inbox": "tl-dot-inbox", "Needs_Action": "tl-dot-action", "Pending_Approval": "tl-dot-approval",
                   "Approved": "tl-dot-approval", "Done": "tl-dot-done", "Rejected": "tl-dot-rejected"}
    for d_name in VAULT_DIRS.values():
        d = VAULT / d_name
        if not d.exists(): continue
        for f in d.glob("*.md"):
            meta, _ = parse_frontmatter(read_file(f))
            mtime = datetime.fromtimestamp(f.stat().st_mtime)
            timeline_files.append({"name": f.stem.replace("_", " "), "stage": d_name, "time": mtime, "meta": meta})
    timeline_files.sort(key=lambda x: x["time"], reverse=True)
    if timeline_files:
        tl_html = '<div class="timeline">'
        for item in timeline_files[:12]:
            dot = dot_cls_map.get(item["stage"], "tl-dot-inbox")
            pri = str(item["meta"].get("priority", "")).lower()
            pri_badge = f'<span class="pri-{pri}" style="margin-left:8px">{_esc(pri)}</span>' if pri in ("urgent","high","normal","low","medium") else ""
            tl_html += (f'<div class="tl-item"><div class="tl-dot {dot}"></div>'
                        f'<div class="tl-title">{_esc(item["name"])}{pri_badge}</div>'
                        f'<div class="tl-meta">{_esc(item["stage"].replace("_"," "))} | {item["time"].strftime("%b %d, %I:%M %p")}</div></div>')
        tl_html += '</div>'
        st.markdown(tl_html, unsafe_allow_html=True)
    else:
        st.info("No tasks to show in timeline.")

    # ── Create & Upload Section ──
    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(
            '<div class="cmd-center">'
            '<div class="cmd-header">'
            '<div class="cmd-header-icon">🚀</div>'
            '<div class="cmd-header-text">'
            '<div class="cmd-header-title">Command Center</div>'
            '<div class="cmd-header-desc">Create a new task for your AI Employee</div>'
            '</div></div>'
            '<div class="cmd-body">'
            '<div class="quick-templates">'
            '<span class="qt-btn">📧 Email</span>'
            '<span class="qt-btn">💼 LinkedIn</span>'
            '<span class="qt-btn">📘 Facebook</span>'
            '<span class="qt-btn">📸 Instagram</span>'
            '<span class="qt-btn">🐦 Twitter</span>'
            '<span class="qt-btn">💬 WhatsApp</span>'
            '<span class="qt-btn">🏢 Odoo</span>'
            '</div></div></div>', unsafe_allow_html=True
        )
        with st.form("new_task"):
            title = st.text_input("Task Title", placeholder="e.g. Send weekly report to stakeholders...")
            fc1, fc2, fc3 = st.columns(3)
            with fc1:
                priority = st.selectbox("Priority", ["low", "medium", "high", "urgent"], index=1)
            with fc2:
                category = st.selectbox("Category", ["general", "email", "linkedin", "facebook", "instagram", "twitter", "whatsapp", "odoo", "social", "other"])
            with fc3:
                domain = st.selectbox("Domain", ["business", "personal"])
            content = st.text_area("Instructions for AI Employee", height=120, placeholder="Describe what your AI Employee should do...")
            if st.form_submit_button("⚡ Assign to AI Employee", type="primary", use_container_width=True):
                if not title.strip():
                    st.error("Title is required.")
                else:
                    safe = re.sub(r"[^\w\-. ]", "", title.strip()).replace(" ", "_")
                    inbox = VAULT / "Inbox"; inbox.mkdir(parents=True, exist_ok=True)
                    fm = (
                        f"---\ntitle: {title.strip()}\npriority: {priority}\n"
                        f"category: {category}\ndomain: {domain}\n"
                        f"created: {datetime.now().isoformat()}\n---\n\n"
                    )
                    p = inbox / f"{safe}.md"; p.write_text(fm + content, encoding="utf-8")
                    st.success(f"✅ Task **{p.name}** assigned to AI Employee!"); st.rerun()
    with c2:
        st.markdown(
            '<div class="upload-panel">'
            '<div class="upload-header">'
            '<div class="upload-header-icon">📂</div>'
            '<div class="upload-header-text">'
            '<div class="upload-header-title">File Import</div>'
            '<div class="upload-header-desc">Upload task files for AI processing</div>'
            '</div></div>'
            '<div class="cmd-body">'
            '<div class="upload-drop">'
            '<div class="upload-drop-icon">📤</div>'
            '<div class="upload-drop-title">Drop your task file here</div>'
            '<div class="upload-drop-sub">Supports .md files • Auto-processed by AI Employee</div>'
            '</div></div></div>', unsafe_allow_html=True
        )
        uploaded = st.file_uploader(
            "Upload .md file", type=["md"], key="upload_task",
            label_visibility="collapsed",
            help="Upload a Markdown (.md) task file to Inbox",
        )
        if uploaded:
            inbox = VAULT / "Inbox"; inbox.mkdir(parents=True, exist_ok=True)
            safe_name = re.sub(r"[^\w\-. ]", "", uploaded.name)
            if not safe_name.endswith(".md"):
                safe_name += ".md"
            dest = inbox / safe_name
            if dest.exists():
                dest = inbox / f"{Path(safe_name).stem}_{int(datetime.now().timestamp())}.md"
            dest.write_bytes(uploaded.getvalue())
            sz = len(uploaded.getvalue())
            sz_str = f"{sz} B" if sz < 1024 else f"{sz/1024:.1f} KB"
            st.success(f"✅ Uploaded **{dest.name}** ({sz_str}) — AI Employee will process it!")
            st.rerun()
    render_footer()
  except Exception as e:
    st.error(f"Tasks page error: {e}")


def _get_risk_level(meta):
    risk = str(meta.get("risk_level", meta.get("risk", meta.get("priority", "medium")))).lower()
    if risk in ("high", "critical", "urgent"): return "high"
    if risk in ("low", "safe", "minor"): return "low"
    return "medium"

def page_approvals():
  try:
    _hero("🔐 Approval Queue", "Review, approve, or reject pending actions with risk assessment", particles=True)
    files = list_md_files("Pending_Approval")
    if not files:
        st.markdown('<div class="empty"><div class="empty-i">✅</div><div class="empty-t">All Clear!</div><div class="empty-s">No items awaiting approval</div></div>', unsafe_allow_html=True)
        render_footer(); return

    risk_counts = {"high": 0, "medium": 0, "low": 0}
    file_risks = {}
    for f in files:
        meta, _ = parse_frontmatter(read_file(f))
        r = _get_risk_level(meta)
        risk_counts[r] += 1
        file_risks[f.name] = r

    st.markdown(
        f'<div class="stat-row">'
        f'<div class="stat-card"><div class="stat-n">{len(files)}</div><div class="stat-l">Total Pending</div></div>'
        f'<div class="stat-card" style="border-color:rgba(239,68,68,0.2)"><div class="stat-n" style="color:#ef4444">{risk_counts["high"]}</div><div class="stat-l">High Risk</div></div>'
        f'<div class="stat-card" style="border-color:rgba(245,158,11,0.2)"><div class="stat-n" style="color:#f59e0b">{risk_counts["medium"]}</div><div class="stat-l">Medium Risk</div></div>'
        f'<div class="stat-card" style="border-color:rgba(16,185,129,0.2)"><div class="stat-n" style="color:#10b981">{risk_counts["low"]}</div><div class="stat-l">Low Risk</div></div>'
        f'</div>', unsafe_allow_html=True
    )

    lc, dc = st.columns([1, 2], gap="large")
    with lc:
        for f in files:
            r = file_risks.get(f.name, "medium")
            r_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[r]
            st.markdown(f'<div class="file-card"><span class="file-card-icon">{r_icon}</span><span class="file-card-name">{_esc(f.stem.replace("_"," "))}</span><span class="risk-badge risk-badge-{r}">{r}</span></div>', unsafe_allow_html=True)
        sel = st.radio("Select", files, format_func=lambda p: p.stem.replace('_', ' '), key="apr", label_visibility="collapsed")
    with dc:
        if not sel: render_footer(); return
        raw = read_file(sel)
        meta, body = parse_frontmatter(raw)
        risk = file_risks.get(sel.name, "medium")
        risk_label = {"high": "High Risk - Manual Review Required", "medium": "Medium Risk - Review Recommended", "low": "Low Risk - Safe to Approve"}[risk]
        st.markdown(f'<div class="risk-{risk}" style="border-radius:12px;padding:14px 18px;margin-bottom:14px"><span class="risk-badge risk-badge-{risk}">{_esc(risk.upper())}</span> <span style="color:#e2e8f0;font-weight:600;margin-left:8px">{_esc(risk_label)}</span></div>', unsafe_allow_html=True)
        if meta:
            h = '<div class="ameta">'
            for k, v in meta.items():
                if isinstance(v, list): v = ", ".join(str(x) for x in v)
                h += f'<div class="am-i"><div class="am-k">{_esc(k)}</div><div class="am-v">{_esc(v)}</div></div>'
            h += '</div>'
            st.markdown(h, unsafe_allow_html=True)
        st.markdown(body)
        st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)
        c1, c2, _ = st.columns([1, 1, 3])
        with c1:
            if st.button("✅ Approve", type="primary", use_container_width=True):
                move_file(sel, "Approved"); st.balloons(); st.rerun()
        with c2:
            if st.button("❌ Reject", type="secondary", use_container_width=True):
                move_file(sel, "Rejected"); st.rerun()
    render_footer()
  except Exception as e:
    st.error(f"Approvals error: {e}")


def page_audit_logs():
  try:
    _hero("📜 Audit Logs", "Browse, filter, and export daily system activity logs")
    avail = available_log_dates()
    if not avail:
        st.markdown('<div class="empty"><div class="empty-i">📭</div><div class="empty-t">No Logs</div><div class="empty-s">No log files found in the vault</div></div>', unsafe_allow_html=True)
        render_footer(); return

    c_date, c_stats = st.columns([1, 3])
    with c_date:
        log_date = st.date_input("📅 Date", value=avail[0])
    logs = load_log(log_date)
    with c_stats:
        success_n = sum(1 for e in logs if e.get("result") in ("success", "done", "approved"))
        error_n = sum(1 for e in logs if e.get("result") in ("error", "failed"))
        other_n = len(logs) - success_n - error_n
        st.markdown(
            f'<div class="stat-row" style="margin-top:8px">'
            f'<div class="stat-card"><div class="stat-n">{len(logs)}</div><div class="stat-l">Total</div></div>'
            f'<div class="stat-card"><div class="stat-n" style="color:#34d399">{success_n}</div><div class="stat-l">Success</div></div>'
            f'<div class="stat-card"><div class="stat-n" style="color:#f87171">{error_n}</div><div class="stat-l">Errors</div></div>'
            f'<div class="stat-card"><div class="stat-n" style="color:#fbbf24">{other_n}</div><div class="stat-l">Other</div></div>'
            f'</div>', unsafe_allow_html=True
        )

    if not logs:
        st.info(f"No logs for {log_date}")
        render_footer(); return

    aa = sorted({e.get("action_type", e.get("action", "")) for e in logs} - {""})
    ar = sorted({e.get("result", "") for e in logs} - {""})
    ad = sorted({e.get("domain", "") for e in logs if e.get("domain")})
    with st.expander("🔍 Filters", expanded=False):
        c1, c2, c3 = st.columns(3)
        with c1: fa = st.multiselect("Action", aa)
        with c2: fr = st.multiselect("Result", ar)
        with c3: fd = st.multiselect("Domain", ad)
    filtered = logs
    if fa: filtered = [e for e in filtered if e.get("action_type", e.get("action", "")) in fa]
    if fr: filtered = [e for e in filtered if e.get("result", "") in fr]
    if fd: filtered = [e for e in filtered if e.get("domain", "") in fd]
    st.caption(f"Showing **{len(filtered)}** of {len(logs)} entries")
    st.dataframe(filtered, use_container_width=True, height=400)
    if filtered:
        st.download_button("📥 Export CSV", pd.DataFrame(filtered).to_csv(index=False), f"logs_{log_date}.csv", "text/csv")
    render_footer()
  except Exception as e:
    st.error(f"Audit logs error: {e}")


def page_integrations():
  try:
    _hero("🔌 Integrations", "MCP server health monitoring and retry queue management")
    servers = load_integration_status()

    # MCP server definitions (always show, even without status file)
    all_mcps = {
        "email_mcp": {"icon": "📧", "name": "Email (Gmail SMTP)", "tier": "Silver+"},
        "linkedin_mcp": {"icon": "💼", "name": "LinkedIn API", "tier": "Silver+"},
        "facebook_mcp": {"icon": "📘", "name": "Facebook Pages", "tier": "Gold+"},
        "odoo_mcp": {"icon": "🧾", "name": "Odoo Accounting", "tier": "Gold+"},
        "twitter_mcp": {"icon": "🐦", "name": "Twitter/X", "tier": "Gold+"},
        "instagram_mcp": {"icon": "📸", "name": "Instagram", "tier": "Gold+"},
        "whatsapp_mcp": {"icon": "💬", "name": "WhatsApp", "tier": "Gold+"},
    }

    total_s = len(all_mcps)
    healthy_n = sum(1 for k in all_mcps if servers.get(k, {}).get("status") == "healthy")
    st.markdown(
        f'<div class="stat-row">'
        f'<div class="stat-card"><div class="stat-n">{total_s}</div><div class="stat-l">MCP Servers</div></div>'
        f'<div class="stat-card"><div class="stat-n" style="color:#34d399">{healthy_n}</div><div class="stat-l">Healthy</div></div>'
        f'<div class="stat-card"><div class="stat-n" style="color:#f87171">{total_s - healthy_n}</div><div class="stat-l">Issues / Unknown</div></div>'
        f'</div>', unsafe_allow_html=True
    )

    st.markdown("#### Server Status")
    for key, mcp in all_mcps.items():
        info = servers.get(key, {})
        s = info.get("status", "unknown")
        dc = {"healthy": "srv-d-g", "degraded": "srv-d-o", "unavailable": "srv-d-r"}.get(s, "srv-d-x")
        lbl = {"healthy": "Operational", "degraded": "Degraded", "unavailable": "Unavailable"}.get(s, "Not Connected")
        bc = {"healthy": "bdg-g", "degraded": "bdg-o", "unavailable": "bdg-r"}.get(s, "bdg-x")
        fc_n = info.get("consecutive_failures", 0)
        st.markdown(
            f'<div class="srv"><div class="srv-d {dc}"></div>'
            f'<span style="font-size:1.2rem;margin-right:4px">{mcp["icon"]}</span>'
            f'<span class="srv-nm">{_esc(mcp["name"])}</span>'
            f'<span class="bdg {bc}">{_esc(lbl)}</span>'
            f'<span style="color:#64748b;font-size:0.72rem;margin-left:8px">{_esc(mcp["tier"])}</span>'
            f'<span style="color:#64748b;font-size:0.72rem;margin-left:auto">Failures: {fc_n}</span>'
            f'</div>', unsafe_allow_html=True)

    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)
    st.markdown("#### Retry Queue")
    entries = parse_retry_queue()
    if entries:
        st.caption(f"**{len(entries)}** item(s) in queue")
        st.dataframe(entries, use_container_width=True, height=300)
    else:
        st.success("Retry queue is empty - all operations completed successfully.")
    render_footer()
  except Exception as e:
    st.error(f"Integrations error: {e}")


def page_reports():
  try:
    _hero("📊 Reports & Briefings", "Audit reports, CEO briefings, and system analytics")
    bd = VAULT / "Briefings"
    briefing_files = sorted(bd.glob("*.md"), reverse=True) if bd.exists() else []
    log_dates = available_log_dates()

    if not briefing_files and not log_dates:
        st.markdown('<div class="empty"><div class="empty-i">📭</div><div class="empty-t">No Reports</div><div class="empty-s">No briefings or logs available</div></div>', unsafe_allow_html=True)
        render_footer(); return

    st.markdown(
        f'<div class="stat-row">'
        f'<div class="stat-card"><div class="stat-n">{len(briefing_files)}</div><div class="stat-l">Briefings</div></div>'
        f'<div class="stat-card"><div class="stat-n">{len(log_dates)}</div><div class="stat-l">Log Days</div></div>'
        f'</div>', unsafe_allow_html=True
    )

    tab_b, tab_l = st.tabs([f"📋 Briefings ({len(briefing_files)})", f"📜 Audit Summaries ({len(log_dates)})"])

    with tab_b:
        if not briefing_files:
            st.info("No briefing reports available.")
        else:
            lc, vc = st.columns([1, 3], gap="large")
            with lc:
                for f in briefing_files:
                    mod = datetime.fromtimestamp(f.stat().st_mtime).strftime("%b %d, %Y")
                    is_ceo = "ceo" in f.stem.lower() or "briefing" in f.stem.lower()
                    icon = "📋" if is_ceo else "📊"
                    st.markdown(f'<div class="report-card"><div class="report-card-title">{icon} {_esc(f.stem.replace("_"," ").title())}</div><div class="report-card-date">📅 {_esc(mod)}</div></div>', unsafe_allow_html=True)
                sel = st.radio("Select", briefing_files, format_func=lambda p: p.stem.replace('_', ' ').title(), label_visibility="collapsed", key="rpt_sel")
            with vc:
                if sel:
                    content = read_file(sel)
                    meta, body = parse_frontmatter(content)
                    if meta:
                        h = '<div class="ameta">'
                        for k, v in meta.items():
                            if isinstance(v, list): v = ", ".join(str(x) for x in v)
                            h += f'<div class="am-i"><div class="am-k">{_esc(k)}</div><div class="am-v">{_esc(v)}</div></div>'
                        h += '</div>'
                        st.markdown(h, unsafe_allow_html=True)
                    st.markdown(body)
                    # Export report as text
                    st.download_button("📥 Export Report", content, f"{sel.stem}.md", "text/markdown")

    with tab_l:
        if not log_dates:
            st.info("No audit logs available.")
        else:
            for d in log_dates[:10]:
                logs = load_log(d)
                ok = sum(1 for e in logs if e.get("result") in ("success", "done", "approved"))
                err = sum(1 for e in logs if e.get("result") in ("error", "failed"))
                st.markdown(
                    f'<div class="srv">'
                    f'<span class="srv-nm">📅 {d.strftime("%B %d, %Y")}</span>'
                    f'<span class="bdg bdg-g">{ok} ok</span>'
                    f'<span class="bdg {"bdg-r" if err else "bdg-x"}">{err} err</span>'
                    f'<span style="color:#64748b;font-size:0.78rem">{len(logs)} total</span>'
                    f'</div>', unsafe_allow_html=True
                )
    render_footer()
  except Exception as e:
    st.error(f"Reports error: {e}")


# ===================================================================
# NEW PAGE: Plans
# ===================================================================

def page_plans():
  try:
    _hero("📝 Action Plans", "Browse generated action plans from Gold tier autonomous processing")
    plans = list_plans()

    if not plans:
        st.markdown('<div class="empty"><div class="empty-i">📝</div><div class="empty-t">No Plans</div><div class="empty-s">Plans are generated automatically by Gold tier processing</div></div>', unsafe_allow_html=True)
        render_footer(); return

    st.markdown(
        f'<div class="stat-row">'
        f'<div class="stat-card"><div class="stat-n">{len(plans)}</div><div class="stat-l">Total Plans</div></div>'
        f'</div>', unsafe_allow_html=True
    )

    search_q = st.text_input("🔎 Filter plans...", placeholder="Type to filter...", key="plan_search")
    if search_q:
        sq = search_q.lower()
        plans = [p for p in plans if sq in p.stem.lower()]

    if not plans:
        st.warning("No plans match your filter.")
        render_footer(); return

    lc, vc = st.columns([1.2, 2.8], gap="large")
    with lc:
        st.caption(f"**{len(plans)}** plan(s)")
        sel = st.radio("Select", plans,
                       format_func=lambda p: f"📝 {p.stem.replace('PLAN_','').replace('_',' ')[:40]}",
                       key="plan_sel", label_visibility="collapsed")
    with vc:
        if sel:
            content = read_file(sel)
            meta, body = parse_frontmatter(content)
            pri = str(meta.get("priority", "normal")).lower()
            status = str(meta.get("status", "unknown")).lower()
            pri_cls = f"pri-{pri}" if pri in ("urgent", "high", "normal", "low") else "pri-normal"

            st.markdown(
                f'<div class="task-preview-header">'
                f'<span class="task-preview-icon">📝</span>'
                f'<span class="task-preview-name">{_esc(sel.stem.replace("_"," "))}</span>'
                f'<span class="{pri_cls}">{_esc(pri.upper())}</span>'
                f'</div>', unsafe_allow_html=True
            )

            if meta:
                h = '<div class="ameta">'
                for k, v in meta.items():
                    if isinstance(v, list): v = ", ".join(str(x) for x in v)
                    h += f'<div class="am-i"><div class="am-k">{_esc(k)}</div><div class="am-v">{_esc(v)}</div></div>'
                h += '</div>'
                st.markdown(h, unsafe_allow_html=True)
            st.markdown(body)
    render_footer()
  except Exception as e:
    st.error(f"Plans error: {e}")


# ===================================================================
# NEW PAGE: Social Media
# ===================================================================

def page_social():
  try:
    _hero("📱 Social Media", "Track social media posts across LinkedIn, Facebook, Twitter, Instagram, WhatsApp")

    platforms = {
        "linkedin": {"icon": "💼", "name": "LinkedIn", "cls": "social-linkedin",
                     "configured": bool(CONFIG.get("LINKEDIN_ACCESS_TOKEN"))},
        "facebook": {"icon": "📘", "name": "Facebook", "cls": "social-facebook",
                     "configured": bool(CONFIG.get("INSTAGRAM_ACCESS_TOKEN"))},
        "twitter": {"icon": "🐦", "name": "Twitter/X", "cls": "social-twitter",
                    "configured": bool(CONFIG.get("TWITTER_API_KEY"))},
        "instagram": {"icon": "📸", "name": "Instagram", "cls": "social-instagram",
                      "configured": bool(CONFIG.get("INSTAGRAM_ACCESS_TOKEN"))},
        "whatsapp": {"icon": "💬", "name": "WhatsApp", "cls": "social-whatsapp",
                     "configured": CONFIG.get("WHATSAPP_MODE") in ("playwright", "api")},
    }

    posts = load_social_posts()
    platform_counts = {}
    for p in posts:
        platform_counts[p["platform"]] = platform_counts.get(p["platform"], 0) + 1

    # Platform cards
    cards_html = '<div class="stat-row">'
    for key, info in platforms.items():
        count = platform_counts.get(key, 0)
        status = "Configured" if info["configured"] else "Not Set"
        status_cls = "ws-active" if info["configured"] else "ws-inactive"
        cards_html += (
            f'<div class="social-card {info["cls"]}">'
            f'<div class="social-icon">{info["icon"]}</div>'
            f'<div class="social-name" style="color:#f1f5f9">{_esc(info["name"])}</div>'
            f'<div class="social-stat">{count} post(s)</div>'
            f'<span class="watcher-status {status_cls}" style="margin-top:8px">{status}</span>'
            f'</div>')
    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

    # Post history
    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)
    st.markdown("#### 📋 Post History")
    if posts:
        for p in posts:
            pinfo = platforms.get(p["platform"], {})
            icon = pinfo.get("icon", "📄")
            dir_badge_cls = {"Done": "act-bg-ok", "Needs_Action": "act-bg-er", "Pending_Approval": "act-bg-er"}.get(p["dir"], "act-bg-ok")
            st.markdown(
                f'<div class="act"><div class="act-d act-d-ok"></div><div class="act-b">'
                f'<div class="act-a">{icon} {_esc(p["file"].replace("_"," ").replace(".md",""))}'
                f'<span class="act-bg {dir_badge_cls}">{_esc(p["dir"])}</span></div>'
                f'<div class="act-m">{_esc(p["platform"].title())} | Priority: {_esc(p["priority"])}</div>'
                f'</div></div>', unsafe_allow_html=True)
    else:
        st.info("No social media posts found. Create tasks with 'linkedin', 'facebook', 'twitter', 'instagram', or 'whatsapp' in the filename.")

    render_footer()
  except Exception as e:
    st.error(f"Social media error: {e}")


# ===================================================================
# NEW PAGE: Accounting
# ===================================================================

def page_accounting():
  try:
    _hero("🧾 Accounting", "Odoo ERP integration - expenses, invoices, and financial overview")

    # Odoo config status
    odoo_configured = bool(CONFIG.get("ODOO_URL")) and bool(CONFIG.get("ODOO_USERNAME"))
    st.markdown(
        f'<div class="stat-row">'
        f'<div class="stat-card"><div class="stat-n" style="color:{"#34d399" if odoo_configured else "#f87171"}">{"✅" if odoo_configured else "❌"}</div><div class="stat-l">Odoo Connection</div></div>'
        f'<div class="stat-card"><div class="stat-n">{_esc(CONFIG.get("ODOO_URL","Not set"))}</div><div class="stat-l">Odoo URL</div></div>'
        f'<div class="stat-card"><div class="stat-n">{_esc(CONFIG.get("ODOO_DB","Not set"))}</div><div class="stat-l">Database</div></div>'
        f'</div>', unsafe_allow_html=True
    )

    acc_files = load_accounting_files()
    if acc_files:
        st.markdown("#### 📄 Accounting Records")
        for af in acc_files:
            st.markdown(f'<div class="report-card"><div class="report-card-title">🧾 {_esc(af["file"].replace("_"," ").replace(".md",""))}</div></div>', unsafe_allow_html=True)
            with st.expander(f"View: {af['file']}", expanded=False):
                if af["meta"]:
                    h = '<div class="ameta">'
                    for k, v in af["meta"].items():
                        if isinstance(v, list): v = ", ".join(str(x) for x in v)
                        h += f'<div class="am-i"><div class="am-k">{_esc(k)}</div><div class="am-v">{_esc(v)}</div></div>'
                    h += '</div>'
                    st.markdown(h, unsafe_allow_html=True)
                st.markdown(af["body"])
    else:
        st.markdown(
            '<div class="empty"><div class="empty-i">🧾</div>'
            '<div class="empty-t">No Accounting Records</div>'
            '<div class="empty-s">Financial records from Odoo will appear in Business/Accounting/</div></div>',
            unsafe_allow_html=True)

    # Scan Done/ for accounting-related tasks
    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)
    st.markdown("#### 📋 Related Tasks")
    acc_tasks = []
    for d_name in VAULT_DIRS.values():
        d = VAULT / d_name
        if not d.exists(): continue
        for f in d.glob("*.md"):
            name_lower = f.stem.lower()
            if any(kw in name_lower for kw in ("expense", "invoice", "accounting", "financial", "odoo", "payment")):
                acc_tasks.append({"file": f.name, "dir": d_name})
    if acc_tasks:
        for t in acc_tasks:
            dir_color = {"Done": "#34d399", "Needs_Action": "#fb923c", "Pending_Approval": "#fbbf24"}.get(t["dir"], "#94a3b8")
            st.markdown(
                f'<div class="file-card"><span class="file-card-icon">🧾</span>'
                f'<span class="file-card-name">{_esc(t["file"].replace("_"," ").replace(".md",""))}</span>'
                f'<span style="color:{dir_color};font-size:0.72rem;font-weight:600">{_esc(t["dir"])}</span></div>',
                unsafe_allow_html=True)
    else:
        st.info("No accounting-related tasks found.")

    render_footer()
  except Exception as e:
    st.error(f"Accounting error: {e}")


# ===================================================================
# NEW PAGE: Watchers & Deployment (Platinum)
# ===================================================================

def page_watchers():
  try:
    _hero("📡 Watchers & Deployment", "Watcher status, cloud/local split, health endpoint, vault sync (Platinum)")

    is_cloud = CONFIG.get("DEPLOYMENT_MODE", "local") == "cloud"
    mode = "Cloud" if is_cloud else "Local"

    st.markdown(
        f'<div class="stat-row">'
        f'<div class="stat-card"><div class="stat-n">🌐 {_esc(mode)}</div><div class="stat-l">Deployment Mode</div></div>'
        f'<div class="stat-card"><div class="stat-n">{CONFIG.get("HEALTH_PORT", 8080)}</div><div class="stat-l">Health Port</div></div>'
        f'<div class="stat-card"><div class="stat-n">{CONFIG.get("PROCESSING_INTERVAL", 30)}s</div><div class="stat-l">Processing Interval</div></div>'
        f'</div>', unsafe_allow_html=True
    )

    # Watcher cards
    st.markdown("#### 📡 Watcher Status")
    watchers = get_watcher_info()
    w_html = '<div class="watcher-grid">'
    for w in watchers:
        status_cls = "ws-active" if w["active"] else "ws-inactive"
        loc_cls = "ws-cloud" if w["location"] == "cloud" else "ws-local"
        w_html += (
            f'<div class="watcher-card">'
            f'<div class="watcher-icon">{w["icon"]}</div>'
            f'<div class="watcher-name">{_esc(w["name"])}</div>'
            f'<div style="font-size:0.68rem;color:#64748b;margin:4px 0">{_esc(w["desc"])}</div>'
            f'<span class="watcher-status {status_cls}">{"Online" if w["active"] else "Offline"}</span> '
            f'<span class="watcher-status {loc_cls}">{_esc(w["location"])}</span>'
            f'</div>')
    w_html += '</div>'
    st.markdown(w_html, unsafe_allow_html=True)

    # Cloud/Local architecture
    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)
    st.markdown("#### 🏗️ Architecture Split")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown(
            '<div class="glass"><h4>☁️ Cloud (GCP e2-micro)</h4>'
            '<div class="irow"><span class="ik">main-processor</span><span class="iv">~80MB</span></div>'
            '<div class="irow"><span class="ik">file-system-watcher</span><span class="iv">~50MB</span></div>'
            '<div class="irow"><span class="ik">gmail-watcher</span><span class="iv">~60MB</span></div>'
            '<div class="irow"><span class="ik">linkedin-watcher</span><span class="iv">~60MB</span></div>'
            '<div class="irow"><span class="ik">health-check</span><span class="iv">~25MB</span></div>'
            '<div class="irow"><span class="ik">MCP: email, linkedin, facebook, odoo</span><span class="iv">~50MB</span></div>'
            '<div class="irow"><span class="ik">PM2 + OS</span><span class="iv">~260MB</span></div>'
            '<div class="irow" style="border-top:2px solid rgba(124,58,237,0.3);margin-top:8px;padding-top:8px">'
            '<span class="ik" style="color:#a78bfa;font-weight:700">Total</span>'
            '<span class="iv" style="color:#a78bfa;font-weight:700">~585MB / 1024MB</span></div>'
            '</div>', unsafe_allow_html=True)
    with c2:
        st.markdown(
            '<div class="glass"><h4>💻 Local (Windows)</h4>'
            '<div class="irow"><span class="ik">whatsapp-watcher</span><span class="iv">Playwright</span></div>'
            '<div class="irow"><span class="ik">twitter MCP</span><span class="iv">Playwright</span></div>'
            '<div class="irow"><span class="ik">instagram MCP</span><span class="iv">Playwright</span></div>'
            '<div class="irow"><span class="ik" style="color:#64748b">Reason</span>'
            '<span class="iv" style="color:#64748b">Too heavy for 1GB cloud RAM</span></div>'
            '</div>', unsafe_allow_html=True)

    # Git Vault Sync status
    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)
    st.markdown("#### 🔄 Vault Sync")
    st.markdown(
        '<div class="glass"><h4>Git-Based Vault Sync</h4>'
        '<div class="irow"><span class="ik">Sync Interval</span><span class="iv">Every 5 minutes</span></div>'
        '<div class="irow"><span class="ik">Direction</span><span class="iv">Bidirectional</span></div>'
        '<div class="irow"><span class="ik">Method</span><span class="iv">Git pull/push via cron</span></div>'
        '</div>', unsafe_allow_html=True)

    render_footer()
  except Exception as e:
    st.error(f"Watchers error: {e}")


def _highlight_snippet(text, query):
    safe = html_mod.escape(text)
    safe_q = html_mod.escape(query)
    pattern = re.compile(re.escape(safe_q), re.IGNORECASE)
    return pattern.sub(lambda m: f"<mark>{m.group()}</mark>", safe)


def page_search():
  try:
    _hero("🔍 Global Search", "Search across all vault files instantly", particles=True)

    sc1, sc2 = st.columns([3, 1])
    with sc1:
        query = st.text_input("Search", placeholder="Type a keyword to search all files...", label_visibility="collapsed")
    with sc2:
        dir_filter = st.selectbox("Category", ["All"] + list(VAULT_DIRS.values()) + ["Plans", "Briefings"], label_visibility="collapsed")

    if query and len(query) >= 2:
        results = search_vault(query)
        # Also search Plans and Briefings
        for extra_dir in ("Plans", "Briefings"):
            d = VAULT / extra_dir
            if not d.exists(): continue
            q = query.lower()
            for f in d.glob("*.md"):
                content = read_file(f)
                if q in f.name.lower() or q in content.lower():
                    snippet = ""
                    idx = content.lower().find(q)
                    if idx >= 0:
                        s, e = max(0, idx - 40), min(len(content), idx + len(query) + 40)
                        snippet = "..." + content[s:e].replace("\n", " ") + "..."
                    results.append({"file": f.name, "dir": extra_dir, "path": str(f), "snippet": snippet})

        if dir_filter != "All":
            results = [r for r in results if r["dir"] == dir_filter]
        if results:
            dir_counts = {}
            for r in results:
                dir_counts[r["dir"]] = dir_counts.get(r["dir"], 0) + 1
            tags_html = " ".join(
                f'<span style="display:inline-block;background:rgba(124,58,237,0.12);color:#a78bfa;'
                f'padding:3px 10px;border-radius:8px;font-size:0.72rem;font-weight:600;margin-right:4px">'
                f'{_esc(d)} ({c})</span>'
                for d, c in dir_counts.items())
            st.markdown(f'<div style="margin-bottom:12px"><span style="color:#94a3b8;font-size:0.85rem;font-weight:600">Found **{len(results)}** result(s)</span> {tags_html}</div>', unsafe_allow_html=True)

            for r in results:
                snippet_html = ""
                if r["snippet"]:
                    snippet_html = _highlight_snippet(r["snippet"], query)
                st.markdown(
                    f'<div class="search-hit">'
                    f'<span class="search-hit-title">📄 {_esc(r["file"])}</span>'
                    f'<span class="search-hit-dir">{_esc(r["dir"])}</span>'
                    f'{"<div class=search-hit-snippet>" + snippet_html + "</div>" if snippet_html else ""}'
                    f'</div>', unsafe_allow_html=True
                )
                with st.expander("View full content", expanded=False):
                    content = read_file(Path(r["path"]))
                    _, body = parse_frontmatter(content)
                    st.markdown(body[:1500])
        else:
            st.markdown('<div class="empty"><div class="empty-i">🔍</div><div class="empty-t">No Results</div><div class="empty-s">Try different keywords or check another category</div></div>', unsafe_allow_html=True)
    elif query:
        st.caption("Type at least 2 characters to search...")
    else:
        st.markdown('<div class="empty"><div class="empty-i">🔍</div><div class="empty-t">Search Your Vault</div><div class="empty-s">Enter keywords to search across all vault directories including Plans and Briefings</div></div>', unsafe_allow_html=True)
    render_footer()
  except Exception as e:
    st.error(f"Search error: {e}")


def page_settings():
  try:
    _hero("⚙️ Settings", "Read-only configuration loaded from environment variables")
    groups = {
        "🔧 Core": ["VAULT_PATH","CHECK_INTERVAL","LOG_LEVEL","DRY_RUN","PROCESSING_INTERVAL","DEPLOYMENT_MODE"],
        "🥇 Gold Tier": ["GOLD_TIER_ENABLED","AUTO_APPROVE_LOW_RISK","AUDIT_SCHEDULE","BRIEFING_SCHEDULE","LOG_RETENTION_DAYS"],
        "📧 Email": ["EMAIL_SMTP_HOST","EMAIL_SMTP_PORT","EMAIL_SMTP_USERNAME","EMAIL_SMTP_PASSWORD","EMAIL_FROM_ADDRESS","EMAIL_RATE_LIMIT_PER_DAY"],
        "💼 LinkedIn": ["LINKEDIN_ACCESS_TOKEN","LINKEDIN_PERSONAL_ACCOUNT_ID"],
        "🐦 Twitter": ["TWITTER_BEARER_TOKEN","TWITTER_API_KEY","TWITTER_API_SECRET","TWITTER_ACCESS_TOKEN","TWITTER_ACCESS_TOKEN_SECRET"],
        "📸 Instagram": ["INSTAGRAM_ACCESS_TOKEN","INSTAGRAM_BUSINESS_ACCOUNT_ID"],
        "💬 WhatsApp": ["WHATSAPP_MODE","WHATSAPP_API_TOKEN","WHATSAPP_TRIGGER_KEYWORDS"],
        "🧾 Odoo": ["ODOO_URL","ODOO_DB","ODOO_USERNAME","ODOO_API_KEY"],
        "📬 Gmail": ["GOOGLE_APPLICATION_CREDENTIALS","GMAIL_TOKEN_FILE"],
        "🏗 Infra": ["HEALTH_PORT"],
    }
    shown = set()
    for gn, keys in groups.items():
        present = [k for k in keys if k in CONFIG]
        if not present: continue
        h = f'<div class="sg"><div class="sg-t">{gn}</div>'
        for k in present:
            shown.add(k); v = CONFIG[k]
            if is_sensitive(k) and v:
                h += f'<div class="si"><span class="sk">{_esc(k)}</span><span class="sv sv-m">••••••••</span></div>'
            else:
                h += f'<div class="si"><span class="sk">{_esc(k)}</span><span class="sv">{_esc(v)}</span></div>'
        h += '</div>'
        st.markdown(h, unsafe_allow_html=True)
    rem = {k: v for k, v in sorted(CONFIG.items()) if k not in shown}
    if rem:
        h = '<div class="sg"><div class="sg-t">📦 Other</div>'
        for k, v in rem.items():
            if is_sensitive(k) and v:
                h += f'<div class="si"><span class="sk">{_esc(k)}</span><span class="sv sv-m">••••••••</span></div>'
            else:
                h += f'<div class="si"><span class="sk">{_esc(k)}</span><span class="sv">{_esc(v)}</span></div>'
        h += '</div>'
        st.markdown(h, unsafe_allow_html=True)

    # Logout
    st.markdown('<div class="neon-line"></div>', unsafe_allow_html=True)
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state["authenticated"] = False
        st.rerun()

    render_footer()
  except Exception as e:
    st.error(f"Settings error: {e}")


# ===================================================================
# SIDEBAR — Icon Navigation with option_menu (12 pages now)
# ===================================================================

PAGES = {
    "Dashboard": page_dashboard, "Tasks": page_tasks, "Plans": page_plans,
    "Approvals": page_approvals, "Audit Logs": page_audit_logs,
    "Integrations": page_integrations, "Social Media": page_social,
    "Accounting": page_accounting, "Reports": page_reports,
    "Watchers": page_watchers, "Search": page_search, "Settings": page_settings,
}
ICONS = [
    "house-fill", "list-task", "map-fill",
    "shield-check", "journal-text",
    "plug-fill", "share-fill",
    "cash-coin", "file-earmark-bar-graph-fill",
    "broadcast", "search", "gear-fill",
]

with st.sidebar:
    st.markdown(
        '<div style="text-align:center;padding:8px 0 2px">'
        '<div style="font-size:2.5rem;animation:float 3s ease-in-out infinite">🤖</div>'
        '<h2 style="margin:2px 0;font-weight:900;font-size:1.2rem;'
        'background:linear-gradient(135deg,#a78bfa,#7c3aed,#06b6d4);'
        '-webkit-background-clip:text;-webkit-text-fill-color:transparent;'
        'background-clip:text">AI Employee</h2>'
        '<p style="color:#475569;font-size:0.7rem;margin:0">Personal Automation Hub</p>'
        '</div>',
        unsafe_allow_html=True
    )
    st.markdown("")

    pending_count = get_vault_counts().get("pending_approval", 0)
    approval_label = f"Approvals ({pending_count})" if pending_count else "Approvals"
    menu_options = [
        "Dashboard", "Tasks", "Plans",
        approval_label, "Audit Logs",
        "Integrations", "Social Media",
        "Accounting", "Reports",
        "Watchers", "Search", "Settings",
    ]

    selection = option_menu(
        menu_title=None,
        options=menu_options,
        icons=ICONS,
        default_index=0,
        styles={
            "container": {"padding": "0", "background-color": "transparent"},
            "icon": {"color": "#6d28d9", "font-size": "16px"},
            "nav-link": {
                "font-size": "14px", "text-align": "left", "margin": "2px 0",
                "padding": "10px 16px", "border-radius": "10px",
                "color": "#475569", "font-weight": "600",
                "transition": "all 0.2s ease",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #ede9fe, #dbeafe)",
                "color": "#6d28d9", "font-weight": "700",
                "border": "1px solid rgba(109,40,217,0.2)",
            },
        },
    )

    if selection.startswith("Approvals"):
        selection = "Approvals"

    st.markdown("---")

    # Sidebar stats
    counts = get_vault_counts()
    total = sum(counts.values())
    pending = counts.get("pending_approval", 0)
    score = compute_health_score()
    tiers = _get_active_tiers()
    highest = "Platinum" if tiers["platinum"] else ("Gold" if tiers["gold"] else "Silver")
    tier_colors = {"Gold": "#ffd700", "Platinum": "#06b6d4", "Silver": "#c0c0c0"}
    tier_icons = {"Gold": "🥇", "Platinum": "💎", "Silver": "🥈"}

    st.markdown(f'<div class="sb-s"><div class="sb-n">{total}</div><div class="sb-l">Total Tasks</div></div>', unsafe_allow_html=True)

    if pending:
        st.markdown(f'<div class="sb-s" style="background:#fffbeb;border-color:#fde68a"><div class="sb-n" style="color:#d97706 !important">⚠️ {pending}</div><div class="sb-l">Awaiting Approval</div></div>', unsafe_allow_html=True)

    h_color = "#059669" if score >= 80 else ("#d97706" if score >= 50 else "#dc2626")
    st.markdown(f'<div class="sb-s" style="background:#f0fdf4;border-color:#bbf7d0"><div class="sb-n" style="color:{h_color} !important">{score}%</div><div class="sb-l">System Health</div></div>', unsafe_allow_html=True)

    tc = {"Gold": "#a16207", "Platinum": "#0e7490", "Silver": "#475569"}.get(highest, "#6d28d9")
    ti = tier_icons.get(highest, "🏅")
    st.markdown(f'<div class="sb-s" style="background:#faf5ff;border-color:#e9d5ff"><div class="sb-n" style="color:{tc} !important">{ti} {highest}</div><div class="sb-l">Active Tier</div></div>', unsafe_allow_html=True)

    plans_n = len(list_plans())
    if plans_n:
        st.markdown(f'<div class="sb-s" style="background:#ede9fe;border-color:#c4b5fd"><div class="sb-n" style="color:#6d28d9 !important">{plans_n}</div><div class="sb-l">Action Plans</div></div>', unsafe_allow_html=True)

    st.markdown("")
    st.markdown(f'<p style="text-align:center;color:#475569;font-size:0.78rem;font-family:JetBrains Mono,monospace !important">🕐 {datetime.now().strftime("%I:%M:%S %p")}</p>', unsafe_allow_html=True)

    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()
    auto = st.toggle("Auto-refresh (30s)", value=False)

# Run selected page
PAGES[selection]()

# Auto-refresh using JS instead of blocking sleep
if auto:
    st.markdown(
        '<script>setTimeout(function(){window.location.reload()},30000);</script>',
        unsafe_allow_html=True
    )
