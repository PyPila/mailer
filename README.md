# mailer
[![codecov](https://codecov.io/gh/PyPila/mailer/branch/master/graph/badge.svg)](https://codecov.io/gh/PyPila/mailer)

## Installation

    cd /your/work/dir
    git clone <this_repo>
    cd <this_repo>
    pip install -r requirements/develop.txt
  
## Usage

### First time

Make a `service/settings/local.py` settings file, example:

    from service.settings.common import *

    AUTH_PASSWORD_VALIDATORS = []
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
  
After that execute:

    cd /your/work/dir/<this_repo>/
    python src/manage.py migrate
  
### Day-to-day usage

    cd /your/work/dir/<this_repo>/
    python src/manage.py runserver 0.0.0.0:8000
  
### Running tests

    cd /your/work/dir/<this_repo>/
    python src/manage.py test src
  
With coverage:

    coverage run --source='src' src/manage.py test src
    coverage html
  
