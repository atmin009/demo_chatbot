import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# 1. ตั้งค่าหน้าเว็บ
st.set_page_config(
    page_title="Focus Shield AI Assistant",
    page_icon="🛡️",
    layout="centered"
)

# 2. โหลด Key และเชื่อมต่อระบบ
@st.cache_resource
def init_connections():
    load_dotenv()
    
    GEMINI_KEY = os.getenv("GEMINI_API_KEY")
    SUPA_URL = os.getenv("SUPABASE_URL")
    SUPA_KEY = os.getenv("SUPABASE_KEY")
    
    if not GEMINI_KEY:
        st.error("❌ ไม่พบ API Key กรุณาตรวจสอบไฟล์ .env หรือ Secrets ใน Cloud")
        return None, None, None

    # Connect Gemini
    genai.configure(api_key=GEMINI_KEY)
    
    # Auto-detect โมเดล Flash ที่ใช้ได้
    model_name = 'gemini-1.5-flash'  # Default
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name.lower():
                    model_name = m.name.replace("models/", "")
                    if '1.5' in m.name: 
                        break
    except Exception as e:
        st.warning(f"⚠️ ไม่สามารถหาโมเดล Flash ได้ ใช้ default: {model_name}")
    
    model = genai.GenerativeModel(model_name)
    
    # Connect Supabase
    supabase = create_client(SUPA_URL, SUPA_KEY)
    
    return model, supabase, model_name

model, supabase, active_model_name = init_connections()

# 3. ฟังก์ชันสมอง AI
def get_focus_response(user_input, history_text):
    try:
        # Vector Search
        query_vec = genai.embed_content(
            model="models/text-embedding-004",
            content=user_input
        )['embedding']

        results = supabase.rpc(
            "match_products",
            {
                "query_embedding": query_vec,
                "match_threshold": 0.35,
                "match_count": 5
            }
        ).execute()

        # Context
        context = ""
        if results.data:
            for item in results.data:
                meta = item['metadata']
                price = meta.get('price', '-')
                link = meta.get('link', '#')
                context += f"- {item['content']} (ราคา: {price} | Link: {link})\n"
        else:
            context = "ไม่พบข้อมูลสินค้าที่ตรงกับคำถาม"

        # Prompt
        final_prompt = f"""
        คุณคือ "น้องโฟกัส" แอดมินขายฟิล์ม Focus Shield
        [ข้อมูลสินค้า]
        {context}
        [ประวัติการคุย]
        {history_text}
        [คำถามลูกค้า]
        {user_input}
        
        --- คำสั่ง ---
        1. ทักทาย/ถามรุ่น ถ้ายังไม่รู้
        2. เสนอทางเลือก (ใส/ด้าน/กันมอง) ถ้ารู้รุ่นแล้ว
        3. ปิดการขาย (ราคา+ลิงก์) เมื่อรู้ครบ
        4. ห้ามมั่วข้อมูล
        5. ตอบสั้นๆ น่ารัก เป็นกันเอง
        """
        
        response = model.generate_content(final_prompt)
        return response.text
    except Exception as e:
        return f"ระบบขัดข้อง: {e}"

# 4. UI
st.title("🛡️ น้องโฟกัส (AI Assistant)")
st.caption(f"Model: {active_model_name} | Powered by Supabase")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "สวัสดีครับ! น้องโฟกัสยินดีให้บริการ กำลังมองหาฟิล์มรุ่นไหนอยู่ครับ? 😊"}
    ]

for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant", avatar="🛡️").write(msg["content"])

if prompt := st.chat_input("พิมพ์ข้อความ..."):
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    history_str = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-4:]])

    with st.spinner("น้องโฟกัสกำลังพิมพ์..."):
        response_text = get_focus_response(prompt, history_str)

    st.chat_message("assistant", avatar="🛡️").write(response_text)
    st.session_state.messages.append({"role": "assistant", "content": response_text})