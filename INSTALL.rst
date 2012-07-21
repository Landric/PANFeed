=======
Install
=======

1. Install dependencies using setup.py
2. Edit local_settings.py in this directory and set up your database details with your mysql username and password::

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': '<database name here>',                      # Or path to database file if using sqlite3.
            'USER': '<username here>',                      # Not used with sqlite3.
            'PASSWORD': '<password here>',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }

3. Install the database schema and fixtures using::

    $ ./manage.py syncdb

4. Set up a cronjob to update from feeds hourly::

    1 * * * * python <your_path_goes_here>/personal/manage.py grabfeeds > /dev/null; <your_path_goes_here>/personal/manage.py grabfeeds update_index > /dev/null

5. Finally deploy using `WSGI`_
6. Done!

If you have any comments or suggestions or you find any bugs please `email`_ us or post on our `googlecode`_ page.

.. _WSGI: https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
.. _googlecode: http://code.google.com/p/panfeed
.. _email: panfeed@gmail.com