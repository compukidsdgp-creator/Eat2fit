import streamlit as st
from geopy.distance import geodesic
import folium
from streamlit_folium import st_folium
 
import csv
from datetime import date

# ---------------- SESSION ----------------
if "show_result" not in st.session_state:
    st.session_state.show_result = False

# ---------------- TITLE ----------------
st.title("🏥 Nearest Nutrition Clinic Finder")

# ---------------- USER LOCATIONS ----------------
locations = {
    # ---------------- ASANSOL BELT ----------------
    "Asansol": (23.6739, 86.9524),
    "Burnpur": (23.6667, 86.9333),
    "Raniganj": (23.6236, 87.1306),
    "Andal": (23.5833, 87.2000),

    # ---------------- DURGAPUR BELT ----------------
    "Durgapur": (23.5204, 87.3119),
    "Panagarh": (23.4500, 87.4333),
    "Kanksa": (23.4200, 87.3500),

    # ---------------- BANKURA ----------------
    "Bankura": (23.2320, 87.0780),
    "Bishnupur": (23.0730, 87.3190),
    "Sonamukhi": (23.3040, 87.4170),
    "Indpur": (23.1700, 86.9700),

    # ---------------- PURULIA ----------------
    "Purulia": (23.3320, 86.3650),
    "Raghunathpur": (23.5500, 86.6700),
    "Adra": (23.4950, 86.6830),
    "Jhalda": (23.3700, 85.9800),

    # ---------------- BIRBHUM ----------------
    "Bolpur (Shantiniketan)": (23.6700, 87.6800),
    "Suri": (23.9100, 87.5300),
    "Rampurhat": (24.1800, 87.7800),

    # ---------------- BARDHAMAN TO KOLKATA ----------------
    "Bud Bud": (23.4000, 87.5167),
    "Galsi": (23.3000, 87.7167),
    "Bardhaman": (23.2324, 87.8615),
    "Memari": (23.2000, 88.1000),
    "Palsit": (23.1500, 88.2000),
    "Dankuni": (22.6800, 88.3000),
    "Howrah": (22.5958, 88.2636),
    "Kolkata": (22.5726, 88.3639)
}

# ---------------- CLINICS ----------------
clinics = [
    {"name": "Aloka Medicare", "coords": (22.5257, 88.3525), "address": "Sarat Bose Road, Kolkata", "contact": "+91 9609222208", "services": "Weight Loss, Diet Plan"},
    {"name": "Hope Nursing Home", "coords": (23.6236, 87.1306), "address": "Raniganj", "contact": "+91 9609222208", "services": "Diabetes Diet"},
    {"name": "Aviskar Diagnostic", "coords": (23.5500, 87.2900), "address": "Durgapur", "contact": "+91 9609222208", "services": "Fitness Diet"},
    {"name": "Prayas Foundation", "coords": (23.5450, 87.2950), "address": "Durgapur", "contact": "+91 9609222208", "services": "Kids Diet"},
    {"name": "Life Support Medical", "coords": (23.5405, 87.2955), "address": "Durgapur", "contact": "+91 9609222208", "services": "General Nutrition"},
    {"name": "Meditree Pharma", "coords": (23.6820, 86.9750), "address": "Asansol", "contact": "+91 9609222208", "services": "Nutrition"},
    {"name": "Annapurna Medical Hall", "coords": (23.6880, 86.9800), "address": "Asansol", "contact": "+91 9609222208", "services": "Diet Plan"},
    {"name": "Hill View Hospital", "coords": (23.6895, 86.9835), "address": "Asansol", "contact": "+91 9609222208", "services": "General Care"}
]

# ---------------- FORM ----------------
with st.form("form"):
    selected_location = st.selectbox("Select your location", list(locations.keys()))
    submit = st.form_submit_button("Find Nearest Clinic")

# ---------------- STORE ----------------
if submit:
    st.session_state.location = selected_location
    st.session_state.show_result = True

# ---------------- MAIN LOGIC ----------------
if st.session_state.show_result:

    user_coords = locations[st.session_state.location]

    results = []

    # ---------------- MAP ----------------
    m = folium.Map(location=user_coords, zoom_start=9)

    # User marker
    folium.Marker(
        user_coords,
        tooltip="Your Location",
        icon=folium.Icon(color="blue")
    ).add_to(m)

    # ---------------- DISTANCE ----------------
    for clinic in clinics:

        distance = geodesic(user_coords, clinic["coords"]).km
        clinic["distance"] = round(distance, 2)

        results.append(clinic)

        # Marker
        folium.Marker(
            clinic["coords"],
            tooltip=f"{clinic['name']} ({clinic['distance']} km)",
            icon=folium.Icon(color="green")
        ).add_to(m)

    # 🔥 CONNECTING LINE
    folium.PolyLine(
        locations=[user_coords, clinic["coords"]],
        color="blue",
        weight=2,
        opacity=0.6
    ).add_to(m)

    # Sort
    results = sorted(results, key=lambda x: x["distance"])
    nearest = results[0]

    # ---------------- OUTPUT ----------------
    st.subheader("🏆 Nearest Clinic")
    st.success(f"{nearest['name']} ({nearest['distance']} km away)")

    st.write("📍 Address:", nearest["address"])
    st.write("📞 Contact:", nearest["contact"])
    st.write("💼 Services:", nearest["services"])

    import csv

# ---------------- BOOK BUTTON ----------------
if st.button("📅 Book Appointment", key="book_btn"):

    st.session_state.show_form = True

# ---------------- SHOW FORM ----------------
if "show_form" in st.session_state and st.session_state.show_form:

    st.subheader("📝 Enter Your Details")

    with st.form("lead_form"):
        name = st.text_input("Patient Name")
        phone = st.text_input("Phone Number")

        submit_lead = st.form_submit_button("Proceed")

    # ---------------- AFTER SUBMIT ----------------
    if submit_lead:

        if name == "" or phone == "":
            st.error("Please fill all details")
        else:
            # Save to CSV
            with open("leads.csv", "a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow([
                    name,
                    phone,
                    nearest["name"],
                    nearest["address"]
                ])

            st.success("✅ Details Saved! Now contact clinic below 👇")

            # Store state
            st.session_state.lead_submitted = True
            st.session_state.name = name

# ---------------- SHOW CONTACT OPTIONS ----------------
if "lead_submitted" in st.session_state and st.session_state.lead_submitted:

    st.subheader("📞 Contact Clinic")

    # CALL BUTTON (clickable)
    phone = nearest["contact"]
    name = st.session_state.get("name", "Patient")

    # WhatsApp message
    message = f"Hello, I am {name}. I would like to consult at {nearest['name']}."
    whatsapp_url = f"https://wa.me/{phone}?text={message}"

    # ---------------- BUTTON STYLE ----------------
    st.markdown(f"""
    <div style="display:flex; gap:20px;">

    <a href="tel:{phone}">
        <button style="
            background-color:#28a745;
            color:white;
            padding:12px 20px;
            border:none;
            border-radius:8px;
            font-size:16px;
            cursor:pointer;">
            📞 Call Now
        </button>
    </a>

    <a href="{whatsapp_url}" target="_blank">
        <button style="
            background-color:#25D366;
            color:white;
            padding:12px 20px;
            border:none;
            border-radius:8px;
            font-size:16px;
            cursor:pointer;">
            💬 WhatsApp
        </button>
    </a>

    </div>
    """, unsafe_allow_html=True)

    

    st.balloons()

    # ---------------- ALL CLINICS ----------------
    st.subheader("📊 All Clinics Distance")
    for r in results:
        st.write(f"{r['name']} → {r['distance']} km")

    # ---------------- MAP ----------------
    st.subheader("🗺️ Clinic Map")
    st_folium(m, width=700, height=500)
 


