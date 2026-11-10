# ==============================================================================
# 1. Update index.html
# ==============================================================================
with open('school_website/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html_norm = html.replace('\r\n', '\n')

old_assign_footer = """                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-assign-user-role')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Role & Identity</button>
                </div>"""

new_assign_footer = """                <div class="modal-footer" style="display:flex; justify-content:space-between; align-items:center;">
                    <button type="button" class="btn btn-danger btn-sm" id="assign-role-delete-btn" style="background:#dc2626; border-color:#b91c1c; font-weight:700;" onclick="deleteUserFromAssignRoleModal()">
                        🗑️ Delete User ID
                    </button>
                    <div style="display:flex; gap:8px;">
                        <button type="button" class="btn btn-outline" onclick="closeModal('modal-assign-user-role')">Cancel</button>
                        <button type="submit" class="btn btn-primary">Save Role & Identity</button>
                    </div>
                </div>"""

if old_assign_footer in html_norm:
    html_norm = html_norm.replace(old_assign_footer, new_assign_footer)
    print("Updated modal-assign-user-role footer in index.html")
else:
    print("old_assign_footer not found!")

old_creds_footer = """                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-it-request-change-creds')">Cancel</button>
                    <button type="submit" class="btn btn-primary" style="background:#1e3a8a; font-weight:700;">🚀 Submit for Owner Approval</button>
                </div>"""

new_creds_footer = """                <div class="modal-footer" style="display:flex; justify-content:space-between; align-items:center;">
                    <button type="button" class="btn btn-danger btn-sm" id="it-cred-delete-btn" style="background:#dc2626; border-color:#b91c1c; font-weight:700;" onclick="deleteUserFromCredsModal()">
                        🗑️ Delete User ID
                    </button>
                    <div style="display:flex; gap:8px;">
                        <button type="button" class="btn btn-outline" onclick="closeModal('modal-it-request-change-creds')">Cancel</button>
                        <button type="submit" class="btn btn-primary" style="background:#1e3a8a; font-weight:700;">🚀 Submit for Owner Approval</button>
                    </div>
                </div>"""

if old_creds_footer in html_norm:
    html_norm = html_norm.replace(old_creds_footer, new_creds_footer)
    print("Updated modal-it-request-change-creds footer in index.html")
else:
    print("old_creds_footer not found!")

# Bump cache buster query in index.html
html_norm = html_norm.replace('js/app.js?v=20261109_common_id_no_student', 'js/app.js?v=20261109_with_delete_btn')

with open('school_website/index.html', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(html_norm)
print("Saved patched index.html")

# ==============================================================================
# 2. Update app.js
# ==============================================================================
with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

app_norm = app_js.replace('\r\n', '\n')

# Add Delete ID button to renderCredentialsTab
old_creds_action_btns = """                                        <div style="display:flex; gap:6px; flex-wrap:wrap;">
                                            <button class="btn btn-primary btn-sm" style="font-size:0.73rem; padding:4px 8px; font-weight:700;" onclick="openITSupportChangeCredsModal(${u.id})">
                                                ✏️ Modify ID / Pwd
                                            </button>
                                            <button class="btn btn-secondary btn-sm" style="font-size:0.73rem; padding:4px 8px; font-weight:700; background:#2563eb; color:white;" onclick="openAssignUserRoleModal(${u.id})">
                                                🎭 Change Role
                                            </button>
                                        </div>"""

new_creds_action_btns = """                                        <div style="display:flex; gap:6px; flex-wrap:wrap;">
                                            <button class="btn btn-primary btn-sm" style="font-size:0.73rem; padding:4px 8px; font-weight:700;" onclick="openITSupportChangeCredsModal(${u.id})">
                                                ✏️ Modify ID / Pwd
                                            </button>
                                            <button class="btn btn-secondary btn-sm" style="font-size:0.73rem; padding:4px 8px; font-weight:700; background:#2563eb; color:white;" onclick="openAssignUserRoleModal(${u.id})">
                                                🎭 Change Role
                                            </button>
                                            ${(!['Owner(Directer)', 'GS_itsupport'].includes(u.username)) ? `
                                                <button class="btn btn-danger btn-sm" style="font-size:0.73rem; padding:4px 8px; font-weight:700; background:#dc2626; border-color:#b91c1c; color:white;" onclick="confirmDeleteUser(${u.id}, '${u.username}')" title="Delete User ID permanently">
                                                    🗑️ Delete ID
                                                </button>
                                            ` : ''}
                                        </div>"""

if old_creds_action_btns in app_norm:
    app_norm = app_norm.replace(old_creds_action_btns, new_creds_action_btns)
    print("Added Delete ID button to renderCredentialsTab in app.js")
else:
    print("old_creds_action_btns not found!")

# Update openAssignUserRoleModal to show/hide delete button
old_open_assign_end = """    populateAdminIdOptions('assign-role-admin-id', u.admin_user_id || u.admin_username);
    toggleAssignRoleCommon(isCommon);

    openModal('modal-assign-user-role');"""

new_open_assign_end = """    populateAdminIdOptions('assign-role-admin-id', u.admin_user_id || u.admin_username);
    toggleAssignRoleCommon(isCommon);

    const assignDelBtn = document.getElementById('assign-role-delete-btn');
    if (assignDelBtn) {
        assignDelBtn.style.display = (['Owner(Directer)', 'GS_itsupport'].includes(u.username)) ? 'none' : 'inline-block';
    }

    openModal('modal-assign-user-role');"""

if old_open_assign_end in app_norm:
    app_norm = app_norm.replace(old_open_assign_end, new_open_assign_end)
    print("Updated openAssignUserRoleModal delete button visibility in app.js")

# Update openITSupportChangeCredsModal to show/hide delete button
old_open_creds_end = """    document.getElementById('it-cred-target-info').innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <strong>${u.name || '(Unassigned Role ID)'}</strong> (ID #${u.id})
                <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">Role: <code>${u.user_type}</code> | Current User ID: <code style="color:#1e40af; font-weight:700;">${u.username}</code></div>
            </div>
            <span class="cred-role-badge role-${u.user_type}">${formatRoleName(u.user_type)}</span>
        </div>
    `;

    openModal('modal-it-request-change-creds');"""

new_open_creds_end = """    document.getElementById('it-cred-target-info').innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <strong>${u.name || '(Unassigned Role ID)'}</strong> (ID #${u.id})
                <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">Role: <code>${u.user_type}</code> | Current User ID: <code style="color:#1e40af; font-weight:700;">${u.username}</code></div>
            </div>
            <span class="cred-role-badge role-${u.user_type}">${formatRoleName(u.user_type)}</span>
        </div>
    `;

    const itCredDelBtn = document.getElementById('it-cred-delete-btn');
    if (itCredDelBtn) {
        itCredDelBtn.style.display = (['Owner(Directer)', 'GS_itsupport'].includes(u.username)) ? 'none' : 'inline-block';
    }

    openModal('modal-it-request-change-creds');"""

if old_open_creds_end in app_norm:
    app_norm = app_norm.replace(old_open_creds_end, new_open_creds_end)
    print("Updated openITSupportChangeCredsModal delete button visibility in app.js")

# Add modal delete helper functions and update confirmDeleteUser
old_confirm_del_succ = """        if (res.success) {
            alert(`✓ ${res.message}`);
            if (typeof renderUsersTab === 'function') renderUsersTab();
            if (typeof loadLoginDirectory === 'function') loadLoginDirectory();
        } else {"""

new_confirm_del_succ = """        if (res.success) {
            alert(`✓ ${res.message}`);
            closeModal('modal-assign-user-role');
            closeModal('modal-it-request-change-creds');
            if (typeof renderUsersTab === 'function' && currentTab === 'users') renderUsersTab();
            if (typeof renderCredentialsTab === 'function' && currentTab === 'credentials') renderCredentialsTab();
            if (typeof loadLoginDirectory === 'function') loadLoginDirectory();
        } else {"""

if old_confirm_del_succ in app_norm:
    app_norm = app_norm.replace(old_confirm_del_succ, new_confirm_del_succ)
    print("Updated confirmDeleteUser callbacks in app.js")

del_helpers = """
function deleteUserFromAssignRoleModal() {
    const userId = parseInt(document.getElementById('assign-role-user-id').value);
    const username = document.getElementById('assign-role-username').value;
    if (userId && username) {
        confirmDeleteUser(userId, username);
    }
}

function deleteUserFromCredsModal() {
    const userId = parseInt(document.getElementById('it-cred-user-id').value);
    const username = document.getElementById('it-cred-new-username').value;
    if (userId && username) {
        confirmDeleteUser(userId, username);
    }
}
"""

if 'function deleteUserFromAssignRoleModal' not in app_norm:
    app_norm += del_helpers
    print("Appended deleteUserFromAssignRoleModal and deleteUserFromCredsModal to app.js")

with open('school_website/js/app.js', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(app_norm)
print("Saved patched app.js")

# ==============================================================================
# 3. Update server.py
# ==============================================================================
with open('school_website/server.py', 'r', encoding='utf-8') as f:
    server_code = f.read()

server_norm = server_code.replace('\r\n', '\n')

old_server_delete = """                # Clean up dependencies if teacher
                if utype == 'teacher':
                    cur.execute("UPDATE sections SET class_teacher_id = NULL WHERE class_teacher_id = ?", (uid,))
                    cur.execute("UPDATE subjects SET teacher_id = NULL WHERE teacher_id = ?", (uid,))
                    cur.execute("DELETE FROM leaves WHERE user_id = ?", (uid,))

                cur.execute("DELETE FROM users WHERE id = ?", (uid,))"""

new_server_delete = """                # Clean up dependencies if teacher
                if utype == 'teacher':
                    cur.execute("UPDATE sections SET class_teacher_id = NULL WHERE class_teacher_id = ?", (uid,))
                    cur.execute("UPDATE subjects SET teacher_id = NULL WHERE teacher_id = ?", (uid,))
                    cur.execute("DELETE FROM leaves WHERE user_id = ?", (uid,))

                # Clean up common ID admin links and workstation assignments
                cur.execute("UPDATE users SET admin_user_id = NULL, admin_username = NULL, admin_name = NULL WHERE admin_user_id = ? OR admin_username = ?", (uid, uname))
                cur.execute("UPDATE lab_computers SET assigned_teacher_id = NULL, assigned_teacher_username = NULL WHERE assigned_teacher_id = ? OR assigned_teacher_username = ?", (uid, uname))
                cur.execute("UPDATE lab_computers SET admin_user_id = NULL, admin_username = NULL WHERE admin_user_id = ? OR admin_username = ?", (uid, uname))
                cur.execute("DELETE FROM credential_requests WHERE user_id = ? OR target_username = ? OR proposed_username = ?", (uid, uname, uname))

                cur.execute("DELETE FROM users WHERE id = ?", (uid,))"""

if old_server_delete in server_norm:
    server_norm = server_norm.replace(old_server_delete, new_server_delete)
    with open('school_website/server.py', 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(server_norm)
    print("Updated /api/users/delete in server.py")
