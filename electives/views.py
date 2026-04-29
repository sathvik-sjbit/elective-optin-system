"""
Views for Priority-Based Elective Opt-In System.

Views:
- CatalogView: Browse courses with search/filter/pagination
- SubmitPreferenceView: Students submit ranked preferences
- ResultsView: Students see their allocation results
- AdminDashboardView: Admin overview with charts and override
- SeatAvailabilityAPIView: DRF endpoint for AJAX seat polling
- CSVExportView: Download allocation data as CSV
- RegisterView: Student registration
"""

import json
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, TemplateView
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.db.models import Q
from django.utils.decorators import method_decorator
from django.contrib.admin.views.decorators import staff_member_required

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Course, Student, Preference, Allocation, Department
from .forms import (
    StudentRegistrationForm, PreferenceForm,
    AdminAllocationOverrideForm, CourseFilterForm, AdminAddCourseForm
)
from .utils import allocate_seats, export_allocations_csv, get_course_preference_stats
from .serializers import SeatAvailabilitySerializer


# ---------------------------------------------------------------------------
# Registration & Auth Helpers
# ---------------------------------------------------------------------------

class RegisterView(View):
    """Student registration: creates User + Student profile"""

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('catalog')
        form = StudentRegistrationForm()
        return render(request, 'registration/register.html', {'form': form})

    def post(self, request):
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created! Please log in.")
            return redirect('login')
        return render(request, 'registration/register.html', {'form': form})


# ---------------------------------------------------------------------------
# Course Catalog
# ---------------------------------------------------------------------------

class CatalogView(LoginRequiredMixin, View):
    """
    Course catalog with:
    - Category and department filtering
    - Full-text search
    - Pagination (12 courses per page)
    """

    def get(self, request):
        form = CourseFilterForm(request.GET)
        courses = Course.objects.filter(is_active=True).select_related('department')

        # Apply filters
        if form.is_valid():
            category = form.cleaned_data.get('category')
            department = form.cleaned_data.get('department')
            search = form.cleaned_data.get('search')

            if category:
                courses = courses.filter(category=category)
            if department:
                courses = courses.filter(
                    Q(department__name__icontains=department) |
                    Q(department__code__icontains=department)
                )
            if search:
                courses = courses.filter(
                    Q(title__icontains=search) |
                    Q(code__icontains=search) |
                    Q(salient_features__icontains=search) |
                    Q(job_perspective__icontains=search)
                )

        # Pagination
        paginator = Paginator(courses, 9)
        page_obj = paginator.get_page(request.GET.get('page'))
        departments = Department.objects.all()

        return render(request, 'electives/catalog.html', {
            'page_obj': page_obj,
            'form': form,
            'departments': departments,
            'total_count': courses.count(),
        })


# ---------------------------------------------------------------------------
# Preference Submission
# ---------------------------------------------------------------------------

class SubmitPreferenceView(LoginRequiredMixin, View):
    """
    Allows students to submit ranked course preferences.
    Validates eligibility, prevents duplicates, enforces branch quota.
    """

    def _get_student(self, request):
        try:
            return request.user.student
        except Student.DoesNotExist:
            return None

    def get(self, request):
        student = self._get_student(request)
        if not student:
            messages.error(request, "Student profile not found. Contact admin.")
            return redirect('catalog')

        # Check if already has pending/allocated preferences
        existing_prefs = student.preferences.select_related('course').order_by('rank')
        form = PreferenceForm(student=student)

        return render(request, 'electives/submit.html', {
            'form': form,
            'student': student,
            'existing_prefs': existing_prefs,
        })

    def post(self, request):
        student = self._get_student(request)
        if not student:
            messages.error(request, "Student profile not found.")
            return redirect('catalog')

        form = PreferenceForm(student=student, data=request.POST)
        if form.is_valid():
            choices = [
                form.cleaned_data.get('choice1'),
                form.cleaned_data.get('choice2'),
                form.cleaned_data.get('choice3'),
            ]
            # Get current max rank for this student
            existing_max = student.preferences.count()
            created_count = 0

            for rank_offset, course in enumerate(choices):
                if course:
                    _, created = Preference.objects.get_or_create(
                        student=student,
                        course=course,
                        defaults={'rank': existing_max + rank_offset + 1}
                    )
                    if created:
                        created_count += 1

            if created_count > 0:
                messages.success(
                    request,
                    f"Successfully submitted {created_count} preference(s)! "
                    "Allocation results will be available after the deadline."
                )
            else:
                messages.warning(request, "No new preferences were added (already submitted?).")

            return redirect('results')

        existing_prefs = student.preferences.select_related('course').order_by('rank')
        return render(request, 'electives/submit.html', {
            'form': form,
            'student': student,
            'existing_prefs': existing_prefs,
        })


# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

class ResultsView(LoginRequiredMixin, View):
    """Student's allocation result page"""

    def get(self, request):
        try:
            student = request.user.student
        except Student.DoesNotExist:
            messages.error(request, "Student profile not found.")
            return redirect('catalog')

        preferences = student.preferences.select_related(
            'course__department'
        ).order_by('rank')

        allocation = student.allocations.select_related('course__department').first()

        return render(request, 'electives/results.html', {
            'student': student,
            'preferences': preferences,
            'allocation': allocation,
        })


# ---------------------------------------------------------------------------
# Admin Dashboard
# ---------------------------------------------------------------------------

@method_decorator(staff_member_required, name='dispatch')
class AdminDashboardView(View):
    """
    Admin overview dashboard with:
    - Allocation statistics
    - Chart.js preference visualization
    - Admin override form
    - Run allocation button
    """

    def get(self, request):
        # Stats
        total_students = Student.objects.count()
        total_prefs = Preference.objects.count()
        allocated_count = Preference.objects.filter(status='allocated').count()
        waitlisted_count = Preference.objects.filter(status='waitlisted').count()
        pending_count = Preference.objects.filter(status='pending').count()

        # Recent allocations
        recent_allocations = Allocation.objects.select_related(
            'student__user', 'course__department'
        ).order_by('-allocated_at')[:20]

        # Pending preferences - all pending, ordered by timestamp
        pending_preferences = (
            Preference.objects
            .select_related('student__user', 'course__department')
            .filter(status='pending')
            .order_by('timestamp', 'rank')
        )

        # Chart data
        chart_data = get_course_preference_stats()

        # Courses with seat info
        courses = Course.objects.select_related('department').order_by('department__name', 'title')

        # All students (for override dropdown)
        all_students = Student.objects.select_related('user').order_by('roll_number')

        # Departments (for add course modal)
        departments = Department.objects.all().order_by('name')

        # Override form & Add Course form
        override_form = AdminAllocationOverrideForm()
        add_course_form = AdminAddCourseForm()

        return render(request, 'electives/admin_dashboard.html', {
            'total_students': total_students,
            'total_prefs': total_prefs,
            'allocated_count': allocated_count,
            'waitlisted_count': waitlisted_count,
            'pending_count': pending_count,
            'recent_allocations': recent_allocations,
            'pending_preferences': pending_preferences,
            'chart_data': json.dumps(chart_data),
            'courses': courses,
            'all_students': all_students,
            'departments': departments,
            'override_form': override_form,
            'add_course_form': add_course_form,
        })

    def post(self, request):
        action = request.POST.get('action')

        if action == 'run_allocation':
            summary = allocate_seats()
            messages.success(
                request,
                f"Allocation complete! Allocated: {summary['allocated']}, "
                f"Waitlisted: {summary['waitlisted']}, Rejected: {summary['rejected']}"
            )

        elif action == 'admin_override':
            form = AdminAllocationOverrideForm(request.POST)
            if form.is_valid():
                allocation = form.save(commit=False)
                allocation.is_admin_override = True
                allocation.save()
                # Update course seat count
                course = allocation.course
                if course.available_seats > 0:
                    course.available_seats -= 1
                    course.save()
                messages.success(request, f"Admin override: {allocation.student} → {allocation.course}")
            else:
                messages.error(request, "Override form has errors. Check inputs.")

        elif action == 'add_course':
            form = AdminAddCourseForm(request.POST)
            if form.is_valid():
                course = form.save()
                messages.success(request, f"Course '{course.title}' ({course.code}) added successfully!")
            else:
                messages.error(request, f"Failed to add course. Please check the form inputs. Errors: {form.errors}")

        elif action == 'cancel_allocation':
            alloc_id = request.POST.get('allocation_id')
            alloc = get_object_or_404(Allocation, id=alloc_id)
            student_name = alloc.student.user.get_full_name()
            course_code = alloc.course.code
            alloc.delete()  # Signal handles seat restoration + waitlist promotion
            messages.success(request, f"Cancelled allocation of {student_name} from {course_code}. Waitlist promoted if applicable.")

        return redirect('admin_dashboard')


# ---------------------------------------------------------------------------
# CSV Export
# ---------------------------------------------------------------------------

@method_decorator(staff_member_required, name='dispatch')
class CSVExportView(View):
    """Download allocations as CSV, optionally filtered by department/category"""

    def get(self, request):
        department = request.GET.get('department', '')
        category = request.GET.get('category', '')

        csv_content = export_allocations_csv(
            department=department or None,
            category=category or None
        )

        response = HttpResponse(csv_content.read(), content_type='text/csv')
        response['Content-Disposition'] = (
            f'attachment; filename="allocations_{department or "all"}_{category or "all"}.csv"'
        )
        return response


# ---------------------------------------------------------------------------
# AJAX / API Views
# ---------------------------------------------------------------------------

class SeatAvailabilityAPIView(APIView):
    """
    DRF endpoint: GET /api/seats/<course_id>/
    Returns real-time seat availability for a single course.
    Consumed by AJAX polling in the frontend.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        course = get_object_or_404(Course, id=course_id)
        serializer = SeatAvailabilitySerializer(course)
        return Response(serializer.data)


class AllCoursesSeatsAPIView(APIView):
    """
    DRF endpoint: GET /api/seats/
    Returns seat availability for all active courses.
    Used by AJAX to refresh the entire catalog.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        courses = Course.objects.filter(is_active=True).select_related('department')
        serializer = SeatAvailabilitySerializer(courses, many=True)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# Admin: Accept / Reject a single pending preference
# ---------------------------------------------------------------------------

@method_decorator(staff_member_required, name='dispatch')
class AcceptPreferenceView(View):
    """
    Admin accepts a specific pending preference → creates an Allocation record.
    POST /dashboard/preference/<pref_id>/accept/
    """

    def post(self, request, pref_id):
        pref = get_object_or_404(Preference, id=pref_id, status='pending')
        course = pref.course
        student = pref.student

        # Check if student already has an allocation
        if student.allocations.exists():
            messages.error(
                request,
                f"{student.user.get_full_name()} is already allocated to another course."
            )
            return redirect('admin_dashboard')

        # Check seat availability
        if course.available_seats <= 0:
            messages.error(request, f"No available seats in {course.title}.")
            return redirect('admin_dashboard')

        with transaction.atomic():
            # Check if allocation already exists for this student-course pair
            if Allocation.objects.filter(student=student, course=course).exists():
                messages.warning(request, "This student is already allocated to this course.")
                return redirect('admin_dashboard')

            Allocation.objects.create(
                student=student,
                course=course,
                preference=pref,
                is_admin_override=True,
                notes="Manually accepted by admin"
            )
            course.available_seats -= 1
            course.save()
            pref.status = 'allocated'
            pref.save()

            # Mark other pending preferences for this student as rejected
            student.preferences.filter(status='pending').exclude(id=pref.id).update(status='rejected')

        messages.success(
            request,
            f"✅ Allocated {student.user.get_full_name()} → {course.title}"
        )
        return redirect('admin_dashboard')


@method_decorator(staff_member_required, name='dispatch')
class RejectPreferenceView(View):
    """
    Admin rejects a specific pending preference.
    POST /dashboard/preference/<pref_id>/reject/
    """

    def post(self, request, pref_id):
        pref = get_object_or_404(Preference, id=pref_id, status='pending')
        pref.status = 'rejected'
        pref.save()
        messages.success(
            request,
            f"❌ Rejected preference of {pref.student.user.get_full_name()} for {pref.course.title}"
        )
        return redirect('admin_dashboard')
