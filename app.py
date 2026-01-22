import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json

# --- BASİT AYARLAR ---
st.set_page_config(page_title="Mural Asistanı", layout="wide")
st.title("🎨 Mural Proje Listesi")

# --- 1. SİSTEM KONTROLÜ ---
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except:
    st.error("🚨 HATA: API Anahtarı bulunamadı! Secrets kısmını kontrol et.")
    st.stop()

# --- 2. ÇALIŞAN MODELİ BUL ---
def get_best_model():
    """Senin hesabında açık olan ilk modeli bulur ve onu kullanır"""
    try:
        # Google'dan senin için açık olan modelleri iste
        my_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # Öncelik sırası (Hızlı -> Güçlü -> Eski)
        preferred = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro-vision']
        
        for p in preferred:
            if p in my_models:
                return genai.GenerativeModel(p)
        
        # Listede bulamazsa varsayılanı dene
        return genai.GenerativeModel('gemini-1.5-flash')
    except:
        # Liste alamazsa kör atışı yap
        return genai.GenerativeModel('gemini-1.5-flash')

# --- 3. ANALİZ ---
def analyze_simple(image):
    model = get_best_model()
    
    prompt = """
    Bu resimdeki iş fırsatlarını veya mural projelerini listele.
    Çıktı formatı SAF JSON olsun:
    [{"Proje": "İsim", "Tarih": "YYYY-MM-DD", "Butce": "Miktar", "Konum": "Yer", "Link": "URL"}]
    """
    
    try:
        response = model.generate_content([prompt, image])
        # JSON temizliği
        clean_json = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(clean_json)
    except Exception as e:
        st.error(f"Okuma Hatası: {e}")
        return []

# --- 4. ARAYÜZ ---
uploaded_files = st.file_uploader("Resim Yükle", accept_multiple_files=True)

if uploaded_files and st.button("Listele 🚀"):
    st.write("⏳ Resimler taranıyor...")
    
    all_data = []
    for file in uploaded_files:
        img = Image.open(file)
        results = analyze_simple(img)
        if results:
            all_data.extend(results)

    # --- SONUÇLARI GÖSTER (TABLO YOK, DÜZ LİSTE VAR) ---
    if all_data:
        st.success("✅ İşlem Başarılı!")
        
        # Veriyi DataFrame yap
        df = pd.DataFrame(all_data)
        
        # Sade Tablo (Hata vermez)
        st.table(df)
        
        # İndirme Butonu
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Excel İndir", csv, "projeler.csv", "text/csv")
        
    else:
        st.warning("⚠️ Resimlerden veri çıkarılamadı veya model erişimi yok.")
