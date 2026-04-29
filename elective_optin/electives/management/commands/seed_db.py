"""
Management command to seed the database with departments, courses, and sample students.

Usage:
    python manage.py seed_db
    python manage.py seed_db --clear   (wipes existing data first)
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from electives.models import Department, Course, Student


DEPARTMENTS = [
    ('CSE',   'Computer Science & Engineering'),
    ('ECE',   'Electronics & Communication Engineering'),
    ('MECH',  'Mechanical Engineering'),
    ('CIVIL', 'Civil Engineering'),
    ('EEE',   'Electrical Engineering'),
    ('IT',    'Information Technology'),
    ('CHEM',  'Chemical Engineering'),
    ('BIO',   'Biotechnology'),
]

COURSES = [
    # ── CSE ────────────────────────────────────────────────────────────────
    {
        'code': 'CS501', 'title': 'Machine Learning',
        'category': 'professional', 'department': 'CSE',
        'total_seats': 60, 'semester_offered': 5,
        'salient_features': (
            'Supervised & unsupervised learning, regression, classification, clustering, '
            'neural networks, model evaluation, scikit-learn and TensorFlow basics.'
        ),
        'job_perspective': (
            'Data Scientist, ML Engineer, AI Researcher at top product companies '
            'and startups. High demand across every industry.'
        ),
        'prerequisites': 'Linear Algebra, Python Programming, Statistics',
        'branch_quota': {'CSE': 30, 'IT': 15, 'ECE': 10, 'EEE': 5},
    },
    {
        'code': 'CS502', 'title': 'Cloud Computing',
        'category': 'open', 'department': 'CSE',
        'total_seats': 60, 'semester_offered': 5,
        'salient_features': (
            'AWS, Azure and GCP fundamentals. Containerisation with Docker & Kubernetes, '
            'serverless computing, IaC with Terraform, cost optimisation.'
        ),
        'job_perspective': (
            'Cloud Architect, DevOps / SRE, Platform Engineer. '
            'AWS/Azure certifications significantly boost hiring chances.'
        ),
        'prerequisites': 'Basic Linux, Networking Fundamentals',
        'branch_quota': {},
    },
    {
        'code': 'CS503', 'title': 'Cybersecurity Fundamentals',
        'category': 'open', 'department': 'CSE',
        'total_seats': 50, 'semester_offered': 5,
        'salient_features': (
            'Network security, cryptography, ethical hacking, OWASP Top 10, '
            'SOC operations, incident response, penetration testing basics.'
        ),
        'job_perspective': (
            'Security Analyst, Penetration Tester, CISO-track roles. '
            'Cybersecurity is among the fastest-growing career fields globally.'
        ),
        'prerequisites': 'Computer Networks, Operating Systems',
        'branch_quota': {},
    },
    {
        'code': 'CS504', 'title': 'Blockchain Technology',
        'category': 'ability', 'department': 'CSE',
        'total_seats': 40, 'semester_offered': 7,
        'salient_features': (
            'Distributed ledger fundamentals, consensus algorithms, '
            'smart contracts with Solidity, Ethereum, DeFi, NFTs and Web3 concepts.'
        ),
        'job_perspective': (
            'Blockchain Developer, DeFi Analyst, Smart Contract Auditor, '
            'FinTech and crypto-exchange roles.'
        ),
        'prerequisites': 'Data Structures, Cryptography Basics',
        'branch_quota': {},
    },
    {
        'code': 'CS505', 'title': 'Full-Stack Web Development',
        'category': 'open', 'department': 'CSE',
        'total_seats': 60, 'semester_offered': 5,
        'salient_features': (
            'HTML/CSS/JS, React front-end, Node.js + Django back-end, REST APIs, '
            'PostgreSQL/MongoDB, deployment on cloud, CI/CD pipelines.'
        ),
        'job_perspective': (
            'Full-Stack Developer, Front-End Engineer, Back-End Engineer. '
            'Extremely high demand; freelance opportunities available immediately.'
        ),
        'prerequisites': 'Python / JavaScript Basics, DBMS',
        'branch_quota': {},
    },
    {
        'code': 'CS506', 'title': 'Artificial Intelligence',
        'category': 'professional', 'department': 'CSE',
        'total_seats': 50, 'semester_offered': 7,
        'salient_features': (
            'Search algorithms, knowledge representation, planning, natural language processing, '
            'computer vision, reinforcement learning, ethical AI.'
        ),
        'job_perspective': (
            'AI Engineer, NLP Researcher, Computer Vision Specialist. '
            'Core role at AI-first product companies and research labs.'
        ),
        'prerequisites': 'Machine Learning, Mathematics for CS',
        'branch_quota': {'CSE': 35, 'IT': 15},
    },
    {
        'code': 'CS507', 'title': 'Data Science & Analytics',
        'category': 'open', 'department': 'CSE',
        'total_seats': 60, 'semester_offered': 5,
        'salient_features': (
            'Exploratory data analysis, pandas, NumPy, data visualisation with Matplotlib/Seaborn/Tableau, '
            'SQL, A/B testing, business intelligence dashboards.'
        ),
        'job_perspective': (
            'Data Analyst, Business Analyst, BI Developer. '
            'Entry point into data careers with immediate industry applicability.'
        ),
        'prerequisites': 'Statistics, Python or R',
        'branch_quota': {},
    },

    # ── ECE ────────────────────────────────────────────────────────────────
    {
        'code': 'EC501', 'title': 'IoT and Embedded Systems',
        'category': 'professional', 'department': 'ECE',
        'total_seats': 50, 'semester_offered': 5,
        'salient_features': (
            'Arduino, Raspberry Pi, MQTT protocol, BLE/Zigbee, '
            'sensor integration, edge computing, real-time OS concepts.'
        ),
        'job_perspective': (
            'IoT Engineer, Embedded Systems Developer, Smart City Specialist. '
            'Strong demand in automotive, healthcare and industrial automation.'
        ),
        'prerequisites': 'Microprocessors, C Programming',
        'branch_quota': {'ECE': 30, 'CSE': 10, 'EEE': 10},
    },
    {
        'code': 'EC502', 'title': '5G and Wireless Communications',
        'category': 'professional', 'department': 'ECE',
        'total_seats': 40, 'semester_offered': 7,
        'salient_features': (
            'NR (New Radio), beamforming, massive MIMO, network slicing, '
            '5G RAN/Core architecture, O-RAN, spectrum management.'
        ),
        'job_perspective': (
            'Telecom / RF Engineer, Network Architect at Nokia, Ericsson, Qualcomm. '
            '5G rollout globally drives strong hiring through 2030.'
        ),
        'prerequisites': 'Digital Communications, Signal Processing',
        'branch_quota': {},
    },
    {
        'code': 'EC503', 'title': 'VLSI Design',
        'category': 'professional', 'department': 'ECE',
        'total_seats': 40, 'semester_offered': 7,
        'salient_features': (
            'CMOS circuit design, HDL (Verilog/VHDL), RTL design, synthesis, '
            'place & route, DFT, timing analysis, FPGA prototyping.'
        ),
        'job_perspective': (
            'VLSI Design Engineer, ASIC/FPGA Engineer at Intel, AMD, Qualcomm, Samsung. '
            'Semiconductor shortage has made this a hot career.'
        ),
        'prerequisites': 'Digital Electronics, Electronic Circuits',
        'branch_quota': {'ECE': 30, 'EEE': 10},
    },
    {
        'code': 'EC504', 'title': 'Signal Processing & DSP',
        'category': 'ability', 'department': 'ECE',
        'total_seats': 35, 'semester_offered': 5,
        'salient_features': (
            'Discrete-time systems, FFT, FIR/IIR filter design, spectral analysis, '
            'MATLAB/Python DSP libraries, audio/image processing applications.'
        ),
        'job_perspective': (
            'DSP Engineer, Audio/Video Algorithm Developer, Radar & Sonar systems.'
        ),
        'prerequisites': 'Signals and Systems, Mathematics',
        'branch_quota': {},
    },

    # ── MECH ───────────────────────────────────────────────────────────────
    {
        'code': 'ME501', 'title': 'Robotics and Automation',
        'category': 'open', 'department': 'MECH',
        'total_seats': 50, 'semester_offered': 5,
        'salient_features': (
            'Robot kinematics & dynamics, ROS 2 framework, PLC programming, '
            'industrial automation, collaborative robots (cobots).'
        ),
        'job_perspective': (
            'Robotics Engineer, Automation Specialist, Manufacturing Tech Lead. '
            'Industry 4.0 drives massive demand across automotive and electronics manufacturing.'
        ),
        'prerequisites': 'Engineering Mechanics, Control Systems',
        'branch_quota': {},
    },
    {
        'code': 'ME502', 'title': 'Additive Manufacturing (3D Printing)',
        'category': 'ability', 'department': 'MECH',
        'total_seats': 30, 'semester_offered': 5,
        'salient_features': (
            'FDM, SLA, SLS processes, design for AM, materials science, '
            'slicing software, topology optimisation, bioprinting introduction.'
        ),
        'job_perspective': (
            'Prototyping / Product Engineer, Aerospace & Medical device manufacturing roles.'
        ),
        'prerequisites': 'Engineering Drawing, Manufacturing Processes',
        'branch_quota': {},
    },
    {
        'code': 'ME503', 'title': 'CAD/CAM and Product Design',
        'category': 'professional', 'department': 'MECH',
        'total_seats': 40, 'semester_offered': 5,
        'salient_features': (
            'SolidWorks, CATIA, AutoCAD, GD&T, CNC machining, '
            'CAM toolpath generation, product lifecycle management.'
        ),
        'job_perspective': (
            'Product Design Engineer, CAD Designer, R&D Engineer at OEMs and Tier-1 suppliers.'
        ),
        'prerequisites': 'Engineering Drawing, Manufacturing Technology',
        'branch_quota': {},
    },

    # ── CIVIL ──────────────────────────────────────────────────────────────
    {
        'code': 'CV501', 'title': 'GIS and Remote Sensing',
        'category': 'open', 'department': 'CIVIL',
        'total_seats': 40, 'semester_offered': 5,
        'salient_features': (
            'QGIS, ArcGIS, satellite imagery analysis, LiDAR, '
            'urban planning applications, drone surveys, spatial data analysis.'
        ),
        'job_perspective': (
            'GIS Analyst, Urban Planner, Environmental Consultant, '
            'government and smart-city roles.'
        ),
        'prerequisites': 'Surveying, Engineering Mathematics',
        'branch_quota': {},
    },
    {
        'code': 'CV502', 'title': 'Sustainable & Green Building Design',
        'category': 'ability', 'department': 'CIVIL',
        'total_seats': 35, 'semester_offered': 7,
        'salient_features': (
            'LEED/GRIHA rating systems, passive design strategies, '
            'solar passive architecture, rainwater harvesting, net-zero building concepts.'
        ),
        'job_perspective': (
            'Green Building Consultant, Sustainability Analyst, '
            'LEED-certified project roles in real estate and infrastructure.'
        ),
        'prerequisites': 'Building Materials, Environmental Engineering',
        'branch_quota': {},
    },

    # ── EEE ────────────────────────────────────────────────────────────────
    {
        'code': 'EE501', 'title': 'Electric Vehicles & Power Electronics',
        'category': 'professional', 'department': 'EEE',
        'total_seats': 50, 'semester_offered': 7,
        'salient_features': (
            'Battery management systems, motor drives, charging infrastructure, '
            'grid integration, regenerative braking, EV ecosystem overview.'
        ),
        'job_perspective': (
            'EV Design Engineer, Power Electronics R&D, OEM roles at Tata, Mahindra, Tesla, Ola Electric.'
        ),
        'prerequisites': 'Power Systems, Electrical Machines',
        'branch_quota': {'EEE': 30, 'MECH': 15, 'ECE': 5},
    },
    {
        'code': 'EE502', 'title': 'Renewable Energy Systems',
        'category': 'open', 'department': 'EEE',
        'total_seats': 45, 'semester_offered': 5,
        'salient_features': (
            'Solar PV systems, wind energy, grid-scale storage, '
            'energy auditing, power system simulation (MATLAB/PSCAD).'
        ),
        'job_perspective': (
            'Energy Consultant, Solar Project Engineer, Grid Integration Specialist. '
            'Booming sector with government incentives and green mandates.'
        ),
        'prerequisites': 'Power Systems, Electrical Machines',
        'branch_quota': {},
    },

    # ── IT ─────────────────────────────────────────────────────────────────
    {
        'code': 'IT501', 'title': 'Mobile Application Development',
        'category': 'open', 'department': 'IT',
        'total_seats': 50, 'semester_offered': 5,
        'salient_features': (
            'Android (Kotlin/Java) and iOS (Swift) development, '
            'Flutter cross-platform, REST API integration, app store deployment, UX principles.'
        ),
        'job_perspective': (
            'Mobile Developer, App Entrepreneur. '
            'India has 750M+ smartphone users — mobile skills are perpetually in demand.'
        ),
        'prerequisites': 'OOP Concepts, Java or Python',
        'branch_quota': {},
    },
    {
        'code': 'IT502', 'title': 'Database Management & SQL',
        'category': 'ability', 'department': 'IT',
        'total_seats': 55, 'semester_offered': 5,
        'salient_features': (
            'Advanced SQL, query optimisation, indexing, stored procedures, '
            'NoSQL (MongoDB, Redis), database design, ER modelling, ACID properties.'
        ),
        'job_perspective': (
            'Database Administrator, Data Engineer, Backend Developer. '
            'Core skill required for almost every software role.'
        ),
        'prerequisites': 'Basic DBMS',
        'branch_quota': {},
    },
]

STUDENTS = [
    ('student1', 'Arjun',   'Sharma', 'arjun@college.edu',  '21CS001', 'CSE',   5, 8.5),
    ('student2', 'Priya',   'Patel',  'priya@college.edu',  '21CS002', 'CSE',   5, 7.9),
    ('student3', 'Ravi',    'Kumar',  'ravi@college.edu',   '21EC001', 'ECE',   5, 8.1),
    ('student4', 'Sneha',   'Nair',   'sneha@college.edu',  '21ME001', 'MECH',  5, 7.5),
    ('student5', 'Amit',    'Singh',  'amit@college.edu',   '21EE001', 'EEE',   7, 8.8),
    ('student6', 'Deepa',   'Reddy',  'deepa@college.edu',  '21CV001', 'CIVIL', 5, 7.2),
    ('student7', 'Karthik', 'Raj',    'karthik@college.edu','21IT001', 'IT',    5, 8.3),
    ('student8', 'Nisha',   'Menon',  'nisha@college.edu',  '21CS003', 'CSE',   7, 9.1),
]


class Command(BaseCommand):
    help = 'Seed the database with departments, courses, and sample students'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear', action='store_true',
            help='Delete all existing courses, departments and students before seeding'
        )

    def handle(self, *args, **options):
        if options['clear']:
            Course.objects.all().delete()
            Department.objects.all().delete()
            Student.objects.all().delete()
            self.stdout.write(self.style.WARNING('Cleared existing data.'))

        # ── Departments ───────────────────────────────────────────────────
        dept_objs = {}
        for code, name in DEPARTMENTS:
            obj, created = Department.objects.get_or_create(
                code=code, defaults={'name': name}
            )
            dept_objs[code] = obj
            if created:
                self.stdout.write(f'  ✚ Dept: {code} – {name}')

        self.stdout.write(self.style.SUCCESS(f'Departments ready: {len(dept_objs)}'))

        # ── Courses ───────────────────────────────────────────────────────
        created_courses = 0
        for cd in COURSES:
            dept_code = cd.pop('department')
            dept = dept_objs[dept_code]
            seats = cd['total_seats']
            obj, created = Course.objects.get_or_create(
                code=cd['code'],
                defaults={**cd, 'department': dept, 'available_seats': seats}
            )
            cd['department'] = dept_code          # restore for next runs
            if created:
                created_courses += 1
                self.stdout.write(f'  ✚ Course: {obj.code} – {obj.title}')

        self.stdout.write(self.style.SUCCESS(
            f'Courses ready: {Course.objects.count()} total ({created_courses} new)'
        ))

        # ── Admin superuser ───────────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@college.edu', 'admin123')
            self.stdout.write(self.style.SUCCESS('Admin created  →  admin / admin123'))
        else:
            self.stdout.write('Admin already exists, skipped.')

        # ── Sample students ───────────────────────────────────────────────
        created_students = 0
        for uname, first, last, email, roll, branch, sem, cgpa in STUDENTS:
            if not User.objects.filter(username=uname).exists():
                u = User.objects.create_user(
                    uname, email, 'pass1234',
                    first_name=first, last_name=last
                )
                Student.objects.create(
                    user=u, roll_number=roll, branch=branch,
                    current_semester=sem, cgpa=cgpa
                )
                created_students += 1
                self.stdout.write(f'  ✚ Student: {uname} ({branch})')

        self.stdout.write(self.style.SUCCESS(
            f'Students ready: {Student.objects.count()} total ({created_students} new)'
        ))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✅  Seed complete!'))
        self.stdout.write('─' * 40)
        self.stdout.write('Login credentials:')
        self.stdout.write('  Admin    →  admin / admin123')
        self.stdout.write('  Students →  student1 … student8 / pass1234')
        self.stdout.write('─' * 40)
