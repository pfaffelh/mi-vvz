#!/bin/bash

CURRENTDATE=`date +"%Y-%m-%d-%H-%M"`

echo Current Date and Time is: ${CURRENTDATE}

# Server-Hostname
SERVER="www2"

# Benutzername für die SSH-Verbindung
USERNAME="flask-reader"

# Führe den Befehl "deploy" auf dem Remote-Server aus
ssh $USERNAME@$SERVER 'cd mi-vvz/backup; CURRENTDATE=`date +"%Y-%m-%d-%H-%M"`; mongodump --db vvz --archive=vvz_backup_${CURRENTDATE}'
scp $USERNAME@$SERVER:~/mi-vvz/backup/vvz_backup_${CURRENTDATE} .
mongorestore --drop --archive=vvz_backup_${CURRENTDATE}

