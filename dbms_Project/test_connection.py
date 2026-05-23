import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Load .env file
load_dotenv()

# Read credentials
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

# Create Supabase client
supabase: Client = create_client(url, key)

print("🚀 Secure connection to Supabase established successfully!")