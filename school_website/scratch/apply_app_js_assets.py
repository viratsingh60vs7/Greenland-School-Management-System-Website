import sys

with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

# 1. Update ROLE_ALLOWED_TABS
old_sa_tabs = "'super_admin': ['dashboard', 'users', 'credentials', 'teachers', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'lab_manager', 'lab_complaints', 'notices', 'settings'],"
new_sa_tabs = "'super_admin': ['dashboard', 'users', 'credentials', 'asset_management', 'teachers', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'lab_manager', 'lab_complaints', 'notices', 'settings'],"

old_it_tabs = "'it_admin': ['dashboard', 'users', 'credentials', 'lab_manager', 'lab_complaints', 'notices']"
new_it_tabs = "'it_admin': ['dashboard', 'users', 'credentials', 'asset_management', 'lab_manager', 'lab_complaints', 'notices']"

old_admin_tabs = "'admin': ['dashboard', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'lab_manager', 'lab_complaints', 'notices'],"
new_admin_tabs = "'admin': ['dashboard', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'lab_manager', 'lab_complaints', 'asset_management', 'notices'],"

if old_sa_tabs in app_js:
    app_js = app_js.replace(old_sa_tabs, new_sa_tabs, 1)
    print("✓ Added asset_management to super_admin in ROLE_ALLOWED_TABS")
if old_it_tabs in app_js:
    app_js = app_js.replace(old_it_tabs, new_it_tabs, 1)
    print("✓ Added asset_management to it_admin in ROLE_ALLOWED_TABS")
if old_admin_tabs in app_js:
    app_js = app_js.replace(old_admin_tabs, new_admin_tabs, 1)
    print("✓ Added asset_management to admin in ROLE_ALLOWED_TABS")

# 2. Add showTab case
show_tab_marker = '''        case 'lab_manager':
            if (['it_admin', 'super_admin', 'admin'].includes(currentRole)) {
                renderLabManagerTab();
            } else {
                renderDashboardTab();
            }
            break;'''

show_tab_code = '''        case 'asset_management':
            if (['it_admin', 'super_admin', 'admin'].includes(currentRole)) {
                renderAssetManagementTab();
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
            break;'''

if show_tab_marker in app_js and "case 'asset_management':" not in app_js:
    app_js = app_js.replace(show_tab_marker, show_tab_code, 1)
    print("✓ Added case 'asset_management' to showTab in app.js")

# 3. Add Asset Management Cards & Quick Action to renderITAdminDashboard
old_it_dash_header = '''    try {
        const compData = await fetch('/api/lab/computers').then(r => r.json());
        const compSummary = compData.summary || { total: 0, working: 0, faulty: 0, in_repair: 0 };
        const complaintsData = await fetch('/api/lab/complaints').then(r => r.json());
        const complaints = complaintsData.complaints || [];
        const pendingComplaints = complaints.filter(c => c.status === 'Pending' || c.status === 'Assigned');'''

new_it_dash_header = '''    try {
        const compData = await fetch('/api/lab/computers').then(r => r.json());
        const compSummary = compData.summary || { total: 0, working: 0, faulty: 0, in_repair: 0 };
        const complaintsData = await fetch('/api/lab/complaints').then(r => r.json());
        const complaints = complaintsData.complaints || [];
        const pendingComplaints = complaints.filter(c => c.status === 'Pending' || c.status === 'Assigned');
        
        let assetAnalytics = { metrics: { total_assets: 0, total_allocated: 0, total_on_rent: 0, total_in_service: 0 }, due_payments: [], expiring_warranties: [] };
        try {
            assetAnalytics = await fetch('/api/it_assets/analytics').then(r => r.json());
        } catch(e) {}'''

if old_it_dash_header in app_js:
    app_js = app_js.replace(old_it_dash_header, new_it_dash_header, 1)
    print("✓ Added asset analytics fetch to renderITAdminDashboard")

# Add asset action button in Quick IT Actions of renderITAdminDashboard
old_it_quick_btns = '''                        <button class="btn btn-secondary" onclick="showTab('lab_manager')" style="text-align:left; display:flex; align-items:center; gap:10px;">
                            <span>🖥️</span> Explore Computer Lab Grid
                        </button>'''

new_it_quick_btns = '''                        <button class="btn btn-primary" onclick="showTab('asset_management')" style="text-align:left; display:flex; align-items:center; gap:10px; background:linear-gradient(135deg, #0284c7, #1e3a8a); color:white; font-weight:700;">
                            <span>💻</span> Laptop & PC Asset Manager (Full System)
                        </button>
                        <button class="btn btn-secondary" onclick="showTab('lab_manager')" style="text-align:left; display:flex; align-items:center; gap:10px;">
                            <span>🖥️</span> Explore Computer Lab Grid
                        </button>'''

if old_it_quick_btns in app_js:
    app_js = app_js.replace(old_it_quick_btns, new_it_quick_btns, 1)
    print("✓ Added Laptop & PC Asset Manager button to IT Admin Dashboard Quick Actions")

with open('school_website/js/app.js', 'w', encoding='utf-8') as f:
    f.write(app_js)

print("Navigation wiring updated in app.js!")
