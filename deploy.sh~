#!/bin/bash

# Server-Hostname
SERVER="www2"

# Benutzername für die SSH-Verbindung
USERNAME="flask-reader"

# Führe den Befehl "deploy" auf dem Remote-Server aus
ssh $USERNAME@$SERVER 'cd mi-hp; git pull'
ssh $USERNAME@$SERVER 'sudo ./deploy-hp.sh > /dev/null'

