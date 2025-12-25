import streamlit as st
import google.generativeai as genai
from supabase import create_client, Client
from dotenv import load_dotenv
import os

# 1. ตั้งค่าหน้าเว็บ (Web Config)
st.set_page_config(
    page_title="Focus Shield AI Assistant",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS สำหรับ UI ที่สวยงามและสะอาด
st.markdown("""
    <style>
        /* ปรับแต่งหน้าจอให้ดูสะอาดและโปร */
        .main {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
        
        /* ปรับแต่งหัวข้อ */
        h1 {
            color: #1f77b4;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        /* ปรับแต่งข้อความ caption */
        .stCaption {
            color: #666;
            font-size: 0.9rem;
            margin-bottom: 2rem;
        }
        
        /* ปรับแต่งกล่องข้อความของ User */
        .stChatMessage[data-testid="user"] {
            background-color: #f0f2f6;
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        }
        
        /* ปรับแต่งกล่องข้อความของ Assistant */
        .stChatMessage[data-testid="assistant"] {
            background-color: #ffffff;
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 1rem;
            border-left: 4px solid #1f77b4;
        }
        
        /* ปรับแต่งข้อความในแชท */
        .stChatMessage .stMarkdown {
            line-height: 1.6;
            font-size: 1rem;
        }
        
        /* ปรับแต่งช่อง input */
        .stChatInputContainer > div {
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        
        .stChatInputContainer input {
            font-size: 1rem;
            padding: 0.75rem;
        }
        
        /* ปรับแต่ง spinner */
        .stSpinner > div {
            border-color: #1f77b4;
        }
        
        /* เพิ่มพื้นที่ด้านล่างเพื่อไม่ให้ข้อความถูกบัง */
        .chat-container {
            padding-bottom: 100px;
        }
        
        /* ปรับแต่ง avatar */
        .stChatMessageAvatar {
            font-size: 1.5rem;
        }
        
        /* ปรับแต่ง spacing ระหว่างข้อความ */
        .element-container {
            margin-bottom: 1rem;
        }
        
        /* ทำให้ข้อความอ่านง่ายขึ้น */
        .stMarkdown p {
            margin-bottom: 0.5rem;
        }
        
        /* ปรับแต่ง scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f1f1;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #888;
            border-radius: 4px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #555;
        }
    </style>
""", unsafe_allow_html=True)

# 2. โหลด Key และเชื่อมต่อระบบ (ใช้ Cache เพื่อไม่ให้ต่อใหม่ทุกครั้งที่คุย)
@st.cache_resource
def init_connections():
    # รองรับทั้ง local (.env) และ Streamlit Cloud (secrets)
    try:
        # ลองใช้ Streamlit secrets ก่อน (สำหรับ production)
        GEMINI_KEY = st.secrets["GEMINI_API_KEY"]
        SUPA_URL = st.secrets["SUPABASE_URL"]
        SUPA_KEY = st.secrets["SUPABASE_KEY"]
    except (KeyError, FileNotFoundError):
        # ถ้าไม่มี secrets ให้ใช้ .env (สำหรับ local)
        load_dotenv()
        GEMINI_KEY = os.getenv("GEMINI_API_KEY")
        SUPA_URL = os.getenv("SUPABASE_URL")
        SUPA_KEY = os.getenv("SUPABASE_KEY")
    
    if not GEMINI_KEY:
        st.error("❌ ไม่พบ API Key กรุณาตรวจสอบไฟล์ .env หรือ Streamlit Secrets")
        return None, None, None

    # Connect Gemini
    genai.configure(api_key=GEMINI_KEY)
    
    # Auto-Select Model (Logic เดิมของคุณ)
    model_name = 'gemini-1.5-flash' # Default
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if 'flash' in m.name.lower():
                    model_name = m.name
                    if '1.5' in m.name: break
    except:
        pass
    
    clean_model_name = model_name.replace("models/", "")
    model = genai.GenerativeModel(clean_model_name)
    
    # Connect Supabase
    supabase = create_client(SUPA_URL, SUPA_KEY)
    
    return model, supabase, clean_model_name

# เรียกใช้ฟังก์ชันเชื่อมต่อ
model, supabase, active_model_name = init_connections()

# 3. ฟังก์ชันสมอง AI (Logic เดิม)
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

        # Prepare Context
        context = ""
        if results.data:
            for item in results.data:
                meta = item['metadata']
                m_name = meta.get('model', '-')
                price = meta.get('price', '-')
                link = meta.get('link', '#')
                context += f"- {item['content']} (ราคา: {price} | Link: {link})\n"
        else:
            context = "ไม่พบข้อมูลสินค้าที่ตรงกับคำถาม"

        # Prompt - ปรับให้เป็นกันเองมากขึ้น
        final_prompt = f"""
        คุณคือ "น้องโฟกัส" แอดมินขายฟิล์ม Focus Shield ที่เป็นกันเองและน่ารัก
        
        [ข้อมูลสินค้าที่มีในคลัง]
        {context}
        
        [ประวัติการคุย]
        {history_text}
        
        [คำถามลูกค้า]
        {user_input}
        
        --- วิธีตอบ ---
        1. ใช้ภาษาพูดที่สบายๆ เป็นกันเอง เหมือนคุยกับเพื่อน (ใช้คำว่า "ครับ/ค่ะ" แต่อย่าเยอะเกินไป)
        2. ถ้ายังไม่รู้รุ่นมือถือ ให้ถามแบบน่ารัก เช่น "ใช้มือถือรุ่นไหนอยู่คะ?" หรือ "บอกรุ่นมือถือหน่อยได้ไหมครับ?"
        3. ถ้ารู้รุ่นแล้ว แต่มีฟิล์มหลายแบบ ให้ถามความชอบแบบเป็นกันเอง เช่น "อยากได้แบบใส ด้าน หรือกันมองคะ?" หรือ "ชอบแบบไหนมากกว่าครับ?"
        4. เมื่อรู้ครบแล้ว ให้บอกราคาและส่งลิงก์แบบเป็นกันเอง เช่น "ราคาอยู่ที่ XXX บาทเลยค่ะ ลิงก์สั่งซื้อ: [ลิงก์]"
        5. ถ้าไม่มีข้อมูล ให้บอกตรงๆ แต่อย่าให้ดูเย็นชา เช่น "ขอโทษนะคะ ตอนนี้ของรุ่นนี้อาจจะหมดชั่วคราว ลองดูรุ่นอื่นได้ไหมคะ?"
        6. ใช้ emoji นิดหน่อยให้ดูน่ารัก (แต่ไม่เยอะเกินไป)
        7. ตอบสั้นๆ กระชับ อ่านง่าย ไม่ยาวจนเกินไป
        """
        
        response = model.generate_content(final_prompt)
        return response.text
    except Exception as e:
        return f"ระบบขัดข้อง: {e}"

# 4. ส่วนแสดงผลหน้าจอ (UI) =============================================

# Container สำหรับจัดวางให้ดูสะอาด
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # หัวข้อ - ปรับให้ดูโปรและสะอาดขึ้น
    st.markdown("""
        <div style='text-align: center; margin-bottom: 1rem;'>
            <h1 style='color: #1f77b4; font-weight: 700; margin-bottom: 0.5rem;'>🛡️ น้องโฟกัส</h1>
        </div>
        <div style='text-align: center; color: #666; font-size: 0.9rem; margin-bottom: 2rem; line-height: 1.6;'>
            AI Assistant สำหรับช่วยเลือกฟิล์ม Focus Shield ที่เหมาะกับคุณ<br>
            <small style='color: #999;'>Powered by {}</small>
        </div>
    """.format(active_model_name), unsafe_allow_html=True)

    # สร้างตัวแปรเก็บประวัติการคุย (Session State)
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant", 
                "content": "สวัสดีค่ะ! 👋 น้องโฟกัสยินดีช่วยเลือกฟิล์มให้เลยนะคะ ใช้มือถือรุ่นไหนอยู่คะ? หรือมีคำถามอะไรเกี่ยวกับฟิล์ม Focus Shield บ้างไหมคะ? 😊"
            }
        ]

    # Container สำหรับแชท
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    # วนลูปแสดงข้อความเก่าทั้งหมดในหน้าจอ
    for msg in st.session_state.messages:
        # แยกฝั่งซ้ายขวา (User/Assistant)
        if msg["role"] == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg["content"])
        else:
            with st.chat_message("assistant", avatar="🛡️"):
                st.markdown(msg["content"])
    
    st.markdown('</div>', unsafe_allow_html=True)

# กล่องรับข้อความ (Chat Input) - วางไว้ด้านล่างสุด
if prompt := st.chat_input("พิมพ์ข้อความที่นี่... (เช่น 'ต้องการฟิล์มสำหรับ iPhone 15')"):
    # 1. แสดงข้อความลูกค้าทันที
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. เตรียมประวัติส่งให้ AI
    history_str = "\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[-4:]])

    # 3. AI คิดและตอบ (แสดง Loading spinner)
    with st.chat_message("assistant", avatar="🛡️"):
        with st.spinner("กำลังคิดอยู่... 💭"):
            response_text = get_focus_response(prompt, history_str)
        st.markdown(response_text)
    
    st.session_state.messages.append({"role": "assistant", "content": response_text})
    
    # Scroll to bottom
    st.rerun()