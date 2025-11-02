# app.py
import customtkinter as ctk
from tkinter import messagebox, ttk
from datetime import date, datetime
import matplotlib

# use Agg backend for embedding in Tkinter
matplotlib.use("Agg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

import models, utils, seed_demo

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("green")

class ClinicApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Clinic OPD - Dark Professional")
        self.geometry("1100x700")
        self.sidebar = ctk.CTkFrame(self, width=200); self.sidebar.pack(side="left", fill="y")
        self.header = ctk.CTkFrame(self, height=60); self.header.pack(side="top", fill="x")
        self.main = ctk.CTkFrame(self); self.main.pack(side="right", fill="both", expand=True)
        ctk.CTkLabel(self.header, text="Clinic OPD Management", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left", padx=12)

        for t,c in [("Dashboard", self.show_dashboard), ("Register", self.show_register),
                    ("Add Appointment", self.show_add_appointment), ("Appointments", self.show_appointments),
                    ("Doctor", self.show_doctor), ("Billing", self.show_billing),
                    ("Exit", self.destroy)]:
            ctk.CTkButton(self.sidebar, text=t, command=c).pack(padx=12, pady=8, fill="x")
        self.show_dashboard()

    def clear(self):
        for w in self.main.winfo_children(): w.destroy()

    # ---------- DASHBOARD ----------
    def show_dashboard(self):
        self.clear()
        plt.style.use('seaborn-v0_8-darkgrid')
        header_frame = ctk.CTkFrame(self.main)
        header_frame.pack(fill="x", padx=12, pady=8)
        today = date.today().isoformat()

        appts_today = models.list_appointments_for_date(today)
        patients_today = len(appts_today)

        # ✅ Total appointments lifetime
        total_appts_lifetime = models.count_all_appointments()

        today_rev = models.get_revenue_for_date(today) or 0
        total_rev = models.get_total_revenue() or 0

        stat_font = ctk.CTkFont(size=16, weight="bold")
        for label in [
            (f"Patients Today\n{patients_today}"),
            (f"Total Appointments (Lifetime)\n{total_appts_lifetime}"),
            (f"Today's Revenue\n₹{today_rev:.2f}"),
            (f"Total Revenue\n₹{total_rev:.2f}")
]:

            ctk.CTkLabel(header_frame, text=label, font=stat_font).pack(side="left", padx=15)

        charts_frame = ctk.CTkFrame(self.main)
        charts_frame.pack(fill="both", expand=True, padx=12, pady=6)

        fig = plt.Figure(figsize=(10,5), tight_layout=True)
        ax1 = fig.add_subplot(1,2,1)
        ax2 = fig.add_subplot(1,2,2)

        dis = models.get_disease_distribution(10)
        diseases = [r['diagnosis'] for r in dis] if dis else ["No Data"]
        counts = [int(r['cnt']) for r in dis] if dis else [1]
        ax1.bar(diseases, counts)
        ax1.set_title("Disease Distribution")
        ax1.tick_params(axis='x', rotation=45)

        appt_stats = models.get_appointment_status_counts_for_date(today)
        statuses = [r['status'] for r in appt_stats] or ['No Data']
        st_counts = [int(r['cnt']) for r in appt_stats] or [1]
        ax2.pie(st_counts, labels=statuses, autopct='%1.1f%%')

        canvas = FigureCanvasTkAgg(fig, master=charts_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=8, pady=8)

    # ---------- REGISTER PATIENT ----------
    def show_register(self):
        self.clear()
        frame = ctk.CTkFrame(self.main); frame.pack(fill="both", expand=True, padx=12, pady=8)

        left = ctk.CTkFrame(frame, width=320); left.pack(side="left", fill="y", padx=(0,12))
        ctk.CTkLabel(left, text="Register Patient", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=6)

        name=ctk.StringVar(); age=ctk.StringVar(); phone=ctk.StringVar(); addr=ctk.StringVar(); gender=ctk.StringVar()

        def labeled(p, t, v, ph=""):
            ctk.CTkLabel(p, text=t).pack(fill="x")
            e=ctk.CTkEntry(p, textvariable=v, placeholder_text=ph); e.pack(fill="x", pady=(2,8))

        labeled(left,"Full name",name,"e.g., Rohan Sharma")
        labeled(left,"Age",age,"32")

        ctk.CTkLabel(left, text="Gender").pack(fill="x")
        ttk.Combobox(left, values=["Male","Female","Other","Prefer not to say"], textvariable=gender, width=28).pack(fill="x", pady=(2,8))

        labeled(left,"Phone",phone,"10-digit")
        labeled(left,"Address",addr,"City / Address")
        ctk.CTkButton(left, text="Save", command=lambda: self._save_patient(name,age,gender,phone,addr)).pack(pady=6)

        right = ctk.CTkFrame(frame); right.pack(side="left", fill="both", expand=True)

        search_frame = ctk.CTkFrame(right); search_frame.pack(fill="x", padx=6, pady=(6,4))
        search_var = ctk.StringVar()
        ctk.CTkEntry(search_frame, placeholder_text="Search by ID / Name / Phone", textvariable=search_var).pack(side="left", fill="x", expand=True, padx=(0,6))
        ctk.CTkButton(search_frame, text="Search", width=90, command=lambda: load_search()).pack(side="left", padx=(0,6))
        ctk.CTkButton(search_frame, text="Clear", width=80, command=lambda: load_all()).pack(side="left")

        cols=("ID","Name","Age","Gender","Phone")
        tree=ttk.Treeview(right, columns=cols, show="headings", height=14)
        for c in cols: tree.heading(c,text=c)
        tree.pack(fill="both",expand=True,padx=6,pady=6)
        self.tree_pat = tree

        def load_rows(rows):
            for i in tree.get_children(): tree.delete(i)
            for r in rows:
                tree.insert("", "end", values=(r['patient_id'], r['name'], r['age'], r['gender'], r['phone']))

        def load_all(): load_rows(models.list_patients(200))
        def load_search(): load_rows(models.search_patients(search_var.get(), 200))
        load_all()

    def _save_patient(self, name, age, gender, phone, addr):
        if not name.get().strip(): messagebox.showwarning("Missing","Name required"); return
        try: a = int(age.get().strip()) if age.get().strip() else None
        except: messagebox.showerror("Age","Invalid age"); return
        models.insert_patient(name.get().strip(), a, gender.get().strip(), phone.get().strip(), addr.get().strip())
        messagebox.showinfo("Saved","Patient saved"); self.show_register()

    # ---------- ADD APPOINTMENT ----------
    def show_add_appointment(self):
        self.clear()
        frm = ctk.CTkFrame(self.main); frm.pack(fill="both", expand=True, padx=12, pady=8)
        ctk.CTkLabel(frm, text="Add Appointment", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=6)

        pats = models.list_patients(1000)
        patient_map = {f"{p['patient_id']} - {p['name']} ({p.get('phone','')})": p['patient_id'] for p in pats}
        patient_var = ctk.StringVar()
        ttk.Combobox(frm, values=list(patient_map.keys()), textvariable=patient_var, width=60).pack(pady=6)

        date_var = ctk.StringVar(value=date.today().isoformat())
        time_var = ctk.StringVar(value="09:00")
        ctk.CTkEntry(frm, textvariable=date_var, width=160).pack(pady=4)
        ctk.CTkEntry(frm, textvariable=time_var, width=160).pack(pady=4)

        def add():
            if not patient_var.get(): return messagebox.showwarning("Select","Select a patient")
            try: datetime.fromisoformat(date_var.get())
            except: return messagebox.showerror("Date","Invalid date format")
            models.create_appointment(patient_map[patient_var.get()], date_var.get(), time_var.get())
            messagebox.showinfo("Added","Appointment created")
            patient_var.set(""); time_var.set("09:00"); date_var.set(date.today().isoformat())

        ctk.CTkButton(frm, text="Create Appointment", command=add).pack(pady=8)

    # ---------- LIFETIME APPOINTMENTS + SEARCH ----------
    def show_appointments(self):
        self.clear()
        frm=ctk.CTkFrame(self.main); frm.pack(fill="both",expand=True,padx=12,pady=8)
        ctk.CTkLabel(frm, text="Appointments (Lifetime)", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=6)

        search = ctk.StringVar()
        sf = ctk.CTkFrame(frm); sf.pack(fill="x", pady=6)
        ctk.CTkEntry(sf, placeholder_text="Search by Name / Phone / Date", textvariable=search).pack(side="left", fill="x", expand=True, padx=6)
        ctk.CTkButton(sf, text="Search", command=lambda: load(search.get())).pack(side="left", padx=6)
        ctk.CTkButton(sf, text="Show All", command=lambda: load("")).pack(side="left", padx=6)

        tree=ttk.Treeview(frm, columns=("ApptID","Patient","Date","Time","Status"), show="headings", height=17)
        for c in ("ApptID","Patient","Date","Time","Status"):
            tree.heading(c,text=c); tree.column(c,anchor="center")
        tree.pack(fill="both",expand=True,padx=6,pady=6)

        def load(q):
            for i in tree.get_children(): tree.delete(i)
            rows = models.search_appointments(q) if q else models.list_all_appointments(2000)
            for r in rows:
                tree.insert("", "end", values=(r['appointment_id'], r['name'], r['date'], r['time_slot'], r['status']))

        def complete():
            sel = tree.selection()
            if not sel: return messagebox.showwarning("Select","Select appointment")
            models.mark_appointment_completed(tree.item(sel[0])['values'][0])
            load(search.get())

        ctk.CTkButton(frm, text="Mark Completed", command=complete).pack(pady=4)
        load("")


    def _mark_complete(self, tree, reload_cb):
        sel = tree.selection()
        if not sel: messagebox.showwarning("Select","Select appointment"); return
        apid = tree.item(sel[0])['values'][0]
        models.mark_appointment_completed(apid)
        messagebox.showinfo("Done","Marked Completed")
        reload_cb()

    # Doctor (prescription)
    def show_doctor(self):
        self.clear()
        frm=ctk.CTkFrame(self.main); frm.pack(fill="both",expand=True,padx=12,pady=8)
        left=ctk.CTkFrame(frm, width=300); left.pack(side="left", fill="y", padx=(0,12))
        ctk.CTkLabel(left, text="Pending (Today)", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=6)

        tree=ttk.Treeview(left, columns=("ApptID","Patient","Time"), show="headings", height=20)
        for c in ("ApptID","Patient","Time"):
            tree.heading(c,text=c); tree.column(c,anchor="center")
        tree.pack(fill="both",expand=True,padx=6,pady=6)

        def load(): 
            for i in tree.get_children(): tree.delete(i)
            for r in models.get_pending_appointments_today():
                tree.insert("", "end", values=(r['appointment_id'], r['name'], r['time_slot']))
        load()
        ctk.CTkButton(left, text="Refresh", command=load).pack(pady=6)

        right=ctk.CTkFrame(frm); right.pack(side="left", fill="both", expand=True)
        info_lbl = ctk.CTkLabel(right, text="Load an appointment", anchor="w")
        info_lbl.pack(fill="x", pady=(0,6))

        diag = ctk.StringVar(); meds = ctk.StringVar(); dosage = ctk.StringVar(); notes = ctk.StringVar(); follow = ctk.StringVar()
        def labeled(p,txt,var):
            ctk.CTkLabel(p,text=txt).pack(fill="x")
            ctk.CTkEntry(p,textvariable=var).pack(fill="x",pady=(2,8))
        labeled(right,"Diagnosis",diag)
        labeled(right,"Medicines (comma sep)",meds)
        labeled(right,"Dosage",dosage)
        labeled(right,"Notes",notes)
        labeled(right,"Follow-up (YYYY-MM-DD)",follow)

        current_appt = {'id': None}

        def load_sel():
            sel = tree.selection()
            if not sel: messagebox.showwarning("Select","Select appointment"); return
            apid = tree.item(sel[0])['values'][0]; current_appt['id']=apid
            row = models.db.fetchone("""SELECT a.*, p.name, p.age, p.gender, p.phone 
                                        FROM appointment a JOIN patient p ON a.patient_id=p.patient_id 
                                        WHERE a.appointment_id=%s""",(apid,))
            info_lbl.configure(text=f"Patient: {row['name']}  Age:{row['age']}  Gender:{row['gender']}  Phone:{row['phone']}")
            diag.set(""); meds.set(""); dosage.set(""); notes.set(""); follow.set("")

        def save_pres():
            if not current_appt['id']: messagebox.showwarning("Load","Load appointment"); return
            models.save_prescription(current_appt['id'], diag.get(), meds.get(), dosage.get(), notes.get(), follow.get() or None)
            models.mark_appointment_completed(current_appt['id'])
            messagebox.showinfo("Saved","Prescription saved")
            load()

        ctk.CTkButton(right, text="Load Selected", command=load_sel).pack(pady=6)
        ctk.CTkButton(right, text="Save Prescription", command=save_pres).pack(pady=6)
        ctk.CTkButton(right, text="Export Prescription PDF", command=lambda: self._export_prescription(current_appt)).pack(pady=6)

    def _export_prescription(self, current_appt):
        apid = current_appt.get('id')
        if not apid: messagebox.showwarning("Load","Load appointment"); return
        pres = models.latest_prescription_for_appt(apid)
        ap = models.db.fetchone("SELECT a.*, p.name, p.age, p.gender, p.phone FROM appointment a JOIN patient p ON a.patient_id=p.patient_id WHERE a.appointment_id=%s",(apid,))
        if not pres: messagebox.showwarning("No Data","No prescription"); return
        fname = f"prescription_{apid}.pdf"
        patient_info = {'name': ap['name'], 'age': ap['age'], 'gender': ap['gender'], 'phone': ap['phone']}
        utils.export_prescription_pdf(fname, patient_info, pres)
        messagebox.showinfo("Exported", f"Saved {fname}")

    # Billing
    def show_billing(self):
        self.clear()
        frm=ctk.CTkFrame(self.main); frm.pack(fill="both",expand=True,padx=12,pady=8)
        ctk.CTkLabel(frm, text="Billing (Itemized)", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=6)

        appts = models.get_appointments_for_billing()
        apt_map = {f"{r['appointment_id']} - {r['name']} ({r['date']})": r['appointment_id'] for r in appts}
        ap_sel = ctk.StringVar()
        comb = ttk.Combobox(frm, values=list(apt_map.keys()), textvariable=ap_sel, width=60)
        comb.pack(pady=6)

        cols = ("Item","Qty","Price","Amount")
        tree = ttk.Treeview(frm, columns=cols, show="headings", height=10)
        for c in cols: tree.heading(c,text=c); tree.column(c,anchor="center")
        tree.pack(fill="both",expand=True,padx=6,pady=6)

        total_var = ctk.StringVar(value="0.00")
        def refresh_total():
            total = 0
            for iid in tree.get_children():
                it = tree.item(iid)['values']; total += float(it[3])
            total_var.set(f"{total:.2f}")

        def import_meds():
            sel_text = ap_sel.get()
            if not sel_text: messagebox.showwarning("Select","Select appointment"); return
            apid = apt_map[sel_text]
            pres = models.latest_prescription_for_appt(apid)
            if not pres:
                messagebox.showinfo("No Presc","No prescription to import")
                return
            meds = pres['medicines'] or ""
            meds_list = [m.strip() for m in meds.split(",") if m.strip()]
            for m in meds_list:
                qty = 1; price = 0.0
                amt = qty * price
                tree.insert("", "end", values=(m, qty, f"{price:.2f}", f"{amt:.2f}"))
            refresh_total()

        item_name = ctk.StringVar(); item_qty=ctk.StringVar(value="1"); item_price=ctk.StringVar(value="0.00")
        entry_frame = ctk.CTkFrame(frm); entry_frame.pack(fill="x", pady=6)
        ctk.CTkEntry(entry_frame, placeholder_text="Item name", textvariable=item_name, width=220).pack(side="left", padx=6)
        ctk.CTkEntry(entry_frame, placeholder_text="Qty", textvariable=item_qty, width=80).pack(side="left", padx=6)
        ctk.CTkEntry(entry_frame, placeholder_text="Price", textvariable=item_price, width=120).pack(side="left", padx=6)

        def add_item():
            try:
                q = int(item_qty.get()); p = float(item_price.get()); 
            except:
                messagebox.showerror("Invalid","Enter numeric qty/price"); return
            amt = q * p
            tree.insert("", "end", values=(item_name.get(), q, f"{p:.2f}", f"{amt:.2f}"))
            item_name.set(""); item_qty.set("1"); item_price.set("0.00")
            refresh_total()

        ctk.CTkButton(entry_frame, text="Add Item", command=add_item).pack(side="left", padx=6)
        ctk.CTkButton(entry_frame, text="Import Medicines", command=import_meds).pack(side="left", padx=6)

        def save_bill():
            sel_text = ap_sel.get()
            if not sel_text: messagebox.showwarning("Select","Select appointment"); return
            apid = apt_map[sel_text]
            items = []
            for iid in tree.get_children():
                it = tree.item(iid)['values']
                items.append({'item_name': str(it[0]), 'qty': int(it[1]), 'price': float(it[2])})
            if not items: messagebox.showwarning("Empty","Add at least one item"); return
            bill_id = models.create_bill(apid, items)
            bill, its = models.get_bill(bill_id)
            patient = sel_text.split("-")[1].split("(")[0].strip()
            fname = f"invoice_{bill_id}.pdf"
            utils.export_invoice_pdf(fname, bill, its, patient)
            messagebox.showinfo("Billed", f"Saved invoice {fname}")

        footer = ctk.CTkFrame(frm); footer.pack(fill="x", pady=6)
        ctk.CTkLabel(footer, text="Total: ").pack(side="left", padx=6)
        ctk.CTkLabel(footer, textvariable=total_var).pack(side="left")
        ctk.CTkButton(footer, text="Save Bill & Export Invoice", command=save_bill).pack(side="right", padx=6)

    

if __name__ == "__main__":
    app = ClinicApp(); app.mainloop()
