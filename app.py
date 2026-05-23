import os
import re
import uuid
import math
import textwrap
import datetime

# Avoid failing when optional native packages like `pyiceberg` are missing/build-failing.
# If `pyiceberg` is not installed (or fails to build on Windows), we provide a lightweight
# stub so the Streamlit UI can run. Remove this stub if you actually need pyiceberg functionality.
try:
    import pyiceberg  # type: ignore
except Exception:
    import sys
    from unittest.mock import MagicMock

    mock_iceberg = MagicMock()
    sys.modules["pyiceberg"] = mock_iceberg
    sys.modules["pyiceberg.catalog"] = mock_iceberg
    sys.modules["pyiceberg.catalog.rest"] = mock_iceberg

import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from supabase import create_client
import logging
logging.basicConfig(level=logging.INFO)


def apply_custom_theme():
    """Apply custom CSS styling for better UX."""
    custom_css = """
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        /* Main background */
        body, .main, [data-testid="stAppViewContainer"] {
            background: #f6efe3;
            color: #17243f;
        }

        /* Page container */
        [data-testid="stAppViewContainer"] {
            padding: 0 !important;
            background: #f6efe3;
        }

        /* Sidebar styling */
        [data-testid="stSidebar"] {
            background: #1f3856;
            color: #ffffff;
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
            color: #ffffff !important;
        }

        /* Main title */
        h1 {
            color: #233d5c !important;
            font-weight: 800 !important;
            text-align: center;
            margin: 30px 0 20px 0 !important;
            text-shadow: 0 2px 6px rgba(35, 61, 92, 0.08);
            font-size: 2.8em !important;
        }

        h2 {
            color: #4a5f7f !important;
            border-left: 4px solid #cbb895 !important;
            padding-left: 15px !important;
            margin: 25px 0 15px 0 !important;
            font-weight: 700 !important;
        }

        h3 {
            color: #5b708f !important;
            font-weight: 600 !important;
            margin: 20px 0 10px 0 !important;
        }

        /* Card styling */
        .card {
            background: #ffffff;
            border: 1px solid rgba(35, 61, 92, 0.08);
            border-radius: 20px;
            padding: 26px;
            margin: 16px 0;
            box-shadow: 0 18px 35px rgba(35, 61, 92, 0.06);
            transition: all 0.25s ease;
        }

        .card:hover {
            transform: translateY(-2px);
            box-shadow: 0 22px 45px rgba(35, 61, 92, 0.08);
        }

        /* Button styling */
        .stButton>button,
        .stButton>button * {
            background: #1f3856 !important;
            color: #ffffff !important;
        }

        .stButton>button {
            border: none !important;
            padding: 12px 24px !important;
            border-radius: 12px !important;
            font-weight: 700 !important;
            font-size: 0.95em !important;
            transition: all 0.25s ease !important;
            width: 100% !important;
            letter-spacing: 0.5px !important;
            box-shadow: 0 8px 20px rgba(31, 56, 86, 0.18) !important;
        }

        .stButton>button:hover,
        .stButton>button:focus {
            transform: translateY(-2px) !important;
            box-shadow: 0 10px 28px rgba(31, 56, 86, 0.22) !important;
            background: #163147 !important;
            color: #ffffff !important;
        }

        .stButton>button:active {
            transform: translateY(-1px) !important;
        }

        /* Form inputs */
        .stTextInput>div>div>input,
        .stNumberInput>div>div>input,
        .stSelectbox>div>div>select,
        .stTextArea>div>div>textarea {
            background-color: #ffffff !important;
            border: 1px solid rgba(35, 61, 92, 0.12) !important;
            border-radius: 12px !important;
            color: #233d5c !important;
            padding: 14px !important;
            font-size: 0.95em !important;
            transition: all 0.25s ease !important;
        }

        .stTextInput>div>div>input::placeholder,
        .stTextArea>div>div>textarea::placeholder {
            color: #9ca7b6 !important;
        }

        .stTextInput>div>div>input:focus,
        .stNumberInput>div>div>input:focus,
        .stSelectbox>div>div>select:focus,
        .stTextArea>div>div>textarea:focus {
            border-color: #233d5c !important;
            box-shadow: 0 0 10px rgba(35, 61, 92, 0.12) !important;
            background-color: #ffffff !important;
        }

        /* Radio buttons */
        .stRadio>label {
            font-weight: 600 !important;
            font-size: 1em !important;
            color: #233d5c !important;
            padding: 10px 15px !important;
        }

        /* Stats/Metric boxes */
        .metric-box {
            background: rgba(203, 184, 149, 0.14);
            border-left: 4px solid #cbb895;
            border-radius: 12px;
            padding: 20px;
            margin: 10px 0;
            color: #233d5c;
        }

        /* Info/Success/Error/Warning messages */
        .stAlert {
            border-radius: 12px !important;
            padding: 15px !important;
            margin: 10px 0 !important;
        }

        .stSuccess { background-color: rgba(34, 197, 94, 0.14) !important; }
        .stError { background-color: rgba(220, 38, 38, 0.14) !important; }
        .stWarning { background-color: rgba(234, 179, 8, 0.14) !important; }
        .stInfo { background-color: rgba(59, 130, 246, 0.14) !important; }

        /* Divider */
        hr {
            border-color: rgba(35, 61, 92, 0.14) !important;
            margin: 30px 0 !important;
        }

        /* Table styling */
        .stDataFrame {
            border-radius: 12px !important;
            overflow: hidden !important;
        }

        /* Form container */
        form {
            background: #ffffff;
            border: 1px solid rgba(35, 61, 92, 0.10);
            border-radius: 18px;
            padding: 30px;
            margin: 20px 0;
        }

        /* Divider style */
        .divider {
            background: linear-gradient(90deg, transparent, #233d5c, transparent);
            height: 2px;
            margin: 30px 0;
        }

        /* Text styling */
        p, span, label, .stMarkdown, .stTextInput, .stSelectbox, .stTextArea {
            color: #17243f !important;
        }

        a {
            color: #1f3856 !important;
            text-decoration: none;
            transition: all 0.25s ease;
        }

        a:hover {
            color: #233d5c !important;
            text-decoration: underline;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def load_supabase_client() -> "create_client":
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    anon_key = os.getenv("SUPABASE_KEY")

    if not url or not (service_key or anon_key):
        st.error("Missing Supabase credentials. Please set SUPABASE_URL and either SUPABASE_KEY or SUPABASE_SERVICE_ROLE_KEY in your .env file.")
        st.stop()

    if service_key:
        logging.info("Using Supabase service role key for database access.")
        return create_client(url, service_key)

    logging.warning("Using the anon Supabase key. Inserts may fail if row-level security is enabled.")
    return create_client(url, anon_key)


def execute_supabase_insert(client, table_name: str, payload: dict):
    payload = payload.copy()
    while True:
        try:
            resp = client.table(table_name).insert(payload).execute()
            error = getattr(resp, "error", None)
            if not error:
                return resp

            if isinstance(error, dict):
                message = error.get("message") or str(error)
            else:
                message = str(error)
        except Exception as exc:
            message = str(exc)
            resp = None

        # Handle missing schema columns gracefully by dropping them and retrying.
        match = re.search(r"Could not find the '([^']+)' column", message)
        if match:
            missing_column = match.group(1)
            if missing_column in payload:
                payload.pop(missing_column)
                logging.warning("Dropped unknown column '%s' from %s insert and retrying.", missing_column, table_name)
                continue

        if "row-level security policy" in message.lower() or "42501" in message:
            raise RuntimeError(
                f"Supabase insert error for {table_name}: {message}. "
                "This usually means row-level security is enabled for that table. "
                "Set SUPABASE_SERVICE_ROLE_KEY in .env or update your RLS policies to allow inserts."
            )

        raise RuntimeError(f"Supabase insert error for {table_name}: {message}")


def generate_code(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:8].upper()}"


def insert_donor(client, name: str, phone: str, blood_type: str, address: str):
    donor = {
        "name": name,
        "phone": phone,
        "blood_type": blood_type,
        "address": address,
        "donor_code": generate_code("DONOR"),
    }

    resp = execute_supabase_insert(client, "donors", donor)
    logging.info("Insert donor response: %s", getattr(resp, 'data', resp))
    return True


def insert_hospital(client, name: str, phone: str, address: str, role: str):
    hospital = {
        "name": name,
        "phone": phone,
        "address": address,
        "role": role,
        "hospital_code": generate_code("HOSP"),
    }

    resp = execute_supabase_insert(client, "hospitals", hospital)
    logging.info("Insert hospital response: %s", getattr(resp, 'data', resp))
    return True


def fetch_blood_requests(client):
    """Fetch all blood requests from the database."""
    try:
        response = client.table("blood_requests").select("*").execute()
        return response.data or []
    except Exception:
        return []


def fetch_donor_info(client, phone: str):
    try:
        resp = client.table("donors").select("*").eq("phone", phone).limit(1).execute()
        return (resp.data or [])[0] if resp.data else {}
    except Exception:
        return {}


def fetch_hospital_info(client, phone: str):
    try:
        resp = client.table("hospitals").select("*").eq("phone", phone).limit(1).execute()
        return (resp.data or [])[0] if resp.data else {}
    except Exception:
        return {}



def sync_expired_requests(client):
    now = datetime.datetime.utcnow()
    requests = fetch_blood_requests(client)
    for req in requests:
        request_id = req.get("id")
        status = req.get("status")
        due_date = req.get("due_date")
        units_needed = req.get("units_needed", 0)
        if not request_id or status != "open" or not due_date:
            continue

        try:
            due_dt = datetime.datetime.fromisoformat(due_date) if isinstance(due_date, str) else due_date
        except Exception:
            continue

        if due_dt < now:
            acceptances_resp = client.table("acceptances").select("*").eq("request_id", request_id).execute()
            acceptances = acceptances_resp.data or []
            if acceptances:
                canceled = len(acceptances)
                client.table("acceptances").delete().eq("request_id", request_id).execute()
                client.table("blood_requests").update({
                    "units_needed": units_needed + canceled,
                    "status": "open"
                }).eq("id", request_id).execute()

def insert_acceptance(client, request_id, donor_name, donor_phone):
    """Record that a donor accepted one unit for a request."""
    try:
        payload = {
            "acceptance_code": generate_code("ACC"),
            "request_id": request_id,
            "donor_name": donor_name,
            "donor_phone": donor_phone,
            "created_at": None,
        }
        # Supabase will fill timestamps if configured; created_at None is harmless
        client.table("acceptances").insert(payload).execute()
        return True
    except Exception:
        return False


def donor_has_accepted(client, request_id, donor_phone):
    try:
        resp = client.table("acceptances").select("*").eq("request_id", request_id).eq("donor_phone", donor_phone).execute()
        data = resp.data or []
        return len(data) > 0
    except Exception:
        return False


def fetch_acceptances_for_donor(client, donor_phone):
    try:
        resp = client.table("acceptances").select("*").eq("donor_phone", donor_phone).execute()
        return resp.data or []
    except Exception:
        return []


def render_hospital_request_form(client, hospital_name: str):
    """Hospital/Blood Bank form to create blood requests."""
    st.markdown("## 📋 Create Blood Request")
    st.markdown("Post a new blood request to find donors matching your needs.")
    
    with st.form("hospital_request_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🩸 What you need")
            blood_type = st.selectbox(
                "Blood Type",
                ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"],
                key="hosp_blood"
            )
            units_needed = st.number_input(
                "Units Needed",
                min_value=1,
                value=5,
                step=1,
                key="hosp_units"
            )
        
        with col2:
            st.markdown("### ⚠️ Urgency Level")
            urgency_options = {
                "🟡 Normal": "Normal",
                "🟠 High": "High",
                "🔴 Critical": "Critical"
            }
            urgency_display = st.selectbox(
                "Priority",
                list(urgency_options.keys()),
                key="hosp_urgency"
            )
            urgency = urgency_options[urgency_display]
            due_date = st.date_input(
                "Request Deadline",
                value=datetime.date.today() + datetime.timedelta(days=2),
                key="hosp_due_date"
            )
            due_time = st.time_input(
                "Deadline Time",
                value=datetime.time(18, 0),
                key="hosp_due_time"
            )
        
        st.markdown("---")
        description = st.text_area(
            "📝 Additional Details",
            placeholder="Any special instructions or medical context...",
            height=80,
            key="hosp_desc"
        )
        
        submit = st.form_submit_button("🚀 Post Request", use_container_width=True)
        
        if submit:
            if not blood_type:
                st.error("❌ Please select a blood type")
                return

            due_dt = datetime.datetime.combine(due_date, due_time)
            request_data = {
                "hospital_name": hospital_name,
                "blood_type": blood_type,
                "units_needed": units_needed,
                "units_collected": 0,
                "urgency": urgency,
                "description": description,
                "status": "open",
                "request_code": generate_code("REQ"),
                "due_date": due_dt.isoformat(),
            }

            try:
                client.table("blood_requests").insert(request_data).execute()
                st.success(f"✅ Request posted! Donors will see your request in the feed.")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Failed to create request: {e}")


def render_donor_requests_view(client, donor_blood_type: str):
    """Show open blood requests matching donor's blood type."""
    st.markdown("## 💧 Available Blood Requests")
    st.markdown(f"Showing requests for **{donor_blood_type}** blood type")
    
    requests = fetch_blood_requests(client)
    if not requests:
        st.info("📭 No pending blood requests at this time. Come back later!")
        return

    try:
        df_requests = pd.DataFrame(requests)
        
        required_cols = ["blood_type", "status", "id", "hospital_name", "units_needed", "units_collected"]
        missing_cols = [col for col in required_cols if col not in df_requests.columns]
        
        if missing_cols:
            st.error(f"Database error: missing columns {missing_cols}")
            return
        
        open_reqs = df_requests[
            (df_requests["status"] == "open") & 
            (df_requests["blood_type"] == donor_blood_type)
        ]

        if open_reqs.empty:
            st.info(f"📭 No open requests for {donor_blood_type} blood at this time.")
            return

        donor_phone = st.session_state.get("user_info", {}).get("phone")
        donor_name = st.session_state.get("user_info", {}).get("name")

        request_records = open_reqs.to_dict(orient="records")

        if not request_records:
            st.info("📭 No open requests for this blood type at the moment. Check back soon!")
            return
    except Exception as e:
        st.error(f"Error processing blood requests: {e}")
        return

    urgency_colors = {
        "Normal": "🟡",
        "High": "🟠",
        "Critical": "🔴"
    }

    for idx, req in enumerate(request_records):
        try:
            request_id = req.get("id")
            request_code = req.get("request_code")
            hospital = req.get("hospital_name")
            units_needed = req.get("units_needed", 0)
            units_collected = req.get("units_collected", 0)
            urgency = req.get("urgency", "Normal")
            description = req.get("description")
            distance_km = req.get("distance_km")
            due_date = req.get("due_date")

            if pd.isna(request_code):
                request_code = None
            if pd.isna(hospital):
                hospital = "Unknown hospital"
            if pd.isna(units_needed):
                units_needed = 0
            if pd.isna(units_collected):
                units_collected = 0
            if pd.isna(description):
                description = ""
            if pd.isna(due_date):
                due_date = ""

            valid_request_id = request_id is not None and not (isinstance(request_id, float) and math.isnan(request_id))
            if not request_code:
                request_code = f"REQ-{request_id}" if valid_request_id else "REQ-UNKNOWN"
            if not hospital:
                hospital = "Unknown hospital"

            quota_met = units_collected >= units_needed
            request_accepted = False
            if donor_phone and valid_request_id:
                request_accepted = donor_has_accepted(client, request_id, donor_phone)

            progress_pct = min(100, int((units_collected / units_needed * 100) if units_needed > 0 else 0))
            distance_text = f"<p style=\"margin: 8px 0; font-size: 0.9em; color: #5a6d8f;\">Distance: {distance_km:.1f} km</p>" if distance_km is not None else ""
            due_text = f"<p style=\"margin: 8px 0; font-size: 0.9em; color: #5a6d8f;\">Deadline: {due_date}</p>" if due_date else ""

            html_card = textwrap.dedent(f"""
                <div class="card">
                    <div style="display: flex; justify-content: space-between; align-items: start; gap: 16px;">
                        <div>
                            <h4 style="margin: 0; color: #1f3856;">🏥 {hospital}</h4>
                            <p style="margin: 8px 0; font-size: 0.95em; color: #475a7c;">{urgency_colors.get(urgency, "🟡")} {urgency} · {units_needed} units · {request_code}</p>
                        </div>
                    </div>
                    {distance_text}
                    {due_text}
                    <div style="margin: 12px 0;">
                        <div style="background: #e8dfc8; border-radius: 8px; overflow: hidden; height: 10px;">
                            <div style="background: linear-gradient(90deg, #1f3856, #3f5c8b); height: 100%; width: {progress_pct}%;"></div>
                        </div>
                        <p style="font-size: 0.88em; color: #5a6d8f; margin: 8px 0 0 0;">{units_collected}/{units_needed} units collected</p>
                    </div>
                    {f'<p style="color: #475a7c; font-style: italic; margin: 8px 0;">{description}</p>' if description else ''}
                </div>
            """)

            st.markdown(html_card, unsafe_allow_html=True)

            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                pass
            
            with col2:
                if quota_met:
                    st.info("✅ Quota met")
                elif request_accepted:
                    st.success("✅ You accepted this")
            
            with col3:
                if not quota_met and not request_accepted:
                    donate_key = f"donate_{request_id}_{idx}" if valid_request_id else f"donate_{idx}"
                    if st.button(f"💉 Donate", key=donate_key, use_container_width=True):
                        ok = insert_acceptance(client, request_id, donor_name or "", donor_phone or "")
                        if ok:
                            new_collected = units_collected + 1
                            updates = {"units_collected": new_collected}
                            if new_collected >= units_needed:
                                updates["status"] = "closed"
                            client.table("blood_requests").update(updates).eq("id", request_id).execute()
                            st.success("✅ Thank you for donating! You've saved a life.")
                            st.balloons()
                        else:
                            st.error("❌ Could not record donation. Try again.")
                        st.rerun()
            st.divider()
        except Exception as e:
            st.error(f"Error displaying request: {e}")
            continue


def render_donor_profile(client, user_info: dict):
    """Show donor profile and contribution metrics."""
    name = user_info.get("name", "Unknown")
    phone = user_info.get("phone", "Unknown")
    blood_type = user_info.get("blood_type", "Unknown")
    donor_info = fetch_donor_info(client, phone)
    donor_code = donor_info.get("donor_code", "N/A")
    
    accepts = fetch_acceptances_for_donor(client, phone)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("👤 Name", name, delta=None)
    with col2:
        st.metric("🩸 Blood Type", blood_type, delta=None)
    with col3:
        st.metric("🆔 Donor ID", donor_code, delta=None)
    with col4:
        st.metric("✅ Donations", len(accepts), delta=None)
    
    st.markdown('</div>', unsafe_allow_html=True)

    if accepts:
        st.markdown("#### Your recent donations")
        for a in accepts[-10:][::-1]:
            rid = a.get("request_id")
            acode = a.get("acceptance_code", "N/A")
            t = a.get("created_at") or ""
            st.markdown(f"- Request `{rid}` | Acceptance `{acode}` — {t}")


def render_hospital_profile(client, user_info: dict):
    """Show hospital profile with list of own requests and management actions."""
    name = user_info.get("name", "Hospital")
    hospital_info = fetch_hospital_info(client, user_info.get("phone", ""))
    hospital_code = hospital_info.get("hospital_code", "N/A")
    
    reqs = fetch_blood_requests(client)
    my_reqs = [r for r in reqs if r.get("hospital_name") == name]
    open_reqs = [r for r in my_reqs if r.get('status') == 'open']
    closed = len([r for r in my_reqs if r.get('status') == 'closed'])
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏥 Organization", name[:15], delta=None)
    with col2:
        st.metric("📋 Total Requests", len(my_reqs), delta=None)
    with col3:
        st.metric("🆔 Hospital ID", hospital_code, delta=None)
    with col4:
        st.metric("🟡 Active", len(open_reqs), delta=None)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if open_reqs:
        st.markdown("### 📋 Your Active Requests")
        for r in open_reqs:
            request_code = r.get("request_code") or f"REQ-{r.get('id')}"
            due_date = r.get("due_date")
            due_text = f"<p><strong>Deadline:</strong> {due_date}</p>" if due_date else ""
            urgency_color = {"Normal": "🟡", "High": "🟠", "Critical": "🔴"}

            st.markdown(f'''
            <div class="card">
                <h4>{urgency_color.get(r.get("urgency", "Normal"), "")} {r.get("blood_type")} Blood Request</h4>
                <p><strong>Request ID:</strong> {request_code}</p>
                <p><strong>Progress:</strong> {r.get("units_collected", 0)}/{r.get("units_needed", 0)} units</p>
                <p><strong>Status:</strong> {r.get("status", "unknown").upper()}</p>
                {due_text}
                <p><strong>Details:</strong> {r.get("description", "N/A")}</p>
            </div>
            ''', unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button(f"View Acceptances", key=f"view_{r.get('id')}"):
                    accepts = client.table("acceptances").select("*").eq("request_id", r.get('id')).execute()
                    if accepts.data:
                        st.dataframe(accepts.data)
                    else:
                        st.info("No donors have accepted this request yet")
            with col2:
                if st.button(f"❌ Close Request", key=f"close_{r.get('id')}"):
                    try:
                        client.table('blood_requests').update({'status':'closed'}).eq('id', r.get('id')).execute()
                        st.success("✅ Request closed successfully")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not close request: {e}")


def main():
    st.set_page_config(
        page_title="Vital Flow - Your blood, their future",
        page_icon="🩸",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom theme at the beginning
    apply_custom_theme()

    client = load_supabase_client()
    sync_expired_requests(client)

    # Show role registration if not logged in
    if "role" not in st.session_state:
        render_role_registration(client)
        return

    # Show current role and allow changing it
    role = st.session_state.get("role")
    user_info = st.session_state.get("user_info", {})
    user_name = user_info.get("name", "Unknown")

    # Sidebar
    with st.sidebar:
        st.markdown("### 👤 Account")
        st.markdown(f"**{user_name}**")
        st.markdown(f"*{role}*")
        st.markdown("---")
        
        if st.button("🔄 Change Role", use_container_width=True):
            del st.session_state["role"]
            if "user_info" in st.session_state:
                del st.session_state["user_info"]
            st.rerun()
        
        if st.button("❌ Logout", use_container_width=True):
            del st.session_state["role"]
            if "user_info" in st.session_state:
                del st.session_state["user_info"]
            st.rerun()

    st.markdown("---")

    # Role-based UI
    if role == "Donor":
        render_donor_profile(client, user_info)
        blood_type = user_info.get("blood_type")
        if not blood_type:
            st.error("❌ Donor blood type not found. Please change role and register again.")
            return
        st.markdown("---")
        render_donor_requests_view(client, blood_type)

    elif role in ["Hospital", "Blood Bank"]:
        render_hospital_profile(client, user_info)
        st.markdown("---")
        render_hospital_request_form(client, user_name)

    else:
        st.error(f"❌ Unknown role: {role}")


def render_role_registration(client):
    """Landing page: pick role and register."""
    # Hero section
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px; background: rgba(255,255,255,0.92); border-radius: 20px; margin-bottom: 40px; box-shadow: 0 18px 40px rgba(31,56,86,0.08);">
        <h1 style="font-size: 3em; margin: 0; color: #1f3856;">🩸 Vital_Flow</h1>
        <p style="font-size: 1.2em; color: #475a7c; margin: 10px 0 0 0;">Your blood, their future</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 👥 Who are you?")
    
    # Role selection with enhanced UI
    role_col1, role_col2, role_col3 = st.columns(3)
    
    with role_col1:
        if st.button("🩸 Donor", use_container_width=True, help="Register as a blood donor"):
            st.session_state["selected_role"] = "Donor"
    
    with role_col2:
        if st.button("🏥 Hospital", use_container_width=True, help="Register as a hospital"):
            st.session_state["selected_role"] = "Hospital"
    
    with role_col3:
        if st.button("🏦 Blood Bank", use_container_width=True, help="Register as a blood bank"):
            st.session_state["selected_role"] = "Blood Bank"
    
    st.markdown("---")
    
    selected_role = st.session_state.get("selected_role")
    
    if selected_role == "Donor":
        st.markdown("## 🩸 Donor Registration")
        st.markdown("Help save lives by registering as a blood donor. Your contribution matters!")
        
        with st.form("donor_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("👤 Full Name", placeholder="Enter your full name")
                phone = st.text_input("📱 Phone Number", placeholder="+91 XXXXXXXXXX")
                address = st.text_input("📍 Address", placeholder="City/Area")
            
            with col2:
                blood_type = st.selectbox("🩸 Blood Type", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            
            submitted = st.form_submit_button("✅ Register as Donor", use_container_width=True)

            if submitted:
                if not name or not phone or not address:
                    st.error("❌ Please fill in all fields to continue.")
                    return

                try:
                    insert_donor(client, name, phone, blood_type, address)
                    donor_info = fetch_donor_info(client, phone)
                    donor_code = donor_info.get("donor_code", "N/A")
                    st.success(f"✅ Welcome! You're registered as a donor. Your Donor ID is {donor_code}")
                    st.session_state["role"] = "Donor"
                    st.session_state["user_info"] = {
                        "name": name,
                        "phone": phone,
                        "role": "Donor",
                        "blood_type": blood_type,
                    }
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Registration failed: {e}")

    elif selected_role in ["Hospital", "Blood Bank"]:
        st.markdown(f"## 🏥 {selected_role} Registration")
        st.markdown(f"Register your {selected_role.lower()} to post blood requests and manage donations.")
        
        with st.form("org_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("🏢 Organization Name", placeholder="Hospital/Bank name")
                phone = st.text_input("📱 Contact Phone", placeholder="+91 XXXXXXXXXX")
            
            with col2:
                address = st.text_input("📍 Address", placeholder="City/Area")
            
            submitted = st.form_submit_button(f"✅ Register as {selected_role}", use_container_width=True)

            if submitted:
                if not name or not phone or not address:
                    st.error("❌ Please fill in all fields to continue.")
                    return

                try:
                    insert_hospital(client, name, phone, address, selected_role)
                    hosp_info = fetch_hospital_info(client, phone)
                    hosp_code = hosp_info.get("hospital_code", "N/A")
                    st.success(f"✅ Welcome! {name} is registered. Your Hospital ID is {hosp_code}")
                    st.session_state["role"] = selected_role
                    st.session_state["user_info"] = {
                        "name": name,
                        "phone": phone,
                        "role": selected_role,
                    }
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Registration failed: {e}")
    
    else:
        st.info("👈 Select a role to get started!")


if __name__ == "__main__":
    main()