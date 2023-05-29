#!/bin/sh

echo "Activate python environment"
. env/bin/activate
echo "Environment activated successfully"

echo "Start Asset Accounting application"
python manage.py runserver
