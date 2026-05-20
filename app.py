import streamlit as st
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

    st.markdown(f"""
    <style>
    .stApp {{
        background: linear-gradient(135deg, #07111f 0%, #0b1628 50%, #0f1f35 100%);
        color: #f8fafc;
        font-family: Inter, Arial, sans-serif;
    }}

    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Do not hide Streamlit header, because the sidebar reopen arrow lives there */
    header {{
        background: transparent !important;
    }}

    [data-testid="stHeader"] {{
        background: transparent !important;
    }}

    section[data-testid="stSidebar"] {{
        display: block !important;
        visibility: visible !important;
        transform: translateX(0px) !important;
        margin-left: 0 !important;
    }}
    

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
        width: 270px !important;
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
        padding: 8px 0 24px 0;
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
        margin-bottom: 18px;
    }}

    .sidebar-summary-item {{
        margin-bottom: 18px;
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
    </style>
    """, unsafe_allow_html=True)


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


def send_email_smtp(smtp_server, smtp_port, sender_email, password, recipient, subject, body):
    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls(context=context)
        server.login(sender_email, password)
        server.send_message(msg)


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


def prepare_dataframe(uploaded_file):
    df_original = pd.read_excel(uploaded_file)
    original_count = len(df_original)

    df = df_original.copy().dropna(how="all")

    text_columns = [
        "Investor", "Type", "Location", "Website",
        "1st PiC", "Email 1", "2nd PiC", "Email 2",
        "Investment Thesis", "Status"
    ]

    for col in text_columns:
        if col in df.columns:
            df[col] = df[col].fillna("").astype(str).str.strip()

    required_subset = [col for col in ["Investor", "Website", "Email 1"] if col in df.columns]
    df = df.drop_duplicates(subset=required_subset) if required_subset else df.drop_duplicates()

    for col in ["Website", "Investor", "Type", "Location", "Investment Thesis", "Email 1"]:
        if col not in df.columns:
            df[col] = ""

    cleaned_count = len(df)
    duplicates_removed = original_count - cleaned_count

    df["Domain"] = df["Website"].apply(clean_domain)
    df["Generic Email"] = df["Domain"].apply(generate_generic_email)
    df["Contact Email"] = df["Domain"].apply(generate_contact_email)
    df["Website Email"] = ""
    df["Best Company Email"] = df.apply(get_best_company_email, axis=1)
    df["LinkedIn Search"] = df["Investor"].apply(generate_linkedin_search)
    df["Possible Contact Page"] = df["Domain"].apply(generate_contact_page)

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
        "Website Email",
        "Best Company Email"
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


# =========================
# FILE UPLOAD FIRST
# =========================
existing_file = st.session_state.get("uploaded_file_object", None)
load_css(has_file=existing_file is not None)

if existing_file is None:
    st.markdown("""
    <div class="landing-wrap">
        <div class="landing-card">
            <div class="landing-title">Investor Outreach Automation Dashboard</div>
            <div class="landing-subtitle">
                Upload your investor Excel tracker to clean records, score leads, generate dashboard visuals, and prepare outreach.
            </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="landing-upload">', unsafe_allow_html=True)
    first_upload = st.file_uploader("Upload Investor Excel File", type=["xlsx"])
    st.markdown('</div></div></div>', unsafe_allow_html=True)

    if first_upload is not None:
        st.session_state.uploaded_file_object = first_upload
        st.session_state.uploaded_file_name = first_upload.name
        st.session_state.uploaded_time = datetime.now().strftime("%b %d, %Y %I:%M %p")
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
    "Email Outreach": ("Email Outreach", "SMTP-based outreach preview and sending workspace"),
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
    new_upload = st.file_uploader("Add New File", type=["xlsx"], label_visibility="collapsed", key="add_new_file")
    st.markdown('</div>', unsafe_allow_html=True)

if new_upload is not None:
    st.session_state.uploaded_file_object = new_upload
    st.session_state.uploaded_file_name = new_upload.name
    st.session_state.uploaded_time = datetime.now().strftime("%b %d, %Y %I:%M %p")
    st.rerun()

st.markdown('</div>', unsafe_allow_html=True)


# =========================
# DATA PROCESSING
# =========================
df, original_count, duplicates_removed = prepare_dataframe(st.session_state.uploaded_file_object)

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
        "Website Email",
        "Best Company Email"
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

    for col in ["Website Email", "Best Company Email"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].astype("string")

    for investor_name, result in website_results.items():
        investor_mask = df["Investor"].astype(str) == str(investor_name)

        for col_name, col_value in result.items():
            if col_name in df.columns:
                safe_value = "" if pd.isna(col_value) else str(col_value)
                df.loc[investor_mask, col_name] = safe_value

    df["Best Company Email"] = df.apply(get_best_company_email, axis=1)


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
    scoring_columns = ["Investor", "Type", "Location", "Investment Thesis", "Score", "Priority"]
    scored_df = df.sort_values(by="Score", ascending=False)
    render_priority_table(scored_df[scoring_columns])

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
            "Website Email": website_email
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

    website_email = str(selected_row.get("Website Email", "")).strip() or "Not Found"

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
        st.write("**Website:**", selected_row.get("Website", ""))

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
        st.write("**Website Email:**", website_email)

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
    st.warning("Test mode is enabled by default. Emails will be sent to yourself first.")

    email_columns = [col for col in df.columns if "email" in col.lower()]

    if not email_columns:
        st.error("No email column found in your Excel file.")
    else:
        email_col = st.selectbox("Select recipient email column", email_columns)
        outreach_df = df[df[email_col].astype(str).str.strip() != ""].copy()
        st.write(f"Detected **{len(outreach_df)}** rows with emails.")

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
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.markdown("### Sender Settings")
            st.write(f"**Sender:** {sender_email}")
            st.write(f"**SMTP Server:** {smtp_server}")
            st.write(f"**SMTP Port:** {smtp_port}")
            st.markdown('</div>', unsafe_allow_html=True)

            test_mode = st.checkbox("Test mode: send all emails to myself", value=True)
            selected_investors = st.multiselect("Select investors to email", outreach_df["Investor"].tolist())
            selected_email_df = outreach_df[outreach_df["Investor"].isin(selected_investors)].copy()

            if len(selected_email_df) > 0:
                st.markdown("### Email Preview")
                preview_rows = []

                for _, row in selected_email_df.iterrows():
                    real_recipient = str(row.get(email_col, "")).strip()
                    final_recipient = test_email if test_mode else real_recipient
                    subject = create_email_subject(row)
                    body = create_email_body(row)
                    preview_rows.append({
                        "Investor": row.get("Investor", ""),
                        "Actual Recipient": real_recipient,
                        "Send To": final_recipient,
                        "Subject": subject,
                        "Body Preview": body[:180] + "..."
                    })

                st.dataframe(pd.DataFrame(preview_rows), use_container_width=True)
                selected_preview = st.selectbox("Preview full email for", selected_email_df["Investor"].tolist())
                preview_row = selected_email_df[selected_email_df["Investor"] == selected_preview].iloc[0]

                st.write("**Subject:**")
                st.code(create_email_subject(preview_row))
                st.write("**Body Preview:**")
                st.code(create_email_body(preview_row))
                st.divider()

                max_send = st.number_input("Maximum emails to send now", min_value=1, max_value=10, value=1)
                confirm_send = st.checkbox("I confirm I want to send these selected emails")

                if st.button("Send Selected Emails"):
                    if not confirm_send:
                        st.error("Please tick the confirmation checkbox first.")
                    else:
                        sent_count = 0
                        failed = []
                        send_df = selected_email_df.head(max_send)

                        for _, row in send_df.iterrows():
                            real_recipient = str(row.get(email_col, "")).strip()
                            recipient = test_email if test_mode else real_recipient
                            subject = create_email_subject(row)
                            body = create_email_body(row)

                            try:
                                send_email_smtp(smtp_server, smtp_port, sender_email, sender_password, recipient, subject, body)
                                sent_count += 1
                            except Exception as e:
                                failed.append({"Investor": row.get("Investor", ""), "Recipient": recipient, "Error": str(e)})

                        if sent_count > 0:
                            st.success(f"Successfully sent {sent_count} email(s).")

                        if failed:
                            st.error("Some emails failed to send.")
                            st.dataframe(pd.DataFrame(failed), use_container_width=True)
            else:
                st.info("Select at least one investor to preview and send emails.")
