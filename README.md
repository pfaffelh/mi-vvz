## mi-faq

Hier wird eine CRUD-App (Create, Read, Update, Delete) bereitgestellt, um ein FAQ in einem MongoDB abzubilden. Nach

```pip3 install -r requirements.txt```

ist es sinnvoll, zunächst die Datenbank mit einem Minimalsatz an Daten zu füttern (Achtung: das löscht alle Daten im cluser "faq" der mongoDB!), und zwar mit

``` python3 import.py```

Anschließend startet man die App mit

```streamlit run FAQ.py```

Man kann dann Kategorien im FAQ definieren, und Frage-Antwort-Paare (QA-Paare) in zwei-sprachiger Form eingeben. Es muss immer die Verbindung zu einem Mongo-DB unter 127.0.0.1:27017 sichergestellt sein. 

Files in `misc`: 
* `config.py`: Hier werden Basisdaten (hier: alle Studiengänge) bereitsgestellt.
* `schema.py`: Das Datenbank-Schema
* `util.py`, `ufr.png`: Hier wird das Uni-Logo bereitgestellt.
* `import.py`: siehe oben

Files in `pages`:
* `02_Kategorien.py`: Erzeugt die Seite, die die Kategorien definiert, und auf der man diese löschen und updaten kann.
* `01_Frage-Antwort-Paare.py`: Erzeugt die Seite, die die QA-Paare definiert, und auf der man diese löschen und updaten kann.

### Kommentare zur Funktionalität
* Ein Login ist momentan möglich, wenn 1) die Benutzerkennung (rz-Kennung) richtig eingegeben wird (diese wird gegen den LDAP-Server der Uni authentifiziert) und 2) der User (d.h. die rz-Kennung) in der Datenbank (user) in der Kategorie "faq" ist.
* Die Daten dieses FAQs werden verwendet, um auf xxx ein FAQ zu erzeugen.
* In allen Textfelder soll/kann Markdown verwendet werden. Bei der Darstellung auf xxx wird dieses dann in HTML übersetzt.
* Die Kategorie _unsichtbar_ gibt es immer, sie lässt sich nicht löschen. Der Grund ist, dass beim Löschen einer Kategorie die übrigen qa-Paare immer hierhin verschoben werden. 

TODO:
* Einklappen funktioniert manchmal nicht, wenn gespeichert wird
* 
