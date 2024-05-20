# This is the sqlite3 db
for file in files:
    conn = sqlite3.connect(file)
    logging.info("Connected to " + file)
    # cur = conn.cursor()

    # Update building and place    
    location = mongo_db["location"]
    df = pd.read_sql_query(f"SELECT * from Place", conn)
    building_list = list(set(df['building']))
    building = mongo_db["building"]
    posts = [{"name": x} for x in building_list]
    logging.debug(posts)
#    building.insert_many_if_new(posts, "name")
    logging.debug("printing building:")
    logging.debug(list(building.find({})))

    port_sqlite_to_mongo(conn, 'Place', 'location', '_id', trans = {'id': '_id'})

documents = location.find()
for document in documents:
    b = document.get("building")
    b_id = building.find_one({"name": document.get("building")})
    document["building"] = b_id["_id"]
    logging.debug(document)

