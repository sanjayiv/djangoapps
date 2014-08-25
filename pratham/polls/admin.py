from django.contrib import admin
from polls.models import Poll
from polls.models import Choice

# Register your models here.
admin.site.register(Poll)
admin.site.register(Choice)
