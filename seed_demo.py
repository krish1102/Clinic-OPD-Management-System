# seed_demo.py
from db import db
import random
from datetime import date

def seed(n=50):
    first = ["Aman","Riya","Vikram","Priya","Arun","Sneha","Rohan","Meera","Karan","Sonal","Deepa","Nitin","Anita","Pooja","Rahul","Sahil","Nisha","Varun","Tina","Jay"]
    last = ["Sharma","Verma","Singh","Patel","Kumar","Nair","Joshi","Gupta","Reddy","Mehta"]
    patients = []
    for i in range(n):
        name = f"{random.choice(first)} {random.choice(last)}"
        age = random.randint(8,70)
        gender = random.choice(["Male","Female","Other"])
        phone = str(9000000000 + random.randint(0,99999999))
        addr = random.choice(["Jaipur","Delhi","Mumbai","Pune","Chennai","Bangalore"])
        patients.append((name,age,gender,phone,addr))
    db.executemany("INSERT INTO patient (name,age,gender,phone,address) VALUES (%s,%s,%s,%s,%s)", patients)
    rows = db.fetchall("SELECT patient_id FROM patient ORDER BY created_at DESC LIMIT %s", (n+10,))
    pids = [r['patient_id'] for r in rows]
    times = ["09:00","09:20","09:40","10:00","10:20","10:40","11:00","11:20","11:40","12:00","12:20","12:40","14:00","14:20","14:40"]
    today = date.today().isoformat()
    appts = [(pid, today, random.choice(times), 'Pending') for pid in pids[:n]]
    db.executemany("INSERT INTO appointment (patient_id,date,time_slot,status) VALUES (%s,%s,%s,%s)", appts)
    print("Seeded demo data.")

if __name__ == "__main__":
    seed()
