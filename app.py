import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin, urlparse, unquote
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime
import time
import html


# =========================
# PERSISTENT SYSTEM MESSAGES
# =========================
if "persistent_neon_message" not in st.session_state:
    st.session_state.persistent_neon_message = ""



# =========================
# PAGE CONFIG
# =========================
st.set_page_config(
    page_title="Investor Outreach Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================
# CSS DESIGN
# =========================
def load_css(has_file=False):
    sidebar_css = ""
    sidebar_width = "270px"

    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #07111f 0%, #0b1628 50%, #0f1f35 100%);
        color: #f8fafc;
        font-family: Inter, Arial, sans-serif;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Hide Streamlit deploy button only */
    .stDeployButton {{
        display: none !important;
    }}

    /* Keep Streamlit toolbar available so the native sidebar button can work.
       Deploy button is still hidden separately above. */
    
    /* Do not hide Streamlit header, because the sidebar reopen arrow lives there */
    header {{
        background: transparent !important;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    /* Let Streamlit handle sidebar open/close natively.
       Do not force display/position/transform here. */

    .block-container {{
        padding-top: 2rem;
        padding-left: 2rem;
        padding-right: 2rem;
        max-width: 1550px;
    }}

    {sidebar_css}

    [data-testid="stSidebar"] {{
        background: rgba(8, 17, 31, 0.98);
        border-right: 1px solid rgba(148, 163, 184, 0.18);
    }}

    [data-testid="stSidebar"] * {{
        color: #e5e7eb;
    }}

    [data-testid="stSidebar"] .stRadio > label {{
        color: #94a3b8 !important;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }}

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
        background: transparent;
        padding: 8px 10px;
        border-radius: 10px;
        margin-bottom: 4px;
    }}

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {{
        background: rgba(30, 41, 59, 0.72);
    }}

    .sidebar-brand {{
        padding: 0 0 14px 0;
    }}

    .sidebar-brand h2 {{
        margin-bottom: 0;
        color: #ffffff;
        font-size: 22px;
        font-weight: 800;
        line-height: 1.1;
    }}

    .sidebar-brand p {{
        color: #94a3b8;
        font-size: 13px;
        margin-top: 7px;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}

    .sidebar-summary-title {{
        color: #94a3b8;
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        margin-bottom: 10px;
    }}

    .sidebar-summary-item {{
        margin-bottom: 10px;
        font-size: 13px;
        color: #94a3b8;
    }}

    .sidebar-summary-value {{
        color: #ffffff;
        font-size: 14px;
        margin-top: 4px;
        word-break: break-word;
    }}

    .app-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        gap: 18px;
        margin-bottom: 24px;
    }}

    .main-title {{
        font-size: 30px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 8px;
    }}

    .sub-title {{
        color: #94a3b8;
        font-size: 14px;
    }}

    .upload-button-wrap {{
        display: flex;
        justify-content: flex-end;
        min-width: 210px;
    }}

    .upload-button-wrap [data-testid="stFileUploader"] {{
        width: 210px;
    }}

    .upload-button-wrap [data-testid="stFileUploaderDropzone"] {{
        padding: 0 !important;
        min-height: 44px !important;
        border: 1px solid rgba(148, 163, 184, 0.26) !important;
        background: rgba(15, 23, 42, 0.72) !important;
        border-radius: 12px !important;
    }}

    .upload-button-wrap [data-testid="stFileUploaderDropzone"] > div:first-child {{
        display: none !important;
    }}

    .upload-button-wrap [data-testid="stFileUploaderDropzone"] button {{
        background: transparent !important;
        border: none !important;
        color: transparent !important;
        font-weight: 700 !important;
        width: 100% !important;
        height: 42px !important;
        position: relative;
    }}

    .upload-button-wrap [data-testid="stFileUploaderDropzone"] button::after {{
        content: "+ Add New File";
        color: #ffffff;
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
    }}

    .upload-button-wrap [data-testid="stFileUploaderDropzone"] button div,
    .upload-button-wrap [data-testid="stFileUploaderDropzone"] button span,
    .upload-button-wrap [data-testid="stFileUploaderDropzone"] small {{
        display: none !important;
    }}

    .upload-button-wrap [data-testid="stFileUploaderFile"] {{
        display: none !important;
    }}

    .landing-wrap {{
        min-height: 75vh;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .landing-card {{
        background: rgba(15, 23, 42, 0.78);
        border: 1px solid rgba(148, 163, 184, 0.20);
        border-radius: 24px;
        padding: 42px;
        max-width: 760px;
        width: 100%;
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.35);
        backdrop-filter: blur(14px);
        text-align: center;
    }}

    .landing-title {{
        font-size: 38px;
        color: #ffffff;
        font-weight: 850;
        margin-bottom: 10px;
    }}

    .landing-subtitle {{
        color: #94a3b8;
        font-size: 16px;
        line-height: 1.6;
        margin-bottom: 24px;
    }}

    .landing-upload [data-testid="stFileUploader"] {{
        max-width: 420px;
        margin: 0 auto;
    }}

    .landing-upload [data-testid="stFileUploaderDropzone"] {{
        border: 1px dashed rgba(96, 165, 250, 0.55) !important;
        background: rgba(30, 41, 59, 0.72) !important;
        border-radius: 18px !important;
        padding: 26px !important;
    }}

    .section-title {{
        font-size: 20px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 14px;
    }}

    .glass-card {{
        background: rgba(15, 23, 42, 0.74);
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 16px;
        padding: 18px;
        box-shadow: 0 16px 35px rgba(0, 0, 0, 0.25);
        backdrop-filter: blur(12px);
        margin-bottom: 18px;
    }}

    .kpi-card {{
        background: linear-gradient(145deg, rgba(30, 41, 59, 0.97), rgba(15, 23, 42, 0.97));
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 16px;
        padding: 16px 14px;
        box-shadow: 0 14px 30px rgba(0, 0, 0, 0.24);
        min-height: 112px;
        display: flex;
        align-items: center;
        gap: 12px;
        overflow: hidden;
    }}

    .kpi-icon {{
        width: 54px;
        height: 54px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 22px;
        flex-shrink: 0;
        box-shadow: inset 0 0 18px rgba(255,255,255,0.08), 0 10px 22px rgba(0,0,0,0.28);
        overflow: hidden;
    }}

    .kpi-img {{
        width: 30px;
        height: 30px;
        object-fit: contain;
    }}

    .kpi-icon-blue {{ background: linear-gradient(135deg, #1d4ed8, #1e3a8a); }}
    .kpi-icon-green {{ background: linear-gradient(135deg, #059669, #065f46); }}
    .kpi-icon-purple {{ background: linear-gradient(135deg, #9333ea, #6b21a8); }}
    .kpi-icon-yellow {{ background: linear-gradient(135deg, #ca8a04, #854d0e); }}
    .kpi-icon-teal {{ background: linear-gradient(135deg, #0d9488, #115e59); }}
    .kpi-icon-cyan {{ background: linear-gradient(135deg, #0284c7, #075985); }}

    .kpi-content {{
        min-width: 0;
    }}

    .kpi-label {{
        color: #94a3b8;
        font-size: 10px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.035em;
        line-height: 1.15;
        white-space: normal;
        word-break: normal;
    }}

    .kpi-value {{
        color: #ffffff;
        font-size: 26px;
        font-weight: 850;
        margin-top: 7px;
        line-height: 1;
    }}

    .kpi-help {{
        color: #94a3b8;
        font-size: 11px;
        margin-top: 7px;
        line-height: 1.25;
        word-break: normal;
    }}

    .chart-title {{
        font-size: 16px;
        font-weight: 800;
        color: #ffffff;
        margin-bottom: 4px;
    }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: rgba(15, 23, 42, 0.74) !important;
        border: 1px solid rgba(148, 163, 184, 0.18) !important;
        border-radius: 16px !important;
        box-shadow: 0 16px 35px rgba(0, 0, 0, 0.22) !important;
        padding: 12px !important;
    }}

    .status-ok {{
        color: #22c55e;
        background: rgba(34, 197, 94, 0.10);
        border: 1px solid rgba(34, 197, 94, 0.22);
        padding: 12px 14px;
        border-radius: 12px;
        font-size: 14px;
        margin-top: 8px;
    }}

    .badge {{
        display: inline-block;
        padding: 4px 9px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 800;
        color: #ffffff;
    }}

    .badge-high {{ background: rgba(239, 68, 68, 0.88); }}
    .badge-medium {{ background: rgba(234, 179, 8, 0.88); color: #111827; }}
    .badge-low {{ background: rgba(34, 197, 94, 0.88); }}

    .stButton > button {{
        background: rgba(37, 99, 235, 0.95);
        color: white;
        border: 1px solid rgba(96, 165, 250, 0.35);
        border-radius: 12px;
        padding: 0.65rem 1rem;
        font-weight: 700;
    }}

    .stButton > button:hover {{
        background: rgba(59, 130, 246, 1);
        border-color: rgba(147, 197, 253, 0.8);
    }}

    .stTextInput input,
    .stSelectbox div[data-baseweb="select"],
    .stMultiSelect div[data-baseweb="select"] {{
        background-color: rgba(15, 23, 42, 0.95);
        border-radius: 12px;
        color: white;
    }}

    [data-testid="stDataFrame"] {{
        border-radius: 16px;
        overflow: hidden;
        border: 1px solid rgba(148, 163, 184, 0.18);
    }}

    hr {{
        border: none;
        border-top: 1px solid rgba(148, 163, 184, 0.18);
        margin: 24px 0;
    }}


    /* =========================
       INTERACTIVE / MOTION EFFECTS
       Safe CSS-only upgrades
    ========================= */
    html {{
        scroll-behavior: smooth;
    }}

    .stApp::before {{
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        background:
            radial-gradient(circle at 18% 20%, rgba(59, 130, 246, 0.16), transparent 28%),
            radial-gradient(circle at 82% 10%, rgba(168, 85, 247, 0.12), transparent 26%),
            radial-gradient(circle at 60% 88%, rgba(20, 184, 166, 0.10), transparent 30%);
        animation: ambientGlow 13s ease-in-out infinite alternate;
    }}

    .stApp > div {{
        position: relative;
        z-index: 1;
    }}

    @keyframes ambientGlow {{
        0% {{ opacity: 0.45; transform: scale(1); }}
        100% {{ opacity: 0.95; transform: scale(1.06); }}
    }}

    .main-title {{
        background: linear-gradient(90deg, #ffffff, #93c5fd, #c4b5fd, #ffffff);
        background-size: 220% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: titleShimmer 7s linear infinite;
    }}

    @keyframes titleShimmer {{
        0% {{ background-position: 0% center; }}
        100% {{ background-position: 220% center; }}
    }}

    .kpi-card,
    .glass-card,
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease, background 0.22s ease;
    }}

    .kpi-card:hover,
    .glass-card:hover,
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {{
        transform: translateY(-5px);
        border-color: rgba(96, 165, 250, 0.50) !important;
        box-shadow: 0 22px 48px rgba(0, 0, 0, 0.34), 0 0 26px rgba(37, 99, 235, 0.14) !important;
    }}

    .kpi-icon {{
        animation: softPulse 3.2s ease-in-out infinite;
    }}

    @keyframes softPulse {{
        0%, 100% {{ transform: scale(1); filter: brightness(1); }}
        50% {{ transform: scale(1.05); filter: brightness(1.18); }}
    }}

    .stButton > button {{
        position: relative;
        overflow: hidden;
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 28px rgba(37, 99, 235, 0.32);
    }}

    .stButton > button::before {{
        content: "";
        position: absolute;
        top: 0;
        left: -80%;
        width: 55%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.28), transparent);
        transform: skewX(-20deg);
        transition: left 0.55s ease;
    }}

    .stButton > button:hover::before {{
        left: 125%;
    }}

    section[data-testid="stSidebar"] {{
        box-shadow: 18px 0 55px rgba(0, 0, 0, 0.22);
    }}

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
        transition: transform 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
    }}

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {{
        transform: translateX(5px);
        box-shadow: inset 3px 0 0 rgba(96, 165, 250, 0.85);
    }}

    [data-testid="stDataFrame"],
    table {{
        transition: box-shadow 0.22s ease, border-color 0.22s ease;
    }}

    [data-testid="stDataFrame"]:hover {{
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.24);
        border-color: rgba(96, 165, 250, 0.42);
    }}

    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}

    ::-webkit-scrollbar-track {{
        background: rgba(15, 23, 42, 0.85);
    }}

    ::-webkit-scrollbar-thumb {{
        background: linear-gradient(180deg, #2563eb, #7c3aed);
        border-radius: 999px;
        border: 2px solid rgba(15, 23, 42, 0.85);
    }}

    ::-webkit-scrollbar-thumb:hover {{
        background: linear-gradient(180deg, #60a5fa, #a78bfa);
    }}

    .block-container > div {{
        animation: pageFadeUp 0.45s ease both;
    }}

    @keyframes pageFadeUp {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}


    /* =========================
       REAL VIBE / NEON INTERACTION LAYER
       Visible mouse trail + neon UI motion
    ========================= */

    .stApp {{
        overflow-x: hidden;
    }}

    .stApp::after {{
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        opacity: 0.25;
        background-image:
            linear-gradient(rgba(56, 189, 248, 0.16) 1px, transparent 1px),
            linear-gradient(90deg, rgba(168, 85, 247, 0.14) 1px, transparent 1px);
        background-size: 52px 52px;
        mask-image: radial-gradient(circle at center, black 0%, transparent 72%);
        animation: neonGridMove 18s linear infinite;
    }}

    @keyframes neonGridMove {{
        0% {{ background-position: 0 0, 0 0; }}
        100% {{ background-position: 104px 104px, 104px 104px; }}
    }}

    .main-title {{
        text-shadow:
            0 0 12px rgba(96, 165, 250, 0.38),
            0 0 28px rgba(168, 85, 247, 0.22);
        animation: titleShimmer 7s linear infinite, titleFloat 4s ease-in-out infinite;
    }}

    @keyframes titleFloat {{
        0%, 100% {{ transform: translateY(0); }}
        50% {{ transform: translateY(-3px); }}
    }}

    .kpi-card,
    .glass-card,
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        position: relative;
        isolation: isolate;
    }}

    .kpi-card::before,
    .glass-card::before,
    div[data-testid="stVerticalBlockBorderWrapper"]::before {{
        content: "";
        position: absolute;
        inset: -1px;
        border-radius: inherit;
        padding: 1px;
        background: linear-gradient(120deg, transparent, rgba(56,189,248,0.75), rgba(168,85,247,0.75), transparent);
        background-size: 260% 260%;
        -webkit-mask: linear-gradient(#000 0 0) content-box, linear-gradient(#000 0 0);
        -webkit-mask-composite: xor;
        mask-composite: exclude;
        opacity: 0;
        pointer-events: none;
        animation: borderRun 4.5s linear infinite;
        z-index: -1;
    }}

    .kpi-card:hover::before,
    .glass-card:hover::before,
    div[data-testid="stVerticalBlockBorderWrapper"]:hover::before {{
        opacity: 1;
    }}

    @keyframes borderRun {{
        0% {{ background-position: 0% 50%; }}
        100% {{ background-position: 260% 50%; }}
    }}

    .kpi-card:hover {{
        transform: perspective(900px) rotateX(3deg) rotateY(-4deg) translateY(-8px) scale(1.015);
    }}

    .kpi-card:hover .kpi-icon {{
        animation: iconBounce 0.7s ease both, softPulse 2.4s ease-in-out infinite;
        box-shadow:
            inset 0 0 18px rgba(255,255,255,0.12),
            0 0 22px rgba(56,189,248,0.34),
            0 0 45px rgba(168,85,247,0.24);
    }}

    @keyframes iconBounce {{
        0% {{ transform: translateY(0) scale(1); }}
        45% {{ transform: translateY(-8px) scale(1.08); }}
        100% {{ transform: translateY(0) scale(1.03); }}
    }}

    .stButton > button {{
        animation: buttonBreath 3s ease-in-out infinite;
    }}

    @keyframes buttonBreath {{
        0%, 100% {{ box-shadow: 0 0 0 rgba(37, 99, 235, 0); }}
        50% {{ box-shadow: 0 0 24px rgba(37, 99, 235, 0.34); }}
    }}

    .neon-cursor-glow {{
        position: fixed;
        width: 360px;
        height: 360px;
        border-radius: 999px;
        pointer-events: none;
        z-index: 999999;
        left: 0;
        top: 0;
        transform: translate(-50%, -50%);
        background:
            radial-gradient(circle, rgba(56, 189, 248, 0.24) 0%, rgba(168, 85, 247, 0.13) 35%, transparent 68%);
        mix-blend-mode: screen;
        filter: blur(10px);
        opacity: 0;
        transition: opacity 0.25s ease;
    }}

    .neon-trail-dot {{
        position: fixed;
        width: 11px;
        height: 11px;
        border-radius: 999px;
        pointer-events: none;
        z-index: 999998;
        transform: translate(-50%, -50%);
        background: #38bdf8;
        box-shadow:
            0 0 10px #38bdf8,
            0 0 22px rgba(168,85,247,0.9),
            0 0 38px rgba(34,211,238,0.45);
        animation: trailFade 0.75s ease-out forwards;
    }}

    @keyframes trailFade {{
        0% {{ opacity: 0.95; transform: translate(-50%, -50%) scale(1); }}
        100% {{ opacity: 0; transform: translate(-50%, -50%) scale(0.15); }}
    }}

    .neon-click-ring {{
        position: fixed;
        width: 22px;
        height: 22px;
        border: 2px solid rgba(56,189,248,0.9);
        border-radius: 999px;
        pointer-events: none;
        z-index: 1000000;
        transform: translate(-50%, -50%);
        box-shadow: 0 0 22px rgba(168,85,247,0.9);
        animation: clickRing 0.72s ease-out forwards;
    }}

    @keyframes clickRing {{
        0% {{ opacity: 1; width: 16px; height: 16px; }}
        100% {{ opacity: 0; width: 110px; height: 110px; }}
    }}

    .neon-comet {{
        position: fixed;
        width: 160px;
        height: 2px;
        pointer-events: none;
        z-index: 999997;
        background: linear-gradient(90deg, transparent, rgba(56,189,248,0.95), rgba(168,85,247,0.9), transparent);
        box-shadow: 0 0 18px rgba(56,189,248,0.8);
        transform-origin: center;
        animation: cometSwipe 0.6s ease-out forwards;
    }}

    @keyframes cometSwipe {{
        0% {{ opacity: 0.95; transform: translate(-50%, -50%) rotate(var(--angle)) scaleX(0.25); }}
        100% {{ opacity: 0; transform: translate(-50%, -50%) rotate(var(--angle)) scaleX(1.45); }}
    }}

    .status-ok {{
        box-shadow: 0 0 22px rgba(34, 197, 94, 0.12);
        animation: greenPulse 2.8s ease-in-out infinite;
    }}

    @keyframes greenPulse {{
        0%, 100% {{ border-color: rgba(34,197,94,0.22); }}
        50% {{ border-color: rgba(34,197,94,0.58); }}
    }}

    /* =========================
       SIDEBAR — native Streamlit collapse, styled only.
       Important: no fixed positioning, no forced display, no forced width on collapse.
       This lets the dashboard fill the freed space when collapsed.
    ========================= */
    [data-testid="stSidebar"] {{
        background: rgba(8, 17, 31, 0.98) !important;
        border-right: 1px solid rgba(148, 163, 184, 0.18) !important;
        box-shadow: 18px 0 55px rgba(0, 0, 0, 0.22) !important;
    }}

    /* Width only when sidebar is expanded. When collapsed, do NOT reserve space. */
    [data-testid="stSidebar"][aria-expanded="true"] {{
        min-width: {sidebar_width} !important;
        max-width: {sidebar_width} !important;
    }}

    [data-testid="stSidebar"][aria-expanded="false"] {{
        min-width: 0 !important;
        max-width: 0 !important;
        width: 0 !important;
        border-right: 0 !important;
        box-shadow: none !important;
        overflow: hidden !important;
    }}

    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {{
        display: none !important;
    }}

    /* Main dashboard stretches naturally after native sidebar collapse */
    [data-testid="stAppViewContainer"],
    [data-testid="stMain"],
    .main {{
        width: 100% !important;
    }}

    [data-testid="stSidebar"] > div:first-child {{
        background: rgba(8, 17, 31, 0.98) !important;
        padding-top: 0.5rem !important;
        overflow-y: auto !important;
    }}

    [data-testid="stSidebar"] hr {{
        margin: 14px 0 !important;
    }}

    /* Keep the native sidebar open/close control visible and clickable */
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    button[aria-label*="sidebar"],
    button[title*="sidebar"] {{
        visibility: visible !important;
        opacity: 1 !important;
        pointer-events: auto !important;
    }}

    .block-container {{
        max-width: none !important;
    }}


    /* =========================
       CLEANED / MERGED SHEET NEON UI
    ========================= */
    .neon-ack {{
        color: #38bdf8;
        background: rgba(14, 165, 233, 0.10);
        border: 1px solid rgba(56, 189, 248, 0.35);
        border-radius: 14px;
        padding: 14px 16px;
        margin: 12px 0 18px 0;
        font-weight: 800;
        letter-spacing: 0.01em;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.85), 0 0 26px rgba(14, 165, 233, 0.45);
        box-shadow: 0 0 24px rgba(56, 189, 248, 0.16), inset 0 0 18px rgba(56, 189, 248, 0.06);
        animation: neonAckPulse 2.4s ease-in-out infinite;
    }}

    @keyframes neonAckPulse {{
        0%, 100% {{ border-color: rgba(56, 189, 248, 0.35); box-shadow: 0 0 20px rgba(56, 189, 248, 0.14); }}
        50% {{ border-color: rgba(125, 211, 252, 0.85); box-shadow: 0 0 34px rgba(56, 189, 248, 0.30); }}
    }}

    .cleaned-sheet-table {{
        width: 100%;
        border-collapse: collapse;
        overflow: hidden;
        border-radius: 14px;
        border: 1px solid rgba(148, 163, 184, 0.18);
        margin-top: 10px;
    }}

    .cleaned-sheet-table th {{
        background: rgba(30, 41, 59, 0.95);
        color: #94a3b8;
        text-align: left;
        padding: 12px;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }}

    .cleaned-sheet-table td {{
        background: rgba(15, 23, 42, 0.72);
        border-top: 1px solid rgba(148, 163, 184, 0.12);
        padding: 12px;
        color: #e5e7eb;
        font-size: 13px;
    }}

    .merged-sheet-row td {{
        color: #7dd3fc !important;
        font-weight: 850;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.85), 0 0 24px rgba(14, 165, 233, 0.45);
        background: linear-gradient(90deg, rgba(14, 165, 233, 0.18), rgba(15, 23, 42, 0.72)) !important;
    }}



    /* =========================
       DATA READINESS TABLE FIX
       Allows full readiness table to be viewed with horizontal scroll.
       Does not affect Outreach Prep or Email Outreach logic.
    ========================= */
    .data-readiness-table-wrap {{
        width: 100%;
        max-width: 100%;
        max-height: 650px;
        overflow-x: auto;
        overflow-y: auto;
        border: 1px solid rgba(148, 163, 184, 0.18);
        border-radius: 14px;
        margin-top: 12px;
    }}

    .data-readiness-table-wrap table {{
        min-width: 1500px;
        width: max-content;
        border-collapse: collapse;
        color: #e5e7eb;
        font-size: 13px;
        table-layout: auto;
    }}

    .data-readiness-table-wrap th {{
        background: rgba(30, 41, 59, 0.95);
        color: #94a3b8;
        text-align: left;
        padding: 12px;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        position: sticky;
        top: 0;
        z-index: 2;
        white-space: nowrap;
    }}

    .data-readiness-table-wrap td {{
        background: rgba(15, 23, 42, 0.72);
        border-top: 1px solid rgba(148, 163, 184, 0.12);
        padding: 12px;
        vertical-align: middle;
        white-space: nowrap;
    }}

    .data-readiness-table-wrap td:nth-child(7) {{
        min-width: 360px;
        max-width: 520px;
        white-space: normal;
        line-height: 1.45;
    }}

    .data-readiness-table-wrap::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}


    /* =========================
       OUTREACH PREP BUTTON GROUP
       Cleaner spacing for enrichment buttons.
    ========================= */
    .outreach-button-note {{
        color: #94a3b8;
        font-size: 12px;
        line-height: 1.45;
        margin-top: 8px;
        margin-bottom: 10px;
    }}

    div[data-testid="column"] .stButton > button {{
        width: 100%;
        min-height: 48px;
        white-space: normal;
        line-height: 1.25;
    }}


    /* =========================
       NEON BLUE SYSTEM MESSAGE
       Used when no missing PIC/email rows are found.
    ========================= */
    .neon-blue-message {{
        color: #7dd3fc;
        background: rgba(14, 165, 233, 0.10);
        border: 1px solid rgba(56, 189, 248, 0.45);
        border-radius: 14px;
        padding: 14px 16px;
        margin: 12px 0 18px 0;
        font-weight: 800;
        letter-spacing: 0.01em;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.85), 0 0 26px rgba(14, 165, 233, 0.45);
        box-shadow: 0 0 24px rgba(56, 189, 248, 0.18), inset 0 0 18px rgba(56, 189, 248, 0.07);
        animation: neonBluePulse 2.4s ease-in-out infinite;
    }}

    @keyframes neonBluePulse {{
        0%, 100% {{
            border-color: rgba(56, 189, 248, 0.45);
            box-shadow: 0 0 20px rgba(56, 189, 248, 0.16);
        }}
        50% {{
            border-color: rgba(125, 211, 252, 0.95);
            box-shadow: 0 0 36px rgba(56, 189, 248, 0.34);
        }}
    }}



    /* =========================
       SIDEBAR SPACING IMPROVEMENT
       Keeps sidebar content high, but adds breathing room in Data Summary.
    ========================= */
    [data-testid="stSidebar"] > div:first-child {{
        padding-top: 0rem !important;
        margin-top: -0.45rem !important;
    }}

    [data-testid="stSidebar"] .block-container,
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
        padding-top: 0rem !important;
        gap: 0.7rem !important;
    }}

    .sidebar-brand {{
        padding: 0 0 10px 0 !important;
        margin-top: -2px !important;
        margin-bottom: 2px !important;
    }}

    .sidebar-brand h2 {{
        font-size: 21px !important;
        line-height: 1.08 !important;
        margin-bottom: 2px !important;
    }}

    .sidebar-brand p {{
        font-size: 12px !important;
        margin-top: 6px !important;
        margin-bottom: 10px !important;
    }}

    [data-testid="stSidebar"] .stRadio > label {{
        margin-bottom: 5px !important;
        font-size: 12px !important;
    }}

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] {{
        gap: 0.28rem !important;
    }}

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {{
        padding: 5px 8px !important;
        margin-bottom: 2px !important;
        min-height: 34px !important;
    }}

    [data-testid="stSidebar"] hr {{
        margin: 12px 0 14px 0 !important;
    }}

    .sidebar-summary-title {{
        margin-bottom: 10px !important;
        font-size: 11px !important;
        letter-spacing: 0.08em !important;
    }}

    .sidebar-summary-item {{
        margin-bottom: 16px !important;
        font-size: 12px !important;
        line-height: 1.45 !important;
    }}

    .sidebar-summary-value {{
        font-size: 14px !important;
        margin-top: 6px !important;
        line-height: 1.4 !important;
        color: #ffffff !important;
    }}

    [data-testid="stSidebar"] .stSelectbox label {{
        font-size: 12px !important;
        margin-bottom: 6px !important;
    }}

    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] {{
        min-height: 46px !important;
        margin-bottom: 8px !important;
    }}

    </style>
    """, unsafe_allow_html=True)


def render_neon_mouse_effects():
    components.html(
        """
        <script>
        (function () {
            const doc = window.parent.document;
            if (doc.getElementById("neon-cursor-glow")) return;

            const glow = doc.createElement("div");
            glow.id = "neon-cursor-glow";
            glow.className = "neon-cursor-glow";
            doc.body.appendChild(glow);

            let lastX = 0;
            let lastY = 0;
            let lastTrail = 0;
            let lastComet = 0;

            function makeTrail(x, y) {
                const dot = doc.createElement("div");
                dot.className = "neon-trail-dot";
                dot.style.left = x + "px";
                dot.style.top = y + "px";
                doc.body.appendChild(dot);
                setTimeout(() => dot.remove(), 800);
            }

            function makeComet(x, y, angle) {
                const comet = doc.createElement("div");
                comet.className = "neon-comet";
                comet.style.left = x + "px";
                comet.style.top = y + "px";
                comet.style.setProperty("--angle", angle + "rad");
                doc.body.appendChild(comet);
                setTimeout(() => comet.remove(), 650);
            }

            doc.addEventListener("mousemove", function (e) {
                const x = e.clientX;
                const y = e.clientY;
                const now = Date.now();

                glow.style.opacity = "1";
                glow.style.left = x + "px";
                glow.style.top = y + "px";

                const dx = x - lastX;
                const dy = y - lastY;
                const speed = Math.sqrt(dx * dx + dy * dy);

                if (now - lastTrail > 24) {
                    makeTrail(x, y);
                    lastTrail = now;
                }

                if (speed > 28 && now - lastComet > 90) {
                    makeComet(x, y, Math.atan2(dy, dx));
                    lastComet = now;
                }

                lastX = x;
                lastY = y;
            });

            doc.addEventListener("mouseleave", function () {
                glow.style.opacity = "0";
            });

            doc.addEventListener("click", function (e) {
                const ring = doc.createElement("div");
                ring.className = "neon-click-ring";
                ring.style.left = e.clientX + "px";
                ring.style.top = e.clientY + "px";
                doc.body.appendChild(ring);
                setTimeout(() => ring.remove(), 750);
            });
        })();
        </script>
        """,
        height=0,
        width=0,
    )


# FIX: lock_sidebar_open removed — it was hiding the native Streamlit
# collapse arrow on hover via a setInterval that matched "collapse"/"sidebar"
# in button aria-labels. The custom toggle button in the main area handles
# show/hide instead.
def lock_sidebar_open():
    pass


def force_sidebar_visible():
    pass


# =========================
# HELPER FUNCTIONS
# =========================
# Change these paths to your own custom icon files when ready.
# Example: put icons inside an /assets folder, then use "assets/investors.png".
ICON_TOTAL_INVESTORS = "./icons/audience.png"
ICON_DUPLICATES = "./icons/documentation.png"
ICON_HIGH_PRIORITY = "./icons/crisis.png"
ICON_LOCATIONS = "./icons/placeholder.png"
ICON_EMAILS = "./icons/mail.png"
ICON_AVG_SCORE = "./icons/growth.png"


def kpi_card(label, value, help_text="", emoji="📊", icon_class="kpi-icon-blue"):
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-icon {icon_class}">
            <span style="font-size:28px;">{emoji}</span>
        </div>
        <div class="kpi-content">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            <div class="kpi-help">{help_text}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def style_plotly_chart(fig, height=285):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e5e7eb", size=11),
        height=height,
        margin=dict(l=10, r=10, t=15, b=10),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#e5e7eb", size=10), orientation="v"),
        title=""
    )
    fig.update_xaxes(gridcolor="rgba(148,163,184,0.15)", tickfont=dict(size=9))
    fig.update_yaxes(gridcolor="rgba(148,163,184,0.15)", tickfont=dict(size=9))
    return fig


def clean_domain(website):
    if pd.isna(website) or website == "":
        return ""
    website = str(website).strip()
    website = website.replace("https://", "").replace("http://", "")
    website = website.replace("www.", "")
    website = website.split("/")[0]
    return website


def generate_generic_email(domain):
    return "" if domain == "" else f"info@{domain}"


def generate_contact_email(domain):
    return "" if domain == "" else f"contact@{domain}"


def generate_linkedin_search(investor):
    if pd.isna(investor) or investor == "":
        return ""
    keyword = quote(str(investor).strip())
    return f"https://www.linkedin.com/search/results/all/?keywords={keyword}"


def generate_contact_page(domain):
    return "" if domain == "" else f"https://{domain}/contact"


def normalize_company_website_url(website):
    """Turn a messy website/domain cell into a usable homepage URL."""
    if pd.isna(website) or str(website).strip() == "":
        return ""

    website = str(website).strip()
    if website.lower() in ["nan", "none", "null", "n/a", "na", "not found", "no input"]:
        return ""

    # If the Website column accidentally contains a LinkedIn URL, keep it out of scraping.
    if "linkedin.com" in website.lower():
        return ""

    if not website.startswith(("http://", "https://")):
        website = "https://" + website

    parsed = urlparse(website)
    if not parsed.netloc:
        return ""

    return website.rstrip("/")


def decode_cfemail(encoded_string):
    """Decode Cloudflare-protected email strings from /cdn-cgi/l/email-protection."""
    try:
        encoded_string = encoded_string.strip().split("#")[-1]
        key = int(encoded_string[:2], 16)
        return "".join(chr(int(encoded_string[i:i + 2], 16) ^ key) for i in range(2, len(encoded_string), 2))
    except Exception:
        return ""


def deobfuscate_email_text(text):
    """Convert common website obfuscations like name [at] domain [dot] com into normal emails."""
    if not text:
        return ""

    text = html.unescape(unquote(str(text)))
    replacements = [
        (r"\s*\[\s*at\s*\]\s*", "@"),
        (r"\s*\(\s*at\s*\)\s*", "@"),
        (r"\s+at\s+", "@"),
        (r"\s*\[\s*dot\s*\]\s*", "."),
        (r"\s*\(\s*dot\s*\)\s*", "."),
        (r"\s+dot\s+", "."),
    ]
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text, flags=re.I)
    return text


def is_probably_bad_email(email):
    """Filter false positives from images, placeholders, examples, scripts, and tracking text."""
    email = str(email).strip().lower()
    if not email or "@" not in email:
        return True

    blocked_parts = [
        ".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg", ".ico", ".css", ".js",
        "example.com", "email.com", "domain.com", "yourdomain", "your-email", "youremail",
        "name@", "test@", "no-reply@", "noreply@", "donotreply@", "sentry.io",
        "wixpress.com", "wordpress.com", "schema.org"
    ]
    if any(part in email for part in blocked_parts):
        return True

    # Avoid emails accidentally glued to long script/CSS strings.
    if len(email) > 90:
        return True

    return False


def score_company_email(email, base_domain=""):
    """Higher score = better public company email candidate."""
    email = str(email).strip().lower()
    local_part = email.split("@")[0]
    email_domain = email.split("@")[-1] if "@" in email else ""
    score = 0

    priority_locals = [
        "contact", "info", "hello", "team", "enquiry", "enquiries", "inquiry", "inquiries",
        "support", "admin", "office", "business", "partnership", "partnerships", "investor",
        "investors", "ir", "sales", "bd", "corporate", "general"
    ]
    lower_priority_locals = ["careers", "jobs", "hr", "privacy", "legal", "press", "media", "marketing"]

    for keyword in priority_locals:
        if local_part == keyword or local_part.startswith(keyword + ".") or local_part.startswith(keyword + "-"):
            score += 80
            break
        elif keyword in local_part:
            score += 35

    if any(keyword in local_part for keyword in lower_priority_locals):
        score -= 25

    # Prefer emails on the same company domain where possible.
    if base_domain and email_domain:
        base_domain = base_domain.replace("www.", "")
        if email_domain == base_domain or email_domain.endswith("." + base_domain):
            score += 70
        elif base_domain.endswith(email_domain) or email_domain.endswith(base_domain.split(".")[-2] + "." + base_domain.split(".")[-1]):
            score += 35

    # Generic company inboxes are usually better than personal emails for "Company Email".
    if re.match(r"^[a-z]+\.[a-z]+$", local_part) or re.match(r"^[a-z][a-z]+$", local_part):
        score -= 5

    return score


def extract_emails_from_html(soup, raw_html):
    """Extract normal, mailto, Cloudflare, and lightly obfuscated emails from one page."""
    found_emails = []
    email_pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

    for mailto in soup.select('a[href^="mailto:"]'):
        email = mailto.get("href", "").replace("mailto:", "").split("?")[0].strip()
        if email:
            found_emails.append(email)

    for cf_tag in soup.select("[data-cfemail]"):
        decoded = decode_cfemail(cf_tag.get("data-cfemail", ""))
        if decoded:
            found_emails.append(decoded)

    for href_tag in soup.select('a[href*="/cdn-cgi/l/email-protection"]'):
        decoded = decode_cfemail(href_tag.get("href", ""))
        if decoded:
            found_emails.append(decoded)

    page_text = soup.get_text(" ")
    searchable_text = " ".join([raw_html or "", page_text or ""])
    searchable_text = deobfuscate_email_text(searchable_text)
    found_emails.extend(re.findall(email_pattern, searchable_text))

    cleaned_emails = []
    for email in found_emails:
        email = html.unescape(unquote(str(email))).strip().strip(".,;:()[]{}<>\"'").lower()
        if not is_probably_bad_email(email) and email not in cleaned_emails:
            cleaned_emails.append(email)

    return cleaned_emails


def get_relevant_internal_links(soup, current_url, base_domain):
    """Find likely contact/about/team pages from the current page only."""
    relevant_keywords = [
        "contact", "contact-us", "about", "about-us", "team", "people", "leadership", "management",
        "office", "location", "locations", "imprint", "legal", "privacy", "company", "who-we-are"
    ]
    skip_extensions = (".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".zip", ".jpg", ".jpeg", ".png", ".gif", ".svg", ".webp")
    links = []

    for tag in soup.select("a[href]"):
        href = tag.get("href", "").strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:", "#")):
            continue

        absolute_url = urljoin(current_url, href).split("#")[0].rstrip("/")
        parsed = urlparse(absolute_url)
        link_domain = parsed.netloc.lower().replace("www.", "")
        path = parsed.path.lower()

        if not parsed.scheme.startswith("http"):
            continue
        if link_domain != base_domain and not link_domain.endswith("." + base_domain):
            continue
        if path.endswith(skip_extensions):
            continue
        if any(keyword in path for keyword in relevant_keywords):
            links.append(absolute_url)

    return links


def scrape_company_email_from_website(website, max_pages=24):
    """
    Deeper public website email scan.
    This does NOT use Hunter.io and does NOT check Email 1 / 1st PiC restrictions.

    What it scans:
    - homepage
    - common contact/about/team/office pages
    - relevant internal links discovered from those pages
    - mailto links, visible text emails, Cloudflare-protected emails, and simple [at]/[dot] obfuscations
    """
    homepage = normalize_company_website_url(website)
    if not homepage:
        return ""

    parsed_home = urlparse(homepage)
    base_domain = parsed_home.netloc.lower().replace("www.", "")
    root = f"{parsed_home.scheme}://{parsed_home.netloc}".rstrip("/")

    common_paths = [
        "", "contact", "contact-us", "contacts", "about", "about-us", "team", "people",
        "leadership", "management", "company", "who-we-are", "office", "locations",
        "imprint", "legal", "privacy", "support"
    ]

    urls_to_visit = []
    for path in common_paths:
        url = root if path == "" else f"{root}/{path}"
        if url not in urls_to_visit:
            urls_to_visit.append(url)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    })

    visited = set()
    found_emails = []

    while urls_to_visit and len(visited) < max_pages:
        url = urls_to_visit.pop(0)
        if url in visited:
            continue
        visited.add(url)

        try:
            response = session.get(url, timeout=10, allow_redirects=True)
            if response.status_code >= 400:
                continue

            content_type = response.headers.get("Content-Type", "").lower()
            if "text/html" not in content_type and "application/xhtml" not in content_type and content_type != "":
                continue

            soup = BeautifulSoup(response.text, "html.parser")
            found_emails.extend(extract_emails_from_html(soup, response.text))

            for link in get_relevant_internal_links(soup, response.url, base_domain):
                if link not in visited and link not in urls_to_visit and len(urls_to_visit) < max_pages * 2:
                    urls_to_visit.append(link)

        except Exception:
            continue

    cleaned_emails = []
    for email in found_emails:
        email = str(email).strip().lower()
        if email not in cleaned_emails:
            cleaned_emails.append(email)

    if not cleaned_emails:
        return ""

    cleaned_emails = sorted(
        cleaned_emails,
        key=lambda candidate: score_company_email(candidate, base_domain),
        reverse=True
    )
    return cleaned_emails[0]

def get_best_company_email(row):
    website_email = str(row.get("Website Email", "")).strip()
    original_email = str(row.get("Email 1", "")).strip()
    domain = str(row.get("Domain", "")).strip()

    if website_email:
        return website_email

    if original_email:
        return original_email

    if domain:
        return generate_contact_email(domain)

    return ""


def find_all_company_emails_from_websites(dataframe):
    """
    Bulk company email lookup.
    This is NOT Hunter.io and does NOT use credits.
    It scans every row that has a usable website / Hunter company website,
    regardless of whether Email 1 or 1st PiC already exists.

    Hunter remains restricted separately:
    - Hunter only runs when 1st PiC OR Email 1 is missing.
    - Company email scan runs across all available company websites.
    """
    results = {}

    if dataframe is None or dataframe.empty:
        return results

    rows_to_process = []
    seen_investors = set()

    for _, row in dataframe.iterrows():
        investor_name = str(row.get("Investor", "")).strip()

        # Prefer original Website. If missing, fall back to Hunter Company Website if it already exists.
        website = str(row.get("Website", "")).strip()
        hunter_company_website = str(row.get("Hunter Company Website", "")).strip()

        website_to_scan = website or hunter_company_website

        # Skip empty/invalid values only. Do NOT skip just because Email 1 or Company Email already exists.
        if (
            investor_name
            and website_to_scan
            and website_to_scan.lower() not in ["nan", "none", "null", "n/a", "na", "not found", "no input"]
            and investor_name not in seen_investors
        ):
            rows_to_process.append((investor_name, website_to_scan))
            seen_investors.add(investor_name)

    if not rows_to_process:
        st.session_state.persistent_neon_message = """
        <div class="neon-blue-message">
            ⚡ No company websites found to scan. Please make sure the Website column has valid URLs.
        </div>
        """
        return results

    progress_bar = st.progress(0)
    status_text = st.empty()
    total_rows = len(rows_to_process)

    for position, (investor_name, website) in enumerate(rows_to_process, start=1):
        status_text.caption(f"Scanning company website {position}/{total_rows}: {investor_name}")
        found_email = scrape_company_email_from_website(website)

        # Store result for every scanned investor so the app can show successful scans and blanks clearly.
        results[investor_name] = {
            "Company Email": found_email,
            "Company Email Source": website if found_email else "No public company email found on website/contact/about pages"
        }

        progress_bar.progress(position / total_rows)
        time.sleep(0.10)

    status_text.caption("Bulk company email scan completed.")
    return results




def hunter_company_find(domain):
    if domain == "":
        return {
            "Hunter Company Website": "",
            "Hunter Company Name": "",
            "Hunter Company LinkedIn": "",
            "Hunter Company Source": ""
        }

    try:
        api_key = st.secrets["HUNTER_API_KEY"]
    except Exception:
        return {
            "Hunter Company Website": "",
            "Hunter Company Name": "",
            "Hunter Company LinkedIn": "",
            "Hunter Company Source": "Missing HUNTER_API_KEY in secrets.toml"
        }

    url = "https://api.hunter.io/v2/companies/find"
    params = {
        "domain": domain,
        "api_key": api_key
    }

    try:
        response = requests.get(url, params=params, timeout=12)

        if response.status_code != 200:
            return {
                "Hunter Company Website": "",
                "Hunter Company Name": "",
                "Hunter Company LinkedIn": "",
                "Hunter Company Source": f"Hunter Company API error {response.status_code}"
            }

        data = response.json().get("data", {})

        if not data:
            return {
                "Hunter Company Website": "",
                "Hunter Company Name": "",
                "Hunter Company LinkedIn": "",
                "Hunter Company Source": "No Hunter company result found"
            }

        hunter_domain = data.get("domain", "") or domain
        hunter_website = data.get("website", "") or data.get("url", "") or hunter_domain

        if hunter_website and not str(hunter_website).startswith(("http://", "https://")):
            hunter_website = f"https://{hunter_website}"

        linkedin_raw = data.get("linkedin", "") or data.get("linkedin_url", "")

        # Hunter sometimes returns LinkedIn as a dict like {"handle": "company/500global"}.
        # Convert that into a proper clickable LinkedIn URL.
        if isinstance(linkedin_raw, dict):
            linkedin_handle = linkedin_raw.get("handle", "") or linkedin_raw.get("url", "")
        else:
            linkedin_handle = str(linkedin_raw or "")

        if linkedin_handle and linkedin_handle.startswith("http"):
            linkedin = linkedin_handle
        elif linkedin_handle:
            linkedin = f"https://www.linkedin.com/{linkedin_handle.lstrip('/')}"
        else:
            linkedin = ""

        return {
            "Hunter Company Website": hunter_website,
            "Hunter Company Name": data.get("name", ""),
            "Hunter Company LinkedIn": linkedin,
            "Hunter Company Source": "Hunter companies/find"
        }

    except Exception as e:
        return {
            "Hunter Company Website": "",
            "Hunter Company Name": "",
            "Hunter Company LinkedIn": "",
            "Hunter Company Source": str(e)
        }


def hunter_domain_search(domain):
    company_result = hunter_company_find(domain)

    empty_result = {
        "Hunter Email": "",
        "Hunter Name": "",
        "Hunter Position": "",
        "Hunter LinkedIn": "",
        "Hunter Confidence": "",
        "Hunter Source": ""
    }
    empty_result.update(company_result)

    if domain == "":
        return empty_result

    try:
        api_key = st.secrets["HUNTER_API_KEY"]
    except Exception:
        empty_result["Hunter Source"] = "Missing HUNTER_API_KEY in secrets.toml"
        return empty_result

    url = "https://api.hunter.io/v2/domain-search"
    params = {
        "domain": domain,
        "api_key": api_key,
        "limit": 10
    }

    try:
        response = requests.get(url, params=params, timeout=12)

        if response.status_code != 200:
            empty_result["Hunter Source"] = f"Hunter Domain API error {response.status_code}"
            return empty_result

        data = response.json().get("data", {})
        emails = data.get("emails", [])

        if not emails:
            empty_result["Hunter Source"] = "No Hunter email result found"
            return empty_result

        best_email = None

        for item in emails:
            email_type = str(item.get("type", "")).lower()
            confidence = item.get("confidence") or 0
            if email_type == "personal" and confidence >= 50:
                best_email = item
                break

        if best_email is None:
            best_email = sorted(emails, key=lambda x: x.get("confidence") or 0, reverse=True)[0]

        first_name = best_email.get("first_name") or ""
        last_name = best_email.get("last_name") or ""
        full_name = f"{first_name} {last_name}".strip()

        sources = best_email.get("sources", [])
        source_url = sources[0].get("uri", "") if sources else "Hunter.io"

        enriched_result = {
            "Hunter Email": best_email.get("value", ""),
            "Hunter Name": full_name,
            "Hunter Position": best_email.get("position", ""),
            "Hunter LinkedIn": best_email.get("linkedin", ""),
            "Hunter Confidence": str(best_email.get("confidence", "")),
            "Hunter Source": source_url
        }
        enriched_result.update(company_result)
        return enriched_result

    except Exception as e:
        empty_result["Hunter Source"] = str(e)
        return empty_result

def enrich_single_investor_with_hunter(row):
    domain = str(row.get("Domain", "")).strip()
    return hunter_domain_search(domain)


def enrich_all_investors_with_hunter(dataframe):
    """
    Smart Hunter.io bulk enrichment.
    Only processes rows where 1st PiC OR Email 1 is blank.
    This saves Hunter credits and avoids re-enriching complete records.
    """
    results = {}
    domain_cache = {}

    if dataframe is None or dataframe.empty:
        return results

    rows_to_process = []
    for _, row in dataframe.iterrows():
        investor_name = str(row.get("Investor", "")).strip()
        domain = str(row.get("Domain", "")).strip()
        first_pic = str(row.get("1st PiC", "")).strip()
        email_1 = str(row.get("Email 1", "")).strip()

        if investor_name and (not first_pic or not email_1):
            rows_to_process.append((investor_name, domain, row))

    if not rows_to_process:
        st.session_state.persistent_neon_message = """
        <div class="neon-blue-message">
            ⚡ No missing PIC/email records found — every row already has both 1st PiC and Email 1.
        </div>
        """
        return results

    total_rows = len(rows_to_process)
    progress_bar = st.progress(0)
    status_text = st.empty()

    for position, (investor_name, domain, row) in enumerate(rows_to_process, start=1):
        status_text.caption(f"Finding missing PIC/email {position}/{total_rows}: {investor_name}")

        if domain:
            if domain not in domain_cache:
                domain_cache[domain] = hunter_domain_search(domain)
                time.sleep(0.20)
            results[investor_name] = domain_cache[domain]
        else:
            results[investor_name] = {
                "Hunter Email": "",
                "Hunter Name": "",
                "Hunter Position": "",
                "Hunter LinkedIn": "",
                "Hunter Confidence": "",
                "Hunter Source": "Missing domain",
                "Hunter Company Website": "",
                "Hunter Company Name": "",
                "Hunter Company LinkedIn": "",
                "Hunter Company Source": "Missing domain"
            }

        progress_bar.progress(position / total_rows)

    status_text.caption("Hunter.io missing PIC/email enrichment completed.")
    return results


def has_value(value):
    """Return True when a cell has meaningful text/data."""
    if pd.isna(value):
        return False
    value = str(value).strip()
    return value != "" and value.lower() not in ["nan", "none", "null", "n/a", "na"]


def calculate_score(row):
    """
    Outreach Readiness Score.
    This is intentionally based on data completeness, not investor attractiveness.
    It answers: "Is this record complete enough for an analyst to use for outreach?"

    Weighting:
    - Email 1: 30
    - 1st PiC: 20
    - Investment Thesis: 20
    - Website: 15
    - Type: 10
    - Location: 5
    Total: 100
    """
    score = 0

    if has_value(row.get("Email 1", "")):
        score += 30
    if has_value(row.get("1st PiC", "")):
        score += 20
    if has_value(row.get("Investment Thesis", "")):
        score += 20
    if has_value(row.get("Website", "")):
        score += 15
    if has_value(row.get("Type", "")):
        score += 10
    if has_value(row.get("Location", "")):
        score += 5

    return min(score, 100)


def assign_priority(score):
    """Keep the existing column name as Priority for compatibility, but use readiness labels."""
    if score >= 80:
        return "Ready"
    elif score >= 50:
        return "Partial"
    return "Needs Research"


def get_missing_readiness_fields(row):
    missing = []
    checks = [
        ("Email", "Email 1"),
        ("Contact", "1st PiC"),
        ("Thesis", "Investment Thesis"),
        ("Website", "Website"),
        ("Type", "Type"),
        ("Location", "Location"),
    ]

    for label, col in checks:
        if not has_value(row.get(col, "")):
            missing.append(label)

    return "Complete" if not missing else ", ".join(missing)


def create_email_subject(row):
    investor = row.get("Investor", "")
    return f"Potential collaboration with {investor}"


def create_email_body(row):
    contact_name = str(row.get("1st PiC", "")).strip()
    investor = str(row.get("Investor", "")).strip()
    thesis = str(row.get("Investment Thesis", "")).strip()

    greeting = "Hi," if contact_name == "" or contact_name.lower() == "team" else f"Hi {contact_name},"

    return f"""{greeting}

I hope you're doing well.

I'm reaching out regarding {investor}. Based on your investment focus around {thesis}, I thought there may be potential alignment for a relevant opportunity we are currently reviewing.

Would you be open to a short introductory discussion?

Best regards,
Thet
"""


def get_first_name(name):
    name = str(name).strip()
    if not name or name.lower() in ["nan", "none", "not found", "no input", "team"]:
        return ""
    return name.split()[0]


def render_email_template(template, row, sender_name, sender_company):
    first_name = get_first_name(row.get("1st PiC", "")) or get_first_name(row.get("Hunter Name", ""))
    greeting = f"Hi {first_name}," if first_name else "Hi,"

    values = {
        "greeting": greeting,
        "investor": str(row.get("Investor", "")).strip(),
        "investment_thesis": str(row.get("Investment Thesis", "")).strip(),
        "type": str(row.get("Type", "")).strip(),
        "location": str(row.get("Location", "")).strip(),
        "sender_name": sender_name,
        "sender_company": sender_company,
    }

    for key, value in values.items():
        template = template.replace("{" + key + "}", value)

    return template


def send_email_smtp(smtp_server, smtp_port, sender_email, password, recipient, subject, body, cc=""):
    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = recipient
    if cc.strip():
        msg["Cc"] = cc
    msg["Subject"] = subject
    msg.set_content(body)

    recipients = [recipient]
    if cc.strip():
        recipients += [x.strip() for x in cc.split(",") if x.strip()]

    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.send_message(msg, to_addrs=recipients)


def priority_badge(priority):
    priority_text = str(priority).strip().lower()
    if priority_text in ["ready", "high"]:
        return '<span class="badge badge-low">Ready</span>' if priority_text == "ready" else '<span class="badge badge-high">High</span>'
    if priority_text in ["partial", "medium"]:
        return '<span class="badge badge-medium">Partial</span>' if priority_text == "partial" else '<span class="badge badge-medium">Medium</span>'
    if priority_text in ["needs research", "low"]:
        return '<span class="badge badge-high">Needs Research</span>' if priority_text == "needs research" else '<span class="badge badge-low">Low</span>'
    return str(priority)


def render_priority_table(dataframe):
    display_df = dataframe.copy()
    if "Priority" in display_df.columns:
        display_df["Priority"] = display_df["Priority"].apply(priority_badge)
        display_df = display_df.rename(columns={"Priority": "Readiness"})
    if "Score" in display_df.columns:
        display_df = display_df.rename(columns={"Score": "Readiness Score"})

    html = display_df.to_html(index=False, escape=False)
    st.markdown(
        f"""
        <div class="data-readiness-table-wrap">
            {html}
        </div>
        """,
        unsafe_allow_html=True
    )




def get_cleaned_tracker_export_df(dataframe):
    """
    Cleaned Tracker display/export version.
    Keeps internal helper fields available in the app, but removes generated research columns
    that should not appear in the cleaned Excel/CSV output.
    """
    hidden_cols = ["Domain", "Possible Contact Page", "LinkedIn Search"]
    return dataframe.drop(columns=[col for col in hidden_cols if col in dataframe.columns], errors="ignore")


def normalize_column_name(col):
    """Normalize messy column headers for matching."""
    col = "" if pd.isna(col) else str(col)
    col = col.strip().lower()
    col = re.sub(r"[^a-z0-9]+", " ", col)
    return re.sub(r"\s+", " ", col).strip()


STANDARD_COLUMNS = [
    "Investor", "Type", "Location", "Website",
    "1st PiC", "Email 1", "2nd PiC", "Email 2",
    "Investment Thesis", "Status"
]

REQUIRED_IMPORT_COLUMNS = ["Investor"]
IMPORTANT_IMPORT_COLUMNS = ["Investor", "Email 1", "Website", "1st PiC", "Type", "Location", "Investment Thesis"]
OPTIONAL_IMPORT_COLUMNS = ["2nd PiC", "Email 2", "Status"]

COLUMN_ALIASES = {
    # Investor / company / fund name
    "investor": "Investor", "investor name": "Investor", "organisation": "Investor",
    "organization": "Investor", "organisation name": "Investor", "organization name": "Investor",
    "company": "Investor", "company name": "Investor", "company names": "Investor",
    "target company": "Investor", "target": "Investor", "firm": "Investor", "firm name": "Investor",
    "fund": "Investor", "fund name": "Investor", "fund manager": "Investor", "asset manager": "Investor",
    "manager": "Investor", "institution": "Investor", "entity": "Investor", "fof name": "Investor",
    "vc name": "Investor", "gp": "Investor", "general partner firm": "Investor",
    "longlist name": "Investor", "target name": "Investor", "buyer target": "Investor",
    "ma target": "Investor", "m a target": "Investor", "acquisition target": "Investor",
    "portfolio company": "Investor", "business name": "Investor", "client": "Investor",

    # Type
    "type": "Type", "investor type": "Type", "fund type": "Type", "category": "Type",
    "industry": "Type", "sector": "Type", "sub sector": "Type", "business sector": "Type",
    "business type": "Type", "service line": "Type", "solution": "Type", "solutions": "Type",
    "product": "Type", "products": "Type", "specialisation": "Type", "specialization": "Type",
    "classification": "Type", "vertical": "Type", "segment": "Type", "space": "Type",

    # Location
    "location": "Location", "country": "Location", "region": "Location", "geography": "Location",
    "market": "Location", "geo": "Location", "geography focus": "Location", "country region": "Location",
    "hq": "Location", "headquarters": "Location", "office location": "Location",
    "address": "Location", "city": "Location", "base": "Location", "based in": "Location",

    # Website
    "website": "Website", "web site": "Website", "url": "Website", "website url": "Website",
    "company website": "Website", "homepage": "Website", "domain": "Website", "site": "Website",
    "linkedin": "Website", "linked in": "Website", "linkedin url": "Website", "linkedin link": "Website",
    "source url": "Website", "source link": "Website", "profile link": "Website",
    "company link": "Website", "link": "Website", "links": "Website",

    # Primary contact
    "name": "1st PiC", "contact": "1st PiC", "contact name": "1st PiC", "person": "1st PiC",
    "pic": "1st PiC", "1st pic": "1st PiC", "primary contact": "1st PiC", "contact person": "1st PiC",
    "representative": "1st PiC", "partner": "1st PiC", "partner name": "1st PiC", "full name": "1st PiC",
    "contact title": "1st PiC", "key person": "1st PiC", "lead partner": "1st PiC",
    "managing partner": "1st PiC", "founder": "1st PiC", "ceo": "1st PiC", "owner": "1st PiC",
    "decision maker": "1st PiC", "contact 1": "1st PiC", "pic 1": "1st PiC",

    # Primary email
    "email": "Email 1", "email address": "Email 1", "e mail": "Email 1", "mail": "Email 1",
    "contact email": "Email 1", "primary email": "Email 1", "email 1": "Email 1", "1st email": "Email 1",
    "pic email": "Email 1", "contact email 1": "Email 1", "email of 1st pic": "Email 1",
    "1st pic email": "Email 1", "first pic email": "Email 1", "work email": "Email 1",
    "business email": "Email 1", "direct email": "Email 1", "recipient email": "Email 1",

    # Secondary contact/email
    "second contact": "2nd PiC", "secondary contact": "2nd PiC", "2nd pic": "2nd PiC",
    "contact 2": "2nd PiC", "second name": "2nd PiC", "secondary name": "2nd PiC", "pic 2": "2nd PiC",
    "secondary email": "Email 2", "second email": "Email 2", "email 2": "Email 2", "2nd email": "Email 2",
    "contact email 2": "Email 2", "email of 2nd pic": "Email 2", "2nd pic email": "Email 2",
    "second pic email": "Email 2", "alternate email": "Email 2", "alternative email": "Email 2",

    # Thesis / notes
    "investment thesis": "Investment Thesis", "thesis": "Investment Thesis", "focus": "Investment Thesis",
    "investment focus": "Investment Thesis", "mandate": "Investment Thesis", "strategy": "Investment Thesis",
    "notes": "Investment Thesis", "note": "Investment Thesis", "description": "Investment Thesis",
    "remarks": "Investment Thesis", "comment": "Investment Thesis", "comments": "Investment Thesis",
    "memo": "Investment Thesis", "criteria": "Investment Thesis", "strategic fit": "Investment Thesis",
    "fit": "Investment Thesis", "synergy": "Investment Thesis", "potential synergy": "Investment Thesis",
    "rationale": "Investment Thesis", "investment rationale": "Investment Thesis",
    "reason": "Investment Thesis", "why relevant": "Investment Thesis", "target rationale": "Investment Thesis",
    "sector focus": "Investment Thesis", "past investment": "Investment Thesis", "portfolio": "Investment Thesis",
    "maximum check": "Investment Thesis", "max check": "Investment Thesis", "check size": "Investment Thesis",
    "ticket size": "Investment Thesis", "investment size": "Investment Thesis", "revenue": "Investment Thesis",
    "employees": "Investment Thesis", "source": "Investment Thesis",

    # Status
    "status": "Status", "outreach status": "Status", "stage": "Status", "progress": "Status",
    "follow up": "Status", "follow up status": "Status", "contacted status": "Status",
    "reply status": "Status", "email status": "Status", "pipeline status": "Status",
}

HEADER_KEYWORDS = set(COLUMN_ALIASES.keys()) | {
    "email", "organization", "organisation", "company", "fund", "name", "type", "title",
    "notes", "note", "source", "website", "location", "sector", "industry", "partner", "country", "url", "link", "linkedin", "strategic fit", "investment thesis", "status", "maximum check"
}

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
URL_RE = re.compile(r"(https?://|www\.|linkedin\.com|[A-Za-z0-9-]+\.(com|co|io|ai|net|org|vc|sg|jp|vn|uk|de|fr|id|my|th|ph|au|hk)(/|\b))", re.I)
BAD_INVESTOR_HEADERS = {"no", "no.", "number", "s n", "sn", "sno", "id", "index", "rank", "#"}
STATUS_WORDS = {"not contacted", "contacted", "follow up", "follow-up", "sent", "replied", "meeting", "rejected", "interested", "pending", "done"}
COMMON_COUNTRIES = {
    "singapore", "japan", "vietnam", "viet nam", "usa", "us", "united states", "uk", "united kingdom",
    "hong kong", "china", "india", "indonesia", "malaysia", "thailand", "philippines", "korea",
    "south korea", "taiwan", "australia", "germany", "france", "netherlands", "switzerland", "canada"
}


BUSINESS_NAME_TERMS = {
    "ventures", "venture", "capital", "partners", "partner", "fund", "funds", "management",
    "asset", "assets", "holdings", "holding", "group", "company", "limited", "ltd", "pte",
    "inc", "corp", "corporation", "llc", "lp", "llp", "gmbh", "plc", "jsc", "co ltd",
    "equity", "private equity", "investment", "investments", "advisory", "advisors",
    "finance", "financial", "bank", "systems", "technologies", "technology", "software",
    "solutions", "services", "consulting", "infrastructure", "logistics", "warehouse",
    "foods", "seafood", "retail", "industries", "international", "global", "asia"
}

PERSON_TITLE_TERMS = {
    "partner", "director", "manager", "analyst", "associate", "principal", "founder",
    "ceo", "cfo", "cto", "head", "vp", "president", "officer", "chairman"
}

THESIS_HEADER_TERMS = {
    "strategic fit", "fit", "synergy", "potential synergy", "investment thesis", "thesis",
    "investment focus", "focus", "mandate", "strategy", "rationale", "description", "notes",
    "note", "remarks", "comments", "memo", "criteria", "sector focus", "past investment",
    "portfolio", "maximum check", "max check", "check size", "ticket size", "investment size"
}

IGNORE_AS_THESIS_HEADERS = {
    "no", "no.", "number", "#", "id", "rank"
}


def safe_text_series(series):
    return series.fillna("").astype(str).replace({"nan": "", "None": "", "NaN": ""})



def clean_cell_value(value):
    """Clean one Excel cell into safe text."""
    if pd.isna(value):
        return ""
    value = str(value).strip()
    if value.lower() in ["nan", "none", "null", "n/a", "na"]:
        return ""
    return re.sub(r"\s+", " ", value).strip()


def extract_emails_from_text(text):
    """Extract all emails from any messy text/cell/row."""
    text = "" if pd.isna(text) else str(text)
    emails = EMAIL_RE.findall(text)
    cleaned = []
    for email in emails:
        email = str(email).strip().strip(".,;:()[]{}<>").lower()
        if email and email not in cleaned:
            cleaned.append(email)
    return cleaned


def extract_urls_from_text(text):
    """Extract website/linkedin/domain-like URLs from messy text."""
    text = "" if pd.isna(text) else str(text)
    url_pattern = re.compile(
        r"((?:https?://|www\.)[^\s,;]+|(?:[A-Za-z0-9-]+\.)+(?:com|co|io|ai|net|org|vc|sg|jp|vn|uk|de|fr|id|my|th|ph|au|hk)(?:/[^\s,;]*)?)",
        re.I,
    )
    urls = []
    for match in url_pattern.findall(text):
        url = str(match).strip().strip(".,;:()[]{}<>")
        if not url:
            continue
        if "@" in url:
            continue
        if not url.startswith(("http://", "https://")):
            url = "https://" + url.lstrip("/")
        if url not in urls:
            urls.append(url)
    return urls


def is_blankish(value):
    return clean_cell_value(value) == ""


def is_bad_investor_value(value):
    v = normalize_column_name(value)
    if not v:
        return True
    if v in BAD_INVESTOR_HEADERS:
        return True
    if re.fullmatch(r"[0-9,\.\-]+", v):
        return True
    if EMAIL_RE.search(str(value)) or URL_RE.search(str(value)):
        return True
    if len(v) <= 1:
        return True
    return False


def looks_like_person_name(value):
    """Basic person-name heuristic so people do not become Investor."""
    value = clean_cell_value(value)
    if not value or EMAIL_RE.search(value) or URL_RE.search(value):
        return False
    words = value.split()
    if len(words) < 2 or len(words) > 4:
        return False
    business_terms = ["capital", "ventures", "partners", "fund", "management", "group", "holdings", "company", "corp", "llc", "ltd", "pte", "inc", "bank"]
    if any(term in value.lower() for term in business_terms):
        return False
    return all(w[:1].isupper() for w in words if w[:1].isalpha())


def business_name_ratio(series):
    """How much a column looks like company/fund/target names."""
    vals = [clean_cell_value(v).lower() for v in column_sample(series)]
    if not vals:
        return 0
    hits = 0
    for v in vals:
        if EMAIL_RE.search(v) or URL_RE.search(v) or re.fullmatch(r"[0-9,\.\-\s]+", v):
            continue
        if any(term in v for term in BUSINESS_NAME_TERMS):
            hits += 1
        elif len(v.split()) <= 6 and not looks_like_person_name(v):
            hits += 0.35
    return hits / len(vals)


def person_name_ratio(series):
    """How much a column looks like contact person names."""
    vals = column_sample(series)
    if not vals:
        return 0
    hits = 0
    for v in vals:
        clean = clean_cell_value(v)
        lower = clean.lower()
        if looks_like_person_name(clean):
            hits += 1
        elif any(title in lower for title in PERSON_TITLE_TERMS) and not any(term in lower for term in BUSINESS_NAME_TERMS):
            hits += 0.3
    return hits / len(vals)


def compact_join_unique(values, max_parts=4):
    parts = []
    for value in values:
        value = clean_cell_value(value)
        if not value:
            continue
        if value.lower() in ["nan", "none", "null"]:
            continue
        if value not in parts:
            parts.append(value)
    return " | ".join(parts[:max_parts])


def choose_first_nonempty_from_columns(row, columns):
    for col in columns:
        if col in row.index:
            val = clean_cell_value(row.get(col, ""))
            if val:
                return val
    return ""


def best_columns_for_target(df_raw, target, min_score=25):
    scored = []
    for raw_col in df_raw.columns:
        score = score_column_for_target(raw_col, df_raw[raw_col], target)
        if score >= min_score:
            scored.append((score, raw_col))
    scored.sort(reverse=True)
    return [col for _, col in scored]


def extract_fields_rowwise(df_raw, standardized, mapping_used):
    """
    Row-level extractor: after column mapping, scan each whole row to pull key fields.
    This makes messy trackers more accurate because emails/URLs/notes can be extracted
    even when the column names are strange or the mapping is imperfect.
    """
    result = standardized.copy()

    investor_candidates = best_columns_for_target(df_raw, "Investor", min_score=25)
    pic_candidates = best_columns_for_target(df_raw, "1st PiC", min_score=25)
    type_candidates = best_columns_for_target(df_raw, "Type", min_score=25)
    location_candidates = best_columns_for_target(df_raw, "Location", min_score=25)
    thesis_candidates = best_columns_for_target(df_raw, "Investment Thesis", min_score=20)

    # Prefer business-name columns over serial numbers and person-name columns.
    investor_candidates = [
        c for c in investor_candidates
        if normalize_column_name(c) not in BAD_INVESTOR_HEADERS
        and email_ratio(df_raw[c]) < 0.05
        and url_ratio(df_raw[c]) < 0.25
        and numeric_ratio(df_raw[c]) < 0.45
    ]

    for idx, raw_row in df_raw.iterrows():
        row_values = [clean_cell_value(v) for v in raw_row.tolist()]
        row_text = " | ".join([v for v in row_values if v])

        # Emails: extract from the whole row, not just mapped column.
        emails = extract_emails_from_text(row_text)
        if emails:
            if is_blankish(result.at[idx, "Email 1"]):
                result.at[idx, "Email 1"] = emails[0]
            if len(emails) > 1 and is_blankish(result.at[idx, "Email 2"]):
                result.at[idx, "Email 2"] = emails[1]

        # Website/source link: extract from mapped website or whole row.
        current_website = clean_cell_value(result.at[idx, "Website"])
        website_urls = extract_urls_from_text(current_website) or extract_urls_from_text(row_text)
        if website_urls:
            result.at[idx, "Website"] = website_urls[0]

        # Investor: if blank/bad, extract from strongest business-name column.
        current_investor = clean_cell_value(result.at[idx, "Investor"])
        if is_bad_investor_value(current_investor):
            for col in investor_candidates:
                val = clean_cell_value(raw_row.get(col, ""))
                if not is_bad_investor_value(val) and not looks_like_person_name(val):
                    result.at[idx, "Investor"] = val
                    break

        # Contact person: if blank, extract from name/person/partner columns.
        if is_blankish(result.at[idx, "1st PiC"]):
            for col in pic_candidates:
                val = clean_cell_value(raw_row.get(col, ""))
                if val and not EMAIL_RE.search(val) and not URL_RE.search(val) and not re.fullmatch(r"[0-9,\.\-]+", val):
                    # Avoid copying organization name into PIC.
                    if normalize_column_name(val) != normalize_column_name(result.at[idx, "Investor"]):
                        result.at[idx, "1st PiC"] = val
                        break

        # Type/location fallback.
        if is_blankish(result.at[idx, "Type"]):
            result.at[idx, "Type"] = choose_first_nonempty_from_columns(raw_row, type_candidates)
        if is_blankish(result.at[idx, "Location"]):
            result.at[idx, "Location"] = choose_first_nonempty_from_columns(raw_row, location_candidates)

        # Thesis/notes: combine useful text columns; avoid emails/URLs/serial numbers.
        note_parts = []
        existing_thesis = clean_cell_value(result.at[idx, "Investment Thesis"])
        if existing_thesis:
            note_parts.append(existing_thesis)

        for col in thesis_candidates:
            norm_col = normalize_column_name(col)
            val = clean_cell_value(raw_row.get(col, ""))
            if not val:
                continue
            if EMAIL_RE.fullmatch(val) or URL_RE.fullmatch(val):
                continue
            if normalize_column_name(val) == normalize_column_name(result.at[idx, "Investor"]):
                continue
            # Keep standalone numeric values only when the header gives useful context, e.g. Revenue / Employees / Maximum Check.
            if re.fullmatch(r"[0-9,\.\-]+", val) and not any(x in norm_col for x in ["revenue", "employee", "check", "ticket"]):
                continue
            if any(x in norm_col for x in ["revenue", "employee", "maximum check", "max check", "ticket", "check size"]):
                val = f"{col}: {val}"
            if val not in note_parts:
                note_parts.append(val)

        if note_parts:
            result.at[idx, "Investment Thesis"] = " | ".join(note_parts[:4])

    return result


def column_sample(series, n=80):
    return safe_text_series(series).str.strip().replace("", pd.NA).dropna().head(n).tolist()


def email_ratio(series):
    vals = column_sample(series)
    return 0 if not vals else sum(bool(EMAIL_RE.search(v)) for v in vals) / len(vals)


def url_ratio(series):
    vals = column_sample(series)
    return 0 if not vals else sum(bool(URL_RE.search(v)) for v in vals) / len(vals)


def numeric_ratio(series):
    vals = column_sample(series)
    if not vals:
        return 0
    return sum(bool(re.fullmatch(r"[\d,\.\-\s]+", v)) for v in vals) / len(vals)


def country_ratio(series):
    vals = [normalize_column_name(v) for v in column_sample(series)]
    if not vals:
        return 0
    count = 0
    for v in vals:
        if v in COMMON_COUNTRIES or any(country in v for country in COMMON_COUNTRIES):
            count += 1
    return count / len(vals)


def average_words(series):
    vals = column_sample(series)
    if not vals:
        return 0
    return sum(len(str(v).split()) for v in vals) / len(vals)


def header_tokens(raw_col):
    return set(normalize_column_name(raw_col).split())


def score_column_for_target(raw_col, series, target):
    """Score a raw column against a standard app column using header + content patterns."""
    norm = normalize_column_name(raw_col)
    tokens = header_tokens(raw_col)
    vals = column_sample(series)
    e_ratio = email_ratio(series)
    u_ratio = url_ratio(series)
    n_ratio = numeric_ratio(series)
    c_ratio = country_ratio(series)
    avg_words = average_words(series)
    biz_ratio = business_name_ratio(series)
    person_ratio = person_name_ratio(series)
    non_empty = len(vals)
    score = 0

    if not non_empty:
        return -100

    # Never map serial number/index columns to meaningful fields.
    if norm in BAD_INVESTOR_HEADERS or tokens & {"no", "number", "id", "index", "rank"}:
        if target not in []:
            score -= 80

    # Strong exact alias bonus.
    if norm in COLUMN_ALIASES and COLUMN_ALIASES[norm] == target:
        score += 55

    if target == "Email 1":
        score += e_ratio * 100
        if "email" in tokens or "mail" in tokens:
            score += 35
        if any(x in norm for x in ["2", "second", "secondary"]):
            score -= 35
        score -= u_ratio * 20 + n_ratio * 30

    elif target == "Email 2":
        score += e_ratio * 95
        if "email" in tokens or "mail" in tokens:
            score += 25
        if any(x in norm for x in ["2", "second", "secondary"]):
            score += 30
        else:
            score -= 20
        score -= u_ratio * 20 + n_ratio * 30

    elif target == "Website":
        score += u_ratio * 100
        if tokens & {"website", "url", "domain", "homepage", "site", "link", "linkedin"}:
            score += 45
        # Source is only website if the content actually contains links.
        if "source" in tokens and u_ratio < 0.25:
            score -= 30
        score -= e_ratio * 25 + n_ratio * 25

    elif target == "Investor":
        if tokens & {"organization", "organisation", "company", "firm", "fund", "investor", "entity", "manager", "institution", "gp", "target", "client"}:
            score += 60
        if norm in ["name", "fund name", "company name", "organisation name", "organization name", "investor name", "target name", "business name"]:
            score += 35
        # Plain "Name" can be a company column in target longlists, but a person column in contact lists.
        if norm == "name":
            score += biz_ratio * 70
            score -= person_ratio * 55
        score += biz_ratio * 45
        score -= person_ratio * 35
        if tokens & {"contact", "person", "pic", "email", "title", "role"}:
            score -= 35
        if e_ratio > 0.05 or u_ratio > 0.2 or n_ratio > 0.55:
            score -= 65
        if 1 <= avg_words <= 6:
            score += 15
        if avg_words > 10:
            score -= 10

    elif target == "1st PiC":
        if tokens & {"name", "contact", "person", "partner", "pic", "representative", "founder", "ceo", "owner"}:
            score += 45
        if tokens & {"organization", "organisation", "company", "firm", "fund", "investor", "target"}:
            score -= 45
        score += person_ratio * 55
        score -= biz_ratio * 45
        if any(x in norm for x in ["2", "second", "secondary"]):
            score -= 35
        if e_ratio > 0.05 or u_ratio > 0.05 or n_ratio > 0.25:
            score -= 60
        if 1 <= avg_words <= 4:
            score += 20
        if "title" in tokens or "role" in tokens or "position" in tokens:
            score -= 30

    elif target == "2nd PiC":
        if tokens & {"name", "contact", "person", "partner", "pic", "representative"}:
            score += 35
        if any(x in norm for x in ["2", "second", "secondary"]):
            score += 30
        else:
            score -= 25
        if tokens & {"organization", "organisation", "company", "firm", "fund", "investor"}:
            score -= 45
        if e_ratio > 0.05 or u_ratio > 0.05 or n_ratio > 0.25:
            score -= 60

    elif target == "Type":
        if tokens & {"type", "category", "classification", "sector", "industry", "vertical"}:
            score += 60
        if e_ratio > 0.05 or u_ratio > 0.2 or n_ratio > 0.4:
            score -= 45
        if avg_words <= 5:
            score += 10

    elif target == "Location":
        if tokens & {"location", "country", "region", "geography", "market", "hq", "headquarters", "city", "address", "base"}:
            score += 55
        score += c_ratio * 45
        if e_ratio > 0.05 or u_ratio > 0.15 or n_ratio > 0.45:
            score -= 45
        if avg_words <= 5:
            score += 8

    elif target == "Investment Thesis":
        if tokens & {"thesis", "focus", "strategy", "mandate", "notes", "note", "description", "remarks", "comment", "comments", "criteria", "memo", "fit", "synergy", "rationale", "portfolio"}:
            score += 55
        if norm in THESIS_HEADER_TERMS or any(term in norm for term in THESIS_HEADER_TERMS):
            score += 45
        if "source" in tokens:
            # Source becomes thesis only when it is text notes, not links.
            score += 20 if u_ratio < 0.2 else -35
        if "title" in tokens or "role" in tokens or "position" in tokens:
            score += 8
        if avg_words >= 5:
            score += 18
        if any(term in " ".join([str(v).lower() for v in vals[:15]]) for term in ["synergy", "focus", "investment", "sector", "portfolio", "strategic", "enterprise", "technology", "fintech", "ai", "cloud"]):
            score += 15
        if e_ratio > 0.05 or u_ratio > 0.35 or n_ratio > 0.5:
            score -= 35

    elif target == "Status":
        if tokens & {"status", "stage", "progress"}:
            score += 60
        vals_norm = [normalize_column_name(v) for v in vals]
        if vals_norm:
            score += (sum(any(sw in v for sw in STATUS_WORDS) for v in vals_norm) / len(vals_norm)) * 45
        if e_ratio > 0.05 or u_ratio > 0.1:
            score -= 40

    return score


def guess_standard_column(raw_col):
    """Fast header-only fallback for header row detection."""
    normalized = normalize_column_name(raw_col)
    if normalized in COLUMN_ALIASES:
        return COLUMN_ALIASES[normalized]
    if normalized in BAD_INVESTOR_HEADERS:
        return None
    if any(word in normalized for word in ["email", "e mail", "mail"]):
        return "Email 2" if any(word in normalized for word in ["2", "second", "secondary"]) else "Email 1"
    if any(word in normalized for word in ["website", "url", "domain", "homepage", "linkedin", "link"]):
        return "Website"
    if any(word in normalized for word in ["company", "organization", "organisation", "fund", "firm", "investor"]):
        return "Investor"
    if any(word in normalized for word in ["country", "location", "region", "market", "geography", "hq", "headquarter"]):
        return "Location"
    if any(word in normalized for word in ["thesis", "focus", "strategy", "mandate", "notes", "note", "description", "remarks", "comment", "strategic fit", "synergy", "rationale", "maximum check", "ticket size"]):
        return "Investment Thesis"
    if "type" in normalized or "category" in normalized or "classification" in normalized or "sector" in normalized or "industry" in normalized or "vertical" in normalized:
        return "Type"
    if any(word in normalized for word in ["contact", "person", "pic", "representative", "partner", "name"]):
        return "2nd PiC" if any(word in normalized for word in ["2", "second", "secondary"]) else "1st PiC"
    return None


def score_header_row(values):
    """Score how likely a row is the real table header."""
    score = 0
    non_empty = 0
    mapped_targets = set()
    for value in values:
        if pd.isna(value) or str(value).strip() == "":
            continue
        non_empty += 1
        normalized = normalize_column_name(value)
        guessed = guess_standard_column(value)
        if normalized in HEADER_KEYWORDS:
            score += 4
        if guessed:
            mapped_targets.add(guessed)
            score += 8
        if normalized in ["email", "name", "organization", "organisation", "company", "type", "website", "notes", "sector"]:
            score += 4
    score += min(non_empty, 10)
    score += len(mapped_targets) * 6
    return score


def detect_header_row(raw_no_header_df, max_scan_rows=40):
    """Find the header row even when the Excel file has title/logo rows above the table."""
    best_idx = 0
    best_score = -1
    rows_to_scan = min(len(raw_no_header_df), max_scan_rows)
    for idx in range(rows_to_scan):
        row_values = raw_no_header_df.iloc[idx].tolist()
        score = score_header_row(row_values)
        if score > best_score:
            best_score = score
            best_idx = idx
    return best_idx, best_score


def make_unique_columns(columns):
    """Avoid duplicate column names after cleaning."""
    seen = {}
    result = []
    for col in columns:
        col = "" if pd.isna(col) else str(col).strip()
        if col == "":
            col = "Unnamed"
        if col in seen:
            seen[col] += 1
            result.append(f"{col}_{seen[col]}")
        else:
            seen[col] = 0
            result.append(col)
    return result



def get_uploaded_sheet_names(uploaded_file):
    """Return available sheet names for Excel files. CSV has one virtual sheet."""
    file_name = uploaded_file.name.lower()
    try:
        uploaded_file.seek(0)
    except Exception:
        pass

    if file_name.endswith(".csv"):
        return ["CSV"]

    try:
        xls = pd.ExcelFile(uploaded_file)
        return xls.sheet_names
    finally:
        try:
            uploaded_file.seek(0)
        except Exception:
            pass


def read_one_sheet_with_header_detection(uploaded_file, sheet_name=None):
    """Read one selected CSV/Excel sheet and detect the actual table header row."""
    file_name = uploaded_file.name.lower()
    try:
        uploaded_file.seek(0)
    except Exception:
        pass

    if file_name.endswith(".csv"):
        raw_no_header = pd.read_csv(uploaded_file, header=None, dtype=str, encoding_errors="ignore")
        header_idx, header_score = detect_header_row(raw_no_header)
        headers = make_unique_columns(raw_no_header.iloc[header_idx].tolist())
        df = raw_no_header.iloc[header_idx + 1:].copy()
        df.columns = headers
        return df.dropna(how="all"), "CSV", header_idx + 1, header_score

    try:
        uploaded_file.seek(0)
    except Exception:
        pass

    raw_no_header = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=None, dtype=str)
    if raw_no_header.empty:
        raise ValueError(f"Selected sheet '{sheet_name}' is empty.")

    header_idx, header_score = detect_header_row(raw_no_header)
    headers = make_unique_columns(raw_no_header.iloc[header_idx].tolist())
    df = raw_no_header.iloc[header_idx + 1:].copy()
    df.columns = headers
    return df.dropna(how="all"), sheet_name, header_idx + 1, header_score


def detect_best_sheet(uploaded_file):
    """Scan all sheets and return a summary table plus the best sheet name."""
    file_name = uploaded_file.name.lower()
    if file_name.endswith(".csv"):
        df, sheet_name, header_row, header_score = read_one_sheet_with_header_detection(uploaded_file, "CSV")
        return pd.DataFrame([{
            "Sheet": "CSV",
            "Detected Header Row": header_row,
            "Detection Score": header_score,
            "Rows After Header": len(df)
        }]), "CSV"

    try:
        uploaded_file.seek(0)
    except Exception:
        pass

    sheets = pd.read_excel(uploaded_file, sheet_name=None, header=None, dtype=str)
    summaries = []
    best_sheet = None
    best_score = -1

    for sheet_name, raw_no_header in sheets.items():
        if raw_no_header.empty:
            summaries.append({
                "Sheet": sheet_name,
                "Detected Header Row": "-",
                "Detection Score": 0,
                "Rows After Header": 0
            })
            continue

        header_idx, header_score = detect_header_row(raw_no_header)
        rows_after_header = max(len(raw_no_header) - header_idx - 1, 0)
        summaries.append({
            "Sheet": sheet_name,
            "Detected Header Row": header_idx + 1,
            "Detection Score": header_score,
            "Rows After Header": rows_after_header
        })

        if header_score > best_score:
            best_score = header_score
            best_sheet = sheet_name

    summary_df = pd.DataFrame(summaries)
    if best_sheet is None:
        raise ValueError("No readable sheet found in the uploaded file.")
    summary_df = summary_df[["Sheet", "Detected Header Row", "Detection Score", "Rows After Header"]]

    try:
        uploaded_file.seek(0)
    except Exception:
        pass

    return summary_df, best_sheet


def read_uploaded_file_smart(uploaded_file, selected_sheet=None):
    """Read CSV/XLS/XLSX and return the selected or best detected table as a dataframe."""
    file_name = uploaded_file.name.lower()

    if file_name.endswith(".csv"):
        return read_one_sheet_with_header_detection(uploaded_file, "CSV")

    if selected_sheet:
        return read_one_sheet_with_header_detection(uploaded_file, selected_sheet)

    sheet_summary, best_sheet = detect_best_sheet(uploaded_file)
    return read_one_sheet_with_header_detection(uploaded_file, best_sheet)

def build_auto_mapping(df_raw):
    """Choose the best raw column for each app column using content-aware scoring."""
    candidate_scores = []
    for raw_col in df_raw.columns:
        for target in STANDARD_COLUMNS:
            score = score_column_for_target(raw_col, df_raw[raw_col], target)
            candidate_scores.append((score, raw_col, target))

    # Assign high-confidence fields first so No./Source won't steal important mappings.
    target_priority = ["Email 1", "Email 2", "Website", "Investor", "1st PiC", "2nd PiC", "Type", "Location", "Investment Thesis", "Status"]
    mapping = {col: "" for col in STANDARD_COLUMNS}
    confidence = {col: 0 for col in STANDARD_COLUMNS}
    used_cols = set()

    for target in target_priority:
        candidates = sorted(
            [(s, c) for s, c, t in candidate_scores if t == target and c not in used_cols],
            reverse=True
        )
        if not candidates:
            continue
        best_score, best_col = candidates[0]
        threshold = 35
        if target in ["Investor", "Email 1"]:
            threshold = 45
        if target in ["Email 2", "2nd PiC", "Status"]:
            threshold = 50
        if best_score >= threshold:
            mapping[target] = best_col
            confidence[target] = round(min(max(best_score, 0), 100), 1)
            used_cols.add(best_col)

    # If no investor yet, do a safer fallback: choose text column with company-like header/content, never No./ID/email/url.
    if not mapping["Investor"]:
        fallback_candidates = []
        for raw_col in df_raw.columns:
            if raw_col in used_cols:
                continue
            norm = normalize_column_name(raw_col)
            if norm in BAD_INVESTOR_HEADERS or "email" in norm or "mail" in norm:
                continue
            if email_ratio(df_raw[raw_col]) > 0.05 or url_ratio(df_raw[raw_col]) > 0.15 or numeric_ratio(df_raw[raw_col]) > 0.35:
                continue
            score = 10
            if any(x in norm for x in ["org", "company", "firm", "fund", "investor", "manager", "target", "name"]):
                score += 50
            score += business_name_ratio(df_raw[raw_col]) * 40
            score -= person_name_ratio(df_raw[raw_col]) * 30
            score += min(len(column_sample(df_raw[raw_col])), 30) / 3
            fallback_candidates.append((score, raw_col))
        if fallback_candidates:
            fallback_candidates.sort(reverse=True)
            mapping["Investor"] = fallback_candidates[0][1]
            confidence["Investor"] = round(min(fallback_candidates[0][0], 75), 1)

    return mapping, confidence


def standardize_uploaded_dataframe(raw_df, manual_mapping=None):
    """Convert any uploaded tracker into the app's standard columns."""
    df_raw = raw_df.copy().dropna(how="all")
    df_raw.columns = make_unique_columns([str(c).strip() for c in df_raw.columns])

    if manual_mapping:
        mapping_used = {col: manual_mapping.get(col, "") for col in STANDARD_COLUMNS}
        confidence = {col: 100 if mapping_used.get(col) else 0 for col in STANDARD_COLUMNS}
    else:
        mapping_used, confidence = build_auto_mapping(df_raw)

    standardized = pd.DataFrame(index=df_raw.index)
    used_raw_cols = set()
    for standard_col in STANDARD_COLUMNS:
        raw_col = mapping_used.get(standard_col, "")
        if raw_col and raw_col in df_raw.columns:
            standardized[standard_col] = df_raw[raw_col]
            used_raw_cols.add(raw_col)
        else:
            standardized[standard_col] = ""
            mapping_used[standard_col] = ""

    # Combine obvious notes/title/source text into thesis only if thesis is blank.
    extra_note_cols = []
    for raw_col in df_raw.columns:
        norm = normalize_column_name(raw_col)
        if raw_col in used_raw_cols:
            continue
        if any(x in norm for x in ["note", "description", "focus", "strategy", "remark", "comment", "criteria", "memo", "title", "strategic fit", "synergy", "rationale", "maximum check", "max check", "ticket", "revenue", "employees"]):
            if normalize_column_name(raw_col) not in IGNORE_AS_THESIS_HEADERS and email_ratio(df_raw[raw_col]) < 0.05 and url_ratio(df_raw[raw_col]) < 0.3:
                extra_note_cols.append(raw_col)

    if extra_note_cols:
        extra_notes = df_raw[extra_note_cols].fillna("").astype(str).agg(" | ".join, axis=1).str.strip(" |")
        empty_thesis = standardized["Investment Thesis"].fillna("").astype(str).str.strip() == ""
        standardized.loc[empty_thesis, "Investment Thesis"] = extra_notes[empty_thesis]
        if not mapping_used.get("Investment Thesis"):
            mapping_used["Investment Thesis"] = " + ".join(extra_note_cols)
            confidence["Investment Thesis"] = 60

    standardized = standardized[STANDARD_COLUMNS]

    # NEW: extract key fields row-by-row from the full uploaded sheet.
    # This is more accurate than relying only on column names because messy Excel files
    # often hide emails, URLs, notes, or source links in unexpected columns.
    standardized = extract_fields_rowwise(df_raw, standardized, mapping_used)

    for col in STANDARD_COLUMNS:
        standardized[col] = standardized[col].fillna("").astype(str).str.strip()
        standardized[col] = standardized[col].replace({"nan": "", "None": "", "NaN": ""})

    # Remove rows that are clearly not real leads.
    standardized = standardized.dropna(how="all")
    standardized = standardized[standardized.apply(lambda row: any(str(x).strip() for x in row), axis=1)]
    standardized = standardized[~standardized["Investor"].apply(is_bad_investor_value)]
    standardized = standardized.reset_index(drop=True)
    standardized.index = standardized.index + 1

    warnings = []
    if standardized["Investor"].astype(str).str.strip().eq("").all():
        warnings.append("Investor / company name was not detected. Please choose the correct column below.")
    if standardized["Email 1"].astype(str).str.strip().eq("").all():
        warnings.append("No primary email detected. You can still use the dashboard, but email sending needs an email column.")
    if standardized["Website"].astype(str).str.strip().eq("").all():
        warnings.append("No website detected. Hunter/company email lookup may have fewer results.")

    return standardized, mapping_used, warnings, confidence


def prepare_dataframe_from_df(df_original):
    """Prepare an already-standardized dataframe for dashboard/scoring/outreach."""
    original_count = len(df_original)
    df = df_original.copy().dropna(how="all")

    for col in STANDARD_COLUMNS:
        if col not in df.columns:
            df[col] = ""

    text_columns = [
        "Investor", "Type", "Location", "Website",
        "1st PiC", "Email 1", "2nd PiC", "Email 2",
        "Investment Thesis", "Status"
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()
            df[col] = df[col].replace({"nan": "", "None": "", "NaN": ""})

    useful_cols = [col for col in ["Investor", "Website", "Email 1", "1st PiC"] if col in df.columns]
    if useful_cols:
        df = df[df[useful_cols].apply(lambda row: any(str(x).strip() for x in row), axis=1)]

    required_subset = [col for col in ["Investor", "Website", "Email 1"] if col in df.columns]
    df = df.drop_duplicates(subset=required_subset) if required_subset else df.drop_duplicates()
    df = df.reset_index(drop=True)
    df.index = df.index + 1

    for col in ["Website", "Investor", "Type", "Location", "Investment Thesis", "Email 1", "Email 2", "1st PiC", "2nd PiC"]:
        if col not in df.columns:
            df[col] = ""

    cleaned_count = len(df)
    duplicates_removed = original_count - cleaned_count

    df["Domain"] = df["Website"].apply(clean_domain)

    if "Company Email" not in df.columns:
        df["Company Email"] = ""
    df["LinkedIn Search"] = df["Investor"].apply(generate_linkedin_search)
    df["Possible Contact Page"] = df["Domain"].apply(generate_contact_page)

    hunter_columns = [
        "Hunter Email", "Hunter Name", "Hunter Position", "Hunter LinkedIn", "Hunter Confidence", "Hunter Source",
        "Hunter Company Website", "Hunter Company Name", "Hunter Company LinkedIn", "Hunter Company Source", "Company Email"
    ]

    for col in hunter_columns:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].astype("string")

    df["Score"] = df.apply(calculate_score, axis=1)
    df["Priority"] = df["Score"].apply(assign_priority)

    if "Status" not in df.columns:
        df["Status"] = "Not Contacted"
    df["Status"] = df["Status"].fillna("Not Contacted").replace("", "Not Contacted")

    return df, original_count, duplicates_removed


def prepare_dataframe(uploaded_file):
    """Backward-compatible wrapper for direct file processing."""
    raw_df, _, _, _ = read_uploaded_file_smart(uploaded_file)
    standardized_df, _, _, _ = standardize_uploaded_dataframe(raw_df)
    return prepare_dataframe_from_df(standardized_df)


def confidence_badge(score):
    if score >= 70:
        return "✅ High"
    if score >= 45:
        return "🟡 Medium"
    return "⚪ Blank / Low"


def render_mapping_table(mapping, confidence):
    rows = []
    for standard_col in STANDARD_COLUMNS:
        mapped_from = mapping.get(standard_col, "")
        rows.append({
            "App Column": standard_col,
            "Auto detected from": mapped_from if mapped_from else "Not detected / blank",
            "Confidence": confidence_badge(confidence.get(standard_col, 0))
        })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)



def clean_single_sheet_for_import(uploaded_file, selected_sheet):
    """Read and clean one sheet into the standard app dataframe."""
    raw_df, sheet_name, header_row, header_score = read_uploaded_file_smart(uploaded_file, selected_sheet=selected_sheet)
    cleaned_df, mapping, warnings, confidence = standardize_uploaded_dataframe(raw_df)
    cleaned_df = cleaned_df.copy()
    cleaned_df["Source Sheet"] = str(sheet_name)
    return {
        "cleaned_df": cleaned_df,
        "raw_df": raw_df,
        "sheet_name": sheet_name,
        "header_row": header_row,
        "header_score": header_score,
        "mapping": mapping,
        "warnings": warnings,
        "confidence": confidence,
    }


def get_auto_sheet_detection_threshold(sheet_summary):
    """Return a fixed sheet score cutoff for deciding usable workbook sheets.
    50 is practical for DealFlow sourcing files: flexible enough for smaller
    shortlists, while still filtering obvious notes/summary tabs.
    """
    return 50


def clean_all_usable_sheets_for_import(uploaded_file, min_score=None, min_rows=1):
    """Clean every detected usable sheet separately. No merging is done here."""
    sheet_summary, recommended_sheet = detect_best_sheet(uploaded_file)
    if min_score is None:
        min_score = get_auto_sheet_detection_threshold(sheet_summary)
    cleaned_sheets = {}
    import_results = []

    for _, item in sheet_summary.iterrows():
        sheet_name = str(item["Sheet"])
        score_value = item.get("Detection Score", 0)
        rows_value = item.get("Rows After Header", 0)

        try:
            score_value = float(score_value)
        except Exception:
            score_value = 0
        try:
            rows_value = int(rows_value)
        except Exception:
            rows_value = 0

        if score_value < min_score or rows_value < min_rows:
            import_results.append({
                "Sheet": sheet_name,
                "Status": "Skipped",
                "Reason": f"Low detection score ({score_value}) or no usable rows",
                "Rows Cleaned": 0,
            })
            continue

        try:
            result = clean_single_sheet_for_import(uploaded_file, sheet_name)
            cleaned_df = result["cleaned_df"]
            if len(cleaned_df) == 0:
                import_results.append({
                    "Sheet": sheet_name,
                    "Status": "Skipped",
                    "Reason": "No valid investor/company rows after cleaning",
                    "Rows Cleaned": 0,
                })
                continue

            cleaned_name = f"{sheet_name}_CLEANED"
            cleaned_sheets[cleaned_name] = cleaned_df
            import_results.append({
                "Sheet": sheet_name,
                "Status": "Cleaned",
                "Reason": "Usable sheet detected",
                "Rows Cleaned": len(cleaned_df),
            })
        except Exception as e:
            import_results.append({
                "Sheet": sheet_name,
                "Status": "Error",
                "Reason": str(e),
                "Rows Cleaned": 0,
            })

    return cleaned_sheets, pd.DataFrame(import_results), recommended_sheet, sheet_summary


def set_active_cleaned_sheet(sheet_name):
    """Set one stored cleaned sheet as the dataframe powering the dashboard."""
    cleaned_sheets = st.session_state.get("cleaned_sheets", {})
    if sheet_name not in cleaned_sheets:
        st.error("Selected cleaned sheet was not found.")
        return
    st.session_state.active_cleaned_sheet = sheet_name
    st.session_state.cleaned_import_df = cleaned_sheets[sheet_name]
    st.session_state.import_stage = "ready"


def render_cleaned_sheets_manager(uploaded_file=None):
    """Let user choose a cleaned sheet or manually merge cleaned sheets."""
    cleaned_sheets = st.session_state.get("cleaned_sheets", {})
    if not cleaned_sheets:
        return

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### Available Cleaned Sheets")
    st.caption("These sheets are already cleaned separately. Nothing is merged unless you manually choose sheets and click merge.")

    summary_rows = []
    for name, sheet_df in cleaned_sheets.items():
        source_sheet = sheet_df.get("Source Sheet", pd.Series([name])).iloc[0] if len(sheet_df) > 0 else name
        summary_rows.append({
            "Cleaned Sheet": name,
            "Source Sheet": source_sheet,
            "Rows": len(sheet_df),
        })
    summary_df = pd.DataFrame(summary_rows)
    last_merged_sheet = st.session_state.get("last_merged_sheet", "")
    table_html = "<table class='cleaned-sheet-table'><thead><tr><th>Cleaned Sheet</th><th>Source Sheet</th><th>Rows</th></tr></thead><tbody>"
    for _, row in summary_df.iterrows():
        sheet_name = str(row.get("Cleaned Sheet", ""))
        row_class = " class='merged-sheet-row'" if sheet_name == last_merged_sheet else ""
        table_html += (
            f"<tr{row_class}>"
            f"<td>{html.escape(sheet_name)}</td>"
            f"<td>{html.escape(str(row.get('Source Sheet', '')))}</td>"
            f"<td>{html.escape(str(row.get('Rows', '')))}</td>"
            f"</tr>"
        )
    table_html += "</tbody></table>"
    st.markdown(table_html, unsafe_allow_html=True)

    sheet_names = list(cleaned_sheets.keys())
    default_active = st.session_state.get("active_cleaned_sheet", sheet_names[0])
    default_index = sheet_names.index(default_active) if default_active in sheet_names else 0
    chosen_sheet = st.selectbox("Choose cleaned sheet to use in dashboard", sheet_names, index=default_index, key="choose_active_cleaned_sheet")

    c1, c2 = st.columns([1.2, 4])
    with c1:
        if st.button("Use This Sheet", type="primary"):
            set_active_cleaned_sheet(chosen_sheet)
            if uploaded_file is not None:
                st.session_state.uploaded_file_object = uploaded_file
                st.session_state.uploaded_file_name = uploaded_file.name
                st.session_state.uploaded_time = datetime.now().strftime("%b %d, %Y %I:%M %p")
            st.rerun()

    last_merge_ack = st.session_state.get("last_merge_ack", "")
    if last_merge_ack:
        st.markdown(f"<div class='neon-ack'>{html.escape(last_merge_ack)}</div>", unsafe_allow_html=True)
    else:
        st.markdown("#### Manual Merge")
        st.caption("Select only the cleaned sheets you want to combine. The merge keeps a Source Sheet column so the origin is clear.")
        merge_selection = st.multiselect("Cleaned sheets to merge", sheet_names, key="manual_merge_sheet_selection")
        merge_name = st.text_input("Merged sheet name", value="Merged_CLEANED", key="manual_merge_name")

        if st.button("Merge Selected Cleaned Sheets"):
            if len(merge_selection) < 2:
                st.warning("Select at least 2 cleaned sheets to merge.")
            else:
                merged_parts = []
                for selected in merge_selection:
                    part = cleaned_sheets[selected].copy()
                    if "Source Sheet" not in part.columns:
                        part["Source Sheet"] = selected
                    merged_parts.append(part)

                merged_df = pd.concat(merged_parts, ignore_index=True)
                dedupe_cols = [col for col in ["Investor", "Website", "Email 1"] if col in merged_df.columns]
                if dedupe_cols:
                    merged_df = merged_df.sort_values(
                        by=["Investor"],
                        key=lambda s: s.astype(str).str.len(),
                        ascending=False,
                    ).drop_duplicates(subset=dedupe_cols, keep="first")

                safe_merge_name = clean_cell_value(merge_name) or "Merged_CLEANED"
                st.session_state.cleaned_sheets[safe_merge_name] = merged_df
                st.session_state.last_merged_sheet = safe_merge_name
                st.session_state.last_merge_ack = f"✦ Merge complete: {safe_merge_name} is ready with {len(merged_df)} cleaned rows. The merged file is highlighted above. ✦"
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)


def render_import_cleaner(uploaded_file):
    """Show import options: clean selected sheet, clean all usable sheets separately, and manual merge."""
    st.markdown('<div class="main-title">Review & Auto-Clean Uploaded File</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Choose one sheet to clean, or clean all usable sheets separately. Manual merge is available after cleaning.</div>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    # If the user has already cleaned sheets, keep the screen simple.
    # Do not keep showing the workbook detection table because it confuses coworkers after cleaning is done.
    has_cleaned_sheets = bool(st.session_state.get("cleaned_sheets", {}))
    show_import_options = st.session_state.get("show_import_options", False)

    if has_cleaned_sheets and not show_import_options:
        render_cleaned_sheets_manager(uploaded_file)
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.info("Cleaned sheets are ready above. Workbook detection is hidden to keep this page simple.")
        cleaned_all_done = st.session_state.get("cleaned_all_sheets_done", False)
        if cleaned_all_done:
            c1, c2 = st.columns([1.3, 4])
            with c1:
                if st.button("Upload Different File"):
                    for key in ["raw_uploaded_file", "uploaded_file_object", "cleaned_import_df", "cleaned_sheets", "active_cleaned_sheet", "import_stage", "selected_import_sheet", "show_import_options", "cleaned_all_sheets_done", "last_merge_ack", "last_merged_sheet"]:
                        st.session_state.pop(key, None)
                    st.rerun()
        else:
            c1, c2 = st.columns([1.3, 1.3])
            with c1:
                if st.button("Clean More From This Workbook"):
                    st.session_state.show_import_options = True
                    st.rerun()
            with c2:
                if st.button("Upload Different File"):
                    for key in ["raw_uploaded_file", "uploaded_file_object", "cleaned_import_df", "cleaned_sheets", "active_cleaned_sheet", "import_stage", "selected_import_sheet", "show_import_options", "cleaned_all_sheets_done", "last_merge_ack", "last_merged_sheet"]:
                        st.session_state.pop(key, None)
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()

    render_cleaned_sheets_manager(uploaded_file)

    try:
        sheet_summary, recommended_sheet = detect_best_sheet(uploaded_file)
        # Keep the detection table simple. No Recommended column.
        sheet_summary = sheet_summary[["Sheet", "Detected Header Row", "Detection Score", "Rows After Header"]]
        sheet_names = sheet_summary["Sheet"].tolist()
        auto_sheet_threshold = get_auto_sheet_detection_threshold(sheet_summary)
    except Exception as e:
        st.error(f"Could not read this file: {e}")
        if st.button("Upload another file"):
            for key in ["raw_uploaded_file", "uploaded_file_object", "cleaned_import_df", "cleaned_sheets", "active_cleaned_sheet", "import_stage", "selected_import_sheet", "show_import_options", "cleaned_all_sheets_done", "last_merge_ack", "last_merged_sheet"]:
                st.session_state.pop(key, None)
            st.rerun()
        st.stop()

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### Workbook Sheet Detection")
    st.caption("The app scores each sheet based on whether it looks like a usable sourcing/investor table.")
    st.dataframe(sheet_summary, use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    tab_selected, tab_all = st.tabs(["Clean Selected Sheet", "Clean All Usable Sheets Separately"])

    with tab_selected:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 1) Choose Sheet to Clean")
        st.caption("Use this when you only want one tab from the workbook.")

        if len(sheet_names) > 1:
            default_index = sheet_names.index(recommended_sheet) if recommended_sheet in sheet_names else 0
            selected_sheet = st.selectbox(
                "Sheet to clean",
                sheet_names,
                index=default_index,
                key="selected_import_sheet"
            )
        else:
            selected_sheet = sheet_names[0]
            st.info(f"Only one sheet detected: {selected_sheet}")
        st.markdown('</div>', unsafe_allow_html=True)

        try:
            result = clean_single_sheet_for_import(uploaded_file, selected_sheet)
            raw_df = result["raw_df"]
            auto_df = result["cleaned_df"]
            auto_mapping = result["mapping"]
            warnings = result["warnings"]
            auto_confidence = result["confidence"]
            sheet_name = result["sheet_name"]
            header_row = result["header_row"]
        except Exception as e:
            st.error(f"Could not clean selected sheet: {e}")
            st.stop()

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 2) Selected Sheet Detection")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Detected sheet", str(sheet_name))
        c2.metric("Header row", header_row)
        c3.metric("Raw rows", len(raw_df))
        c4.metric("Cleaned rows", len(auto_df))
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 3) Extracted Key Fields")
        render_mapping_table(auto_mapping, auto_confidence)
        if warnings:
            for warning in warnings:
                st.warning(warning)
        else:
            st.success("Auto-clean looks good. Check the preview, then continue.")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 4) Auto-Cleaned Preview")
        st.dataframe(auto_df.head(30), use_container_width=True)
        # Keep the action buttons close together under the preview table.
        # The last spacer column takes the remaining width so the two buttons do not sit far apart.
        b1, b2, b3 = st.columns([1.35, 1.1, 10], gap="small")
        with b1:
            if st.button("Use Selected Sheet", type="primary"):
                cleaned_name = f"{sheet_name}_CLEANED"
                if "cleaned_sheets" not in st.session_state:
                    st.session_state.cleaned_sheets = {}
                st.session_state.cleaned_sheets[cleaned_name] = auto_df
                st.session_state.active_cleaned_sheet = cleaned_name
                st.session_state.cleaned_import_df = auto_df
                st.session_state.uploaded_file_object = uploaded_file
                st.session_state.uploaded_file_name = uploaded_file.name
                st.session_state.uploaded_time = datetime.now().strftime("%b %d, %Y %I:%M %p")
                st.session_state.import_stage = "ready"
                st.session_state.show_import_options = False
                st.session_state.cleaned_all_sheets_done = False
                st.session_state.pop("last_merge_ack", None)
                st.session_state.pop("last_merged_sheet", None)
                st.rerun()
        with b2:
            if st.button("Cancel Upload"):
                for key in ["raw_uploaded_file", "uploaded_file_object", "cleaned_import_df", "cleaned_sheets", "active_cleaned_sheet", "import_stage", "selected_import_sheet", "show_import_options", "cleaned_all_sheets_done", "last_merge_ack", "last_merged_sheet"]:
                    st.session_state.pop(key, None)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        with st.expander("Fix selected sheet mapping manually only if preview looks wrong", expanded=bool(warnings)):
            st.info("Only change fields that look wrong in the preview. Most files should work automatically after extraction.")

            raw_options = [""] + list(raw_df.columns)
            manual_mapping = dict(auto_mapping)

            st.markdown("#### Important fields")
            simple_cols = st.columns(2)
            helper = {
                "Investor": "Company / fund / organisation name",
                "Email 1": "Main recipient email",
                "Website": "Website, URL, LinkedIn, or source link",
                "1st PiC": "Main contact person name",
                "Type": "Investor type, sector, category, industry",
                "Location": "Country, city, HQ, region",
                "Investment Thesis": "Notes, focus, thesis, strategy, remarks",
            }
            for idx, standard_col in enumerate(IMPORTANT_IMPORT_COLUMNS):
                default_raw = manual_mapping.get(standard_col, "")
                default_index = raw_options.index(default_raw) if default_raw in raw_options else 0
                with simple_cols[idx % 2]:
                    manual_mapping[standard_col] = st.selectbox(
                        f"{standard_col} — {helper.get(standard_col, '')}",
                        raw_options,
                        index=default_index,
                        key=f"simple_manual_map_{standard_col}"
                    )

            with st.expander("Optional fields"):
                opt_cols = st.columns(2)
                for idx, standard_col in enumerate(OPTIONAL_IMPORT_COLUMNS):
                    default_raw = manual_mapping.get(standard_col, "")
                    default_index = raw_options.index(default_raw) if default_raw in raw_options else 0
                    with opt_cols[idx % 2]:
                        manual_mapping[standard_col] = st.selectbox(
                            f"{standard_col}",
                            raw_options,
                            index=default_index,
                            key=f"optional_manual_map_{standard_col}"
                        )

            preview_df, _, manual_warnings, _ = standardize_uploaded_dataframe(raw_df, manual_mapping=manual_mapping)
            preview_df["Source Sheet"] = str(sheet_name)
            st.markdown("#### Preview after your fixes")
            st.dataframe(preview_df.head(30), use_container_width=True)
            if manual_warnings:
                for warning in manual_warnings:
                    st.warning(warning)

            if st.button("Use This Fixed Mapping", type="primary"):
                cleaned_name = f"{sheet_name}_CLEANED"
                if "cleaned_sheets" not in st.session_state:
                    st.session_state.cleaned_sheets = {}
                st.session_state.cleaned_sheets[cleaned_name] = preview_df
                st.session_state.active_cleaned_sheet = cleaned_name
                st.session_state.cleaned_import_df = preview_df
                st.session_state.uploaded_file_object = uploaded_file
                st.session_state.uploaded_file_name = uploaded_file.name
                st.session_state.uploaded_time = datetime.now().strftime("%b %d, %Y %I:%M %p")
                st.session_state.import_stage = "ready"
                st.session_state.show_import_options = False
                st.session_state.cleaned_all_sheets_done = False
                st.session_state.pop("last_merge_ack", None)
                st.session_state.pop("last_merged_sheet", None)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_all:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### Clean All Usable Sheets Separately")
        st.caption("This does not merge anything. Each usable tab becomes its own cleaned sheet.")
        st.markdown(
            f"""
            <div class="glass-card" style="margin-top:12px;">
                <b>Auto Sheet Detection Threshold: {auto_sheet_threshold}</b><br>
                <span style="color:#94a3b8;font-size:13px;">Fixed at 50 for practical sourcing-sheet detection. Users do not need to adjust this.</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Clean All Usable Sheets", type="primary"):
            with st.spinner("Cleaning all usable sheets separately..."):
                cleaned_sheets, import_results, recommended, _ = clean_all_usable_sheets_for_import(uploaded_file, min_score=auto_sheet_threshold)

            if cleaned_sheets:
                existing = st.session_state.get("cleaned_sheets", {})
                existing.update(cleaned_sheets)
                st.session_state.cleaned_sheets = existing
                first_cleaned_name = list(cleaned_sheets.keys())[0]
                st.session_state.active_cleaned_sheet = first_cleaned_name
                st.session_state.cleaned_import_df = cleaned_sheets[first_cleaned_name]
                st.session_state.uploaded_file_object = uploaded_file
                st.session_state.uploaded_file_name = uploaded_file.name
                st.session_state.uploaded_time = datetime.now().strftime("%b %d, %Y %I:%M %p")
                st.session_state.show_import_options = False
                st.session_state.cleaned_all_sheets_done = True
                st.session_state.pop("last_merge_ack", None)
                st.session_state.pop("last_merged_sheet", None)
                st.success(f"Cleaned {len(cleaned_sheets)} usable sheet(s). They are saved separately below.")
                st.dataframe(import_results, use_container_width=True, hide_index=True)
                st.rerun()
            else:
                st.warning("No usable sheets were cleaned. This workbook may not contain sourcing sheets above the automatic threshold.")
                st.dataframe(import_results, use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.stop()

# =========================
# FILE UPLOAD FIRST + SMART IMPORT CLEANER
# =========================
existing_file = st.session_state.get("uploaded_file_object", None)
existing_cleaned_df = st.session_state.get("cleaned_import_df", None)
existing_cleaned_sheets = st.session_state.get("cleaned_sheets", {})
raw_import_file = st.session_state.get("raw_uploaded_file", None)

load_css(has_file=(existing_file is not None or existing_cleaned_df is not None or bool(existing_cleaned_sheets) or raw_import_file is not None))
render_neon_mouse_effects()

# If a new raw file was uploaded, clean/map it before allowing the dashboard to load.
if st.session_state.get("import_stage") == "mapping" and raw_import_file is not None:
    render_import_cleaner(raw_import_file)

if existing_cleaned_df is None and not existing_cleaned_sheets and existing_file is None:
    st.markdown("""
    <div class="landing-wrap">
        <div class="landing-card">
            <div class="landing-title">Investor Outreach Automation Dashboard</div>
            <div class="landing-subtitle">
                Upload any investor tracker. The app will auto-detect messy headers, standardize the columns, and show a preview before loading the dashboard.
            </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="landing-upload">', unsafe_allow_html=True)
    first_upload = st.file_uploader("Upload Investor File", type=["xlsx", "xls", "csv"])
    st.markdown('</div></div></div>', unsafe_allow_html=True)

    if first_upload is not None:
        st.session_state.raw_uploaded_file = first_upload
        st.session_state.uploaded_file_name = first_upload.name
        st.session_state.uploaded_time = datetime.now().strftime("%b %d, %Y %I:%M %p")
        st.session_state.import_stage = "mapping"
        st.rerun()

    st.stop()


# =========================
# SIDEBAR AFTER FILE UPLOAD
# =========================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <h2>Investor Outreach</h2>
        <p>Automation Dashboard</p>
    </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        ["Dashboard", "Cleaned Tracker", "Lead Scoring", "Outreach Prep", "Email Outreach"],
        label_visibility="visible",
        key="page_nav"
    )

    st.markdown("---")
    st.markdown('<div class="sidebar-summary-title">Data Summary</div>', unsafe_allow_html=True)

    uploaded_name = st.session_state.get("uploaded_file_name", "No file uploaded")
    uploaded_time = st.session_state.get("uploaded_time", "-")
    total_count = st.session_state.get("total_investors", "-")

    if st.session_state.get("cleaned_sheets"):
        cleaned_sheet_names = list(st.session_state.cleaned_sheets.keys())
        active_sheet = st.session_state.get("active_cleaned_sheet", cleaned_sheet_names[0])
        active_index = cleaned_sheet_names.index(active_sheet) if active_sheet in cleaned_sheet_names else 0
        selected_active_sheet = st.selectbox(
            "Active cleaned sheet",
            cleaned_sheet_names,
            index=active_index,
            key="sidebar_active_cleaned_sheet"
        )
        if selected_active_sheet != active_sheet:
            st.session_state.active_cleaned_sheet = selected_active_sheet
            st.session_state.cleaned_import_df = st.session_state.cleaned_sheets[selected_active_sheet]
            st.rerun()

    st.markdown(f"""
    <div class="sidebar-summary-item">Last Uploaded<div class="sidebar-summary-value">{uploaded_time}</div></div>
    <div class="sidebar-summary-item">Total Investors<div class="sidebar-summary-value">{total_count}</div></div>
    <div class="sidebar-summary-item">File<div class="sidebar-summary-value">{uploaded_name}</div></div>
    """, unsafe_allow_html=True)




# =========================
# HEADER + ADD NEW FILE
# =========================
page_headers = {
    "Dashboard": ("Dashboard Overview", "Key metrics and insights from your investor database"),
    "Cleaned Tracker": ("Cleaned Investor Outreach Tracker", "Full cleaned investor list with generated domains, emails, scores, and priority ratings"),
    "Lead Scoring": ("Data Readiness", "Completeness scoring for outreach-ready investor records"),
    "Outreach Prep": ("Outreach Prep", "Investor research links and draft preparation workspace"),
    "Email Outreach": ("Email Outreach", "Send emails using Email 1, Email 2, Hunter Email, or Company Email saved from Outreach Prep"),
}
page_title, page_subtitle = page_headers.get(page, ("Investor Outreach", "Automation Dashboard"))

st.markdown('<div class="app-header">', unsafe_allow_html=True)
left_head, right_head = st.columns([5, 1])

with left_head:
    st.markdown(f"""
    <div class="main-title">{page_title}</div>
    <div class="sub-title">{page_subtitle}</div>
    """, unsafe_allow_html=True)

with right_head:
    st.markdown('<div class="upload-button-wrap">', unsafe_allow_html=True)
    new_upload = st.file_uploader("Add New File", type=["xlsx", "xls", "csv"], label_visibility="collapsed", key="add_new_file")
    st.markdown('</div>', unsafe_allow_html=True)

if new_upload is not None:
    # Send every new upload through the same smart importer before loading dashboard.
    st.session_state.raw_uploaded_file = new_upload
    st.session_state.uploaded_file_name = new_upload.name
    st.session_state.uploaded_time = datetime.now().strftime("%b %d, %Y %I:%M %p")
    st.session_state.import_stage = "mapping"
    st.session_state.pop("cleaned_import_df", None)
    st.session_state.pop("cleaned_sheets", None)
    st.session_state.pop("active_cleaned_sheet", None)
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)


# =========================
# DATA PROCESSING
# =========================
if "cleaned_import_df" in st.session_state:
    df, original_count, duplicates_removed = prepare_dataframe_from_df(st.session_state.cleaned_import_df)
elif "cleaned_sheets" in st.session_state and st.session_state.cleaned_sheets:
    first_cleaned_name = list(st.session_state.cleaned_sheets.keys())[0]
    st.session_state.active_cleaned_sheet = first_cleaned_name
    st.session_state.cleaned_import_df = st.session_state.cleaned_sheets[first_cleaned_name]
    df, original_count, duplicates_removed = prepare_dataframe_from_df(st.session_state.cleaned_import_df)
else:
    df, original_count, duplicates_removed = prepare_dataframe(st.session_state.uploaded_file_object)

total_investors = len(df)
ready_count = (df["Priority"] == "Ready").sum()
partial_count = (df["Priority"] == "Partial").sum()
needs_research_count = (df["Priority"] == "Needs Research").sum()
locations_count = df["Location"].replace("", pd.NA).dropna().nunique()
emails_available = (df["Email 1"].astype(str).str.strip() != "").sum()
missing_emails = total_investors - emails_available
contacts_available = (df["1st PiC"].astype(str).str.strip() != "").sum()
st.session_state.total_investors = total_investors

if "hunter_enrichment_results" in st.session_state:
    hunter_results = st.session_state.hunter_enrichment_results

    hunter_columns = [
        "Hunter Email",
        "Hunter Name",
        "Hunter Position",
        "Hunter LinkedIn",
        "Hunter Confidence",
        "Hunter Source",
        "Hunter Company Website",
        "Hunter Company Name",
        "Hunter Company LinkedIn",
        "Hunter Company Source",
        "Company Email"
    ]

    for col in hunter_columns:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].astype("string")

    for investor_name, result in hunter_results.items():
        investor_mask = df["Investor"].astype(str) == str(investor_name)

        for col_name, col_value in result.items():
            if col_name in df.columns:
                safe_value = "" if pd.isna(col_value) else str(col_value)
                df.loc[investor_mask, col_name] = safe_value

if "website_email_results" in st.session_state:
    website_results = st.session_state.website_email_results

    for col in ["Company Email"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].astype("string")

    for investor_name, result in website_results.items():
        investor_mask = df["Investor"].astype(str) == str(investor_name)

        for col_name, col_value in result.items():
            if col_name in df.columns:
                safe_value = "" if pd.isna(col_value) else str(col_value)
                df.loc[investor_mask, col_name] = safe_value

    # Company Email is kept as the actual email found from Outreach Prep.

if "company_email_results" in st.session_state:
    company_results = st.session_state.company_email_results

    for col in ["Company Email", "Company Email Source"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].astype("string")

    for investor_name, result in company_results.items():
        investor_mask = df["Investor"].astype(str) == str(investor_name)

        # New format: result is a dict with Company Email and source.
        if isinstance(result, dict):
            for col_name, col_value in result.items():
                if col_name in df.columns:
                    safe_value = "" if pd.isna(col_value) else str(col_value)
                    df.loc[investor_mask, col_name] = safe_value
        else:
            # Backward compatibility with older saved session results where value was just the email string.
            safe_value = "" if pd.isna(result) else str(result)
            df.loc[investor_mask, "Company Email"] = safe_value


# =========================
# PAGE NAVIGATION CALLBACKS
# =========================
def go_to_cleaned_tracker():
    st.session_state.page_nav = "Cleaned Tracker"


# =========================
# PAGES
# =========================
if page == "Dashboard":
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1:
        kpi_card("Total Investors", total_investors, "In database", "👥", "kpi-icon-blue")

    with c2:
        duplicate_pct = round((duplicates_removed / original_count) * 100, 1) if original_count else 0
        kpi_card("Duplicates Removed", duplicates_removed, f"{duplicate_pct}% of total", "🧹", "kpi-icon-green")

    with c3:
        ready_pct = round((ready_count / total_investors) * 100, 1) if total_investors else 0
        kpi_card("Outreach Ready", ready_count, f"{ready_pct}% complete records", "✅", "kpi-icon-purple")

    with c4:
        kpi_card("Missing Emails", missing_emails, "Need enrichment", "🔎", "kpi-icon-yellow")

    with c5:
        contact_pct = round((contacts_available / total_investors) * 100, 1) if total_investors else 0
        kpi_card("Contacts Found", contacts_available, f"{contact_pct}% with PiC", "🤝", "kpi-icon-teal")

    with c6:
        kpi_card("Locations", locations_count, "Countries / Regions", "🌍", "kpi-icon-cyan")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Filter Investors</div>', unsafe_allow_html=True)

    f1, f2, f3, f4, f5 = st.columns([1.2, 1.2, 1.1, 1.1, 1.8])

    selected_location = f1.selectbox("Location", ["All Locations"] + sorted([x for x in df["Location"].dropna().unique() if x != ""]))
    selected_type = f2.selectbox("Type", ["All Types"] + sorted([x for x in df["Type"].dropna().unique() if x != ""]))
    selected_priority = f3.selectbox("Readiness", ["All Readiness"] + sorted(df["Priority"].dropna().unique()))
    selected_status = f4.selectbox("Status", ["All Statuses"] + sorted(df["Status"].dropna().unique()))
    search_query = f5.text_input("Search Investor", placeholder="Search by investor name...")

    filtered_df = df.copy()

    if selected_location != "All Locations":
        filtered_df = filtered_df[filtered_df["Location"] == selected_location]
    if selected_type != "All Types":
        filtered_df = filtered_df[filtered_df["Type"] == selected_type]
    if selected_priority != "All Readiness":
        filtered_df = filtered_df[filtered_df["Priority"] == selected_priority]
    if selected_status != "All Statuses":
        filtered_df = filtered_df[filtered_df["Status"] == selected_status]
    if search_query:
        filtered_df = filtered_df[filtered_df["Investor"].str.contains(search_query, case=False, na=False)]

    clear_col, status_col = st.columns([5, 1])
    with clear_col:
        st.markdown(f'<div class="status-ok">✓ Showing {len(filtered_df)} out of {len(df)} investors</div>', unsafe_allow_html=True)
    with status_col:
        st.button("Clear Filters")

    st.markdown('</div>', unsafe_allow_html=True)

    chart_col1, chart_col2, chart_col3, chart_col4 = st.columns(4)

    with chart_col1:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Data Completeness</div>', unsafe_allow_html=True)
            completeness_counts = pd.DataFrame({
                "Field": ["Email", "Contact", "Website", "Thesis", "Type", "Location"],
                "Complete Records": [
                    (filtered_df["Email 1"].astype(str).str.strip() != "").sum(),
                    (filtered_df["1st PiC"].astype(str).str.strip() != "").sum(),
                    (filtered_df["Website"].astype(str).str.strip() != "").sum(),
                    (filtered_df["Investment Thesis"].astype(str).str.strip() != "").sum(),
                    (filtered_df["Type"].astype(str).str.strip() != "").sum(),
                    (filtered_df["Location"].astype(str).str.strip() != "").sum(),
                ]
            })
            fig_completeness = px.bar(completeness_counts, x="Field", y="Complete Records", text="Complete Records")
            fig_completeness.update_traces(textposition="outside", marker_color="#60a5fa")
            fig_completeness = style_plotly_chart(fig_completeness, height=270)
            st.plotly_chart(fig_completeness, use_container_width=True)

    with chart_col2:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Investor Type Distribution</div>', unsafe_allow_html=True)
            type_counts = filtered_df["Type"].value_counts().head(6).reset_index()
            type_counts.columns = ["Type", "Count"]
            fig_type = px.bar(type_counts, x="Type", y="Count", text="Count")
            fig_type.update_traces(textposition="outside", marker_color="#60a5fa")
            fig_type = style_plotly_chart(fig_type, height=270)
            st.plotly_chart(fig_type, use_container_width=True)

    with chart_col3:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Location Distribution</div>', unsafe_allow_html=True)
            location_counts = filtered_df["Location"].value_counts().head(6).reset_index()
            location_counts.columns = ["Location", "Count"]
            fig_location = px.bar(location_counts, x="Location", y="Count", text="Count")
            fig_location.update_traces(textposition="outside", marker_color="#60a5fa")
            fig_location = style_plotly_chart(fig_location, height=270)
            st.plotly_chart(fig_location, use_container_width=True)

    with chart_col4:
        with st.container(border=True):
            st.markdown('<div class="chart-title">Outreach Status</div>', unsafe_allow_html=True)
            status_counts = filtered_df["Status"].value_counts().reset_index()
            status_counts.columns = ["Status", "Count"]
            fig_status = px.pie(status_counts, names="Status", values="Count", hole=0.55)
            fig_status = style_plotly_chart(fig_status, height=270)
            st.plotly_chart(fig_status, use_container_width=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Ready for Outreach</div>', unsafe_allow_html=True)
    top_investors = filtered_df.sort_values(by="Score", ascending=False)[["Investor", "Type", "Location", "Score", "Priority", "Status"]].head(5)
    render_priority_table(top_investors)
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("View All Investors", on_click=go_to_cleaned_tracker)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Cleaned Tracker":
    cleaned_tracker_df = get_cleaned_tracker_export_df(df)

    st.dataframe(cleaned_tracker_df, use_container_width=True)

    st.download_button(
        label="Download Cleaned Investor Tracker",
        data=cleaned_tracker_df.to_csv(index=False).encode("utf-8"),
        file_name="cleaned_investor_tracker.csv",
        mime="text/csv"
    )

elif page == "Lead Scoring":
    st.markdown('<div class="section-title">Outreach Readiness Breakdown</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="glass-card">
            <b>How the score works:</b> This page now scores record completeness, not investor attractiveness.<br>
            Email = 30 pts, 1st PiC = 20 pts, Investment Thesis = 20 pts, Website = 15 pts, Type = 10 pts, Location = 5 pts.
            <br><br>
            <b>Readiness labels:</b> Ready = 80–100, Partial = 50–79, Needs Research = below 50.
        </div>
        """,
        unsafe_allow_html=True
    )

    scoring_columns = [
        "Investor",
        "Type",
        "Location",
        "Website",
        "1st PiC",
        "Email 1",
        "Investment Thesis",
        "Score",
        "Priority",
        "Missing Fields"
    ]

    readiness_order = {
        "Ready": 1,
        "Partial": 2,
        "Needs Research": 3
    }

    scored_df = df.copy()
    scored_df["Missing Fields"] = scored_df.apply(get_missing_readiness_fields, axis=1)
    scored_df["Readiness Rank"] = scored_df["Priority"].map(readiness_order).fillna(4)
    scored_df = scored_df.sort_values(
        by=["Readiness Rank", "Score"],
        ascending=[True, False]
    )

    display_df = scored_df[scoring_columns].copy()
    display_df["Priority"] = display_df["Priority"].apply(priority_badge)
    display_df = display_df.rename(columns={
        "Score": "Readiness Score",
        "Priority": "Readiness"
    })

    html = display_df.to_html(index=False, escape=False)

    st.markdown(
        f"""
        <div class="data-readiness-table-wrap">
            {html}
        </div>
        """,
        unsafe_allow_html=True
    )

elif page == "Outreach Prep":
    st.markdown('<div class="section-title">Outreach Preparation Workspace</div>', unsafe_allow_html=True)

    selected_investor = st.selectbox(
        "Select Investor",
        df["Investor"].unique()
    )

    selected_row = df[df["Investor"] == selected_investor].iloc[0]

    st.markdown(
        """
        <div class="outreach-button-note">
            <b>Hunter.io</b> is used for PIC/contact enrichment. 
            <b>Company Email Scan</b> is not Hunter.io — it scans public website/contact/about pages.
        </div>
        """,
        unsafe_allow_html=True
    )

    top1, top2, top3, top4 = st.columns([1.05, 1.2, 1.2, 2.55])

    with top1:
        enrich_clicked = st.button("Enrich Selected")

    with top2:
        bulk_enrich_clicked = st.button("Find Missing PICs")

    with top3:
        scrape_clicked = st.button("Find Company Email")

    with top4:
        bulk_scrape_clicked = st.button("Find All Company Emails")

    # Clear the persistent neon message only when the user starts another action.
    # This keeps the message visible after reruns instead of flashing for 0.5 seconds.
    if enrich_clicked or bulk_enrich_clicked or scrape_clicked or bulk_scrape_clicked:
        st.session_state.persistent_neon_message = ""

    # =========================
    # HUNTER ENRICHMENT
    # =========================
    if enrich_clicked:
        with st.spinner("Searching Hunter.io for selected investor..."):
            hunter_result = enrich_single_investor_with_hunter(selected_row)

        if "hunter_enrichment_results" not in st.session_state:
            st.session_state.hunter_enrichment_results = {}

        st.session_state.hunter_enrichment_results[str(selected_investor)] = hunter_result
        st.rerun()

    if bulk_enrich_clicked:
        with st.spinner("Using Hunter.io only for rows where 1st PiC OR Email 1 is missing..."):
            bulk_results = enrich_all_investors_with_hunter(df)

        if "hunter_enrichment_results" not in st.session_state:
            st.session_state.hunter_enrichment_results = {}

        st.session_state.hunter_enrichment_results.update(bulk_results)

        if bulk_results:
            st.success(f"Hunter.io missing PIC/email enrichment completed for {len(bulk_results)} investor records.")

        st.rerun()

    # Render persistent neon message after Streamlit reruns.
    # It stays on screen until another Outreach Prep button is clicked.
    if st.session_state.get("persistent_neon_message", ""):
        st.markdown(st.session_state.persistent_neon_message, unsafe_allow_html=True)

    if bulk_scrape_clicked:
        with st.spinner("Scanning all available company websites for public company emails..."):
            company_email_results = find_all_company_emails_from_websites(df)

        if "company_email_results" not in st.session_state:
            st.session_state.company_email_results = {}

        st.session_state.company_email_results.update(company_email_results)

        found_count = 0
        for result in company_email_results.values():
            if isinstance(result, dict) and str(result.get("Company Email", "")).strip():
                found_count += 1
            elif not isinstance(result, dict) and str(result).strip():
                found_count += 1

        st.success(f"Company email scan completed. Scanned {len(company_email_results)} companies and found {found_count} company emails.")
        st.rerun()

    # =========================
    # WEBSITE EMAIL SCRAPE
    # =========================
    if scrape_clicked:
        website_to_check = (
            str(selected_row.get("Hunter Company Website", "")).strip()
            or str(selected_row.get("Website", "")).strip()
        )

        with st.spinner("Searching company website for public email..."):
            website_email = scrape_company_email_from_website(website_to_check)

        if "website_email_results" not in st.session_state:
            st.session_state.website_email_results = {}

        st.session_state.website_email_results[str(selected_investor)] = {
            "Company Email": website_email
        }

        st.rerun()

    selected_row = df[df["Investor"] == selected_investor].iloc[0]

    left_col, right_col = st.columns([1.05, 1])

    # =========================
    # SAFE DISPLAY VALUES
    # =========================
    pic1_name = str(selected_row.get("1st PiC", "")).strip() or "No Input"
    pic1_email = str(selected_row.get("Email 1", "")).strip() or "No Input"
    pic2_name = str(selected_row.get("2nd PiC", "")).strip() or "No Input"
    pic2_email = str(selected_row.get("Email 2", "")).strip() or "No Input"

    company_email = str(selected_row.get("Company Email", "")).strip() or "Not Found"

    hunter_company_name = str(selected_row.get("Hunter Company Name", "")).strip() or "Not Found"
    hunter_company_website = str(selected_row.get("Hunter Company Website", "")).strip() or "Not Found"
    hunter_company_linkedin = str(selected_row.get("Hunter Company LinkedIn", "")).strip() or "Not Found"

    hunter_name = str(selected_row.get("Hunter Name", "")).strip() or "Not Found"
    hunter_position = str(selected_row.get("Hunter Position", "")).strip() or "Not Found"
    hunter_email = str(selected_row.get("Hunter Email", "")).strip() or "Not Found"
    hunter_confidence = str(selected_row.get("Hunter Confidence", "")).strip() or "Not Found"
    hunter_linkedin = str(selected_row.get("Hunter LinkedIn", "")).strip() or "Not Found"

    # =========================
    # LEFT COLUMN
    # =========================
    with left_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        st.markdown("## Company & Contact Overview")

        st.write("### Company")
        st.write("**Investor:**", selected_row.get("Investor", ""))
        st.write("**Type:**", selected_row.get("Type", ""))
        st.write("**Location:**", selected_row.get("Location", ""))
        st.markdown("<br>", unsafe_allow_html=True)

        st.write("### Primary Contact")
        st.write("**PIC 1:**", pic1_name)
        st.write("**PIC 1 Email:**", pic1_email)

        st.markdown("<br>", unsafe_allow_html=True)

        st.write("### Secondary Contact")
        st.write("**PIC 2:**", pic2_name)
        st.write("**PIC 2 Email:**", pic2_email)

        st.markdown("<br>", unsafe_allow_html=True)

        st.write("### Company Inbox")
        st.write("**Company Email:**", company_email)

        st.markdown('</div>', unsafe_allow_html=True)

    # =========================
    # RIGHT COLUMN
    # =========================
    with right_col:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)

        st.markdown("## Hunter.io Intelligence")

        st.write("### Company Intelligence")
        st.write("**Company Name:**", hunter_company_name)
        st.write("**Company Website:**", hunter_company_website)
        st.write("**Company LinkedIn:**", hunter_company_linkedin)

        st.markdown("<br>", unsafe_allow_html=True)

        st.write("### Contact Intelligence")
        st.write("**Hunter Contact Name:**", hunter_name)
        st.write("**Hunter Position:**", hunter_position)
        st.write("**Hunter Verified Email:**", hunter_email)
        st.write("**Hunter Confidence:**", hunter_confidence)
        st.write("**Hunter Person LinkedIn:**", hunter_linkedin)

        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("## Investment Thesis")
    st.info(selected_row["Investment Thesis"])
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Email Outreach":
    st.markdown('<div class="section-title">Email Outreach Automation</div>', unsafe_allow_html=True)

    # Only use real outreach email fields.
    # Removed old generated fields: Generic Email, Contact Email, Best Company Email.
    allowed_email_columns = ["Email 1", "Email 2", "Hunter Email", "Company Email"]
    email_columns = [col for col in allowed_email_columns if col in df.columns]

    if not email_columns:
        st.error("No supported email columns found. Expected: Email 1, Email 2, Hunter Email, or Company Email.")
    else:
        try:
            smtp_server = st.secrets["SMTP_SERVER"]
            smtp_port = int(st.secrets["SMTP_PORT"])
            sender_email = st.secrets["SENDER_EMAIL"]
            sender_password = st.secrets["SENDER_PASSWORD"]
            test_email = st.secrets["TEST_EMAIL"]
            secrets_loaded = True
        except Exception:
            secrets_loaded = False
            st.error("SMTP secrets not found. Check `.streamlit/secrets.toml`.")

        if secrets_loaded:
            st.markdown("""
            <style>
            .placeholder-help-card {
                background: rgba(15, 23, 42, 0.96);
                border: 1px solid rgba(96, 165, 250, 0.35);
                border-radius: 16px;
                padding: 16px;
                margin: 10px 0 16px 0;
                box-shadow: 0 18px 42px rgba(0,0,0,0.30), 0 0 24px rgba(37,99,235,0.14);
            }
            .placeholder-help-card h4 {
                margin: 0 0 10px 0;
                color: #ffffff;
                font-size: 17px;
            }
            .placeholder-help-card li {
                color: #dbeafe;
                margin-bottom: 7px;
                font-size: 14px;
            }
            .template-preview-box {
                background: rgba(2, 6, 23, 0.72);
                border: 1px solid rgba(148, 163, 184, 0.20);
                border-radius: 14px;
                padding: 16px;
                white-space: pre-wrap;
                color: #e5e7eb;
                font-size: 14px;
                line-height: 1.55;
            }
            .template-tip-box {
                background: rgba(37, 99, 235, 0.12);
                border: 1px solid rgba(96, 165, 250, 0.24);
                border-radius: 14px;
                padding: 14px;
                color: #bfdbfe;
                font-size: 13px;
                line-height: 1.55;
                margin-bottom: 14px;
            }
            .builder-chip {
                display: inline-block;
                background: rgba(37, 99, 235, 0.22);
                border: 1px solid rgba(96, 165, 250, 0.45);
                color: #bfdbfe;
                border-radius: 999px;
                padding: 7px 12px;
                font-size: 13px;
                font-weight: 800;
                margin: 4px 4px 4px 0;
            }
            .builder-note {
                color: #94a3b8;
                font-size: 13px;
                line-height: 1.5;
                margin-top: 8px;
            }
            </style>
            """, unsafe_allow_html=True)

            default_subject_template = "Potential collaboration with {investor}"
            default_body_template = """{greeting}

I hope you're doing well.

I'm reaching out regarding {investor}. Based on your investment focus around {investment_thesis}, I thought there may be potential alignment with an opportunity we are currently reviewing.

Would you be open to a short introductory discussion?

Best regards,
{sender_name}
{sender_company}"""

            if "email_subject_template" not in st.session_state:
                st.session_state.email_subject_template = default_subject_template
            if "email_body_template" not in st.session_state:
                st.session_state.email_body_template = default_body_template
            if "show_template_help" not in st.session_state:
                st.session_state.show_template_help = False

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Sender Settings")
            st.write(f"**Sender:** {sender_email}")
            st.write(f"**SMTP Server:** {smtp_server}")
            st.write(f"**SMTP Port:** {smtp_port}")
            st.markdown('</div>', unsafe_allow_html=True)

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Recipient Sources")
            selected_email_cols = st.multiselect(
                "Select which email columns to use",
                email_columns,
                default=[email_columns[0]] if email_columns else []
            )

            investor_options = df["Investor"].astype(str).tolist()
            selected_investors = st.multiselect(
                "Select investors to email",
                investor_options,
                default=investor_options[:1] if investor_options else []
            )
            st.caption("Email outreach will use only the selected investor rows and selected recipient source columns.")
            st.markdown('</div>', unsafe_allow_html=True)

            # =========================
            # SIMPLE EMAIL TEMPLATE EDITOR
            # =========================
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Customizable Email Template")

            st.markdown("""
            <style>
            .placeholder-help-card {
                background: rgba(15, 23, 42, 0.96);
                border: 1px solid rgba(96, 165, 250, 0.35);
                border-radius: 16px;
                padding: 16px;
                margin: 10px 0 16px 0;
                box-shadow: 0 18px 42px rgba(0,0,0,0.30), 0 0 24px rgba(37,99,235,0.14);
            }
            .placeholder-help-card h4 { margin: 0 0 10px 0; color: #ffffff; font-size: 17px; }
            .placeholder-help-card li { color: #dbeafe; margin-bottom: 7px; font-size: 14px; }
            .template-preview-box {
                background: rgba(2, 6, 23, 0.72);
                border: 1px solid rgba(148, 163, 184, 0.20);
                border-radius: 14px;
                padding: 16px;
                white-space: pre-wrap;
                color: #e5e7eb;
                font-size: 14px;
                line-height: 1.55;
            }
            .template-tip-box {
                background: rgba(37, 99, 235, 0.12);
                border: 1px solid rgba(96, 165, 250, 0.24);
                border-radius: 14px;
                padding: 14px;
                color: #bfdbfe;
                font-size: 13px;
                line-height: 1.55;
                margin-bottom: 14px;
            }
            .placeholder-grid-label { color: #94a3b8; font-size: 13px; margin-bottom: 8px; }
            </style>
            """, unsafe_allow_html=True)

            if "show_template_help" not in st.session_state:
                st.session_state.show_template_help = False

            btn_col1, btn_col2, btn_col3 = st.columns([1.2, 1.2, 5])
            with btn_col1:
                if st.button("How to use template", key="template_help_btn"):
                    st.session_state.show_template_help = not st.session_state.show_template_help
            with btn_col2:
                if st.button("Reset template", key="template_reset_btn"):
                    st.session_state.email_subject_template = default_subject_template
                    st.session_state.email_body_template = default_body_template
                    st.rerun()
            with btn_col3:
                st.caption("Use the default template, or click inside the big body box and insert placeholders where your cursor is.")

            if st.session_state.show_template_help:
                st.markdown("""
                <div class="placeholder-help-card">
                    <h4>How to use the email template</h4>
                    <ul>
                        <li>Click inside the big <b>Body template</b> box where you want a field to appear.</li>
                        <li>Click a blue placeholder chip to insert it at your cursor position.</li>
                        <li>Edit normal wording directly inside the big body box.</li>
                        <li>Preview the real email before sending.</li>
                        <li>The greeting uses first name only, e.g. <b>Hi Michael,</b> not the full name.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)

            sender_col1, sender_col2 = st.columns(2)
            with sender_col1:
                sender_name = st.text_input("Sender name", value="Thet")
            with sender_col2:
                sender_company = st.text_input("Sender company", value="DealFlow")

            subject_template = st.text_input(
                "Subject template",
                value=st.session_state.email_subject_template,
                key="email_subject_template_input"
            )
            st.session_state.email_subject_template = subject_template

            st.markdown("#### Placeholder Panel")
            st.markdown('<div class="placeholder-grid-label">Click inside the body template first, then click a placeholder below. It will insert at your cursor.</div>', unsafe_allow_html=True)

            placeholder_keys = [
                "greeting", "investor", "investment_thesis", "type", "location", "sender_name", "sender_company",
            ]

            placeholder_buttons_html = """
            <div style="display:grid; grid-template-columns: repeat(7, minmax(120px, 1fr)); gap: 12px; margin: 12px 0 16px 0;">
            """
            for placeholder in placeholder_keys:
                placeholder_buttons_html += """
                <button type="button" class="template-placeholder-btn" data-placeholder="{0}" style="
                    background: rgba(37, 99, 235, 0.95);
                    color: #ffffff;
                    border: 1px solid rgba(96, 165, 250, 0.55);
                    border-radius: 12px;
                    padding: 12px 10px;
                    font-weight: 800;
                    cursor: pointer;
                    box-shadow: 0 10px 24px rgba(37,99,235,0.25);
                ">{0}</button>
                """.format("{" + placeholder + "}")
            placeholder_buttons_html += "</div>"

            body_template = st.text_area(
                "Body template",
                value=st.session_state.email_body_template,
                height=260,
                key="email_body_template_input",
                help="Click inside this box, then click a placeholder chip above to insert it at your cursor."
            )
            st.session_state.email_body_template = body_template

            components.html(
                placeholder_buttons_html + """
                <script>
                (function () {
                    const parentDoc = window.parent.document;

                    function findBodyTemplateBox() {
                        const textareas = Array.from(parentDoc.querySelectorAll('textarea'));
                        return textareas.find(t => {
                            const label = (t.getAttribute('aria-label') || '').toLowerCase();
                            return label.includes('body template');
                        }) || textareas[textareas.length - 1];
                    }

                    function setNativeValue(element, value) {
                        const valueSetter = Object.getOwnPropertyDescriptor(element, 'value')?.set;
                        const prototype = Object.getPrototypeOf(element);
                        const prototypeValueSetter = Object.getOwnPropertyDescriptor(prototype, 'value')?.set;
                        if (prototypeValueSetter && valueSetter !== prototypeValueSetter) {
                            prototypeValueSetter.call(element, value);
                        } else if (valueSetter) {
                            valueSetter.call(element, value);
                        } else {
                            element.value = value;
                        }
                        element.dispatchEvent(new Event('input', { bubbles: true }));
                        element.dispatchEvent(new Event('change', { bubbles: true }));
                    }

                    document.querySelectorAll('.template-placeholder-btn').forEach(btn => {
                        btn.addEventListener('click', function () {
                            const placeholder = this.getAttribute('data-placeholder');
                            const textarea = findBodyTemplateBox();
                            if (!textarea) return;
                            textarea.focus();
                            const start = textarea.selectionStart ?? textarea.value.length;
                            const end = textarea.selectionEnd ?? textarea.value.length;
                            const current = textarea.value || '';
                            const next = current.slice(0, start) + placeholder + current.slice(end);
                            setNativeValue(textarea, next);
                            const cursor = start + placeholder.length;
                            textarea.setSelectionRange(cursor, cursor);
                            textarea.focus();
                        });
                    });
                })();
                </script>
                """,
                height=92,
            )

            st.markdown("""
            <div class="template-tip-box">
                <b>Recommended:</b> keep <code>{greeting}</code> at the top, use <code>{investor}</code> for the investor/company name, and use <code>{investment_thesis}</code> for personalization.
            </div>
            """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            if selected_email_cols and selected_investors:
                selected_base_df = df[df["Investor"].astype(str).isin([str(x) for x in selected_investors])].copy()

                outreach_rows = []
                for _, row in selected_base_df.iterrows():
                    for email_col in selected_email_cols:
                        recipient = str(row.get(email_col, "")).strip()
                        if recipient and recipient.lower() not in ["nan", "none", "not found", "no input"]:
                            row_dict = row.to_dict()
                            outreach_rows.append({
                                "Investor": row.get("Investor", ""),
                                "Recipient Source": email_col,
                                "Actual Recipient": recipient,
                                "_row_data": row_dict
                            })

                selected_email_df = pd.DataFrame(outreach_rows)
            else:
                selected_email_df = pd.DataFrame()

            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Test Email Section")
            st.info("Use this section to send one test email to yourself before sending real outreach emails.")

            test_col1, test_col2 = st.columns([2, 1])
            with test_col1:
                selected_test_investor = st.selectbox(
                    "Select investor for test preview",
                    investor_options,
                    key="test_email_investor_select"
                )
            with test_col2:
                st.write("**Test recipient:**")
                st.code(test_email)

            test_row_data = df[df["Investor"].astype(str) == str(selected_test_investor)].iloc[0].to_dict()
            test_subject = render_email_template(subject_template, test_row_data, sender_name, sender_company)
            test_body = render_email_template(body_template, test_row_data, sender_name, sender_company)

            st.write("**Test Subject:**")
            st.code(test_subject)
            st.write("**Test Body:**")
            st.markdown(f'<div class="template-preview-box">{test_body}</div>', unsafe_allow_html=True)

            if st.button("Send Test Email To Myself"):
                try:
                    send_email_smtp(
                        smtp_server,
                        smtp_port,
                        sender_email,
                        sender_password,
                        test_email,
                        test_subject,
                        test_body,
                        ""
                    )
                    st.success(f"Test email sent to {test_email}.")
                except Exception as e:
                    st.error(f"Test email failed: {e}")

            st.markdown('</div>', unsafe_allow_html=True)

            if len(selected_email_df) > 0:
                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("### Real Outreach Preview")

                preview_rows = []
                for _, item in selected_email_df.iterrows():
                    row = item["_row_data"]
                    real_recipient = str(item["Actual Recipient"]).strip()
                    subject = render_email_template(subject_template, row, sender_name, sender_company)
                    body = render_email_template(body_template, row, sender_name, sender_company)

                    preview_rows.append({
                        "Investor": item["Investor"],
                        "Recipient Source": item["Recipient Source"],
                        "Actual Recipient": real_recipient,
                        "Subject": subject,
                        "Body Preview": body[:180] + "..."
                    })

                preview_df = pd.DataFrame(preview_rows)
                st.dataframe(preview_df, use_container_width=True)

                preview_options = [
                    f"{item['Investor']} — {item['Recipient Source']} — {item['Actual Recipient']}"
                    for _, item in selected_email_df.iterrows()
                ]

                selected_preview = st.selectbox("Preview full real email for", preview_options)
                selected_preview_index = preview_options.index(selected_preview)
                preview_item = selected_email_df.iloc[selected_preview_index]
                preview_row = preview_item["_row_data"]

                full_subject = render_email_template(subject_template, preview_row, sender_name, sender_company)
                full_body = render_email_template(body_template, preview_row, sender_name, sender_company)

                st.write("**Subject:**")
                st.code(full_subject)
                st.write("**Body Preview:**")
                st.markdown(f'<div class="template-preview-box">{full_body}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

                st.markdown('<div class="glass-card">', unsafe_allow_html=True)
                st.markdown("### Email Controls")
                cc_email = st.text_input(
                    "CC email(s)",
                    value="",
                    placeholder="Optional. Example: manager@company.com, teammate@company.com"
                )
                delay_seconds = st.number_input(
                    "Delay between emails (seconds)",
                    min_value=0,
                    max_value=300,
                    value=5,
                    step=1
                )
                max_send = st.number_input(
                    "Maximum emails to send now",
                    min_value=1,
                    max_value=max(1, len(selected_email_df)),
                    value=1,
                    step=1
                )

                st.divider()
                confirm_send = st.checkbox("I confirm I want to send these selected emails to the real recipients")

                if st.button("Send Selected Real Emails"):
                    if not confirm_send:
                        st.error("Please tick the confirmation checkbox first.")
                    else:
                        sent_count = 0
                        failed = []
                        send_df = selected_email_df.head(max_send)
                        progress = st.progress(0)
                        status_text = st.empty()

                        for index, (_, item) in enumerate(send_df.iterrows(), start=1):
                            row = item["_row_data"]
                            recipient = str(item["Actual Recipient"]).strip()
                            subject = render_email_template(subject_template, row, sender_name, sender_company)
                            body = render_email_template(body_template, row, sender_name, sender_company)

                            try:
                                status_text.write(f"Sending {index}/{len(send_df)} to {recipient}...")
                                send_email_smtp(
                                    smtp_server,
                                    smtp_port,
                                    sender_email,
                                    sender_password,
                                    recipient,
                                    subject,
                                    body,
                                    cc_email
                                )
                                sent_count += 1
                            except Exception as e:
                                failed.append({
                                    "Investor": item["Investor"],
                                    "Recipient Source": item["Recipient Source"],
                                    "Recipient": recipient,
                                    "Error": str(e)
                                })

                            progress.progress(index / len(send_df))

                            if index < len(send_df) and delay_seconds > 0:
                                time.sleep(delay_seconds)

                        status_text.write("Done.")

                        if sent_count > 0:
                            st.success(f"Successfully sent {sent_count} real email(s).")

                        if failed:
                            st.error("Some emails failed to send.")
                            st.dataframe(pd.DataFrame(failed), use_container_width=True)

                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Select at least one investor and at least one valid recipient source to preview and send emails.")
