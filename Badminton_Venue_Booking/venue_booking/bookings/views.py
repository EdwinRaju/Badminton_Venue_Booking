from rest_framework.response import Response
from rest_framework import generics, status
from .models import Booking, Venue, Profile
from .serializers import BookingSerializer
from datetime import datetime, timedelta,date
from .serializers import BookingSerializer
from rest_framework.views import APIView


class BookingCreateView(generics.CreateAPIView):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        user_id = request.data.get('user')
        try:
            user = Profile.objects.get(pk=user_id)
        except Profile.DoesNotExist:
            return Response(
                {"message": f"User with ID {user_id} does not exist."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if serializer.is_valid():
            venue = serializer.validated_data.get('venue')
            start_time = serializer.validated_data.get('start_time')
            end_time = serializer.validated_data.get('end_time')
            booking_date = serializer.validated_data.get('date')
            
            booking_start_datetime = datetime.combine(booking_date, start_time)
            booking_end_datetime = datetime.combine(booking_date, end_time)
            current_datetime = datetime.now()

            if booking_start_datetime < current_datetime or booking_end_datetime < current_datetime:
                return Response(
                    {"message": "Cannot book for a past time."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            today = current_datetime.date()
            one_month_later = today + timedelta(days=30)
            if not (today <= booking_date <= one_month_later):
                return Response(
                    {"message": f"Booking date must be within one month from today: {today} - {one_month_later}"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if not self.is_within_venue_hours(venue, start_time, end_time):
                return Response(
                    {"message": "Booking time must be within the venue's opening and closing hours."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if start_time >= end_time:
                return Response(
                    {"message": "End time must be after start time."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            overlapping_bookings = self.get_overlapping_bookings(venue, booking_date, start_time, end_time)
            if overlapping_bookings.exists():
                available_slots = self.get_available_slots(venue, booking_date)
                if not available_slots:
                    return Response(
                        {"message": "No slots are available today."},
                        status=status.HTTP_400_BAD_REQUEST
                        )

                return Response(
                    {"message": "This time slot is already booked.", "available_slots": available_slots},
                    status=status.HTTP_400_BAD_REQUEST
                )

            self.perform_create(serializer)
            return Response(
                {"message": "Booking created successfully."},
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def is_within_venue_hours(self, venue, start_time, end_time):
        if start_time < venue.opening_time or end_time > venue.closing_time:
            return False
        return True

    def get_overlapping_bookings(self, venue, date, start_time, end_time):
        return Booking.objects.filter(
            venue=venue,
            date=date,
            start_time__lt=end_time,
            end_time__gt=start_time
        )

    def get_available_slots(self, venue, date):
        bookings = Booking.objects.filter(venue=venue, date=date).order_by('start_time')
        available_slots = []

        venue_opening_time = venue.opening_time
        venue_closing_time = venue.closing_time

        current_time = venue_opening_time
        
        for booking in bookings:
            if current_time < booking.start_time:
                available_slots.append((current_time, booking.start_time))
            current_time = max(current_time, booking.end_time)

        if current_time < venue_closing_time:
            available_slots.append((current_time, venue_closing_time))

        now = datetime.now().time()
        if date == datetime.now().date():
            available_slots = [
                (start, end) for start, end in available_slots
                if start > now or (start == now and end > now)
            ]

        return available_slots




class VenuePerformanceView(APIView):
    def get(self, request):
        performance = {}
        
        months_with_bookings = Booking.objects.dates('date', 'month', order='ASC')

        month_mapping = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 
                         7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
        
        category_order = ['Category A', 'Category B', 'Category C', 'Category D']
        
        for booking_month in months_with_bookings:
            monthly_performance = {}
            month_name = month_mapping[booking_month.month]

            for category in category_order:
                monthly_performance[category] = []

            for venue in Venue.objects.all():
                count = Booking.objects.filter(venue=venue, date__month=booking_month.month).count()
                
                if count > 15:
                    category = 'Category A'
                elif 10 <= count <= 15:
                    category = 'Category B'
                elif 5 <= count < 10:
                    category = 'Category C'
                else:
                    category = 'Category D'
                
                if count > 0:
                    monthly_performance[category].append(venue.name)
            
            monthly_performance = {cat: venues for cat, venues in monthly_performance.items() if venues}

            if monthly_performance:
                performance[month_name] = monthly_performance
        
        return Response(performance)
