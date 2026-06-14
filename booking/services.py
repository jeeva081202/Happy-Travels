import uuid
from decimal import Decimal

from django.db import transaction

from .models import Booking, Passenger, Payment, Seat, Ticket, Trip


def dynamic_fare(trip, travel_date, seat_count=1):
    available = trip.available_seats(travel_date)
    occupancy_factor = Decimal("1.18") if available < trip.bus.total_seats * 0.25 else Decimal("1.00")
    weekend_factor = Decimal("1.10") if travel_date.weekday() in (4, 5, 6) else Decimal("1.00")
    return (trip.fare * occupancy_factor * weekend_factor * seat_count).quantize(Decimal("0.01"))


def seat_map(trip, travel_date):
    booked = set(Seat.objects.filter(
        booking__trip=trip,
        booking__travel_date=travel_date,
        booking__status="CONFIRMED",
    ).values_list("seat_number", flat=True))
    return [
        {"number": str(index), "is_booked": str(index) in booked}
        for index in range(1, trip.bus.total_seats + 1)
    ]


@transaction.atomic
def create_booking(user, trip_id, travel_date, seat_numbers, passengers):
    trip = Trip.objects.select_for_update().get(id=trip_id, is_active=True)
    occupied = set(Seat.objects.filter(
        booking__trip=trip,
        booking__travel_date=travel_date,
        booking__status="CONFIRMED",
        seat_number__in=seat_numbers,
    ).values_list("seat_number", flat=True))
    if occupied:
        raise ValueError(f"Seats already booked: {', '.join(sorted(occupied))}")

    booking = Booking.objects.create(
        user=user,
        trip=trip,
        travel_date=travel_date,
        status="CONFIRMED",
        total_amount=dynamic_fare(trip, travel_date, len(seat_numbers)),
    )
    for seat in seat_numbers:
        Seat.objects.create(booking=booking, seat_number=seat)
    for passenger in passengers:
        Passenger.objects.create(booking=booking, **passenger)
    Payment.objects.create(
        booking=booking,
        amount=booking.total_amount,
        transaction_id=f"PAY-{uuid.uuid4().hex[:12].upper()}",
    )
    Ticket.objects.create(
        booking=booking,
        qr_payload=f"TNT|{booking.booking_reference}|{booking.trip.route}|{booking.travel_date}|{booking.total_amount}",
    )
    return booking


def suggest_routes(source):
    return Trip.objects.filter(route__source__name__icontains=source, is_active=True).select_related(
        "route__source", "route__destination", "bus"
    )[:6]
