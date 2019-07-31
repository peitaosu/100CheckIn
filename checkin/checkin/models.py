from django.db import models

class Event(models.Model):
    eid = models.IntegerField(unique=True)
    ueid = models.IntegerField()
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=128)
    picture = models.ImageField(blank=True)
    checkin_time = models.DateTimeField(null=True, blank=True)

    EVENT_STATUS_CHOICES = (
        ('ADDED', 'Event Added'),
        ('DONE', 'Event Done'),
    )

    status = models.CharField(
        max_length=5,
        choices=EVENT_STATUS_CHOICES,
        default='ADDED',
    )

    def __str__(self):
        return self.title

class User(models.Model):
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=64, blank=True)

    def __str__(self):
        return self.name

class User_Event(models.Model):
    user = models.ForeignKey("User", on_delete=User)
    event = models.ForeignKey("Event", on_delete=Event)

    def __str__(self):
        return "User: {} Event: {}".format(self.user, self.event)

