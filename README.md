# employees-api

A simple app to help my students understand backend development and cover it with automated tests. \
This app is replication of employees-api, just without DB, all data will be stored inside JSON while application is running.

Application is live on https://employees-api-i9ae.onrender.com/

# Technical stack
* Python
* Flask

# Quick start

* Clone this repo to your local
* Create and activate virtual env
* Install dependencies:
  * `pip install -r requirements.txt`
* To make this code work in your local machine, create `.env` in root directory and add environment variables there as shown in below example:
```
JWT_SECRET_KEY='your secret key'
APP_SUPERUSER='your username'
APP_PASSWORD='your password'
```
* Run application using below command:
  * `python app.py`
