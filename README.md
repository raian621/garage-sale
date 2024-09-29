# Garage Sale App

[![codecov](https://codecov.io/gh/raian621/garage-sale/graph/badge.svg?token=96TAKPWAZO)](https://codecov.io/gh/raian621/garage-sale)
[![CI Checks](https://github.com/raian621/garage-sale/actions/workflows/checks.yml/badge.svg)](https://github.com/raian621/garage-sale/actions/workflows/checks.yml)

Makes running a garage sale easier by tracking prices and inventory.

## Running

```sh
pip install -r requirements.txt
python manage.py runserver
```

## Environment variables

- `MODE`: `DEBUG` for debug mode, `PROD` (default) for production mode
- `SECRET_KEY`: secret key used for encryption and signing
