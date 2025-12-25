import os
import time
import google.generativeai as genai
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. โหลดค่าความลับจากไฟล์ .env
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# เช็คว่าเจอ Key ไหม
if not GEMINI_API_KEY or not SUPABASE_URL:
    print("❌ Error: ไม่พบ API Key กรุณาเช็คไฟล์ .env")
    exit()

# 2. ตั้งค่าระบบ
try:
    genai.configure(api_key=GEMINI_API_KEY)
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    print("✅ เชื่อมต่อระบบสำเร็จ")
except Exception as e:
    print(f"❌ ตั้งค่าไม่ผ่าน: {e}")

# 3. ค้นหาโมเดล Flash อัตโนมัติ
print("🔍 กำลังสแกนหาโมเดล Flash...")
final_model_name = ""

try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            if 'flash' in m.name.lower():
                final_model_name = m.name
                if '1.5' in m.name: break 

    if final_model_name:
        print(f"🎯 ใช้โมเดล: {final_model_name}")
        clean_name = final_model_name.replace("models/", "")
        model = genai.GenerativeModel(clean_name)
    else:
        print("⚠️ หา Flash ไม่เจอ ใช้ตัวแรกสุดแทน")
        model = genai.GenerativeModel('gemini-1.5-flash') # Default

except Exception as e:
    print(f"❌ Error หาโมเดล: {e}")

# 4. ฟังก์ชันแชท
def ask_focus(user_question, chat_history_text):
    print("🤖 น้องโฟกัสกำลังหาข้อมูล...")
    
    try:
        # แปลงคำถามเป็น Vector
        query_vec = genai.embed_content(
            model="models/text-embedding-004",
            content=user_question
        )['embedding']

        # ค้นหาใน Supabase
        results = supabase.rpc(
            "match_products",
            {
                "query_embedding": query_vec,
                "match_threshold": 0.35,
                "match_count": 5
            }
        ).execute()
        
        # รวบรวมข้อมูล
        context = ""
        found_items = []
        if results.data:
            for item in results.data:
                meta = item['metadata']
                model_name = meta.get('model', 'ไม่ระบุรุ่น')
                link = meta.get('link', '#')
                price = meta.get('price', '-')
                context += f"- {item['content']} (ราคา: {price} | Link: {link})\n"
                found_items.append(model_name)
        else:
            context = "ไม่พบข้อมูลสินค้าที่ตรงกับคำถาม"

        print(f"   (เจอ: {', '.join(found_items)})") 

        # Prompt
        final_prompt = f"""
        บทบาท: คุณคือ "น้องโฟกัส" แอดมินขายฟิล์ม Focus Shield
        
        [ข้อมูลสินค้าที่มีในคลัง]
        {context}
        
        [ประวัติการคุย]
        {chat_history_text}
        
        [คำถามลูกค้า]
        {user_question}
        
        --- คำสั่งการตอบ ---
        1. "ทักทายและถามรุ่น" ถ้ารู้แค่ว่าลูกค้าอยากได้ฟิล์ม แต่ไม่รู้รุ่นมือถือ
        2. "เสนอทางเลือก" ถ้ารู้รุ่นแล้ว แต่มีฟิล์มหลายแบบ (ใส/ด้าน/กันมอง) ให้ถามความชอบ
        3. "ปิดการขาย" ถ้ารู้ครบแล้ว ให้บอกราคาและส่งลิงก์
        4. ถ้าไม่มีข้อมูล ให้บอกตรงๆ ว่าของหมด
        5. ใช้ภาษาพูด น่ารัก เป็นกันเอง
        """

        response = model.generate_content(final_prompt)
        return response.text

    except Exception as e:
        return f"ระบบขัดข้อง: {e}"

# --- เริ่มรันโปรแกรม ---
if __name__ == "__main__":
    print("\n🎉 น้องโฟกัส (PC Version) พร้อมทำงาน! (พิมพ์ exit เพื่อจบ)")
    history_log = []

    while True:
        try:
            q = input("\n💬 ลูกค้า: ")
            if q.lower() == 'exit': break
            if q.strip() == "": continue
            
            hist_text = "\n".join([f"{h['role']}: {h['msg']}" for h in history_log[-3:]])
            ans = ask_focus(q, hist_text)
            
            print(f"\n⚡ น้องโฟกัส:\n{ans}")
            print("-" * 50)
            
            history_log.append({"role": "User", "msg": q})
            history_log.append({"role": "Focus", "msg": ans})
        except KeyboardInterrupt:
            print("\nปิดโปรแกรม...")
            break