#!/usr/bin/env sh

python manage.py collectstatic --no-input
gunicorn garage_sale.wsgi:application --bind 0.0.0.0
