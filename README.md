# 🛡️ Focus Shield AI Bot

AI Assistant สำหรับช่วยเลือกฟิล์ม Focus Shield ที่เหมาะกับคุณ โดยใช้ Google Gemini AI และ Supabase Vector Search

## ✨ Features

- 🤖 AI Chatbot ที่เป็นกันเองและน่ารัก
- 🔍 Vector Search สำหรับค้นหาฟิล์มที่เหมาะสม
- 💬 UI ที่สวยงามและใช้งานง่าย
- 🎯 ตอบคำถามเกี่ยวกับฟิล์ม Focus Shield แบบ real-time

## 🚀 Quick Start

### 1. ติดตั้ง Dependencies

```bash
pip install -r requirements.txt
```

### 2. ตั้งค่า Environment Variables

สร้างไฟล์ `.env` ในโฟลเดอร์ root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
SUPABASE_URL=your_supabase_url_here
SUPABASE_KEY=your_supabase_key_here
```

### 3. รันแอป

```bash
streamlit run app.py
```

แอปจะเปิดที่ `http://localhost:8501`

## 📁 โครงสร้างโปรเจกต์

```
focus-ai-bot/
├── app.py              # Streamlit web app (สำหรับ deploy)
├── main.py             # CLI version (สำหรับทดสอบ)
├── build_brain.py      # สคริปต์สำหรับสร้าง vector database
├── evaluate.py         # สคริปต์สำหรับทดสอบ
├── requirements.txt    # Python dependencies
├── .gitignore         # Git ignore rules
├── DEPLOY.md          # คู่มือการ deploy
└── README.md          # ไฟล์นี้
```

## 🌐 Deploy

ดูคู่มือการ deploy แบบละเอียดใน [DEPLOY.md](./DEPLOY.md)

### วิธีที่แนะนำ: Streamlit Cloud

1. Push code ขึ้น GitHub
2. ไปที่ https://share.streamlit.io/
3. เชื่อมต่อ GitHub repository
4. ตั้งค่า Secrets (Environment Variables)
5. Deploy!

## 🔧 Development

### Local Development

```bash
# รัน Streamlit app
streamlit run app.py

# รัน CLI version
python main.py
```

### Update Vector Database

```bash
python build_brain.py
```

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GEMINI_API_KEY` | Google Gemini API Key | ✅ |
| `SUPABASE_URL` | Supabase Project URL | ✅ |
| `SUPABASE_KEY` | Supabase API Key | ✅ |

## 🛠️ Tech Stack

- **Streamlit** - Web framework
- **Google Gemini AI** - LLM สำหรับตอบคำถาม
- **Supabase** - Vector database สำหรับค้นหาสินค้า
- **Python 3.11+** - Programming language

## 📄 License

MIT License

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

Made with ❤️ for Focus Shield

