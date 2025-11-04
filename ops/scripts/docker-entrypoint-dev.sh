#!/bin/bash
# This script must not be used for production.

set -e

bash ops/scripts/tcp-port-wait.sh $DATABASE_HOST $DATABASE_PORT

echo $(date -u) "- Setting up database extensions"
python -c "
import psycopg2
import os
conn = psycopg2.connect(
    host=os.environ.get('DATABASE_HOST', 'localhost'),
    port=os.environ.get('DATABASE_PORT', '5432'),
    user=os.environ.get('DATABASE_USER', 'root'),
    password=os.environ.get('DATABASE_PASSWORD', 'root'),
    database=os.environ.get('DATABASE_NAME', 'crm_service')
)
conn.autocommit = True
cursor = conn.cursor()
cursor.execute('CREATE EXTENSION IF NOT EXISTS hstore;')
cursor.close()
conn.close()
"

echo $(date -u) "- Migrating"
python src/manage.py makemigrations
python src/manage.py migrate

echo $(date -u) "- Creating admin user"
python src/manage.py shell -c "from django.contrib.auth.models import User; user, created = User.objects.get_or_create(username='admin', defaults={'email': 'admin@example.com', 'is_staff': True, 'is_superuser': True}); user.set_password('admin'); user.save(); print('Admin user created' if created else 'Admin user exists')"

echo $(date -u) "- Running the server"
cd src && gunicorn crm_service.wsgi --config crm_service/gunicorn_conf.py -w 2 \
 --timeout 120 --reload --log-level debug
