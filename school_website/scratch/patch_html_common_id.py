with open('school_website/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html_norm = html.replace('\r\n', '\n')

# 1. Update modal-create-user
old_create_role = """                        <div class="form-group">
                            <label class="form-label">Account Role *</label>
                            <select id="create-user-role" class="form-control" required>
                                <option value="it_admin">💻 IT Support Administrator (Top-Level Role)</option>
                                <option value="teacher">👨‍🏫 Faculty / Teacher</option>
                                <option value="accountant">💰 Accountant</option>
                                <option value="admin">🛡️ Principal (Administrator)</option>
                                <option value="librarian">📚 Librarian</option>
                                <option value="student">🎓 Student</option>
                                <option value="parent">👨‍👩‍👧 Parent</option>
                            </select>
                        </div>"""

new_create_role = """                        <div class="form-group">
                            <label class="form-label">Account Role *</label>
                            <select id="create-user-role" class="form-control" required onchange="handleCreateUserRoleChange(this.value)">
                                <option value="common_id">🏷️ Common ID (Lab Fleet / Shared Account)</option>
                                <option value="it_admin">💻 IT Support Administrator (Top-Level Role)</option>
                                <option value="teacher">👨‍🏫 Faculty / Teacher</option>
                                <option value="accountant">💰 Accountant</option>
                                <option value="admin">🛡️ Principal (Administrator)</option>
                                <option value="librarian">📚 Librarian</option>
                                <option value="student">🎓 Student</option>
                                <option value="parent">👨‍👩‍👧 Parent</option>
                            </select>
                        </div>"""

if old_create_role in html_norm:
    html_norm = html_norm.replace(old_create_role, new_create_role)
    print("Updated create-user-role in index.html")
else:
    print("old_create_role not found!")

old_create_common_fields = """                        <div id="create-user-common-fields" style="display:none; margin-top:10px;">
                            <div class="form-group" style="margin-bottom:6px;">
                                <label class="form-label">Common ID Name *</label>
                                <input type="text" id="create-user-common-name" class="form-control" placeholder="e.g. Computer Teacher Lab Fleet / Lab 1 & 2">
                            </div>
                            <div style="font-size:0.75rem; color:#dc2626; font-weight:600;">
                                📭 Common ID Policy: Common IDs have <strong>NO mail services</strong> (email notifications disabled).
                            </div>
                        </div>"""

new_create_common_fields = """                        <div id="create-user-common-fields" style="display:none; margin-top:10px;">
                            <div class="form-grid">
                                <div class="form-group" style="margin-bottom:6px;">
                                    <label class="form-label">Common ID Name *</label>
                                    <input type="text" id="create-user-common-name" class="form-control" placeholder="e.g. Computer Lab 1 Fleet (Common ID)">
                                </div>
                                <div class="form-group" style="margin-bottom:6px;">
                                    <label class="form-label">👑 Assigned Admin / In-Charge ID for this Common ID *</label>
                                    <select id="create-user-admin-id" class="form-control">
                                        <option value="">— Select Admin ID (e.g. Computer Teacher GS_teacher) —</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-group" style="margin-bottom:6px;">
                                <label class="form-label">🖥️ Assign Computer Lab Workstations to this Common ID</label>
                                <select id="create-user-lab-fleet" class="form-control">
                                    <option value="none">No Workstations Fleet</option>
                                    <option value="lab1">Computer Lab 1 (50 Computers: PC-01 to PC-50)</option>
                                    <option value="lab2">Computer Lab 2 (50 Computers: PC-51 to PC-100)</option>
                                    <option value="both">Both Computer Labs (100 Computers: Lab 1 & 2)</option>
                                </select>
                            </div>
                            <div style="font-size:0.75rem; color:#dc2626; font-weight:600;">
                                📭 Common ID Policy: Common IDs have <strong>NO mail services</strong> (email notifications disabled).
                            </div>
                        </div>"""

if old_create_common_fields in html_norm:
    html_norm = html_norm.replace(old_create_common_fields, new_create_common_fields)
    print("Updated create-user-common-fields in index.html")
else:
    print("old_create_common_fields not found!")

# 2. Update modal-assign-user-role
old_assign_role_select = """                        <div class="form-group">
                            <label class="form-label">Assigned Role *</label>
                            <select id="assign-role-role" class="form-control" required>
                                <option value="it_admin">💻 IT Support Administrator (Top-Level Role)</option>
                                <option value="super_admin">👑 Super Admin</option>
                                <option value="admin">🛡️ Principal (Admin)</option>
                                <option value="teacher">👨‍🏫 Faculty / Teacher</option>
                                <option value="accountant">💰 Accountant</option>
                                <option value="librarian">📚 Librarian</option>
                                <option value="student">🎓 Student</option>
                                <option value="parent">👨‍👩‍👧 Parent</option>
                            </select>
                        </div>"""

new_assign_role_select = """                        <div class="form-group">
                            <label class="form-label">Assigned Role *</label>
                            <select id="assign-role-role" class="form-control" required onchange="handleAssignRoleRoleChange(this.value)">
                                <option value="common_id">🏷️ Common ID (Lab Fleet / Shared Account)</option>
                                <option value="it_admin">💻 IT Support Administrator (Top-Level Role)</option>
                                <option value="super_admin">👑 Super Admin</option>
                                <option value="admin">🛡️ Principal (Admin)</option>
                                <option value="teacher">👨‍🏫 Faculty / Teacher</option>
                                <option value="accountant">💰 Accountant</option>
                                <option value="librarian">📚 Librarian</option>
                                <option value="student">🎓 Student</option>
                                <option value="parent">👨‍👩‍👧 Parent</option>
                            </select>
                        </div>"""

if old_assign_role_select in html_norm:
    html_norm = html_norm.replace(old_assign_role_select, new_assign_role_select)
    print("Updated assign-role-role in index.html")
else:
    print("old_assign_role_select not found!")

old_assign_common_fields = """                        <div id="assign-role-common-fields" style="display:none; margin-top:10px;">
                            <div class="form-group" style="margin-bottom:8px;">
                                <label class="form-label">Common ID Name</label>
                                <input type="text" id="assign-role-common-name" class="form-control" placeholder="e.g. Computer Teacher Lab Fleet">
                            </div>
                            <div class="form-group" style="margin-bottom:4px;">
                                <label class="form-label">Assign Lab Fleet to this ID</label>
                                <select id="assign-role-lab-fleet" class="form-control">
                                    <option value="none">No Lab Fleet</option>
                                    <option value="both" selected>Both Labs (Computer Lab 1 & 2 - 100 Computers)</option>
                                    <option value="lab1">Computer Lab 1 (50 Computers)</option>
                                    <option value="lab2">Computer Lab 2 (50 Computers)</option>
                                </select>
                            </div>
                            <div style="font-size:0.74rem; color:#dc2626; font-weight:600; margin-top:4px;">
                                📭 Common ID Policy: Common IDs have <strong>NO mail services</strong>.
                            </div>
                        </div>"""

new_assign_common_fields = """                        <div id="assign-role-common-fields" style="display:none; margin-top:10px;">
                            <div class="form-grid">
                                <div class="form-group" style="margin-bottom:8px;">
                                    <label class="form-label">Common ID Name</label>
                                    <input type="text" id="assign-role-common-name" class="form-control" placeholder="e.g. Computer Lab 1 Fleet (Common ID)">
                                </div>
                                <div class="form-group" style="margin-bottom:8px;">
                                    <label class="form-label">👑 Assigned Admin / In-Charge ID</label>
                                    <select id="assign-role-admin-id" class="form-control">
                                        <option value="">— Select Admin ID (e.g. Computer Teacher GS_teacher) —</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-group" style="margin-bottom:4px;">
                                <label class="form-label">Assign Lab Fleet to this ID</label>
                                <select id="assign-role-lab-fleet" class="form-control">
                                    <option value="none">No Lab Fleet</option>
                                    <option value="both" selected>Both Labs (Computer Lab 1 & 2 - 100 Computers)</option>
                                    <option value="lab1">Computer Lab 1 (50 Computers)</option>
                                    <option value="lab2">Computer Lab 2 (50 Computers)</option>
                                </select>
                            </div>
                            <div style="font-size:0.74rem; color:#dc2626; font-weight:600; margin-top:4px;">
                                📭 Common ID Policy: Common IDs have <strong>NO mail services</strong>.
                            </div>
                        </div>"""

if old_assign_common_fields in html_norm:
    html_norm = html_norm.replace(old_assign_common_fields, new_assign_common_fields)
    print("Updated assign-role-common-fields in index.html")
else:
    print("old_assign_common_fields not found!")

# 3. Update modal-it-request-create-user
old_it_create_role = """                        <div class="form-group">
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
                        </div>"""

new_it_create_role = """                        <div class="form-group">
                            <label class="form-label">Account Role *</label>
                            <select id="it-create-role" class="form-control" required onchange="handleITCreateUserRoleChange(this.value)">
                                <option value="common_id">🏷️ Common ID (Lab Fleet / Shared Account)</option>
                                <option value="teacher">👨‍🏫 Faculty / Teacher</option>
                                <option value="accountant">💰 Accountant</option>
                                <option value="librarian">📚 Librarian</option>
                                <option value="admin">🛡️ Principal (Admin)</option>
                                <option value="it_admin">💻 IT Support Administrator</option>
                                <option value="student">🎓 Student</option>
                                <option value="parent">👨‍👩‍👧 Parent</option>
                            </select>
                        </div>"""

if old_it_create_role in html_norm:
    html_norm = html_norm.replace(old_it_create_role, new_it_create_role)
    print("Updated it-create-role in index.html")
else:
    print("old_it_create_role not found!")

# Insert Common ID block in modal-it-request-create-user right after gender
old_it_gender = """                        <small id="it-create-gender-hint" style="font-size:0.73rem; color:#64748b;">🔒 Disabled: Provide person's name to assign gender.</small>
                    </div>
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Proposed User ID / Username *</label>"""

new_it_gender = """                        <small id="it-create-gender-hint" style="font-size:0.73rem; color:#64748b;">🔒 Disabled: Provide person's name to assign gender.</small>
                    </div>

                    <!-- Common ID Option for IT Support Creation -->
                    <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:12px 14px; margin-bottom:14px;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <label class="form-label" style="display:flex; align-items:center; gap:8px; margin-bottom:0; cursor:pointer;">
                                <input type="checkbox" id="it-create-is-common" onchange="toggleITCreateUserCommon(this.checked)">
                                <strong>🏷️ Assign as Common ID (Shared / Lab Fleet Account)</strong>
                            </label>
                            <span class="badge" id="it-create-mail-badge" style="background:#dcfce7; color:#15803d; font-size:0.7rem; font-weight:700;">
                                ✉️ Standard Mail Service
                            </span>
                        </div>
                        <div id="it-create-common-fields" style="display:none; margin-top:10px;">
                            <div class="form-grid">
                                <div class="form-group" style="margin-bottom:6px;">
                                    <label class="form-label">Common ID Name *</label>
                                    <input type="text" id="it-create-common-name" class="form-control" placeholder="e.g. Computer Lab 1 Fleet (Common ID)">
                                </div>
                                <div class="form-group" style="margin-bottom:6px;">
                                    <label class="form-label">👑 Assigned Admin / In-Charge ID for this Common ID *</label>
                                    <select id="it-create-admin-id" class="form-control">
                                        <option value="">— Select Admin ID (e.g. Computer Teacher GS_teacher) —</option>
                                    </select>
                                </div>
                            </div>
                            <div class="form-group" style="margin-bottom:6px;">
                                <label class="form-label">🖥️ Assign Computer Lab Workstations to this Common ID</label>
                                <select id="it-create-lab-fleet" class="form-control">
                                    <option value="none">No Workstations Fleet</option>
                                    <option value="lab1">Computer Lab 1 (50 Computers: PC-01 to PC-50)</option>
                                    <option value="lab2">Computer Lab 2 (50 Computers: PC-51 to PC-100)</option>
                                    <option value="both">Both Computer Labs (100 Computers: Lab 1 & 2)</option>
                                </select>
                            </div>
                            <div style="font-size:0.75rem; color:#dc2626; font-weight:600;">
                                📭 Common ID Policy: Common IDs have <strong>NO mail services</strong> (email notifications disabled).
                            </div>
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Proposed User ID / Username *</label>"""

if old_it_gender in html_norm:
    html_norm = html_norm.replace(old_it_gender, new_it_gender)
    print("Inserted Common ID fields into modal-it-request-create-user in index.html")
else:
    print("old_it_gender not found!")

with open('school_website/index.html', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(html_norm)
print("Saved patched index.html")
