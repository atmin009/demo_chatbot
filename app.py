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
    
    # Auto-detect โมเดล Flash ที่ใช้ได้ (เหมือนใน main.py)
    # แต่เลือกเฉพาะ 1.5-flash เพื่อหลีกเลี่ยง gemini-3-flash ที่มี quota น้อย
    model_name = None
    try:
        # ลองหา 1.5-flash ก่อน (quota มากกว่า)
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name.lower() and '1.5' in m.name.lower():
                    model_name = m.name.replace("models/", "")
                    break
        
        # ถ้าไม่เจอ 1.5-flash ลองหา flash ตัวอื่น (แต่ไม่เอา 3-flash)
        if not model_name:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    if 'flash' in m.name.lower() and '3' not in m.name.lower():
                        model_name = m.name.replace("models/", "")
                        break
        
        # ถ้ายังไม่เจอ ลองใช้ gemini-pro หรือ gemini-1.5-pro
        if not model_name:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    if 'pro' in m.name.lower() and '1.5' in m.name.lower():
                        model_name = m.name.replace("models/", "")
                        break
            
    except Exception as e:
        # ถ้า list_models() ไม่ได้ ใช้ default
        model_name = 'gemini-1.5-flash'
        st.warning(f"⚠️ ไม่สามารถหาโมเดลได้ ใช้ default: {model_name}")
    
    # ถ้ายังไม่เจอเลย ใช้ default
    if not model_name:
        model_name = 'gemini-1.5-flash'
    
    # สร้างโมเดล (ถ้า error จะจัดการใน get_focus_response)
    try:
        model = genai.GenerativeModel(model_name)
    except Exception as e:
        # ถ้าโมเดลที่เลือกใช้ไม่ได้ ลองหาโมเดลอื่นที่ใช้ได้
        st.warning(f"⚠️ โมเดล {model_name} ใช้ไม่ได้ กำลังหาโมเดลอื่น...")
        model = None
        try:
            for m in genai.list_models():
                if 'generateContent' in m.supported_generation_methods:
                    try:
                        model = genai.GenerativeModel(m.name.replace("models/", ""))
                        model_name = m.name.replace("models/", "")
                        break
                    except:
                        continue
        except:
            pass
        
        # ถ้ายังไม่ได้ ให้ใช้ default อีกครั้ง
        if model is None:
            try:
                model = genai.GenerativeModel('gemini-1.5-flash')
                model_name = 'gemini-1.5-flash'
            except:
                # ถ้ายังไม่ได้เลย ให้ใช้ gemini-pro
                model = genai.GenerativeModel('gemini-pro')
                model_name = 'gemini-pro'
    
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
        error_msg = str(e)
        
        # จัดการ quota exceeded (429)
        if "429" in error_msg or "quota" in error_msg.lower() or "exceeded" in error_msg.lower():
            return """😅 ขอโทษนะคะ ตอนนี้ระบบมีผู้ใช้งานเยอะมาก ทำให้ quota หมดชั่วคราวค่ะ 
            
**วิธีแก้:**
- รอสักครู่แล้วลองใหม่ (ประมาณ 1-2 นาที)
- หรือลองใหม่ในวันพรุ่งนี้ (quota จะ reset ทุกวัน)

ถ้าต้องการใช้งานต่อเนื่อง แนะนำให้อัปเกรดเป็น paid plan ของ Google Gemini API ค่ะ

ขอบคุณที่เข้าใจนะคะ 🙏"""
        
        # จัดการ model not found (404)
        if "404" in error_msg or "not found" in error_msg.lower() or "not supported" in error_msg.lower():
            return """⚠️ ไม่พบโมเดลที่ต้องการใช้งาน

**สาเหตุ:** โมเดลที่เลือกอาจไม่พร้อมใช้งานใน API version นี้

**วิธีแก้:**
- ระบบจะพยายามหาโมเดลอื่นที่ใช้ได้อัตโนมัติ
- หรือลอง refresh หน้าเว็บใหม่

ถ้ายังมีปัญหา กรุณาติดต่อทีมสนับสนุนค่ะ"""
        
        # จัดการ error อื่นๆ
        return f"""⚠️ เกิดข้อผิดพลาดในระบบ: {error_msg}

กรุณาลองใหม่อีกครั้ง หรือติดต่อทีมสนับสนุนค่ะ"""

# 4. UI
st.title("🛡️ น้องโฟกัส (AI Assistant)")
st.caption(f"Model: {active_model_name} | Powered by Supabase")

if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "สวัสดีครับ! น้องโฟกัสยินดีให้บริการ กำลังมองหาฟิล์มรุ่นไหนอยู่ค่ะ? 😊"}
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