# Script to apply updates to js/app.js
with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update ROLE_ALLOWED_TABS: add 'credentials' for super_admin and it_admin
old_tabs_anchor = """const ROLE_ALLOWED_TABS = {
    'super_admin': ['dashboard', 'users', 'teachers', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'lab_manager', 'lab_complaints', 'notices', 'settings'],
    'admin': ['dashboard', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'lab_manager', 'lab_complaints', 'notices'],
    'teacher': ['dashboard', 'attendance', 'marks', 'timetable', 'leaves', 'payroll', 'library', 'lab_complaints', 'notices'],
    'student': ['dashboard', 'marksheet', 'timetable', 'payments', 'library', 'notices'],
    'parent': ['dashboard', 'marksheet', 'timetable', 'attendance', 'payments', 'notices'],
    'accountant': ['dashboard', 'payments', 'leaves', 'payroll', 'students', 'notices'],
    'librarian': ['dashboard', 'library', 'notices'],
    'it_admin': ['dashboard', 'lab_manager', 'lab_complaints', 'notices']
};"""

new_tabs_anchor = """const ROLE_ALLOWED_TABS = {
    'super_admin': ['dashboard', 'users', 'credentials', 'teachers', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'lab_manager', 'lab_complaints', 'notices', 'settings'],
    'admin': ['dashboard', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'lab_manager', 'lab_complaints', 'notices'],
    'teacher': ['dashboard', 'attendance', 'marks', 'timetable', 'leaves', 'payroll', 'library', 'lab_complaints', 'notices'],
    'student': ['dashboard', 'marksheet', 'timetable', 'payments', 'library', 'notices'],
    'parent': ['dashboard', 'marksheet', 'timetable', 'attendance', 'payments', 'notices'],
    'accountant': ['dashboard', 'payments', 'leaves', 'payroll', 'students', 'notices'],
    'librarian': ['dashboard', 'library', 'notices'],
    'it_admin': ['dashboard', 'credentials', 'lab_manager', 'lab_complaints', 'notices']
};"""

if old_tabs_anchor in code:
    code = code.replace(old_tabs_anchor, new_tabs_anchor)
    print("1. Updated ROLE_ALLOWED_TABS with 'credentials'")
else:
    print("WARNING: ROLE_ALLOWED_TABS anchor not found")

# 2. Update showTab switch to route 'credentials'
old_show_tab_case = """        case 'lab_manager':
            if (['it_admin', 'super_admin', 'admin'].includes(currentRole)) {
                renderLabManagerTab();
            } else {
                renderDashboardTab();
            }
            break;"""

new_show_tab_case = """        case 'credentials':
            if (['it_admin', 'super_admin'].includes(currentRole)) {
                renderCredentialsTab();
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
            break;"""

if old_show_tab_case in code:
    code = code.replace(old_show_tab_case, new_show_tab_case)
    print("2. Added 'credentials' routing in showTab")
else:
    print("WARNING: showTab case not found")

# 3. Update submitAdmitStudent to pass approved_by and admission_status
old_admit_payload = """    const payload = {
        name: document.getElementById('new-std-name').value,
        class_name: classVal,
        section: sectionVal,
        stream: streamVal,
        aadhaar_no: aadhaarVal,
        blood_group: document.getElementById('new-std-blood').value,
        gender: document.getElementById('new-std-gender').value,
        phone: document.getElementById('new-std-phone').value
    };"""

new_admit_payload = """    const payload = {
        name: document.getElementById('new-std-name').value,
        class_name: classVal,
        section: sectionVal,
        stream: streamVal,
        aadhaar_no: aadhaarVal,
        blood_group: document.getElementById('new-std-blood').value,
        gender: document.getElementById('new-std-gender').value,
        phone: document.getElementById('new-std-phone').value,
        approved_by: currentUser ? (currentUser.name || currentUser.username) : 'Super Admin',
        admission_status: 'Approved for New Admission'
    };"""

if old_admit_payload in code:
    code = code.replace(old_admit_payload, new_admit_payload)
    print("3. Updated submitAdmitStudent payload with admission_status and approved_by")
else:
    print("WARNING: submitAdmitStudent payload not found")

# 4. Update submitBulkExcelUpload to pass approved_by and immediately reload students data
old_bulk_fetch = """        const res = await fetch('/api/students/upload_excel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: uploadedExcelFileName,
                file_data: uploadedExcelBase64
            })
        });"""

new_bulk_fetch = """        const res = await fetch('/api/students/upload_excel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: uploadedExcelFileName,
                file_data: uploadedExcelBase64,
                approved_by: currentUser ? (currentUser.name || currentUser.username) : 'Super Admin'
            })
        });"""

if old_bulk_fetch in code:
    code = code.replace(old_bulk_fetch, new_bulk_fetch)
    print("4. Updated submitBulkExcelUpload with approved_by")
else:
    print("WARNING: submitBulkExcelUpload fetch not found")

old_bulk_refresh = """            if (currentTab === 'students') {
                renderStudentsTab();
            }
            loadInitialData();"""

new_bulk_refresh = """            const freshStudents = await fetch('/api/students').then(r => r.json());
            siteData.students = freshStudents;
            cachedStudentsList = freshStudents;
            if (currentTab === 'students') {
                renderStudentsTab();
            }
            loadInitialData();"""

if old_bulk_refresh in code:
    code = code.replace(old_bulk_refresh, new_bulk_refresh)
    print("5. Added immediate student synchronization to submitBulkExcelUpload")
else:
    print("WARNING: submitBulkExcelUpload refresh block not found")

# 5. In students table headers & rows: add Admission Status
old_std_header1 = """                                    <th>Student</th>
                                    <th>Adm No.</th>
                                    <th>Section (Arm)</th>
                                    <th>User ID</th>
                                    <th>Gender</th>
                                    <th>Guardian</th>
                                    <th>Blood Group</th>
                                    <th>Actions</th>"""

new_std_header1 = """                                    <th>Student</th>
                                    <th>Adm No.</th>
                                    <th>Section (Arm)</th>
                                    <th>User ID</th>
                                    <th>Gender</th>
                                    <th>Admission Status</th>
                                    <th>Guardian</th>
                                    <th>Blood Group</th>
                                    <th>Actions</th>"""

old_std_header2 = """                            <th>Student</th>
                            <th>Adm No.</th>
                            <th>Class & Section</th>
                            <th>User ID</th>
                            <th>Gender</th>
                            <th>Guardian</th>
                            <th>Blood Group</th>
                            <th>Actions</th>"""

new_std_header2 = """                            <th>Student</th>
                            <th>Adm No.</th>
                            <th>Class & Section</th>
                            <th>User ID</th>
                            <th>Gender</th>
                            <th>Admission Status</th>
                            <th>Guardian</th>
                            <th>Blood Group</th>
                            <th>Actions</th>"""

if old_std_header1 in code:
    code = code.replace(old_std_header1, new_std_header1)
    print("6. Added Admission Status to grouped table header")
if old_std_header2 in code:
    code = code.replace(old_std_header2, new_std_header2)
    print("7. Added Admission Status to flat table header")

old_render_row = """            <td><code>${s.username || '—'}</code></td>
            <td><span style="font-size:0.82rem; color:#475569;">${s.gender || '—'}</span></td>
            <td>
                <div style="font-size:0.83rem; font-weight:600;">${s.parent_name || 'Guardian'}</div>
                <div style="font-size:0.72rem; color:#64748b;">${s.phone || '—'}</div>
            </td>"""

new_render_row = """            <td><code>${s.username || '—'}</code></td>
            <td><span style="font-size:0.82rem; color:#475569;">${s.gender || '—'}</span></td>
            <td>
                <span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700; padding:3px 8px; border-radius:6px; font-size:0.74rem; display:inline-flex; align-items:center; gap:4px;">
                    <i class="fas fa-check-circle"></i> ${s.admission_status || 'Approved for New Admission'}
                </span>
                <div style="font-size:0.7rem; color:#64748b; margin-top:2px;">by ${s.approved_by || 'Administration'}</div>
            </td>
            <td>
                <div style="font-size:0.83rem; font-weight:600;">${s.parent_name || 'Guardian'}</div>
                <div style="font-size:0.72rem; color:#64748b;">${s.phone || '—'}</div>
            </td>"""

if old_render_row in code:
    code = code.replace(old_render_row, new_render_row)
    print("8. Added Admission Status badge to student table rows")
else:
    print("WARNING: renderSingleStudentRow anchor not found")

# 6. Append renderCredentialsTab and related credential handlers
credentials_js = """
// =====================================================================
// CREDENTIAL MANAGEMENT & OWNER EXECUTIVE APPROVAL SYSTEM
// =====================================================================
async function renderCredentialsTab() {
    if (!['it_admin', 'super_admin'].includes(currentRole)) {
        showTab('dashboard');
        return;
    }

    const isOwner = currentUser && (currentUser.username === 'Owner(Directer)' || (currentUser.name && currentUser.name.includes('Rajeev Sinha')));
    const isITAdmin = currentRole === 'it_admin';

    document.getElementById('portal-header-title').innerText = isOwner ? 'Owner Credential & User ID Executive Approval Center' : 'User ID & Password Management Desk (IT Support)';
    document.getElementById('portal-header-desc').innerText = isOwner 
        ? 'Director Authority: Review and approve/reject IT Support credential modifications and new account creations'
        : 'IT Support Administrator: Propose User ID/Password modifications and create new accounts subject to Owner approval';

    try {
        const users = await fetch('/api/users').then(r => r.json());
        siteData.users = users;

        const reqData = await fetch('/api/credentials/requests').then(r => r.json());
        const allRequests = reqData.requests || [];
        const pendingRequests = allRequests.filter(r => r.status === 'Pending Owner Approval');

        const html = `
            <!-- Policy Callout -->
            <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:16px 20px; margin-bottom:20px; color:#1e40af; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <span style="font-size:2rem;">🔐</span>
                    <div>
                        <strong style="font-size:1rem;">Strict Institutional Password & Identity Governance Policy</strong>
                        <div style="font-size:0.84rem; color:#1d4ed8; margin-top:2px; line-height:1.4;">
                            • <strong>Self-service password change is removed from everyone.</strong><br>
                            • <strong>Only IT Support Administrator</strong> can initiate User ID and Password modifications or propose new User IDs.<br>
                            • Every credential modification and new User ID creation strictly requires <strong>Executive Approval by Owner (Director) Rajeev Sinha</strong>.
                        </div>
                    </div>
                </div>
                <div>
                    <button class="btn btn-primary" style="background:#1e3a8a; font-weight:700; padding:8px 16px; display:inline-flex; align-items:center; gap:8px;" onclick="openModal('modal-it-request-create-user')">
                        <i class="fas fa-user-plus"></i> ➕ Propose New User ID
                    </button>
                </div>
            </div>

            <!-- OWNER PENDING APPROVAL QUEUE (Prominently displayed to Director) -->
            ${isOwner ? `
                <div class="card" style="margin-bottom:24px; border:2px solid #7c3aed;">
                    <div class="card-header" style="background:#faf5ff; justify-content:space-between; align-items:center;">
                        <div>
                            <span class="card-title" style="color:#6b21a8;"><i class="fas fa-crown"></i> 👑 Director Executive Approval Queue (${pendingRequests.length} Pending)</span>
                            <p style="font-size:0.78rem; color:#7e22ce; margin-top:2px;">Pending credential updates and user creations submitted by IT Support Administrator awaiting your authorization</p>
                        </div>
                        <span class="badge" style="background:${pendingRequests.length > 0 ? '#ef4444' : '#10b981'}; color:white; font-weight:700; padding:5px 12px; border-radius:12px;">
                            ${pendingRequests.length > 0 ? `${pendingRequests.length} Action(s) Required` : 'Queue Clear'}
                        </span>
                    </div>
                    <div class="card-body" style="padding:0; overflow-x:auto;">
                        ${pendingRequests.length === 0 ? `
                            <div style="text-align:center; padding:30px; color:#10b981;">
                                <div style="font-size:2rem; margin-bottom:6px;">✓</div>
                                <strong>No Pending Credential Requests</strong>
                                <p style="font-size:0.8rem; color:#64748b; margin-top:4px;">All User ID and password requests submitted by IT Support have been reviewed.</p>
                            </div>
                        ` : `
                            <table class="data-table" style="font-size:0.83rem;">
                                <thead>
                                    <tr>
                                        <th>Request #</th>
                                        <th>Request Type</th>
                                        <th>Target Identity</th>
                                        <th>Proposed User ID</th>
                                        <th>Proposed Password</th>
                                        <th>Requested By</th>
                                        <th>Reason / Justification</th>
                                        <th>Executive Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${pendingRequests.map(r => `
                                        <tr>
                                            <td><code>REQ-${r.id}</code></td>
                                            <td>
                                                <span class="badge" style="background:${r.request_type === 'create_user' ? '#f0fdf4; color:#15803d;' : '#eff6ff; color:#1e40af;'} font-weight:700;">
                                                    ${r.request_type === 'create_user' ? '➕ New User Creation' : '✏️ Credential Change'}
                                                </span>
                                            </td>
                                            <td>
                                                <strong>${r.proposed_name || r.current_name_db || r.target_username || 'Role Account'}</strong>
                                                <div style="font-size:0.72rem; color:#64748b;">Role: <code>${r.proposed_role || r.current_role_db}</code></div>
                                            </td>
                                            <td><code style="font-weight:700; color:#1e3a8a;">${r.proposed_username}</code></td>
                                            <td><code style="font-weight:700; color:#b91c1c;">${r.proposed_password}</code></td>
                                            <td>
                                                <div style="font-weight:700;">${r.requested_by_name || 'IT Support Admin'}</div>
                                                <div style="font-size:0.72rem; color:#64748b;">${r.created_at || 'Recently'}</div>
                                            </td>
                                            <td style="max-width:200px;"><span style="font-size:0.78rem; color:#334155;">${r.reason || '—'}</span></td>
                                            <td>
                                                <div style="display:flex; gap:6px;">
                                                    <button class="btn btn-success btn-sm" style="font-size:0.74rem; padding:4px 10px; background:#16a34a; font-weight:700;" onclick="approveCredentialRequest(${r.id})">
                                                        ✅ Approve & Apply
                                                    </button>
                                                    <button class="btn btn-danger btn-sm" style="font-size:0.74rem; padding:4px 8px; background:#dc2626;" onclick="rejectCredentialRequest(${r.id})">
                                                        ❌ Reject
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        `}
                    </div>
                </div>
            ` : ''}

            <!-- ALL SYSTEM ACCOUNTS DIRECTORY -->
            <div class="card" style="margin-bottom:24px;">
                <div class="card-header" style="justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                    <div>
                        <span class="card-title">👥 All System User Accounts (${users.length})</span>
                        <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Select any user to propose a User ID or Password modification</p>
                    </div>
                    <div>
                        <input type="text" id="cred-user-search" placeholder="Search user ID, name, role..." class="form-control" style="padding:6px 12px; width:260px;" onkeyup="filterCredentialsTable()">
                    </div>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    <table class="data-table" id="credentials-table" style="font-size:0.83rem;">
                        <thead>
                            <tr>
                                <th>User / Name</th>
                                <th>Role</th>
                                <th>Current User ID</th>
                                <th>Current Password</th>
                                <th>Email</th>
                                <th>Phone</th>
                                <th>Security Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${users.map(u => `
                                <tr>
                                    <td style="display:flex; align-items:center; gap:10px;">
                                        <img src="${u.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150'}" style="width:34px; height:34px; border-radius:50%; object-fit:cover;">
                                        <div>
                                            <div style="font-weight:700; color:#0f172a;">${u.name || '(Unassigned Role ID)'}</div>
                                            <div style="font-size:0.72rem; color:#64748b;">ID #${u.id}</div>
                                        </div>
                                    </td>
                                    <td>
                                        <span class="cred-role-badge role-${u.user_type}">
                                            ${formatRoleName(u.user_type)}
                                        </span>
                                    </td>
                                    <td>
                                        <span class="pwd-badge" style="color:#1e40af; font-weight:700; font-family:monospace;">${u.username}</span>
                                    </td>
                                    <td>
                                        <div style="display:flex; align-items:center; gap:6px;">
                                            <span class="pwd-badge" id="cred-pwd-${u.id}">••••••••</span>
                                            <button type="button" class="btn-icon" onclick="toggleTablePassword('cred-pwd-${u.id}', '${u.password}', true)" title="Show / Hide Password">
                                                👁️
                                            </button>
                                        </div>
                                    </td>
                                    <td><span style="font-size:0.8rem; color:#475569;">${u.email || '—'}</span></td>
                                    <td><span style="font-size:0.8rem; color:#475569;">${u.phone || '—'}</span></td>
                                    <td>
                                        <button class="btn btn-primary btn-sm" style="font-size:0.73rem; padding:4px 10px; font-weight:700;" onclick="openITSupportChangeCredsModal(${u.id})">
                                            ✏️ Modify ID / Password
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- CREDENTIAL REQUESTS AUDIT & STATUS TRACKER -->
            <div class="card">
                <div class="card-header" style="justify-content:space-between; align-items:center;">
                    <div>
                        <span class="card-title">📜 Credential Modification Requests Audit Trail (${allRequests.length})</span>
                        <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Complete record of all User ID and Password modifications and Owner approvals</p>
                    </div>
                    <button class="btn btn-outline btn-sm" onclick="renderCredentialsTab()">🔄 Refresh Log</button>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    ${allRequests.length === 0 ? `
                        <div style="text-align:center; padding:30px; color:#64748b;">
                            No credential modification requests on record yet.
                        </div>
                    ` : `
                        <table class="data-table" style="font-size:0.82rem;">
                            <thead>
                                <tr>
                                    <th>Request #</th>
                                    <th>Type</th>
                                    <th>Target / Identity</th>
                                    <th>Proposed User ID</th>
                                    <th>Requested By</th>
                                    <th>Status</th>
                                    <th>Executive Approver</th>
                                    <th>Date / Time</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${allRequests.map(r => {
                                    let statusBadge = `<span class="badge" style="background:#fef3c7; color:#d97706; font-weight:700;">⏳ Pending Owner Approval</span>`;
                                    if (r.status === 'Approved') {
                                        statusBadge = `<span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700;">✅ Approved & Applied</span>`;
                                    } else if (r.status === 'Rejected') {
                                        statusBadge = `<span class="badge" style="background:#fee2e2; color:#dc2626; font-weight:700;">❌ Rejected</span>`;
                                    }

                                    return `
                                        <tr>
                                            <td><code>REQ-${r.id}</code></td>
                                            <td><strong>${r.request_type === 'create_user' ? '➕ Create User' : '✏️ Change Credentials'}</strong></td>
                                            <td><strong>${r.proposed_name || r.current_name_db || r.target_username}</strong></td>
                                            <td><code style="font-weight:700; color:#1e3a8a;">${r.proposed_username}</code></td>
                                            <td>${r.requested_by_name || 'IT Support'}</td>
                                            <td>${statusBadge}</td>
                                            <td>${r.approved_by || '<span style="color:#94a3b8; font-style:italic;">Awaiting Owner</span>'}</td>
                                            <td><span style="font-size:0.74rem; color:#64748b;">${r.created_at || 'Recently'}</span></td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    `}
                </div>
            </div>
        `;

        document.getElementById('portal-tab-content').innerHTML = html;
    } catch (err) {
        document.getElementById('portal-tab-content').innerHTML = `<div style="padding:20px; color:red;">Error loading Credentials tab: ${err.message}</div>`;
    }
}

function filterCredentialsTable() {
    const q = document.getElementById('cred-user-search').value.toLowerCase();
    const rows = document.querySelectorAll('#credentials-table tbody tr');
    rows.forEach(r => {
        r.style.display = r.innerText.toLowerCase().includes(q) ? '' : 'none';
    });
}

function openITSupportChangeCredsModal(userId) {
    const u = (siteData.users || []).find(x => x.id === userId);
    if (!u) {
        alert('User account not found.');
        return;
    }
    document.getElementById('it-cred-user-id').value = u.id;
    document.getElementById('it-cred-new-username').value = u.username;
    document.getElementById('it-cred-new-password').value = '';
    document.getElementById('it-cred-reason').value = '';

    document.getElementById('it-cred-target-info').innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <strong>${u.name || '(Unassigned Role ID)'}</strong> (ID #${u.id})
                <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">Role: <code>${u.user_type}</code> | Current User ID: <code style="color:#1e40af; font-weight:700;">${u.username}</code></div>
            </div>
            <span class="cred-role-badge role-${u.user_type}">${formatRoleName(u.user_type)}</span>
        </div>
    `;

    openModal('modal-it-request-change-creds');
}

async function submitITSupportChangeCreds(e) {
    e.preventDefault();
    const userId = parseInt(document.getElementById('it-cred-user-id').value);
    const newUsername = document.getElementById('it-cred-new-username').value.trim();
    const newPassword = document.getElementById('it-cred-new-password').value.trim();
    const reason = document.getElementById('it-cred-reason').value.trim();

    try {
        const res = await fetch('/api/credentials/request_change', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                username: newUsername,
                password: newPassword,
                reason: reason,
                requested_by_id: currentUser ? currentUser.id : null,
                requested_by_name: currentUser ? (currentUser.name || currentUser.username) : 'IT Support Administrator',
                requested_by_username: currentUser ? currentUser.username : 'GS_itsupport',
                role: currentRole
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-it-request-change-creds');
            e.target.reset();
            renderCredentialsTab();
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    } catch (err) {
        alert('Failed to submit credential change: ' + err.message);
    }
}

function handleITCreateUserNameChange(val) {
    const sel = document.getElementById('it-create-gender');
    const hint = document.getElementById('it-create-gender-hint');
    if (!val || !val.trim()) {
        if (sel) {
            sel.disabled = true;
            sel.value = '';
        }
        if (hint) hint.innerHTML = '🔒 Disabled: Role ID has no assigned person name (no gender shown).';
    } else {
        if (sel) sel.disabled = false;
        if (hint) hint.innerHTML = '✅ Enabled: Assigned person gender can now be set (Male / Female).';
    }
}

async function submitITSupportCreateUser(e) {
    e.preventDefault();
    const name = document.getElementById('it-create-name').value.trim();
    const role = document.getElementById('it-create-role').value;
    const genderSel = document.getElementById('it-create-gender');
    const gender = name && genderSel ? genderSel.value : null;
    const username = document.getElementById('it-create-username').value.trim();
    const password = document.getElementById('it-create-password').value.trim();
    const email = document.getElementById('it-create-email').value.trim();
    const phone = document.getElementById('it-create-phone').value.trim();
    const reason = document.getElementById('it-create-reason').value.trim();

    try {
        const res = await fetch('/api/credentials/request_create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                user_type: role,
                gender: gender,
                username: username,
                password: password,
                email: email,
                phone: phone,
                reason: reason,
                requested_by_id: currentUser ? currentUser.id : null,
                requested_by_name: currentUser ? (currentUser.name || currentUser.username) : 'IT Support Administrator',
                requested_by_username: currentUser ? currentUser.username : 'GS_itsupport'
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-it-request-create-user');
            e.target.reset();
            renderCredentialsTab();
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    } catch (err) {
        alert('Failed to submit user creation request: ' + err.message);
    }
}

async function approveCredentialRequest(requestId) {
    const approverName = currentUser ? (currentUser.name || 'Owner (Director) Rajeev Sinha') : 'Owner (Director) Rajeev Sinha';
    try {
        const res = await fetch('/api/credentials/approve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                request_id: requestId,
                name: approverName,
                username: currentUser ? currentUser.username : 'Owner(Directer)'
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`👑 ${data.message}`);
            renderCredentialsTab();
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    } catch (err) {
        alert('Failed to approve request: ' + err.message);
    }
}

async function rejectCredentialRequest(requestId) {
    const reason = prompt('Please enter reason for rejecting this credential request:', 'Declined by Owner (Director) Rajeev Sinha');
    if (!reason) return;

    try {
        const res = await fetch('/api/credentials/reject', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                request_id: requestId,
                rejection_reason: reason,
                name: currentUser ? (currentUser.name || 'Owner (Director) Rajeev Sinha') : 'Owner (Director) Rajeev Sinha'
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✓ ${data.message}`);
            renderCredentialsTab();
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    } catch (err) {
        alert('Failed to reject request: ' + err.message);
    }
}

async function approveStudentAdmission(studentId) {
    const approver = currentUser ? (currentUser.name || currentUser.username) : 'Super Admin';
    try {
        const res = await fetch('/api/students/approve_admission', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_id: studentId,
                approved_by: approver
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            renderStudentsTab();
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    } catch (err) {
        alert('Failed to approve admission: ' + err.message);
    }
}
"""

code = code + "\n" + credentials_js

with open('school_website/js/app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("app.js updated successfully!")
