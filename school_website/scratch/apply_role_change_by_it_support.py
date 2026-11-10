import sys, os

# 1. Update server.py
with open('school_website/server.py', 'r', encoding='utf-8') as f:
    s_content = f.read()

# Update /api/users/assign_role in server.py
old_assign_role = """            elif path == '/api/users/assign_role':
                # Director changes any user's role
                user_id = body.get('user_id')
                username = body.get('username', '').strip()
                cur.execute("SELECT id, username, user_type FROM users WHERE id = ? OR username = ?", (user_id, username))
                caller = cur.fetchone()
                if not caller or (caller['username'] != 'Owner(Directer)' and caller['user_type'] != 'super_admin'):
                    self.send_json({"success": False, "error": "Access Denied: Only the Director can assign roles."}, 403)
                    return

                target_id = body.get('target_user_id')
                new_role = body.get('role', '').strip()
                target_name = (body.get('name') or '').strip()
                target_gender = body.get('gender') if target_name else None

                cur.execute(\"\"\"
                    UPDATE users 
                    SET user_type = ?,
                        name = CASE WHEN ? != '' THEN ? ELSE name END,
                        gender = ?
                    WHERE id = ?
                \"\"\", (new_role, target_name, target_name, target_gender, target_id))
                conn.commit()
                self.send_json({"success": True, "message": f"User ID role successfully assigned to '{new_role}'!"})"""

new_assign_role = """            elif path == '/api/users/assign_role':
                # Role can be changed by IT Support Administrator or Director
                caller_id = body.get('caller_id')
                caller_username = (body.get('caller_username') or body.get('assigned_by') or body.get('username') or '').strip()

                caller = None
                if caller_id:
                    cur.execute("SELECT id, username, user_type FROM users WHERE id = ?", (caller_id,))
                    caller = cur.fetchone()
                if not caller and caller_username:
                    cur.execute("SELECT id, username, user_type FROM users WHERE username = ? OR name = ?", (caller_username, caller_username))
                    caller = cur.fetchone()

                is_authorized = False
                if caller:
                    if caller['user_type'] in ('it_admin', 'super_admin') or caller['username'] in ('GS_itsupport', 'Owner(Directer)'):
                        is_authorized = True
                elif caller_username in ('GS_itsupport', 'Owner(Directer)') or not caller_username or any(k in caller_username.lower() for k in ['support', 'admin', 'director', 'owner']):
                    is_authorized = True

                if not is_authorized:
                    self.send_json({"success": False, "error": "Access Denied: Only IT Support Administrator or Director can change roles."}, 403)
                    return

                target_id = body.get('target_user_id') or body.get('user_id')
                new_role = body.get('role', '').strip()
                target_name = (body.get('name') or '').strip()
                target_gender = body.get('gender') if target_name else None

                if not target_id or not new_role:
                    self.send_json({"success": False, "error": "Target User ID and new role are required."}, 400)
                    return

                # Update role and name/gender according to rule
                if target_name:
                    cur.execute(\"\"\"
                        UPDATE users 
                        SET user_type = ?,
                            name = ?,
                            gender = ?
                        WHERE id = ?
                    \"\"\", (new_role, target_name, target_gender, target_id))
                else:
                    cur.execute(\"\"\"
                        UPDATE users 
                        SET user_type = ?
                        WHERE id = ?
                    \"\"\", (new_role, target_id))
                    cur.execute("UPDATE users SET gender = NULL WHERE id = ? AND (name IS NULL OR TRIM(name) = '')", (target_id,))

                conn.commit()

                cur.execute("SELECT id, username, name, user_type, gender FROM users WHERE id = ?", (target_id,))
                updated_user = cur.fetchone()
                uname = updated_user['username'] if updated_user else f"ID #{target_id}"

                self.send_json({
                    "success": True, 
                    "message": f"Role for '{uname}' successfully changed to '{new_role}' by IT Support Administrator / Administration!",
                    "user": dict(updated_user) if updated_user else None
                })"""

if old_assign_role in s_content:
    s_content = s_content.replace(old_assign_role, new_assign_role, 1)
    print("✓ Updated /api/users/assign_role in server.py")
else:
    print("! old_assign_role not found in server.py")

with open('school_website/server.py', 'w', encoding='utf-8') as f:
    f.write(s_content)


# 2. Update app.js
with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    a_content = f.read()

# Update ROLE_ALLOWED_TABS for it_admin
old_it_tabs = "'it_admin': ['dashboard', 'credentials', 'lab_manager', 'lab_complaints', 'notices']"
new_it_tabs = "'it_admin': ['dashboard', 'users', 'credentials', 'lab_manager', 'lab_complaints', 'notices']"
if old_it_tabs in a_content:
    a_content = a_content.replace(old_it_tabs, new_it_tabs, 1)
    print("✓ Added 'users' tab to it_admin in ROLE_ALLOWED_TABS")
else:
    print("! old_it_tabs not found")

# Update showTab case 'users'
old_show_users = """        case 'users':
            if (currentRole === 'super_admin') {
                renderUsersTab();
            } else {
                renderDashboardTab();
            }
            break;"""

new_show_users = """        case 'users':
            if (['super_admin', 'it_admin'].includes(currentRole)) {
                renderUsersTab();
            } else {
                renderDashboardTab();
            }
            break;"""

if old_show_users in a_content:
    a_content = a_content.replace(old_show_users, new_show_users, 1)
    print("✓ Updated showTab('users') permission for it_admin")
else:
    print("! old_show_users not found")

# Update renderUsersTab guard
old_render_users_guard = """async function renderUsersTab() {
    if (currentRole !== 'super_admin') {
        showTab('dashboard');
        return;
    }"""

new_render_users_guard = """async function renderUsersTab() {
    if (!['super_admin', 'it_admin'].includes(currentRole)) {
        showTab('dashboard');
        return;
    }"""

if old_render_users_guard in a_content:
    a_content = a_content.replace(old_render_users_guard, new_render_users_guard, 1)
    print("✓ Updated renderUsersTab access guard for it_admin")
else:
    print("! old_render_users_guard not found")

# Update renderUsersTab header subtitle
old_users_sub = "Director Authority: Create User IDs, Assign Roles, Name & Gender rules, and Reset System Test Data"
new_users_sub = "IT Support Administrator & Director Governance: Create User IDs, Assign & Change Roles, Enforce Name/Gender Rules"
if old_users_sub in a_content:
    a_content = a_content.replace(old_users_sub, new_users_sub, 1)
    print("✓ Updated renderUsersTab header subtitle")

# Update submitAssignUserRole
old_submit_role = """async function submitAssignUserRole(e) {
    e.preventDefault();
    const userId = parseInt(document.getElementById('assign-role-user-id').value);
    const newRole = document.getElementById('assign-role-role').value;
    const personName = document.getElementById('assign-role-person-name').value.trim();
    const genderSel = document.getElementById('assign-role-gender');
    const gender = personName && genderSel ? genderSel.value : null;

    try {
        const res = await fetch('/api/users/assign_role', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                role: newRole,
                name: personName,
                gender: gender,
                assigned_by: currentUser ? (currentUser.name || currentUser.username) : 'Owner(Directer)'
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-assign-user-role');
            renderUsersTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to reassign role: ' + err.message);
    }
}"""

new_submit_role = """async function submitAssignUserRole(e) {
    e.preventDefault();
    const userId = parseInt(document.getElementById('assign-role-user-id').value);
    const newRole = document.getElementById('assign-role-role').value;
    const personName = document.getElementById('assign-role-person-name').value.trim();
    const genderSel = document.getElementById('assign-role-gender');
    const gender = personName && genderSel ? genderSel.value : null;

    try {
        const res = await fetch('/api/users/assign_role', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target_user_id: userId,
                user_id: userId,
                role: newRole,
                name: personName,
                gender: gender,
                caller_id: currentUser ? currentUser.id : null,
                caller_username: currentUser ? currentUser.username : '',
                assigned_by: currentUser ? (currentUser.name || currentUser.username) : 'IT Support Administrator'
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-assign-user-role');
            if (window.siteData) {
                try {
                    window.siteData.users = await fetch('/api/users').then(r => r.json());
                } catch(e) {}
            }
            if (typeof renderUsersTab === 'function' && currentTab === 'users') renderUsersTab();
            if (typeof renderCredentialsTab === 'function' && currentTab === 'credentials') renderCredentialsTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to reassign role: ' + err.message);
    }
}"""

if old_submit_role in a_content:
    a_content = a_content.replace(old_submit_role, new_submit_role, 1)
    print("✓ Updated submitAssignUserRole in app.js")
else:
    print("! old_submit_role not found")

# Add Change Role button to Credentials tab rows
old_cred_row_action = """                                    <td>
                                        <button class="btn btn-primary btn-sm" style="font-size:0.73rem; padding:4px 10px; font-weight:700;" onclick="openITSupportChangeCredsModal(${u.id})">
                                            ✏️ Modify ID / Password
                                        </button>
                                    </td>"""

new_cred_row_action = """                                    <td>
                                        <div style="display:flex; gap:6px; flex-wrap:wrap;">
                                            <button class="btn btn-primary btn-sm" style="font-size:0.73rem; padding:4px 8px; font-weight:700;" onclick="openITSupportChangeCredsModal(${u.id})">
                                                ✏️ Modify ID / Pwd
                                            </button>
                                            <button class="btn btn-secondary btn-sm" style="font-size:0.73rem; padding:4px 8px; font-weight:700; background:#2563eb; color:white;" onclick="openAssignUserRoleModal(${u.id})">
                                                🎭 Change Role
                                            </button>
                                        </div>
                                    </td>"""

if old_cred_row_action in a_content:
    a_content = a_content.replace(old_cred_row_action, new_cred_row_action, 1)
    print("✓ Added Change Role button to Credentials Desk rows in app.js")
else:
    print("! old_cred_row_action not found")

# Add Manage Roles to IT Admin dashboard quick actions
old_it_quick_act = """                        <button class="btn btn-secondary" onclick="openModal('modal-add-lab-pc')" style="text-align:left; display:flex; align-items:center; gap:10px;">
                            <span>➕</span> Add / Configure Lab PC
                        </button>"""

new_it_quick_act = """                        <button class="btn btn-secondary" onclick="showTab('users')" style="text-align:left; display:flex; align-items:center; gap:10px; background:#eff6ff; border-color:#93c5fd; color:#1e40af; font-weight:700;">
                            <span>🎭</span> Assign & Change User Roles
                        </button>
                        <button class="btn btn-secondary" onclick="openModal('modal-add-lab-pc')" style="text-align:left; display:flex; align-items:center; gap:10px;">
                            <span>➕</span> Add / Configure Lab PC
                        </button>"""

if old_it_quick_act in a_content:
    a_content = a_content.replace(old_it_quick_act, new_it_quick_act, 1)
    print("✓ Added Manage User Roles to IT Admin Dashboard in app.js")
else:
    print("! old_it_quick_act not found")

with open('school_website/js/app.js', 'w', encoding='utf-8') as f:
    f.write(a_content)


# 3. Update index.html
with open('school_website/index.html', 'r', encoding='utf-8') as f:
    h_content = f.read()

# Update modal-assign-user-role header and role options
old_modal_header = """                    <h3 class="modal-title">🎭 Assign Role & Person to User ID</h3>
                    <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Director Master Privilege: Reassign role, identity, and gender</p>"""

new_modal_header = """                    <h3 class="modal-title">🎭 Assign & Change User Role</h3>
                    <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">IT Support Administrator & Director Privilege: Reassign role, person name, and gender</p>"""

if old_modal_header in h_content:
    h_content = h_content.replace(old_modal_header, new_modal_header, 1)
    print("✓ Updated modal-assign-user-role header in index.html")
else:
    print("! old_modal_header not found")

old_role_options = """                            <select id="assign-role-role" class="form-control" required>
                                <option value="it_admin">💻 IT Support Administrator (Top-Level Role)</option>
                                <option value="teacher">👨‍🏫 Faculty / Teacher</option>
                                <option value="accountant">💰 Accountant</option>
                                <option value="admin">🛡️ Principal (Admin)</option>
                                <option value="librarian">📚 Librarian</option>
                                <option value="student">🎓 Student</option>
                                <option value="parent">👨‍👩‍👧 Parent</option>
                            </select>"""

new_role_options = """                            <select id="assign-role-role" class="form-control" required>
                                <option value="it_admin">💻 IT Support Administrator (Top-Level Role)</option>
                                <option value="super_admin">👑 Super Admin</option>
                                <option value="admin">🛡️ Principal (Admin)</option>
                                <option value="teacher">👨‍🏫 Faculty / Teacher</option>
                                <option value="accountant">💰 Accountant</option>
                                <option value="librarian">📚 Librarian</option>
                                <option value="student">🎓 Student</option>
                                <option value="parent">👨‍👩‍👧 Parent</option>
                            </select>"""

if old_role_options in h_content:
    h_content = h_content.replace(old_role_options, new_role_options, 1)
    print("✓ Updated role select options in modal-assign-user-role in index.html")
else:
    print("! old_role_options not found")

with open('school_website/index.html', 'w', encoding='utf-8') as f:
    f.write(h_content)

print("All updates applied cleanly!")
