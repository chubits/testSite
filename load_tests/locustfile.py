import os
from datetime import date, timedelta
from itertools import count

from locust import HttpUser, between, task


USER_POOL_SIZE = int(os.getenv("LOADTEST_USER_POOL", "100"))
USERNAME_PREFIX = os.getenv("LOADTEST_USERNAME_PREFIX", "loaduser")
USER_PASSWORD = os.getenv("LOADTEST_PASSWORD", "LoadTestPass123!")


class WebsiteUser(HttpUser):
    wait_time = between(2, 5)
    host = os.getenv("LOADTEST_HOST", "http://127.0.0.1:8000")
    user_sequence = count(1)

    def on_start(self):
        user_index = ((next(self.user_sequence) - 1) % USER_POOL_SIZE) + 1
        self.username = f"{USERNAME_PREFIX}{user_index:03d}"
        self.login()

    def _get_csrf_token(self, path):
        response = self.client.get(path, name=f"GET {path}")
        token = response.cookies.get("csrftoken") or self.client.cookies.get("csrftoken")
        if not token:
            raise RuntimeError(f"CSRF token was not returned for {path}")
        return token

    def login(self):
        csrf_token = self._get_csrf_token("/")
        with self.client.post(
            "/",
            data={
                "username": self.username,
                "password": USER_PASSWORD,
                "login": "1",
                "csrfmiddlewaretoken": csrf_token,
            },
            headers={"Referer": f"{self.host}/"},
            allow_redirects=False,
            catch_response=True,
            name="POST / login",
        ) as response:
            if response.status_code not in (302, 303):
                response.failure(f"Login failed for {self.username}: {response.status_code}")

    @task(4)
    def profile_page(self):
        self.client.get("/profile/", name="GET /profile/")

    @task(4)
    def osago_list(self):
        self.client.get("/osago/", name="GET /osago/")

    @task(1)
    def create_draft_policy(self):
        csrf_token = self._get_csrf_token("/osago/new/")
        policy_number = f"LT-{self.username}-{date.today():%m%d}"
        today = date.today()
        with self.client.post(
            "/osago/new/",
            data={
                "insured_last_name": "Тестов",
                "insured_first_name": "Нагрузочный",
                "insured_middle_name": "Пользователь",
                "insured_dob": "1990-01-15",
                "insured_phone": "+79990000000",
                "insured_email": f"{self.username}@example.com",
                "vehicle_make": "Lada",
                "vehicle_model": "Vesta",
                "vehicle_year": "2021",
                "vehicle_vin": f"VIN{self.username[-3:]}{today:%d%m}",
                "vehicle_plate": f"A{self.username[-3:]}AA77",
                "vehicle_category": "B",
                "engine_power": "106",
                "drivers_type": "limited",
                "policy_start": today.isoformat(),
                "policy_end": (today + timedelta(days=365)).isoformat(),
                "insurer_name": "Тестовая страховая",
                "premium_amount": "12500.00",
                "policy_number": policy_number,
                "status": "draft",
                "notes": "Нагрузочный тест на 100 пользователей.",
                "csrfmiddlewaretoken": csrf_token,
            },
            headers={"Referer": f"{self.host}/osago/new/"},
            allow_redirects=False,
            catch_response=True,
            name="POST /osago/new/",
        ) as response:
            if response.status_code not in (302, 303):
                response.failure(f"Policy create failed for {self.username}: {response.status_code}")

    def on_stop(self):
        csrf_token = self.client.cookies.get("csrftoken") or self._get_csrf_token("/profile/")
        self.client.post(
            "/logout/",
            data={"csrfmiddlewaretoken": csrf_token},
            headers={"Referer": f"{self.host}/profile/"},
            allow_redirects=False,
            name="POST /logout/",
        )