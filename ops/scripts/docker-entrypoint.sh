#!/usr/bin/env bash

set -e

echo $(date -u) "- Migrating"
python src/manage.py makemigrations
python src/manage.py migrate

echo $(date -u) "- Load Initial Data"
python src/manage.py loadinitialdata

# export env variable from file
if [ -e /JWT_PRIVATE_KEY_RSA_BUILDLY ]
then
  export JWT_PRIVATE_KEY_RSA_BUILDLY=`cat /JWT_PRIVATE_KEY_RSA_BUILDLY`
fi

if [ -e /JWT_PUBLIC_KEY_RSA_BUILDLY ]
then
  export JWT_PUBLIC_KEY_RSA_BUILDLY=`cat /JWT_PUBLIC_KEY_RSA_BUILDLY`
fi

echo $(date -u) "- Collect Static"
python src/manage.py collectstatic --no-input

echo $(date -u) "- Running the server"
cd src && gunicorn -b 0.0.0.0:8080 crm_service.wsgi
