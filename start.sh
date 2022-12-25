#!/bin/sh

nohup ./manage.py runserver 8000 &
cd ./frontend
npm install
npm start --port 3000