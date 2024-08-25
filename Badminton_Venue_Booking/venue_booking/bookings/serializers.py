# serializers.py
from rest_framework import serializers
from .models import Venue, Booking, Profile

class VenueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Venue
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = '__all__'

class BookingSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Booking
        fields = ['user', 'venue', 'date', 'start_time', 'end_time']
