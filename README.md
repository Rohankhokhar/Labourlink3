# LabourLink

LabourLink

- clone your repo
  (specific-location)>>> git clone https://github.com/brijeshpytops/LabourLink.git
- change dir and got to the basedir
  > > > cd LabourLink

.../LabourLink > <- base dir

- make sure you have installed python (\* Python version 3.x.y)
  .../LabourLink > python --version
  Python 3.12.2

- create virtual env
  .../LabourLink > python -m venv [your-env-name]

- activate and deactivate your virtual env
  .../LabourLink > [your-env-name]\Scripts\activate
  ([your-env-name]).../LabourLink > [your-env-name]\Scripts\deactivate
  .../LabourLink >

- create requirements.txt
  ([your-env-name]).../LabourLink > type nul > requirements.txt

- add installed modules and packages in requirements.txt file
  ([your-env-name]).../LabourLink > pip freeze > requirements.txt

- install modules and packegs from requirements.txt file
  ([your-env-name]).../LabourLink > pip install -r requirements.txt

- Now install django
  ([your-env-name]).../LabourLink > pip install django

- verify django installed
  ([your-env-name]).../LabourLink > python
  Python 3.12.2 (tags/v3.12.2:6abddd9, Feb 6 2024, 21:26:36) [MSC v.1937 64 bit (AMD64)] on win32
  Type "help", "copyright", "credits" or "license" for more information.
  > > > import django
  > > > django.get_version()
  > > > '5.1.3'

OR

([your-env-name]).../LabourLink > python -m django --version
5.1.3

- Creating a Django project
  ([your-env-name]).../LabourLink > django-admin startproject project .

- create django app's dir
  ([your-env-name]).../LabourLink > mkdir LLApps
  LLApps -
  / master
  / dashboard
  / labour

- create django app's
  ([your-env-name]).../LabourLink > python manage.py startapp [app-name] APPDIR/[app-name]

- go to the base_dir/project/settings.py

INSTALLED_APPS = [
'django.contrib.admin',
'django.contrib.auth',
'django.contrib.contenttypes',
'django.contrib.sessions',
'django.contrib.messages',
'django.contrib.staticfiles',

]

CUSTOM_APPS = [
'LLApps.master', # add your app
'LLApps.dashboard', # add your app
'LLApps.labour', # add your app
]

THIRD_PARTIES_APPS = [

]

INSTALLED_APPS += CUSTOM_APPS

INSTALLED_APPS += THIRD_PARTIES_APPS

Now go to the specific app in apps.py

from django.apps import AppConfig

class DashboardConfig(AppConfig):
default_auto_field = 'django.db.models.BigAutoField'
name = '[app-dir-name].[app-name]'

- Django admin account:[ create super user]
  ([your-env-name]).../LabourLink > python manage.py createsuperuser
  Username (leave blank to use 'brijesh'): admin
  Email address: admn
  Error: Enter a valid email address.
  Email address:
  Password: **\*\*\*\***
  Password (again): **\*\*\*\***
  The password is too similar to the username.
  This password is too short. It must contain at least 8 characters.
  This password is too common.
  Bypass password validation and create user anyway? [y/N]: y
  Superuser created successfully.

- migrate and make-migrations
  ([your-env-name]).../LabourLink > python manage.py migrate
  ([your-env-name]).../LabourLink > python manage.py makemigrations

- create static dir
  LLApps(apps-dir) /
  / dashboard(app)
  / static - mkdir
  / dashbaord(app-name) - mkdir

- create templates dir
  LLApps(apps-dir) /
  / dashboard(app)
  / templates - mkdir
  / dashbaord(app-name) - mkdir

- run your project
  ([your-env-name]).../LabourLink > python manage.py runserver [port-number]
  Watching for file changes with StatReloader
  Performing system checks...

System check identified no issues (0 silenced).

You have 18 unapplied migration(s). Your project may not work properly until you apply the migrations for app(s): admin, auth, contenttypes, sessions.
Run 'python manage.py migrate' to apply them.
November 28, 2024 - 10:15:09
Django version 5.1.3, using settings 'project.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.



URL : https://witzcode.pythonanywhere.com/technology/1/15/?wz_tech=python&wz_category=variable

http: hyper text transfer protocol
s: secure socket layer
witzcode.pythonanywhere.com : domain -> ip-address:port 
/technology/1/15: endpoints
?wz_tech=python&wz_category=variable: query paramenters



- CREATE MODEL
from django.db import models

class AbstrctModelName(models.Model)
  field_name = models.field_type(config...)

class ChildModelName(AbstractModelName):
  field_name = models.field_type(config...)


if any change or add in model fields
([your-env-name]).../LabourLink > python manage.py makemigrations
after make-migrations, you have to apply the migrations via "python manage.py migrate"
([your-env-name]).../LabourLink > python manage.py migrate

Now check created table in database : exist or not



Project Flow:

Labour -
  AUTH :
    - can registration
      * first_name
      * last_name
      * email
      * mobile
      * password
      * confirm_password

    - can login
      * email
      * password

    - can forgot password
      * registered-email 
        - send otp
          - auto render on otp verification page
            * otp
            * new-password
            * confirm-password
