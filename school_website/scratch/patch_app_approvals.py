with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update ROLE_ALLOWED_TABS
old_role_tabs = """ROLE_ALLOWED_TABS = {
    'super_admin': ['dashboard', 'users', 'credentials', 'asset_management', 'teachers', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'lab_manager', 'lab_complaints', 'notices', 'settings'],
    'admin': ['dashboard', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'lab_manager', 'lab_complaints', 'asset_management', 'notices'],
    'teacher': ['dashboard', 'attendance', 'marks', 'timetable', 'leaves', 'payroll', 'library', 'lab_complaints', 'notices'],
    'student': ['dashboard', 'marksheet', 'timetable', 'payments', 'library', 'notices'],
    'parent': ['dashboard', 'marksheet', 'timetable', 'attendance', 'payments', 'notices'],
    'accountant': ['dashboard', 'payments', 'leaves', 'payroll', 'students', 'notices'],
    'librarian': ['dashboard', 'library', 'notices'],
    'it_admin': ['dashboard', 'users', 'credentials', 'asset_management', 'lab_manager', 'lab_complaints', 'notices']
};"""

new_role_tabs = """// IT Access Helper: Checks if current user is IT Support (GS_itsupport or any future IT User ID)
function isITUser(user) {
    if (!user) return false;
    const role = (user.user_type || '').toLowerCase();
    const uname = (user.username || '').toLowerCase();
    return role === 'it_admin' || role === 'it_support' || role.includes('it_') || uname.startsWith('gs_it') || uname.startsWith('it_') || uname.includes('itsupport');
}

// STRICT REQUIREMENT: Laptop & PC Asset Manager is exclusively used by ONLY IT Support (or any future IT User ID)
ROLE_ALLOWED_TABS = {
    'super_admin': ['dashboard', 'users', 'credentials', 'teachers', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'lab_manager', 'lab_complaints', 'notices', 'settings'],
    'admin': ['dashboard', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'lab_manager', 'lab_complaints', 'notices'],
    'teacher': ['dashboard', 'attendance', 'marks', 'timetable', 'leaves', 'payroll', 'library', 'lab_complaints', 'notices'],
    'student': ['dashboard', 'marksheet', 'timetable', 'payments', 'library', 'notices'],
    'parent': ['dashboard', 'marksheet', 'timetable', 'attendance', 'payments', 'notices'],
    'accountant': ['dashboard', 'payments', 'leaves', 'payroll', 'students', 'notices'],
    'librarian': ['dashboard', 'library', 'notices'],
    'it_admin': ['dashboard', 'users', 'credentials', 'asset_management', 'lab_manager', 'lab_complaints', 'notices']
};"""

assert old_role_tabs in code, "old_role_tabs not found in app.js"
code = code.replace(old_role_tabs, new_role_tabs, 1)

# 2. Update updateSidebarForRole to strictly show asset_management for IT Support only
old_sidebar_func = """function updateSidebarForRole(role) {
    const allowed = ROLE_ALLOWED_TABS[role] || ROLE_ALLOWED_TABS['super_admin'];

    document.querySelectorAll('.sidebar-nav li').forEach(li => {
        const tab = li.dataset.tab;
        if (tab) {
            li.style.display = allowed.includes(tab) ? 'block' : 'none';
        }
    });
}"""

new_sidebar_func = """function updateSidebarForRole(role) {
    const allowed = ROLE_ALLOWED_TABS[role] || ROLE_ALLOWED_TABS['super_admin'];

    document.querySelectorAll('.sidebar-nav li').forEach(li => {
        const tab = li.dataset.tab;
        if (tab) {
            let isPermitted = allowed.includes(tab);
            // STRICT REQUIREMENT: Laptop & PC Asset Manager is accessible by ONLY IT Support (current and future IT User IDs)
            if (tab === 'asset_management') {
                isPermitted = isITUser(currentUser);
            }
            li.style.display = isPermitted ? 'block' : 'none';
        }
    });
}"""

assert old_sidebar_func in code, "old_sidebar_func not found in app.js"
code = code.replace(old_sidebar_func, new_sidebar_func, 1)

# 3. Update showTab to strictly enforce IT Support access for asset_management
old_show_tab_check = """    const allowed = ROLE_ALLOWED_TABS[currentRole] || [];
    // Only allow tab if permitted for this role (or if super_admin/admin is viewing an inspected marksheet)
    if (!allowed.includes(tabName) && !(tabName === 'marksheet' && (currentRole === 'super_admin' || currentRole === 'admin'))) {
        tabName = 'dashboard';
    }"""

new_show_tab_check = """    // STRICT REQUIREMENT: Laptop & PC Asset Manager can ONLY be used by IT Support
    if (tabName === 'asset_management') {
        if (!isITUser(currentUser)) {
            alert("🔒 Access Restricted: The Laptop & PC Asset Management System is exclusively reserved for IT Support Administrator accounts (and any future IT User IDs).");
            tabName = 'dashboard';
        }
    }

    const allowed = ROLE_ALLOWED_TABS[currentRole] || [];
    if (!allowed.includes(tabName) && !(tabName === 'marksheet' && (currentRole === 'super_admin' || currentRole === 'admin')) && !(tabName === 'asset_management' && isITUser(currentUser))) {
        tabName = 'dashboard';
    }"""

assert old_show_tab_check in code, "old_show_tab_check not found in app.js"
code = code.replace(old_show_tab_check, new_show_tab_check, 1)

# 4. Update handleHashNavigation to support #app
old_hash_nav = """function handleHashNavigation() {
    const hash = window.location.hash;
    if (hash === '#portal') {"""

new_hash_nav = """function handleHashNavigation() {
    const hash = window.location.hash;
    if (hash === '#app' || hash === '#campus-app') {
        openCampusApp();
    } else if (hash === '#portal') {"""

assert old_hash_nav in code, "old_hash_nav not found in app.js"
code = code.replace(old_hash_nav, new_hash_nav, 1)

# 5. In renderSuperAdminDashboard, add the 👑 Director Approval Desk (Requests from Teachers & IT Team)
old_super_dash = """    document.getElementById('portal-header-title').innerText = 'Super Admin Master Dashboard';
    document.getElementById('portal-header-desc').innerText = 'Institutional Oversight, User Credentials & System Administration';

    const html = `
        <div class="metrics-row">"""

new_super_dash = """    document.getElementById('portal-header-title').innerText = 'Director Executive Master Dashboard';
    document.getElementById('portal-header-desc').innerText = 'Director Rajeev Sinha: Institutional Governance, Teacher & IT Request Approvals Center';

    // Fetch unified pending requests from Teachers and IT Team
    let pendingData = { total_pending: 0, requests: [] };
    try {
        pendingData = await fetch('/api/director/pending_requests').then(r => r.json());
    } catch (e) {
        console.error("Failed to load director pending requests:", e);
    }

    const approvalDeskHtml = `
        <!-- DIRECTOR EXCLUSIVE APPROVAL DESK (TEACHER & IT TEAM REQUESTS) -->
        <div class="card" style="margin-bottom:22px; border:2px solid #3b82f6; box-shadow:0 8px 24px rgba(37,99,235,0.12);">
            <div class="card-header" style="background:linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); color:white; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:1.6rem;">👑</span>
                    <div>
                        <div style="font-size:1.05rem; font-weight:800; letter-spacing:0.3px;">Director Exclusive Approvals Desk</div>
                        <div style="font-size:0.75rem; color:#bfdbfe;">
                            Policy Enforcement: Only Director Rajeev Sinha has authority to approve requests created by Teachers or IT Team.
                        </div>
                    </div>
                </div>
                <div>
                    <span style="font-size:0.78rem; font-weight:800; background:${pendingData.total_pending > 0 ? '#ef4444' : '#10b981'}; color:white; padding:4px 12px; border-radius:50px;">
                        ${pendingData.total_pending > 0 ? `🔔 ${pendingData.total_pending} Pending Approvals` : '✅ All Requests Cleared'}
                    </span>
                </div>
            </div>
            <div class="card-body" style="padding:16px;">
                ${pendingData.requests && pendingData.requests.length > 0 ? `
                    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(310px, 1fr)); gap:12px;">
                        ${pendingData.requests.map(req => {
                            let originBadge = req.origin.includes('Teacher') ? 
                                '<span class="badge" style="background:#eff6ff; color:#1d4ed8; font-weight:700;">👨‍🏫 Teacher Request</span>' :
                                '<span class="badge" style="background:#fef3c7; color:#b45309; font-weight:700;">💻 IT Team Request</span>';
                            
                            let reqTypeKey = 'it_asset';
                            if (req.request_type.includes('Leave')) reqTypeKey = 'teacher_leave';
                            else if (req.request_type.includes('Lab')) reqTypeKey = 'lab_complaint';
                            else if (req.request_type.includes('Credential')) reqTypeKey = 'it_credential';

                            return `
                                <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:10px; padding:14px; display:flex; flex-direction:column; justify-content:space-between; gap:10px;">
                                    <div>
                                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                                            ${originBadge}
                                            <span style="font-size:0.72rem; color:#64748b; font-family:monospace;">${req.created_at || 'Today'}</span>
                                        </div>
                                        <div style="font-weight:700; color:#0f172a; font-size:0.9rem;">${req.title}</div>
                                        <div style="font-size:0.78rem; color:#475569; margin-top:3px;">${req.description || 'No description provided'}</div>
                                        <div style="font-size:0.74rem; color:#2563eb; margin-top:4px; font-weight:600;">${req.details}</div>
                                        <div style="font-size:0.72rem; color:#64748b; margin-top:3px;">Initiated by: <strong>${req.creator_name}</strong> (${req.creator_username})</div>
                                    </div>
                                    <div style="display:flex; gap:8px; border-top:1px dashed #cbd5e1; padding-top:10px; justify-content:flex-end;">
                                        <button class="btn btn-sm" style="background:#15803d; color:white; font-size:0.76rem; font-weight:700; border:none; padding:5px 12px; cursor:pointer;" onclick="handleDirectorApprove('${reqTypeKey}', ${req.id}, 'approve')">
                                            ✅ Approve Request
                                        </button>
                                        <button class="btn btn-sm" style="background:#dc2626; color:white; font-size:0.76rem; font-weight:700; border:none; padding:5px 10px; cursor:pointer;" onclick="handleDirectorApprove('${reqTypeKey}', ${req.id}, 'reject')">
                                            ❌ Reject
                                        </button>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                ` : `
                    <div style="text-align:center; padding:24px; color:#64748b;">
                        <span style="font-size:2.4rem;">🎉</span>
                        <div style="font-weight:700; color:#1e293b; margin-top:8px;">No Pending Requests from Teachers or IT Team</div>
                        <div style="font-size:0.8rem; color:#94a3b8; margin-top:2px;">All faculty leaves, lab repair authorizations, and IT requests are currently up to date.</div>
                    </div>
                `}
            </div>
        </div>
    `;

    const html = `
        ${approvalDeskHtml}
        <div class="metrics-row">"""

assert old_super_dash in code, "old_super_dash not found in app.js"
code = code.replace(old_super_dash, new_super_dash, 1)

with open('school_website/js/app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ app.js successfully patched with IT restrictions and Director Approval Desk!")
