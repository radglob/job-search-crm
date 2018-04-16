# Job Search CRM
[![Build Status](https://travis-ci.org/sdroadie/job-search-crm.svg?branch=master)](https://travis-ci.org/sdroadie/job-search-crm)
[![Maintainability](https://api.codeclimate.com/v1/badges/86ecb66d95424728138b/maintainability)](https://codeclimate.com/github/sdroadie/job-search-crm/maintainability)

A CRM designed for tech workers of all stripes to streamline their job
search process.

Built using Python 3.6 and Django. Make sure you have Python 3.6+ installed on your system. I recommend using [pyenv](https://github.com/pyenv/pyenv).

Using Python 3.6, install [pipenv](https://github.com/pypa/pipenv), clone this project and run `pipenv install`.

## Running a server:
The test server can be run with `pipenv run python manage.py runserver`.

## Testing:
You can run tests with `make test`. If you want a coverage report, run `make coverage`.

## Code Quality
Try to add tests as you write code. Untested code is broken by design.

We are using [Black](https://github.com/ambv/black) to format our code. Try to remember to run it before you commit.
If you're using a pre-commit hook for this, it leave your branch dirty.
