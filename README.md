## mi-vvz

Hier wird eine CRUD-App (Create, Read, Update, Delete) bereitgestellt, um ein Veranstaltungsverzeichnis im Mathematischen Institut (Uni Freiburg) mit Hilfe einer MongoDB zu verwalten. Nach

```pip3 install -r requirements.txt```

ist es sinnvoll, zunächst die Datenbank mit einem Satz an Daten zu füttern (Achtung: das löscht alle Daten im cluster "vvz" der mongoDB!), und zwar mit

``` python3 mongo/import.py```

Anschließend startet man die App mit

```streamlit run VVZ.py```

### Kommentare zur Funktionalität
* Ein Login ist momentan möglich, wenn 1) die Benutzerkennung (rz-Kennung) richtig eingegeben wird (diese wird gegen den LDAP-Server der Uni authentifiziert) und 2) der User (d.h. die rz-Kennung) in der Datenbank (user) in der Kategorie "vvz" ist.
* Die Daten dieses FAQs werden verwendet, um die Webpage xxx zu erzeugen.
* In allen Textfelder soll/kann Markdown verwendet werden. Bei der Darstellung auf xxx wird dieses dann in HTML übersetzt.
* Eine Darstellung aller Felder der Datenbank ist unter _Dolumentation_ der App zu finden.

### Auf dem Webserver des MIs

Der User flask-reader kann die App auf www2.mathematik.privat (zu erreichen aus dem privaten Netz der Uni) updated. Hierzu einloggen, in `mi-vvz` dann 

```
git pull
sudo /home/flask-reader/deploy-mi-vvz.sh
```

ausführen. Die App ist zu erreichen unter [http://mi-vvz1.mathematik.privat](http://mi-vvz1.mathematik.privat).

