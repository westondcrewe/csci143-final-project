# README for Flask-on-Docker
## Overview
This repository creates a web app that allows users to upload and view media files. The app is containerized in Docker and uses Flask's Python web development framework and a Postgres database for user information. Nginx acts as a reverse proxy for the app, and Gunicorn is used as a WSGI server to handle client requests. The app serves static files, like ```hello.txt``` in the ```project/static``` subfolder, as well as user-uploaded files, as shown in this screen recording. 

![CSCI143-HW3-ScreenRecord](https://github.com/westondcrewe/flask-on-docker/assets/123044932/42cd55a5-824f-464d-b02f-be6d2f580cde)

## Instructions
To run the project properly, the user should follow these steps and commands:
  1. (After downloading the files in this repository) Ensure that you are in the root folder of the project with the ```cd``` command
  2. Create a file in the root folder with the command ```vim .env.prod.db``` to define user-specific environment variables. The file should contain the following lines:
	```POSTGRES_USER=<username>
	   POSTGRES_PASSWORD=<passwork>
	   POSTGRES_DB=<database_name>```
  3. 
