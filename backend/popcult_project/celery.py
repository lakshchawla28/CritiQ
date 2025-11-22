import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'popcult_project.settings')

app = Celery('popcult_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Periodic tasks
app.conf.beat_schedule = {
    'generate-recommendations-daily': {
        'task': 'apps.recommendations.tasks.generate_all_recommendations',
        'schedule': crontab(hour=2, minute=0),  # Run at 2 AM daily
    },
    'update-popular-movies': {
        'task': 'apps.movies.tasks.update_popular_movies',
        'schedule': crontab(hour=3, minute=0),  # Run at 3 AM daily
    },
    'check-upcoming-movies': {
        'task': 'apps.movies.tasks.check_upcoming_releases',
        'schedule': crontab(hour=6, minute=0),  # Run at 6 AM daily
    },
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')