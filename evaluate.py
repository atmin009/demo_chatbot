import os
import time
import google.generativeai as genai
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. โหลด Key
load_dotenv()
GEMINI_KEY = os.getenv("GEMINI_API_KEY")
SUPA_URL = os.getenv("SUPABASE_URL")
SUPA_KEY = os.getenv("SUPABASE_KEY")

genai.configure(api_key=GEMINI_KEY)
supabase: Client = create_client(SUPA_URL, SUPA_KEY)

# เลือกโมเดล (Flash)
model = genai.GenerativeModel('gemini-1.5-flash')

# --- 2. ชุดข้อสอบ (แก้โจทย์ตรงนี้ได้ตามใจชอบ) ---
test_cases = [
    {
        "question": "สวัสดีครับ", 
        "expected_concept": "ทักทาย / ถามรุ่นมือถือ"
    },
    {
        "question": "มีฟิล์ม iPhone 15 Pro Max ไหม", 
        "expected_concept": "มีของ / แนะนำสินค้า / ขอประเภท"
    },
    {
        "question": "ขอแบบกันมอง iPhone 14", 
        "expected_concept": "Focus Privacy / กันมอง / iPhone 14"
    },
    {
        "question": "Samsung S24 Ultra ราคาเท่าไหร่", 
        "expected_concept": "ราคา / บาท / S24 Ultra"
    },
    {
        "question": "มีฟิล์มรุ่น Nokia 3310 ไหม", 
        "expected_concept": "ไม่มีของ / ขออภัย"
    }
]

# --- 3. ฟังก์ชันให้น้องโฟกัสตอบ (จำลองการทำงาน) ---
def get_bot_response(user_q):
    try:
        # Search
        vec = genai.embed_content(model="models/text-embedding-004", content=user_q)['embedding']
        res = supabase.rpc("match_products", {"query_embedding": vec, "match_threshold": 0.35, "match_count": 3}).execute()
        
        context = ""
        if res.data:
            for item in res.data:
                meta = item['metadata']
                context += f"- {item['content']} (ราคา: {meta.get('price')} Link: {meta.get('link')})\n"
        else:
            context = "ไม่พบข้อมูลสินค้า"

        # Prompt
        prompt = f"""
        คุณคือแอดมินขายฟิล์ม Focus Shield
        [ข้อมูลอ้างอิง] {context}
        [คำถาม] {user_q}
        ให้ตอบคำถามลูกค้า ถ้ามีของให้บอกราคาและลิงก์ ถ้าไม่มีให้บอกตรงๆ
        """
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Error"

# --- 4. ฟังก์ชันครูตรวจข้อสอบ (Judge) ---
def evaluate_answer(question, answer, expected):
    judge_prompt = f"""
    บทบาท: คุณคือครูตรวจข้อสอบ
    
    โจทย์: "{question}"
    สิ่งที่คาดหวัง (Key Concept): "{expected}"
    คำตอบของ AI: "{answer}"
    
    ภารกิจ:
    คำตอบของ AI "สื่อความหมายถูกต้อง" ตามสิ่งที่คาดหวังหรือไม่?
    (ไม่จำเป็นต้องคำพูดเป๊ะๆ ขอแค่ใจความได้)
    
    - ถ้าถูกต้อง/ตรงประเด็น: ตอบ YES
    - ถ้าผิด/มั่ว/ไม่ตรงคำถาม: ตอบ NO
    
    ตอบแค่คำว่า YES หรือ NO เท่านั้น
    """
    try:
        res = model.generate_content(judge_prompt)
        return "YES" in res.text.strip().upper()
    except:
        return False

# --- 5. เริ่มสอบ ---
print(f"📝 เริ่มการสอบวัดผล (จำนวน {len(test_cases)} ข้อ)...\n")
score = 0

for i, case in enumerate(test_cases):
    q = case["question"]
    expect = case["expected_concept"]
    
    print(f"ข้อที่ {i+1}: {q}")
    
    # ให้น้องตอบ
    bot_ans = get_bot_response(q)
    # ให้ครูตรวจ
    is_correct = evaluate_answer(q, bot_ans, expect)
    
    if is_correct:
        score += 1
        print(f"✅ ผ่าน! (บอทตอบ: {bot_ans[:50]}...)")
    else:
        print(f"❌ ไม่ผ่าน")
        print(f"   - คาดหวัง: {expect}")
        print(f"   - บอทตอบ: {bot_ans}")
    
    print("-" * 30)
    time.sleep(1) # พักนิดนึง

# สรุปผล
accuracy = (score / len(test_cases)) * 100
print(f"\n🎯 ผลการสอบ: ได้คะแนน {score}/{len(test_cases)}")
print(f"📊 ความแม่นยำ (Accuracy): {accuracy:.2f}%")