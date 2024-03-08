import pymongo

# This is the ldap-server of the University, which is required for authentication
server="ldaps://ldap.uni-freiburg.de"
base_dn = "ou=people,dc=uni-freiburg,dc=de"

import logging
logging.basicConfig(level=logging.INFO, format = "%(asctime)s - %(levelname)s - schema - %(message)s")

# Das ist die mongodb; 
# QA-Paar ist ein Frage-Antwort-Paar aus dem FAQ.
# category enthält alle Kategorien von QA-Paaren. "invisible" muss es geben!
# qa enthält alle Frage-Antwort-Paare.
# user ist aus dem Cluster users und wird nur bei der Authentifizierung benötigt
cluster = pymongo.MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["vvz"]
mongo_db_users = cluster["user"]

gebaeude = mongo_db["gebaeude"]
ort = mongo_db["ort"]

course = mongo_db["course"]
course_category = mongo_db["course_category"]
group = mongo_db["group"]
person = mongo_db["person"]
person_category = mongo_db["person_category"]
program = mongo_db["program"]
semester = mongo_db["semester"]

user = mongo_db_users["user"]

logging.info("Connected to MongoDB")
logging.info("Database contains collections: ")
logging.info(str(mongo_db.list_collection_names()))
