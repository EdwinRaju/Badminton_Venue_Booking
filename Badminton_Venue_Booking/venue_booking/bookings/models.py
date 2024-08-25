from django.db import models

class Profile(models.Model):
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name

class Venue(models.Model):
    name = models.CharField(max_length=100)
    opening_time = models.TimeField()
    closing_time = models.TimeField()

    def __str__(self):
        return self.name

class Booking(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()
    date = models.DateField()

