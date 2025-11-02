# utils.py
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from datetime import datetime

def export_prescription_pdf(filename, patient_info, prescription):
    # patient_info: dict with name, age, gender, phone, address
    # prescription: dict with diagnosis, medicines, dosage, notes, follow_up_date, created_at
    c = canvas.Canvas(filename, pagesize=A4)
    w, h = A4
    c.setFont("Helvetica-Bold", 14)
    c.drawString(40, h-60, "City Care Clinic")
    c.setFont("Helvetica", 11)
    c.drawString(40, h-90, f"Patient Name: {patient_info.get('name','')}")
    c.drawString(300, h-90, f"Age: {patient_info.get('age','')}  Gender: {patient_info.get('gender','')}")
    c.drawString(40, h-110, f"Phone: {patient_info.get('phone','')}")
    c.drawString(40, h-140, "Diagnosis:")
    t = c.beginText(40, h-160); t.setFont("Helvetica", 11)
    for line in (prescription.get('diagnosis') or "").split("\n"):
        t.textLine(line)
    c.drawText(t)
    c.drawString(40, h-250, "Medicines & Dosage:")
    t2 = c.beginText(40, h-270); t2.setFont("Helvetica", 11)
    meds = prescription.get('medicines','')
    dos = prescription.get('dosage','')
    meds_list = [m.strip() for m in meds.split(",") if m.strip()]
    for i,m in enumerate(meds_list, start=1):
        t2.textLine(f"{i}. {m} - {dos}")
    c.drawText(t2)
    c.drawString(40, h-380, f"Notes: {prescription.get('notes','')}")
    c.drawString(40, h-410, f"Follow-up Date: {prescription.get('follow_up_date') or 'N/A'}")
    c.drawString(40, h-460, f"Date: {prescription.get('created_at') or datetime.now()}")
    c.drawString(40, h-500, "Doctor Signature: ____________________")
    c.save()

def export_invoice_pdf(filename, bill, items, patient_name):
    c = canvas.Canvas(filename, pagesize=A4)
    w, h = A4
    c.setFont("Helvetica-Bold", 16); c.drawString(40, h-60, "City Care Clinic   Invoice")
    c.setFont("Helvetica", 11)
    c.drawString(40, h-90, f"Patient / Visit: {patient_name}")
    c.drawString(40, h-110, f"Bill ID: {bill['bill_id']}   Date: {bill['date']}")
    # table header
    y = h-150
    c.drawString(40, y, "Item"); c.drawString(320, y, "Qty"); c.drawString(420, y, "Price"); c.drawString(520, y, "Amount")
    y -= 20
    total = 0
    for it in items:
        amt = it['qty'] * float(it['price'])
        c.drawString(40, y, it['item_name'])
        c.drawString(320, y, str(it['qty']))
        c.drawString(420, y, f"{it['price']:.2f}")
        c.drawString(520, y, f"{amt:.2f}")
        total += amt
        y -= 18
        if y < 120:
            c.showPage(); y = h-60
    c.drawString(420, y-10, "Total:"); c.drawString(520, y-10, f"{total:.2f}")
    c.save()
