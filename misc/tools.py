import streamlit as st
from streamlit_extras.switch_page_button import switch_page 
import pymongo
import time
import ldap
import misc.util as util
from bson import ObjectId
from misc.config import *
from datetime import datetime

def move_up(collection, x, query = {}):
    query["rang"] = {"$lt": x["rang"]}
    target = collection.find_one(query, sort = [("rang",pymongo.DESCENDING)])
    if target:
        n= target["rang"]
        collection.update_one({"_id": target["_id"]}, {"$set": {"rang": x["rang"]}})    
        collection.update_one({"_id": x["_id"]}, {"$set": {"rang": n}})    

def move_down(collection, x, query = {}):
    query["rang"] = {"$gt": x["rang"]}
    target = collection.find_one(query, sort = [("rang", pymongo.ASCENDING)])
    if target:
        n= target["rang"]
        collection.update_one({"_id": target["_id"]}, {"$set": {"rang": x["rang"]}})    
        collection.update_one({"_id": x["_id"]}, {"$set": {"rang": n}})    

def move_up_list(collection, id, field, element):
    list = collection.find_one({"_id": id})[field]
    i = list.index(element)
    if i > 0:
        x = list[i-1]
        list[i-1] = element
        list[i] = x
    collection.update_one({"_id": id}, { "$set": {field: list}})

def move_down_list(collection, id, field, element):
    list = collection.find_one({"_id": id})[field]
    i = list.index(element)
    if i+1 < len(list):
        x = list[i+1]
        list[i+1] = element
        list[i] = x
    collection.update_one({"_id": id}, { "$set": {field: list}})

def remove_from_list(collection, id, field, element):
    collection.update_one({"_id": id}, {"$pull": {field: element}})

def update_confirm(collection, x, x_updated, reset = True):
    util.logger.info(f"User {st.session_state.user} hat in {util.collection_name[collection]} Item {repr(collection, x['_id'])} geändert.")
    collection.update_one({"_id" : x["_id"]}, {"$set": x_updated })
    if reset:
        reset_vars("")
    st.toast("🎉 Erfolgreich geändert!")

def new(collection, ini = {}, switch = True):
    if list(collection.find({ "rang" : { "$exists": True }})) != []:
        z = list(collection.find(sort = [("rang", pymongo.ASCENDING)]))
        rang = z[0]["rang"]-1
        util.new[collection]["rang"] = rang    
    for key, value in ini.items():
        util.new[collection][key] = value
    util.new[collection].pop("_id", None)
    # print(util.new[collection])
    x = collection.insert_one(util.new[collection])
    st.session_state.edit=x.inserted_id
    util.logger.info(f"User {st.session_state.user} hat in {util.collection_name[collection]} ein neues Item angelegt.")
    if switch:
        switch_page(f"{util.collection_name[collection].lower()} edit")


# Finde in collection.field die id, und gebe im Datensatz return_field zurück. Falls list=True,
# dann ist collection.field ein array.
def references(collection, field, list = False):    
    res = {}
    for x in util.abhaengigkeit[collection]:
        res = res | { collection: references(x["collection"], x["field"], x["list"]) } 
    if list:
        z = list(collection.find({field: {"$elemMatch": {"$eq": id}}}))
    else:
        z = list(collection.find({field: id}))
        res = {collection: [t["_id"] for t in z]}
    return res

# Finde in collection.field die id, und gebe im Datensatz return_field zurück. Falls list=True,
# dann ist collection.field ein array.
def find_dependent_items(collection, id):
    res = []
    for x in util.abhaengigkeit[collection]:
        if x["list"]:
            for y in list(x["collection"].find({x["field"].replace(".$",""): { "$elemMatch": { "$eq": id }}})):
                res.append(repr(x["collection"], y["_id"]))
        else:
            for y in list(x["collection"].find({x["field"]: id})):
                res.append(repr(x["collection"], y["_id"]))
    return res

# Finde in collection.field die id, und gebe im Datensatz return_field zurück. Falls list=True,
# dann ist collection.field ein array.
def find_dependent_veranstaltung(collection, id):
    res = []
    for x in util.abhaengigkeit[collection]:
        if x["collection"] == util.veranstaltung:
            if x["list"]:
                for y in list(x["collection"].find({x["field"].replace(".$",""): { "$elemMatch": { "$eq": id }}})):
                    res.append(y["_id"])
            else:
                for y in list(x["collection"].find({x["field"]: id})):
                    res.append(y["_id"])
    return res

def delete_item_update_dependent_items(collection, id, switch = True):
    if collection in util.leer.keys() and id == util.leer[collection]:
            st.toast("Fehler! Dieses Item kann nicht gelöscht werden!")
            reset_vars("")
    else:
        for x in util.abhaengigkeit[collection]:
            if x["list"]:
                x["collection"].update_many({x["field"].replace(".$",""): { "$elemMatch": { "$eq": id }}}, {"$pull": { x["field"] : id}})
            else:
                st.write(util.collection_name[x["collection"]])
                x["collection"].update_many({x["field"]: id}, { "$set": { x["field"].replace(".", ".$."): util.leer[collection]}})             
        s = ("  \n".join(find_dependent_items(collection, id)))
        if s:
            s = f"\n{s}  \ngeändert."
        util.logger.info(f"User {st.session_state.user} hat in {util.collection_name[collection]} item {repr(collection, id)} gelöscht, und abhängige Felder geändert.")
        collection.delete_one({"_id": id})
        reset_vars("")
        st.success(f"🎉 Erfolgreich gelöscht!  {s}")
        time.sleep(4)
        if switch:
            switch_page(util.collection_name[collection].lower())

def kopiere_veranstaltung_confirm(id, kop_sem_id, kopiere_personen, kopiere_termine, kopiere_kommVVZ, kopiere_verwendbarkeit):
    w_id = kopiere_veranstaltung(id, kop_sem_id, kopiere_personen, kopiere_termine, kopiere_kommVVZ, kopiere_verwendbarkeit)
    st.success("Erfolgreich kopiert!")
    time.sleep(2)
    st.session_state.semester_id = kop_sem_id
    st.session_state.edit = w_id

# id ist die id der zu kopierenden Veranstaltung, sem_id die id des Semesters, in das kopiert werden soll.
def kopiere_veranstaltung(id, sem_id, kopiere_personen, kopiere_termine, kopiere_kommVVZ, kopiere_verwendbarkeit):
    v = util.veranstaltung.find_one({"_id": id})
    if v["semester"] == sem_id:
        k = v["rubrik"] 
    else:
        # Wenn es die Rubrik im eigenen Semester auch gibt, dann dahin kopieren, ansonsten in leere Rubrik
        try: 
            r = util.rubrik.find_one({"_id": v["rubrik"]})
            k = util.rubrik.find_one({"semester": sem_id, "titel_de": r["titel_de"]})["_id"]
        except:
            k = util.rubrik.find_one({"semester": sem_id, "titel_de": "-"})["_id"]
    # Das wird der Rang der kopierten Veranstaltung
    try:
        r = util.veranstaltung.find_one({"semester": sem_id}, sort = [("rang",pymongo.DESCENDING)])["rang"] + 1
    except:
        r = 0
    v_new = {
        "kurzname": v["kurzname"],
        "name_de": v["name_de"],
        "name_en": v["name_en"],
        "midname_de": v["midname_de"],
        "midname_en": v["midname_en"],
        "ects": v["ects"],
        "url": "",
        "semester": sem_id,
        "rubrik": k,
        "code": v["code"] if v["semester"] == sem_id else [],
        "rang": r,
        "kommentar_html_de": v["kommentar_html_de"],
        "kommentar_html_en": v["kommentar_html_en"],
        "inhalt_de": v["inhalt_de"] if kopiere_kommVVZ else "",
        "inhalt_en":  v["inhalt_en"] if kopiere_kommVVZ else "",
        "literatur_de": v["literatur_de"] if kopiere_kommVVZ else "", 
        "literatur_en":  v["literatur_en"] if kopiere_kommVVZ else "",
        "vorkenntnisse_de": v["vorkenntnisse_de"] if kopiere_kommVVZ else "",
        "vorkenntnisse_en": v["vorkenntnisse_en"] if kopiere_kommVVZ else "",
        "kommentar_latex_de": v["kommentar_latex_de"] if kopiere_kommVVZ else "",
        "kommentar_latex_en": v["kommentar_latex_en"] if kopiere_kommVVZ else "",
        "verwendbarkeit_modul": v["verwendbarkeit_modul"] if kopiere_verwendbarkeit else [],
        "verwendbarkeit_anforderung": v["verwendbarkeit_anforderung"] if kopiere_verwendbarkeit else [],
        "verwendbarkeit": v["verwendbarkeit"] if kopiere_verwendbarkeit else [], 
        "kommentar_verwendbarkeit_de": v["kommentar_verwendbarkeit_de"] if kopiere_verwendbarkeit else "", 
        "kommentar_verwendbarkeit_en": v["kommentar_verwendbarkeit_en"] if kopiere_verwendbarkeit else "", 
        "dozent": [p for p in v["dozent"] if (sem_id in util.person.find_one({"_id": p})["semester"])] if kopiere_personen else [],
        "assistent": [p for p in v["assistent"] if sem_id in util.person.find_one({"_id": p})["semester"]] if kopiere_personen else [],
        "organisation": [p for p in v["organisation"] if sem_id in util.person.find_one({"_id": p})["semester"]] if kopiere_personen else [],
        "woechentlicher_termin": v["woechentlicher_termin"] if kopiere_termine else [],
        "einmaliger_termin": v["einmaliger_termin"] if kopiere_termine else [],
        "hp_sichtbar": v["hp_sichtbar"],
        "komm_sichtbar": v["komm_sichtbar"],
        "bearbeitet": "",
        "deputat": v["deputat"] if kopiere_personen else []
    }
    for et in v_new["einmaliger_termin"]:
        et["startdatum"] = None
        et["enddatum"] = None 
        et["startzeit"] = None 
        et["endzeit"] = None 
    
    w = util.veranstaltung.insert_one(v_new)
    util.logger.info(f"User {st.session_state.user} hat Veranstaltung {repr(util.veranstaltung, id)} nach Semester {repr(util.semester, sem_id)} kopiert.")
    util.semester.update_one({"_id": sem_id}, {"$push": {"veranstaltung": w.inserted_id}})
    util.rubrik.update_one({"_id": k}, {"$push": {"veranstaltung": w.inserted_id}})
    if kopiere_personen:
        for p in ( list(set(v_new["dozent"] + v_new["assistent"] + v_new["organisation"]))):
            util.person.update_one({"_id": p}, { "$push": {"veranstaltung": w.inserted_id}})
    if kopiere_verwendbarkeit:
        for a in v["verwendbarkeit_anforderung"]:            
            util.anforderung.update_one({"_id" : a}, { "$addToSet" : { "semester" : st.session_state.semester_id}})
            b = util.anforderung.find_one({"_id" : a})
            se = list(util.semester.find({"_id": {"$in": b["semester"]}}, sort=[("rang", pymongo.ASCENDING)]))
            util.anforderung.update_one({"_id" : a}, { "$set" : { "semester" :[s["_id"] for s in se] }})

    return w.inserted_id

# Neues Semester anlegen
# df ist ein dataframe, wobei "Veranstaltung übernehmen" die ids der aus dem vorletzten Semester zu übernehmenden Veranstaltungen enthält.
def semester_anlegen(x_updated, df, personen_uebernehmen, anforderung_uebernehmen, veranstaltung_uebernehmen):
    sem = list(util.semester.find({}, sort = [("rang", pymongo.DESCENDING)]))
    s = util.semester.insert_one(x_updated)
    # sem_id ist die id des anzulegenden Semesters
    sem_id = s.inserted_id
    # kopien enthält die ids der originalen und kopierten Datensätze
    id = sem[1]["_id"]
    kopie = {id: sem_id}
    # Kopiere Studiengänge aus dem letzten Semester
    util.studiengang.update_many({"semester": {"$elemMatch": {"$eq": sem[0]["_id"] }}}, { "$push": { "semester": sem_id}})
    # Kopiere Personen aus dem letzten Semester
    if personen_uebernehmen:
        util.person.update_many({"semester": {"$elemMatch": {"$eq": sem[0]["_id"] }}}, { "$push": { "semester": sem_id}})
        for p in list(util.person.find({"semester": {"$elemMatch": {"$eq": sem[0]["_id"] }}})):
            se = list(util.semester.find({"_id": {"$in": p["semester"]}}, sort=[("rang", pymongo.ASCENDING)]))
            util.person.update_one({"_id" : p["_id"]}, { "$set" : { "semester" :[s["_id"] for s in se] }})        
    # Kopiere Anforderungne aus dem letzten Semester
    if anforderung_uebernehmen:
        util.anforderung.update_many({"semester": {"$elemMatch": {"$eq": sem[0]["_id"] }}}, { "$push": { "semester": sem_id}})
        for a in util.anforderung.find({"semester": {"$elemMatch": {"$eq": sem[0]["_id"] }}}):
            se = list(util.semester.find({"_id": {"$in": a["semester"]}}, sort=[("rang", pymongo.ASCENDING)]))
            util.anforderung.update_one({"_id" : a["_id"]}, { "$set" : { "semester" :[s["_id"] for s in se] }})

    # Kopiere Rubriken und Codes
    if veranstaltung_uebernehmen:        
        for k in list(util.rubrik.find({"semester": sem[1]["_id"]})):
            k_loc = k["_id"]
            del k["_id"] # andernfalls gibt es einen duplicate key error
            k["semester"] = sem_id
            k_new = util.rubrik.insert_one(k)
            kopie[k_loc] = k_new.inserted_id
            util.semester.update_one({"_id": sem_id}, {"$push": {"rubrik": k_new.inserted_id}})
        for k in list(util.codekategorie.find({"semester": sem[1]["_id"]})):
            k_loc = k["_id"]
            del k["_id"]  # andernfalls gibt es einen duplicate key error
            k["semester"] = sem_id
            k_new = util.codekategorie.insert_one(k)
            kopie[k_loc] = k_new.inserted_id
            util.semester.update_one({"_id": sem_id}, {"$push": {"codekategorie": k_new.inserted_id}})
        for k in list(util.code.find({"semester": sem[1]["_id"]})):
            k_loc = k["_id"]
            del k["_id"]  # andernfalls gibt es einen duplicate key error
            k["codekategorie"] = kopie[k["codekategorie"]]
            k["semester"] = sem_id
            k_new = util.code.insert_one(k)
            kopie[k_loc] = k_new.inserted_id
            util.semester.update_one({"_id": sem_id}, {"$push": {"code": k_new.inserted_id}})
            util.codekategorie.update_one({"_id": k["codekategorie"]}, {"$push": {"code": k_new.inserted_id}})
        # Kopiere Veranstaltungen, übertrage rubrik und Codes
        for index, row in df.iterrows():
            if row["Veranstaltung übernehmen"]:
                kop_ver_id = kopiere_veranstaltung(ObjectId(row["_id"]), sem_id, row["...mit Dozenten/Assistenten"], row["...mit Terminen"], row["...mit Kommentaren"], row["...mit Verwendbarkeit"])
                kopie[row["_id"]] = kop_ver_id
                v = util.veranstaltung.find_one({"_id": ObjectId(row["_id"])})
                util.veranstaltung.update_one({"_id": kop_ver_id}, 
                                        {"$set": 
                                        {"rubrik": kopie[v["rubrik"]],
                                        "code": [kopie[co] for co in v["code"]]}})
            util.semester.update_one({"_id": sem_id}, {"$push": {"veranstaltung": kop_ver_id}})

    st.success("Semester erfolgreich angelegt!")
    util.logger.info(f"User {st.session_state.user} hat Semester {repr(util.semester, sem_id)} neu algelegt.")
    time.sleep(2)
    st.session_state.edit = ""
    st.session_state.page = "Veranstaltung"

# Lösche ein Semester
def delete_semester(id):
    x = util.semester.find_one({"_id": id})
    for v in list(util.veranstaltung.find({"semester": id})):
        util.person.update_many({"veranstaltung": { "$elemMatch": { "$eq": v["_id"]}}}, { "$pull": { "veranstaltung": v["_id"]}})
        util.veranstaltung.delete_one({"_id": v["_id"]})
    
    util.person.update_many({"semester": { "$elemMatch": {"$eq": id}}}, {"$pull": {"semester" : id}})
    util.anforderung.update_many({"semester": { "$elemMatch": {"$eq": id}}}, {"$pull": {"semester" : id}})
    util.studiengang.update_many({"semester": { "$elemMatch": {"$eq": id}}}, {"$pull": {"semester" : id}})
    util.rubrik.delete_many({"semester": id})
    util.code.delete_many({"semester": id})
    util.codekategorie.delete_many({"semester": id})
    util.logger.info(f"User {st.session_state.user} hat Semester {repr(util.semester, id)} gelöscht.")
    util.semester.delete_one({"_id": id})
    st.toast("🎉 Semester gelöscht, alle Personen, Studiengänge und Veranstaltungen geupdated.")

# Die Authentifizierung gegen den Uni-LDAP-Server
def authenticate(username, password):
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    ldap.set_option(ldap.OPT_NETWORK_TIMEOUT, 2.0)
    user_dn = "uid={},{}".format(username, base_dn)
    try:
        l = ldap.initialize(server)
        l.protocol_version = ldap.VERSION3
        l.simple_bind_s(user_dn, password)
        return True
    except ldap.INVALID_CREDENTIALS:
        return False
    except ldap.LDAPError as error:
        util.logger.warning(f"LDAP-Error: {error}")
        return False

def can_edit(username):
    u = util.user.find_one({"rz": username})
    id = util.group.find_one({"name": app_name})["_id"]
    return (True if id in u["groups"] else False)

def logout():
    st.session_state.logged_in = False
    util.logger.info(f"User {st.session_state.user} hat sich ausgeloggt.")

def reset_vars(text=""):
    st.session_state.edit = ""
    if text != "":
        st.success(text)

def display_navigation():
    st.markdown("<style>.st-emotion-cache-16txtl3 { padding: 2rem 2rem; }</style>", unsafe_allow_html=True)
    with st.sidebar:
        st.image("static/ufr.png", use_container_width=True)
        semesters = list(util.semester.find(sort=[("kurzname", pymongo.DESCENDING)]))
        st.session_state.semester_id = st.selectbox(label="Semester", options = [x["_id"] for x in semesters], index = [s["_id"] for s in semesters].index(st.session_state.semester_id), format_func = (lambda a: f"{util.semester.find_one({'_id': a})['name_de']} {'😎' if util.semester.find_one({'_id': a})['hp_sichtbar'] else ''}"), placeholder = "Wähle ein Semester", label_visibility = "collapsed", key = "master_semester_choice")

    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/00_Veranstaltungen.py", label="Veranstaltungen")
    st.sidebar.page_link("pages/01_Raumplan.py", label="Raumplan")
    st.sidebar.page_link("pages/02_Planung.py", label="Zukunftsplanung")
    #st.sidebar.page_link("pages/02_www.py", label="Vorschau www.math...")
    st.sidebar.page_link("pages/02_Veranstaltungen_suchen.py", label="Suchen/Datenexport")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/03_Personen.py", label="Personen")
    st.sidebar.page_link("pages/05_Studiengänge.py", label="Studiengänge")
    st.sidebar.page_link("pages/06_Module.py", label="Module")
    st.sidebar.page_link("pages/07_Anforderungen.py", label="Anforderungen")
    st.sidebar.page_link("pages/08_Räume.py", label="Räume")
    st.sidebar.page_link("pages/09_Gebäude.py", label="Gebäude")
    st.sidebar.page_link("pages/10_Terminart.py", label="Art von Terminen")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/12_Semester.py", label="Semester")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/13_LaTeX.py", label="Latex-Files")
    st.sidebar.page_link("pages/15_Dokumentation.py", label="Dokumentation")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)

# short Version ohne abhängige Variablen
def repr(collection, id, show_collection = True, short = False):
    x = collection.find_one({"_id": id})
    if collection == util.gebaeude:
        res = x['name_de']
    elif collection == util.raum:
        res = x['name_de']
    elif collection == util.semester:
        res = x['kurzname'] if short else x["name_de"]
    elif collection == util.rubrik:
        sem = util.semester.find_one({"_id": x["semester"]})["kurzname"]
        res = x['titel_de'] if short else f"{x['titel_de']} ({sem})"
    elif collection == util.code:
        sem = util.semester.find_one({"_id": x["semester"]})["kurzname"]
        res = x['beschreibung_de'] if short else f"{x['beschreibung_de']} ({sem})"    
    elif collection == util.person:
        res = f"{x['name']}, {x['name_prefix']}" if short else f"{x['name']}, {x['vorname']}"
    elif collection == util.studiengang:
        res = f"{x['name']}"
    elif collection == util.modul:
        res = []
        for id1 in x["studiengang"]:
            stu = util.studiengang.find_one({"_id" : id1, "semester" : { "$elemMatch" : { "$eq" : st.session_state.semester_id}}})
            if stu:
                res.append(stu["kurzname"])
        s = ", ".join(res)
        res = x['name_de'] if short else f"{x['name_de']} ({s})"
    elif collection == util.anforderung:
        an = util.anforderungkategorie.find_one({"_id": x["anforderungskategorie"]})["kurzname"]
        if an.strip() == "Kommentar":
            res = f"{x['name_de'].strip()}"
        else:
            res = f"{an.strip()}: {x['name_de'].strip()}"
    elif collection == util.anforderungkategorie:
        res = x['name_de']
    elif collection == util.codekategorie:
        res = x['name_de']
    elif collection == util.veranstaltung:
        s = ", ".join([util.person.find_one({"_id" : id1})["name"] for id1 in x["dozent"]])
        sem = util.semester.find_one({"_id": x["semester"]})["kurzname"]
        res = x['name_de'] if short else f"{x['name_de']} ({s}, {sem})"
    elif collection == st.session_state.terminart:
        res = f"{x['name_de']}"
    elif collection == st.session_state.dictionary:
        res = f"{x['de']}: {x['en']}"
    elif collection == util.planungveranstaltung:
        res = f"{x['name']}"
    elif collection == util.planung:
        res = f"{', '.join([repr(util.person, y, False, True) for y in x['dozent']])}"
    if show_collection:
        res = f"{util.collection_name[collection]}: {res}"
    return res

def hour_of_datetime(dt):
    return "" if dt is None else str(dt.hour)

# str1 und str2 sind zwei strings, die mit "," getrennte Felder enthalten, etwa
# str1 = "HS Rundbau, Mo, 8-10"
# str2 = "HS Rundbau, Mi, 8-10"
# Ausgabe ist dann
# HS Rundbau, Mo, Mi, 8-10
def shortify(str1, str2):
    str1_list = str.split(str1, ",")
    str2_list = str.split(str2, ",")
    if str1_list[0] == str2_list[0]:
        if str1_list[2] == str2_list[2]:
            return f"{str1_list[0]}, {str1_list[1]}, {str2_list[1]} {str2_list[2]}"
        else:
            return f"{str1_list[0]}, {str1_list[1]} {str1_list[2]}, {str2_list[1]} {str2_list[2]}"
    else:
        return None

def next_semester_kurzname(kurzname):
    a = int(kurzname[:4])
    b = kurzname[4:]
    return f"{a+1}SS" if b == "WS" else f"{a}WS"

def last_semester_kurzname(kurzname):
    a = int(kurzname[:4])
    b = kurzname[4:]
    return f"{a}SS" if b == "WS" else f"{a-1}WS"

def semester_name_de(kurzname):
    a = int(kurzname[:4])
    b = kurzname[4:]
    c = f"/{a+1}" if b == "WS" else ""
    return f"{'Wintersemester' if b == 'WS' else 'Sommersemester'} {a}{c}"

def semester_name_en(kurzname):
    a = int(kurzname[:4])
    b = kurzname[4:]
    c = f"/{a+1}" if b == "WS" else ""
    return f"{'Winter term' if b == 'WS' else 'Summer term'} {a}{c}"

def new_semester_dict():
    most_current_semester = util.semester.find_one({}, sort = [("rang", pymongo.DESCENDING)])
    kurzname = next_semester_kurzname(most_current_semester["kurzname"])
    name_de = semester_name_de(kurzname)
    name_en = semester_name_en(kurzname)
    return {"kurzname": kurzname, "name_de": name_de, "name_en": name_en, "rubrik":[], "code": [], "veranstaltung": [], "hp_sichtbar": True, "rang": most_current_semester["rang"]+1}

def veranstaltung_anlegen(sem_id, rub_id, v_dict):
    try:
        r = util.veranstaltung.find_one({"semester": sem_id}, sort = [("rang",pymongo.DESCENDING)])["rang"] + 1
    except:
        r = 0

    v = {
        "semester": sem_id,
        "hp_sichtbar": False,
        "komm_sichtbar": False,
        "name_de": "",
        "name_en": "",
        "midname_de": "",
        "midname_en": "",
        "kurzname": "",
        "ects": 0.0,
        "rubrik": rub_id,
        "code": [],
        "url": "",
        "kommentar_html_de": "",
        "kommentar_html_en": "",
        "rang": r,
        "inhalt_de": "",
        "inhalt_en":  "",
        "literatur_de": "",
        "literatur_en": "",
        "vorkenntnisse_de": "",
        "vorkenntnisse_en": "",
        "kommentar_latex_de": "",
        "kommentar_latex_en": "",
        "verwendbarkeit_modul": [],
        "verwendbarkeit_anforderung": [],
        "verwendbarkeit": [], 
        "kommentar_verwendbarkeit_de": "", 
        "kommentar_verwendbarkeit_en": "", 
        "dozent": [],
        "assistent": [],
        "organisation": [],
        "woechentlicher_termin": [],
        "einmaliger_termin": [],
        "bearbeitet": "",
        "deputat": []
    }
    for key, value in v_dict.items():
        v[key] = value
    w = util.veranstaltung.insert_one(v)
    util.logger.info(f"User {st.session_state.user} hat Veranstaltung {repr(util.veranstaltung, w.inserted_id)} angelegt.")
    util.semester.update_one({"_id": st.session_state.semester_id}, {"$push": {"veranstaltung": w.inserted_id}})
    util.rubrik.update_one({"_id": rub_id}, {"$push": {"veranstaltung": w.inserted_id}})
    st.session_state.edit = w.inserted_id
    return w.inserted_id

def delete_temporary(except_field = ""):
    """ Delete temporary data except for the given field."""
    if not except_field == "veranstaltung_tmp":
        st.session_state.veranstaltung_tmp.clear()
        st.session_state.translation_tmp = None

def get_semester_in_years(y = 0):
    if datetime.now().month < 4:
        res = f"{datetime.now().year-1+y}WS"
    elif 3 < datetime.now().month and datetime.now().month < 11:
        res = f"{datetime.now().year+y}SS"
    else:
        res = f"{datetime.now().year+y}WS"
    return res

    