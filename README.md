# congenial_fiesta
Python and Django project for building an offline mp3 library.

### Terminal 1:
```bash
python manage.py runserver
```

### Terminal 2:
```bash
redis-server
```

### Terminal 3:
```bash
python -m celery -A congenial_fiesta worker
```

### Terminal 4:
```bash
celery -A congenial_fiesta beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

Handy links
https://eyed3.readthedocs.io/en/latest/plugins/genres_plugin.html
https://stackoverflow.com/questions/31816624/naming-convention-for-django-url-templates-models-and-views
https://python.plainenglish.io/setting-up-a-basic-django-project-with-pipenv-7c58fa2ec631