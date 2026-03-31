from locust import HttpUser, task, between
import random

NAMES = ["Ali Hassan", "Sara Khan", "Ahmed Raza", "Fatima Malik", "Usman Tariq"]
SUBJECTS = ["Login issue", "API not working", "Export failed", "Slack not connecting", "Dashboard slow"]
MESSAGES = [
    "I cannot login to my account since this morning",
    "The API endpoint is returning 500 errors",
    "Export button is not working on dashboard",
    "Slack integration keeps disconnecting",
    "Dashboard is loading very slowly today",
]
CATEGORIES = ["general", "technical", "feedback", "bug_report"]
EMAILS = [
    "wm0297567@gmail.com",
    "muhammadwaheed128@gmail.com",
    "loadtest1@example.com",
    "loadtest2@example.com",
    "loadtest3@example.com",
]

class WebFormUser(HttpUser):
    """Simulate users submitting support forms."""
    wait_time = between(2, 8)
    weight = 3

    @task(3)
    def submit_support_form(self):
        self.client.post("/support/submit", json={
            "name": random.choice(NAMES),
            "email": f"load{random.randint(1,9999)}@test.com",
            "subject": random.choice(SUBJECTS),
            "category": random.choice(CATEGORIES),
            "priority": "medium",
            "message": random.choice(MESSAGES),
        })

    @task(1)
    def check_metrics_summary(self):
        self.client.get("/metrics/summary")

    @task(1)
    def check_metrics_channels(self):
        self.client.get("/metrics/channels")

class APIUser(HttpUser):
    """Simulate API consumers."""
    wait_time = between(5, 15)
    weight = 1

    @task(2)
    def submit_and_check(self):
        # Submit ticket
        res = self.client.post("/support/submit", json={
            "name": "API Test User",
            "email": random.choice(EMAILS),
            "subject": "API Load Test",
            "category": "general",
            "message": "Load testing the API endpoints for verification",
        })
        if res.status_code == 200:
            ticket_id = res.json().get("ticket_id")
            if ticket_id:
                self.client.get(f"/support/ticket/{ticket_id}")

    @task(1)
    def check_daily_report(self):
        self.client.get("/metrics/daily-report")
