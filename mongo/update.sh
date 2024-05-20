#!/bin/bash

mongo vvz --eval 'db.dropDatabase()'
cd port
python port.py
cd ..
python import.py
python change20240522.py

