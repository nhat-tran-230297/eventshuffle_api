from django.db import models

# Create your models here.
class Event(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.id} - {self.name}"


class Date(models.Model):
    date_format = models.CharField(max_length=10)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='dates')

    def __str__(self):
        return f"{self.id} - {self.event}"

class Participant(models.Model):
    name = models.CharField(max_length=100)
    votes = models.ManyToManyField(Date, blank=True, related_name='participants')

    def __str__(self):
        return f"{self.id} - {self.name}"