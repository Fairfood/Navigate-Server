#!/bin/sh

python manage.py migrate

# if [ "$CREATE_SUPER_USER" ]
# then
#     echo "Creating super user $DJANGO_SUPERUSER_USERNAME"
#     python fairtrace_v2/manage.py createsuperuser \
#         --noinput \
#         --username $DJANGO_SUPERUSER_USERNAME \
#         --email $DJANGO_SUPERUSER_EMAIL
#     echo  "Created super user $DJANGO_SUPERUSER_USERNAME"
# fi


$@

exec "$@"