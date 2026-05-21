import streamlit as st
from logic import update_request_status, get_nearby_donors

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Blood Donor Portal",
    page_icon="🩸",
    layout="centered"
)

# =====================================================
# TITLE
# =====================================================

st.title("🩸 Blood Donor Portal")

# =====================================================
# DONOR REGISTRATION
# =====================================================

st.header("Donor Registration")

name = st.text_input("Enter Your Name")

blood_group = st.selectbox(
    "Select Blood Group",
    ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
)

location = st.text_input("Enter Your Location")

if st.button("Register"):
    st.success(f"Thank you {name}! You are registered as a donor.")

# =====================================================
# STATUS UPDATE
# =====================================================

st.divider()

st.header("Update Donation Status")

request_id = st.number_input(
    "Request ID",
    min_value=1
)

status = st.selectbox(
    "Select Status",
    ["Pending", "Accepted", "Completed"]
)

if st.button("Update Status"):
    update_request_status(request_id, status)
    st.success("Request status updated successfully!")

# =====================================================
# FIND DONORS
# =====================================================

st.divider()

st.header("Nearby Blood Requests")

blood_needed = st.selectbox(
    "Required Blood Group",
    ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
)

if st.button("Find Donors"):

    donor_list = [
        {
            "name": "Rahul",
            "blood_group": blood_needed,
            "lat": 12.9698,
            "lon": 77.7500
        },
        {
            "name": "Priya",
            "blood_group": blood_needed,
            "lat": 12.9591,
            "lon": 77.6974
        }
    ]

    hospital_lat = 12.9716
    hospital_lon = 77.5946

    donors = get_nearby_donors(
        hospital_lat,
        hospital_lon,
        donor_list,
        10
    )

    st.write("Available Donors:")

    st.write(donors)