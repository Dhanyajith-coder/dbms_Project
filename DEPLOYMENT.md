# 🚀 Deployment Guide

## Deploy to Streamlit Cloud (Recommended)

### Prerequisites
- GitHub account
- Streamlit Cloud account (free)
- Supabase project with credentials

### Step 1: Prepare Your GitHub Repository

1. Initialize git if not already done:
   ```bash
   git init
   git add .
   git commit -m "Initial blood bank app"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/blood-bank-app.git
   git push -u origin main
   ```

2. Make sure `.env` is in `.gitignore` (secrets not committed)

### Step 2: Deploy on Streamlit Cloud

1. Go to [Streamlit Cloud Dashboard](https://share.streamlit.io/)
2. Click **"New app"**
3. Select:
   - Repository: `YOUR-USERNAME/blood-bank-app`
   - Branch: `main`
   - File path: `app.py`
4. Click **"Deploy"**

Streamlit will automatically install requirements and start your app!

### Step 3: Add Secrets

1. In Streamlit Cloud, go to your app menu (⋮)
2. Click **"Settings"**
3. Go to **"Secrets"** tab
4. Add your credentials:
   ```toml
   SUPABASE_URL = "https://your-project.supabase.co"
   SUPABASE_KEY = "your-public-anon-key"
   SUPABASE_SERVICE_ROLE_KEY = "your-service-role-key"
   ```
5. Click **"Save"**

### Step 4: App URL

Your app will be live at:
```
https://share.streamlit.io/YOUR-USERNAME/blood-bank-app
```

You can customize the URL in app settings!

## Environment Variables for Streamlit Cloud

Streamlit Cloud automatically uses secrets from the "Secrets" tab as environment variables. They appear in your app as if they were in a `.env` file.

## Continuous Deployment

Every push to `main` branch automatically redeploys your app!

```bash
# Make changes locally
git add .
git commit -m "Feature: improve UI"
git push origin main
# App updates automatically in ~1 minute
```

## Custom Domain (Optional)

After deploying:
1. Go to app settings
2. Add your custom domain
3. Update DNS records at your domain provider

## Monitoring & Logs

- View app logs in Streamlit Cloud dashboard
- Check app metrics under "Usage"

## Need Help?

- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-cloud/get-started)
- [Supabase Docs](https://supabase.com/docs)
