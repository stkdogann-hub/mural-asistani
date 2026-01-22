{\rtf1\ansi\ansicpg1254\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import google.generativeai as genai\
from PIL import Image\
import pandas as pd\
import urllib.parse\
import json\
\
# --- AYARLAR ---\
st.set_page_config(page_title="Mural Tracker", layout="wide", page_icon="\uc0\u55356 \u57256 ")\
\
# API Key'i G\'fcvenli \uc0\u350 ekilde Al\u305 yoruz (Streamlit Secrets'tan)\
try:\
    api_key = st.secrets["GOOGLE_API_KEY"]\
    genai.configure(api_key=api_key)\
except:\
    st.error("API Key bulunamad\uc0\u305 ! L\'fctfen Streamlit ayarlar\u305 ndan ekleyin.")\
    st.stop()\
\
# --- FONKS\uc0\u304 YONLAR ---\
def create_calendar_link(title, date_str, details):\
    try:\
        base = "https://www.google.com/calendar/render?action=TEMPLATE"\
        dt = pd.to_datetime(date_str)\
        dates = f"\{dt.strftime('%Y%m%d')\}/\{dt.strftime('%Y%m%d')\}"\
        url = f"\{base\}&text=\{urllib.parse.quote(title)\}&dates=\{dates\}&details=\{urllib.parse.quote(details)\}"\
        return url\
    except:\
        return "#"\
\
def analyze_image_with_ai(image):\
    model = genai.GenerativeModel('gemini-1.5-flash')\
    prompt = """\
    Bu resmi bir mural sanat\'e7\uc0\u305 s\u305  i\'e7in analiz et. Resim bir ekran g\'f6r\'fcnt\'fcs\'fc veya el \'e7izimi notlar olabilir.\
    G\'d6REV: Resimdeki T\'dcM projeleri tespit et.\
    \'c7IKTI FORMATI (JSON Listesi):\
    [\
      \{\
        "project_name": "Proje Ad\uc0\u305 ",\
        "deadline": "YYYY-MM-DD" (Tarih yoksa null),\
        "price": "B\'fct\'e7e",\
        "state": "Konum",\
        "link": "Link veya 'Notlardan'",\
        "wall_desc": "G\'f6rsel tan\uc0\u305 m (\'d6rn: K\'f6pr\'fc alt\u305 )"\
      \}\
    ]\
    Sadece JSON ver.\
    """\
    try:\
        response = model.generate_content([prompt, image])\
        text = response.text.replace('```json', '').replace('```', '').strip()\
        return json.loads(text)\
    except:\
        return []\
\
# --- ARAY\'dcZ ---\
st.title("\uc0\u55356 \u57256  S\u305 tk\u305 'n\u305 n Mural Asistan\u305 ")\
st.markdown("---")\
\
with st.expander("\uc0\u10133  Yeni Proje / Screenshot Y\'fckle", expanded=True):\
    uploaded_files = st.file_uploader("Resimleri Se\'e7", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])\
    \
    if uploaded_files and st.button("Analiz Et \uc0\u55357 \u56960 "):\
        if 'projects' not in st.session_state: st.session_state.projects = []\
        \
        for file in uploaded_files:\
            img = Image.open(file)\
            results = analyze_image_with_ai(img)\
            for res in results:\
                res['image_data'] = file # Resmi sakla\
                st.session_state.projects.append(res)\
        st.success("Listeye eklendi!")\
\
if 'projects' in st.session_state and st.session_state.projects:\
    df = pd.DataFrame(st.session_state.projects)\
    # Tarihe g\'f6re s\uc0\u305 ralama (Hata \'f6nleyici)\
    if 'deadline' in df.columns:\
        df['deadline'] = pd.to_datetime(df['deadline'], errors='coerce')\
        df = df.sort_values(by='deadline')\
\
    st.subheader(f"\uc0\u55357 \u56523  Takip Listesi (\{len(df)\})")\
    \
    for index, row in df.iterrows():\
        with st.container():\
            c1, c2, c3 = st.columns([1, 3, 1])\
            with c1:\
                if 'image_data' in row: st.image(row['image_data'], use_container_width=True)\
            with c2:\
                d_str = row['deadline'].strftime('%Y-%m-%d') if pd.notnull(row['deadline']) else "Tarih Yok"\
                st.markdown(f"### \{row.get('project_name', 'Proje')\}")\
                st.caption(f"\uc0\u55357 \u56525  \{row.get('state', '-')\} | \u55357 \u56496  \{row.get('price', '-')\}")\
                if pd.notnull(row['deadline']): st.markdown(f"\uc0\u55357 \u56787 \u65039  **:red[\{d_str\}]**")\
            with c3:\
                cal_link = create_calendar_link(f"DEADLINE: \{row.get('project_name')\}", row.get('deadline'), f"Link: \{row.get('link')\}")\
                st.link_button("\uc0\u55357 \u56517  Takvime Ekle", cal_link)\
                if row.get('link') and row.get('link') != 'Notlardan':\
                    st.link_button("\uc0\u55357 \u56599  Link", row.get('link'))\
            st.markdown("---")}