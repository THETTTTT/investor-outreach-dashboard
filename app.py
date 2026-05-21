import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import quote
import smtplib
import ssl
from email.message import EmailMessage
from datetime import datetime
import time


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


def scrape_company_email_from_website(website):
    if pd.isna(website) or str(website).strip() == "":
        return ""

    website = str(website).strip()

    if not website.startswith(("http://", "https://")):
        website = "https://" + website

    urls_to_check = [
        website,
        website.rstrip("/") + "/contact",
        website.rstrip("/") + "/contact-us",
        website.rstrip("/") + "/about",
    ]

    email_pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"
    blocked_extensions = [".png", ".jpg", ".jpeg", ".webp", ".gif", ".svg"]
    priority_keywords = ["contact", "hello", "info", "team", "admin", "support", "enquiry", "inquiries"]

    found_emails = []

    for url in urls_to_check:
        try:
            response = requests.get(
                url,
                timeout=8,
                headers={"User-Agent": "Mozilla/5.0"}
            )

            if response.status_code >= 400:
                continue

            soup = BeautifulSoup(response.text, "html.parser")

            for mailto in soup.select('a[href^="mailto:"]'):
                email = mailto.get("href", "").replace("mailto:", "").split("?")[0].strip()
                if email:
                    found_emails.append(email)

            page_text = soup.get_text(" ")
            found_emails.extend(re.findall(email_pattern, page_text))

        except Exception:
            continue

    cleaned_emails = []

    for email in found_emails:
        email = email.strip().strip(".").strip(",").strip(";").lower()

        if any(ext in email for ext in blocked_extensions):
            continue

        if email not in cleaned_emails:
            cleaned_emails.append(email)

    for email in cleaned_emails:
        if any(keyword in email for keyword in priority_keywords):
            return email

    return cleaned_emails[0] if cleaned_emails else ""


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


def calculate_score(row):
    score = 0
    investor_type = str(row.get("Type", "")).lower()
    location = str(row.get("Location", "")).lower()
    thesis = str(row.get("Investment Thesis", "")).lower()
    email = str(row.get("Email 1", "")).strip()
    website = str(row.get("Website", "")).strip()

    if "vc" in investor_type:
        score += 25
    elif "family office" in investor_type:
        score += 25
    elif "corporate vc" in investor_type:
        score += 22
    elif "accelerator" in investor_type:
        score += 18
    elif "fund" in investor_type:
        score += 18
    elif "investor" in investor_type:
        score += 15

    if location in ["singapore", "us", "usa", "japan", "hong kong"]:
        score += 18
    elif location in ["vietnam", "indonesia", "malaysia", "thailand", "philippines"]:
        score += 12

    keywords = [
        "technology", "deeptech", "deep tech", "quantum", "ai",
        "software", "enterprise", "cloud", "consumer", "retail",
        "startup", "digital", "fintech", "sea"
    ]

    for keyword in keywords:
        if keyword in thesis:
            score += 4

    if email != "":
        score += 12

    if website != "":
        score += 8

    return min(score, 100)


def assign_priority(score):
    if score >= 70:
        return "High"
    elif score >= 45:
        return "Medium"
    return "Low"


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
    if priority_text == "high":
        return '<span class="badge badge-high">High</span>'
    if priority_text == "medium":
        return '<span class="badge badge-medium">Medium</span>'
    if priority_text == "low":
        return '<span class="badge badge-low">Low</span>'
    return str(priority)


def render_priority_table(dataframe):
    display_df = dataframe.copy()
    if "Priority" in display_df.columns:
        display_df["Priority"] = display_df["Priority"].apply(priority_badge)

    html = display_df.to_html(index=False, escape=False)
    st.markdown(
        f"""
        <div style="border:1px solid rgba(148,163,184,0.18); border-radius:14px; overflow:hidden;">
            {html}
        </div>
        <style>
        table {{ width: 100%; border-collapse: collapse; color: #e5e7eb; font-size: 13px; }}
        th {{ background: rgba(30, 41, 59, 0.95); color: #94a3b8; text-align: left; padding: 12px; font-size: 12px; text-transform: uppercase; letter-spacing: 0.04em; }}
        td {{ background: rgba(15, 23, 42, 0.72); border-top: 1px solid rgba(148, 163, 184, 0.12); padding: 12px; }}
        </style>
        """,
        unsafe_allow_html=True
    )



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

    # Type
    "type": "Type", "investor type": "Type", "fund type": "Type", "category": "Type",
    "classification": "Type", "sector": "Type", "industry": "Type", "vertical": "Type",

    # Location
    "location": "Location", "country": "Location", "region": "Location", "geography": "Location",
    "market": "Location", "hq": "Location", "headquarters": "Location", "office location": "Location",
    "address": "Location", "city": "Location", "base": "Location", "based in": "Location",

    # Website
    "website": "Website", "web site": "Website", "url": "Website", "website url": "Website",
    "company website": "Website", "homepage": "Website", "domain": "Website", "site": "Website",
    "linkedin": "Website", "linkedin url": "Website", "source url": "Website", "link": "Website",

    # Primary contact
    "name": "1st PiC", "contact": "1st PiC", "contact name": "1st PiC", "person": "1st PiC",
    "pic": "1st PiC", "1st pic": "1st PiC", "primary contact": "1st PiC", "contact person": "1st PiC",
    "representative": "1st PiC", "partner": "1st PiC", "partner name": "1st PiC", "full name": "1st PiC",
    "decision maker": "1st PiC", "contact 1": "1st PiC", "pic 1": "1st PiC",

    # Primary email
    "email": "Email 1", "email address": "Email 1", "e mail": "Email 1", "mail": "Email 1",
    "contact email": "Email 1", "primary email": "Email 1", "email 1": "Email 1", "1st email": "Email 1",
    "pic email": "Email 1", "contact email 1": "Email 1",

    # Secondary contact/email
    "second contact": "2nd PiC", "secondary contact": "2nd PiC", "2nd pic": "2nd PiC",
    "contact 2": "2nd PiC", "second name": "2nd PiC", "secondary name": "2nd PiC", "pic 2": "2nd PiC",
    "secondary email": "Email 2", "second email": "Email 2", "email 2": "Email 2", "2nd email": "Email 2",
    "contact email 2": "Email 2",

    # Thesis / notes
    "investment thesis": "Investment Thesis", "thesis": "Investment Thesis", "focus": "Investment Thesis",
    "investment focus": "Investment Thesis", "mandate": "Investment Thesis", "strategy": "Investment Thesis",
    "notes": "Investment Thesis", "note": "Investment Thesis", "description": "Investment Thesis",
    "remarks": "Investment Thesis", "comment": "Investment Thesis", "comments": "Investment Thesis",
    "memo": "Investment Thesis", "criteria": "Investment Thesis",

    # Status
    "status": "Status", "outreach status": "Status", "stage": "Status", "progress": "Status",
    "follow up": "Status", "follow up status": "Status",
}

HEADER_KEYWORDS = set(COLUMN_ALIASES.keys()) | {
    "email", "organization", "organisation", "company", "fund", "name", "type", "title",
    "notes", "source", "website", "location", "sector", "partner", "country", "url"
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
        if is_blankish(result.at[idx, "Investment Thesis"]):
            note_parts = []
            for col in thesis_candidates:
                val = clean_cell_value(raw_row.get(col, ""))
                if not val:
                    continue
                if EMAIL_RE.fullmatch(val) or URL_RE.fullmatch(val) or re.fullmatch(r"[0-9,\.\-]+", val):
                    continue
                if normalize_column_name(val) == normalize_column_name(result.at[idx, "Investor"]):
                    continue
                if val not in note_parts:
                    note_parts.append(val)
            if note_parts:
                result.at[idx, "Investment Thesis"] = " | ".join(note_parts[:3])

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
        if tokens & {"organization", "organisation", "company", "firm", "fund", "investor", "entity", "manager", "institution", "gp"}:
            score += 60
        if norm in ["name", "fund name", "company name", "organisation name", "organization name", "investor name"]:
            score += 35
        if tokens & {"contact", "person", "partner", "pic", "email", "title", "role"}:
            score -= 35
        if e_ratio > 0.05 or u_ratio > 0.2 or n_ratio > 0.55:
            score -= 65
        if 1 <= avg_words <= 6:
            score += 15
        if avg_words > 10:
            score -= 10

    elif target == "1st PiC":
        if tokens & {"name", "contact", "person", "partner", "pic", "representative"}:
            score += 45
        if tokens & {"organization", "organisation", "company", "firm", "fund", "investor"}:
            score -= 45
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
        if tokens & {"thesis", "focus", "strategy", "mandate", "notes", "note", "description", "remarks", "comment", "comments", "criteria", "memo"}:
            score += 55
        if "source" in tokens:
            # Source becomes thesis only when it is text notes, not links.
            score += 20 if u_ratio < 0.2 else -35
        if "title" in tokens or "role" in tokens or "position" in tokens:
            score += 8
        if avg_words >= 5:
            score += 18
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
    if any(word in normalized for word in ["website", "url", "domain", "homepage", "linkedin"]):
        return "Website"
    if any(word in normalized for word in ["company", "organization", "organisation", "fund", "firm", "investor"]):
        return "Investor"
    if any(word in normalized for word in ["country", "location", "region", "market", "geography", "hq", "headquarter"]):
        return "Location"
    if any(word in normalized for word in ["thesis", "focus", "strategy", "mandate", "notes", "description", "remarks", "comment"]):
        return "Investment Thesis"
    if "type" in normalized or "category" in normalized or "classification" in normalized or "sector" in normalized:
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


def read_uploaded_file_smart(uploaded_file):
    """Read CSV/XLS/XLSX and return the best detected table as a dataframe."""
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

    sheets = pd.read_excel(uploaded_file, sheet_name=None, header=None, dtype=str)
    best = None
    for sheet_name, raw_no_header in sheets.items():
        if raw_no_header.empty:
            continue
        header_idx, header_score = detect_header_row(raw_no_header)
        current = (header_score, sheet_name, header_idx, raw_no_header)
        if best is None or current[0] > best[0]:
            best = current

    if best is None:
        raise ValueError("No readable sheet found in the uploaded file.")

    header_score, sheet_name, header_idx, raw_no_header = best
    headers = make_unique_columns(raw_no_header.iloc[header_idx].tolist())
    df = raw_no_header.iloc[header_idx + 1:].copy()
    df.columns = headers
    return df.dropna(how="all"), sheet_name, header_idx + 1, header_score


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
            if any(x in norm for x in ["org", "company", "firm", "fund", "investor", "manager"]):
                score += 50
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
        if any(x in norm for x in ["note", "description", "focus", "strategy", "remark", "comment", "criteria", "memo", "title"]):
            if email_ratio(df_raw[raw_col]) < 0.05 and url_ratio(df_raw[raw_col]) < 0.3:
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


def render_import_cleaner(uploaded_file):
    """Show upload review, auto-cleaning, simple manual fixes, and confirmation before dashboard loads."""
    st.markdown('<div class="main-title">Review & Auto-Clean Uploaded File</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">The app detects the table, maps messy columns into the standard tracker format, and lets you fix only the fields that look wrong.</div>',
        unsafe_allow_html=True
    )
    st.markdown("<br>", unsafe_allow_html=True)

    try:
        raw_df, sheet_name, header_row, header_score = read_uploaded_file_smart(uploaded_file)
    except Exception as e:
        st.error(f"Could not read this file: {e}")
        if st.button("Upload another file"):
            for key in ["raw_uploaded_file", "uploaded_file_object", "cleaned_import_df", "import_stage"]:
                st.session_state.pop(key, None)
            st.rerun()
        st.stop()

    auto_df, auto_mapping, warnings, auto_confidence = standardize_uploaded_dataframe(raw_df)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 1) File Detection")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Detected sheet", str(sheet_name))
    c2.metric("Header row", header_row)
    c3.metric("Raw rows", len(raw_df))
    c4.metric("Cleaned rows", len(auto_df))
    st.caption("If the preview below looks correct, just click **Use Auto-Cleaned File**. No manual work needed.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 2) Extracted Key Fields")
    st.caption("The app first extracts emails, websites, investor names, contacts, type, location, and notes from the whole sheet, then maps them into your standard tracker format.")
    render_mapping_table(auto_mapping, auto_confidence)
    if warnings:
        for warning in warnings:
            st.warning(warning)
    else:
        st.success("Auto-clean looks good. Check the preview, then continue.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("### 3) Auto-Cleaned Preview")
    st.dataframe(auto_df.head(30), use_container_width=True)
    b1, b2, b3 = st.columns([1.2, 1, 4])
    with b1:
        if st.button("Use Auto-Cleaned File", type="primary"):
            st.session_state.cleaned_import_df = auto_df
            st.session_state.uploaded_file_object = uploaded_file
            st.session_state.uploaded_file_name = uploaded_file.name
            st.session_state.uploaded_time = datetime.now().strftime("%b %d, %Y %I:%M %p")
            st.session_state.import_stage = "ready"
            st.rerun()
    with b2:
        if st.button("Cancel Upload"):
            for key in ["raw_uploaded_file", "uploaded_file_object", "cleaned_import_df", "import_stage"]:
                st.session_state.pop(key, None)
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    with st.expander("Fix mapping manually only if preview looks wrong", expanded=bool(warnings)):
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
        st.markdown("#### Preview after your fixes")
        st.dataframe(preview_df.head(30), use_container_width=True)
        if manual_warnings:
            for warning in manual_warnings:
                st.warning(warning)

        if st.button("Use This Fixed Mapping", type="primary"):
            st.session_state.cleaned_import_df = preview_df
            st.session_state.uploaded_file_object = uploaded_file
            st.session_state.uploaded_file_name = uploaded_file.name
            st.session_state.uploaded_time = datetime.now().strftime("%b %d, %Y %I:%M %p")
            st.session_state.import_stage = "ready"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.stop()


# =========================
# FILE UPLOAD FIRST + SMART IMPORT CLEANER
# =========================
existing_file = st.session_state.get("uploaded_file_object", None)
existing_cleaned_df = st.session_state.get("cleaned_import_df", None)
raw_import_file = st.session_state.get("raw_uploaded_file", None)

load_css(has_file=(existing_file is not None or existing_cleaned_df is not None or raw_import_file is not None))
render_neon_mouse_effects()

# If a new raw file was uploaded, clean/map it before allowing the dashboard to load.
if st.session_state.get("import_stage") == "mapping" and raw_import_file is not None:
    render_import_cleaner(raw_import_file)

if existing_cleaned_df is None and existing_file is None:
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
    "Lead Scoring": ("Lead Scoring", "Scoring breakdown and priority ranking for each investor"),
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
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)


# =========================
# DATA PROCESSING
# =========================
df, original_count, duplicates_removed = prepare_dataframe_from_df(st.session_state.cleaned_import_df) if "cleaned_import_df" in st.session_state else prepare_dataframe(st.session_state.uploaded_file_object)

total_investors = len(df)
high_priority = (df["Priority"] == "High").sum()
locations_count = df["Location"].replace("", pd.NA).dropna().nunique()
emails_available = (df["Email 1"].astype(str).str.strip() != "").sum()
avg_score = round(df["Score"].mean(), 1) if len(df) > 0 else 0
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
        high_pct = round((high_priority / total_investors) * 100, 1) if total_investors else 0
        kpi_card("High Priority", high_priority, f"{high_pct}% of total", "🔥", "kpi-icon-purple")

    with c4:
        kpi_card("Locations", locations_count, "Countries / Regions", "🌍", "kpi-icon-yellow")

    with c5:
        email_pct = round((emails_available / total_investors) * 100, 1) if total_investors else 0
        kpi_card("Emails Available", emails_available, f"{email_pct}% of total", "📧", "kpi-icon-teal")

    with c6:
        kpi_card("Avg Score", avg_score, "Out of 100", "📈", "kpi-icon-cyan")

    st.markdown("<br>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">Filter Investors</div>', unsafe_allow_html=True)

    f1, f2, f3, f4, f5 = st.columns([1.2, 1.2, 1.1, 1.1, 1.8])

    selected_location = f1.selectbox("Location", ["All Locations"] + sorted([x for x in df["Location"].dropna().unique() if x != ""]))
    selected_type = f2.selectbox("Type", ["All Types"] + sorted([x for x in df["Type"].dropna().unique() if x != ""]))
    selected_priority = f3.selectbox("Priority", ["All Priorities"] + sorted(df["Priority"].dropna().unique()))
    selected_status = f4.selectbox("Status", ["All Statuses"] + sorted(df["Status"].dropna().unique()))
    search_query = f5.text_input("Search Investor", placeholder="Search by investor name...")

    filtered_df = df.copy()

    if selected_location != "All Locations":
        filtered_df = filtered_df[filtered_df["Location"] == selected_location]
    if selected_type != "All Types":
        filtered_df = filtered_df[filtered_df["Type"] == selected_type]
    if selected_priority != "All Priorities":
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
            st.markdown('<div class="chart-title">Priority Breakdown</div>', unsafe_allow_html=True)
            priority_counts = filtered_df["Priority"].value_counts().reset_index()
            priority_counts.columns = ["Priority", "Count"]
            fig_priority = px.pie(
                priority_counts,
                names="Priority",
                values="Count",
                hole=0.55,
                color="Priority",
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_priority = style_plotly_chart(fig_priority, height=270)
            st.plotly_chart(fig_priority, use_container_width=True)

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
    st.markdown('<div class="section-title">Top Scoring Investors</div>', unsafe_allow_html=True)
    top_investors = filtered_df.sort_values(by="Score", ascending=False)[["Investor", "Type", "Location", "Score", "Priority", "Status"]].head(5)
    render_priority_table(top_investors)
    st.markdown("<br>", unsafe_allow_html=True)
    st.button("View All Investors", on_click=go_to_cleaned_tracker)
    st.markdown('</div>', unsafe_allow_html=True)

elif page == "Cleaned Tracker":
    st.dataframe(df, use_container_width=True)
    st.download_button(
        label="Download Cleaned Investor Tracker",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="cleaned_investor_tracker.csv",
        mime="text/csv"
    )

elif page == "Lead Scoring":
    st.markdown('<div class="section-title">Investor Scoring Breakdown</div>', unsafe_allow_html=True)

    scoring_columns = [
        "Investor",
        "Type",
        "Location",
        "Investment Thesis",
        "Score",
        "Priority"
    ]

    priority_order = {
        "High": 1,
        "Medium": 2,
        "Low": 3
    }

    scored_df = df.copy()
    scored_df["Priority Rank"] = scored_df["Priority"].map(priority_order).fillna(4)
    scored_df = scored_df.sort_values(
        by=["Priority Rank", "Score"],
        ascending=[True, False]
    )

    display_df = scored_df[scoring_columns].copy()
    display_df["Priority"] = display_df["Priority"].apply(priority_badge)

    html = display_df.to_html(index=False, escape=False)

    st.markdown(
        f"""
        <div style="
            border:1px solid rgba(148,163,184,0.18);
            border-radius:14px;
            overflow:hidden;
            max-height:650px;
            overflow-y:auto;
        ">
            {html}
        </div>
        <style>
        table {{
            width: 100%;
            border-collapse: collapse;
            color: #e5e7eb;
            font-size: 13px;
        }}
        th {{
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
        }}
        td {{
            background: rgba(15, 23, 42, 0.72);
            border-top: 1px solid rgba(148, 163, 184, 0.12);
            padding: 12px;
        }}
        </style>
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

    top1, top2, top3 = st.columns([1, 1, 3])

    with top1:
        enrich_clicked = st.button("Enrich with Hunter.io")

    with top2:
        scrape_clicked = st.button("Find Company Email")

    with top3:
        st.caption(
            "Hunter.io pulls verified company/contact intelligence. "
            "Company email lookup scans the actual website for public inboxes."
        )

    # =========================
    # HUNTER ENRICHMENT
    # =========================
    if enrich_clicked:
        with st.spinner("Searching Hunter.io..."):
            hunter_result = enrich_single_investor_with_hunter(selected_row)

        if "hunter_enrichment_results" not in st.session_state:
            st.session_state.hunter_enrichment_results = {}

        st.session_state.hunter_enrichment_results[str(selected_investor)] = hunter_result
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
