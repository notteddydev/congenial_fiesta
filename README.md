# Python and Django project for building an offline mp3 library.

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