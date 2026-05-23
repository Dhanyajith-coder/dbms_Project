# 🩸 Blood Bank Management System

A beautiful, modern platform connecting blood donors, hospitals, and blood banks in real-time.

> Save lives by donating blood. Streamline blood requests with advanced tracking.

![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-red?style=flat-square&logo=streamlit)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)
![Supabase](https://img.shields.io/badge/Supabase-PostgreSQL-green?style=flat-square&logo=supabase)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

## ✨ Features

### 👤 Donor Portal
- 🎯 Easy registration with blood type
- 📋 Browse all active blood requests  
- ✅ Accept requests and track donations
- 📊 View donation history
- 🔔 Real-time updates on matching requests

### 🏥 Hospital & Blood Bank Portal
- 📝 Create urgent blood requests
- ⚠️ Set urgency levels (Normal, High, Critical)
- 📈 Real-time progress tracking
- 👥 View all donor acceptances
- ✓ Close requests when quota met
- 📊 Dashboard with key metrics

### 🔧 Technical Features
- 🔐 Secure Supabase authentication
- 🚀 Real-time database synchronization
- 🎨 Modern, responsive dark theme UI
- 📱 Mobile-friendly design
- ☁️ Cloud-ready deployment
- ♿ Accessible interface

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Git
- Supabase project (free tier OK)

### Local Installation

1. **Clone repository**
   ```bash
   git clone https://github.com/yourusername/blood-bank-app.git
   cd blood-bank-app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate  # Windows
   # or
   source .venv/bin/activate  # macOS/Linux
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Supabase**
   - Go to [Supabase](https://supabase.com) and create a free project
   - Run `database/schema.sql` in Supabase SQL editor to create tables
   - Get your credentials from Settings → API

5. **Configure environment**
   ```bash
   # Create .env file
   echo SUPABASE_URL=your-url > .env
   echo SUPABASE_KEY=your-key >> .env
   echo SUPABASE_SERVICE_ROLE_KEY=your-service-key >> .env
   ```

6. **Run app**
   ```bash
   streamlit run app.py
   ```

   Open http://localhost:8501 in your browser!

## 🌐 Deploy Online (1-Click)

### Using Streamlit Cloud (Recommended)

1. Push code to GitHub
2. Go to [Streamlit Cloud](https://share.streamlit.io)
3. Click "New app"
4. Select your GitHub repo and `app.py`
5. Add secrets in app settings
6. Deploy!

**See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed steps.**

Your app will be live at: `https://share.streamlit.io/your-username/blood-bank-app`

## 📁 Project Structure

```
blood-bank-app/
├── app.py                          # Main Streamlit application (start here)
├── logic.py                        # Business logic & database functions
├── requirements.txt                # Python dependencies
├── .env                           # Environment variables (local only)
├── .streamlit/
│   └── config.toml               # Streamlit theme & settings
├── database/
│   ├── schema.sql                # Database schema (run in Supabase)
│   └── migration_cleanup.sql     # Cleanup script
├── DEPLOYMENT.md                 # Cloud deployment guide
└── README.md                     # This file
```

## 🔧 Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend** | Streamlit 1.40+ |
| **Backend** | Python 3.10+ |
| **Database** | Supabase (PostgreSQL) |
| **Auth** | Supabase Auth |
| **Hosting** | Streamlit Cloud |
| **UI/UX** | Custom CSS (Dark Theme) |

## 🎨 UI/UX Highlights

- **Dark Theme**: Reduces eye strain, modern aesthetic
- **Color Coding**: Red for urgency, green for success
- **Progress Bars**: Visual donation progress tracking
- **Responsive Design**: Works on desktop & mobile
- **Fast Loading**: Optimized database queries

## 📋 Usage

### As a Donor

1. Register with your name, phone, blood type, and address
2. View all active blood requests for your blood type
3. Click "💉 Donate" on any request you want to help with
4. Your donation is recorded in real-time!

### As a Hospital

1. Register your hospital/blood bank
2. Create a blood request (specify type, quantity, urgency)
3. View all donors who accepted your request
4. Track collection progress automatically
5. Request closes when quota is met

## 🔐 Security

- ✅ Environment variables for sensitive data (never committed)
- ✅ Supabase Row-Level Security (RLS) policies
- ✅ Service role key for secure server operations
- ✅ HTTPS encryption for all data in transit
- ✅ No user passwords stored (Supabase handles auth)

## 🐛 Troubleshooting

### Streamlit won't connect to Supabase
```
Error: "Could not connect to Supabase"
→ Check SUPABASE_URL and SUPABASE_KEY in .env
→ Verify Supabase project is active
→ Test connection: python -c "from supabase import create_client; print('OK')"
```

### Row-level security error
```
Error: "new row violates row-level security policy"
→ Add SUPABASE_SERVICE_ROLE_KEY to .env
→ Or disable RLS temporarily for testing
```

### Port 8501 already in use
```bash
streamlit run app.py --server.port 8502
```

### Clear Streamlit cache
```bash
streamlit cache clear
```

## 📊 Database Schema

### Donors Table
```sql
- id (Primary Key)
- donor_code (Unique code like DONOR-xxx)
- name
- phone
- address
- blood_type
- created_at
```

### Hospitals Table
```sql
- id (Primary Key)
- hospital_code
- name
- phone
- address
- role (Hospital or Blood Bank)
- created_at
```

### Blood Requests Table
```sql
- id (Primary Key)
- request_code
- hospital_name
- blood_type
- units_needed
- units_collected
- urgency (Normal/High/Critical)
- status (open/closed)
- description
- created_at
```

### Acceptances Table
```sql
- id (Primary Key)
- acceptance_code
- request_id (Foreign Key)
- donor_name
- donor_phone
- created_at
```

## 🤝 Contributing

Contributions welcome! Here's how:

1. Fork the repository
2. Create feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes and commit: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open Pull Request

## 📝 License

MIT License - feel free to use for personal or commercial projects.

## 🙌 Acknowledgments

- [Streamlit](https://streamlit.io) - Amazing framework
- [Supabase](https://supabase.com) - Open source Firebase alternative
- Blood donation organizations - Inspired by their mission

## 💬 Get Help

- 📖 [Streamlit Docs](https://docs.streamlit.io)
- 📚 [Supabase Docs](https://supabase.com/docs)
- 🐛 [Report Issues](https://github.com/yourusername/blood-bank-app/issues)

---

<div align="center">

### Made with ❤️ to save lives

**If this helps you, please consider starring the repo!** ⭐

</div>
