from datetime import time
from decimal import Decimal

from django.core.management.base import BaseCommand

from booking.models import Bus, Conductor, District, Driver, Location, Route, Trip


DISTRICTS = [
    "Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", "Thanjavur", "Erode",
    "Dindigul", "Theni", "Virudhunagar", "Sivagangai", "Ramanathapuram", "Kanyakumari", "Cuddalore",
    "Villupuram", "Kallakurichi", "Vellore", "Tirupathur", "Ranipet", "Tiruvannamalai", "Namakkal",
    "Karur", "Perambalur", "Ariyalur", "Nagapattinam", "Mayiladuthurai", "Tiruvarur", "Pudukkottai",
    "Dharmapuri", "Krishnagiri", "Tiruppur", "Nilgiris", "Chengalpattu", "Kanchipuram", "Tiruvallur",
    "Tenkasi", "Tuticorin",
]

TOURIST_TOWNS = {
    "Nilgiris": ["Ooty", "Coonoor"],
    "Ramanathapuram": ["Rameswaram"],
    "Thanjavur": ["Kumbakonam"],
    "Tiruchirappalli": ["Trichy"],
    "Theni": ["Bodinayakanur", "Munnar Gateway"],
    "Kanyakumari": ["Kanyakumari"],
    "Tirunelveli": ["Courtallam"],
}

ROUTES = [
    ("Chennai", "Madurai", 462, 480, "760.00"), ("Chennai", "Coimbatore", 508, 520, "840.00"),
    ("Chennai", "Salem", 343, 380, "560.00"), ("Chennai", "Tirunelveli", 625, 660, "980.00"),
    ("Chennai", "Kanyakumari", 705, 750, "1150.00"), ("Chennai", "Theni", 530, 560, "900.00"),
    ("Chennai", "Tiruchirappalli", 330, 360, "540.00"), ("Chennai", "Erode", 410, 440, "680.00"),
    ("Chennai", "Ooty", 555, 620, "1020.00"), ("Chennai", "Rameswaram", 560, 600, "940.00"),
    ("Madurai", "Coimbatore", 214, 260, "390.00"), ("Madurai", "Theni", 76, 105, "140.00"),
    ("Madurai", "Tirunelveli", 162, 190, "260.00"), ("Madurai", "Tiruchirappalli", 134, 160, "220.00"),
    ("Coimbatore", "Salem", 165, 190, "280.00"), ("Coimbatore", "Erode", 100, 120, "170.00"),
    ("Coimbatore", "Ooty", 85, 180, "240.00"), ("Tiruchirappalli", "Thanjavur", 58, 80, "110.00"),
    ("Tiruchirappalli", "Kumbakonam", 98, 130, "170.00"), ("Theni", "Bodinayakanur", 16, 35, "55.00"),
    ("Theni", "Chennai", 530, 560, "900.00"), ("Theni", "Coimbatore", 205, 260, "370.00"),
]


class Command(BaseCommand):
    help = "Seed Tamil Nadu districts, towns, routes, buses, drivers, conductors, and trips."

    def handle(self, *args, **options):
        locations = {}
        for name in DISTRICTS:
            district, _ = District.objects.get_or_create(name=name, defaults={"region": "Tamil Nadu"})
            location, _ = Location.objects.get_or_create(district=district, name=name, defaults={"location_type": "District"})
            locations[name] = location

        for district_name, towns in TOURIST_TOWNS.items():
            district = District.objects.get(name=district_name)
            district.is_tourist_destination = True
            district.save(update_fields=["is_tourist_destination"])
            for town in towns:
                locations[town], _ = Location.objects.get_or_create(district=district, name=town, defaults={"location_type": "Tourist"})

        driver, _ = Driver.objects.get_or_create(name="R Kumar", license_number="TN-DRV-1001", defaults={"phone": "9000001001", "years_experience": 12})
        conductor, _ = Conductor.objects.get_or_create(name="S Prakash", employee_id="TN-CON-1001", defaults={"phone": "9000002001"})

        categories = [choice[0] for choice in Bus.CATEGORY_CHOICES]
        buses = []
        for index, category in enumerate(categories, start=1):
            bus, _ = Bus.objects.get_or_create(
                registration_number=f"TN 01 TT {1000 + index}",
                defaults={
                    "name": f"Happy Travels {category}",
                    "category": category,
                    "total_seats": 36 if "Sleeper" in category else 40,
                    "amenities": "GPS, Charging, Water Bottle, Reading Light",
                    "driver": driver,
                    "conductor": conductor,
                },
            )
            buses.append(bus)

        for index, (source, destination, distance, minutes, fare) in enumerate(ROUTES):
            route, _ = Route.objects.get_or_create(
                source=locations[source],
                destination=locations[destination],
                defaults={
                    "distance_km": distance,
                    "estimated_minutes": minutes,
                    "base_fare": Decimal(fare),
                    "is_popular": True,
                },
            )
            bus = buses[index % len(buses)]
            Trip.objects.get_or_create(
                route=route,
                bus=bus,
                departure_time=time((index * 2 + 6) % 24, 30),
                defaults={
                    "arrival_time": time((index * 2 + 12) % 24, 15),
                    "fare_multiplier": Decimal("1.15") if bus.category in ["Volvo", "Luxury Coach", "AC Sleeper"] else Decimal("1.00"),
                    "service_days": "Daily",
                },
            )
            reverse_route, _ = Route.objects.get_or_create(
                source=locations[destination],
                destination=locations[source],
                defaults={
                    "distance_km": distance,
                    "estimated_minutes": minutes,
                    "base_fare": Decimal(fare),
                    "is_popular": True,
                },
            )
            Trip.objects.get_or_create(
                route=reverse_route,
                bus=bus,
                departure_time=time((index * 2 + 14) % 24, 45),
                defaults={
                    "arrival_time": time((index * 2 + 20) % 24, 30),
                    "fare_multiplier": Decimal("1.15") if bus.category in ["Volvo", "Luxury Coach", "AC Sleeper"] else Decimal("1.00"),
                    "service_days": "Daily",
                },
            )

        self.stdout.write(self.style.SUCCESS("Tamil Nadu statewide travel data seeded successfully."))
