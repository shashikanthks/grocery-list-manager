## Prerequisites

- Python 3.10+
- pip
- PostgreSQL


## Setup

In the project directory, run following commands prior to starting the server:

## Create virtual environment
`python -m venv venv`


## Activate virtual environment
`source venv/bin/activate` (macOS/Linux)
`venv\Scripts\activate`     (Windows)

## Install dependencies
`pip install -r requirements.txt`

## Setup Database
`psql -U postgres`
`CREATE DATABASE grocery_db;`
`\q`

## Migrate Database
`python manage.py makemigrations`
`python manage.py migrate`

## Create Superuser
`python manage.py createsuperuser`
Set username and password which will be used in the frontend application to login.

To start the development server:
`python manage.py runserver`


## Run Tests
`python manage.py test`