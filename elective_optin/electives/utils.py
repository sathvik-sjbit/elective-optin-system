"""
Core allocation utilities for the elective opt-in system.

Functions:
- allocate_seats(): Main FCFS allocation engine
- get_waitlist_position(): Calculates waitlist rank
- promote_waitlist(): Promotes next waitlisted student when a seat opens
- export_allocations_csv(): Generates CSV export
"""

import csv
import io
from django.db import transaction
from django.utils import timezone
from .models import Preference, Allocation, Course


def allocate_seats():
    """
    First-Cum-First-Serve (FCFS) seat allocation algorithm.

    Logic:
    1. Get all pending preferences ordered by timestamp (earliest first)
    2. For each preference, check if:
       - Student hasn't already been allocated a course
       - Course has available seats
       - Student's branch quota isn't exceeded
    3. Allocate or waitlist accordingly

    Uses database transaction to prevent race conditions.
    Returns a summary dict with counts.
    """
    summary = {'allocated': 0, 'waitlisted': 0, 'rejected': 0}

    with transaction.atomic():
        # Lock pending preferences and order by timestamp (FCFS)
        pending = (
            Preference.objects
            .select_related('student', 'course')
            .filter(status='pending')
            .order_by('timestamp', 'rank')
            .select_for_update()  # Row-level lock to handle race conditions
        )

        # Track which students have been allocated in this run
        allocated_students = set(
            Allocation.objects.values_list('student_id', flat=True)
        )

        for pref in pending:
            student = pref.student
            course = pref.course

            # Skip if student is already allocated to any course
            if student.id in allocated_students:
                continue

            # Refresh course from DB with lock to get latest seat count
            course = Course.objects.select_for_update().get(id=course.id)

            # Check eligibility: already completed this course?
            already_completed = student.history.filter(course=course).exists()
            if already_completed:
                pref.status = 'rejected'
                pref.save()
                summary['rejected'] += 1
                continue

            # Check branch quota if defined
            if course.branch_quota:
                branch_limit = course.branch_quota.get(student.branch)
                if branch_limit is not None:
                    branch_count = Allocation.objects.filter(
                        course=course, student__branch=student.branch
                    ).count()
                    if branch_count >= branch_limit:
                        # Waitlist this preference
                        pref.status = 'waitlisted'
                        pref.waitlist_position = _get_waitlist_position(course, student.branch)
                        pref.save()
                        summary['waitlisted'] += 1
                        continue

            # Check seat availability
            if course.available_seats > 0:
                # ALLOCATE
                Allocation.objects.create(
                    student=student,
                    course=course,
                    preference=pref,
                )
                course.available_seats -= 1
                course.save()
                pref.status = 'allocated'
                pref.save()
                allocated_students.add(student.id)
                summary['allocated'] += 1
            else:
                # WAITLIST
                pref.status = 'waitlisted'
                pref.waitlist_position = _get_waitlist_position(course)
                pref.save()
                summary['waitlisted'] += 1

    return summary


def _get_waitlist_position(course, branch=None):
    """Calculate the next waitlist position for a course (optionally per branch)"""
    qs = Preference.objects.filter(course=course, status='waitlisted')
    if branch:
        qs = qs.filter(student__branch=branch)
    return qs.count() + 1


def promote_waitlist(course):
    """
    Called via signal when an allocation is cancelled.
    Promotes the next student on the waitlist to allocated status.
    Returns the promoted Preference object or None.
    """
    next_in_line = (
        Preference.objects
        .filter(course=course, status='waitlisted')
        .order_by('waitlist_position', 'timestamp')
        .first()
    )

    if not next_in_line:
        return None

    with transaction.atomic():
        course = Course.objects.select_for_update().get(id=course.id)
        if course.available_seats > 0:
            Allocation.objects.create(
                student=next_in_line.student,
                course=course,
                preference=next_in_line,
                notes="Auto-promoted from waitlist"
            )
            course.available_seats -= 1
            course.save()
            next_in_line.status = 'allocated'
            next_in_line.save()

            # Reorder remaining waitlist
            remaining = (
                Preference.objects
                .filter(course=course, status='waitlisted')
                .order_by('waitlist_position')
            )
            for i, p in enumerate(remaining, start=1):
                p.waitlist_position = i
                p.save()

            return next_in_line
    return None


def export_allocations_csv(department=None, category=None):
    """
    Generate a CSV file of all allocations with optional filtering.

    Returns:
        StringIO object containing the CSV content.
    """
    output = io.StringIO()
    writer = csv.writer(output)

    # Header row
    writer.writerow([
        'Student Name', 'Roll Number', 'Branch', 'CGPA',
        'Course Code', 'Course Title', 'Category', 'Department',
        'Allocation Status', 'Preference Rank', 'Timestamp'
    ])

    # Build queryset with optional filters
    qs = Preference.objects.select_related(
        'student__user', 'course__department'
    ).order_by('course__department__name', 'student__roll_number')

    if department:
        qs = qs.filter(course__department__code=department)
    if category:
        qs = qs.filter(course__category=category)

    for pref in qs:
        writer.writerow([
            pref.student.user.get_full_name(),
            pref.student.roll_number,
            pref.student.get_branch_display(),
            pref.student.cgpa,
            pref.course.code,
            pref.course.title,
            pref.course.get_category_display(),
            pref.course.department.name,
            pref.get_status_display(),
            pref.rank,
            pref.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        ])

    output.seek(0)
    return output


def get_course_preference_stats():
    """
    Returns course preference counts for Chart.js visualization.
    Returns list of dicts: [{title, total, allocated, waitlisted}]
    """
    from .models import Course
    stats = []
    for course in Course.objects.filter(is_active=True).prefetch_related('preferences'):
        prefs = course.preferences.all()
        stats.append({
            'title': f"{course.code}: {course.title[:25]}",
            'total': prefs.count(),
            'allocated': prefs.filter(status='allocated').count(),
            'waitlisted': prefs.filter(status='waitlisted').count(),
        })
    return stats
