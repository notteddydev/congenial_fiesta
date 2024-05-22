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