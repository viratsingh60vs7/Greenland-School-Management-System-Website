# ==============================================================================
# 1. Update index.html
# ==============================================================================
with open('school_website/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html_norm = html.replace('\r\n', '\n')

old_s1 = '<select id="create-user-admin-id" class="form-control">'
new_s1 = '<select id="create-user-admin-id" class="form-control" onfocus="populateAdminIdOptions(this.id)" onclick="if(this.options.length<=1) populateAdminIdOptions(this.id)">'

old_s2 = '<select id="assign-role-admin-id" class="form-control">'
new_s2 = '<select id="assign-role-admin-id" class="form-control" onfocus="populateAdminIdOptions(this.id)" onclick="if(this.options.length<=1) populateAdminIdOptions(this.id)">'

old_s3 = '<select id="it-create-admin-id" class="form-control">'
new_s3 = '<select id="it-create-admin-id" class="form-control" onfocus="populateAdminIdOptions(this.id)" onclick="if(this.options.length<=1) populateAdminIdOptions(this.id)">'

if old_s1 in html_norm:
    html_norm = html_norm.replace(old_s1, new_s1)
    print("Updated create-user-admin-id in index.html")

if old_s2 in html_norm:
    html_norm = html_norm.replace(old_s2, new_s2)
    print("Updated assign-role-admin-id in index.html")

if old_s3 in html_norm:
    html_norm = html_norm.replace(old_s3, new_s3)
    print("Updated it-create-admin-id in index.html")

with open('school_website/index.html', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(html_norm)
print("Saved patched index.html")

# ==============================================================================
# 2. Update app.js
# ==============================================================================
with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    app_js = f.read()

app_norm = app_js.replace('\r\n', '\n')

old_pop_admin = """function populateAdminIdOptions(selectId, selectedId = null) {
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
}"""

new_pop_admin = """async function populateAdminIdOptions(selectId, selectedId = null) {
    const sel = document.getElementById(selectId);
    if (!sel) return;

    let users = (window.siteData && Array.isArray(window.siteData.users) && window.siteData.users.length > 0)
        ? window.siteData.users
        : [];

    if (!users || users.length === 0) {
        try {
            const res = await fetch('/api/users');
            if (res.ok) {
                const data = await res.json();
                if (Array.isArray(data) && data.length > 0) {
                    users = data;
                    if (!window.siteData) window.siteData = {};
                    window.siteData.users = users;
                }
            }
        } catch (e) {
            console.warn('Could not fetch users for admin dropdown:', e);
        }
    }

    if (!users || users.length === 0) {
        if (typeof UNIQUE_ROLE_ACCOUNTS !== 'undefined' && Array.isArray(UNIQUE_ROLE_ACCOUNTS)) {
            users = UNIQUE_ROLE_ACCOUNTS.map((u, i) => ({
                id: i + 1,
                username: u.username,
                name: u.name,
                user_type: u.roleKey
            }));
        }
    }

    let opts = '<option value="">— Select Admin / Manager for this Common ID —</option>';
    let matched = false;

    const rolePriority = { 'teacher': 1, 'it_admin': 2, 'super_admin': 3, 'admin': 4, 'accountant': 5, 'librarian': 6 };
    const sorted = [...users].sort((a, b) => {
        const pa = rolePriority[a.user_type] || 99;
        const pb = rolePriority[b.user_type] || 99;
        return pa - pb;
    });

    sorted.forEach(u => {
        if (u.user_type === 'common_id' && (!selectedId || (String(u.id) !== String(selectedId) && String(u.username) !== String(selectedId)))) {
            return;
        }
        const isMatch = selectedId && (String(u.id) === String(selectedId) || String(u.username).toLowerCase() === String(selectedId).toLowerCase());
        if (isMatch) matched = true;
        const roleLabel = (typeof formatRoleName === 'function') ? formatRoleName(u.user_type) : (u.user_type || 'User');
        const nameLabel = u.name ? `${u.name} (${u.username})` : u.username;
        opts += `<option value="${u.id}" data-username="${u.username}" data-name="${u.name || u.username}" ${isMatch ? 'selected' : ''}>👑 ${nameLabel} [${roleLabel}]</option>`;
    });

    if (!matched && !selectedId) {
        const teacherMatch = users.find(u => u.username === 'GS_teacher' || (u.name && u.name.toLowerCase().includes('computer teacher')));
        if (teacherMatch) {
            opts = opts.replace(`value="${teacherMatch.id}"`, `value="${teacherMatch.id}" selected`);
        }
    }

    sel.innerHTML = opts;
}"""

if old_pop_admin in app_norm:
    app_norm = app_norm.replace(old_pop_admin, new_pop_admin)
    print("Replaced populateAdminIdOptions with async auto-fetching version in app.js")
else:
    print("old_pop_admin not found in app.js!")

# Also update openModal to await populateAdminIdOptions and handle modal-assign-user-role
old_open_modal_part = """    if (id === 'modal-create-user') {
        populateAdminIdOptions('create-user-admin-id');
    }
    if (id === 'modal-it-request-create-user') {
        populateAdminIdOptions('it-create-admin-id');
    }"""

new_open_modal_part = """    if (id === 'modal-create-user') {
        await populateAdminIdOptions('create-user-admin-id');
    }
    if (id === 'modal-it-request-create-user') {
        await populateAdminIdOptions('it-create-admin-id');
    }
    if (id === 'modal-assign-user-role') {
        await populateAdminIdOptions('assign-role-admin-id');
    }"""

if old_open_modal_part in app_norm:
    app_norm = app_norm.replace(old_open_modal_part, new_open_modal_part)
    print("Updated openModal in app.js")

# In toggleAssignRoleCommon, also call populateAdminIdOptions
old_toggle_assign_common = """function toggleAssignRoleCommon(isCommon) {
    const fields = document.getElementById('assign-role-common-fields');
    const badge = document.getElementById('assign-role-mail-badge');
    if (fields) fields.style.display = isCommon ? 'block' : 'none';
    if (badge) badge.style.display = isCommon ? 'inline-block' : 'none';
}"""

new_toggle_assign_common = """function toggleAssignRoleCommon(isCommon) {
    const fields = document.getElementById('assign-role-common-fields');
    const badge = document.getElementById('assign-role-mail-badge');
    if (fields) fields.style.display = isCommon ? 'block' : 'none';
    if (badge) badge.style.display = isCommon ? 'inline-block' : 'none';
    if (isCommon) {
        populateAdminIdOptions('assign-role-admin-id');
    }
}"""

if old_toggle_assign_common in app_norm:
    app_norm = app_norm.replace(old_toggle_assign_common, new_toggle_assign_common)
    print("Updated toggleAssignRoleCommon in app.js")

with open('school_website/js/app.js', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(app_norm)
print("Saved patched app.js")
