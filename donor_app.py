import streamlit as st
from logic import get_nearby_donors, update_request_status


def configure_page() -> None:
    st.set_page_config(page_title="Blood Donor Portal", page_icon="🩸", layout="centered")
    st.title("🩸 Blood Donor Portal")


def render_registration_section() -> None:
    st.header("Donor Registration")
    with st.form("donor_registration_form", clear_on_submit=True):
        name = st.text_input("Enter your name")
        blood_group = st.selectbox(
            "Select blood group",
            ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
        )
        location = st.text_input("Enter your location")
        submitted = st.form_submit_button("Register")

        if submitted:
            if not name or not location:
                st.error("Please enter both name and location.")
                return
            st.success(f"Thank you {name}! You are registered as a donor.")
            st.info(f"Blood group: {blood_group}, Location: {location}")


def render_status_update_section() -> None:
    st.divider()
    st.header("Update Donation Status")
    with st.form("donation_status_form", clear_on_submit=True):
        request_id = st.number_input("Request ID", min_value=1, step=1)
        status = st.selectbox("Select status", ["Pending", "Accepted", "Completed"])
        submitted = st.form_submit_button("Update Status")

        if submitted:
            update_request_status(request_id, status)
            st.success("Request status update sent.")


def render_find_donors_section() -> None:
    st.divider()
    st.header("Nearby Blood Requests")
    blood_needed = st.selectbox(
        "Required blood group",
        ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"]
    )

    if st.button("Find Donors"):
        donor_list = [
            {"name": "Rahul", "blood_group": blood_needed, "lat": 12.9698, "lon": 77.7500},
            {"name": "Priya", "blood_group": blood_needed, "lat": 12.9591, "lon": 77.6974},
        ]

        hospital_lat = 12.9716
        hospital_lon = 77.5946

        donors = get_nearby_donors(hospital_lat, hospital_lon, donor_list, max_distance_km=10)

        if donors:
            st.write("### Available Donors")
            for d in donors:
                card_cols = st.columns([1, 3, 1])
                with card_cols[0]:
                    st.icon("person") if hasattr(st, "icon") else st.text("👤")
                with card_cols[1]:
                    st.markdown(f"**{d.get('name')}**  ")
                    st.markdown(f"Blood: **{d.get('blood_group')}**  ")
                    st.markdown(f"Distance: **{d.get('distance_km')} km**  ")
                    phone = d.get("phone")
                    if phone:
                        st.markdown(f"Phone: {phone}")
                with card_cols[2]:
                    if st.button(f"Contact {d.get('name')}"):
                        st.success(f"Contact initiated for {d.get('name')}")
        else:
            st.info("No nearby donors found.")


def main() -> None:
    configure_page()
    render_registration_section()
    render_status_update_section()
    render_find_donors_section()


if __name__ == "__main__":
    main()
