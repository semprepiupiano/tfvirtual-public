from django.db import models
from datetime import datetime, timedelta
from pytz import timezone
import operator
from functools import reduce
from .modelhelpers import days_hours_minutes_seconds

# Create your models here.

class Event(models.Model):
    name = models.CharField(max_length=200, default="Tacy Foundation Virtual Live Performance")
    date = models.DateTimeField('date of performance')
    streamyard_link = models.URLField()
    youtube_link = models.URLField()
    signup_limit = models.PositiveIntegerField(default=8)
    order_finalized = models.BooleanField(default=False)

    def signups_remaining(self):
        return self.signup_limit - self.signup_set.count()

    def spots_open(self):
        return self.signups_remaining() > 0

    def signups_closed(self):
        eastern = timezone('US/Eastern')
        now = eastern.localize(datetime.now())
        one_day = self.date - timedelta(days=1)
        ten_days = self.date - timedelta(days=10)
        return ten_days > now or now > one_day
    
    def get_date(self):
        return self.date.strftime("%m/%d/%Y")

    def is_future_event(self):
        eastern = timezone('US/Eastern')
        now = eastern.localize(datetime.now())
        return now < self.date

    def program_length(self):
        signups = [signup.piece_length for signup in self.signup_set.all()]
        if len(signups) == 0:
            return "0:00"
        (days, hours, minutes, seconds) = days_hours_minutes_seconds(reduce(operator.add, signups))
        if days > 0:
            return (str(days) + " day", str(days) + " days")[days > 1] + ", " + str(hours) + \
            ":" + "{0:0=2d}".format(minutes) + ":" + "{0:0=2d}".format(seconds)
        if hours > 0:
            return str(hours) + ":" + "{0:0=2d}".format(minutes) + ":" + "{0:0=2d}".format(seconds)
        return str(minutes) + ":" + "{0:0=2d}".format(seconds)
    
    def performance_order_active(self):
        eastern = timezone('US/Eastern')
        now = eastern.localize(datetime.now())
        one_day = self.date - timedelta(days=1)
        return now > one_day and self.order_finalized

    def __str__(self):
        return self.date.strftime("%B %-d, %Y, %-I:%M %p")

    
class SignUp(models.Model):
    performer = models.CharField(max_length=200)
    parent_email = models.EmailField()
    performer_email = models.EmailField(blank=True, null=True)
    instrument = models.CharField(max_length=50)
    piece = models.CharField(max_length=200)
    composer = models.CharField(max_length=200)
    piece_length = models.DurationField()
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    order_number = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.performer