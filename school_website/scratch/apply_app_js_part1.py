# Helper script to update app.js cleanly
import re

with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update ROLE_ALLOWED_TABS
old_tabs = """const ROLE_ALLOWED_TABS = {
    'super_admin': ['dashboard', 'users', 'teachers', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'notices', 'settings'],
    'admin': ['dashboard', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'notices'],
    'teacher': ['dashboard', 'attendance', 'marks', 'timetable', 'leaves', 'payroll', 'library', 'notices'],
    'student': ['dashboard', 'marksheet', 'timetable', 'payments', 'library', 'notices'],
    'parent': ['dashboard', 'marksheet', 'timetable', 'attendance', 'payments', 'notices'],
    'accountant': ['dashboard', 'payments', 'leaves', 'payroll', 'students', 'notices'],
    'librarian': ['dashboard', 'library', 'notices']
};"""

new_tabs = """const ROLE_ALLOWED_TABS = {
    'super_admin': ['dashboard', 'users', 'teachers', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'lab_manager', 'lab_complaints', 'notices', 'settings'],
    'admin': ['dashboard', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'lab_manager', 'lab_complaints', 'notices'],
    'teacher': ['dashboard', 'attendance', 'marks', 'timetable', 'leaves', 'payroll', 'library', 'lab_complaints', 'notices'],
    'student': ['dashboard', 'marksheet', 'timetable', 'payments', 'library', 'notices'],
    'parent': ['dashboard', 'marksheet', 'timetable', 'attendance', 'payments', 'notices'],
    'accountant': ['dashboard', 'payments', 'leaves', 'payroll', 'students', 'notices'],
    'librarian': ['dashboard', 'library', 'notices'],
    'it_admin': ['dashboard', 'lab_manager', 'lab_complaints', 'notices']
};"""

code = code.replace(old_tabs, new_tabs)

# 2. Add it_admin to UNIQUE_ROLE_ACCOUNTS
old_unique_acc = """    {
        roleKey: 'librarian',
        roleTitle: 'Librarian',
        name: 'Librarian Rose Davies',
        username: 'GS_librarian',
        password: 'Greenland@2026',
        email: 'library@greenlandschool.net',
        badgeClass: 'role-librarian',
        icon: '📚',
        photo: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150',
        desc: 'Books catalogue, inventory management & issue requests'
    }"""

new_unique_acc = """    {
        roleKey: 'it_admin',
        roleTitle: 'IT Support Administrator',
        name: 'IT Support Administrator',
        username: 'GS_itsupport',
        password: 'Greenland@2026',
        email: 'itsupport@greenlandschool.net',
        badgeClass: 'role-it_admin',
        icon: '💻',
        photo: 'https://images.unsplash.com/photo-1531482615713-2afd69097998?w=150',
        desc: 'Top-level IT administrative oversight, computer lab infrastructure & repair dispatch'
    },
    {
        roleKey: 'librarian',
        roleTitle: 'Librarian',
        name: 'Librarian Rose Davies',
        username: 'GS_librarian',
        password: 'Greenland@2026',
        email: 'library@greenlandschool.net',
        badgeClass: 'role-librarian',
        icon: '📚',
        photo: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150',
        desc: 'Books catalogue, inventory management & issue requests'
    }"""

code = code.replace(old_unique_acc, new_unique_acc)

# 3. Update formatRoleName
old_format = """        'super_admin': 'Super Admin',
        'admin': 'Administrator',
        'teacher': 'Teacher',
        'student': 'Student',
        'parent': 'Parent',
        'accountant': 'Accountant',
        'librarian': 'Librarian'"""

new_format = """        'super_admin': 'Super Admin',
        'admin': 'Administrator',
        'teacher': 'Teacher',
        'student': 'Student',
        'parent': 'Parent',
        'accountant': 'Accountant',
        'librarian': 'Librarian',
        'it_admin': 'IT Support Administrator'"""

code = code.replace(old_format, new_format)

# 4. Update showTab switch
old_switch = """        case 'inquiries':
            if (['admin', 'super_admin'].includes(currentRole)) {
                renderInquiriesTab();
            } else {
                renderDashboardTab();
            }
            break;"""

new_switch = """        case 'inquiries':
            if (['admin', 'super_admin'].includes(currentRole)) {
                renderInquiriesTab();
            } else {
                renderDashboardTab();
            }
            break;
        case 'lab_manager':
            if (['it_admin', 'super_admin', 'admin'].includes(currentRole)) {
                renderLabManagerTab();
            } else {
                renderDashboardTab();
            }
            break;
        case 'lab_complaints':
            if (['it_admin', 'super_admin', 'admin', 'teacher'].includes(currentRole)) {
                renderLabComplaintsTab();
            } else {
                renderDashboardTab();
            }
            break;"""

code = code.replace(old_switch, new_switch)

# 5. Update renderDashboardTab
old_dash = """async function renderDashboardTab() {
    if (currentRole === 'super_admin') {
        renderSuperAdminDashboard();
    } else if (currentRole === 'teacher') {
        renderTeacherDashboard();
    } else if (currentRole === 'student') {
        renderStudentDashboard();
    } else if (currentRole === 'parent') {
        renderParentDashboard();
    } else if (currentRole === 'accountant') {
        renderAccountantDashboard();
    } else if (currentRole === 'librarian') {
        renderLibrarianDashboard();
    } else {
        renderAdminDashboard();
    }
}"""

new_dash = """async function renderDashboardTab() {
    if (currentRole === 'super_admin') {
        renderSuperAdminDashboard();
    } else if (currentRole === 'it_admin') {
        renderITAdminDashboard();
    } else if (currentRole === 'teacher') {
        renderTeacherDashboard();
    } else if (currentRole === 'student') {
        renderStudentDashboard();
    } else if (currentRole === 'parent') {
        renderParentDashboard();
    } else if (currentRole === 'accountant') {
        renderAccountantDashboard();
    } else if (currentRole === 'librarian') {
        renderLibrarianDashboard();
    } else {
        renderAdminDashboard();
    }
}"""

code = code.replace(old_dash, new_dash)

with open('school_website/js/app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Step 1 of app.js updates applied successfully!")
