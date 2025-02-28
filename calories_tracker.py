import streamlit as st
import json
import os
import datetime

# Dateien zur Speicherung der Daten
DATA_FILE = "kalorien_data.json"
STANDARD_FILE = "standard_plan.json"
HISTORIE_FILE = "historie.json"
PASSWORD = "jonas"

# Wochentage auf Deutsch
WOCHENTAGE = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]

# Englische Namen zu deutschen Wochentagen mappen
wochentag_deutsch = {
    "Monday": "Montag",
    "Tuesday": "Dienstag",
    "Wednesday": "Mittwoch",
    "Thursday": "Donnerstag",
    "Friday": "Freitag",
    "Saturday": "Samstag",
    "Sunday": "Sonntag"
}

# Funktion zum Laden der Standardwerte
def load_standard_data():
    if os.path.exists(STANDARD_FILE):
        with open(STANDARD_FILE, "r") as file:
            return json.load(file)
    else:
        return {tag: {"Fruehstück": [], "Mittagessen": [], "Abendessen": [], "Zusatzkalorien": []} for tag in WOCHENTAGE}

# Funktion zum Laden der aktuellen Wochen-Daten
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
    else:
        data = load_standard_data()

    for tag in WOCHENTAGE:
        for category in ["Fruehstück", "Mittagessen", "Abendessen", "Zusatzkalorien"]:
            if category not in data[tag]:
                data[tag][category] = []
    
    return data

# Funktion zum Speichern der aktuellen Daten
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Funktion zum Speichern der historischen Daten
def save_to_history():
    if os.path.exists(HISTORIE_FILE):
        with open(HISTORIE_FILE, "r") as file:
            history_data = json.load(file)
    else:
        history_data = []

    today = datetime.datetime.today().strftime("%Y-%m-%d")  # Aktuelles Datum
    history_data.append({"datum": today, "daten": kalorien_data})  # Speichert aktuelle Woche

    with open(HISTORIE_FILE, "w") as file:
        json.dump(history_data, file, indent=4)

# Daten laden
kalorien_data = load_data()

st.header("🍽️ Mama's Kalorien Wochenplaner")

# Heutigen Wochentag setzen
heute = datetime.datetime.today().strftime("%A")
selected_day = st.selectbox("Wähle einen Wochentag:", WOCHENTAGE, index=WOCHENTAGE.index(wochentag_deutsch.get(heute, "Montag")))

# Mahlzeiten-Typ auswählen
meal_type = st.radio("Mahlzeit wählen:", ["Fruehstück", "Mittagessen", "Abendessen", "Zusatzkalorien"])

# Eingabe für Mahlzeit & Kalorien
meal_name = st.text_input("Gericht oder Snack eingeben:")
meal_calories = st.number_input("Kalorienzahl eingeben:", min_value=0, max_value=2000, step=1)

# Button zum Speichern der Mahlzeit oder Zusatzkalorien
if st.button("Hinzufügen"):
    if meal_name and meal_calories > 0:
        kalorien_data[selected_day][meal_type].append({"name": meal_name, "kalorien": meal_calories, "gegessen": False})
        save_data(kalorien_data)
        st.success(f"{meal_name} mit {meal_calories} kcal wurde zu {meal_type} am {selected_day} hinzugefügt!")
    else:
        st.warning("Bitte fülle alle Felder aus!")

# Mahlzeiten des gewählten Tages anzeigen
st.subheader(f"📅 Mahlzeiten & Zusatzkalorien am {selected_day}")

total_calories = 0

for meal_type, meals in kalorien_data[selected_day].items():
    if meals:
        st.write(f"**{meal_type}:**")
        for i, meal in enumerate(meals):
            checked = st.checkbox(f"{meal['name']} ({meal['kalorien']} kcal)", meal["gegessen"], key=f"{selected_day}_{meal_type}_{i}")
            if checked != meal["gegessen"]:
                kalorien_data[selected_day][meal_type][i]["gegessen"] = checked
                save_data(kalorien_data)

            if checked:
                total_calories += meal["kalorien"]
    else:
        st.write(f"**{meal_type}:** Keine Einträge")

# Tagesziel-Check (1200 kcal)
ziel_kcal = 1200
ziel_wochen_kcal = 8400
status_icon = "✅" if total_calories < ziel_kcal else "❌"
st.write(f"**🔢 Tageskalorien: {total_calories} / {ziel_kcal} kcal {status_icon}**")

# Wochenübersicht
st.subheader("📊 Wochenübersicht")
week_total = 0

for tag in WOCHENTAGE:
    day_total = sum(meal["kalorien"] for meals in kalorien_data[tag].values() for meal in meals if meal["gegessen"])
    week_total += day_total
    st.write(f"**{tag}: {day_total} kcal**")

week_status_icon = "✅" if week_total < ziel_wochen_kcal else "❌"
st.write(f"**🔢 Gesamtkalorien der Woche: {week_total} / {ziel_wochen_kcal} kcal {week_status_icon}**")

# Wochenplan zurücksetzen & historisch speichern
st.subheader("🔄 Wochenplan zurücksetzen (Automatischer Reset am Montag)")
reset_password = st.text_input("Passwort eingeben für Reset:", type="password", key="reset")

if st.button("🔴 Wochenplan zurücksetzen"):
    if reset_password == PASSWORD:
        save_to_history()  # Speichert aktuelle Woche
        standard_data = load_standard_data()  # Lädt Standardplan
        save_data(standard_data)  # Setzt Plan zurück
        st.success("Der Wochenplan wurde gespeichert und auf den Standard zurückgesetzt!")
    else:
        st.error("Falsches Passwort!")

# Historische Wochenübersicht
st.subheader("📜 Historische Wochenübersicht")

if os.path.exists(HISTORIE_FILE):
    with open(HISTORIE_FILE, "r") as file:
        history_data = json.load(file)
else:
    history_data = []

if history_data:
    for entry in reversed(history_data):  # Neueste zuerst anzeigen
        st.write(f"📅 **Woche vom {entry['datum']}**")

        total_kcal = 0  # Gesamtkalorien der Woche

        # Durchlaufe alle Wochentage
        for tag, meals in entry["daten"].items():
            for category, meal_list in meals.items():
                if isinstance(meal_list, list):  # Sicherstellen, dass es eine Liste ist
                    for meal in meal_list:
                        if isinstance(meal, dict) and "kalorien" in meal and "gegessen" in meal:
                            if meal["gegessen"]:  # Nur wenn "gegessen": true
                                total_kcal += meal["kalorien"]

        st.write(f"🔢 Gesamtkalorien: {total_kcal} kcal")
        st.write("---")
else:
    st.write("Noch keine historischen Daten gespeichert.")


