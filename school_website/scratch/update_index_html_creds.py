# Update index.html for Credential Management, removing forgot password, adding credentials tab and modals
import sys

with open('school_website/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. In login form: Remove forgot-password link, replace with IT Support security notice
old_login_forgot = """                        <a href="javascript:void(0)" onclick="openForgotPasswordModal()" style="color:#2563eb; text-decoration:none; font-weight:700;">
                            🔑 Forgot Password?
                        </a>"""

new_login_forgot = """                        <span style="font-size:0.78rem; color:#64748b; display:inline-flex; align-items:center; gap:4px;">
                            <i class="fas fa-shield-alt" style="color:#2563eb;"></i> Need credentials? Contact <strong>IT Support</strong>
                        </span>"""

if old_login_forgot in html:
    html = html.replace(old_login_forgot, new_login_forgot)
    print("1. Replaced forgot password link on login form")
else:
    print("WARNING: login forgot password link not found")

# 2. In sidebar: Add credentials tab item
old_sidebar_users = """                    <li data-tab="users">
                        <a href="javascript:void(0)" data-tab="users" onclick="showTab('users')" style="color:#fde047; font-weight:700;">
                            <span>🔑</span> Manage Users & Passwords
                        </a>
                    </li>"""

new_sidebar_users = """                    <li data-tab="users">
                        <a href="javascript:void(0)" data-tab="users" onclick="showTab('users')" style="color:#fde047; font-weight:700;">
                            <span>👑</span> Manage Users & Governance
                        </a>
                    </li>
                    <li data-tab="credentials">
                        <a href="javascript:void(0)" data-tab="credentials" onclick="showTab('credentials')" style="color:#60a5fa; font-weight:700;">
                            <span>🔐</span> User IDs & Passwords
                        </a>
                    </li>"""

if old_sidebar_users in html:
    html = html.replace(old_sidebar_users, new_sidebar_users)
    print("2. Added credentials tab item to sidebar-nav")
else:
    print("WARNING: sidebar users not found")

# 3. Add admission approval note to modal-admit-student
old_modal_admit_header = """            <form onsubmit="submitAdmitStudent(event)">
                <div class="modal-body">
                    <div class="form-group">
                        <label class="form-label">Student Full Name *</label>"""

new_modal_admit_header = """            <form onsubmit="submitAdmitStudent(event)">
                <div class="modal-body">
                    <div class="form-group" style="background:#f0fdf4; border:1px solid #bbf7d0; padding:10px 14px; border-radius:8px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <span style="font-weight:700; color:#166534; font-size:0.85rem;"><i class="fas fa-user-check"></i> Admission Status:</span>
                            <div style="font-size:0.75rem; color:#15803d; margin-top:2px;">Student data added by Admin / Super Admin will be automatically approved for new admission.</div>
                        </div>
                        <span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700; padding:4px 10px; border-radius:6px;">
                            ✓ Approved for New Admission
                        </span>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Student Full Name *</label>"""

if old_modal_admit_header in html:
    html = html.replace(old_modal_admit_header, new_modal_admit_header)
    print("3. Added admission status banner to modal-admit-student")
else:
    print("WARNING: modal-admit-student header not found")

# 4. Add new IT Support Credential Change & Create Modals before <script src="js/app.js">
new_credential_modals = """
    <!-- Modal: IT Support Propose User ID / Password Change (Requires Owner Approval) -->
    <div id="modal-it-request-change-creds" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header" style="background:#1e3a8a; color:white;">
                <div>
                    <h3 class="modal-title" style="color:white;"><i class="fas fa-key"></i> Modify User ID & Password (IT Support Desk)</h3>
                    <p style="font-size:0.78rem; color:#bfdbfe; margin-top:2px;">Dispatches credential update request to Owner (Director) Rajeev Sinha for final executive approval</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-it-request-change-creds')" style="color:white;">&times;</button>
            </div>
            <form onsubmit="submitITSupportChangeCreds(event)">
                <div class="modal-body">
                    <input type="hidden" id="it-cred-user-id">
                    <div class="form-group">
                        <div id="it-cred-target-info" style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:12px 14px; font-size:0.85rem;">
                            <!-- Target user info populated dynamically -->
                        </div>
                    </div>
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Proposed New User ID / Username *</label>
                            <input type="text" id="it-cred-new-username" class="form-control" required style="font-family:monospace; font-weight:700;">
                        </div>
                        <div class="form-group">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                <label class="form-label" style="margin-bottom:0;">Proposed New Password *</label>
                                <button type="button" class="btn btn-outline btn-sm" style="padding:2px 8px; font-size:0.72rem;" onclick="generateStrongPassword('it-cred-new-password')">
                                    🎲 Auto
                                </button>
                            </div>
                            <input type="text" id="it-cred-new-password" class="form-control" required style="font-family:monospace; font-weight:700;">
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Reason / Justification for Change *</label>
                        <textarea id="it-cred-reason" class="form-control" rows="2" required placeholder="e.g. User requested password refresh; approved role reassignment, etc."></textarea>
                    </div>
                    <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:6px; padding:10px 14px; font-size:0.8rem; color:#1e40af;">
                        🔒 <strong>Security Policy:</strong> Passwords and User IDs can only be changed by IT Support with Owner (Director) approval. This request will be submitted to <strong>Owner (Director) Rajeev Sinha</strong> for review and executive approval.
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-it-request-change-creds')">Cancel</button>
                    <button type="submit" class="btn btn-primary" style="background:#1e3a8a; font-weight:700;">🚀 Submit for Owner Approval</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal: IT Support Propose New User ID Creation (Requires Owner Approval) -->
    <div id="modal-it-request-create-user" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header" style="background:linear-gradient(135deg, #1e3a8a, #0f172a); color:white;">
                <div>
                    <h3 class="modal-title" style="color:white;"><i class="fas fa-user-plus"></i> Propose New User ID (IT Support Desk)</h3>
                    <p style="font-size:0.78rem; color:#bfdbfe; margin-top:2px;">Dispatches new account creation request to Owner (Director) Rajeev Sinha for final executive approval</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-it-request-create-user')" style="color:white;">&times;</button>
            </div>
            <form onsubmit="submitITSupportCreateUser(event)">
                <div class="modal-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Assigned Person's Name</label>
                            <input type="text" id="it-create-name" class="form-control" placeholder="Leave blank if unassigned role ID" oninput="handleITCreateUserNameChange(this.value)">
                            <small style="font-size:0.73rem; color:#64748b;">(Rule: If unassigned, ID will carry no gender)</small>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Account Role *</label>
                            <select id="it-create-role" class="form-control" required>
                                <option value="teacher">👨‍🏫 Faculty / Teacher</option>
                                <option value="accountant">💰 Accountant</option>
                                <option value="librarian">📚 Librarian</option>
                                <option value="admin">🛡️ Principal (Admin)</option>
                                <option value="it_admin">💻 IT Support Administrator</option>
                                <option value="student">🎓 Student</option>
                                <option value="parent">👨‍👩‍👧 Parent</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Gender (Rule: Disabled if unassigned)</label>
                        <select id="it-create-gender" class="form-control" disabled>
                            <option value="">— No Gender (Unassigned ID) —</option>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                        </select>
                        <small id="it-create-gender-hint" style="font-size:0.73rem; color:#64748b;">🔒 Disabled: Provide person's name to assign gender.</small>
                    </div>
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Proposed User ID / Username *</label>
                            <input type="text" id="it-create-username" class="form-control" required placeholder="e.g. GS_teacher_math" style="font-family:monospace; font-weight:700;">
                        </div>
                        <div class="form-group">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                <label class="form-label" style="margin-bottom:0;">Proposed Password *</label>
                                <button type="button" class="btn btn-outline btn-sm" style="padding:2px 8px; font-size:0.72rem;" onclick="generateStrongPassword('it-create-password')">
                                    🎲 Auto
                                </button>
                            </div>
                            <input type="text" id="it-create-password" class="form-control" required placeholder="e.g. Greenland@2026" style="font-family:monospace; font-weight:700;">
                        </div>
                    </div>
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Email Address</label>
                            <input type="email" id="it-create-email" class="form-control" placeholder="user@greenlandschool.net">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Phone Number</label>
                            <input type="text" id="it-create-phone" class="form-control" placeholder="+91 761 700 5055">
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Reason / Justification for Account Creation *</label>
                        <textarea id="it-create-reason" class="form-control" rows="2" required placeholder="e.g. Newly hired Computer Science faculty member joining Greenland School."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-it-request-create-user')">Cancel</button>
                    <button type="submit" class="btn btn-primary" style="background:#1e3a8a; font-weight:700;">👑 Submit for Owner Approval</button>
                </div>
            </form>
        </div>
    </div>
"""

script_tag = '    <!-- Application Scripts -->'
if script_tag in html:
    html = html.replace(script_tag, new_credential_modals + "\n" + script_tag)
    print("4. Added IT Support credential modals before application scripts")
else:
    print("WARNING: script tag not found")

with open('school_website/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("index.html updated successfully!")
