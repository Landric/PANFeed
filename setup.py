from os.path import join, dirname
from distutils.core import setup

try:
    f = open(join(dirname(__file__), 'README'))
    long_description = f.read().strip()
    f.close()
except IOError:
    long_description = None

setup(
    name='django-panfeed',
    version='2.0.0',
    url="http://panfeed.ecs.soton.ac.uk/",
    description='PANFeed is a tool to help you take control of news feeds already existing on your university campus. It harvests feeds from university websites and uses them to build custom feeds of news you are actually interested in. The tool has a range of applications including personal custom news feeds, custom feeds for use in department websites or simply taking an inventory of your university feeds. Try out and take control of your news!',
    long_description=long_description,
    author='University of Southampton CampusROAR',
    author_email='lac@ecs.soton.ac.uk',
    license='LICENSE',
    keywords='django rss feed panfeed ATOM'.split(),
    platforms='any',
    packages=['panfeed',],
    install_requires=[
        "Django",
        "feedparser",
        "django-jquery",
        "django-angularjs",
        "django-bootstrap-less",
        "django-respite >= 1.2.0",
        "django-registration",
        "django-csp",
        "django-browserid",
        "django-tastypie",
        "django-crispy-forms",
        "django-haystack",
        "django-extensions",
        "xapian-haystack",
        "progressbar",
        "django-compressor",
        "ogp",
    ],
    package_data={'panfeed': [
        'text.txt',
        'static/featured.txt',
        'static/index.html',
        'static/images/*',
        'static/scripts/*.js',
        'templates/*.html',
        'templates/registration/*.html',
    ]},
)
