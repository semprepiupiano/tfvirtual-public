from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect
from .models import Event, SignUp
from django.views import generic
from django.utils import timezone
import datetime
from django.urls import reverse
from .helpers import insert_row, future_event, check_password, load_headshots
from django.contrib import messages
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from urllib.parse import urlencode
from .forms import SignUpForm, LoginForm, ContactForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

def index(request):
    return render(request, 'signups/index.html', {'nbar': 'index'})

def about(request):
    headshots = load_headshots()
    return render(request, 'signups/about.html', {'staff': headshots, 'nbar': 'about'})

def contact(request):
    if request.method == "GET":
        form = ContactForm()
        return render(request, 'signups/contact.html', {'form': form, 'nbar': 'contact'})
    if request.method == "POST":
        honeypot =  request.POST.get('contact_me_by_fax_only')
        if honeypot is not None and honeypot is True:
            return redirect(reverse('signups:index'))
        form = ContactForm(request.POST)
        if form.is_valid():    
            name = form.cleaned_data.get('name')
            email = form.cleaned_data.get('email')
            whoami = form.cleaned_data.get('whoami')
            subject = form.cleaned_data.get('subject')
            questions = form.cleaned_data.get('questions')
            context = {
                'name': name,
                'email': email,
                'whoami': whoami,
                'questions': questions,
            }
            html_message = render_to_string('signups/email.html', context)
            plain_message = strip_tags(html_message)
            from_email = 'admin@tfwvirtual.herokuapp.com'
            to = 'concerts.thetacyfoundation@gmail.com'
            mail.send_mail(subject, plain_message, from_email, [to], html_message=html_message)
            messages.success(request, 'Your submission has been received, and we will be in contact with you shortly!')
            return redirect(reverse('signups:index'))
        messages.warning(request, "The contact form was invalid. Please try again.")
        return redirect(reverse('signups:contact'))


def events(request):
    event_list = Event.objects.filter(date__gte=timezone.now()).order_by('date')
    past_events = Event.objects.filter(date__lt=timezone.now()).order_by('-date')
    return render(request, 'signups/events.html', {'event_list': event_list, 'nbar': 'events', 'past_events': past_events})

@login_required
@future_event
def event_detail(request, event_id):
    event = get_object_or_404(Event, pk=event_id)
    if event.performance_order_active():
        performers = event.signup_set.order_by('order_number')
        context = {'event': event, 'nbar': 'events', 'performers': performers}
    else:
        context = {'event': event, 'nbar': 'events'}   
    return render(request, 'signups/event_detail.html', context)

@login_required
@future_event
def sign_up(request, event_id):
    if request.method == 'GET':
        event = get_object_or_404(Event, pk=event_id)
        if event.signups_closed():
            error_message = 'Signups are closed for this event.'
            return render(request, 'signups/signup_error.html', {'event': event, 'error_message': error_message, 'nbar': 'events'})
        elif event.spots_open():
            form = SignUpForm()
            return render(request, 'signups/signup.html', {'event': event, 'form': form, 'nbar': 'events'})
        error_message = 'There are no more signups remaining for this event.'
        return render(request, 'signups/signup_error.html', {'event': event, 'error_message': error_message, 'nbar': 'events'})
    if request.method == 'POST':
        event = get_object_or_404(Event, pk=event_id)
        form = SignUpForm(request.POST)
        if event.signups_closed():
            error_message = 'Signups are closed for this event.'
            return render(request, 'signups/signup_error.html', {'event': event, 'error_message': error_message, 'nbar': 'events'})
        elif not event.spots_open():
            error_message = 'There are no more signups remaining for this event.'
            return render(request, 'signups/signup_error.html', {'event': event, 'error_message': error_message, 'nbar': 'events'})
        elif request.POST.get('public_domain') is None:
            messages.warning(request, 'Please make sure your piece is in the public domain.')
            return redirect(reverse('signups:signup', args=[event.id]))
        elif request.POST.get('consent_form') is None:
            messages.warning(request, 'Please make sure you have filled out the consent form.')
            return redirect(reverse('signups:signup', args=[event.id]))
        elif form.is_valid():
            performer = form.cleaned_data.get('performer')
            parent_email = form.cleaned_data.get('parent_email')
            performer_email = form.cleaned_data.get('performer_email')
            instrument = form.cleaned_data.get('instrument')
            piece = form.cleaned_data.get('piece')
            composer = form.cleaned_data.get('composer')
            minutes = form.cleaned_data.get('minutes')
            #seconds = form.cleaned_data.get('seconds')
            questions = request.POST.get('questions')
            # piece_length = datetime.timedelta(minutes=minutes, seconds=seconds)
            piece_length = datetime.timedelta(minutes=minutes)
            signup = SignUp(performer=performer, parent_email=parent_email, performer_email=performer_email, instrument=instrument, piece=piece, composer=composer, piece_length=piece_length, event_id=event.id)
            signup.save()
            insert_row(event, performer, parent_email, performer_email, piece, composer, piece_length, questions)
            return redirect(reverse('signups:success'))
        messages.warning(request, 'The form was invalid. Please try again.')
        return render(request, 'signups/signup.html', {'event': event, 'form': form, 'nbar': 'events'})

@login_required
def success(request):
    return render(request, 'signups/success.html', {'nbar': 'events'})

def guide(request):
    return render(request, 'signups/guide.html', {'nbar': 'guide'})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data.get('password')
            if check_password(request, password):
                messages.success(request, "You have been logged in!")
                if 'next' in request.GET:
                    return redirect(request.GET.get('next'))
                return redirect(reverse('signups:events'))
            messages.warning(request, 'The password was incorrect. Please try again.')   
            if 'next' in request.GET:
                base_url = reverse('signups:login')
                next = urlencode({'next': request.GET.get('next')})
                url = '{}?{}'.format(base_url, next)
                return redirect(url)
            return redirect(reverse('signups:login'))
    if request.user.is_authenticated:
        return redirect(reverse('signups:events'))
    form = LoginForm()
    return render(request, 'signups/login.html', {'next': request.GET.get('next', ''), 'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out!")
    return redirect(reverse('signups:index'))