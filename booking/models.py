import uuid
from decimal import Decimal

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class District(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    region = models.CharField(max_length=80, blank=True)
    is_tourist_destination = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Location(TimeStampedModel):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="locations")
    name = models.CharField(max_length=100)
    location_type = models.CharField(max_length=40, default="Town")

    class Meta:
        unique_together = ("district", "name")
        ordering = ["name"]

    def __str__(self):
        return self.name


class Driver(TimeStampedModel):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    license_number = models.CharField(max_length=40, unique=True)
    years_experience = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Conductor(TimeStampedModel):
    name = models.CharField(max_length=120)
    phone = models.CharField(max_length=20)
    employee_id = models.CharField(max_length=40, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Bus(TimeStampedModel):
    GOVERNMENT = "Government Bus"
    SETC = "SETC"
    TNSTC = "TNSTC"
    DELUXE = "Deluxe"
    ULTRA_DELUXE = "Ultra Deluxe"
    AC_SLEEPER = "AC Sleeper"
    NON_AC_SLEEPER = "Non AC Sleeper"
    VOLVO = "Volvo"
    SEMI_SLEEPER = "Semi Sleeper"
    LUXURY = "Luxury Coach"

    CATEGORY_CHOICES = [(value, value) for value in [
        GOVERNMENT, SETC, TNSTC, DELUXE, ULTRA_DELUXE, AC_SLEEPER,
        NON_AC_SLEEPER, VOLVO, SEMI_SLEEPER, LUXURY,
    ]]

    name = models.CharField(max_length=140)
    registration_number = models.CharField(max_length=30, unique=True)
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES)
    total_seats = models.PositiveSmallIntegerField(default=40)
    amenities = models.CharField(max_length=255, blank=True)
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.SET_NULL)
    conductor = models.ForeignKey(Conductor, null=True, blank=True, on_delete=models.SET_NULL)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.category})"


class Route(TimeStampedModel):
    source = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="departing_routes")
    destination = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="arriving_routes")
    distance_km = models.PositiveIntegerField()
    estimated_minutes = models.PositiveIntegerField()
    base_fare = models.DecimalField(max_digits=8, decimal_places=2)
    is_popular = models.BooleanField(default=False)

    class Meta:
        unique_together = ("source", "destination")
        ordering = ["source__name", "destination__name"]

    def __str__(self):
        return f"{self.source} to {self.destination}"


class Trip(TimeStampedModel):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="trips")
    bus = models.ForeignKey(Bus, on_delete=models.PROTECT, related_name="trips")
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    service_days = models.CharField(max_length=80, default="Daily")
    fare_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("1.00"))
    tracking_lat = models.DecimalField(max_digits=9, decimal_places=6, default=Decimal("13.082680"))
    tracking_lng = models.DecimalField(max_digits=9, decimal_places=6, default=Decimal("80.270721"))
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["departure_time"]

    @property
    def fare(self):
        return (self.route.base_fare * self.fare_multiplier).quantize(Decimal("0.01"))

    def available_seats(self, travel_date):
        booked = Seat.objects.filter(booking__trip=self, booking__travel_date=travel_date, booking__status="CONFIRMED").count()
        return max(self.bus.total_seats - booked, 0)

    def __str__(self):
        return f"{self.route} - {self.departure_time}"


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    phone = models.CharField(max_length=20, blank=True)
    gender = models.CharField(max_length=20, blank=True)
    preferred_language = models.CharField(max_length=20, default="English")
    favorite_routes = models.ManyToManyField(Route, blank=True)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Booking(TimeStampedModel):
    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
    ]

    booking_reference = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bookings")
    trip = models.ForeignKey(Trip, on_delete=models.PROTECT, related_name="bookings")
    travel_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.booking_reference:
            self.booking_reference = f"TNT{uuid.uuid4().hex[:9].upper()}"
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("ticket_detail", args=[self.booking_reference])

    def __str__(self):
        return self.booking_reference


class Passenger(TimeStampedModel):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="passengers")
    name = models.CharField(max_length=120)
    age = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(110)])
    gender = models.CharField(max_length=20)
    phone = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.name


class Seat(TimeStampedModel):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="seats")
    seat_number = models.CharField(max_length=5)

    class Meta:
        unique_together = ("booking", "seat_number")

    def __str__(self):
        return self.seat_number


class Payment(TimeStampedModel):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="payment")
    provider = models.CharField(max_length=40, default="Demo Gateway")
    transaction_id = models.CharField(max_length=80, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, default="SUCCESS")

    def __str__(self):
        return self.transaction_id


class Ticket(TimeStampedModel):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name="ticket")
    qr_payload = models.TextField()
    pdf_file = models.FileField(upload_to="tickets/", blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Ticket {self.booking.booking_reference}"


class Review(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name="reviews")
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ("user", "trip")
        ordering = ["-created_at"]


class Notification(TimeStampedModel):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.CASCADE, related_name="notifications")
    title = models.CharField(max_length=140)
    message = models.TextField()
    audience = models.CharField(max_length=40, default="Passenger")
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Complaint(TimeStampedModel):
    booking = models.ForeignKey(Booking, null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=160)
    message = models.TextField()
    status = models.CharField(max_length=30, default="Open")

    def __str__(self):
        return self.subject
