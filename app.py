import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import urllib.parse
import json
import datetime

# --- AYARLAR ---
st.set_page_config(page_title="Mural Asistanı", layout="wide", page_icon="🎨")

# API Key Kontrolü
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error("API Key bulunamadı! Lütfen Streamlit ayarlarından 'Secrets' kısmına ekleyin.")
    st.stop()

# --- FONKSİYONLAR ---

def create_calendar_link(title, date_str, details):
    """Google Takvim linki oluşturur"""
    try:
        base = "https://www.google.com/calendar/render?action=TEMPLATE"
        # Tarihi datetime objesine çevir
        dt = pd.to_datetime(date_str)
        # Format: YYYYMMDD (Tüm gün etkinliği için)
        dates = f"{dt.strftime('%Y%m%d')}/{dt.strftime('%Y%m%d')}"
        
        # Linki oluştur
        url = f"{base}&text={urllib.parse.quote(title)}&dates={dates}&details={urllib.parse.quote(details)}"
        return url
    except:
        return "#"

def analyze_image_with_ai(image):
    """Resmi Gemini 1.5 Pro ile analiz eder"""
    # MODELİ BURADA GÜNCELLEDİK (Flash yerine Pro kullanıyoruz)
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    prompt = """
    Bu resmi bir mural sanatçısı için analiz et. Resim bir ekran görüntüsü, Instagram postu veya el çizimi notlar olabilir.
    
    GÖREV: Resimdeki TÜM projeleri ve iş fırsatlarını tespit et.
    Eğer resimde birden fazla proje varsa (örneğin defter notlarında 3 farklı başlık varsa), her birini ayrı ayrı listele.
    
    ÇIKTI FORMATI (Sadece saf JSON listesi ver, markdown kullanma):
    [
      {
        "project_name": "Proje Adı (Kısa ve net)",
        "deadline": "YYYY-MM-DD" (Eğer yıl yoksa 2026 kabul et. Tarih yoksa null yap),
        "price": "Bütçe/Ücret (Bulamazsan 'Belirtilmemiş' yaz)",
        "state": "Konum (Eyalet kısaltması veya Şehir)",
        "link": "Başvuru linki (Yoksa 'Resimde')",
        "wall_desc": "Duvarın görsel tanımı (Örn: Köprü altı, Bina cephesi)"
      }
    ]
    """
    
    try:
