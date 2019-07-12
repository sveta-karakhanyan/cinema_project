from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Room(models.Model):
    room_name = models.CharField(max_length=50, null=False, blank=False)

    def __str__(self):
        return self.room_name


class Seat(models.Model):
    row = models.IntegerField(null=False, blank=False)
    column = models.IntegerField(null=False, blank=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)


class Film(models.Model):
    name = models.CharField(max_length=50, null=False, blank=False)
    duration = models.TimeField(null=False, auto_now=False, auto_now_add=False)

    def __str__(self):
        return self.name


class Seance(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    film = models.ForeignKey(Film, on_delete=models.CASCADE)
    date = models.DateField(null=False, auto_now=False, auto_now_add=False)
    start_time = models.TimeField(null=False, auto_now=False, auto_now_add=False)


class Booking(models.Model):
    row = models.IntegerField()
    column = models.IntegerField()
    seance = models.ForeignKey(Seance, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)


class Reserve(models.Model):
    row = models.IntegerField()
    column = models.IntegerField()
    seance = models.ForeignKey(Seance, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
