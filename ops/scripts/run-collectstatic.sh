#!/bin/bash

# All this environment variables need to be defined to run collectstatic
export DATABASE_ENGINE=postgresql
export DATABASE_NAME=nothing
export DATABASE_PORT=nothing
export DATABASE_USER=nothing
export DJANGO_SETTINGS_MODULE=crm_service.settings.base

python src/manage.py collectstatic --no-input
