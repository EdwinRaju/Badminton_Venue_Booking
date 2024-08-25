from django.urls import path
from .views import BookingCreateView, VenuePerformanceView

urlpatterns = [
    path('book', BookingCreateView.as_view(), name='book-venue'),
    path('performance', VenuePerformanceView.as_view(), name='venue-performance'),

]
