#!/bin/bash

env_file=".env"
env_file_template=".env.example"
pyvenv_dir=".venv"

if test ! -f "$env_file"
then
    echo "Environment variables file missing!"
    echo "  cp \"$env_file_template\" \"$env_file\""
    echo "...and set the values as appropriate."
    exit 1
fi

if test ! -d "$pyvenv_dir"
then
    echo "Python virtual environment missing, please create with"
    echo "  make venv"
    exit 1
fi

# run with envvars in '.env'
export $(cat "$env_file" | xargs)

mode="$1"
shift

case $mode in
    manage)
        exec "$pyvenv_dir"/bin/python manage.py $@
        ;;
    python)
        exec "$pyvenv_dir"/bin/python manage.py runserver $@
        ;;
    gunicorn)
        exec "$pyvenv_dir"/bin/gunicorn floridaman.wsgi --log-file - $@
        ;;
    *)
        echo "Usage: $0 {manage|python|gunicorn}"
        exit 1
esac
