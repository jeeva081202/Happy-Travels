from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", auth_views.LoginView.as_view(template_name="booking/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("profile/", views.profile, name="profile"),
    path("routes/", views.routes, name="routes"),
    path("routes/<int:route_id>/favorite/", views.add_favorite_route, name="add_favorite_route"),
    path("search/", views.search, name="search"),
    path("select-seat/<int:trip_id>/<str:travel_date>/", views.select_seat, name="select_seat"),
    path("bookings/", views.booking_history, name="booking_history"),
    path("notifications/", views.notifications, name="notifications"),
    path("complaints/", views.complaints, name="complaints"),
    path("review/<int:trip_id>/", views.add_review, name="add_review"),
    path("ticket/<str:reference>/", views.ticket_detail, name="ticket_detail"),
    path("ticket/<str:reference>/download/", views.download_ticket, name="download_ticket"),
    path("booking/<str:reference>/cancel/", views.cancel_booking, name="cancel_booking"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("management/", views.management_center, name="management_center"),
    path("management/<str:module_slug>/", views.module_list, name="module_list"),
    path("api/routes/", views.api_routes, name="api_routes"),
    path("api/buses/", views.api_buses, name="api_buses"),
    path("api/tracking/<int:trip_id>/", views.api_tracking, name="api_tracking"),
    path("api/verify/<str:reference>/", views.api_verify_ticket, name="api_verify_ticket"),
    path("api/dashboard/", views.api_dashboard_stats, name="api_dashboard_stats"),
]
