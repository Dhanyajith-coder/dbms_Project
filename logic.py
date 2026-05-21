import os
import math
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


def find_nearest_donors(hosp_lat, hosp_lon, blood_group_input):
    """Return the nearest donors for a requested blood group."""
    try:
        response = supabase.rpc(
            "get_nearest_donors_sql",
            {
                "h_lat": hosp_lat,
                "h_lon": hosp_lon,
                "req_blood": blood_group_input,
            },
        ).execute()
        return response.data or []
    except Exception as error:
        print(f"Error fetching donors: {error}")
        return []


def _haversine_km(lat1, lon1, lat2, lon2):
    # Haversine formula
    R = 6371.0
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def get_nearby_donors(h_lat, h_lon, donor_list, max_distance_km=10):
    """Filter a local list of donors by distance and return distances.

    This is a lightweight helper for the UI and does not call the database.
    """
    results = []
    for donor in donor_list:
        try:
            dlat = float(donor.get("lat"))
            dlon = float(donor.get("lon"))
        except Exception:
            continue

        distance = _haversine_km(h_lat, h_lon, dlat, dlon)
        if distance <= max_distance_km:
            donor_copy = donor.copy()
            donor_copy["distance_km"] = round(distance, 2)
            results.append(donor_copy)

    results.sort(key=lambda x: x.get("distance_km", 9999))
    return results


def update_request_status(request_id, action, current_status=None, donor_id=None):
    """Update a blood request status."""
    if current_status:
        current_status = current_status.lower()

    new_status = current_status
    if current_status == "pending" and action == "accept":
        new_status = "Accepted"
    elif current_status in {"accepted", "active"} and action == "completed":
        new_status = "Deactivated"
    elif not current_status:
        new_status = action.capitalize()

    if new_status == current_status:
        print("No status change required.")
        return None

    update_data = {"status": new_status}
    if donor_id is not None:
        update_data["assigned_donor_id"] = donor_id

    try:
        response = (
            supabase.table("blood_requests")
            .update(update_data)
            .eq("id", request_id)
            .execute()
        )
        print(f"Request {request_id} updated to {new_status}.")
        return response.data
    except Exception as error:
        print(f"Database update failed: {error}")
        return None


def _run_self_test():
    test_lat = 19.0760
    test_lon = 72.8777
    test_blood = "O+"

    print("Searching for nearest donors...")
    donors = find_nearest_donors(test_lat, test_lon, test_blood)

    if donors:
        print(f"Found {len(donors)} donors")
        for donor in donors:
            name = donor.get("name")
            phone = donor.get("phone")
            distance = donor.get("distance_km")
            print(f"- {name} | {phone} | {distance} km")
    else:
        print("No matching donors found.")

    print("Updating request status for request 1...")
    update_request_status(request_id=1, current_status="active", action="completed")


if __name__ == "__main__":
    _run_self_test()