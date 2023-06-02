from django.db import models
from django.contrib.postgres.fields import ArrayField

# Create your models here.
class StoreActivity(models.Model):
    store_id = models.BigIntegerField()
    timestamp_utc = models.DateTimeField()
    status = models.CharField(max_length=10)

class StoreBusinessHours(models.Model):
    store_id = models.BigIntegerField()
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ])
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()

class StoreTimezone(models.Model):
    store_id = models.BigIntegerField(unique=True)
    timezone_str = models.CharField(max_length=100, default='America/Chicago')

class Report(models.Model):
    store_id = ArrayField(models.BigIntegerField())
    uptime_last_hour = ArrayField(models.IntegerField())
    uptime_last_day = ArrayField(models.FloatField())
    uptime_last_week = ArrayField(models.FloatField())
    downtime_last_hour = ArrayField(models.IntegerField())
    downtime_last_day = ArrayField(models.FloatField())
    downtime_last_week = ArrayField(models.FloatField())
    