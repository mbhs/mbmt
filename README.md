# MBMT

The Montgomery Blair Math Tournament is a math competition for middle school students in the Maryland area. This is the open source platform registration, logistics, and grading are hosted on. 

## Setup

To set up a development version of the site, clone the git repository and set up a virtual environment. Use Python 3, as Python 2 could not go out of style fast enough...

```
$ git clone git@github.com:mbhs/mbmt.git
$ cd mbmt
$ virtualenv env
```

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
