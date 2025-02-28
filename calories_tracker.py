import streamlit as st
import json
import os
import datetime

# Datei zur Speicherung der Daten
DATA_FILE = "kalorien_data.json"
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

# Funktion zum Laden der Daten
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
    else:
        data = {tag: {"Frühstück": [], "Mittagessen": [], "Abendessen": [], "Zusatzkalorien": []} for tag in WOCHENTAGE}

    # Sicherstellen, dass jeder Wochentag alle Kategorien hat
    for tag in WOCHENTAGE:
        for category in ["Frühstück", "Mittagessen", "Abendessen", "Zusatzkalorien"]:
            if category not in data[tag]:
                data[tag][category] = []

    return data

# Funktion zum Speichern der Daten
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Daten laden
kalorien_data = load_data()

st.header("Mama's Kalorien Wochenplaner")

# Heutigen Wochentag setzen
heute = datetime.datetime.today().strftime("%A")
selected_day = st.selectbox("Wähle einen Wochentag:", WOCHENTAGE, index=WOCHENTAGE.index(wochentag_deutsch.get(heute, "Montag")))

# Mahlzeiten-Typ auswählen
meal_type = st.radio("Mahlzeit wählen:", ["Frühstück", "Mittagessen", "Abendessen", "Zusatzkalorien"])

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

            # Nur gezählte Mahlzeiten zur Tagesbilanz addieren
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
    day_total = 0
    for meals in kalorien_data[tag].values():
        if isinstance(meals, list):
            day_total += sum(meal["kalorien"] for meal in meals if meal["gegessen"])
    
    week_total += day_total
    st.write(f"**{tag}: {day_total} kcal**")

# Wochenziel-Check
week_status_icon = "✅" if week_total < ziel_wochen_kcal else "❌"
st.write(f"**🔢 Gesamtkalorien der Woche: {week_total} / {ziel_wochen_kcal} kcal {week_status_icon}**")

# Einzelne Mahlzeit löschen (mit Passwort)
st.subheader("❌ Einzelne Mahlzeit oder Zusatzkalorie löschen")
meal_to_delete = st.selectbox("Wähle eine Mahlzeit zum Löschen:", [meal["name"] for meals in kalorien_data[selected_day].values() if isinstance(meals, list) for meal in meals])
delete_password = st.text_input("Passwort eingeben:", type="password")

if st.button("Mahlzeit löschen"):
    if delete_password == PASSWORD:
        for meal_type in ["Frühstück", "Mittagessen", "Abendessen", "Zusatzkalorien"]:
            kalorien_data[selected_day][meal_type] = [meal for meal in kalorien_data[selected_day][meal_type] if meal["name"] != meal_to_delete]
        save_data(kalorien_data)
        st.success(f"Mahlzeit '{meal_to_delete}' gelöscht!")
    else:
        st.error("Falsches Passwort!")

# Gesamten Plan zurücksetzen (mit Passwort)
st.subheader("🔄 Gesamten Wochenplan zurücksetzen")
reset_password = st.text_input("Passwort eingeben für Reset:", type="password", key="reset")

if st.button("🔴 Wochenplan zurücksetzen"):
    if reset_password == PASSWORD:
        kalorien_data = {tag: {"Frühstück": [], "Mittagessen": [], "Abendessen": [], "Zusatzkalorien": []} for tag in WOCHENTAGE}
        save_data(kalorien_data)
        st.success("Alle Einträge wurden zurückgesetzt!")
    else:
        st.error("Falsches Passwort!")
