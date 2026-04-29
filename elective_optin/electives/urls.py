"""URL patterns for the electives app"""

from django.urls import path
from . import views

urlpatterns = [
    # Core pages
    path('', views.CatalogView.as_view(), name='home'),
    path('catalog/', views.CatalogView.as_view(), name='catalog'),
    path('submit/', views.SubmitPreferenceView.as_view(), name='submit_preference'),
    path('results/', views.ResultsView.as_view(), name='results'),

    # Admin
    path('dashboard/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('export/csv/', views.CSVExportView.as_view(), name='csv_export'),
    path('dashboard/preference/<int:pref_id>/accept/', views.AcceptPreferenceView.as_view(), name='accept_preference'),
    path('dashboard/preference/<int:pref_id>/reject/', views.RejectPreferenceView.as_view(), name='reject_preference'),

    # Auth
    path('register/', views.RegisterView.as_view(), name='register'),

    # API (DRF)
    path('api/seats/', views.AllCoursesSeatsAPIView.as_view(), name='api_all_seats'),
    path('api/seats/<int:course_id>/', views.SeatAvailabilityAPIView.as_view(), name='api_seat_availability'),
]
