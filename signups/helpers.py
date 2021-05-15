from django.shortcuts import redirect, reverse, get_object_or_404, render
from .models import Event
import gspread
import hashlib
from oauth2client.service_account import ServiceAccountCredentials
from urllib.parse import urlencode
from django.contrib.auth import authenticate, login
import json
import os

from yaml import safe_load
from django.contrib.staticfiles.storage import staticfiles_storage

import functools

from .models import Event

def future_event(func):
    @functools.wraps(func)
    def wrapper_future_event(request, event_id, *args, **kwargs):
        event = get_object_or_404(Event, pk=event_id)
        if event.is_future_event():
            return func(request, event_id, *args, **kwargs)
        else:
            error_message = 'This event has passed.'
            return render(request, 'signups/signup_error.html', {'event': event, 'error_message': error_message})
    return wrapper_future_event

def days_hours_minutes_seconds(td):
    return td.days, td.seconds//3600, (td.seconds//60)%60, td.seconds % 60

def check_password(request, password):
    user = authenticate(username='default', password=password)
    if user is not None:
        request.session.set_expiry(600)
        login(request, user)
        return True
    return False

def insert_row(event, performer, parent_email, performer_email, piece_name, composer, piece_length, questions):
    with open('client_secret.json') as f:
        credentials = json.load(f)
    credentials.update({'private_key': os.environ.get('GOOGLE_API_KEY')})
    client = gspread.service_account_from_dict(credentials)
    sheet = client.open("Virtual Live Concert Signups - Website").sheet1
    (days, hours, minutes, seconds) = days_hours_minutes_seconds(piece_length)
    seconds = "{0:0=2d}".format(seconds)
    values = [event.get_date(), performer, "", "", parent_email, performer_email, composer + " - " + piece_name, str(minutes) + ":" + str(seconds), questions]
    sheet.append_row(values)

def load_headshots():
    lc_staff = open('lc_staff.yaml', 'r')
    headshots_yaml = safe_load(lc_staff)
    headshots = []
    for item in headshots_yaml:
        headshots.append({'name': item.get('name'), 'url': staticfiles_storage.url('headshots/'+item.get('photo'))})
    return headshots

