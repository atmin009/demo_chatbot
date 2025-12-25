import os
import time
import google.generativeai as genai
from supabase import create_client, Client
from dotenv import load_dotenv

# 1. โหลดค่า Key
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

genai.configure(api_key=GEMINI_API_KEY)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 2. ฟังก์ชัน Embed
def get_gemini_embedding(text):
    return genai.embed_content(model="models/text-embedding-004", content=text)['embedding']

# 3. เริ่มกระบวนการอัปเดตสมอง
print("🚀 กำลังเริ่มอัปเดตสมอง AI (Build Brain)...")

# ดึงข้อมูลจาก Catalog
response = supabase.table("product_catalog").select(
    "price, product_link, devices(brand_name, model_name), product_types(main_category, sub_category, features)"
).execute()

products = response.data
print(f"📦 พบสินค้า {len(products)} รายการ")

# วนลูปสร้าง Vector
count = 0
for item in products:
    try:
        device = item.get('devices') or {}
        ptype = item.get('product_types') or {}
        
        brand = device.get('brand_name', '')
        model = device.get('model_name', '')
        # ... (จัด Format ข้อมูลเหมือนเดิม) ...
        text_content = f"สินค้า: {brand} {model} ประเภท: {ptype.get('main_category')} ราคา: {item.get('price')}"
        
        metadata = {
            "model": model,
            "price": item.get('price'),
            "link": item.get('product_link')
        }

        # สร้าง Vector
        vector = get_gemini_embedding(text_content)
        
        # บันทึก (ใช้ upsert หรือ insert ก็ได้)
        supabase.table("product_embeddings").insert({
            "content": text_content,
            "metadata": metadata,
            "embedding": vector
        }).execute()
        
        count += 1
        if count % 10 == 0: print(f"✅ อัปเดตแล้ว {count} รายการ...")
        time.sleep(0)

    except Exception as e:
        print(f"⚠️ Error: {e}")

print("🎉 อัปเดตสมองเสร็จสมบูรณ์!")