=======
Install
=======

1. install dependencies from setup.py
2. Go into local_settings.py in this directory and set up your database details with your mysql username and password::

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

3. Type the following command into the command line (while in the base directory)::

    python manage.py syncdb

4. Set up a cronjob to update from feeds hourly::

    1 * * * * python <your_path_goes_here>/personal/manage.py grabfeeds > /dev/null; <your_path_goes_here>/personal/manage.py grabfeeds update_index > /dev/null

5. Deploy using `WSGI`__
    __ https://docs.djangoproject.com/en/dev/howto/deployment/wsgi/
6. Done!

If you have any comments or suggestions or you find any bugs please let us know. You can email panfeed.gmail.com or post on our googlecode page at code.google.com/p/panfeed
