# Generated for TamilNadu Travels initial schema.
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Conductor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("phone", models.CharField(max_length=20)),
                ("employee_id", models.CharField(max_length=40, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="District",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=80, unique=True)),
                ("region", models.CharField(blank=True, max_length=80)),
                ("is_tourist_destination", models.BooleanField(default=False)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Driver",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("phone", models.CharField(max_length=20)),
                ("license_number", models.CharField(max_length=40, unique=True)),
                ("years_experience", models.PositiveSmallIntegerField(default=1)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Bus",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=140)),
                ("registration_number", models.CharField(max_length=30, unique=True)),
                ("category", models.CharField(choices=[("Government Bus", "Government Bus"), ("SETC", "SETC"), ("TNSTC", "TNSTC"), ("Deluxe", "Deluxe"), ("Ultra Deluxe", "Ultra Deluxe"), ("AC Sleeper", "AC Sleeper"), ("Non AC Sleeper", "Non AC Sleeper"), ("Volvo", "Volvo"), ("Semi Sleeper", "Semi Sleeper"), ("Luxury Coach", "Luxury Coach")], max_length=40)),
                ("total_seats", models.PositiveSmallIntegerField(default=40)),
                ("amenities", models.CharField(blank=True, max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("conductor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="booking.conductor")),
                ("driver", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="booking.driver")),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Location",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100)),
                ("location_type", models.CharField(default="Town", max_length=40)),
                ("district", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="locations", to="booking.district")),
            ],
            options={"ordering": ["name"], "unique_together": {("district", "name")}},
        ),
        migrations.CreateModel(
            name="Notification",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("title", models.CharField(max_length=140)),
                ("message", models.TextField()),
                ("audience", models.CharField(default="Passenger", max_length=40)),
                ("is_read", models.BooleanField(default=False)),
                ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="notifications", to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Route",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("distance_km", models.PositiveIntegerField()),
                ("estimated_minutes", models.PositiveIntegerField()),
                ("base_fare", models.DecimalField(decimal_places=2, max_digits=8)),
                ("is_popular", models.BooleanField(default=False)),
                ("destination", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="arriving_routes", to="booking.location")),
                ("source", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="departing_routes", to="booking.location")),
            ],
            options={"ordering": ["source__name", "destination__name"], "unique_together": {("source", "destination")}},
        ),
        migrations.CreateModel(
            name="Trip",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("departure_time", models.TimeField()),
                ("arrival_time", models.TimeField()),
                ("service_days", models.CharField(default="Daily", max_length=80)),
                ("fare_multiplier", models.DecimalField(decimal_places=2, default="1.00", max_digits=4)),
                ("tracking_lat", models.DecimalField(decimal_places=6, default="13.082680", max_digits=9)),
                ("tracking_lng", models.DecimalField(decimal_places=6, default="80.270721", max_digits=9)),
                ("is_active", models.BooleanField(default=True)),
                ("bus", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="trips", to="booking.bus")),
                ("route", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="trips", to="booking.route")),
            ],
            options={"ordering": ["departure_time"]},
        ),
        migrations.CreateModel(
            name="Booking",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("booking_reference", models.CharField(editable=False, max_length=20, unique=True)),
                ("travel_date", models.DateField()),
                ("status", models.CharField(choices=[("PENDING", "Pending"), ("CONFIRMED", "Confirmed"), ("CANCELLED", "Cancelled")], default="PENDING", max_length=20)),
                ("total_amount", models.DecimalField(decimal_places=2, default="0.00", max_digits=10)),
                ("trip", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="bookings", to="booking.trip")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bookings", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="Passenger",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=120)),
                ("age", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(110)])),
                ("gender", models.CharField(max_length=20)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("booking", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="passengers", to="booking.booking")),
            ],
        ),
        migrations.CreateModel(
            name="Payment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("provider", models.CharField(default="Demo Gateway", max_length=40)),
                ("transaction_id", models.CharField(max_length=80, unique=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("status", models.CharField(default="SUCCESS", max_length=20)),
                ("booking", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="payment", to="booking.booking")),
            ],
        ),
        migrations.CreateModel(
            name="Seat",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("seat_number", models.CharField(max_length=5)),
                ("booking", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="seats", to="booking.booking")),
            ],
            options={"unique_together": {("booking", "seat_number")}},
        ),
        migrations.CreateModel(
            name="Ticket",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("qr_payload", models.TextField()),
                ("pdf_file", models.FileField(blank=True, upload_to="tickets/")),
                ("verified_at", models.DateTimeField(blank=True, null=True)),
                ("booking", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="ticket", to="booking.booking")),
            ],
        ),
        migrations.CreateModel(
            name="Complaint",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("subject", models.CharField(max_length=160)),
                ("message", models.TextField()),
                ("status", models.CharField(default="Open", max_length=30)),
                ("booking", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="booking.booking")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("rating", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ("comment", models.TextField(blank=True)),
                ("trip", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reviews", to="booking.trip")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at"], "unique_together": {("user", "trip")}},
        ),
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("phone", models.CharField(blank=True, max_length=20)),
                ("gender", models.CharField(blank=True, max_length=20)),
                ("preferred_language", models.CharField(default="English", max_length=20)),
                ("favorite_routes", models.ManyToManyField(blank=True, to="booking.route")),
                ("user", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="profile", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
