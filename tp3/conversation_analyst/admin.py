from django.contrib import admin
from .models import (
    File,
    Message,
    Analysis,
    Person,
    Location,
    KeywordSuite,
    RiskWord,
    Topic,
    RiskWordResult,
    VisFile,
    CustomThresholds,
    GptSwitch,
    ChatGPTConvo,
    LastFile
)

# Register your models here.


class FileAdmin(admin.ModelAdmin):
    readonly_fields = ("date",)


admin.site.register(File, FileAdmin)
admin.site.register(Message)
admin.site.register(Analysis)
admin.site.register(Person)
admin.site.register(Location)
admin.site.register(KeywordSuite)
admin.site.register(RiskWord)
admin.site.register(Topic)
admin.site.register(RiskWordResult)
admin.site.register(VisFile)
admin.site.register(CustomThresholds)
admin.site.register(GptSwitch)
admin.site.register(ChatGPTConvo)
admin.site.register(LastFile)
