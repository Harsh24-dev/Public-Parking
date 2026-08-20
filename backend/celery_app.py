from celery import Celery
from app import app
from .models import *
from .mail import send_mail
from datetime import datetime, timedelta
import csv, os, re
from celery.schedules import crontab
from jinja2 import Template

celery = Celery('tasks', broker='redis://127.0.0.1:6379/0')
celery.conf.update(timezone='Asia/Kolkata', enable_utc=False)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXPORT_DIR = os.path.abspath(os.path.join(BASE_DIR, '..', 'static'))
os.makedirs(EXPORT_DIR, exist_ok=True)

@celery.task()
def generate_csv(data, filename="report.csv"):
    filepath = os.path.join(EXPORT_DIR, filename)
    if not data:
        print(f"No data to export for {filename}")
        return

    with open(filepath, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)

    print(f"CSV generated at: {filepath}")

@celery.task()
def daily_reminders():
    with app.app_context():
        users = User.query.all()
        for user in users:
            has_active = Reservation.query.filter_by(user_id=user.id, parking_leaving_time=None).first()
            if not has_active:
                send_mail(
                    user.email,
                    "Reminder: Book Your Parking Spot!",
                    f"Hey {user.full_name},\n\nYou haven’t booked a spot today.\n"
                    "Visit the app and reserve your spot now: http://localhost:5173/"
                )
    print("Daily reminders sent")

@celery.task()
def monthly_report():
    with app.app_context():
        users = User.query.all()
        for user in users:
            this_month = datetime.utcnow().month
            reservations = Reservation.query.filter(
                Reservation.user_id == user.id,
                Reservation.parking_start_time != None,
                db.extract('month', Reservation.parking_start_time) == this_month
            ).all()

            lot_usage = {}
            total_cost = 0
            data = []

            for i, r in enumerate(reservations, start=1):
                spot = Spot.query.get(r.spot_id)
                lot = Lot.query.get(spot.lot_id) if spot else None
                lot_name = lot.name if lot else "N/A"
                lot_usage[lot_name] = lot_usage.get(lot_name, 0) + 1
                cost = r.cost or 0.0
                total_cost += cost

                data.append({
                    "No": i,
                    "Lot": lot_name,
                    "Start Time": r.parking_start_time.strftime("%Y-%m-%d %H:%M"),
                    "End Time": r.parking_leaving_time.strftime("%Y-%m-%d %H:%M") if r.parking_leaving_time else "Active",
                    "Cost": f"₹{cost:.2f}"
                })

            if not data:
                continue

            safe_email = re.sub(r'[^a-zA-Z0-9]', '_', user.email)
            filename = f"{safe_email}_monthly_report.csv"
            generate_csv.delay(data, filename=filename)

            most_used = max(lot_usage.items(), key=lambda x: x[1])[0] if lot_usage else "N/A"

            template = Template("""
                <html>
                <body>
                <h2>Monthly Parking Report</h2>
                <p><strong>Most Used Lot:</strong> {{ most_used }}</p>
                <p><strong>Total Reservations:</strong> {{ total }}</p>
                <p><strong>Total Spent:</strong> ₹{{ total_cost }}</p>

                <h3>Details:</h3>
                <table border="1" cellpadding="6" cellspacing="0">
                  <tr>
                    <th>No</th>
                    <th>Lot</th>
                    <th>Start Time</th>
                    <th>End Time</th>
                    <th>Cost</th>
                  </tr>
                  {% for item in data %}
                  <tr>
                    <td>{{ item.No }}</td>
                    <td>{{ item.Lot }}</td>
                    <td>{{ item["Start Time"] }}</td>
                    <td>{{ item["End Time"] }}</td>
                    <td>{{ item.Cost }}</td>
                  </tr>
                  {% endfor %}
                </table>

                <p><a href="http://127.0.0.1:5000/static/{{ csv_filename }}">Download CSV Report</a></p>
                </body>
                </html>
            """)

            html = template.render(
                data=data,
                most_used=most_used,
                total=len(data),
                total_cost=round(total_cost, 2),
                csv_filename=filename
            )

            send_mail(user.email, "Your Monthly Parking Report", html, html=True)

    print("Monthly reports sent")

@celery.task()
def export_csv_for_user(user_id):
    with app.app_context():
        user = User.query.get(user_id)
        if not user:
            print(f"User not found for export: {user_id}")
            return

        reservations = Reservation.query.filter_by(user_id=user.id).all()
        data = []

        for i, r in enumerate(reservations, start=1):
            spot = Spot.query.get(r.spot_id)
            lot = Lot.query.get(spot.lot_id) if spot else None
            data.append({
                "No": i,
                "Lot": lot.name if lot else "N/A",
                "Spot ID": spot.id if spot else "N/A",
                "Start Time": r.parking_start_time.strftime("%Y-%m-%d %H:%M"),
                "End Time": r.parking_leaving_time.strftime("%Y-%m-%d %H:%M") if r.parking_leaving_time else "Active",
                "Cost": f"₹{r.cost or 0.0:.2f}",
                "Remarks": "Active" if r.parking_leaving_time is None else "Completed"
            })

        if not data:
            print(f"No reservations for user {user.email}")
            return

        safe_email = re.sub(r'[^a-zA-Z0-9]', '_', user.email)
        filename = f"{safe_email}_export.csv"
        generate_csv.delay(data, filename=filename)

        html_content = f"""
        <html>
        <body>
        <p>Hi {user.full_name},</p>
        <p>Your CSV report is ready:</p>
        <p><a href="http://127.0.0.1:5000/static/{filename}">Download CSV</a></p>
        </body>
        </html>
        """

        send_mail(user.email, "Your Requested Parking Report", html_content, html=True)
        print(f"Export complete: {filename}")

celery.conf.beat_schedule = {
    'send_daily_reminders': {
        'task': 'backend.celery_app.daily_reminders',
        'schedule': crontab(hour=18, minute=0), # daily at 6 PM
        #'schedule': timedelta(seconds=30),
    },
    'send_monthly_report': {
        'task': 'backend.celery_app.monthly_report',
        'schedule': crontab(hour=9, minute=0, day_of_month=1),  # 9 AM on 1st
        #'schedule': timedelta(seconds=30),  # for testing
    },
}