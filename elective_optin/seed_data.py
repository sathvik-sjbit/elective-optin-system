"""
seed_data.py – Populate the database with sample departments, courses, and students.
Run with: python manage.py shell < seed_data.py
  OR add to a management command.
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'elective_optin.settings')
django.setup()

from django.contrib.auth.models import User
from electives.models import Department, Course, Student, StudentCourseHistory

# --------------------
# Departments
# --------------------
depts = [
    ('CSE', 'Computer Science & Engineering'),
    ('ECE', 'Electronics & Communication Engineering'),
    ('MECH', 'Mechanical Engineering'),
    ('CIVIL', 'Civil Engineering'),
    ('EEE', 'Electrical Engineering'),
]
dept_objs = {}
for code, name in depts:
    d, _ = Department.objects.get_or_create(code=code, defaults={'name': name})
    dept_objs[code] = d
print(f"Created {len(dept_objs)} departments")

# --------------------
# Courses
# --------------------
courses_data = [
    {
        'code': 'CS501', 'title': 'Machine Learning', 'category': 'professional',
        'department': 'CSE', 'total_seats': 30, 'semester_offered': 5,
        'salient_features': 'Supervised and unsupervised learning, neural networks, model evaluation, scikit-learn, TensorFlow basics.',
        'job_perspective': 'Data Scientist, ML Engineer, AI Researcher at top tech companies.',
        'prerequisites': 'Linear Algebra, Python Programming, Statistics',
        'branch_quota': {'CSE': 20, 'ECE': 5, 'IT': 5},
    },
    {
        'code': 'CS502', 'title': 'Cloud Computing', 'category': 'open',
        'department': 'CSE', 'total_seats': 40, 'semester_offered': 5,
        'salient_features': 'AWS, Azure, GCP fundamentals. Containerization with Docker, Kubernetes, serverless computing.',
        'job_perspective': 'Cloud Architect, DevOps Engineer, Site Reliability Engineer.',
        'prerequisites': 'Basic Linux, Networking fundamentals',
        'branch_quota': {},
    },
    {
        'code': 'CS503', 'title': 'Cybersecurity Fundamentals', 'category': 'open',
        'department': 'CSE', 'total_seats': 35, 'semester_offered': 5,
        'salient_features': 'Network security, cryptography, ethical hacking, OWASP top 10, SOC operations.',
        'job_perspective': 'Security Analyst, Penetration Tester, CISO track.',
        'prerequisites': 'Computer Networks, Operating Systems',
        'branch_quota': {},
    },
    {
        'code': 'CS504', 'title': 'Blockchain Technology', 'category': 'ability',
        'department': 'CSE', 'total_seats': 25, 'semester_offered': 7,
        'salient_features': 'Distributed ledger, smart contracts with Solidity, Ethereum, DeFi concepts.',
        'job_perspective': 'Blockchain Developer, DeFi Analyst, FinTech roles.',
        'prerequisites': 'Data Structures, Cryptography basics',
        'branch_quota': {},
    },
    {
        'code': 'EC501', 'title': 'IoT and Embedded Systems', 'category': 'professional',
        'department': 'ECE', 'total_seats': 30, 'semester_offered': 5,
        'salient_features': 'Arduino, Raspberry Pi, MQTT protocol, sensor integration, edge computing.',
        'job_perspective': 'IoT Engineer, Embedded Systems Developer, Smart City Specialist.',
        'prerequisites': 'Microprocessors, C Programming',
        'branch_quota': {'ECE': 20, 'CSE': 5, 'EEE': 5},
    },
    {
        'code': 'EC502', 'title': '5G and Wireless Communications', 'category': 'professional',
        'department': 'ECE', 'total_seats': 25, 'semester_offered': 7,
        'salient_features': 'NR (New Radio), beamforming, network slicing, MIMO systems, 5G architecture.',
        'job_perspective': 'Telecom Engineer, RF Engineer, Network Architect at Nokia/Ericsson.',
        'prerequisites': 'Digital Communications, Signal Processing',
        'branch_quota': {},
    },
    {
        'code': 'ME501', 'title': 'Robotics and Automation', 'category': 'open',
        'department': 'MECH', 'total_seats': 35, 'semester_offered': 5,
        'salient_features': 'Robot kinematics, ROS framework, PLC programming, industrial automation.',
        'job_perspective': 'Robotics Engineer, Automation Specialist, Manufacturing Tech Lead.',
        'prerequisites': 'Engineering Mechanics, Control Systems',
        'branch_quota': {},
    },
    {
        'code': 'ME502', 'title': 'Additive Manufacturing (3D Printing)', 'category': 'ability',
        'department': 'MECH', 'total_seats': 20, 'semester_offered': 5,
        'salient_features': 'FDM, SLA, SLS processes, design for AM, materials, slicing software, bioprinting intro.',
        'job_perspective': 'Prototyping Engineer, Product Designer, Aerospace/Medical manufacturing.',
        'prerequisites': 'Engineering Drawing, Manufacturing Processes',
        'branch_quota': {},
    },
    {
        'code': 'CV501', 'title': 'GIS and Remote Sensing', 'category': 'open',
        'department': 'CIVIL', 'total_seats': 30, 'semester_offered': 5,
        'salient_features': 'QGIS, satellite imagery analysis, urban planning applications, drone surveys.',
        'job_perspective': 'GIS Analyst, Urban Planner, Environmental Consultant.',
        'prerequisites': 'Surveying, Engineering Mathematics',
        'branch_quota': {},
    },
    {
        'code': 'EE501', 'title': 'Electric Vehicles & Power Electronics', 'category': 'professional',
        'department': 'EEE', 'total_seats': 30, 'semester_offered': 7,
        'salient_features': 'BMS, motor drives, charging infrastructure, grid integration, EV ecosystem.',
        'job_perspective': 'EV Design Engineer, Power Electronics R&D, OEM roles at Tata/Mahindra/Tesla.',
        'prerequisites': 'Power Systems, Electrical Machines',
        'branch_quota': {'EEE': 20, 'MECH': 10},
    },
]

for cd in courses_data:
    dept = dept_objs[cd.pop('department')]
    c, created = Course.objects.get_or_create(code=cd['code'], defaults={**cd, 'department': dept, 'available_seats': cd['total_seats']})
    if created:
        c.available_seats = c.total_seats
        c.save()

print(f"Created {Course.objects.count()} courses")

# --------------------
# Admin User
# --------------------
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@college.edu', 'admin123')
    print("Admin created: admin / admin123")

# --------------------
# Sample Students
# --------------------
students_data = [
    ('student1', 'Arjun', 'Sharma', 'arjun@college.edu', '21CS001', 'CSE', 5, 8.5),
    ('student2', 'Priya', 'Patel', 'priya@college.edu', '21CS002', 'CSE', 5, 7.9),
    ('student3', 'Ravi', 'Kumar', 'ravi@college.edu', '21EC001', 'ECE', 5, 8.1),
    ('student4', 'Sneha', 'Nair', 'sneha@college.edu', '21ME001', 'MECH', 5, 7.5),
    ('student5', 'Amit', 'Singh', 'amit@college.edu', '21EE001', 'EEE', 7, 8.8),
    ('student6', 'Deepa', 'Reddy', 'deepa@college.edu', '21CV001', 'CIVIL', 5, 7.2),
]

for uname, first, last, email, roll, branch, sem, cgpa in students_data:
    if not User.objects.filter(username=uname).exists():
        u = User.objects.create_user(uname, email, 'pass1234', first_name=first, last_name=last)
        Student.objects.create(
            user=u, roll_number=roll, branch=branch,
            current_semester=sem, cgpa=cgpa
        )

print(f"Created {Student.objects.count()} students")
print("\n✅ Seed data loaded successfully!")
print("Login credentials:")
print("  Admin  → admin / admin123")
print("  Students → student1...student6 / pass1234")
