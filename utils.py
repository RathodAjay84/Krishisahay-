# utils.py
"""Utility functions used across the KrishiSahay platform."""

import streamlit as st

# simple multilingual support with hard‑coded texts
LANGUAGES = {
    "English": {
        "home_title": "KrishiSahay – Smart Farming Assistant",
        "nav_home": "Home",
        "nav_crop": "Crop Recommendation",
        "nav_disease": "Plant Disease Detection",
        "nav_fertilizer": "Fertilizer Guide",
        "nav_weather": "Weather",
        "nav_market": "Market Prices",
        "nav_schemes": "Government Schemes",
        "nav_chat": "Chatbot",
        "soil": "Soil Type",
        "season": "Season",
        "rainfall": "Rainfall (mm)",
        "recommend": "Recommend Crop",
        # ... add more keys as needed
    },
    "Hindi": {
        "home_title": "कृषिसहाय – स्मार्ट खेती सहायक",
        "nav_home": "होम",
        "nav_crop": "फसल सुझाव",
        "nav_disease": "रोग पहचान",
        "nav_fertilizer": "उर्वरक मार्गदर्शन",
        "nav_weather": "मौसम",
        "nav_market": "बाजार भाव",
        "nav_schemes": "सरकारी योजनाएँ",
        "nav_chat": "चैटबॉट",
        "soil": "मृदा प्रकार",
        "season": "मौसम",
        "rainfall": "वर्षा (मिमी)",
        "recommend": "फसल सुझाएँ",
    },
    "Telugu": {
        "home_title": "కృష్ణిసహాయ్ – స్మార్ట్ వ్యవసాయ సహాయకుడు",
        "nav_home": "హోమ్",
        "nav_crop": "పంట సిఫార్సు",
        "nav_disease": "రోగ గుర్తింపు",
        "nav_fertilizer": "రసాయనం మార్గదర్శనం",
        "nav_weather": "వాతావరణం",
        "nav_market": "మార్కెట్ ధరలు",
        "nav_schemes": "ప్రభుత్వ పథకాలు",
        "nav_chat": "చాట్బాట్",
        "soil": "మట్టిది రకం",
        "season": "కాలం",
        "rainfall": "వర్షపాతం (మిమీ)",
        "recommend": "పంట సిఫార్సు చేయండి",
    },
}


def t(key: str, lang: str = "English") -> str:
    """Translate a given message key according to the selected language."""
    return LANGUAGES.get(lang, LANGUAGES["English"]).get(key, key)


def load_css():
    """Inject custom CSS for improved UI/UX."""
    st.markdown(
        """
        <style>
        .stApp {
            background: #f4f7f1;
            font-family: 'Trebuchet MS', sans-serif;
            color: #17301f;
        }
        [data-testid="stHeader"] {
            background: rgba(244, 247, 241, 0.92);
        }
        [data-testid="stMainBlockContainer"] {
            max-width: 1440px;
            padding-top: 2rem;
        }
        .stApp p,
        .stApp span,
        .stApp label,
        .stApp [data-testid="stMarkdownContainer"],
        .stApp [data-testid="stWidgetLabel"] {
            color: #17301f;
        }
        .stApp [data-testid="stSidebar"] {
            background: #1b5e20;
        }
        .stApp [data-testid="stSidebar"],
        .stApp [data-testid="stSidebar"] p,
        .stApp [data-testid="stSidebar"] span,
        .stApp [data-testid="stSidebar"] label,
        .stApp [data-testid="stSidebar"] [data-testid="stMarkdownContainer"],
        .stApp [data-testid="stSidebar"] [data-testid="stWidgetLabel"] {
            color: #ffffff;
        }
        .hero {
            background: linear-gradient(115deg, #163d27 0%, #25613a 62%, #b47c3c 100%);
            color: #ffffff;
            padding: 2.5rem 3rem;
            border-radius: 4px 22px 22px 22px;
            margin: 0.5rem 0 1.6rem;
            box-shadow: 0 16px 35px rgba(22, 61, 39, 0.16);
            position: relative;
            overflow: hidden;
        }
        .hero::after {
            border: 1px solid rgba(255,255,255,0.18);
            border-radius: 50%;
            content: "";
            height: 280px;
            position: absolute;
            right: -80px;
            top: -150px;
            width: 280px;
        }
        .hero h1,
        .hero p {
            color: #ffffff !important;
        }
        .card { 
            padding: 1.25rem;
            border-radius: 14px; 
            background: #ffffff;
            border: 1px solid rgba(27, 94, 32, 0.12);
            box-shadow: 0 6px 18px rgba(27, 62, 32, 0.07);
            margin-bottom: 1.5rem;
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 12px 28px rgba(27, 62, 32, 0.13);
        }
        h1, h2, h3 { 
            color: #1B5E20; 
            font-weight: bold;
        }
        h1 { letter-spacing: -0.02em; }
        h2, h3 { margin-top: 0.4rem; }
        .section-kicker {
            color: #b47c3c;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
        }
        .stTabs [data-baseweb="tab"] {
            color: #17301f;
            font-size: 0.82rem;
            font-weight: 700;
        }
        .stTabs [data-baseweb="tab-list"] {
            background: #e7eee3;
            border-radius: 12px;
            gap: 0.2rem;
            padding: 0.3rem;
        }
        .stTabs [data-baseweb="tab"] > div {
            border-radius: 9px;
            padding: 0.5rem 0.8rem;
        }
        .stTabs [aria-selected="true"] {
            color: #1b5e20;
        }
        .chat-thread {
            position: relative;
            padding: 0.75rem 0;
            margin: 0.75rem 0 1.2rem;
            min-height: 8rem;
        }
        .chat-thread::before {
            background: #111811;
            content: "";
            left: 50%;
            opacity: 0.8;
            position: absolute;
            top: 0;
            bottom: 0;
            width: 2px;
        }
        .chat-row {
            display: flex;
            margin: 0.75rem 0;
            position: relative;
            width: 100%;
            z-index: 1;
        }
        .chat-row.user {
            justify-content: flex-end;
        }
        .chat-row.assistant {
            justify-content: flex-start;
        }
        .chat-bubble {
            border: 1px solid rgba(27, 94, 32, 0.16);
            border-radius: 16px;
            box-shadow: 0 5px 14px rgba(27, 62, 32, 0.08);
            max-width: 44%;
            padding: 0.8rem 1rem;
        }
        .chat-row.user .chat-bubble {
            background: #1b5e20;
            border-bottom-right-radius: 4px;
            color: #ffffff;
        }
        .chat-row.assistant .chat-bubble {
            background: #ffffff;
            border-bottom-left-radius: 4px;
            color: #17301f;
        }
        .chat-author {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.04em;
            margin-bottom: 0.28rem;
            text-transform: uppercase;
        }
        .chat-content {
            line-height: 1.55;
            white-space: normal;
        }
        .chat-time {
            font-size: 0.68rem;
            margin-top: 0.45rem;
            opacity: 0.7;
        }
        .chat-row.user .chat-author,
        .chat-row.user .chat-time,
        .chat-row.user .chat-content {
            color: #ffffff !important;
        }
        .chat-row.assistant .chat-author,
        .chat-row.assistant .chat-time,
        .chat-row.assistant .chat-content {
            color: #17301f !important;
        }
        [data-testid="stChatInput"] {
            border: 2px solid rgba(27, 94, 32, 0.28);
            border-radius: 14px;
            background: #ffffff;
        }
        [data-testid="stChatInput"] textarea,
        [data-testid="stChatInput"] input,
        [data-testid="stChatInput"] [contenteditable="true"] {
            background: #ffffff !important;
            color: #17301f !important;
            caret-color: #1b5e20 !important;
            -webkit-text-fill-color: #17301f !important;
        }
        [data-testid="stChatInput"] > div,
        [data-testid="stChatInput"] > div > div,
        [data-testid="stChatInput"] textarea:focus,
        [data-testid="stChatInput"] input:focus {
            background: #ffffff !important;
            color: #17301f !important;
        }
        [data-testid="stChatInput"] textarea::placeholder,
        [data-testid="stChatInput"] input::placeholder,
        [data-testid="stChatInput"] [contenteditable="true"]::before {
            color: #55705b !important;
            opacity: 1 !important;
        }
        [data-testid="stChatInput"] button {
            background: #1b5e20 !important;
            color: #ffffff !important;
        }
        .stButton>button,
        .stButton>button span {
            background: linear-gradient(135deg, #2e7d32 0%, #4f9b58 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.5rem 1rem;
            font-weight: bold;
        }
        .stButton>button:hover {
            background: linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%);
        }
        .sidebar .sidebar-content { 
            background-color: #4CAF50; 
            color: white; 
        }
        .metric {
            background: #f1f8e9;
            padding: 1rem;
            border-radius: 12px;
            text-align: center;
            border: 1px solid rgba(27, 94, 32, 0.12);
        }
        .result-box {
            border-radius: 14px;
            margin: 1rem 0;
            padding: 1.2rem 1.4rem;
        }
        .result-box.green { background: #e6f4e7; border-left: 5px solid #2e7d32; }
        .result-box.orange { background: #fff4df; border-left: 5px solid #c47f35; }
        .result-box.red { background: #fde8e7; border-left: 5px solid #b42318; }
        .result-label { font-size: 0.75rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; }
        .result-value { font-size: 1.8rem; font-weight: 700; margin: 0.15rem 0 0.35rem; }
        .health-result {
            border-radius: 14px;
            margin: 1rem 0;
            padding: 1.2rem 1.4rem;
        }
        .health-good { background: #e6f4e7; border-left: 5px solid #2e7d32; }
        .health-risk { background: #fde8e7; border-left: 5px solid #b42318; }
        [data-testid="stMetric"] {
            background: #ffffff;
            border: 1px solid rgba(27, 94, 32, 0.12);
            border-radius: 12px;
            padding: 0.75rem 1rem;
        }
        [data-testid="stVerticalBlock"] > [data-testid="stElementContainer"] {
            animation: rise-in 0.35s ease both;
        }
        @keyframes rise-in {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @media (max-width: 700px) {
            .hero {
                padding: 1.6rem 1.2rem;
            }
            .chat-thread::before {
                left: 0.25rem;
            }
            .chat-bubble {
                max-width: 88%;
            }
            .chat-row {
                padding-left: 1rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )
