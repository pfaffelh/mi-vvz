import streamlit as st
import pymongo
import time
import misc.util as util

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
    collection.update_one(x, {"$set": x_updated })
    if reset:
        util.reset()
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
                res.append(util.repr(x["collection"], y["_id"]))
        else:
            for y in list(x["collection"].find({x["field"]: id})):
                res.append(util.repr(x["collection"], y["_id"]))
    return res

def delete_item_update_dependent_items(collection, id):
    print(util.collection_name[collection])
    try:
        if id == util.leer[collection]:
            st.error("Dieses Item kann nicht gelöscht werden!")
            util.reset()
    except:
        s = ("  \n".join(find_dependent_items(collection, id)))
        if s:
            s = f"\n{s}  \ngeändert."     
        for x in util.abhaengigkeit[collection]:
            if x["list"]:
                x["collection"].update_many({x["field"]: { "$elemMatch": { "$eq": id }}}, {"$pull": { x["field"] : id}})
            else:
                x["collection"].update_many({x["field"]: id}, { "$set": { x["field"].replace(".", ".$."): util.leer[collection]}})             
        collection.delete_one({"_id": id})
        util.reset()
        st.success(f"🎉 Erfolgreich gelöscht!  {s}")

def kopiere_veranstaltung(id, kop_sem_id, kopiere_personen, kopiere_termine, kopiere_kommVVZ, kopiere_verwendbarkeit):
    v = util.veranstaltung.find_one({"_id": id})
    # Das wird die Kategorie der kopierten Veranstaltung, falls das neue Semester 
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
        "dozent": v["dozent"] if kopiere_personen else [],
        "assistent": v["assistent"] if kopiere_personen else [],
        "organisation":  v["organisation"] if kopiere_personen else [],
        "woechentlicher_termin": v["woechentlicher_termin"] if kopiere_termine else [],
        "einmaliger_termin": v["einmaliger_termin"] if kopiere_termine else [],
        "hp_sichtbar": True
    }
    w = util.veranstaltung.insert_one(v_new)
    util.semester.update_one({"sem": kop_sem_id}, {"$push": {"veranstaltung": w.inserted_id}})
    util.kategorie.update_one({"_id": k}, {"$push": {"veranstaltung": w.inserted_id}})
    for p in ( list(set(v_new["dozent"] + v_new["assistent"] + v_new["organisation"]))):
        util.person.update_one({"_id": p}, { "$push": {"veranstaltung": w.inserted_id}})
    st.success("Erfolgreich kopiert!")
    time.sleep(2)
    st.session_state.edit = w.inserted_id
    st.session_state.page = "Veranstaltung"
    
# Lösche ein Semester
def delete_semester(id):
    for v in list(util.veranstaltung.find({"semester": id})):
        util.person.update_many({"veranstaltung": { "$elemMatch": { "$eq": v["_id"]}}}, { "$pull": { "veranstaltung": v["_id"]}})
        util.veranstaltung.delete_one({"_id": v["_id"]})
    
    util.person.update_many({"semester": { "$elemMatch": {"$eq": id}}}, {"$pull": {"semester" : id}})
    util.kategorie.delete_many({"semester": id})
    util.code.delete_many({"semester": id})
    util.semester.delete_one({"_id": id})
    st.toast("🎉 Semester gelöscht, alle Personen und Veranstaltungen geupdated.")

# collection_dict has the form {id: name}
# subset is a subset of collection_dict.keys which needs to be updated
# no_cols is the number of columns for presenting the checkboxes
# if all_choices == True, there are checkboxes for all cases
# if all_choices == False, there are checkboxes only for elements of the subset, 
# but an additional selectbox where new items can be selected.
# id is from the elements which we change; needed fot the keys of widgets only.
def update_list(collection_dict, subset, no_cols, all_choices, id):
    # diese Items können hier gar nicht geändert werden, also werden sie wieder verwendet:
    field_update_list = [x for x in subset if x not in collection_dict]
    field_update = {}
    cols = st.columns([1 for x in range(no_cols)])
    i = 0
    su = subset if all_choices == False else collection_dict.keys()
    for s in su:
        with cols[i % no_cols]:
            field_update[s] = st.checkbox(f"{collection_dict[s]}", True if s in subset else False, key = f"sem_{id}_{s}")
        i = i+1
    field_update_list = field_update_list + [key for key,value in field_update.items() if value == True]

    if all_choices == False:
        choice = [""] + list(collection_dict.keys())
        new_element = st.selectbox("Hinzufügen", choice, index = 0, format_func = (lambda a: collection_dict[a] if a else ""), key = f"sem_{id}_neu")
        if new_element:
            field_update_list.append(new_element)
    # Duplikate löschen:
    field_update_list = list(set(field_update_list))
    return field_update_list

