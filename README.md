# Blood Donation App

Simple Streamlit application for managing blood donors and nearby donor lookup.

Prerequisites
- Python 3.10+
- A Supabase project with a `donors` and `blood_requests` table

Quick setup
1. Create a virtual environment and activate it:

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# or with cmd: .\.venv\Scripts\activate.bat
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with the following keys:

```
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-supabase-key>
```

Run the app

```bash
streamlit run app.py
```

Alternative pages
- Donor portal UI: `streamlit run donor_app.py`

Notes
- `logic.py` contains Supabase helpers and a local `get_nearby_donors` helper used by the UI.
- If you run into Supabase import errors locally, ensure the `supabase` package is installed and your `.env` is correct.

Map view (optional)

- The app includes a Map view that uses `folium` and `streamlit-folium` for interactive donor markers.
- To enable the map, install the optional dependencies:

```bash
pip install folium streamlit-folium
```

- Donors must include `lat` and `lon` fields in the `donors` table for the map to display markers.
