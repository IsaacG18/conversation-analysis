from django.db import models


# Create your models here.

class File(models.Model):
    file = models.FileField(upload_to="uploads/")
    title = models.CharField(max_length=128, unique=True)
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        partition = self.file.name.partition("uploads/")
        if len(partition[2]) == 0:
            self.title = partition[0]
        else:
            self.title = partition[2]
        super(File, self).save(*args, **kwargs)

    def __str__(self):
        return self.title


class Message(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    sender = models.CharField(max_length=50)
    content = models.CharField(max_length=1000)

    def __str__(self):
        return self.sender + self.timestamp.__str__()


class Analysis(models.Model):
    file = models.ForeignKey(File, null=True, on_delete=models.SET_NULL)

    class Meta:
        verbose_name_plural = "Analyses"
    def __str__(self):
        return self.file.__str__()


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


class RiskWord(models.Model):
    analysis = models.ForeignKey(Analysis, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=50)
    risk_factor = models.FloatField(default=0)
    amount = models.IntegerField(default=0)

    def __str__(self):
        return self.keyword.__str__()