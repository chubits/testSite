from datetime import date, timedelta

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from users.models import OsagoPolicy, UserProfile


class Command(BaseCommand):
    help = "Creates test users and draft OSAGO policies for load testing."

    def add_arguments(self, parser):
        parser.add_argument("--users", type=int, default=100, help="How many users to create.")
        parser.add_argument(
            "--password",
            default="LoadTestPass123!",
            help="Password assigned to every generated user.",
        )
        parser.add_argument(
            "--prefix",
            default="loaduser",
            help="Username prefix, e.g. loaduser001.",
        )
        parser.add_argument(
            "--policies-per-user",
            type=int,
            default=2,
            help="How many draft policies to create for each user.",
        )

    def handle(self, *args, **options):
        total_users = options["users"]
        password = options["password"]
        prefix = options["prefix"]
        policies_per_user = options["policies_per_user"]

        created_users = 0
        created_policies = 0
        today = date.today()

        for number in range(1, total_users + 1):
            username = f"{prefix}{number:03d}"
            email = f"{username}@example.com"
            user, was_created = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": email,
                },
            )
            if was_created:
                user.set_password(password)
                user.save(update_fields=["password"])
                created_users += 1

            profile, _ = UserProfile.objects.get_or_create(user=user)
            if not profile.phone:
                profile.phone = f"+7999{number:07d}"[-12:]
            if not profile.role:
                profile.role = "agent" if number % 2 else "broker"
            profile.save(update_fields=["phone", "role"])

            existing_policies = OsagoPolicy.objects.filter(created_by=user).count()
            missing_policies = max(policies_per_user - existing_policies, 0)
            for policy_index in range(missing_policies):
                serial = existing_policies + policy_index + 1
                OsagoPolicy.objects.create(
                    created_by=user,
                    status="draft",
                    insured_last_name=f"Тестов{number}",
                    insured_first_name="Нагрузочный",
                    insured_middle_name="Профиль",
                    insured_dob=date(1990, 1, 1),
                    insured_phone=f"+7999{number:07d}"[-12:],
                    insured_email=email,
                    vehicle_make="Lada",
                    vehicle_model="Granta",
                    vehicle_year=2020,
                    vehicle_vin=f"VIN{number:03d}{serial:02d}",
                    vehicle_plate=f"A{number:03d}AA77",
                    vehicle_category="B",
                    engine_power=98,
                    drivers_type="limited",
                    policy_start=today,
                    policy_end=today + timedelta(days=365),
                    insurer_name="Тестовая страховая",
                    premium_amount="9500.00",
                    policy_number=f"LOAD-{number:03d}-{serial:02d}",
                    notes="Created for Locust load testing.",
                )
                created_policies += 1

        self.stdout.write(self.style.SUCCESS(
            f"Load data ready: users created={created_users}, policies created={created_policies}."
        ))