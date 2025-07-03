import requests
from datetime import timedelta
from icalendar import Calendar, Event

# 1) Quelle: bestehender iCal-Feed für NRW-Schulferien
SOURCE_URL = "https://www.feiertage-deutschland.de/kalender-download/ics/schulferien-nordrhein-westfalen.ics"

# 2) Emoji-Mapping
EMOJI = {
    "Osterferien":      "🥚 Osterferien",
    "Sommerferien":     "☀️ Sommerferien",
    "Herbstferien":     "🍂 Herbstferien",
    "Weihnachtsferien": "❄️ Weihnachtsferien",
}

def fetch_and_transform():
    # Feed herunterladen
    resp = requests.get(SOURCE_URL)
    resp.raise_for_status()
    cal = Calendar.from_ical(resp.text)

    # Neue Kalender-Instanz mit Metadaten
    new_cal = Calendar()
    for name, value in cal.property_items():
        new_cal.add(name, value)

    # Veranstaltungen anpassen
    for comp in cal.walk():
        if comp.name != "VEVENT":
            continue
        ev = Event()
        # 3) Titel mit Emoji
        orig = str(comp.get("SUMMARY"))
        ev.add("SUMMARY", EMOJI.get(orig, orig))
        # 4) DTSTART (original) übernehmen
        dtstart = comp.decoded("DTSTART")
        ev.add("DTSTART", dtstart)
        # 5) DTEND um einen Tag kürzen
        dtend = comp.decoded("DTEND") - timedelta(days=1)
        ev.add("DTEND", dtend)
        # UID und Klassifizierung übernehmen
        for prop in ("UID","DESCRIPTION","CLASS"):
            if comp.get(prop):
                ev.add(prop, comp.get(prop))
        new_cal.add_component(ev)

    return new_cal.to_ical().decode()

if __name__ == "__main__":
    print(fetch_and_transform())

