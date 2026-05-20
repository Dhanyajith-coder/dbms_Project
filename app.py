import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
import os

# =========================
# LOAD ENV
# =========================

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# =========================
# CHECK ENV
# =========================

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase credentials missing")
    st.stop()

# =========================
# CONNECT SUPABASE
# =========================

supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

# =========================
# PAGE
# =========================

st.set_page_config(
    page_title="Blood Bank",
    page_icon="🩸"
)

st.title("🩸 Blood Bank Management System")

st.write("Supabase connected successfully ✅")

# =========================
# TEST DATABASE
# =========================

try:

    data = supabase.table("donors").select("*").execute()

    st.success("Database connected successfully ✅")

    st.write(data.data)

except Exception as e:

    st.error(f"Database Error: {e}")