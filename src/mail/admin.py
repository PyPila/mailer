from django.contrib import admin

from mail.models import *


admin.site.register(RecipientGroup)
admin.site.register(Recipient)
admin.site.register(EmailFields)
admin.site.register(Email)
admin.site.register(Log)
