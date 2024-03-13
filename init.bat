pip install -r win_requirements.txt
cd tp3
python manage.py makemigrations
python manage.py migrate
python manage.py migrate --run-syncdb
python date_format_populate.py