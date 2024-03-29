from django.db import models
from django.template.defaultfilters import slugify
from .scripts.nlp.nlp import get_keyword_lamma


# Create your models here.


class File(models.Model):
    file = models.FileField(upload_to="uploads/")
    title = models.CharField(max_length=128, unique=False)
    format = models.CharField(max_length=128, unique=False)
    date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True)

    def init_save(self, *args, **kwargs):
        self.title = self.file.name.split("/")[-1]
        self.format = self.title.split(".")[-1]
        self.slug = slugify(self.title + " " + str(self.date))
        super(File, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Analysis(models.Model):
    file = models.ForeignKey(File, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name_plural = "Analyses"

    def __str__(self):
        return self.file.__str__()


class Message(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    sender = models.CharField(max_length=50)
    main_sender = models.CharField(max_length=50)
    content = models.CharField(max_length=1000)
    display_content = models.CharField(max_length=1100)
    risk_rating = models.IntegerField(default=0)
    tags = models.CharField(max_length=1024)

    def set_main_sender(self, new_sender):
        self.main_sender = new_sender
        self.save()

    def __str__(self):
        return self.sender + self.timestamp.__str__()


class Person(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name.__str__()


class Location(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name.__str__()


class KeywordSuite(models.Model):
    name = models.CharField(max_length=128, unique=True)
    default = models.BooleanField(default=False)

    def __str__(self):
        return self.name.__str__()


class Topic(models.Model):
    name = models.CharField(max_length=128)

    def __str__(self):
        return self.name.__str__()


class RiskWord(models.Model):
    suite = models.ForeignKey(KeywordSuite, on_delete=models.CASCADE)
    topics = models.ManyToManyField(Topic, blank=True)
    keyword = models.CharField(max_length=128)
    risk_factor = models.IntegerField(default=128)
    amount = models.IntegerField(default=0)
    lemma = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        self.lemma = get_keyword_lamma(self.keyword)
        super(RiskWord, self).save(*args, **kwargs)

    def __str__(self):
        return self.keyword.__str__()


class RiskWordResult(models.Model):
    riskword = models.ForeignKey(RiskWord, on_delete=models.CASCADE)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    risk_factor = models.IntegerField(default=0, blank=True)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return self.analysis.__str__() + "-" + self.riskword.__str__()


class VisFile(models.Model):
    file_path = models.CharField(max_length=255)
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)

    def __str__(self):
        return self.file_path.__str__()


class DateFormat(models.Model):
    name = models.CharField(max_length=255)
    example = models.CharField(max_length=255)
    format = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.name.__str__()


class Delimiter(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=10)
    order = models.IntegerField(default=0)
    is_default = models.BooleanField(default=False)

    def get_name(self):
        return self.name

    def get_value(self):
        return self.value

    def get_order(self):
        return self.order

    def save(self, *args, **kwargs):
        self.value = self.value
        super(Delimiter, self).save(*args, **kwargs)

    def __str__(self):
        return self.name.__str__()


class ChatGPTConvo(models.Model):
    title = models.CharField(max_length=128, unique=False)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True)

    def init_save(self, *args, **kwargs):
        self.title = self.file.title + "-chat" + str(self.id)
        self.slug = slugify(self.file.slug + " " + str(self.id))
        super(ChatGPTConvo, self).save(*args, **kwargs)


class ChatGPTMessage(models.Model):
    typeOfMessage = models.CharField(max_length=64)
    content = models.CharField(max_length=1000)
    convo = models.ForeignKey(ChatGPTConvo, on_delete=models.CASCADE)


class ChatGPTFilter(models.Model):
    typeOfFilter = models.CharField(max_length=64)
    content = models.CharField(max_length=128)


class ChatGPTConvoFilter(models.Model):
    convo = models.ForeignKey(ChatGPTConvo, on_delete=models.CASCADE)
    filter = models.ForeignKey(ChatGPTFilter, on_delete=models.CASCADE)


class CustomThresholds(models.Model):
    strictness_level = models.IntegerField(null=True)
    sentiment_level = models.IntegerField(null=True)
    average_risk = models.FloatField(null=True)
    sentiment_multiplier = models.FloatField(null=True)
    max_risk = models.FloatField(null=True)
    word_risk = models.FloatField(null=True)


class GptSwitch(models.Model):
    on = models.BooleanField(default=False)


class LastFile(models.Model):
    file = models.ForeignKey(File, on_delete=models.SET_NULL, null=True)
