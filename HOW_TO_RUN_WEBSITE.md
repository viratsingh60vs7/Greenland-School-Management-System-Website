# Greenland School (GS) - School Management System & Website

Institutional Website & Management System for **Greenland School**, located at Khadpathar, Renukoot, Sonbhadra, Uttar Pradesh - 231217.

- **Official School Phone Numbers**: `+91 761 700 5055, +91 761 700 5056`
- **Official School Email**: `info@greenlandschool.net`
- **School Crest / Badge**: `GS`

---

## 🚀 How to Run the Website (Instant 1-Click Launch)

Because Python 3 is already installed on your system, you can launch the website immediately without configuring PHP, Composer, or MySQL!

### Option A: Double-Click
Double-click the **`start_website.bat`** file in the project folder.

### Option B: Command Line (PowerShell / CMD)
Run the following command in the workspace directory:
```powershell
python run_website.py
```

Your default web browser will automatically open:
- **Public School Website**: `http://localhost:5000`
- **SMS Portal Login**: `http://localhost:5000#login`
- **Management Portal**: `http://localhost:5000#portal`

---

## 🔐 Dedicated Portal Authentication Gate & Role Credentials

Each role has a distinct, unique **User ID (Username)** and **Password** to log in separately:

| Role | Role Title | Unique User ID (Username) | Unique Password | Registered Email |
| :--- | :--- | :--- | :--- | :--- |
| 👑 **Super Admin** | Master Administrator | `superadmin` | `SuperAdmin@2026` | `superadmin@greenlandschool.net` |
| 🛡️ **Admin** | Administrator | `admin_kora` | `AdminPass#2026` | `admin@greenlandschool.net` |
| 👨‍🏫 **Teacher** | Senior Teacher | `teacher_chike` | `Teacher#Chike26` | `teacher.chike@greenlandschool.net` |
| 🎓 **Student** | Student Profile | `student_alex` | `Student#Alex2026` | `student.alex@greenlandschool.net` |
| 👨‍👩‍👧 **Parent** | Guardian / Parent | `parent_kaba` | `Parent#Kaba2026` | `parent.kaba@greenlandschool.net` |
| 💰 **Accountant** | Bursar & Accountant | `accountant_jude` | `Accountant#Jude26` | `bursar@greenlandschool.net` |
| 📚 **Librarian** | Head Librarian | `librarian_rose` | `Librarian#Rose26` | `library@greenlandschool.net` |

> [!NOTE]
> In compliance with strict institutional security rules, user credentials and passwords are **never displayed on the login page**. Users must type their User ID and Password.

---

## 🔑 Forgot Password Option & Self-Service Account Recovery

The portal login page features a dedicated **"Forgot Password?"** link:
1. On the login screen (`http://localhost:5000#login`), click **"🔑 Forgot Password?"**.
2. **Step 1 - Account Verification**: Enter your registered User ID (e.g. `superadmin`, `teacher_chike`, `student_alex`) or your registered email address (e.g. `teacher.chike@greenlandschool.net`).
3. Click **"🔍 Verify Account Identity"**. The system checks the SQLite database and confirms your identity.
4. **Step 2 - Reset Password**: Type your new password and confirm it (or click **"🎲 Auto"** to generate a secure password).
5. Click **"💾 Save New Password & Proceed"**.
6. Your new password is saved directly to the database and the login screen will auto-populate with your User ID, allowing you to log in immediately!

---

## 👑 Super Admin Right to Change Any User's ID and Password

The **Super Admin** account (`superadmin`) possesses full master rights to manage and override every account in the school:

1. Log in with User ID: `superadmin` and Password: `SuperAdmin@2026`.
2. In the sidebar menu, click **"🔑 Manage Users & Passwords"**.
3. A complete master ledger of all registered accounts (Teachers, Students, Admins, Parents, Accountants, Librarians) is displayed:
   - Full Name & Avatar
   - System Role
   - Unique User ID
   - Current Password (with an 👁️ eye toggle to view)
   - Email & Phone
4. Click the **"✏️ Change ID & Pass"** button on any user:
   - Edit the **User ID / Username** to any identifier.
   - Edit the **Password** to any new secret (or click **"🎲 Generate Password"** for an automatic strong password).
   - Update full name, email, or role if needed.
   - Click **"💾 Save Credentials"**.
5. The SQLite database updates in real-time.
6. The user can now log in using the new User ID and Password!

---

## 📋 Clean Database State & Student Intake

- **All previous student records have been cleared from the database**: The `students`, `marks`, `attendance`, and `payments` tables start completely empty (`0` records).
- **Admitting New Students**:
  1. Log in as **Super Admin** or **Admin**.
  2. Navigate to **"Student Directory"** in the sidebar.
  3. Click **"➕ Admit Student"**.
  4. Fill in the student's name, class arm, date of birth, blood group, and guardian details.
  5. The student is instantly enrolled with a custom admission number (`GS/2026/...`) and assigned a dedicated student portal login (`std_...`).
  6. The newly admitted student will immediately be available in attendance roll calls, continuous assessment grading sheets, and bursary payment invoices!

---

## 🌟 Other School System Features

- **Institutional Website**: Full homepage, about section, curriculum pathways (Nursery, Primary, JSS, SSS), campus facilities gallery, online admission inquiry form, noticeboard, and contact forms.
- **Official Printable Marksheet**: Official terminal report sheets with Greenland School crest, watermark, subject continuous assessment (CA) + exam scores, grading key (A-F), psychomotor skills assessment, principal remarks, and 1-click **Print / Save PDF**.
- **Attendance Register**: Class roll call with 1-click "Mark All Present".
- **Bursary & Payments**: Fee invoice tracking, payment recording in Rupees (₹), and official printable receipts.
- **Timetable & Library**: Weekly lecture schedule and book catalog inventory.
