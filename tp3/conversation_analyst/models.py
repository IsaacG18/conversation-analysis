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
        self.slug = slugify(self.title+" "+str(self.date))
        super(File, self).save(*args, **kwargs)

    def __str__(self):
        return self.title

class KeywordPlan(models.Model):
    name = models.CharField(max_length=128, null=True)
    def __str__(self):
        return self.name.__str__()

class Analysis(models.Model):
    file = models.ForeignKey(File, null=True, on_delete=models.SET_NULL)
    KeywordPlan = models.ForeignKey(KeywordPlan, null=True, on_delete=models.SET_NULL)
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
    name = models.CharField(max_length=128,unique=True)
    plans = models.ManyToManyField(KeywordPlan, blank=True)
    default = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        global_plan = KeywordPlan.objects.get_or_create(name='global')[0]
        super(KeywordSuite, self).save(*args, **kwargs)
        if self.default:
            self.plans.add(global_plan)
        else:
            self.plans.remove(global_plan)
        super(KeywordSuite, self).save(force_insert=False)
        
    def __str__(self):
        return self.name.__str__()
    
    
class Topic(models.Model):
    name = models.CharField(max_length=128)
    def __str__(self):
        return self.name.__str__()    


class RiskWord(models.Model):
    suite = models.ForeignKey(KeywordSuite, on_delete= models.CASCADE)
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
    riskword = models.ForeignKey(RiskWord, on_delete= models.CASCADE)
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
    def __str__(self):
        return self.name.__str__()

class ChatGPTConvo(models.Model):
    title = models.CharField(max_length=128, unique=False)
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    start = models.DateTimeField(null=True)
    end = models.DateTimeField(null=True)
    date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(unique=True)
    def save(self, *args, **kwargs):
        self.title = self.file.slug
        self.slug = slugify(self.title+" "+ str(self.id))
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

