with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

app_norm = app_js.replace('\r\n', '\n')

# 1. Update ROLE_ALLOWED_TABS
old_role_tabs = """    'accountant': ['dashboard', 'payments', 'leaves', 'payroll', 'students', 'notices'],
    'librarian': ['dashboard', 'library', 'notices'],
    'it_admin': ['dashboard', 'users', 'credentials', 'asset_management', 'lab_manager', 'lab_complaints', 'notices']
};"""

new_role_tabs = """    'accountant': ['dashboard', 'payments', 'leaves', 'payroll', 'students', 'notices'],
    'librarian': ['dashboard', 'library', 'notices'],
    'it_admin': ['dashboard', 'users', 'credentials', 'asset_management', 'lab_manager', 'lab_complaints', 'notices'],
    'common_id': ['dashboard', 'lab_complaints', 'notices']
};"""

if old_role_tabs in app_norm:
    app_norm = app_norm.replace(old_role_tabs, new_role_tabs)
    print("Updated ROLE_ALLOWED_TABS in app.js")
else:
    print("old_role_tabs not found!")

# 2. Update formatRoleName
old_format_role = """        'librarian': 'Librarian',
        'it_admin': 'IT Support Administrator'
    };"""

new_format_role = """        'librarian': 'Librarian',
        'it_admin': 'IT Support Administrator',
        'common_id': '🏷️ Common ID (Lab Fleet)'
    };"""

if old_format_role in app_norm:
    app_norm = app_norm.replace(old_format_role, new_format_role)
    print("Updated formatRoleName in app.js")
else:
    print("old_format_role not found!")

# 3. Update table rendering in renderUsersTab
old_table_common_col = """                                        <td>
                                            ${u.is_common_id || u.common_id_name || u.username === 'GS_teacher' ? `
                                                <div>
                                                    <span class="badge" style="background:#eff6ff; color:#1d4ed8; font-weight:700; font-size:0.75rem;">
                                                        🏷️ ${u.common_id_name || 'Computer Teacher Lab Fleet'}
                                                    </span>
                                                    <div style="margin-top:3px;">
                                                        <span class="badge" style="background:#fee2e2; color:#dc2626; font-size:0.68rem; font-weight:700;">
                                                            📭 No Mail Service
                                                        </span>
                                                    </div>
                                                    ${u.username === 'GS_teacher' || (u.assigned_lab_count && u.assigned_lab_count > 0) ? `
                                                        <div style="font-size:0.72rem; color:#15803d; font-weight:700; margin-top:2px;">
                                                            🖥️ Assigned: Lab 1 (50 PCs) & Lab 2 (50 PCs) [100 Total]
                                                        </div>
                                                    ` : ''}
                                                </div>
                                            ` : `
                                                <span style="color:#64748b; font-size:0.75rem;">Individual Account</span>
                                            `}
                                        </td>"""

new_table_common_col = """                                        <td>
                                            ${u.is_common_id || u.user_type === 'common_id' || u.common_id_name || u.username === 'GS_teacher' ? `
                                                <div>
                                                    <span class="badge" style="background:#eff6ff; color:#1d4ed8; font-weight:700; font-size:0.75rem;">
                                                        🏷️ ${u.common_id_name || 'Common Fleet ID'}
                                                    </span>
                                                    ${u.admin_username ? `
                                                        <div style="margin-top:3px;">
                                                            <span class="badge" style="background:#f0fdf4; color:#166534; font-size:0.72rem; font-weight:700; border:1px solid #bbf7d0;">
                                                                👑 Admin: ${u.admin_name ? `${u.admin_name} (${u.admin_username})` : u.admin_username}
                                                            </span>
                                                        </div>
                                                    ` : (u.username === 'GS_teacher' ? `
                                                        <div style="margin-top:3px;">
                                                            <span class="badge" style="background:#f0fdf4; color:#166534; font-size:0.72rem; font-weight:700; border:1px solid #bbf7d0;">
                                                                👑 Fleet Admin: Computer Teacher (Self)
                                                            </span>
                                                        </div>
                                                    ` : '')}
                                                    <div style="margin-top:3px;">
                                                        <span class="badge" style="background:#fee2e2; color:#dc2626; font-size:0.68rem; font-weight:700;">
                                                            📭 No Mail Service
                                                        </span>
                                                    </div>
                                                    ${(u.username === 'GS_teacher' || (u.assigned_lab_count && u.assigned_lab_count > 0)) ? `
                                                        <div style="font-size:0.72rem; color:#15803d; font-weight:700; margin-top:2px;">
                                                            🖥️ Assigned: ${u.assigned_lab_count >= 100 ? 'Lab 1 & 2 (100 PCs)' : `${u.assigned_lab_count} Lab PCs`}
                                                        </div>
                                                    ` : ''}
                                                </div>
                                            ` : `
                                                <span style="color:#64748b; font-size:0.75rem;">Individual Account</span>
                                            `}
                                        </td>"""

if old_table_common_col in app_norm:
    app_norm = app_norm.replace(old_table_common_col, new_table_common_col)
    print("Updated users-table common ID column in app.js")
else:
    print("old_table_common_col not found!")

# 4. Add helper functions and event handlers
helper_functions = """
function populateAdminIdOptions(selectId, selectedId = null) {
    const sel = document.getElementById(selectId);
    if (!sel) return;
    const users = (window.siteData && window.siteData.users) || [];
    let opts = '<option value="">— Select Admin / Manager for this Common ID —</option>';
    let matched = false;
    users.forEach(u => {
        const isMatch = selectedId && (String(u.id) === String(selectedId) || String(u.username).toLowerCase() === String(selectedId).toLowerCase());
        if (isMatch) matched = true;
        const roleLabel = formatRoleName(u.user_type);
        const nameLabel = u.name ? `${u.name} (${u.username})` : u.username;
        opts += `<option value="${u.id}" data-username="${u.username}" data-name="${u.name || u.username}" ${isMatch ? 'selected' : ''}>👑 ${nameLabel} [${roleLabel}]</option>`;
    });
    // Default to Computer Teacher if not selected
    if (!matched && !selectedId) {
        const teacherMatch = users.find(u => u.username === 'GS_teacher');
        if (teacherMatch) {
            opts = opts.replace(`value="${teacherMatch.id}"`, `value="${teacherMatch.id}" selected`);
        }
    }
    sel.innerHTML = opts;
}

function handleCreateUserRoleChange(val) {
    const isCommon = val === 'common_id';
    const check = document.getElementById('create-user-is-common');
    if (check) check.checked = isCommon;
    toggleCreateUserCommon(isCommon);
    if (isCommon) {
        populateAdminIdOptions('create-user-admin-id');
        const nameInput = document.getElementById('create-user-common-name');
        if (nameInput && !nameInput.value) nameInput.value = 'Computer Lab 1 Fleet (Common ID)';
        const emailInput = document.getElementById('create-user-email');
        if (emailInput) {
            emailInput.value = '';
            emailInput.placeholder = '(No mail service for Common ID)';
        }
    }
}

function handleITCreateUserRoleChange(val) {
    const isCommon = val === 'common_id';
    const check = document.getElementById('it-create-is-common');
    if (check) check.checked = isCommon;
    toggleITCreateUserCommon(isCommon);
    if (isCommon) {
        populateAdminIdOptions('it-create-admin-id');
        const nameInput = document.getElementById('it-create-common-name');
        if (nameInput && !nameInput.value) nameInput.value = 'Computer Lab 1 Fleet (Common ID)';
        const emailInput = document.getElementById('it-create-email');
        if (emailInput) {
            emailInput.value = '';
            emailInput.placeholder = '(No mail service for Common ID)';
        }
    }
}

function toggleITCreateUserCommon(isCommon) {
    const fields = document.getElementById('it-create-common-fields');
    const badge = document.getElementById('it-create-mail-badge');
    if (fields) fields.style.display = isCommon ? 'block' : 'none';
    if (badge) {
        badge.style.background = isCommon ? '#fee2e2' : '#dcfce7';
        badge.style.color = isCommon ? '#dc2626' : '#15803d';
        badge.innerHTML = isCommon ? '📭 No Mail Service' : '✉️ Standard Mail Service';
    }
    if (isCommon) {
        populateAdminIdOptions('it-create-admin-id');
    }
}

function handleAssignRoleRoleChange(val) {
    const isCommon = val === 'common_id';
    const check = document.getElementById('assign-role-is-common');
    if (check) check.checked = isCommon;
    toggleAssignRoleCommon(isCommon);
    if (isCommon) {
        populateAdminIdOptions('assign-role-admin-id');
    }
}
"""

old_toggle_create = """function toggleCreateUserCommon(isCommon) {
    const fields = document.getElementById('create-user-common-fields');
    const badge = document.getElementById('create-user-mail-badge');
    if (fields) fields.style.display = isCommon ? 'block' : 'none';
    if (badge) {
        badge.style.background = isCommon ? '#fee2e2' : '#dcfce7';
        badge.style.color = isCommon ? '#dc2626' : '#15803d';
        badge.innerHTML = isCommon ? '📭 No Mail Service' : '✉️ Standard Mail Service';
    }
}"""

new_toggle_create = helper_functions + """
function toggleCreateUserCommon(isCommon) {
    const fields = document.getElementById('create-user-common-fields');
    const badge = document.getElementById('create-user-mail-badge');
    if (fields) fields.style.display = isCommon ? 'block' : 'none';
    if (badge) {
        badge.style.background = isCommon ? '#fee2e2' : '#dcfce7';
        badge.style.color = isCommon ? '#dc2626' : '#15803d';
        badge.innerHTML = isCommon ? '📭 No Mail Service' : '✉️ Standard Mail Service';
    }
    if (isCommon) {
        populateAdminIdOptions('create-user-admin-id');
    }
}"""

if old_toggle_create in app_norm:
    app_norm = app_norm.replace(old_toggle_create, new_toggle_create)
    print("Inserted helper functions and updated toggleCreateUserCommon in app.js")
else:
    print("old_toggle_create not found!")

# 5. Update openAssignUserRoleModal
old_open_assign_modal = """    const commonCheck = document.getElementById('assign-role-is-common');
    if (commonCheck) commonCheck.checked = isCommon;
    const commonName = document.getElementById('assign-role-common-name');
    if (commonName) commonName.value = u.common_id_name || (isCommon ? 'Computer Teacher Lab Fleet' : '');
    const fleetSel = document.getElementById('assign-role-lab-fleet');
    if (fleetSel) {
        fleetSel.value = (u.username === 'GS_teacher' || (u.assigned_lab_count && u.assigned_lab_count >= 100)) ? 'both' : 'none';
    }
    toggleAssignRoleCommon(isCommon);

    openModal('modal-assign-user-role');"""

new_open_assign_modal = """    const commonCheck = document.getElementById('assign-role-is-common');
    if (commonCheck) commonCheck.checked = isCommon;
    const commonName = document.getElementById('assign-role-common-name');
    if (commonName) commonName.value = u.common_id_name || (isCommon ? 'Computer Teacher Lab Fleet' : '');
    const fleetSel = document.getElementById('assign-role-lab-fleet');
    if (fleetSel) {
        fleetSel.value = (u.username === 'GS_teacher' || (u.assigned_lab_count && u.assigned_lab_count >= 100)) ? 'both' : 'none';
    }
    populateAdminIdOptions('assign-role-admin-id', u.admin_user_id || u.admin_username);
    toggleAssignRoleCommon(isCommon);

    openModal('modal-assign-user-role');"""

if old_open_assign_modal in app_norm:
    app_norm = app_norm.replace(old_open_assign_modal, new_open_assign_modal)
    print("Updated openAssignUserRoleModal in app.js")
else:
    print("old_open_assign_modal not found!")

# 6. Update submitCreateUser in app.js
old_submit_create_payload = """    const isCommon = document.getElementById('create-user-is-common') ? document.getElementById('create-user-is-common').checked : false;
    const commonName = document.getElementById('create-user-common-name') ? document.getElementById('create-user-common-name').value.trim() : '';

    const payload = {
        name: personName,
        username: document.getElementById('create-user-username').value.trim(),
        password: document.getElementById('create-user-password').value.trim(),
        email: isCommon ? '' : document.getElementById('create-user-email').value.trim(),
        user_type: document.getElementById('create-user-role').value,
        phone: document.getElementById('create-user-phone').value.trim(),
        gender: genderVal,
        is_common_id: isCommon ? 1 : 0,
        common_id_name: isCommon ? (commonName || 'Common Fleet Account') : null,
        has_mail_services: isCommon ? 0 : 1,
        created_by: currentUser ? (currentUser.name || currentUser.username) : 'Owner(Directer)'
    };"""

new_submit_create_payload = """    const roleVal = document.getElementById('create-user-role').value;
    const isCommon = (roleVal === 'common_id') || (document.getElementById('create-user-is-common') ? document.getElementById('create-user-is-common').checked : false);
    const commonName = document.getElementById('create-user-common-name') ? document.getElementById('create-user-common-name').value.trim() : '';
    const adminSel = document.getElementById('create-user-admin-id');
    const adminUserId = (isCommon && adminSel && adminSel.value) ? parseInt(adminSel.value) : null;
    const adminUsername = (isCommon && adminSel && adminSel.selectedOptions[0]) ? adminSel.selectedOptions[0].getAttribute('data-username') : null;
    const adminName = (isCommon && adminSel && adminSel.selectedOptions[0]) ? adminSel.selectedOptions[0].getAttribute('data-name') : null;
    const labFleet = (document.getElementById('create-user-lab-fleet')) ? document.getElementById('create-user-lab-fleet').value : 'none';

    const payload = {
        name: personName,
        username: document.getElementById('create-user-username').value.trim(),
        password: document.getElementById('create-user-password').value.trim(),
        email: isCommon ? '' : document.getElementById('create-user-email').value.trim(),
        user_type: roleVal,
        phone: document.getElementById('create-user-phone').value.trim(),
        gender: genderVal,
        is_common_id: isCommon ? 1 : 0,
        common_id_name: isCommon ? (commonName || 'Common Fleet Account') : null,
        admin_user_id: adminUserId,
        admin_username: adminUsername,
        admin_name: adminName,
        assigned_lab_fleet: labFleet,
        has_mail_services: isCommon ? 0 : 1,
        created_by: currentUser ? (currentUser.name || currentUser.username) : 'Owner(Directer)'
    };"""

if old_submit_create_payload in app_norm:
    app_norm = app_norm.replace(old_submit_create_payload, new_submit_create_payload)
    print("Updated submitCreateUser payload in app.js")
else:
    print("old_submit_create_payload not found!")

# 7. Update submitITSupportCreateUser in app.js
old_it_create_payload = """    try {
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
        });"""

new_it_create_payload = """    const isCommon = (role === 'common_id') || (document.getElementById('it-create-is-common') ? document.getElementById('it-create-is-common').checked : false);
    const commonName = document.getElementById('it-create-common-name') ? document.getElementById('it-create-common-name').value.trim() : '';
    const adminSel = document.getElementById('it-create-admin-id');
    const adminUserId = (isCommon && adminSel && adminSel.value) ? parseInt(adminSel.value) : null;
    const adminUsername = (isCommon && adminSel && adminSel.selectedOptions[0]) ? adminSel.selectedOptions[0].getAttribute('data-username') : null;
    const adminName = (isCommon && adminSel && adminSel.selectedOptions[0]) ? adminSel.selectedOptions[0].getAttribute('data-name') : null;
    const labFleet = (document.getElementById('it-create-lab-fleet')) ? document.getElementById('it-create-lab-fleet').value : 'none';

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
                email: isCommon ? '' : email,
                phone: phone,
                reason: reason,
                is_common_id: isCommon ? 1 : 0,
                common_id_name: isCommon ? (commonName || 'Common Fleet Account') : null,
                admin_user_id: adminUserId,
                admin_username: adminUsername,
                admin_name: adminName,
                assigned_lab_fleet: labFleet,
                has_mail_services: isCommon ? 0 : 1,
                requested_by_id: currentUser ? currentUser.id : null,
                requested_by_name: currentUser ? (currentUser.name || currentUser.username) : 'IT Support Administrator',
                requested_by_username: currentUser ? currentUser.username : 'GS_itsupport'
            })
        });"""

if old_it_create_payload in app_norm:
    app_norm = app_norm.replace(old_it_create_payload, new_it_create_payload)
    print("Updated submitITSupportCreateUser in app.js")
else:
    print("old_it_create_payload not found!")

# 8. Update submitAssignUserRole in app.js
old_assign_role_payload = """    const isCommon = document.getElementById('assign-role-is-common') ? document.getElementById('assign-role-is-common').checked : false;
    const commonName = document.getElementById('assign-role-common-name') ? document.getElementById('assign-role-common-name').value.trim() : '';
    const fleetVal = document.getElementById('assign-role-lab-fleet') ? document.getElementById('assign-role-lab-fleet').value : 'none';

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
                is_common_id: isCommon ? 1 : 0,
                common_id_name: isCommon ? (commonName || 'Common Fleet Account') : null,
                has_mail_services: isCommon ? 0 : 1,
                assigned_lab_fleet: fleetVal,
                caller_id: currentUser ? currentUser.id : null,
                caller_username: currentUser ? currentUser.username : '',
                assigned_by: currentUser ? (currentUser.name || currentUser.username) : 'IT Support Administrator'
            })
        });"""

new_assign_role_payload = """    const isCommon = (newRole === 'common_id') || (document.getElementById('assign-role-is-common') ? document.getElementById('assign-role-is-common').checked : false);
    const commonName = document.getElementById('assign-role-common-name') ? document.getElementById('assign-role-common-name').value.trim() : '';
    const fleetVal = document.getElementById('assign-role-lab-fleet') ? document.getElementById('assign-role-lab-fleet').value : 'none';
    const adminSel = document.getElementById('assign-role-admin-id');
    const adminUserId = (isCommon && adminSel && adminSel.value) ? parseInt(adminSel.value) : null;
    const adminUsername = (isCommon && adminSel && adminSel.selectedOptions[0]) ? adminSel.selectedOptions[0].getAttribute('data-username') : null;
    const adminName = (isCommon && adminSel && adminSel.selectedOptions[0]) ? adminSel.selectedOptions[0].getAttribute('data-name') : null;

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
                is_common_id: isCommon ? 1 : 0,
                common_id_name: isCommon ? (commonName || 'Common Fleet Account') : null,
                admin_user_id: adminUserId,
                admin_username: adminUsername,
                admin_name: adminName,
                has_mail_services: isCommon ? 0 : 1,
                assigned_lab_fleet: fleetVal,
                caller_id: currentUser ? currentUser.id : null,
                caller_username: currentUser ? currentUser.username : '',
                assigned_by: currentUser ? (currentUser.name || currentUser.username) : 'IT Support Administrator'
            })
        });"""

if old_assign_role_payload in app_norm:
    app_norm = app_norm.replace(old_assign_role_payload, new_assign_role_payload)
    print("Updated submitAssignUserRole in app.js")
else:
    print("old_assign_role_payload not found!")

with open('school_website/js/app.js', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(app_norm)
print("Saved patched app.js")
