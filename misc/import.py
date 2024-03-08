from pymongo import MongoClient

# This is the mongodb
cluster = MongoClient("mongodb://127.0.0.1:27017")
mongo_db = cluster["faq"]
category = mongo_db["category"]
qa = mongo_db["qa"]

categories = [
              { "kurzname": "allgemein", 
                "name_de": "Allgemeines",
                "name_en": "General",
                "kommentar": "",
                "rang": 10
              },
              {  "kurzname": "verwendung", 
                "name_de": "Belegung und Verwendung von Veranstaltungen",
                "name_en": "Booking and utilisation of classes",
                "kommentar": "",
                "rang": 20
              },
              {  "kurzname": "pruefung", 
                "name_de": "Prüfungen und deren Anmeldung",
                "name_en": "Exams and their registration",
                "kommentar": "",
                "rang": 30
              },
              {  "kurzname": "abschlussarbeit", 
                "name_de": "Abschlussarbeiten",
                "name_en": "Final Thesis",
                "kommentar": "",
                "rang": 40
              },
              {  "kurzname": "sonst", 
                "name_de": "Sonstiges",
                "name_en": "Other",
                "kommentar": "",
                "rang": 50
              },
              {  "kurzname": "unsichtbar", 
                "name_de": "Unsichtbar",
                "name_en": "Invisible",
                "kommentar": "Diese Kategorie erscheint nicht auf der Homepage.",
                "rang": 60
              }]

qas = [{
        "category": "abschlussarbeit",
        "studiengang": ["msc"],
        "q_de": "Wie bekomme ich das Thema für meine Abschlussarbeit?", 
        "q_en": "How can I get the topic of my final thesis?",
        "a_de": "Sprechen Sie mit einem Dozenten und lassen sich beraten.",
        "a_en": "Meet a teacher and ask for advice.",
        "rang": 20,
        "kommentar": ""
        },
        {
        "category": "abschlussarbeit",
        "studiengang": [],
        "q_de": "Wie laufen Prüfungen ab?", 
        "q_en": "",
        "a_de": "Sie müssen Fragen beantworten",
        "a_en": "",
        "rang": 10,
        "kommentar": ""
        },  
        {
        "category": "sonst",
        "studiengang": [],
        "q_de": "Wie funktioniert ein Auslandssemester?", 
        "q_en": "",
        "a_de": '''[Studienberatung]({{url_for('studienberatungbase')}}) International Office der Universität Freiburg: \n\n Fahnenbergplatz, 79085 Freiburg \n Kurzinformation (pdf)  \n [Webseite](https://www.international.uni-freiburg.de/) \n Prof. Dr. Patrick Dondl \n _Auslandsbeautragter des Mathematischen Instituts_\n [Internetseite des Auslandsbeauftragten](https://home.mathematik.uni-freiburg.de/erasmus) Hermann-Herder-Straße 10, Raum 217 Tel. +49 761 203-5642 E-Mail: erasmus@math.uni-freiburg.de Sprechstunde: Mo 12:15–13:45 Uhr''',         
        "a_en": "",
        "rang": 11,
        "kommentar": ""
        },  
        {
        "category": "sonst",
        "studiengang": [],
        "q_de": "Wie melde ich mich zu einer Prüfung an?", 
        "q_en": "",
        "a_de": "Kurzanleitung: \n1. In [HISinOne](https://campus.uni-freiburg.de/) _'Mein Studium > Studienplaner mit Modulplan'_ (ggf. mit richtigem Studiengang) auswählen.\n2. Links oben das richtige Semester auswählen und rechts oben bei Veranstaltungen _'keine'_ und bei Prüfungs-/Studienleistungen _'alle'_ anklicken. \n3. Dann in der Liste das gewünschte Modul bzw. die gewünschte Veranstaltung suchen. \n4. Auf _'Prüfung anmelden'_ bzw. _'Studienleistung registrieren'_ gehen. \n5. Gegebenenfalls noch die richtige Gruppe auswählen. ",         
        "a_en": "",
        "rang": 12,
        "kommentar": ""
        },  
        {
        "category": "sonst",
        "studiengang": ["med", "mederw"],
        "q_de": "Wer ist das LLPA?", 
        "q_en": "",
        "a_de": "Das Landeslehrerprüfungsamt!",
        "a_en": "",
        "rang": 30,
        "kommentar": ""
        }  ]


print("Dieser Vorgang löscht alle Einträge in category und qa!")
print("Wirklch fortfahren? [y/N]")
input = input()
if input == "y":
  category.delete_many({})
  qa.delete_many({})
      
  for x in qas:
      qa.insert_one(x)
  for x in categories:
      category.insert_one(x)

