# 🎓 Priority-Based Elective Opt-In System

A full-stack Django web application for fair, transparent elective course allocation using First-Cum-First-Serve (FCFS) with constraint-based eligibility.

---

## 🚀 Quick Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
source venv/bin/activate       # Linux/Mac
venv\Scripts\activate          # Windows

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run migrations
python manage.py makemigrations
python manage.py migrate

# 4. Load sample data
python seed_data.py

# 5. Start the server
python manage.py runserver
```

Open http://127.0.0.1:8000 in your browser.

**Demo credentials:**
| Role    | Username   | Password  |
|---------|-----------|-----------|
| Admin   | admin     | admin123  |
| Student | student1  | pass1234  |
| Student | student2  | pass1234  |

---

## 📦 Project Structure

```
elective_optin/
├── elective_optin/
│   ├── settings.py         # Django settings
│   ├── urls.py             # Root URL conf
│   └── wsgi.py
├── electives/
│   ├── models.py           # All data models
│   ├── forms.py            # Forms with validation
│   ├── views.py            # CBVs for all pages
│   ├── urls.py             # App URL patterns
│   ├── utils.py            # allocate_seats(), CSV export
│   ├── signals.py          # Waitlist auto-promotion
│   ├── serializers.py      # DRF serializers for API
│   ├── admin.py            # Django admin config
│   └── apps.py             # Signal registration
├── templates/
│   ├── base.html           # Layout with navbar/toasts
│   ├── registration/       # Login & register pages
│   └── electives/          # Catalog, submit, results, dashboard
├── static/
│   └── js/ajax_seats.js    # Real-time seat polling
├── seed_data.py            # Sample data script
├── requirements.txt
└── README.md
```

---

## ✨ Features

### Core Features
| Feature | Description |
|---------|-------------|
| **Course Catalog** | Browse all electives with category/dept filters, search, pagination |
| **Preference Submission** | Students rank up to 3 choices; duplicate/completed course check |
| **FCFS Allocation** | `allocate_seats()` runs timestamp-ordered allocation with row-level DB lock |
| **Constraint Checks** | Rejects already-completed courses; enforces branch quota (JSONField) |
| **Waitlist** | Auto-promotion via Django signal when allocation is cancelled |
| **Admin Dashboard** | Run allocation, cancel seats, override, view Chart.js stats |
| **CSV Export** | Download allocations filtered by dept/category |
| **Real-time Seats** | AJAX polling every 15s via DRF API endpoint |
| **Auth** | Login/logout, student registration, role-based views |

### Bonus Features
- ✅ Waitlist auto-promotion (Django `post_delete` signal)
- ✅ Branch quota enforcement (JSONField per course)
- ✅ Visual preference tracking (Chart.js bar chart)
- ✅ Admin override allocation
- ✅ Pagination + search in catalog
- ✅ Toast notifications (Bootstrap 5)
- ✅ Basic authentication (login/logout)
- ✅ Role-based access (staff vs student)
- ✅ REST API (DRF) for seat availability

---

## 📡 API Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/seats/` | All courses seat availability |
| GET | `/api/seats/<id>/` | Single course seat info |

**Example response:**
```json
{
  "id": 1,
  "code": "CS501",
  "title": "Machine Learning",
  "available_seats": 12,
  "total_seats": 30,
  "is_full": false,
  "waitlist_count": 3
}
```

---

## 📊 CO Mapping with SDG Goals

### CO1: MVT Architecture
**Mapped SDG: Goal 4 – Quality Education**
- Implements Django's Model-View-Template pattern throughout
- `models.py` defines data layer; `views.py` handles logic; templates render UI
- Demonstrates clean separation of concerns for maintainable educational software

### CO2: Models & Forms
**Mapped SDG: Goal 10 – Reduced Inequalities**
- `Course`, `Student`, `Preference`, `Allocation` models capture fair allocation data
- Branch quota via `JSONField` prevents any single branch from monopolizing seats
- Form validation prevents duplicate preferences and ineligible submissions
- FCFS ensures equal opportunity based on time, not favoritism

### CO3: Templates
**Mapped SDG: Goal 9 – Industry, Innovation & Infrastructure**
- Bootstrap 5 responsive templates work on mobile and desktop
- `catalog.html`, `submit.html`, `results.html`, `admin_dashboard.html`
- Reusable `base.html` with template inheritance
- Toast notifications for real-time user feedback

### CO4: CSV Export
**Mapped SDG: Goal 16 – Peace, Justice & Strong Institutions**
- Transparent data export for institutional auditing and accountability
- Filterable by department and category
- Includes all allocation statuses, CGPA, timestamps
- Supports accreditation and administrative review processes

### CO5: AJAX Integration
**Mapped SDG: Goal 17 – Partnerships for the Goals**
- Real-time seat availability via Django REST Framework API
- `ajax_seats.js` polls every 15 seconds without page reload
- DRF endpoints enable third-party integrations and mobile app support
- Demonstrates modern web API design for collaborative systems

---

## 🔧 Tech Stack

- **Backend:** Django 4.2, Django REST Framework 3.14
- **Database:** SQLite (dev), PostgreSQL-ready
- **Frontend:** Bootstrap 5, Bootstrap Icons, Chart.js
- **Auth:** Django built-in auth + role-based decorators
- **API:** Django REST Framework
- **Concurrency:** `select_for_update()` prevents race conditions

---

## 🧪 Running Tests

```bash
python manage.py test electives
```

---

## 📝 License

MIT License – For academic use.
