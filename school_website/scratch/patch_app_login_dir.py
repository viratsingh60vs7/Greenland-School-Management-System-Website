with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update openPortalLogin to call loadLoginDirectory()
target_open_login = """function openPortalLogin() {
    const pub = document.getElementById('public-website');
    const port = document.getElementById('portal-container');
    const login = document.getElementById('portal-login-view');
    if (pub) pub.style.display = 'none';
    if (port) port.style.display = 'none';
    if (login) login.style.display = 'flex';
    window.location.hash = '#login';

    const err = document.getElementById('login-error-msg');
    if (err) err.style.display = 'none';
    const success = document.getElementById('login-success-msg');
    if (success) success.style.display = 'none';
    const usr = document.getElementById('login-username');
    if (usr) usr.focus();
}"""

replacement_open_login = """function openPortalLogin() {
    const pub = document.getElementById('public-website');
    const port = document.getElementById('portal-container');
    const login = document.getElementById('portal-login-view');
    if (pub) pub.style.display = 'none';
    if (port) port.style.display = 'none';
    if (login) login.style.display = 'flex';
    window.location.hash = '#login';

    const err = document.getElementById('login-error-msg');
    if (err) err.style.display = 'none';
    const success = document.getElementById('login-success-msg');
    if (success) success.style.display = 'none';
    const usr = document.getElementById('login-username');
    if (usr) usr.focus();

    if (typeof loadLoginDirectory === 'function') {
        loadLoginDirectory();
    }
}

// =====================================================================
// DYNAMIC LOGIN USER DIRECTORY (Loaded live from database)
// - If user ID is deleted -> NOT listed on login page
// - When new user ID is created -> Automatically shown on login page
// - STRICT POLICY: ONLY TEACHER user IDs can be clicked to auto-fill
// =====================================================================
async function loadLoginDirectory() {
    const container = document.getElementById('login-staff-directory');
    if (!container) return;

    try {
        const res = await fetch('/api/login_directory').then(r => r.json());
        const users = (res && res.users) ? res.users : [];

        if (users.length === 0) {
            container.innerHTML = `
                <div style="font-size:0.75rem; color:#94a3b8; padding:8px; grid-column:1/-1; text-align:center;">
                    No active staff accounts found in database.
                </div>
            `;
            return;
        }

        container.innerHTML = users.map(u => {
            if (u.is_clickable || u.is_teacher) {
                // STRICT REQUIREMENT: ONLY TEACHER CAN CLICK ON IT!
                return `
                    <button type="button" 
                            class="btn btn-outline btn-sm login-teacher-clickable-btn" 
                            style="font-size:0.73rem; padding:6px 8px; text-align:left; border:1.5px solid #2563eb; background:#eff6ff; line-height:1.2; cursor:pointer; border-radius:6px; transition:all 0.15s ease; box-shadow:0 1px 3px rgba(37,99,235,0.12);" 
                            onclick="fillLoginUsername('${u.username}')"
                            title="Teacher Account: Click to auto-fill User ID (${u.username})">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span>${u.icon} <strong>${u.role_title}</strong></span>
                            <span style="font-size:0.62rem; background:#2563eb; color:white; padding:1px 5px; border-radius:10px; font-weight:700;">👆 Clickable</span>
                        </div>
                        <span style="font-size:0.68rem; color:#1e40af; font-family:monospace; font-weight:700; display:block; margin-top:2px;">${u.username}</span>
                    </button>
                `;
            } else {
                // NON-TEACHER: USER ID IS SHOWN FOR VERIFICATION, BUT CANNOT BE CLICKED TO AUTO-FILL!
                return `
                    <div class="login-protected-userid-card" 
                         style="font-size:0.73rem; padding:6px 8px; text-align:left; border:1px solid #cbd5e1; background:#f8fafc; line-height:1.2; border-radius:6px; cursor:not-allowed; opacity:0.9;" 
                         onclick="handleNonTeacherClick('${u.username}', '${u.role_title}')"
                         title="Administrative ID: Protected. Click auto-fill disabled. Please type User ID manually.">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <span style="color:#334155;">${u.icon} <strong>${u.role_title}</strong></span>
                            <span style="font-size:0.62rem; background:#e2e8f0; color:#475569; padding:1px 5px; border-radius:10px; font-weight:600;">🔒 Type ID</span>
                        </div>
                        <span style="font-size:0.68rem; color:#64748b; font-family:monospace; display:block; margin-top:2px;">${u.username}</span>
                    </div>
                `;
            }
        }).join('');
    } catch (err) {
        console.error("Failed to load login directory:", err);
    }
}

function handleNonTeacherClick(username, roleTitle) {
    const err = document.getElementById('login-error-msg');
    if (err) {
        err.innerHTML = `🔒 <strong>Security Policy:</strong> Only <strong>Teacher</strong> accounts can be clicked to auto-fill User ID.<br>As an administrative account (<strong>${username}</strong>), please type your User ID manually into the box below.`;
        err.style.display = 'block';
        err.className = 'login-alert';
        err.style.background = '#fef2f2';
        err.style.color = '#991b1b';
        err.style.border = '1px solid #fecaca';
    }
    const usr = document.getElementById('login-username');
    if (usr) {
        usr.value = ''; // Strictly do NOT auto-fill administrative usernames
        usr.focus();
    }
}

async function confirmDeleteUser(userId, username) {
    if (username === 'Owner(Directer)' || username === 'GS_itsupport') {
        alert("⚠️ Protected Core Account: The Director (Owner) and IT Support Administrator IDs cannot be deleted.");
        return;
    }

    const confirmMsg = `Are you sure you want to permanently delete User ID '${username}'?\\n\\n• This account will no longer be able to log in.\\n• The User ID will be immediately removed from the Login Page Directory.`;
    if (!confirm(confirmMsg)) return;

    try {
        const res = await fetch('/api/users/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, username: username })
        }).then(r => r.json());

        if (res.success) {
            alert(`✓ ${res.message}`);
            if (typeof renderUsersTab === 'function') renderUsersTab();
            if (typeof loadLoginDirectory === 'function') loadLoginDirectory();
        } else {
            alert(`❌ Error: ${res.error || res.message || 'Failed to delete user ID.'}`);
        }
    } catch (err) {
        alert(`❌ Network or server error while deleting user ID: ${err.message}`);
    }
}"""

assert target_open_login in code, "target_open_login not found in app.js"
code = code.replace(target_open_login, replacement_open_login, 1)

# 2. Add Delete ID button in renderUsersTab
target_user_actions = """<button class="btn btn-outline btn-sm" style="font-size:0.73rem; padding:3px 8px; color:#2563eb; border-color:#93c5fd;" onclick="showTab('credentials')">
                                                    🔐 IT & Owner Credential Desk
                                                </button>"""

replacement_user_actions = """<button class="btn btn-outline btn-sm" style="font-size:0.73rem; padding:3px 8px; color:#2563eb; border-color:#93c5fd;" onclick="showTab('credentials')">
                                                    🔐 IT & Owner Credential Desk
                                                </button>
                                                ${(!['Owner(Directer)', 'GS_itsupport'].includes(u.username)) ? `
                                                    <button class="btn btn-danger btn-sm" style="font-size:0.73rem; padding:3px 8px; background:#dc2626; border-color:#b91c1c; color:white;" onclick="confirmDeleteUser(${u.id}, '${u.username}')" title="Delete User ID permanently">
                                                        🗑️ Delete ID
                                                    </button>
                                                ` : ''}"""

assert target_user_actions in code, "target_user_actions not found in app.js"
code = code.replace(target_user_actions, replacement_user_actions, 1)

# 3. Call loadLoginDirectory on DOMContentLoaded
target_dom = """    handleHashNavigation();
    window.addEventListener('hashchange', handleHashNavigation);"""

replacement_dom = """    handleHashNavigation();
    window.addEventListener('hashchange', handleHashNavigation);
    if (typeof loadLoginDirectory === 'function') {
        loadLoginDirectory();
    }"""

assert target_dom in code, "target_dom not found in app.js"
code = code.replace(target_dom, replacement_dom, 1)

# 4. In submitCreateUser, call loadLoginDirectory()
target_create_user = """            closeModal('modal-create-user');
            e.target.reset();
            renderUsersTab();"""

replacement_create_user = """            closeModal('modal-create-user');
            e.target.reset();
            renderUsersTab();
            if (typeof loadLoginDirectory === 'function') loadLoginDirectory();"""

if target_create_user in code:
    code = code.replace(target_create_user, replacement_create_user, 1)

# 5. In submitAddTeacher, call loadLoginDirectory()
target_add_teacher = """            closeModal('modal-add-teacher');
            renderTeachersTab();
            loadInitialData();"""

replacement_add_teacher = """            closeModal('modal-add-teacher');
            renderTeachersTab();
            loadInitialData();
            if (typeof loadLoginDirectory === 'function') loadLoginDirectory();"""

if target_add_teacher in code:
    code = code.replace(target_add_teacher, replacement_add_teacher, 1)

# 6. In confirmDeleteTeacher, call loadLoginDirectory()
target_del_teacher = """            renderTeachersTab();
            loadInitialData();"""

replacement_del_teacher = """            renderTeachersTab();
            loadInitialData();
            if (typeof loadLoginDirectory === 'function') loadLoginDirectory();"""

if target_del_teacher in code:
    code = code.replace(target_del_teacher, replacement_del_teacher, 1)

# 7. In seedFacultyDemo, call loadLoginDirectory()
target_seed = """            renderUsersTab();
        } else {"""

replacement_seed = """            renderUsersTab();
            if (typeof loadLoginDirectory === 'function') loadLoginDirectory();
        } else {"""

if target_seed in code:
    code = code.replace(target_seed, replacement_seed, 1)

with open('school_website/js/app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ app.js successfully patched with dynamic login directory and user deletion!")
