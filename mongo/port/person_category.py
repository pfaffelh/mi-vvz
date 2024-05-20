import pandas as pd
from datetime import datetime
import logging
# Update data from semester from semester.xls
def port(mongo_db):
    cat = mongo_db["person_category"]
    # Delete all entries in mongo_db
    cat.delete_many({})
    cat.create_index("id", unique=True)
    logging.info("Dropped all documents from person_category.")

    # Access person_category.xls
    df = pd.read_excel("person_category.xls")
    logging.info("Opened person_category.xls")
    df.fillna("", inplace=True)
    posts = df.to_dict('records')
    for x in posts:
        keys = []
        for key, value in x.items():
            if value == "":
                keys.append(key)
        for key in keys:
            logging.debug("Deleted " + key)
            del x[key]

    posts = df.to_dict('records')
    for post in posts:
        logging.debug(post)
    cat.insert_many(posts)
    logging.info("Wrote collection person_category.")

    # Now check schema
    # Here are some tests:
    import schema
    mongo_db.command("collMod", "person_category", validator = schema.person_category_validator)


