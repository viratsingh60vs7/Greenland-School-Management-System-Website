# Python script to update app.js with Users Tab, Lab Management, and Payroll features
import sys

with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update renderUsersTab() to include Gender column, Clean Test Data button, Seed Faculty button, and Assign Role button
old_users_tab = """async function renderUsersTab() {
    if (currentRole !== 'super_admin') {
        showTab('dashboard');
        return;
    }

    document.getElementById('portal-header-title').innerText = 'User Accounts & Credentials Control Center';
    document.getElementById('portal-header-desc').innerText = 'Super Admin Master Rights: You can edit or change any user\\'s unique User ID, email, and password.';

    try {
        const users = await fetch('/api/users').then(r => r.json());
        siteData.users = users;

        const html = `
            <div class="card">
                <div class="card-header">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span class="card-title">All System Accounts (${users.length})</span>
                        <span style="font-size:0.75rem; background:#7c3aed; color:white; padding:2px 8px; border-radius:4px; font-weight:700;">
                            👑 Super Admin Privileged Access
                        </span>
                    </div>
                    <div style="display:flex; gap:12px;">
                        <input type="text" id="user-search-input" placeholder="Search user ID, name..." class="form-control" style="padding:6px 12px; width:220px;" onkeyup="filterUsersTable()">
                        <button class="btn btn-primary btn-sm" onclick="openModal('modal-create-user')">➕ Create New User</button>
                    </div>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    <table class="data-table" id="users-table">
                        <thead>
                            <tr>
                                <th>User / Name</th>
                                <th>Role</th>
                                <th>Unique User ID</th>
                                <th>Password</th>
                                <th>Email</th>
                                <th>Phone</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${users.map(u => `
                                <tr>
                                    <td style="display:flex; align-items:center; gap:10px;">
                                        <img src="${u.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150'}" style="width:34px; height:34px; border-radius:50%; object-fit:cover;">
                                        <div>
                                            <div style="font-weight:700; color:#0f172a;">${u.name}</div>
                                            <div style="font-size:0.75rem; color:#64748b;">ID #${u.id}</div>
                                        </div>
                                    </td>
                                    <td>
                                        <span class="cred-role-badge role-${u.user_type}">
                                            ${formatRoleName(u.user_type)}
                                        </span>
                                    </td>
                                    <td>
                                        <span class="pwd-badge" style="color:#1e40af; font-weight:700;">${u.username}</span>
                                    </td>
                                    <td>
                                        <div style="display:flex; align-items:center; gap:6px;">
                                            <span class="pwd-badge" id="pwd-display-${u.id}">••••••••</span>
                                            <button type="button" class="btn-icon" onclick="toggleTablePassword(${u.id}, '${u.password}')" title="Show / Hide Password">
                                                👁️
                                            </button>
                                        </div>
                                    </td>
                                    <td><span style="font-size:0.82rem; color:#475569;">${u.email}</span></td>
                                    <td><span style="font-size:0.82rem; color:#475569;">${u.phone || '—'}</span></td>
                                    <td>
                                        <button class="btn btn-primary btn-sm" style="font-size:0.75rem; padding:4px 10px;" onclick="openEditCredentialsModal(${u.id})">
                                            ✏️ Change ID & Pass
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        document.getElementById('portal-tab-content').innerHTML = html;
    } catch (err) {
        document.getElementById('portal-tab-content').innerHTML = `<div style="padding:20px; color:red;">Error loading users.</div>`;
    }
}"""

new_users_tab = """async function renderUsersTab() {
    if (currentRole !== 'super_admin') {
        showTab('dashboard');
        return;
    }

    document.getElementById('portal-header-title').innerText = 'User Accounts & Roles Governance Hub';
    document.getElementById('portal-header-desc').innerText = 'Director Authority: Create User IDs, Assign Roles, Name & Gender rules, and Reset System Test Data';

    try {
        const users = await fetch('/api/users').then(r => r.json());
        siteData.users = users;

        const html = `
            <!-- Top Action Header & Policy Callout -->
            <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:16px 20px; margin-bottom:20px; color:#1e40af; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:2rem;">👑</span>
                    <div>
                        <strong style="font-size:0.98rem;">Director Exclusive Governance & Name/Gender Policy:</strong>
                        <div style="font-size:0.83rem; color:#1d4ed8; margin-top:2px;">
                            • Every ID is created by the Director, who can assign any ID to any role.<br>
                            • <strong>Name & Gender Rule:</strong> Any ID with no assigned person name will have <strong>no gender</strong> (—). If a role is assigned to a person, their gender is displayed.<br>
                            • <strong>Top-Level Roles:</strong> Director (Owner) & IT Support Administrator (Computer Lab Master).
                        </div>
                    </div>
                </div>
                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <button class="btn btn-primary" style="font-weight:700; padding:8px 16px; background:#1e3a8a;" onclick="openModal('modal-create-user')">
                        👑➕ Create User ID & Role
                    </button>
                    <button class="btn btn-danger" style="background:#dc2626; border-color:#b91c1c; font-weight:700; padding:8px 16px;" onclick="confirmCleanTestData()">
                        🧹 Clean All Test Data
                    </button>
                    <button class="btn btn-outline" style="font-weight:700; padding:8px 14px;" onclick="seedFacultyDemo()" title="Re-seed demo teacher & accountant for testing">
                        🔄 Seed Demo Faculty
                    </button>
                </div>
            </div>

            <div class="card">
                <div class="card-header" style="justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span class="card-title">All System Accounts (${users.length})</span>
                        <span style="font-size:0.75rem; background:#1e3a8a; color:white; padding:2px 8px; border-radius:4px; font-weight:700;">
                            Director & IT Oversight
                        </span>
                    </div>
                    <div>
                        <input type="text" id="user-search-input" placeholder="Search user ID, name, role..." class="form-control" style="padding:6px 12px; width:260px;" onkeyup="filterUsersTable()">
                    </div>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    <table class="data-table" id="users-table">
                        <thead>
                            <tr>
                                <th>User / Name</th>
                                <th>Gender</th>
                                <th>Assigned Role</th>
                                <th>Unique User ID</th>
                                <th>Password</th>
                                <th>Email</th>
                                <th>Phone</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${users.map(u => {
                                const hasName = u.name && u.name.trim().length > 0;
                                const genderBadge = hasName && u.gender ? `
                                    <span class="badge" style="background:#eff6ff; color:#1e40af; font-weight:700;">
                                        ${u.gender === 'Female' ? '👩 Female' : '👨 Male'}
                                    </span>
                                ` : `<span style="color:#94a3b8; font-style:italic;">— (No Gender)</span>`;

                                return `
                                    <tr>
                                        <td style="display:flex; align-items:center; gap:10px;">
                                            <img src="${u.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150'}" style="width:34px; height:34px; border-radius:50%; object-fit:cover;">
                                            <div>
                                                <div style="font-weight:700; color:#0f172a;">${u.name || '<span style="color:#94a3b8; font-style:italic;">(Unassigned ID)</span>'}</div>
                                                <div style="font-size:0.72rem; color:#64748b;">ID #${u.id}</div>
                                            </div>
                                        </td>
                                        <td>${genderBadge}</td>
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
                                                <span class="pwd-badge" id="pwd-display-${u.id}">••••••••</span>
                                                <button type="button" class="btn-icon" onclick="toggleTablePassword(${u.id}, '${u.password}')" title="Show / Hide Password">
                                                    👁️
                                                </button>
                                            </div>
                                        </td>
                                        <td><span style="font-size:0.82rem; color:#475569;">${u.email || '—'}</span></td>
                                        <td><span style="font-size:0.82rem; color:#475569;">${u.phone || '—'}</span></td>
                                        <td>
                                            <div style="display:flex; gap:6px;">
                                                <button class="btn btn-primary btn-sm" style="font-size:0.73rem; padding:3px 8px;" onclick="openEditCredentialsModal(${u.id})">
                                                    ✏️ Edit ID/Pass
                                                </button>
                                                <button class="btn btn-secondary btn-sm" style="font-size:0.73rem; padding:3px 8px; background:#475569; color:white;" onclick="openAssignUserRoleModal(${u.id})">
                                                    🎭 Assign Role
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        document.getElementById('portal-tab-content').innerHTML = html;
    } catch (err) {
        document.getElementById('portal-tab-content').innerHTML = `<div style="padding:20px; color:red;">Error loading users: ${err.message}</div>`;
    }
}"""

if old_users_tab in code:
    code = code.replace(old_users_tab, new_users_tab)
    print("1. Replaced renderUsersTab() successfully")
else:
    # Try normalizing CRLF
    code_norm = code.replace('\r\n', '\n')
    old_norm = old_users_tab.replace('\r\n', '\n')
    if old_norm in code_norm:
        code = code_norm.replace(old_norm, new_users_tab.replace('\r\n', '\n'))
        print("1. Replaced renderUsersTab() (after line ending normalization)")
    else:
        print("WARNING: old renderUsersTab not found")

# 2. Update submitCreateUser to include gender
old_submit_create = """async function submitCreateUser(e) {
    e.preventDefault();
    const payload = {
        name: document.getElementById('create-user-name').value.trim(),
        username: document.getElementById('create-user-username').value.trim(),
        password: document.getElementById('create-user-password').value.trim(),
        email: document.getElementById('create-user-email').value.trim(),
        user_type: document.getElementById('create-user-role').value,
        phone: document.getElementById('create-user-phone').value.trim()
    };"""

new_submit_create = """function handleCreateUserNameChange(val) {
    const sel = document.getElementById('create-user-gender');
    const hint = document.getElementById('create-user-gender-hint');
    if (!val || !val.trim()) {
        if (sel) {
            sel.disabled = true;
            sel.value = '';
        }
        if (hint) hint.innerHTML = '🔒 Disabled: Role ID has no assigned person name (no gender shown).';
    } else {
        if (sel) sel.disabled = false;
        if (hint) hint.innerHTML = '✅ Enabled: Assigned person gender can now be specified.';
    }
}

async function submitCreateUser(e) {
    e.preventDefault();
    const personName = document.getElementById('create-user-name').value.trim();
    const genderSel = document.getElementById('create-user-gender');
    const genderVal = personName && genderSel ? genderSel.value : null;

    const payload = {
        name: personName,
        username: document.getElementById('create-user-username').value.trim(),
        password: document.getElementById('create-user-password').value.trim(),
        email: document.getElementById('create-user-email').value.trim(),
        user_type: document.getElementById('create-user-role').value,
        phone: document.getElementById('create-user-phone').value.trim(),
        gender: genderVal,
        created_by: currentUser ? (currentUser.name || currentUser.username) : 'Owner(Directer)'
    };"""

if old_submit_create in code:
    code = code.replace(old_submit_create, new_submit_create)
    print("2. Updated submitCreateUser() with handleCreateUserNameChange and gender")
else:
    code_norm = code.replace('\r\n', '\n')
    old_norm = old_submit_create.replace('\r\n', '\n')
    if old_norm in code_norm:
        code = code_norm.replace(old_norm, new_submit_create.replace('\r\n', '\n'))
        print("2. Updated submitCreateUser() (after line ending normalization)")
    else:
        print("WARNING: submitCreateUser not found")

with open('school_website/js/app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Part 2 completed.")
