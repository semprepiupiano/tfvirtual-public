from django.contrib import admin

from .models import Event, SignUp

# Register your models here.

class SignUpInline(admin.TabularInline):
    model = SignUp

class EventAdmin(admin.ModelAdmin):
    inlines = [
        SignUpInline,
    ]
    ordering = ('date',)

admin.site.register(Event, EventAdmin)
admin.site.register(SignUp)