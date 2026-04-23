"""Management command to populate the database with realistic demo data."""
import datetime
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from apps.dashboard.models import (
    Activity,
    DashboardMetric,
    Department,
    Employee,
    Notification,
    Project,
    UserProfile,
)

# -- Demo data definitions ---------------------------------------------------

DEPARTMENTS = [
    ("ENG", "Engineering"),
    ("MKT", "Marketing"),
    ("SAL", "Sales"),
    ("FIN", "Finance"),
    ("HR", "Human Resources"),
    ("OPS", "Operations"),
    ("DES", "Design"),
    ("SUP", "Support"),
]

JOB_TITLES = {
    "ENG": ["Software Engineer", "Senior Engineer", "Staff Engineer", "Engineering Manager", "DevOps Engineer"],
    "MKT": ["Marketing Analyst", "Content Strategist", "Growth Manager", "SEO Specialist", "Brand Manager"],
    "SAL": ["Account Executive", "Sales Representative", "Sales Manager", "BDR", "VP of Sales"],
    "FIN": ["Financial Analyst", "Controller", "Accountant", "CFO", "Payroll Specialist"],
    "HR": ["HR Generalist", "Recruiter", "HR Manager", "Talent Partner", "People Operations"],
    "OPS": ["Operations Manager", "Supply Chain Analyst", "Logistics Coordinator", "Process Engineer"],
    "DES": ["Product Designer", "UX Researcher", "UI Designer", "Design Lead", "Graphic Designer"],
    "SUP": ["Support Engineer", "Customer Success Manager", "Technical Writer", "Support Lead"],
}

PROJECTS = [
    ("Platform Redesign", "Complete overhaul of the customer-facing platform with modern UI/UX"),
    ("Q3 Marketing Campaign", "Multi-channel marketing push for the Q3 product launch"),
    ("Data Pipeline v2", "Rebuild ETL pipeline for real-time analytics and reporting"),
    ("Mobile App Launch", "Native iOS and Android companion app for the main platform"),
    ("Security Audit 2024", "Comprehensive security review and penetration testing"),
    ("Customer Portal", "Self-service portal for enterprise customers"),
    ("API Gateway", "Centralised API gateway with rate limiting and analytics"),
    ("Employee Onboarding System", "Automated onboarding workflow with document management"),
]

FIRST_NAMES = [
    "Alice", "Bob", "Carol", "David", "Emma", "Frank", "Grace", "Henry",
    "Isla", "Jack", "Kate", "Liam", "Maya", "Noah", "Olivia", "Peter",
    "Quinn", "Rachel", "Sam", "Tara", "Uma", "Victor", "Wendy", "Xavier",
]

LAST_NAMES = [
    "Anderson", "Brown", "Chen", "Davis", "Evans", "Foster", "Garcia",
    "Harris", "Ibrahim", "Johnson", "Kumar", "Lee", "Martinez", "Nguyen",
    "O'Brien", "Patel", "Quinn", "Roberts", "Singh", "Thompson",
]

METRICS = [
    ("Total Revenue", 284500.00, 12.5, "monthly"),
    ("Active Users", 14832.00, 8.3, "monthly"),
    ("New Signups", 1247.00, -3.2, "weekly"),
    ("Support Tickets", 89.00, -15.4, "weekly"),
    ("Employee Count", 156.00, 4.1, "quarterly"),
    ("Customer Satisfaction", 94.20, 2.1, "monthly"),
    ("Server Uptime", 99.97, 0.02, "daily"),
    ("Deployment Frequency", 23.00, 18.0, "weekly"),
]

ACTIVITY_TEMPLATES = [
    ("create", "Created department {dept}"),
    ("update", "Updated project {project} status to active"),
    ("create", "Added new employee {name} to {dept}"),
    ("view", "Viewed financial report for Q3"),
    ("export", "Exported employee directory to CSV"),
    ("update", "Changed {name}'s role to Manager"),
    ("delete", "Removed inactive project from backlog"),
    ("create", "Created new project {project}"),
    ("login", "Logged in from {ip}"),
    ("view", "Reviewed dashboard metrics"),
]

NOTIFICATION_TEMPLATES = [
    ("info", "System Update", "A scheduled maintenance window is planned for this weekend."),
    ("success", "Deployment Complete", "Version 2.4.1 has been deployed to production successfully."),
    ("warning", "Budget Alert", "Q3 marketing budget is at 85% utilization."),
    ("info", "New Team Member", "{name} has joined the {dept} department."),
    ("success", "Project Milestone", "Platform Redesign reached the beta milestone."),
    ("error", "Integration Error", "Salesforce sync failed — retrying in 30 minutes."),
    ("warning", "Security Notice", "3 failed login attempts detected from IP {ip}."),
    ("info", "Report Ready", "Monthly analytics report is ready for download."),
    ("success", "Goal Achieved", "{dept} team exceeded their Q3 OKR targets."),
    ("warning", "License Expiry", "Adobe Creative Suite license expires in 14 days."),
]


class Command(BaseCommand):
    help = "Populate the database with realistic demo data for the admin dashboard."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing data before seeding",
        )
        parser.add_argument(
            "--employees",
            type=int,
            default=24,
            help="Number of employees to create (default: 24)",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            Notification.objects.all().delete()
            Activity.objects.all().delete()
            DashboardMetric.objects.all().delete()
            Project.objects.all().delete()
            Employee.objects.all().delete()
            UserProfile.objects.all().delete()
            Department.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.SUCCESS("Cleared."))

        # -- Ensure an admin superuser exists --
        admin, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@example.com",
                "first_name": "Admin",
                "last_name": "User",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin.set_password("admin")
            admin.save()
            self.stdout.write(self.style.SUCCESS("Created admin user (admin / admin)"))
        else:
            self.stdout.write("Admin user already exists — skipping.")

        # -- Departments --
        departments = {}
        for code, name in DEPARTMENTS:
            dept, _ = Department.objects.get_or_create(code=code, defaults={"name": name})
            departments[code] = dept
        self.stdout.write(self.style.SUCCESS(f"Created {len(departments)} departments"))

        # -- Employees --
        num_employees = min(options["employees"], len(FIRST_NAMES) * len(LAST_NAMES))
        name_pairs = []
        for fn in FIRST_NAMES:
            for ln in LAST_NAMES:
                name_pairs.append((fn, ln))
        random.shuffle(name_pairs)
        name_pairs = name_pairs[:num_employees]

        employees = []
        dept_codes = list(departments.keys())
        for i, (first, last) in enumerate(name_pairs):
            username = f"{first.lower()}.{last.lower()}"
            user, user_created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@example.com",
                    "first_name": first,
                    "last_name": last,
                    "is_staff": True,
                },
            )
            if user_created:
                user.set_password("demo1234")
                user.save()

            dept_code = dept_codes[i % len(dept_codes)]
            dept = departments[dept_code]
            titles = JOB_TITLES.get(dept_code, ["Specialist"])

            emp, _ = Employee.objects.get_or_create(
                user=user,
                defaults={
                    "department": dept,
                    "job_title": titles[i % len(titles)],
                    "salary": random.randint(55000, 180000),
                    "status": random.choices(
                        [Employee.STATUS_ACTIVE, Employee.STATUS_INACTIVE, Employee.STATUS_ON_LEAVE],
                        weights=[80, 10, 10],
                    )[0],
                    "hire_date": datetime.date.today() - datetime.timedelta(days=random.randint(30, 1200)),
                },
            )
            employees.append(emp)

            # User profile
            roles = [UserProfile.ROLE_VIEWER, UserProfile.ROLE_ANALYST, UserProfile.ROLE_MANAGER, UserProfile.ROLE_ADMIN]
            role = random.choices(roles, weights=[40, 30, 20, 10])[0]
            UserProfile.objects.get_or_create(
                user=user,
                defaults={"role": role, "department": dept},
            )

        # Admin profile
        UserProfile.objects.get_or_create(
            user=admin,
            defaults={"role": UserProfile.ROLE_ADMIN},
        )

        self.stdout.write(self.style.SUCCESS(f"Created {len(employees)} employees with profiles"))

        # -- Assign department heads --
        for code, dept in departments.items():
            dept_employees = [e for e in employees if e.department == dept]
            if dept_employees and not dept.head:
                dept.head = random.choice(dept_employees).user
                dept.save()
        self.stdout.write(self.style.SUCCESS("Assigned department heads"))

        # -- Projects --
        projects = []
        for name, desc in PROJECTS:
            dept = random.choice(list(departments.values()))
            status = random.choice([
                Project.STATUS_PLANNING,
                Project.STATUS_ACTIVE,
                Project.STATUS_ACTIVE,
                Project.STATUS_COMPLETED,
            ])
            start = datetime.date.today() - datetime.timedelta(days=random.randint(10, 300))
            end = start + datetime.timedelta(days=random.randint(60, 365)) if status != Project.STATUS_PLANNING else None
            project, _ = Project.objects.get_or_create(
                name=name,
                defaults={
                    "description": desc,
                    "department": dept,
                    "status": status,
                    "budget": random.randint(10000, 500000),
                    "start_date": start,
                    "end_date": end,
                },
            )
            # Assign random team members
            team_size = random.randint(2, 6)
            team = random.sample(employees, min(team_size, len(employees)))
            project.members.set(team)
            projects.append(project)

        self.stdout.write(self.style.SUCCESS(f"Created {len(projects)} projects"))

        # -- Dashboard Metrics --
        for name, value, change, period in METRICS:
            DashboardMetric.objects.get_or_create(
                name=name,
                defaults={
                    "value": value,
                    "change_percent": change,
                    "period": period,
                },
            )
        self.stdout.write(self.style.SUCCESS(f"Created {len(METRICS)} dashboard metrics"))

        # -- Activities --
        all_users = [admin] + [e.user for e in employees]
        ips = ["192.168.1.42", "10.0.0.15", "172.16.5.100", "192.168.2.88"]
        activity_count = 0
        for _ in range(50):
            user = random.choice(all_users)
            template = random.choice(ACTIVITY_TEMPLATES)
            action = template[0]
            desc_template = template[1]
            desc = desc_template.format(
                dept=random.choice(list(departments.values())).name,
                project=random.choice(projects).name if projects else "Project",
                name=random.choice(all_users).get_full_name(),
                ip=random.choice(ips),
            )
            Activity.objects.create(
                user=user,
                action=action,
                description=desc,
                ip_address=random.choice(ips),
            )
            activity_count += 1
        self.stdout.write(self.style.SUCCESS(f"Created {activity_count} activity records"))

        # -- Notifications --
        notif_count = 0
        for user in all_users[:10]:
            for _ in range(random.randint(2, 5)):
                template = random.choice(NOTIFICATION_TEMPLATES)
                level, title, message = template
                message = message.format(
                    name=random.choice(all_users).get_full_name(),
                    dept=random.choice(list(departments.values())).name,
                    ip=random.choice(ips),
                )
                Notification.objects.create(
                    user=user,
                    title=title,
                    message=message,
                    level=level,
                    read=random.choice([True, False, False]),
                )
                notif_count += 1
        self.stdout.write(self.style.SUCCESS(f"Created {notif_count} notifications"))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Demo data seeded successfully!"))
        self.stdout.write(f"  Admin login: admin / admin")
        self.stdout.write(f"  Employee login: (any employee username) / demo1234")
        self.stdout.write(f"  Dashboard: http://localhost:8000/")
        self.stdout.write(f"  Admin panel: http://localhost:8000/admin/")
        self.stdout.write(f"  API: http://localhost:8000/api/")
