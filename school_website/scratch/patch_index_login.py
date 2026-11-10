with open('school_website/index.html', 'r', encoding='utf-8') as f:
    code = f.read()

target = """<!-- Staff Usernames Directory (User ID List - Passwords are Confidential and Not Shown) -->
                <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:10px; padding:12px 14px; margin-bottom:18px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-size:0.75rem; font-weight:800; color:#1e293b; text-transform:uppercase; letter-spacing:0.5px;">
                            <i class="fas fa-id-badge" style="color:#2563eb;"></i> Staff User ID Directory
                        </span>
                        <span style="font-size:0.7rem; color:#64748b;">Click to fill User ID (Password required)</span>
                    </div>
                    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:6px;">
                        <button type="button" class="btn btn-outline btn-sm" style="font-size:0.73rem; padding:6px 8px; text-align:left; border-color:#cbd5e1; background:#fff; line-height:1.2; cursor:pointer;" onclick="fillLoginUsername('Owner(Directer)')">
                            👑 <strong>Owner (Director)</strong><br><span style="font-size:0.67rem; color:#1e40af; font-family:monospace;">Owner(Directer)</span>
                        </button>
                        <button type="button" class="btn btn-outline btn-sm" style="font-size:0.73rem; padding:6px 8px; text-align:left; border-color:#cbd5e1; background:#fff; line-height:1.2; cursor:pointer;" onclick="fillLoginUsername('GS_superadmin')">
                            👑 <strong>Super Admin</strong><br><span style="font-size:0.67rem; color:#1e40af; font-family:monospace;">GS_superadmin</span>
                        </button>
                        <button type="button" class="btn btn-outline btn-sm" style="font-size:0.73rem; padding:6px 8px; text-align:left; border-color:#cbd5e1; background:#fff; line-height:1.2; cursor:pointer;" onclick="fillLoginUsername('GS_admin')">
                            🛡️ <strong>Principal (Admin)</strong><br><span style="font-size:0.67rem; color:#1e40af; font-family:monospace;">GS_admin</span>
                        </button>
                        <button type="button" class="btn btn-outline btn-sm" style="font-size:0.73rem; padding:6px 8px; text-align:left; border-color:#cbd5e1; background:#fff; line-height:1.2; cursor:pointer;" onclick="fillLoginUsername('GS_accountant')">
                            💰 <strong>Accountant</strong><br><span style="font-size:0.67rem; color:#1e40af; font-family:monospace;">GS_accountant</span>
                        </button>
                        <button type="button" class="btn btn-outline btn-sm" style="font-size:0.73rem; padding:6px 8px; text-align:left; border-color:#cbd5e1; background:#fff; line-height:1.2; cursor:pointer;" onclick="fillLoginUsername('GS_teacher')">
                            👨‍🏫 <strong>Teacher Chike</strong><br><span style="font-size:0.67rem; color:#1e40af; font-family:monospace;">GS_teacher</span>
                        </button>
                        <button type="button" class="btn btn-outline btn-sm" style="font-size:0.73rem; padding:6px 8px; text-align:left; border-color:#cbd5e1; background:#fff; line-height:1.2; cursor:pointer;" onclick="fillLoginUsername('GS_itsupport')">
                            💻 <strong>IT Administrator</strong><br><span style="font-size:0.67rem; color:#1e40af; font-family:monospace;">GS_itsupport</span>
                        </button>
                        <button type="button" class="btn btn-outline btn-sm" style="font-size:0.73rem; padding:6px 8px; text-align:left; border-color:#cbd5e1; background:#fff; line-height:1.2; cursor:pointer;" onclick="fillLoginUsername('GS_librarian')">
                            📚 <strong>Librarian</strong><br><span style="font-size:0.67rem; color:#1e40af; font-family:monospace;">GS_librarian</span>
                        </button>
                    </div>
                    <div style="margin-top:8px; font-size:0.7rem; color:#64748b; line-height:1.3;">
                        🔒 <em>Passwords are confidential and never displayed on portal. Please type your password below.</em>
                        <br>👨‍👩‍👧 <strong>Parents:</strong> Log in with your unique Parent User ID (e.g. <code>GS_parent_Alex_and_Clara</code>) to manage all enrolled children.
                    </div>
                </div>"""

replacement = """<!-- Live Staff Usernames Directory (Dynamic from Database: Deletions auto-remove, new IDs auto-appear, ONLY Teachers can click) -->
                <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:10px; padding:12px 14px; margin-bottom:18px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px; flex-wrap:wrap; gap:4px;">
                        <span style="font-size:0.75rem; font-weight:800; color:#1e293b; text-transform:uppercase; letter-spacing:0.5px;">
                            <i class="fas fa-id-badge" style="color:#2563eb;"></i> Live User ID Directory
                        </span>
                        <span style="font-size:0.7rem; background:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:4px; font-weight:600;">
                            ✨ Only Teacher User IDs can be clicked
                        </span>
                    </div>

                    <div id="login-staff-directory" style="display:grid; grid-template-columns:repeat(auto-fit, minmax(130px, 1fr)); gap:6px;">
                        <!-- Dynamic User ID Cards Loaded Live via loadLoginDirectory() -->
                        <div style="font-size:0.75rem; color:#64748b; padding:10px; text-align:center; grid-column:1/-1;">
                            <i class="fas fa-spinner fa-spin"></i> Loading live user directory...
                        </div>
                    </div>

                    <div style="margin-top:10px; font-size:0.7rem; color:#64748b; line-height:1.35; border-top:1px dashed #cbd5e1; padding-top:8px;">
                        🔒 <strong>Access & Security Policy:</strong> Only <strong>Teacher</strong> accounts are clickable to auto-fill User ID. Administrative and Management accounts (Director, Admin, Accountant, IT Support) are displayed for verification and must be typed manually into the field below.
                        <br>👨‍👩‍👧 <strong>Parents:</strong> Log in with your unique Parent User ID (e.g. <code>GS_parent_Alex_and_Clara</code>) to manage all enrolled children.
                    </div>
                </div>"""

assert target in code, "Target block not found in index.html"
code = code.replace(target, replacement, 1)

with open('school_website/index.html', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ index.html successfully updated with dynamic login directory container!")
