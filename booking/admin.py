from django.contrib import admin

from .models import (
    Booking,
    Bus,
    Complaint,
    Conductor,
    District,
    Driver,
    Location,
    Notification,
    Passenger,
    Payment,
    Review,
    Route,
    Seat,
    Ticket,
    Trip,
    UserProfile,
)


class SeatInline(admin.TabularInline):
    model = Seat
    extra = 0


class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("booking_reference", "user", "trip", "travel_date", "status", "total_amount")
    list_filter = ("status", "travel_date", "trip__bus__category")
    search_fields = ("booking_reference", "user__username", "trip__route__source__name", "trip__route__destination__name")
    inlines = [SeatInline, PassengerInline]


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("source", "destination", "distance_km", "base_fare", "is_popular")
    list_filter = ("is_popular", "source__district")
    search_fields = ("source__name", "destination__name")


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ("route", "bus", "departure_time", "arrival_time", "fare_multiplier", "is_active")
    list_filter = ("is_active", "bus__category", "service_days")


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):
    list_display = ("name", "registration_number", "category", "total_seats", "is_active")
    list_filter = ("category", "is_active")
    search_fields = ("name", "registration_number")


for model in [District, Location, Driver, Conductor, UserProfile, Payment, Ticket, Review, Notification, Complaint]:
    admin.site.register(model)
