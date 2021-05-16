# Backend - Basic

Basic backend. It provides the API to be accessed by frontends.

Designed to follow the closest as possible the JSON version of [Delft-FEWS API](https://publicwiki.deltares.nl/display/FEWSDOC/FEWS+PI+REST+Web+Service) so that they are exchangeable.

Current implementation available at [https://hydro-web.herokuapp.com/](https://hydro-web.herokuapp.com/).

Developed using Django REST framework on Python 3.8.8 Linux. Also tested on Python 3.7.6 Windows 10.

## Setting up basic dev environment

The packages required by this project are described in the classical *requirements.txt* file.

It is highly recommended that you create a new python environment to work in your development. Multiple python package managers provide such a functionality.

If you are using pip, the steps for (1) creating a new environment named `backend-basic_fedora`, (2) entering the environment * and (3) installing the packages needed are:

    $ python -m venv backend-basic_fedora
		$ source [folder_path]/venvs/backend-basic_fedora/bin/activate
		(backend-basic_fedora) $ pip install -r requirements.txt

*: second step is given for Linux environements. Windows and Mac OS may have different command styles

## Endpoints already implemented

They are defined in the *api_rest/urls.py* file.

### http://.../v1/region

Returns the first Region document. It is supposed to be the only one of the database.

### http://.../v1/locations

Returns all available locations.

An endpoint with additional filters is yet to be implemented.

### http://.../v1/filters

Returns all available filters in the database.

### http://.../v1/filter/*<id\>*

Return the filter that has id=*<id\>*. Id is an integer.


## Deploying

As a typical Django project, we need to run:

	$ python manage.py makemigrations
	$ python manage.py migrate

To set up our database to match the designed models.

But just before running the `migrate` the line:

	isMigrate = False

in the file `crud/models.py` must change to:

	isMigrate = True

and, the line:

	MongoClient.HOST = "mongodb+srv://guest:noPass@cluster0.4kqxi.mongodb.net/"

is the file `api_rest/settings.py` so that the user `guest` (and its respective password) is changed to an user with writing permissions in the target database.


## Populating database

In *crud/fixtures/* we have the files to populate the database with some mock data for development and demonstration purposes.

To keep the database up to date, it is recommended the execution of the following commands:

	$ python migrate.py flush
    $ python migrate.py loaddata crud/fixutures/crud_fixture.json
    $ python migrate.py loaddata crud/fixtures/



## About this development branch version

It is set up to be deployed on Heroku. Thus, before submitting to main branch, Heroku-specific elements must be removed.

They are:

- `django-heroku==0.3.1` dependency *@requirements.txt*
- `import django_heroku` line *@backend-basic/settings.py*
- `django_heroku.settings(locals())` line *@backend-basic/settings.py*

It was developed following the instructions provided [here](https://bezkoder.com/django-mongodb-crud-rest-framework/).
