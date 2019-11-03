===============================
W-App
===============================

.. image:: https://travis-ci.org/TobKed/W-App.svg?branch=master
    :target: https://travis-ci.org/TobKed/W-App
    :alt: Build Status

W-App


Quickstart
----------

Run the following commands to bootstrap your environment ::

    git clone https://github.com/TobKed/w_app
    cd w_app
    pip install -r requirements/dev.txt
    cp .env.example .env
    npm install
    npm start  # run the webpack dev server and flask server using concurrently

You will see a pretty welcome screen.

Once you have installed your DBMS, run the following to create your app's
database tables and perform the initial migration ::

    flask db init
    flask db migrate
    flask db upgrade
    npm start


Deployment
----------

To deploy::

    export FLASK_ENV=production
    export FLASK_DEBUG=0
    export DATABASE_URL="<YOUR DATABASE URL>"
    export GOOGLE_CLIENT_ID="<GOOGLE_CLIENT_ID>"
    export GOOGLE_CLIENT_SECRET="<GOOGLE_CLIENT_SECRET>"
    npm run build   # build assets with webpack
    flask run       # start the flask server
    flask run --cert=adhoc  # start the flask server with ad hoc ssl certificates

In your production environment, make sure the ``FLASK_DEBUG`` environment
variable is unset or is set to ``0``.


Shell
-----

To open the interactive shell, run ::

    flask shell

By default, you will have access to the flask ``app``.


Running Tests/Linter
--------------------

To run all tests, run ::

    flask test

To run the linter, run ::

    flask lint

The ``lint`` command will attempt to fix any linting/style errors in the code. If you only want to know if the code will pass CI and do not wish for the linter to make changes, add the ``--check`` argument.

Migrations
----------

Whenever a database migration needs to be made. Run the following commands ::

    flask db migrate

This will generate a new migration script. Then run ::

    flask db upgrade

To apply the migration.

For a full migration command reference, run ``flask db --help``.

If your deployment process is based on the git repository files (e.g on Heroku) you should add `migrations` folder to the repository.
You can do this after ``flask db migrate`` by running the following commands ::

    git add migrations/*
    git commit -m "Add migrations"

Make sure folder `migrations/versions` is not empty.


Docker
------

This app can be run completely using ``Docker`` and ``docker-compose``. Before starting, make sure to create a new copy of ``.env.example`` called ``.env``. You will need to start the development version of the app at least once before running other Docker commands, as starting the dev app bootstraps a necessary file, ``webpack/manifest.json``.

There are three main services:ą

To run the development version of the app ::

    docker-compose up flask-dev

To run the production version of the app ::

    docker-compose up flask-prod

The list of ``environment:`` variables in the ``docker-compose.yml`` file takes precedence over any variables specified in ``.env``.

To run any commands using the ``Flask CLI`` ::

    docker-compose run --rm manage <<COMMAND>>

Therefore, to initialize a database you would run ::

    docker-compose run --rm manage db init

A docker volume ``node-modules`` is created to store NPM packages and is reused across the dev and prod versions of the application. For the purposes of DB testing with ``sqlite``, the file ``dev.db`` is mounted to all containers. This volume mount should be removed from ``docker-compose.yml`` if a production DB server is used.


Asset Management
----------------

Files placed inside the ``assets`` directory and its subdirectories
(excluding ``js`` and ``css``) will be copied by webpack's
``file-loader`` into the ``static/build`` directory, with hashes of
their contents appended to their names.  For instance, if you have the
file ``assets/img/favicon.ico``, this will get copied into something
like
``static/build/img/favicon.fec40b1d14528bf9179da3b6b78079ad.ico``.
You can then put this line into your header::

    <link rel="shortcut icon" href="{{asset_url_for('img/favicon.ico') }}">

to refer to it inside your HTML page.  If all of your static files are
managed this way, then their filenames will change whenever their
contents do, and you can ask Flask to tell web browsers that they
should cache all your assets forever by including the following line
in your ``settings.py``::

    SEND_FILE_MAX_AGE_DEFAULT = 31556926  # one year

Google Login
------------

This app allows you to login by Google Account.

You need to do a few steps before deploying app.

You will need a Google Account. You already have one if you use Gmail.

On the the `Google developers credentials page <https://console.developers.google.com/apis/credentials>`_
press the ``Create credentials`` button and select the option for ``OAuth client ID``:

Select the ``Web application`` option at the top.
You can provide a name for the client in the ``Name`` field as well.
The name you provide will be displayed to users when they are consenting to your application acting on their behalf.

You need to set ``Authorised JavaScript origins`` and ``Authorised redirect URIs``::

    Authorized JavaScript: https://127.0.0.1:5000
    Authorised redirect URIs: https://127.0.0.1:5000/login/callback

Set appropriate URIs with your app address for deployment.

Finally, hit ``Create`` and take note of the ``client ID`` and ``client secret``. You’ll need both later.

You need fill `OAuth consent screen <https://console.developers.google.com/apis/credentials/consent>`_ also.

Heroku
------

Before deploying to Heroku you should be familiar with the basic concepts of `Git <https://git-scm.com/>`_ and `Heroku <https://heroku.com/>`_.

Remember to add migrations to your repository. Please check `Migrations`_ section.

Since the filesystem on Heroku is ephemeral, non-version controlled files (like a SQLite database) will be lost at least once every 24 hours. Therefore, a persistent, standalone database like PostgreSQL is recommended. This application will work with any database backend that is compatible with SQLAlchemy, but we provide specific instructions for Postgres, (including the required library ``psycopg2-binary``).

**Note:** ``psycopg2-binary`` package is a practical choice for development and testing but in production it is advised to use the package built from sources. Read more in the `psycopg2 documentation <http://initd.org/psycopg/docs/install.html?highlight=production%20advised%20use%20package%20built%20from%20sources#binary-install-from-pypi>`_

If you keep your project on GitHub you can use 'Deploy to Heroku' button thanks to which the deployment can be done in web browser with minimal configuration required.
The configuration used by the button is stored in ``app.json`` file.

.. raw:: html

    <a href="https://heroku.com/deploy" style="display: block"><img src="https://www.herokucdn.com/deploy/button.svg" title="Deploy" alt="Deploy"></a>
    <br>

Deployment by using `Heroku CLI <https://devcenter.heroku.com/articles/heroku-cli>`_:

* Create Heroku App. You can leave your app name, change it, or leave it blank (random name will be generated)::

    heroku create {{cookiecutter.app_name}}

* Add buildpacks::

    heroku buildpacks:add --index=1 heroku/nodejs
    heroku buildpacks:add --index=1 heroku/python

* Add database addon which creates a persistent PostgresSQL database. These instructions assume you're using the free `hobby-dev <https://elements.heroku.com/addons/heroku-postgresql#hobby-dev>`_ plan. This command also sets a ``DATABASE_URL`` environmental variable that your app will use to communicate with the DB.::

    heroku addons:create heroku-postgresql:hobby-dev --version=11

* Set environmental variables (change ``SECRET_KEY`` value)::

    heroku config:set SECRET_KEY=not-so-secret
    heroku config:set FLASK_APP=autoapp.py
    heroku config:set GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID
    heroku config:set GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET

*   Please check ``.env.example`` to see which environmental variables are used in the project and also need to be set. The exception is ``DATABASE_URL``, which Heroku sets automatically.

* Deploy on Heroku by pushing to the ``heroku`` branch::

    git push heroku master
