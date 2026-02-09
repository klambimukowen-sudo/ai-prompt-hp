import streamlit as st
import google.generativeai as genai
from PIL import Image
import pandas as pd
from datetime import datetime
import io

# --- KONFIGURASI API ---
MY_API_KEY = "AIzaSyA3nx27boexTQQ-dNRywhdxI4RGA8bQMXw"
genai.configure(api_key=MY_API_KEY)

st.set_page_config(page_title="AI Prompt Master Pro", layout="wide", page_icon="📸")

# --- INITIALIZE SESSION STATE ---
if 'history' not in st.session_state:
    st.session_state.history = []

# --- AUTO DETECT MODEL ---
@st.cache_resource
def get_working_model():
    try:
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        priorities = ['models/gemini-1.5-flash', 'models/gemini-1.5-pro', 'models/gemini-pro-vision']
        for p in priorities:
            if p in available_models: return p
        return available_models[0]
    except:
        return "models/gemini-1.5-flash"

model_name = get_working_model()
model = genai.GenerativeModel(model_name)

# --- UI APP ---
st.title("📸 AI Prompt Master Pro")
st.markdown("Ubah visual menjadi prompt, terjemahkan, dan simpan riwayat Anda.")

tab1, tab2 = st.tabs(["📤 Generator", "📜 Riwayat & Export"])

with tab1:
    col_input, col_output = st.columns([1, 1])
    
    with col_input:
        uploaded_file = st.file_uploader("Upload JPG/PNG", type=['jpg', 'jpeg', 'png'])
        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, use_container_width=True, caption="Original Image")
            
    with col_output:
        if uploaded_file:
            if st.button("🚀 Jalankan AI", use_container_width=True):
                with st.spinner("Menganalisis..."):
                    try:
                        instruction = "Create a detailed English prompt for AI Art (Midjourney/Stable Diffusion) and its Indonesian description."
                        response = model.generate_content([instruction, img])
                        
                        # Simpan data
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.history.append({
                            "Tanggal": now,
                            "Model": model_name,
                            "Hasil Prompt": response.text
                        })
                        
                        st.success("Berhasil!")
                        st.markdown("### 📝 Hasil:")
                        st.info(response.text)
                    except Exception as e:
                        st.error(f"Terjadi kesalahan: {e}")

with tab2:
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        
        # Tombol Download CSV
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Semua Riwayat (CSV)",
            data=csv,
            file_name=f"history_prompt_{datetime.now().strftime('%Y%m%d')}.csv",
            mime='text/csv',
        )
        
        st.divider()
        
        # Tampilan List
        for index, row in df.iloc[::-1].iterrows():
            with st.expander(f"Prompt - {row['Tanggal']}"):
                st.write(row['Hasil Prompt'])
    else:
        st.info("Belum ada riwayat. Hasil akan muncul di sini setelah Anda melakukan scan.")

st.sidebar.caption(f"Engine: {model_name}")