"""
Django REST Framework serializers for the Elective Opt-In API.
Provides seat availability endpoint consumed by AJAX frontend.
"""

from rest_framework import serializers
from .models import Course, Preference, Allocation


class SeatAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for real-time seat availability (used by AJAX)"""
    department_name = serializers.CharField(source='department.name', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    seats_taken = serializers.IntegerField(read_only=True)
    is_full = serializers.BooleanField(read_only=True)
    waitlist_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'code', 'title', 'department_name', 'category_display',
            'total_seats', 'available_seats', 'seats_taken', 'is_full',
            'waitlist_count',
        ]

    def get_waitlist_count(self, obj):
        return obj.preferences.filter(status='waitlisted').count()


class CourseSerializer(serializers.ModelSerializer):
    """Full course detail serializer"""
    department_name = serializers.CharField(source='department.name', read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'code', 'title', 'category', 'department_name',
            'salient_features', 'job_perspective', 'prerequisites',
            'total_seats', 'available_seats', 'semester_offered', 'is_active',
        ]
