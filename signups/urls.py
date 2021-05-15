from django.urls import path 

from . import views
import tfwvirtual

app_name = 'signups'
urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('events/', views.events, name='events'),
    path('event/<int:event_id>/', views.event_detail, name='detail'),
    path('event/<int:event_id>/signup/', views.sign_up, name='signup'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('success/', views.success, name='success'),
    path('guide/', views.guide, name='guide'),
    path('contact/', views.contact, name='contact'),
]