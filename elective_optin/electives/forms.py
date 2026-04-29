"""
Forms for elective opt-in system.
Includes validation for eligibility, duplicate prevention, and branch quota.
"""

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Student, Preference, Course, Allocation


class StudentRegistrationForm(UserCreationForm):
    """Combined user + student registration form"""
    first_name = forms.CharField(max_length=50, required=True)
    last_name = forms.CharField(max_length=50, required=True)
    email = forms.EmailField(required=True)
    roll_number = forms.CharField(max_length=20)
    branch = forms.ChoiceField(choices=Student.BRANCH_CHOICES)
    current_semester = forms.IntegerField(min_value=1, max_value=8)
    cgpa = forms.DecimalField(max_digits=4, decimal_places=2, min_value=0, max_value=10)
    phone = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Student.objects.create(
                user=user,
                roll_number=self.cleaned_data['roll_number'],
                branch=self.cleaned_data['branch'],
                current_semester=self.cleaned_data['current_semester'],
                cgpa=self.cleaned_data['cgpa'],
                phone=self.cleaned_data.get('phone', ''),
            )
        return user


class PreferenceForm(forms.Form):
    """
    Dynamic form to submit ranked preferences.
    Students select up to 3 courses with a priority rank.
    """
    choice1 = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True).select_related('department'),
        label="1st Choice (Highest Priority)",
        empty_label="-- Select Course --"
    )
    choice2 = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True).select_related('department'),
        label="2nd Choice",
        required=False,
        empty_label="-- Select Course (optional) --"
    )
    choice3 = forms.ModelChoiceField(
        queryset=Course.objects.filter(is_active=True).select_related('department'),
        label="3rd Choice",
        required=False,
        empty_label="-- Select Course (optional) --"
    )

    def __init__(self, student, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.student = student
        # Exclude already-allocated or already-submitted courses
        existing_course_ids = student.preferences.values_list('course_id', flat=True)
        completed_course_ids = student.history.values_list('course_id', flat=True)
        excluded = list(existing_course_ids) + list(completed_course_ids)
        available = Course.objects.filter(is_active=True).exclude(id__in=excluded).select_related('department')
        for field in ['choice1', 'choice2', 'choice3']:
            self.fields[field].queryset = available

    def clean(self):
        cleaned = super().clean()
        choices = [
            cleaned.get('choice1'),
            cleaned.get('choice2'),
            cleaned.get('choice3'),
        ]
        # Filter None values
        selected = [c for c in choices if c]
        # Check for duplicates among selections
        ids = [c.id for c in selected]
        if len(ids) != len(set(ids)):
            raise forms.ValidationError("You cannot select the same course more than once.")
        # Validate branch quota
        for course in selected:
            if course.branch_quota:
                branch_limit = course.branch_quota.get(self.student.branch)
                if branch_limit is not None:
                    branch_allocated = course.allocations.filter(
                        student__branch=self.student.branch
                    ).count()
                    branch_waitlisted = course.preferences.filter(
                        student__branch=self.student.branch,
                        status='waitlisted'
                    ).count()
                    if branch_allocated + branch_waitlisted >= branch_limit:
                        raise forms.ValidationError(
                            f"Branch quota for {self.student.branch} in {course.title} is full."
                        )
        return cleaned


class AdminAllocationOverrideForm(forms.ModelForm):
    """Admin form to manually allocate/override a student's course"""
    class Meta:
        model = Allocation
        fields = ['student', 'course', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class CourseFilterForm(forms.Form):
    """Filter form for course catalog"""
    CATEGORY_CHOICES = [('', 'All Categories')] + Course.CATEGORY_CHOICES
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, required=False, label="Category")
    department = forms.CharField(required=False, label="Department")
    search = forms.CharField(required=False, label="Search", widget=forms.TextInput(
        attrs={'placeholder': 'Search courses...'}
    ))


class AdminAddCourseForm(forms.ModelForm):
    """Admin form to add a new course directly from the dashboard"""

    branch_quota_text = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'placeholder': '{"CSE": 10, "ECE": 5}'}),
        label="Branch Quota (JSON)"
    )

    class Meta:
        model = Course
        fields = [
            'title', 'code', 'category', 'department',
            'salient_features', 'job_perspective', 'prerequisites',
            'total_seats', 'available_seats', 'semester_offered',
            'is_active',
        ]
        widgets = {
            'salient_features': forms.Textarea(attrs={'rows': 3}),
            'job_perspective': forms.Textarea(attrs={'rows': 3}),
            'prerequisites': forms.Textarea(attrs={'rows': 2}),
        }

    def clean(self):
        import json as _json
        cleaned = super().clean()
        raw = self.data.get('branch_quota', '').strip()
        if raw:
            try:
                cleaned['branch_quota'] = _json.loads(raw)
            except ValueError:
                self.add_error(None, "Branch quota must be valid JSON, e.g. {\"CSE\": 10}")
        else:
            cleaned['branch_quota'] = {}
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.branch_quota = self.cleaned_data.get('branch_quota', {})
        if commit:
            instance.save()
        return instance
