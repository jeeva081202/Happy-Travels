from datetime import date

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import Count, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.utils.dateparse import parse_date

from .forms import ComplaintForm, ProfileForm, RegisterForm, ReviewForm, SearchForm
from .models import Booking, Bus, Complaint, Conductor, District, Driver, Location, Notification, Payment, Review, Route, Ticket, Trip, UserProfile
from .services import create_booking, dynamic_fare, seat_map, suggest_routes


STAFF_MODULES = {
    "buses": {"title": "Bus Management", "model": Bus, "fields": ["name", "registration_number", "category", "total_seats", "is_active"]},
    "routes": {"title": "Route Management", "model": Route, "fields": ["source", "destination", "distance_km", "base_fare", "is_popular"]},
    "trips": {"title": "Trip Scheduling", "model": Trip, "fields": ["route", "bus", "departure_time", "arrival_time", "is_active"]},
    "drivers": {"title": "Driver Management", "model": Driver, "fields": ["name", "phone", "license_number", "years_experience", "is_active"]},
    "conductors": {"title": "Conductor Management", "model": Conductor, "fields": ["name", "phone", "employee_id", "is_active"]},
    "users": {"title": "User Management", "model": User, "fields": ["username", "email", "first_name", "is_staff", "is_active"]},
    "bookings": {"title": "Booking Management", "model": Booking, "fields": ["booking_reference", "user", "trip", "travel_date", "status", "total_amount"]},
    "payments": {"title": "Payment Reports", "model": Payment, "fields": ["transaction_id", "booking", "amount", "status", "provider"]},
    "tickets": {"title": "QR Ticket Verification", "model": Ticket, "fields": ["booking", "qr_payload", "verified_at", "created_at"]},
    "reviews": {"title": "Reviews and Ratings", "model": Review, "fields": ["user", "trip", "rating", "comment", "created_at"]},
    "notifications": {"title": "Notification System", "model": Notification, "fields": ["title", "audience", "is_read", "created_at"]},
    "complaints": {"title": "Complaint Management", "model": Complaint, "fields": ["user", "booking", "subject", "status", "created_at"]},
    "districts": {"title": "District Coverage", "model": District, "fields": ["name", "region", "is_tourist_destination"]},
    "locations": {"title": "Town and Tourist Destinations", "model": Location, "fields": ["name", "district", "location_type"]},
}


def home(request):
    form = SearchForm(initial={"travel_date": date.today()})
    popular_routes = Route.objects.filter(is_popular=True).select_related("source", "destination")[:8]
    districts = District.objects.all()
    suggestions = suggest_routes(request.GET.get("source", ""))
    return render(request, "booking/home.html", {
        "form": form,
        "popular_routes": popular_routes,
        "districts": districts,
        "suggestions": suggestions,
    })


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to Happy Travels. Your account is ready.")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "booking/register.html", {"form": form})


@login_required
def profile(request):
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile_obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile_obj)
    return render(request, "booking/profile.html", {"form": form})


def routes(request):
    route_list = Route.objects.select_related("source", "destination").all()
    return render(request, "booking/routes.html", {"routes": route_list})


@login_required
def add_favorite_route(request, route_id):
    route = get_object_or_404(Route, id=route_id)
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)
    profile_obj.favorite_routes.add(route)
    messages.success(request, "Route added to favorites.")
    return redirect("routes")


def search(request):
    form = SearchForm(request.GET)
    trips = []
    travel_date = None
    if form.is_valid():
        source = form.cleaned_data["source"]
        destination = form.cleaned_data["destination"]
        travel_date = form.cleaned_data["travel_date"]
        trips = Trip.objects.filter(
            route__source__name__icontains=source,
            route__destination__name__icontains=destination,
            is_active=True,
        ).select_related("route__source", "route__destination", "bus")
    return render(request, "booking/search_results.html", {"form": form, "trips": trips, "travel_date": travel_date})


@login_required
def select_seat(request, trip_id, travel_date):
    trip = get_object_or_404(Trip.objects.select_related("route", "bus"), id=trip_id, is_active=True)
    parsed_date = parse_date(travel_date)
    if parsed_date is None:
        messages.error(request, "Invalid travel date.")
        return redirect("home")
    seats = seat_map(trip, parsed_date)
    if request.method == "POST":
        seat_numbers = request.POST.get("seats", "").split(",")
        seat_numbers = [seat.strip() for seat in seat_numbers if seat.strip()]
        if not seat_numbers:
            messages.error(request, "Please select at least one seat.")
            return redirect("select_seat", trip_id=trip.id, travel_date=travel_date)
        passengers = []
        for seat in seat_numbers:
            passengers.append({
                "name": request.POST.get(f"name_{seat}", request.user.get_full_name() or request.user.username),
                "age": request.POST.get(f"age_{seat}", 25),
                "gender": request.POST.get(f"gender_{seat}", "Not specified"),
                "phone": request.POST.get(f"phone_{seat}", ""),
            })
        try:
            booking = create_booking(request.user, trip.id, parsed_date, seat_numbers, passengers)
            messages.success(request, "Ticket booked successfully.")
            return redirect(booking.get_absolute_url())
        except ValueError as exc:
            messages.error(request, str(exc))
    return render(request, "booking/select_seat.html", {
        "trip": trip,
        "travel_date": parsed_date,
        "seats": seats,
        "fare": dynamic_fare(trip, parsed_date),
    })


@login_required
def booking_history(request):
    bookings = Booking.objects.filter(user=request.user).select_related(
        "trip__route__source", "trip__route__destination", "ticket", "trip__bus"
    ).prefetch_related("seats", "passengers")
    return render(request, "booking/booking_history.html", {"bookings": bookings})


@login_required
def ticket_detail(request, reference):
    queryset = Booking.objects.select_related(
        "trip__route__source", "trip__route__destination", "ticket", "trip__bus", "payment"
    ).prefetch_related("seats", "passengers")
    if not request.user.is_staff:
        queryset = queryset.filter(user=request.user)
    booking = get_object_or_404(queryset, booking_reference=reference)
    return render(request, "booking/ticket.html", {"booking": booking})


@login_required
def download_ticket(request, reference):
    booking = get_object_or_404(Booking, booking_reference=reference, user=request.user)
    html = render_to_string("booking/ticket_pdf.html", {"booking": booking})
    response = HttpResponse(html, content_type="text/html")
    response["Content-Disposition"] = f'attachment; filename="{reference}-ticket.html"'
    return response


@login_required
def cancel_booking(request, reference):
    booking = get_object_or_404(Booking, booking_reference=reference, user=request.user)
    if booking.status == "CONFIRMED":
        booking.status = "CANCELLED"
        booking.save(update_fields=["status", "updated_at"])
        messages.success(request, "Booking cancelled. Refund processing has been initiated.")
    return redirect("booking_history")


@login_required
def notifications(request):
    items = Notification.objects.filter(user__isnull=True) | Notification.objects.filter(user=request.user)
    return render(request, "booking/notifications.html", {"notifications": items.order_by("-created_at")})


@login_required
def complaints(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST, user=request.user)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            messages.success(request, "Complaint submitted. Support team will review it.")
            return redirect("complaints")
    else:
        form = ComplaintForm(user=request.user)
    items = Complaint.objects.filter(user=request.user).order_by("-created_at")
    return render(request, "booking/complaints.html", {"form": form, "complaints": items})


@login_required
def add_review(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    review, _ = Review.objects.get_or_create(user=request.user, trip=trip, defaults={"rating": 5})
    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Review saved.")
            return redirect("booking_history")
    else:
        form = ReviewForm(instance=review)
    return render(request, "booking/review.html", {"form": form, "trip": trip})


@user_passes_test(lambda user: user.is_staff)
def dashboard(request):
    bookings = Booking.objects.select_related("trip__route").all()
    stats = {
        "bookings": bookings.count(),
        "revenue": bookings.filter(status="CONFIRMED").aggregate(total=Sum("total_amount"))["total"] or 0,
        "cancelled": bookings.filter(status="CANCELLED").count(),
        "routes": Route.objects.count(),
    }
    route_performance = Route.objects.annotate(bookings=Count("trips__bookings")).select_related("source", "destination").order_by("-bookings")[:10]
    modules = [
        {"slug": slug, "title": config["title"], "count": config["model"].objects.count()}
        for slug, config in STAFF_MODULES.items()
    ]
    return render(request, "booking/dashboard.html", {"stats": stats, "route_performance": route_performance, "modules": modules})


@user_passes_test(lambda user: user.is_staff)
def management_center(request):
    modules = [
        {"slug": slug, "title": config["title"], "count": config["model"].objects.count()}
        for slug, config in STAFF_MODULES.items()
    ]
    return render(request, "booking/management.html", {"modules": modules})


@user_passes_test(lambda user: user.is_staff)
def module_list(request, module_slug):
    config = STAFF_MODULES.get(module_slug)
    if config is None:
        messages.error(request, "Module not found.")
        return redirect("management_center")
    rows = config["model"].objects.all()[:100]
    return render(request, "booking/module_list.html", {
        "module": config,
        "module_slug": module_slug,
        "rows": rows,
        "fields": config["fields"],
    })


def api_routes(request):
    data = list(Route.objects.select_related("source", "destination").values(
        "id", "source__name", "destination__name", "distance_km", "estimated_minutes", "base_fare"
    ))
    return JsonResponse({"routes": data})


def api_buses(request):
    travel_date = parse_date(request.GET.get("date", str(date.today())))
    trips = Trip.objects.filter(
        route__source__name__icontains=request.GET.get("source", ""),
        route__destination__name__icontains=request.GET.get("destination", ""),
        is_active=True,
    ).select_related("route__source", "route__destination", "bus")
    data = [{
        "trip_id": trip.id,
        "bus": trip.bus.name,
        "category": trip.bus.category,
        "source": trip.route.source.name,
        "destination": trip.route.destination.name,
        "departure": trip.departure_time.strftime("%H:%M"),
        "arrival": trip.arrival_time.strftime("%H:%M"),
        "fare": str(dynamic_fare(trip, travel_date)),
        "available_seats": trip.available_seats(travel_date),
    } for trip in trips]
    return JsonResponse({"buses": data})


def api_tracking(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)
    return JsonResponse({
        "trip": trip.id,
        "status": "On time",
        "lat": str(trip.tracking_lat),
        "lng": str(trip.tracking_lng),
        "next_stop": trip.route.destination.name,
    })


def api_verify_ticket(request, reference):
    ticket = get_object_or_404(Ticket.objects.select_related("booking"), booking__booking_reference=reference)
    return JsonResponse({
        "reference": reference,
        "valid": ticket.booking.status == "CONFIRMED",
        "status": ticket.booking.status,
        "travel_date": ticket.booking.travel_date.isoformat(),
    })


@user_passes_test(lambda user: user.is_staff)
def api_dashboard_stats(request):
    confirmed = Booking.objects.filter(status="CONFIRMED")
    return JsonResponse({
        "revenue": str(confirmed.aggregate(total=Sum("total_amount"))["total"] or 0),
        "bookings": Booking.objects.count(),
        "occupancy": SeatOccupancy.snapshot(),
        "top_routes": list(Route.objects.annotate(bookings=Count("trips__bookings")).values("source__name", "destination__name", "bookings").order_by("-bookings")[:5]),
    })


class SeatOccupancy:
    @staticmethod
    def snapshot():
        total_seats = Bus.objects.aggregate(total=Sum("total_seats"))["total"] or 0
        booked = Booking.objects.filter(status="CONFIRMED").aggregate(total=Count("seats"))["total"] or 0
        if not total_seats:
            return 0
        return round((booked / total_seats) * 100, 2)
