# Backend - Basic

Basic backend. It provides the API to be accessed by frontends.

Designed to follow the closest as possible the JSON version of [Delft-FEWS API](https://publicwiki.deltares.nl/display/FEWSDOC/FEWS+PI+REST+Web+Service) so that they are exchangeable.

Current implementation available at [https://hydro-web.herokuapp.com/](https://hydro-web.herokuapp.com/).

Developed using Django REST framework on Python 3.8.8 Linux. Also tested on Python 3.7.6 Windows 10.

## Endpoints

Please refer to the *README.md* in *crud/*.

## Setting up basic dev environment

The packages required by this project are described in the classical *requirements.txt* file.

It is highly recommended that you create a new python environment to work in your development. Multiple python package managers provide such a functionality.

If you are using only **venv**, the steps for (1) creating a new environment named `backend-basic_fedora`, (2) entering the environment * and (3) installing the packages needed are:

    $ python -m venv backend-basic_fedora
	$ source [folder_path]/venvs/backend-basic_fedora/bin/activate
	(backend-basic_fedora) $ pip install -r requirements.txt

*: second step is given for Linux environments. Windows and Mac OS may have different command styles

If you are using **conda** and **pip** on Linux, the same steps would be:

    $ conda create -n django_frontend_3.8 python=3.8
    $ conda activate django_frontend_3.8
    $ while read requirement; do conda install --yes $requirement; done < requirements.txt
    $ pip install -r requirements.txt

## Activating local development server

As a typical Django system, the command:

    $ python .\manage.py runserver

starts a local server that can be accessed at ```http://127.0.0.1:8000/```.

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

### Error: Not implemented alter command for SQL ALTER TABLE "..." ...

If you get this error after changing a *Collection* structure, try using the command:

    $ python manage.py migrate --fake crud [migration_id]

In which ```migration_id``` can be found in the aforementioned error message in:

    Running migrations:
     Applying crud.[migration_id]...


## Populating database

Please refer to the *README.md* in *crud/fixtures/*.


## About this development branch version

It is set up to be deployed on Heroku. Thus, before submitting to main branch, Heroku-specific elements must be removed.

They are:

- `django-heroku==0.3.1` dependency *@requirements.txt*
- `import django_heroku` line *@backend-basic/settings.py*
- `django_heroku.settings(locals())` line *@backend-basic/settings.py*

It was developed following the instructions provided [here](https://bezkoder.com/django-mongodb-crud-rest-framework/).
