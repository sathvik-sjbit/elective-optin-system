"""
Models for Priority-Based Elective Opt-In System

Covers:
- Department
- Course (with category, seats, branch quota)
- Student (linked to auth.User)
- StudentCourseHistory (completed courses)
- Preference (student's ranked choices)
- Allocation (final seat assignments)
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Department(models.Model):
    """Academic department offering courses"""
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


class Course(models.Model):
    """
    Elective course with category, seats, prerequisites.
    branch_quota: JSONField mapping branch code → max seats for that branch.
    Example: {"CSE": 10, "ECE": 5, "MECH": 3}
    """
    CATEGORY_CHOICES = [
        ('professional', 'Professional Elective'),
        ('open', 'Open Elective'),
        ('ability', 'Ability Enhancement'),
    ]

    title = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='open')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    salient_features = models.TextField(help_text="Key highlights and topics covered")
    job_perspective = models.TextField(help_text="Career opportunities this course opens")
    prerequisites = models.TextField(blank=True, help_text="Required prior knowledge/courses")
    total_seats = models.PositiveIntegerField(default=30)
    available_seats = models.PositiveIntegerField(default=30)
    semester_offered = models.PositiveIntegerField(default=5, help_text="Which semester this is offered")
    branch_quota = models.JSONField(
        default=dict,
        blank=True,
        help_text='Branch-wise seat limits. E.g. {"CSE": 10, "ECE": 5}'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return f"{self.code} - {self.title}"

    @property
    def is_full(self):
        return self.available_seats <= 0

    def seats_taken(self):
        return self.total_seats - self.available_seats


class Student(models.Model):
    """
    Student profile linked to auth.User.
    Stores academic info needed for eligibility checks.
    """
    BRANCH_CHOICES = [
        ('CSE', 'Computer Science'),
        ('ECE', 'Electronics & Communication'),
        ('MECH', 'Mechanical Engineering'),
        ('CIVIL', 'Civil Engineering'),
        ('EEE', 'Electrical Engineering'),
        ('IT', 'Information Technology'),
        ('CHEM', 'Chemical Engineering'),
        ('BIO', 'Biotechnology'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student')
    roll_number = models.CharField(max_length=20, unique=True)
    branch = models.CharField(max_length=10, choices=BRANCH_CHOICES)
    current_semester = models.PositiveIntegerField(default=1)
    cgpa = models.DecimalField(max_digits=4, decimal_places=2, default=0.00)
    phone = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return f"{self.roll_number} - {self.user.get_full_name()}"


class StudentCourseHistory(models.Model):
    """Tracks courses a student has already completed (used for eligibility checks)"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='history')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester_completed = models.PositiveIntegerField()
    grade = models.CharField(max_length=5, blank=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.roll_number} completed {self.course.code}"


class Preference(models.Model):
    """
    Student's ranked course preferences.
    rank: 1 = most preferred, 2 = second choice, etc.
    Timestamp determines first-cum-first-serve priority.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('allocated', 'Allocated'),
        ('waitlisted', 'Waitlisted'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='preferences')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='preferences')
    rank = models.PositiveIntegerField(help_text="1 = top choice")
    timestamp = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    waitlist_position = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['timestamp', 'rank']

    def __str__(self):
        return f"{self.student.roll_number} -> {self.course.code} (Rank {self.rank})"


class Allocation(models.Model):
    """
    Final allocation record created by the allocate_seats() function.
    Supports admin override.
    """
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='allocations')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='allocations')
    preference = models.OneToOneField(
        Preference, on_delete=models.CASCADE, related_name='allocation', null=True, blank=True
    )
    allocated_at = models.DateTimeField(auto_now_add=True)
    is_admin_override = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('student', 'course')

    def __str__(self):
        return f"{self.student.roll_number} allocated to {self.course.code}"
