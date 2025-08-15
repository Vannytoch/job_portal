for run wifi localhost:
waitress-serve --port=8000 job_portal.wsgi:application
------------------------------------------------------

check port able for run
python manage.py diffsettings | findstr ALLOWED_HOSTS
-----------------------------------------------------

activate script 
./env/scripts/activate
-----------------------------------------------------