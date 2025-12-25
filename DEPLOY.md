# 🚀 คู่มือการ Deploy Focus Shield AI Bot

คู่มือนี้จะแนะนำวิธีการ deploy แอป Streamlit ของคุณไปยังแพลตฟอร์มต่างๆ

---

## 📋 สิ่งที่ต้องเตรียมก่อน Deploy

### 1. ตรวจสอบไฟล์ที่จำเป็น
- ✅ `app.py` - ไฟล์หลักของแอป
- ✅ `requirements.txt` - รายการ dependencies
- ✅ `.gitignore` - ป้องกันการ commit ไฟล์สำคัญ

### 2. Environment Variables ที่ต้องตั้งค่า
คุณจะต้องตั้งค่า Environment Variables เหล่านี้ในแพลตฟอร์มที่ deploy:

```
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
```

---

## 🌐 วิธีที่ 1: Streamlit Cloud (แนะนำ - ง่ายที่สุด)

### ขั้นตอน:

1. **Push โค้ดขึ้น GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/your-repo.git
   git push -u origin main
   ```

2. **ไปที่ Streamlit Cloud**
   - เปิด https://share.streamlit.io/
   - คลิก "Sign in" และล็อกอินด้วย GitHub

3. **Deploy แอป**
   - คลิก "New app"
   - เลือก Repository และ Branch
   - ตั้งค่า:
     - **Main file path**: `app.py`
     - **App URL**: เลือกชื่อที่ต้องการ (เช่น `focus-shield-ai`)

4. **ตั้งค่า Secrets (Environment Variables)**
   - คลิก "Advanced settings" → "Secrets"
   - วางโค้ดนี้:
     ```toml
     GEMINI_API_KEY = "your_gemini_api_key_here"
     SUPABASE_URL = "your_supabase_url_here"
     SUPABASE_KEY = "your_supabase_key_here"
     ```
   - คลิก "Save"

5. **รอ Deploy เสร็จ** (ประมาณ 1-2 นาที)

✅ **ข้อดี**: ฟรี, ง่าย, auto-deploy เมื่อ push code ใหม่

---

## 🚂 วิธีที่ 2: Railway

### ขั้นตอน:

1. **Push โค้ดขึ้น GitHub** (เหมือนวิธีที่ 1)

2. **ไปที่ Railway**
   - เปิด https://railway.app/
   - คลิก "Login" และล็อกอินด้วย GitHub
   - คลิก "New Project" → "Deploy from GitHub repo"

3. **ตั้งค่า Deploy**
   - เลือก Repository ของคุณ
   - Railway จะ auto-detect Python project

4. **ตั้งค่า Environment Variables**
   - ไปที่ "Variables" tab
   - เพิ่ม:
     - `GEMINI_API_KEY`
     - `SUPABASE_URL`
     - `SUPABASE_KEY`

5. **ตั้งค่า Start Command**
   - ไปที่ "Settings" → "Deploy"
   - ตั้งค่า Start Command:
     ```
     streamlit run app.py --server.port $PORT
     ```

6. **Generate Domain**
   - ไปที่ "Settings" → "Generate Domain"
   - จะได้ URL สำหรับแอปของคุณ

✅ **ข้อดี**: ฟรี tier มีให้, รองรับ custom domain

---

## 🎯 วิธีที่ 3: Render

### ขั้นตอน:

1. **Push โค้ดขึ้น GitHub**

2. **ไปที่ Render**
   - เปิด https://render.com/
   - คลิก "Sign Up" และล็อกอินด้วย GitHub

3. **สร้าง Web Service**
   - คลิก "New" → "Web Service"
   - เชื่อมต่อ GitHub Repository

4. **ตั้งค่า Deploy**
   - **Name**: ชื่อแอปของคุณ
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`

5. **ตั้งค่า Environment Variables**
   - ไปที่ "Environment" tab
   - เพิ่ม:
     - `GEMINI_API_KEY`
     - `SUPABASE_URL`
     - `SUPABASE_KEY`

6. **Deploy**
   - คลิก "Create Web Service"
   - รอ deploy เสร็จ (ประมาณ 5-10 นาที)

✅ **ข้อดี**: ฟรี tier, auto-deploy

---

## ☁️ วิธีที่ 4: Heroku

### ขั้นตอน:

1. **สร้างไฟล์ `Procfile`**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **สร้างไฟล์ `runtime.txt`** (ถ้าต้องการ Python version เฉพาะ)
   ```
   python-3.11.0
   ```

3. **ติดตั้ง Heroku CLI และ Deploy**
   ```bash
   # Login
   heroku login
   
   # สร้างแอป
   heroku create your-app-name
   
   # ตั้งค่า Environment Variables
   heroku config:set GEMINI_API_KEY=your_key
   heroku config:set SUPABASE_URL=your_url
   heroku config:set SUPABASE_KEY=your_key
   
   # Deploy
   git push heroku main
   ```

⚠️ **หมายเหตุ**: Heroku ฟรี tier ถูกยกเลิกแล้ว ต้องใช้ paid plan

---

## 🔧 วิธีที่ 5: Deploy บน VPS (DigitalOcean, AWS EC2, etc.)

### ขั้นตอน:

1. **SSH เข้า VPS**
   ```bash
   ssh user@your-server-ip
   ```

2. **ติดตั้ง Python และ dependencies**
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip
   pip3 install -r requirements.txt
   ```

3. **สร้างไฟล์ `.env`**
   ```bash
   nano .env
   # ใส่ environment variables
   ```

4. **รันแอปด้วย Streamlit**
   ```bash
   streamlit run app.py --server.port 8501 --server.address 0.0.0.0
   ```

5. **ตั้งค่า Nginx (Optional - สำหรับ production)**
   - ติดตั้ง Nginx และตั้งค่า reverse proxy
   - ใช้ SSL certificate (Let's Encrypt)

---

## 📝 Checklist ก่อน Deploy

- [ ] ตรวจสอบว่า `requirements.txt` มี dependencies ครบ
- [ ] ตั้งค่า Environment Variables ทั้งหมด
- [ ] ทดสอบแอปใน local ก่อน (`streamlit run app.py`)
- [ ] Push code ขึ้น GitHub
- [ ] ตรวจสอบว่า `.env` ไม่ได้ถูก commit (มีใน `.gitignore`)

---

## 🐛 แก้ปัญหา (Troubleshooting)

### ปัญหา: แอปไม่สามารถเชื่อมต่อ API ได้
- **แก้**: ตรวจสอบว่า Environment Variables ตั้งค่าถูกต้อง

### ปัญหา: Import Error
- **แก้**: ตรวจสอบ `requirements.txt` ว่ามี package ที่ต้องการครบ

### ปัญหา: Port Error
- **แก้**: ใช้ `$PORT` environment variable ใน start command

### ปัญหา: Deploy ช้า
- **แก้**: ลองใช้ platform อื่น หรือตรวจสอบ build logs

---

## 💡 คำแนะนำเพิ่มเติม

1. **ใช้ Streamlit Cloud** ถ้าต้องการวิธีที่ง่ายที่สุด
2. **ตั้งค่า Custom Domain** สำหรับดูเป็นมืออาชีพ
3. **Monitor Usage** เพื่อไม่ให้เกิน quota ของ API
4. **Backup Environment Variables** เก็บไว้ในที่ปลอดภัย

---

## 📞 ต้องการความช่วยเหลือ?

ถ้ามีปัญหาหรือคำถาม สามารถ:
- ตรวจสอบ logs ในแพลตฟอร์มที่ deploy
- ดู documentation ของแพลตฟอร์มที่เลือก
- ทดสอบใน local ก่อน deploy

---

**Happy Deploying! 🚀**

