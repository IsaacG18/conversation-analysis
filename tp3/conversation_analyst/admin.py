from django.contrib import admin
from django import forms
from .models import (
    File,
    Message,
    Analysis,
    Person,
    Location,
    KeywordSuite,
    RiskWord,
    KeywordPlan,
    Topic,
    RiskWordResult,
    VisFile,
    CustomThresholds,
    GptSwitch,
    ChatGPTConvo,
)

# Register your models here.


class FileAdmin(admin.ModelAdmin):
    readonly_fields = ("date",)


class SuiteAdminForm(forms.ModelForm):
    class Meta:
        model = KeywordSuite
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["plans"].required = False


class SuiteAdmin(admin.ModelAdmin):
    form = SuiteAdminForm

    def save_model(self, request, obj, form, change):
        obj.save()


admin.site.register(File, FileAdmin)
admin.site.register(Message)
admin.site.register(Analysis)
admin.site.register(Person)
admin.site.register(Location)
admin.site.register(KeywordSuite, SuiteAdmin)
admin.site.register(RiskWord)
admin.site.register(KeywordPlan)
admin.site.register(Topic)
admin.site.register(RiskWordResult)
admin.site.register(VisFile)
admin.site.register(CustomThresholds)
admin.site.register(GptSwitch)
admin.site.register(ChatGPTConvo)
