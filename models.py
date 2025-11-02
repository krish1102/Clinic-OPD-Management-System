# models.py
from db import db
from datetime import date

# --- Patients ---
def insert_patient(name, age, gender, phone, address):
    q = "INSERT INTO patient (name,age,gender,phone,address) VALUES (%s,%s,%s,%s,%s)"
    db.execute(q, (name, age, gender, phone, address))

def list_patients(limit=1000):
    return db.fetchall("SELECT patient_id,name,age,gender,phone FROM patient ORDER BY created_at DESC LIMIT %s", (limit,))

def search_patients(query, limit=200):
    """
    Search patients by ID (exact), name (partial) or phone (partial).
    If query is empty, returns recent patients (same as list_patients).
    """
    qstr = query.strip() if query is not None else ""
    if not qstr:
        return list_patients(limit)
    # treat possible integer id
    try:
        pid = int(qstr)
    except:
        pid = -1
    like = f"%{qstr}%"
    sql = """SELECT patient_id, name, age, gender, phone
             FROM patient
             WHERE patient_id = %s OR name LIKE %s OR phone LIKE %s
             ORDER BY created_at DESC
             LIMIT %s"""
    return db.fetchall(sql, (pid, like, like, limit))

# --- Appointments ---
def create_appointment(patient_id, ap_date, time_slot):
    q = "INSERT INTO appointment (patient_id,date,time_slot,status) VALUES (%s,%s,%s,'Pending')"
    db.execute(q, (patient_id, ap_date, time_slot))

def list_appointments_for_date(ap_date):
    q = """SELECT a.appointment_id, a.time_slot, a.status, p.name
           FROM appointment a JOIN patient p ON a.patient_id=p.patient_id
           WHERE a.date=%s ORDER BY a.time_slot"""
    return db.fetchall(q, (ap_date,))

def mark_appointment_completed(appt_id):
    db.execute("UPDATE appointment SET status='Completed' WHERE appointment_id=%s", (appt_id,))

# --- Prescriptions ---
def save_prescription(appt_id, diagnosis, medicines, dosage, notes, follow_up):
    q = """INSERT INTO prescription (appointment_id, diagnosis, medicines, dosage, notes, follow_up_date)
           VALUES (%s,%s,%s,%s,%s,%s)"""
    db.execute(q, (appt_id, diagnosis, medicines, dosage, notes, follow_up))

def latest_prescription_for_appt(appt_id):
    return db.fetchone("SELECT * FROM prescription WHERE appointment_id=%s ORDER BY created_at DESC LIMIT 1", (appt_id,))

# --- Billing (itemized) ---
def create_bill(appointment_id, items):
    """
    items: list of dicts {'item_name':..., 'qty':int, 'price':float}
    returns bill_id
    """
    total = sum(i['qty'] * i['price'] for i in items)
    # Keep original column names used in app (total_amount + date)
    db.execute("INSERT INTO billing (appointment_id, total_amount, date) VALUES (%s,%s,CURDATE())", (appointment_id, total))
    # get last inserted bill_id
    row = db.fetchone("SELECT LAST_INSERT_ID() AS id")
    bill_id = row['id']
    params = []
    for it in items:
        params.append((bill_id, it['item_name'], it['qty'], it['price']))
    db.executemany("INSERT INTO billing_items (bill_id, item_name, qty, price) VALUES (%s,%s,%s,%s)", params)
    return bill_id

def get_bill(bill_id):
    bill = db.fetchone("SELECT * FROM billing WHERE bill_id=%s", (bill_id,))
    items = db.fetchall("SELECT * FROM billing_items WHERE bill_id=%s", (bill_id,))
    return bill, items

# --- Helpers ---
def get_pending_appointments_today():
    today = date.today().isoformat()
    return db.fetchall("""SELECT a.appointment_id, p.name, a.time_slot FROM appointment a
                          JOIN patient p ON a.patient_id=p.patient_id
                          WHERE a.date=%s AND a.status='Pending' ORDER BY a.time_slot""", (today,))

def get_appointments_for_billing():
    # appointments (recent) that can be billed
    return db.fetchall("""SELECT a.appointment_id, p.name, a.date, a.time_slot, a.status FROM appointment a
                          JOIN patient p ON a.patient_id=p.patient_id
                          ORDER BY a.date DESC LIMIT 500""")

# --- New analytics functions for dashboard ---

def get_revenue_last_n_days(n=30):
    """
    Returns list of dicts with keys: date (DATE), total (sum)
    """
    # MySQL: CURDATE() - INTERVAL n DAY
    q = """SELECT date AS date, COALESCE(SUM(total_amount),0) AS total
           FROM billing
           WHERE date >= (CURDATE() - INTERVAL %s DAY)
           GROUP BY date
           ORDER BY date"""
    return db.fetchall(q, (n,))

def get_age_group_counts():
    """
    Returns aggregated counts by age group:
    <18, 18-35, 36-50, 51-65, 66+
    """
    q = """
    SELECT
      CASE
        WHEN age IS NULL THEN 'Unknown'
        WHEN age < 18 THEN '<18'
        WHEN age BETWEEN 18 AND 35 THEN '18-35'
        WHEN age BETWEEN 36 AND 50 THEN '36-50'
        WHEN age BETWEEN 51 AND 65 THEN '51-65'
        ELSE '66+'
      END AS age_group,
      COUNT(*) AS cnt
    FROM patient
    GROUP BY age_group
    ORDER BY
      CASE
        WHEN age_group = '<18' THEN 1
        WHEN age_group = '18-35' THEN 2
        WHEN age_group = '36-50' THEN 3
        WHEN age_group = '51-65' THEN 4
        WHEN age_group = '66+' THEN 5
        WHEN age_group = 'Unknown' THEN 6
        ELSE 7
      END
    """
    return db.fetchall(q)

def get_appointment_status_counts():
    """
    Returns list of dicts: {'status':..., 'cnt':...}
    """
    q = "SELECT status, COUNT(*) AS cnt FROM appointment GROUP BY status"
    return db.fetchall(q)

def get_today_revenue():
    return db.fetchone("SELECT COALESCE(SUM(total_amount),0) AS total FROM billing WHERE date = CURDATE()")['total']

def get_total_revenue():
    return db.fetchone("SELECT COALESCE(SUM(total_amount),0) AS total FROM billing")['total']

def get_disease_distribution(limit=10):
    q = """
        SELECT diagnosis, COUNT(*) AS cnt
        FROM prescription
        WHERE diagnosis IS NOT NULL AND diagnosis <> ''
        GROUP BY diagnosis
        ORDER BY cnt DESC
        LIMIT %s
    """
    return db.fetchall(q, (limit,))

def get_revenue_for_date(d):
    row = db.fetchone("SELECT COALESCE(SUM(total_amount),0) AS total FROM billing WHERE date=%s", (d,))
    return row['total'] if row else 0

def get_appointment_status_counts_for_date(date_str):
    return db.fetchall("""
        SELECT status, COUNT(*) AS cnt
        FROM appointment
        WHERE date = %s
        GROUP BY status
    """, (date_str,))
def count_all_appointments():
    row = db.fetchone("SELECT COUNT(*) AS cnt FROM appointment")
    return row['cnt'] if row else 0


def list_all_appointments(limit=1000):
    return db.fetchall("""
        SELECT a.appointment_id, p.name, a.date, a.time_slot, a.status
        FROM appointment a 
        JOIN patient p ON a.patient_id = p.patient_id
        ORDER BY a.date DESC, a.time_slot DESC
        LIMIT %s
    """, (limit,))

