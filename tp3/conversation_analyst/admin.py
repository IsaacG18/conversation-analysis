from django.contrib import admin
from .models import File, Message, Analysis, Person, Location, KeywordSuite, RiskWord

# Register your models here.

class FileAdmin(admin.ModelAdmin):
    readonly_fields = ('date',)


admin.site.register(File, FileAdmin)
admin.site.register(Message)
admin.site.register(Analysis)
admin.site.register(Person)
admin.site.register(Location)
admin.site.register(KeywordSuite)
admin.site.register(RiskWord)
