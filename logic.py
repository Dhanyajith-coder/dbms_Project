import os
from supabase import create_client, Client
from dotenv import load_dotenv

# ==========================================
# 1. INITIALIZATION & CONNECTION
# ==========================================

# Load environment variables
load_dotenv()
# Get Supabase credentials
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

# Validate credentials
if not url or not key:
    raise ValueError(
        "Credentials missing! Ensure .env contains "
        "SUPABASE_URL and SUPABASE_KEY."
    )

# Create Supabase client
supabase: Client = create_client(url, key)

# ==========================================
# 2. FIND NEAREST DONORS
# ==========================================

def find_nearest_donors(hosp_lat, hosp_lon, blood_group_input):
    """
    Calls Supabase SQL function to find nearest donors.
    """

    try:

        response = supabase.rpc(
            "get_nearest_donors_sql",
            {
                "h_lat": hosp_lat,
                "h_lon": hosp_lon,
                "req_blood": blood_group_input
            }
        ).execute()

        return response.data

    except Exception as e:

        print(f"\nError fetching donors: {e}")
        return []

# ==========================================
# 3. REQUEST STATUS UPDATE
# ==========================================

def update_request_status(
    request_id,
    current_status,
    action,
    donor_id=None
):
    """
    Handles request lifecycle.

    Pending + accept -> Accepted
    Accepted/active + completed -> Deactivated
    """

    new_status = current_status

    # ======================================
    # STATE MACHINE LOGIC
    # ======================================

    if current_status.lower() == "pending" and action == "accept":
        new_status = "Accepted"

    elif (
        current_status.lower() in ["accepted", "active"]
        and action == "completed"
    ):
        new_status = "Deactivated"

    # ======================================
    # UPDATE DATABASE
    # ======================================

    if new_status != current_status:

        update_data = {
            "status": new_status
        }

        # Add donor ID if available
        if donor_id is not None:
            update_data["assigned_donor_id"] = donor_id

        try:

            response = (
                supabase
                .table("blood_requests")
                .update(update_data)
                .eq("id", request_id)
                .execute()
            )

            print("\nUPDATED DATA:")
            print(response.data)

            print(
                f"\nSUCCESS: Request {request_id} moved "
                f"from {current_status} to {new_status}."
            )

            return response.data

        except Exception as e:

            print(f"\nDatabase update failed: {e}")
            return None

    else:

        print(
            "\nNo status change required.\n"
            "Check current_status value in database."
        )

        return None

# ==========================================
# 4. MAIN TEST SUITE
# ==========================================

if __name__ == "__main__":

    # Mumbai hospital coordinates
    TEST_LAT = 19.0760
    TEST_LON = 72.8777
    TEST_BLOOD = "O+"

    print("\n===================================")
    print(" BLOOD DONATION SYSTEM TEST ")
    print("===================================")

    # ======================================
    # STEP 1 - FIND DONORS
    # ======================================

    print(f"\nSearching for {TEST_BLOOD} donors...\n")

    donors = find_nearest_donors(
        TEST_LAT,
        TEST_LON,
        TEST_BLOOD
    )

    # ======================================
    # DISPLAY DONORS
    # ======================================

    if donors:

        print(f"SUCCESS! Found {len(donors)} donor(s):\n")

        for i, donor in enumerate(donors, 1):

            print(
                f"{i}. "
                f"{donor['name']} | "
                f"Phone: {donor['phone']} | "
                f"Distance: "
                f"{round(donor['distance_km'], 2)} km"
            )

        # ==================================
        # STEP 2 - SEND NOTIFICATIONS
        # ==================================

        print("\n-----------------------------------")
        print(" SENDING DONOR NOTIFICATIONS ")
        print("-----------------------------------\n")

        for donor in donors:

            print(
                f"Notification sent to "
                f"{donor['name']} "
                f"({donor['phone']})"
            )

    else:

        print(
            "\nNo matching donors found.\n"
            "Check donors table data."
        )

    # ======================================
    # STEP 3 - STATUS UPDATE TEST
    # ======================================

    print("\n-----------------------------------")
    print(" TESTING REQUEST STATUS UPDATE ")
    print("-----------------------------------")

    # TEMPORARY TEST
    # Comment this block later after testing

    update_request_status(
        request_id=1,
        current_status="active",
        action="completed"
    )

    print("\n===================================")
    print(" SYSTEM TEST COMPLETED ")
    print("===================================")