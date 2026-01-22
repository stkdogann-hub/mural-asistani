import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json

# --- AYARLAR ---
st.set_page_config(page_title="Mural Tablosu", layout="wide", page_icon="🕵️‍♂️")

st.title("🕵️‍♂️ Sıtkı'nın Mural Tablosu (Dedektif Modu)")
st.info("Bu mod, hataları gizlemez. Eğer tablo boş geliyorsa sebebi aşağıda kırmızı kutuda yazar.")

# --- SİSTEM HAZIRLIK ---
if 'data' not in st.session_state:
    st.session_state.data = []

# API Key Bağlantısı
try:
    api_key = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=api_key)
except Exception as e:
    st.error(f"🚨 API Key Hatası: {e}")
    st.stop()

# --- ANALİZ FONKSİYONU (HATA GİZLEMEZ!) ---
def analyze_image_debug(image):
    # Model: Gemini 1.5 Flash (En günceli)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    prompt = """
    Bu resmi analiz et. Mural projelerini tablo verisi olarak çıkar.
    Eğer resimde proje yoksa boş liste ver.
    
    ÇIKTI FORMATI (Saf JSON):
    [
      {
        "Proje": "Proje Adı",
        "Tarih": "YYYY-MM-DD",
        "Bütçe": "Para birimiyle",
        "Konum": "Şehir/Eyalet",
        "Link": "Varsa link",
        "Notlar": "Detay"
      }
    ]
    """
    
    # BURADA TRY-EXCEPT YOK! HATAYI GÖRECEĞİZ.
    response = model.generate_content([prompt, image])
    
    # AI'nın verdiği ham cevabı ekrana basalım (Debug için)
    with st.expander("🤖 AI'dan Gelen Ham Cevap (Tıkla Gör)", expanded=False):
        st.code(response.text)

    # JSON Temizliği
    text = response.text.replace('```json', '').replace('```', '').strip()
    return json.loads(text)

# --- ARAYÜZ ---
with st.container():
    uploaded_files = st.file_uploader("Resimleri Yükle", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    
    if uploaded_files and st.button("Analiz Et (Hataları Göster) 🚀"):
        
        for file in uploaded_files:
            st.write(f"📂 **{file.name}** işleniyor...")
            
            try:
                img = Image.open(file)
                results = analyze_image_debug(img)
                
                if results:
                    st.success(f"✅ {file.name}: {len(results)} proje bulundu!")
                    for res in results:
                        st.session_state.data.append(res)
                else:
                    st.warning(f"⚠️ {file.name}: AI bu resimde veri bulamadı (Boş liste döndü).")
                    
            except Exception as e:
                # İŞTE SORUNU BURADA GÖRECEĞİZ
                st.error(f"🚨 {file.name} HATASI: {e}")
                st.write("Olası sebepler: API Key yanlış, Model bölgenizde kapalı veya Resim formatı bozuk.")

# --- TABLO ALANI ---
st.divider()
st.subheader("📋 Proje Listesi")

if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
else:
    df = pd.DataFrame(columns=["Proje", "Tarih", "Bütçe", "Konum", "Link", "Notlar"])

# Tabloyu Çiz
st.data_editor(
    df,
    use_container_width=True,
    num_rows="dynamic",
    key="editor"
)
