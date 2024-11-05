from pymongo import MongoClient
import pymongo
from dateutil.relativedelta import relativedelta
import os
import datetime
import json
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]

sem = mongo_db["semester"]
per = mongo_db["person"]
ver = mongo_db["veranstaltung"]
anf = mongo_db["anforderung"]
dic = mongo_db["dictionary"]
ter = mongo_db["terminart"]

import schema20241105
mongo_db.command('collMod','person', validator=schema20241105.person_validator, validationLevel='off')

# Ab hier wird die Datenbank verändert
print("Ab hier wird verändert")

# Bei Person und Anforderung die Liste der Semester sortieren
for p in per.find():
    se = list(sem.find({"_id": {"$in": p["semester"]}}, sort=[("rang", pymongo.ASCENDING)]))
    per.update_one({"_id" : p["_id"]}, { "$set" : { "semester" :[s["_id"] for s in se] }})

for a in anf.find():
    se = list(sem.find({"_id": {"$in": a["semester"]}}, sort=[("rang", pymongo.ASCENDING)]))
    anf.update_one({"_id" : a["_id"]}, { "$set" : { "semester" :[s["_id"] for s in se] }})

# dictionary löschen
dic.drop()

# terminart braucht eine Variable "Im Prüfungskalender sichtbar"

ter.update_many({}, {"$set" : {"cal_sichtbar" : False}})
for t in list(ter.find()):
    if "lausur" in t["name_de"]:
        ter.update_one({ "_id": t["_id"]}, {"$set" : {"cal_sichtbar" : True}})

ter.update_one({"name_de" : ""}, {"$set" : {"cal_sichtbar" : True}})

# calendar auslesen und eintragen
import caldav
from datetime import datetime
from dateutil.relativedelta import relativedelta
import netrc

netrc = netrc.netrc()

calendar_host = "cal.mathematik.privat/davical/caldav.php/"
cal_username, cal_account, cal_password = netrc.authenticators(calendar_host)
sondertermine_lehre_calendar_url = "http://cal.mathematik.privat/davical/caldav.php/pruefungsamt/pramt/"

# Das ist der Prüfungsamts-Kalender
url_prefix = "http://" + calendar_host
calendar = (url_prefix, cal_username, cal_password, sondertermine_lehre_calendar_url)

def remove_p_tags(text):
    text = text.replace("<p>", "")
    text = text.replace("</p>", "")
    return text


def get_caldav_calendar_events(cal, yearsinthepast=10):
    # Define the calendar
    client = caldav.DAVClient(url = cal[0], username = cal[1], password = cal[2])
    calendar = client.calendar(url = cal[3])

    # This will determine what past and future events are being displayed
    datetime_today  = datetime.combine(datetime.today(), datetime.min.time())
    datetime_start = datetime_today - relativedelta(years=yearsinthepast)

    ### Main for calendar from above
    all=[]
    try:
        events = calendar.date_search(start = datetime_start, end = None)
        for event in events:
            e = event.instance.vevent

            # set start time of event, and determine if it is allDay
            try:
                start_time = e.dtstart.value
            except:
#                logger.INFO("Es kann weder Datum noch Startzeit erkannt werden. Das Event wird übersprungen.")
                continue  # Überspringe Veranstaltungen, die weder Startdatum noch Startzeit haben.
            end = start = e.dtstart.value.strftime("%Y-%m-%d %H:%M:00")
            allDay = ("true" if e.dtstart.value.strftime("%H:%M") == "00:00" else "false")

            # determine end time of event
            try:
                end = e.dtend.value.strftime("%Y-%m-%d %H:%M:00")
            except:
                continue # Wenn kein Ende festgelegt ist und der Termin nicht ganztägig ist, ist die Dauer 0h

            # summary + location + description will give the title of the calendar entry
            try:
                summary= e.summary.value
            except:
                summary = ""
            try:
                location = e.location.value
            except:
                location = ""                    
            try:
                description = e.description.value
            except:
                description = ""

            title = summary + ((", " + location) if location != "" else "") + ((", " + description) if description != "" else "")
            title = remove_p_tags(title.replace("\n", ", "))
            # append all events for display in calendar    
            all.append({
                "start": start,
                "end": end,
                "allDay": allDay,
                "title": title
            })

    except Exception as e:
        # Log the error to a file
        error_message = f"Error accessing the calendar at {cal[3]}: {str(e)}"
        #logger.error(error_message)

    return all

all = get_caldav_calendar_events(calendar, yearsinthepast=10)
for a in all:
    print(a)

ta = ter.find_one({ "name_de" : ""})["_id"]
for a in all:
    t = {   "key": ta,
            "raum": [],
            "person": [],
            # wochentag muss so gespeichert werden, um das schema nicht zu verletzen.
            "startdatum": datetime.strptime(a["start"], '%Y-%m-%d %H:%M:%S'),
            "startzeit": datetime.strptime(a["start"], '%Y-%m-%d %H:%M:%S'),
            "enddatum": datetime.strptime(a["end"], '%Y-%m-%d %H:%M:%S'),
            "endzeit": datetime.strptime(a["end"], '%Y-%m-%d %H:%M:%S'),
            "kommentar_de_latex": "",
            "kommentar_en_latex": "",
            "kommentar_de_html": a["title"],
            "kommentar_en_html": ""}
    ver.update_one({"kurzname" : "exam"}, {"$push" : { "einmaliger_termin" : t}})



# Ab hier wird das Schema gecheckt
print("Check schema")
mongo_db.command('collMod','person', validator=schema20241105.person_validator, validationLevel='moderate')

ver.create_index( [ ("name_de", pymongo.TEXT), ("name_en", pymongo.TEXT)], default_language ="german")
