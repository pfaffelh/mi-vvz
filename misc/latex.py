import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import pymongo
import time
import misc.util as util
from bson import ObjectId
from misc.config import *
from collections import OrderedDict
import jinja2
import os

def getraum(raum_id, lang = "de"):
    r = util.raum.find_one({ "_id": raum_id})
    g = util.gebaeude.find_one({ "_id": r["gebaeude"]})
    return ", ".join([r[f"name_{lang}"], g[f"name_{lang}"]])

def makemodulname(modul_id, lang = "de", alter = True):
    otherlang = "de" if "lang" == "en" else "en"
    m = util.modul.find_one({"_id": modul_id})
    mname = m[f"name_{lang}"]
    if alter and mname == "":
        mname = m[f"name_{otherlang}"]    
    s = ", ".join([x["kurzname"] for x in list(util.studiengang.find({"_id": { "$in" : m["studiengang"]}, "semester" : { "$elemMatch" : { "$eq" : st.session_state.semester_id}}}))])
    return f"{mname} ({s})"

def makeanforderungname(anforderung_id, lang = "de", alter = True):
    otherlang = "de" if "lang" == "en" else "en"
    a = util.anforderung.find_one({"_id": anforderung_id})
    aname = a[f"name_{lang}"]
    if alter and aname == "":
        aname = a[f"name_{otherlang}"]
    k = util.anforderungkategorie.find_one({ "_id": a["anforderungskategorie"]})[f"name_{lang}"]
    if alter and k == "":
        k = util.anforderungkategorie.find_one({ "_id": a["anforderungskategorie"]})[f"name_{otherlang}"]
    return f"{aname} ({k})"

def makeverwendbarkeit(verwendbarkeit):
    res = [{"modul": str(x["modul"]), "anforderung": str(x["anforderung"])} for x in verwendbarkeit]
    return res

# Die Funktion fasst zB Mo, 8-10, HS Rundbau, Albertstr. 21 \n Mi, 8-10, HS Rundbau, Albertstr. 21 \n 
# zusammen in
# Mo, Mi, 8-10, HS Rundbau, Albertstr. 21 \n Mi, 8-10, HS Rundbau, Albertstr. 21
def make_raumzeit(veranstaltung, lang="de"):
    res = []
    for termin in veranstaltung["woechentlicher_termin"]:
        ta = util.terminart.find_one({"_id": termin['key']})
        if ta["hp_sichtbar"]:
            ta = ta[f"name_{lang}"]
            if termin['wochentag'] !="":
                # key, raum, zeit, person, kommentar
                key = f"{ta}:" if ta != "" else ""
                # Raum und Gebäude mit Url, zB Hs II.
                r = util.raum.find_one({ "_id": termin["raum"]})                
                raum = getraum(r["_id"], lang)
                # zB Vorlesung: Montag, 8-10 Uhr, HSII, Albertstr. 23a
                if termin['start'] is not None:
                    zeit = f"{str(termin['start'].hour)}{': '+str(termin['start'].minute) if termin['start'].minute > 0 else ''}"
                    if termin['ende'] is not None:
                        zeit = zeit + f"-{str(termin['ende'].hour)}{': '+str(termin['ende'].minute) if termin['ende'].minute > 0 else ''}"
                    zeit = zeit + (" Uhr" if lang == "de" else " h")
                else:
                    zeit = ""
                # zB Mo, 8-10
                tag = util.wochentag[termin['wochentag']][lang]
                # person braucht man, wenn wir dann die Datenbank geupdated haben.
                #person = ", ".join([f"{util.person.find_one({"_id": x})["vorname"]} {util.person.find_one({"_id": x})["name"]}"for x in termin["person"]])
                kommentar = rf"\newline{termin['kommentar']}" if termin['kommentar'] != "" else ""
                new = [key, tag, zeit, raum, kommentar]
                if key in [x[0] for x in res]:
                    new.pop(0)
                    i = [x[0] for x in res].index(key)
                    res[i] = (res[i] + new)
                    res[i].reverse()
                    res[i] = list(OrderedDict.fromkeys(res[i]))
                    res[i].reverse()
                else:
                    res.append(new)
    for termin in veranstaltung["einmaliger_termin"]:
        ta = util.terminart.find_one({"_id": termin['key']})
        if ta["hp_sichtbar"]:
            ta = ta[f"name_{lang}"]
            # Raum und Gebäude mit Url.
            raeume = list(util.raum.find({ "_id": { "$in": termin["raum"]}}))
            raum = ", ".join([getraum(r["_id"], lang) for r in raeume])
            # zB Vorlesung: Montag, 8-10, HSII, Albertstr. 23a
            if termin['enddatum'] is None:
                termin['enddatum'] = termin['startdatum']
            if termin['startdatum'] is not None:
                startdatum = termin['startdatum'].strftime("%d.%m.")
                if termin['startdatum'] != termin['enddatum']:
                    enddatum = termin['enddatum'].strftime("%d.%m.")
                    datum = " bis ".join([startdatum, enddatum]) if startdatum != enddatum else startdatum
                else:
                    datum = startdatum
            else:
                datum = ""
            if termin['startzeit'] is not None:
                zeit = f"{str(termin['startzeit'].hour)}{': '+str(termin['startzeit'].minute) if termin['startzeit'].minute > 0 else ''}"
                if termin['endzeit'] is not None:
                    zeit = zeit + f"-{str(termin['endzeit'].hour)}{': '+str(termin['endzeit'].minute) if termin['endzeit'].minute > 0 else ''}"
                zeit = zeit + (" Uhr" if lang == "de" else " h")
            else:
                zeit = ""
            # person braucht man, wenn wir dann die Datenbank geupdated haben.
            # person = ", ".join([f"{util.person.find_one({"_id": x})["vorname"]} {util.person.find_one({"_id": x})["name"]}"for x in termin["person"]])
            kommentar = rf"{termin['kommentar']}" if termin['kommentar'] != "" else ""
            new = [ta, datum, zeit, raum, kommentar]
            res.append(new)
    res = [f"{x[0]} {(', '.join([z for z in x if z !='' and x.index(z)!=0]))}" for x in res]
    return res

def makedata(sem_kurzname, komm_id, lang, alter):
    sem_id = util.semester.find_one({"kurzname": sem_kurzname})["_id"]
    otherlang = "en" if lang == "de" else "de"

    rubriken = list(util.rubrik.find({"semester": sem_id, "hp_sichtbar": True}, sort=[("rang", pymongo.ASCENDING)]))

    data = {}
    data["rubriken"] = []

    for rubrik in rubriken:
        r_dict = {}

        r_dict["titel"] = rubrik[f"titel_{lang}"] 
        if alter and r_dict["titel"] == "":
            r_dict["titel"] = rubrik[f"titel_{otherlang}"]

        r_dict["veranstaltung"] = []
        veranstaltungen = list(util.veranstaltung.find({"rubrik": rubrik["_id"], "code" : { "$elemMatch" : { "$eq" : komm_id }}}))
        for veranstaltung in veranstaltungen:
            v_dict = {}

            v_dict["titel"] = veranstaltung[f"name_{lang}"]
            if alter and v_dict["titel"] == "":
                v_dict["titel"] = veranstaltung[f"name_{otherlang}"]

            v_dict["dozent"] = ", ".join([f"{util.person.find_one({'_id': x})['vorname']} {util.person.find_one({'_id': x})['name']}"for x in veranstaltung["dozent"]])

            assistent = ", ".join([f"{util.person.find_one({'_id': x})['vorname']} {util.person.find_one({'_id': x})['name']}"for x in veranstaltung["assistent"]])
            if assistent:
                if lang == "de":
                    v_dict["person"] = ", Assistenz: ".join([v_dict["dozent"], assistent])
                else:
                    v_dict["person"] = ", Assistant: ".join([v_dict["dozent"], assistent])
            else:
                v_dict["person"] = v_dict["dozent"]
            # raumzeit ist der Text, der unter der Veranstaltung im kommentierten VVZ steht.

            v_dict["raumzeit"] = make_raumzeit(veranstaltung, lang = lang)

            v_dict["inhalt"] = veranstaltung[f"inhalt_{lang}"]
            if alter and v_dict["inhalt"] == "":
                v_dict["inhalt"] = veranstaltung[f"inhalt_{otherlang}"]
            
            v_dict["literatur"] = veranstaltung[f"literatur_{lang}"]
            if alter and v_dict["literatur"] == "":
                v_dict["literatur"] = veranstaltung[f"literatur_{otherlang}"]
            
            v_dict["vorkenntnisse"] = veranstaltung[f"vorkenntnisse_{lang}"]
            if alter and v_dict["vorkenntnisse"] == "":
                v_dict["vorkenntnisse"] = veranstaltung[f"vorkenntnisse_{otherlang}"]

            v_dict["kommentar"] = veranstaltung[f"kommentar_latex_{lang}"]
            if alter and v_dict["kommentar"] == "":
                v_dict["kommentar"] = veranstaltung[f"kommentar_latex_{otherlang}"]

            v_dict["verwendbarkeit_modul"] = [{"id": str(x), "titel": makemodulname(x, lang, alter)} for x in veranstaltung["verwendbarkeit_modul"]]
            v_dict["verwendbarkeit_anforderung"] = [{"id": str(x), "titel": makeanforderungname(x, lang, alter)} for x in veranstaltung["verwendbarkeit_anforderung"]]
            v_dict["verwendbarkeit"] = [{"modul": str(x["modul"]), "anforderung": str(x["anforderung"])} for x in veranstaltung["verwendbarkeit"]]

            # Spalten zusammenfassen:
            # rm = []
            # for i in range(1,len(v_dict["verwendbarkeit_modul"])):
            #     x = v_dict["verwendbarkeit_modul"][i]
            #     xanforderungen = [(value for key, value in z if key == "anforderung") for z in v_dict["verwendbarkeit"] if z["modul"] == x["id"]]
            #     for j in range(i, len(v_dict["verwendbarkeit_modul"])):
            #         y = v_dict["verwendbarkeit_modul"][j]
            #         yanforderungen = [(value for key, value in z if key == "anforderung") for z in v_dict["verwendbarkeit"] if z["modul"] == y["id"]]
            #         if x != y and set(xanforderungen) == set(yanforderungen):
            #             x["titel"] = ", ".join([x["titel"], y["titel"]])
            #             rm.append(j)
            # rm.reverse
            # for j in rm:
            #     v_dict["verwendbarkeit_modul"].pop(j)

            r_dict["veranstaltung"].append(v_dict)

        # Rubrik nur dann hinzufügen, wenn hier auch Veranstaltungen sind
        if veranstaltungen:
            data["rubriken"].append(r_dict)
    return data

# Für die Kommentare:
# Momentan gibt es so etwas wie: '4-stündige Vorlesung mit 2-stündiger Übung' oder 'Vorlesung mit Praktischer Übung', was jeweils direkt unter der Veranstaltung selbst steht. Ist das wichtig (dann muss es als Feld ins vvz) oder nicht?
# Ein wöchentlicher Termin wird nur dann angezeigt wenn er einen Wochentag hat. Wenn er einen Wochentag hat, wird davon ausgegangen, dass er auch eine Uhrzeit hat.
# 8:00 wird als 8 ausgegeben, aber 8:15 als 8:15. 
# Braucht einmaliger_termin noch eine true/false-Variable, je nachdem ob er in den Kommentaren auftauchen soll? 

latex_jinja_env = jinja2.Environment(
    block_start_string = '\BLOCK{',
    block_end_string = '}',
    variable_start_string = '\VAR{',
    variable_end_string = '}',
    comment_start_string = '\#{',
    comment_end_string = '}',
    line_statement_prefix = '%%',
    line_comment_prefix = '%#',
    trim_blocks = True,
    autoescape = False,
    loader = jinja2.FileSystemLoader(os.path.abspath('.'))
)
