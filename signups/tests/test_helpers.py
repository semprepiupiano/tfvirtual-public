from django.utils import timezone
import datetime
from django.db import models
from signups.models import Event, SignUp

def create_event(days, hours, minutes, seconds):
    time = timezone.now() + datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return Event.objects.create(date=time, streamyard_link="streamyard.com", youtube_link="youtube.com")

def create_event_limit(days, hours, minutes, seconds, limit):
    time = timezone.now() + datetime.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
    return Event.objects.create(date=time, streamyard_link="streamyard.com", youtube_link="youtube.com", 
    signup_limit=limit)

def create_signup(event):
    length = datetime.timedelta(minutes=5)
    return SignUp.objects.create(performer="Sasha Suh", parent_email="myemail@email.com", 
    instrument="Piano", piece="Concerts de Etudes, I. Automne", composer="Cecile Chaminade", piece_length=length, 
    event_id = event.id)

def create_signup_piece_length(event, piece_length):
    return SignUp.objects.create(performer="Sasha Suh", parent_email="myemail@email.com", 
    instrument="Piano", piece="Concerts de Etudes, I. Automne", composer="Cecile Chaminade", piece_length=piece_length, 
    event_id = event.id)