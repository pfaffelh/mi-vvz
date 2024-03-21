import streamlit as st
import pymongo
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

def update_confirm(collection, x, x_updated):
    collection.update_one(x, {"$set": x_updated })
    util.reset()
    st.success("Erfolgreich geändert!")

def new(collection):
    z = list(collection.find(sort = [("rang", pymongo.ASCENDING)]))
    st.write(z[0])
    rang = z[0]["rang"]-1
    util.new[collection]["rang"] = rang
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
    if id == util.leer[collection]:
        st.error("Dieses Item kann nicht gelöscht werden!")
        util.reset()
    else:
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
        st.success(f"Erfolgreich gelöscht!  {s}")

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

