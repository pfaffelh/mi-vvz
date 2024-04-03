import streamlit as st
import pymongo
import time
import ldap
import misc.util as util
from bson import ObjectId
from misc.config import *

def move_up(collection, x, query = {}):
    query["rang"] = {"$lt": x["rang"]}
    target = collection.find_one(query, sort = [("rang",pymongo.DESCENDING)])
    if target:
        n= target["rang"]
        collection.update_one(target, {"$set": {"rang": x["rang"]}})    
        collection.update_one(x, {"$set": {"rang": n}})    

def move_down(collection, x, query = {}):
    query["rang"] = {"$gt": x["rang"]}
    target = collection.find_one(query, sort = [("rang", pymongo.ASCENDING)])
    if target:
        n= target["rang"]
        collection.update_one(target, {"$set": {"rang": x["rang"]}})    
        collection.update_one(x, {"$set": {"rang": n}})    

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
    collection.update_one(x, {"$set": x_updated })
    if reset:
        reset_vars("")
    st.toast("🎉 Erfolgreich geändert!")

def new(collection, ini = {}):
    z = list(collection.find(sort = [("rang", pymongo.ASCENDING)]))
    rang = z[0]["rang"]-1
    st.write(util.new[collection])
    util.new[collection]["rang"] = rang    
    for key, value in ini.items():
        util.new[collection][key] = value
    x = collection.insert_one(util.new[collection])
    st.session_state.expanded=x.inserted_id
    st.session_state.edit=x.inserted_id
    util.logger.info(f"User {st.session_state.user} hat in {util.collection_name[collection]} ein neues Item angelegt.")
    st.rerun()

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
            for y in list(x["collection"].find({x["field"]: { "$elemMatch": { "$eq": id }}})):
                res.append(repr(x["collection"], y["_id"]))
        else:
            for y in list(x["collection"].find({x["field"]: id})):
                res.append(repr(x["collection"], y["_id"]))
    return res

def delete_item_update_dependent_items(collection, id):
    if collection in util.leer.keys() and id == util.leer[collection]:
            st.toast("Fehler! Dieses Item kann nicht gelöscht werden!")
            reset_vars("")
    else:
        print("enter except")
        s = ("  \n".join(find_dependent_items(collection, id)))
        if s:
            s = f"\n{s}  \ngeändert."     
        for x in util.abhaengigkeit[collection]:
            if x["list"]:
                x["collection"].update_many({x["field"]: { "$elemMatch": { "$eq": id }}}, {"$pull": { x["field"] : id}})
            else:
                x["collection"].update_many({x["field"]: id}, { "$set": { x["field"].replace(".", ".$."): util.leer[collection]}})             
        util.logger.info(f"User {st.session_state.user} hat in {util.collection_name[collection]} item {repr(collection, id)} gelöscht, und abhängige Felder geändert.")
        collection.delete_one({"_id": id})
        reset_vars("")
        st.success(f"🎉 Erfolgreich gelöscht!  {s}")

def kopiere_veranstaltung_confirm(id, kop_sem_id, kopiere_personen, kopiere_termine, kopiere_kommVVZ, kopiere_verwendbarkeit):
    w_id = kopiere_veranstaltung(id, kop_sem_id, kopiere_personen, kopiere_termine, kopiere_kommVVZ, kopiere_verwendbarkeit)
    st.success("Erfolgreich kopiert!")
    time.sleep(2)
    st.session_state.edit = w_id
    st.session_state.page = "Veranstaltung"

def kopiere_veranstaltung(id, kop_sem_id, kopiere_personen, kopiere_termine, kopiere_kommVVZ, kopiere_verwendbarkeit):
    v = util.veranstaltung.find_one({"_id": ObjectId(id)})
    k = v["kategorie"] if v["semester"] == kop_sem_id else util.kategorie.find_one({"semester": kop_sem_id, "titel_de": "-"})["_id"]
    # Das wird der Rang der kopierten Veranstaltung
    try:
        r = util.veranstaltung.find_one({"semester": kop_sem_id, "kategorie": k}, sort = [("rang",pymongo.DESCENDING)])["rang"] + 1
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
        "semester": kop_sem_id,
        "kategorie": k,
        "code": v["code"] if v["semester"] == kop_sem_id else [],
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
        "dozent": [p for p in v["dozent"] if (kop_sem_id in util.person.find_one({"_id": p})["semester"])] if kopiere_personen else [],
        "assistent": [p for p in v["assistent"] if kop_sem_id in util.person.find_one({"_id": p})["semester"]] if kopiere_personen else [],
        "organisation": [p for p in v["organisation"] if kop_sem_id in util.person.find_one({"_id": p})["semester"]] if kopiere_personen else [],
        "woechentlicher_termin": v["woechentlicher_termin"] if kopiere_termine else [],
        "einmaliger_termin": v["einmaliger_termin"] if kopiere_termine else [],
        "hp_sichtbar": True
    }
    w = util.veranstaltung.insert_one(v_new)
    util.logger.info(f"User {st.session_state.user} hat Veranstaltung {repr(util.veranstaltung, id)} nach Semester {repr(util.semester, kop_sem_id)} kopiert.")
    util.semester.update_one({"sem": kop_sem_id}, {"$push": {"veranstaltung": w.inserted_id}})
    util.kategorie.update_one({"_id": k}, {"$push": {"veranstaltung": w.inserted_id}})
    for p in ( list(set(v_new["dozent"] + v_new["assistent"] + v_new["organisation"]))):
        util.person.update_one({"_id": p}, { "$push": {"veranstaltung": w.inserted_id}})
    return w.inserted_id

# Kopiere ein Semester    
def kopiere_semester(id, x_updated, df, kopiere_personen):
    last_sem_id = list(util.semester.find(sort = [("rang", pymongo.DESCENDING)]))[0]["_id"]
    s = util.semester.insert_one(x_updated)
    sem_id = s.inserted_id
    util.logger.info(f"User {st.session_state.user} hat Semester {repr(util.semester, id)} nach {repr(util.semester, sem_id)} kopiert.")
    # kopien enthält die ids der originalen und kopierten Datensätze
    kopie = {id: sem_id}
    # Kopiere Personen aus dem letzten Semester
    if kopiere_personen:
        util.person.update_many({"semester": {"$elemMatch": {"$eq": last_sem_id }}}, { "$push": { "semester": sem_id}})

    # Kopiere Kategorien und Codes
    for k in list(util.kategorie.find({"semester": id})):
        k_loc = k["_id"]
        del k["_id"] # andernfalls gibt es einen duplicate key error
        k_new = util.kategorie.insert_one(k)
        util.kategorie.update_one({"_id": k_new.inserted_id}, {"$set": {"semester": sem_id}})
        kopie[k_loc] = k_new.inserted_id
        util.semester.update_one({"_id": sem_id}, {"$push": {"kategorie": k_new.inserted_id}})
    for k in list(util.code.find({"semester": id})):
        k_loc = k["_id"]
        del k["_id"]  # andernfalls gibt es einen duplicate key error
        k_new = util.code.insert_one(k)
        util.code.update_one({"_id": k_new.inserted_id}, {"$set": {"semester": sem_id}})
        kopie[k_loc] = k_new.inserted_id
        util.semester.update_one({"_id": sem_id}, {"$push": {"code": k_new.inserted_id}})
    # Kopiere Veranstaltungen, übertrage Kategorie und Codes
    for index, row in df.iterrows():
        kop_ver_id = kopiere_veranstaltung(ObjectId(row["_id"]), sem_id, row["Personen"], row["Termine"], row["Kommentare"], row["Verwendbarkeit"])
        kopie[row["_id"]] = kop_ver_id
        v = util.veranstaltung.find_one({"_id": ObjectId(row["_id"])})
        util.veranstaltung.update_one({"_id": kop_ver_id}, 
                                 {"$set": 
                                  {"kategorie": kopie[v["kategorie"]],
                                  "code": [kopie[co] for co in v["code"]]}})
        util.semester.update_one({"_id": sem_id}, {"$push": {"veranstaltung": kop_ver_id}})
    st.success("Erfolgreich kopiert!")
    time.sleep(2)
    st.session_state.edit = ""
    st.session_state.page = "Veranstaltung"

# xxx toast einblenden, zu Übersicht springen

# Lösche ein Semester
def delete_semester(id):
    x = util.semester.find_one({"_id": id})
    for v in list(util.veranstaltung.find({"semester": id})):
        util.person.update_many({"veranstaltung": { "$elemMatch": { "$eq": v["_id"]}}}, { "$pull": { "veranstaltung": v["_id"]}})
        util.veranstaltung.delete_one({"_id": v["_id"]})
    
    util.person.update_many({"semester": { "$elemMatch": {"$eq": id}}}, {"$pull": {"semester" : id}})
    util.kategorie.delete_many({"semester": id})
    util.code.delete_many({"semester": id})
    util.logger.info(f"User {st.session_state.user} hat Semester {repr(util.semester, id)} gelöscht.")
    util.semester.delete_one({"_id": id})
    st.toast("🎉 Semester gelöscht, alle Personen und Veranstaltungen geupdated.")

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

# Die Authentifizierung gegen den Uni-LDAP-Server
def authenticate(username, password):
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
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
    faq_id = util.group.find_one({"name": "faq"})["_id"]
    return (True if faq_id in u["groups"] else False)

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
        col1, col2, col3 = st.columns([1,8,1])
        with col2:
            st.image("static/ufr.png", use_column_width=False)
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("VVZ.py", label="Veranstaltungen")
    st.sidebar.page_link("pages/01_Raumplan.py", label="Raumplan")
    st.sidebar.page_link("pages/02_www.py", label="Vorschau www.math...")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/03_Personen.py", label="Personen")
    st.sidebar.page_link("pages/05_Studiengänge.py", label="Studiengänge")
    st.sidebar.page_link("pages/06_Module.py", label="Module")
    st.sidebar.page_link("pages/07_Anforderungen.py", label="Anforderungen")
    st.sidebar.page_link("pages/08_Räume.py", label="Räume")
    st.sidebar.page_link("pages/09_Gebäude.py", label="Gebäude")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/10_Semester.py", label="Semester")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)
    st.sidebar.page_link("pages/11_Dokumentation.py", label="Dokumentation")
    st.sidebar.write("<hr style='height:1px;margin:0px;;border:none;color:#333;background-color:#333;' /> ", unsafe_allow_html=True)


def repr(collection, id, show_collection = True):
    x = collection.find_one({"_id": id})
    if collection == util.gebaeude:
        res = x['name_de']
        if show_collection:
            res = "Gebäude: " + res
    elif collection == util.raum:
        res = x['name_de']
        if show_collection:
            res = "Raum: " + res
    elif collection == util.semester:
        res = x['kurzname']
        if show_collection:
            res = "Semester: " + res
    elif collection == util.kategorie:
        sem = util.semester.find_one({"_id": x["semester"]})["kurzname"]
        res = f"{x['titel_de']} ({sem})"
        if show_collection:
            res = "Kategorie: " + res
    elif collection == util.code:
        sem = util.semester.find_one({"_id": x["semester"]})["kurzname"]
        res = f"{x['beschreibung_de']} ({sem})"    
        if show_collection:
            res = "Code: " + res
    elif collection == util.person:
        res = f"{x['name']}, {x['name_prefix']}"
        if show_collection:
            res = "Person: " + res
    elif collection == util.studiengang:
        res = f"{x['name']}"
        if show_collection:
            res = "Studiengang: " + res
    elif collection == util.modul:
        s = ", ".join([util.studiengang.find_one({"_id" : id1})["kurzname"] for id1 in x["studiengang"]])
        res = f"{x['name_de']} ({s})"
        if show_collection:
            res = "Modul: " + res
    elif collection == util.anforderung:
        res = x['name_de']
        if show_collection:
            res = "Anforderung: " + res
    elif collection == util.anforderungkategorie:
        res = x['name_de']
        if show_collection:
            res = "Anforderungskategorie: " + res
    elif collection == util.veranstaltung:
        s = ", ".join([util.person.find_one({"_id" : id1})["name"] for id1 in x["dozent"]])
        sem = util.semester.find_one({"_id": x["semester"]})["kurzname"]
        res = f"{x['name_de']} ({s}, {sem})"
        if show_collection:
            res = "Veranstaltung: " + res
    return res

def hour_of_datetime(dt):
    if dt is None:
        return ""
    else:
        return str(dt.hour)

def name_of_sem_id(semester_id):
    x = util.semester.find_one({"_id": semester_id})
    return x["name_de"]

def name_of_ver_id(ver_id):
    x = util.veranstaltung.find_one({"_id": ver_id})
    return x["name_de"]


