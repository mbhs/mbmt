# MBMT

The Montgomery Blair Math Tournament is a math competition for middle school students in the Maryland area. 
This is the open source platform registration, logistics, and grading are hosted on. 

## Setup

To set up a development version of the site, clone the git repository and set up a virtual environment. 
Use Python 3, as that is the language this project is intended for. 
Also, make sure you're working on the current version branch through pull requests.
Master reflects full releases and hot-fixes. 

```
$ git clone git@github.com:mbhs/mbmt.git
$ cd mbmt
$ virtualenv env
```

SFTP/SCP (using CyberDuck or PuTTY) to transfer db.sqlite3 from sargon to your local version.

Activate your virtual environment and install the dependencies. Activation varies by operating system.

```
$ source env/bin/activate    # unix
$ .\env\Scripts\activate    # windows 
$ pip install -r requirements.txt
```

Make migrations and migrate Django.

```
$ python manage.py makemigrations
$ python manage.py migrate
```

Run the server.

```
$ python manage.py runserver
```
