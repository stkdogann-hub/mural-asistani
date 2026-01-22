import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
import json

# --- AYARLAR ---
st.set_page_config(page_title="Mural Tablosu", layout="wide", page_icon="🎨")

st.title("🎨 Sıtkı'nın Mural Tablosu (Garantili Mod)")

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

# --- YAN MENÜ: MODEL SEÇİMİ (EN ÖNEMLİ KISIM) ---
st.sidebar.header("⚙️ Model Ayarı")
st.sidebar.info("Aşağıdaki listeden çalışan bir model seç.")

available_models = []
try:
    # Google'a soruyoruz: "Hangi modellerin var?"
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            # Model isminin başındaki 'models/' kısmını temizle
            name = m.name.replace('models/', '')
            available_models.append(name)
except Exception as e:
    st.sidebar.error(f"Model listesi alınamadı: {e}")

# Eğer liste geldiyse kutucuğa koy, gelmediyse elle yazılanı kullan
if available_models:
    # Vision (Resim gören) modelleri öne çıkarmaya çalış
    default_ix = 0
    if 'gemini-1.5-flash' in available_models:
        default_ix = available_models.index('gemini-1.5-flash')
    elif 'gemini-pro-vision' in available_models:
        default_ix = available_models.index('gemini-pro-vision')
        
    selected_model_name = st.sidebar.selectbox(
        "Kullanılacak Model:", 
        available_models, 
        index=default_ix
    )
else:
    st.sidebar.warning("Liste çekilemedi, varsayılan deneniyor.")
    selected_model_name = "gemini-1.5-flash"

st.sidebar.success(f"Seçilen: {selected_model_name}")


# --- ANALİZ FONKSİYONU ---
def analyze_image_final(image, model_name):
    # Seçilen modeli yükle
    model = genai.GenerativeModel(model_name)
    
    prompt = """
    Bu resmi analiz et. Mural projelerini Excel tablosu formatında çıkar.
    ÇIKTI (Sadece JSON):
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
    
    try:
        response = model.generate_content([prompt, image])
        text = response.text.replace('```json', '').replace('```', '').strip()
        return json.loads(text)
    except Exception as e:
        st.error(f"⚠️ Model ({model_name}) Hatası: {e}")
        st.info("İPUCU: Sol menüden başka bir model seçip tekrar dene!")
        return []

# --- ARAYÜZ ---
with st.container():
    uploaded_files = st.file_uploader("Resimleri Yükle", accept_multiple_files=True, type=['jpg', 'png', 'jpeg'])
    
    if uploaded_files and st.button("Tabloya Dönüştür 🚀"):
        
        my_bar = st.progress(0, text="Yapay zeka çalışıyor...")
        
        for i, file in enumerate(uploaded_files):
            try:
                img = Image.open(file)
                # Seçilen modeli fonksiyona gönderiyoruz
                results = analyze_image_final(img, selected_model_name)
                
                if results:
                    for res in results:
                        st.session_state.data.append(res)
                else:
                    st.warning(f"{file.name}: Veri bulunamadı.")
                    
            except Exception as e:
                st.error(f"Dosya Hatası: {e}")
            
            my_bar.progress((i + 1) / len(uploaded_files))
            
        my_bar.empty()
        st.success("İşlem Tamamlandı!")

# --- TABLO ALANI ---
st.divider()
st.subheader("📋 Proje Listesi (Excel Görünümü)")

if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)
else:
    df = pd.DataFrame(columns=["Proje", "Tarih", "Bütçe", "Konum", "Link", "Notlar"])

st.data_editor(
    df,
    column_config={
        "Link": st.column_config.LinkColumn("Link", display_text="🔗 Git"),
        "Tarih": st.column_config.DateColumn("Tarih", format="DD.MM.YYYY"),
    },
    use_container_width=True,
    num_rows="dynamic",
    key="final_table"
)
