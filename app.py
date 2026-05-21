import os
import re
import uuid

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
        /* Main background */
        .main {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        
        /* Title styling */
        h1 {
            color: #c41e3a;
            font-weight: 700;
            text-align: center;
            margin-bottom: 10px;
        }
        
        h2 {
            color: #c41e3a;
            border-bottom: 3px solid #ff6b6b;
            padding-bottom: 10px;
        }
        
        h3 {
            color: #2d3436;
        }
        
        /* Button styling */
        .stButton>button {
            background: linear-gradient(135deg, #c41e3a 0%, #ff6b6b 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
            width: 100%;
        }
        
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(196, 30, 58, 0.4);
        }
        
        /* Form inputs */
        .stTextInput>div>div>input,
        .stNumberInput>div>div>input,
        .stSelectbox>div>div>select,
        .stTextArea>div>div>textarea {
            border-radius: 8px;
            border: 2px solid #e0e0e0;
            transition: all 0.3s ease;
        }
        
        .stTextInput>div>div>input:focus,
        .stNumberInput>div>div>input:focus,
        .stSelectbox>div>div>select:focus,
        .stTextArea>div>div>textarea:focus {
            border-color: #c41e3a;
            box-shadow: 0 0 8px rgba(196, 30, 58, 0.3);
        }
        
        /* Radio buttons */
        .stRadio>label {
            font-weight: 600;
            font-size: 16px;
        }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def load_supabase_client() -> "create_client":
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")

    if not url or not key:
        st.error("Missing Supabase credentials. Please set SUPABASE_URL and SUPABASE_KEY in your .env file.")
        st.stop()

    return create_client(url, key)


def execute_supabase_insert(client, table_name: str, payload: dict):
    payload = payload.copy()
    while True:
        resp = client.table(table_name).insert(payload).execute()
        error = getattr(resp, "error", None)
        if not error:
            return resp

        message = None
        if isinstance(error, dict):
            message = error.get("message") or str(error)
        else:
            message = str(error)

        # Handle missing schema columns gracefully by dropping them and retrying.
        match = re.search(r"Could not find the '([^']+)' column", message)
        if match:
            missing_column = match.group(1)
            if missing_column in payload:
                payload.pop(missing_column)
                logging.warning("Dropped unknown column '%s' from %s insert and retrying.", missing_column, table_name)
                continue

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
    st.markdown("### 📋 Create Blood Request")
    
    with st.container():
        col1, col2 = st.columns([1, 1], gap="large")
        
        with col1:
            st.markdown("#### Request Details")
            blood_type = st.selectbox(
                "🩸 Blood Type Needed",
                ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"],
                key="hosp_blood"
            )
            units_needed = st.number_input(
                "📦 Units Needed",
                min_value=1,
                value=5,
                step=1,
                key="hosp_units"
            )
        
        with col2:
            st.markdown("#### Priority")
            urgency_emoji = {"Normal": "🟡", "High": "🟠", "Critical": "🔴"}
            urgency = st.selectbox(
                "⚠️ Urgency Level",
                ["Normal", "High", "Critical"],
                key="hosp_urgency",
                format_func=lambda x: f"{urgency_emoji.get(x, '')} {x}"
            )
        
        st.markdown("---")
        description = st.text_area(
            "📝 Additional Details / Notes",
            placeholder="Provide any additional context...",
            height=100,
            key="hosp_desc"
        )
        
        st.markdown("")
        col_button = st.columns([1, 3])
        with col_button[0]:
            submit = st.button("🚀 Send Request", use_container_width=True)
        
        if submit:
            request_data = {
                "hospital_name": hospital_name,
                "blood_type": blood_type,
                "units_needed": units_needed,
                "units_collected": 0,
                "urgency": urgency,
                "description": description,
                "status": "open",
                "request_code": generate_code("REQ"),
            }
            try:
                client.table("blood_requests").insert(request_data).execute()
                st.success(f"✅ Request sent! Donors will see it now.")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Failed to create request: {e}")


def render_donor_requests_view(client, donor_blood_type: str):
    """Show open blood requests matching donor's blood type."""
    st.subheader("🩸 Available Blood Requests")
    
    requests = fetch_blood_requests(client)
    if not requests:
        st.info("No pending blood requests at this time.")
        return

    try:
        df_requests = pd.DataFrame(requests)
        
        # Verify required columns exist
        required_cols = ["blood_type", "status", "id", "hospital_name", "units_needed", "units_collected"]
        missing_cols = [col for col in required_cols if col not in df_requests.columns]
        
        if missing_cols:
            st.error(f"Database error: missing columns {missing_cols}. Expected: {required_cols}")
            st.write(f"Available columns: {list(df_requests.columns)}")
            return
        
        # Filter to open requests matching donor blood type
        open_reqs = df_requests[
            (df_requests["status"] == "open") & 
            (df_requests["blood_type"] == donor_blood_type)
        ]

        if open_reqs.empty:
            st.info(f"No open requests for {donor_blood_type} blood at this time.")
            return
    except Exception as e:
        st.error(f"Error processing blood requests: {e}")
        return

    donor_phone = st.session_state.get("user_info", {}).get("phone")
    donor_name = st.session_state.get("user_info", {}).get("name")

    for _, req in open_reqs.iterrows():
        try:
            request_id = req.get("id")
            hospital = req.get("hospital_name")
            units_needed = req.get("units_needed", 0)
            units_collected = req.get("units_collected", 0)
            urgency = req.get("urgency", "Normal")
            description = req.get("description", "")

            # Check if quota met
            quota_met = units_collected >= units_needed
            
            request_accepted = False
            if donor_phone:
                request_accepted = donor_has_accepted(client, request_id, donor_phone)

            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{hospital}** | {urgency} Urgency")
                st.write(f"Need: {units_needed} units | Collected: {units_collected}/{units_needed}")
                if description:
                    st.write(f"*{description}*")
            with col2:
                if quota_met:
                    st.warning("✅ Quota met")
                elif request_accepted:
                    st.info("You have already accepted this request.")
                else:
                    if st.button(f"Accept ##btn_{request_id}"):
                        # Record donor acceptance and close request when complete
                        ok = insert_acceptance(client, request_id, donor_name or "", donor_phone or "")
                        if ok:
                            new_collected = units_collected + 1
                            updates = {"units_collected": new_collected}
                            if new_collected >= units_needed:
                                updates["status"] = "closed"
                            client.table("blood_requests").update(updates).eq("id", request_id).execute()
                            st.success("✅ Thank you! Your blood unit has been recorded.")
                        else:
                            st.error("Could not record acceptance. Please try again.")
                        st.rerun()
            st.divider()
        except Exception as e:
            st.error(f"Error displaying request: {e}")
            continue


def render_donor_profile(client, user_info: dict):
    """Show donor profile and contribution metrics."""
    st.markdown("### 👤 Your Profile")
    name = user_info.get("name", "Unknown")
    phone = user_info.get("phone", "Unknown")
    blood_type = user_info.get("blood_type", "Unknown")

    st.markdown(f"**Name:** {name}")
    st.markdown(f"**Phone:** {phone}")
    st.markdown(f"**Blood Type:** {blood_type}")

    # Contributions
    accepts = fetch_acceptances_for_donor(client, phone)
    total_donations = len(accepts)
    st.metric("🩺 Units donated", total_donations)

    if accepts:
        st.markdown("#### Your recent donations")
        for a in accepts[-10:][::-1]:
            rid = a.get("request_id")
            t = a.get("created_at") or ""
            st.markdown(f"- Request `{rid}` — {t}")


def render_hospital_profile(client, user_info: dict):
    """Show hospital profile with list of own requests and management actions."""
    name = user_info.get("name", "Hospital")
    st.markdown(f"### 🏥 {name} — Dashboard")

    # Show hospital's requests
    reqs = fetch_blood_requests(client)
    my_reqs = [r for r in reqs if r.get("hospital_name") == name]

    st.markdown(f"**Active requests:** {len([r for r in my_reqs if r.get('status')=='open'])}")
    if my_reqs:
        for r in my_reqs:
            st.markdown(f"- **{r.get('blood_type')}** | {r.get('units_collected',0)}/{r.get('units_needed',0)} units — status: {r.get('status')}")
            if r.get('status') == 'open':
                if st.button(f"Close request {r.get('id')}", key=f"close_{r.get('id')}"):
                    try:
                        client.table('blood_requests').update({'status':'closed'}).eq('id', r.get('id')).execute()
                        st.success("Request closed")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Could not close request: {e}")
    else:
        st.info("You have no requests yet. Use the form to create one.")


def main():
    st.set_page_config(page_title="Blood Bank", page_icon="🩸")
    st.title("🩸 Blood Bank Management System")

    client = load_supabase_client()

    # Show role registration if not logged in
    if "role" not in st.session_state:
        render_role_registration(client)
        return

    # Show current role and allow changing it
    role = st.session_state.get("role")
    user_info = st.session_state.get("user_info", {})
    user_name = user_info.get("name", "Unknown")

    st.sidebar.info(f"Signed in as: **{user_name}** ({role})")
    if st.sidebar.button("Change role"):
        del st.session_state["role"]
        if "user_info" in st.session_state:
            del st.session_state["user_info"]
        st.rerun()

    # Role-based UI
    if role == "Donor":
        # Show donor profile first
        render_donor_profile(client, user_info)
        blood_type = user_info.get("blood_type")
        if not blood_type:
            st.warning("Donor blood type not found. Please change role and register again.")
            return
        st.markdown("---")
        render_donor_requests_view(client, blood_type)

    elif role in ["Hospital", "Blood Bank"]:
        # Show hospital profile and request form
        render_hospital_profile(client, user_info)
        st.markdown("---")
        render_hospital_request_form(client, user_name)

    else:
        st.error(f"Unknown role: {role}")


def render_role_registration(client):
    """Landing page: pick role and register."""
    st.title("Welcome to the Blood Bank Portal")
    st.write("Please tell us who you are so we can show the right experience.")


    # Step 1: Select role
    selected_role = st.radio("I am a", ["Donor", "Hospital", "Blood Bank"], horizontal=True)
    st.divider()

    if selected_role == "Donor":
        st.subheader("Donor Registration")
        with st.form("donor_form", clear_on_submit=False):
            name = st.text_input("Full name")
            phone = st.text_input("Phone number")
            blood_type = st.selectbox("Blood type", ["O+", "O-", "A+", "A-", "B+", "B-", "AB+", "AB-"])
            address = st.text_input("Address")
            submitted = st.form_submit_button("Continue")

            if submitted:
                if not name or not phone or not address:
                    st.error("Please provide a name, phone, and address to continue.")
                    return

                try:
                    insert_donor(client, name, phone, blood_type, address)
                    st.success("✅ Donor registered successfully.")
                    st.session_state["role"] = "Donor"
                    st.session_state["user_info"] = {
                        "name": name,
                        "phone": phone,
                        "role": "Donor",
                        "blood_type": blood_type,
                    }
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Could not save donor registration: {e}")

    else:  # Hospital or Blood Bank
        st.subheader(f"{selected_role} Registration")
        with st.form("org_form", clear_on_submit=False):
            name = st.text_input("Organization name")
            phone = st.text_input("Contact phone")
            address = st.text_input("Address")
            submitted = st.form_submit_button("Continue")

            if submitted:
                if not name or not phone or not address:
                    st.error("Please provide a name, phone, and address to continue.")
                    return

                try:
                    insert_hospital(client, name, phone, address, selected_role)
                    st.success(f"✅ {selected_role} registered successfully.")
                    st.session_state["role"] = selected_role
                    st.session_state["user_info"] = {
                        "name": name,
                        "phone": phone,
                        "role": selected_role,
                    }
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Could not save organization registration: {e}")


if __name__ == "__main__":
    main()