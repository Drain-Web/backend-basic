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

### Using VENV only

If you are using only **venv**, the steps for (1) creating a new environment named `django_backend_3.8`, (2) entering the environment\* and (3) installing the packages needed are:

    ? python -m venv django_backend_3.8
	? source [folder_path]/venvs/django_backend_3.8/bin/activate
	(django_backend_3.8) $ pip install -r requirements.txt

*: second step is given for Linux environments. Windows and Mac OS may have different command styles

### Using CONDA + PIP

If you are using *conda* and *pip* on **Linux** and **Windows**, the following 4 commands are required:

	? conda create -n django_backend_3.8 python=3.8
    ? conda activate django_backend_3.8
    [SYSTEM SPECIFIC COMMAND]
    ? pip install -r requirements.txt

As it says, the 3<sup>rd</sup> command is system specific.

On **Linux**, ```[SYSTEM SPECIFIC COMMAND]``` is:

	$ while read requirement; do conda install --yes $requirement; done < requirements.txt

On **Windows** within a PowerShell terminal, ```[SYSTEM SPECIFIC COMMAND]``` is:

	> ForEach ($req in Get-Content -Path requirements.txt) { conda install --yes $req }

## Activating local development server

As a typical Django system, the command:

    ? python .\manage.py runserver

starts a local server that can be accessed at ```http://127.0.0.1:8000/```.

## Deploying

### Updating Database

As a typical Django project, we need to run:

	? python manage.py makemigrations
	? python manage.py migrate

To set up our database to match the designed models.

But just before running the `migrate` the line:

	isMigrate = False

in the file `crud/models.py` must change to:

	isMigrate = True

and, the line:

	MongoClient.HOST = "mongodb+srv://guest:noPass@cluster0.4kqxi.mongodb.net/"

is the file `api_rest/settings.py` so that the user `guest` (and its respective password) is changed to an user with writing permissions in the target database.

#### Error: Not implemented alter command for SQL ALTER TABLE "..." ...

If you get this error after changing a *Collection* structure, try using the command:

    ? python manage.py migrate --fake crud [migration_id]

In which ```migration_id``` can be found in the aforementioned error message in:

    Running migrations:
     Applying crud.[migration_id]...

## Populating database

Please refer to the *README.md* in *crud/fixtures/*.

### Uploading API interface

A Docker setup is available to update the running API on the server.

#### Testing the Docker container locally

To run the Docker locally for a project that will later be hosted at ```https://hydro-web.herokuapp.com/```, a Docker image must first be created with the command:

    ? docker build -f Dockerfile -t registry.heroku.com/hydro-web/web .

Once built, it can be run with:

    ? docker run --name backend_api -e "PORT=8765" -e "DEBUG=1" -p 8007:8765 registry.heroku.com/hydro-web/web

If everything is fine, the result can be accessed opening [http://0.0.0.0:8007/](http://0.0.0.0:8007/) in your browser.

To stop the server its Docker container must be stopped/removed. In a new terminal, run the forced removal:

    ? docker rm backend_api -f

#### Pushing the Docker container to the server

Set ```heroku``` to operate in *container runtime* with:

    ? heroku container:login

Push the image to the registry and release it:

    ? docker push registry.heroku.com/hydro-web/web
    ? heroku container:release -a hydro-web web

Now it should be available at the website given in the beggining of this files.

If it returns ```Error 404```, you may need to run:

    ? heroku open -a hydro-web

To start the stuff.

## About this development branch version

It is set up to be deployed on Heroku. Thus, before submitting to main branch, Heroku-specific elements must be removed.

They are:

- `django-heroku==0.3.1` dependency *@requirements.txt*
- `import django_heroku` line *@backend-basic/settings.py*
- `django_heroku.settings(locals())` line *@backend-basic/settings.py*

It was developed following the instructions provided [here](https://bezkoder.com/django-mongodb-crud-rest-framework/).
