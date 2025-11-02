Clinic OPD Management System (Desktop Application)

**Project Information**
| Field | Details |
|------|---------|
| **Student Name** | Krrishkumar |
| **Course** | MCA Data Science |
| **Subject** | Python Programming  |
| **Semester** | 1st Sem |
| **Institution** | Chandigarh University |

---

## 📌 **Project Overview**
This is a **Clinic OPD (Outpatient Department) Management System** built using **Python (CustomTkinter GUI) and MySQL**.  
It automates patient registration, appointment scheduling, doctor consultations, prescriptions, and billing.

The system provides a **modern dark UI** with a dashboard displaying daily patients, revenue, charts, and analytics.

---

## 🏥 **Features Implemented**

### ✅ Patient Management
- Register new patients
- Store Name, Age, Gender, Phone and Address
- View patient list with table display
- Search patient by Name, Phone or ID *(feature added)*

### ✅ Appointments
- Create appointments with date & time slot
- View appointments by selected date
- Mark appointments as completed

### ✅ Doctor Module
- View pending appointments
- Add diagnosis, medicines, dosage & notes
- Save prescription
- Export **Prescription PDF**

### ✅ Billing Module
- Import medicines from prescription
- Add bill items manually
- Auto calculate totals
- Export **Invoice PDF**

### ✅ Dashboard & Analytics
- Patients per day chart
- Appointment status pie chart
- Disease distribution

---

## 🛠️ **Tech Stack**

| Component | Technology |
|----------|------------|
| GUI | CustomTkinter |
| Backend | Python |
| Database | MySQL |
| Plotting | Matplotlib |
| PDF Generation | ReportLab |
| Widgets/Table | ttk Treeview |

---

## 📂 **Project Structure**

Clinic-OPD-Management/
│
├── app.py # Main Application GUI
├── models.py # Database Query Logic
├── utils.py # PDF Export Helpers
├── db.py # MySQL Connection Helper
├── requirements.txt # Dependencies
└── README.md # Documentation


---

## 🚀 **How to Run**

### 1️⃣ Install Requirements
pip install -r requirements.txt

bash
Copy code

### 2️⃣ Configure MySQL in `db.py`
```python
DB_CONFIG = {
 'host':'localhost',
 'user':'root',
 'password':'your_password',
 'database':'clinicdb',
 'port':3306
}
3️⃣ Start App
nginx
Copy code
python app.py

📌 Future Enhancements
Add Login / Staff roles

Send SMS reminders

Online appointment booking portal

👨‍💻 Author
Your Name : Krishkumar
MCA Data Science Student
Chandigarh University

