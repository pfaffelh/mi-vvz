import pandas as pd
from datetime import datetime
import logging

logging.basicConfig(level=logging.DEBUG, format = "%(asctime)s - %(levelname)s - schema - %(message)s")

# Update data from semester from semester.xls
def port(mongo_db):
    sem = mongo_db["semester"]
    sem.drop()
    logging.info("Dropped all documents from semester.")
    # Access semester.xls
    df = pd.read_excel("semester.xls")
    logging.info("Opened semester.xls")
    df['id1'] = [x.strip().lower() for x in df['kurzname']]

    posts = df.to_dict('records')
    for x in posts:
        x["code"] = []
        x["kategorie"] = []
        x["veranstaltung"] = []
        logging.debug(x)
    sem.insert_many(posts)
    logging.info("Wrote collection semester.")

    # Now check schema
    # Here are some tests:
    import schema
    mongo_db.command("collMod", "semester", validator = schema.semester_validator)
    # Needs to be accessed again once courses are filled. 
    # Every semester must store the courses in the semester.
    # print(tools.new_semester(df['end']))



