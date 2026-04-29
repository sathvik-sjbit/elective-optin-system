"""Django admin configuration for electives app"""

from django.contrib import admin
from .models import Department, Course, Student, StudentCourseHistory, Preference, Allocation


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['code', 'name']
    search_fields = ['name', 'code']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'title', 'department', 'category', 'total_seats', 'available_seats', 'is_active']
    list_filter = ['category', 'department', 'is_active']
    search_fields = ['title', 'code']
    list_editable = ['available_seats', 'is_active']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['roll_number', 'user', 'branch', 'current_semester', 'cgpa']
    list_filter = ['branch', 'current_semester']
    search_fields = ['roll_number', 'user__first_name', 'user__last_name']


@admin.register(StudentCourseHistory)
class StudentCourseHistoryAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'semester_completed', 'grade']


@admin.register(Preference)
class PreferenceAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'rank', 'status', 'timestamp', 'waitlist_position']
    list_filter = ['status', 'course__department']
    search_fields = ['student__roll_number', 'course__code']
    list_editable = ['status']


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'allocated_at', 'is_admin_override']
    list_filter = ['course__department', 'is_admin_override']
    search_fields = ['student__roll_number', 'course__code']
