import sys

with open('school_website/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update Staff User ID Directory on login page
# Add GS_itsupport button right before GS_librarian or right after
old_login_btn = """                        <button type="button" class="btn btn-outline btn-sm" style="font-size:0.73rem; padding:6px 8px; text-align:left; border-color:#cbd5e1; background:#fff; line-height:1.2; cursor:pointer;" onclick="fillLoginUsername('GS_librarian')">
                            📚 <strong>Librarian</strong><br><span style="font-size:0.67rem; color:#1e40af; font-family:monospace;">GS_librarian</span>
                        </button>"""

new_login_btn = """                        <button type="button" class="btn btn-outline btn-sm" style="font-size:0.73rem; padding:6px 8px; text-align:left; border-color:#cbd5e1; background:#fff; line-height:1.2; cursor:pointer;" onclick="fillLoginUsername('GS_itsupport')">
                            💻 <strong>IT Administrator</strong><br><span style="font-size:0.67rem; color:#1e40af; font-family:monospace;">GS_itsupport</span>
                        </button>
                        <button type="button" class="btn btn-outline btn-sm" style="font-size:0.73rem; padding:6px 8px; text-align:left; border-color:#cbd5e1; background:#fff; line-height:1.2; cursor:pointer;" onclick="fillLoginUsername('GS_librarian')">
                            📚 <strong>Librarian</strong><br><span style="font-size:0.67rem; color:#1e40af; font-family:monospace;">GS_librarian</span>
                        </button>"""

if old_login_btn in content:
    content = content.replace(old_login_btn, new_login_btn)
    print("1. Updated login buttons with GS_itsupport")
else:
    print("WARNING: login button not found")

# 2. Add lab_manager and lab_complaints to sidebar-nav
old_sidebar_lib = """                    <li data-tab="library">
                        <a href="javascript:void(0)" data-tab="library" onclick="showTab('library')">
                            <span>📚</span> E-Library Books
                        </a>
                    </li>"""

new_sidebar_lib = """                    <li data-tab="library">
                        <a href="javascript:void(0)" data-tab="library" onclick="showTab('library')">
                            <span>📚</span> E-Library Books
                        </a>
                    </li>
                    <li data-tab="lab_manager">
                        <a href="javascript:void(0)" data-tab="lab_manager" onclick="showTab('lab_manager')">
                            <span>🖥️</span> Computer Lab & Devices
                        </a>
                    </li>
                    <li data-tab="lab_complaints">
                        <a href="javascript:void(0)" data-tab="lab_complaints" onclick="showTab('lab_complaints')">
                            <span>🛠️</span> Lab Complaints & Repairs
                        </a>
                    </li>"""

if old_sidebar_lib in content:
    content = content.replace(old_sidebar_lib, new_sidebar_lib)
    print("2. Added lab_manager and lab_complaints to sidebar-nav")
else:
    print("WARNING: sidebar library not found")

# 3. Update modal-create-user to support it_admin role and Gender rule (no name = no gender)
old_modal_create_user = """    <!-- Create New User Modal -->
    <div id="modal-create-user" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header">
                <h3 class="modal-title">➕ Create New User Account</h3>
                <button class="modal-close" onclick="closeModal('modal-create-user')">&times;</button>
            </div>
            <form onsubmit="submitCreateUser(event)">
                <div class="modal-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Full Name *</label>
                            <input type="text" id="create-user-name" class="form-control" required placeholder="e.g. Samuel Ade">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Account Role *</label>
                            <select id="create-user-role" class="form-control" required>
                                <option value="student">Student</option>
                                <option value="teacher">Teacher</option>
                                <option value="admin">Administrator</option>
                                <option value="parent">Parent</option>
                                <option value="accountant">Accountant</option>
                                <option value="librarian">Librarian</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Unique User ID / Username *</label>
                            <input type="text" id="create-user-username" class="form-control" required placeholder="e.g. std_samuel" style="font-family:monospace;">
                        </div>
                        <div class="form-group">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                <label class="form-label" style="margin-bottom:0;">Password *</label>
                                <button type="button" class="btn btn-outline btn-sm" style="padding:2px 8px; font-size:0.72rem;" onclick="generateStrongPassword('create-user-password')">
                                    🎲 Auto
                                </button>
                            </div>
                            <input type="text" id="create-user-password" class="form-control" required placeholder="e.g. Student#2026" style="font-family:monospace;">
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Email Address</label>
                            <input type="email" id="create-user-email" class="form-control" placeholder="user@greenlandschool.net">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Phone</label>
                            <input type="text" id="create-user-phone" class="form-control" placeholder="+91 761 700 5055">
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-create-user')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Create Account</button>
                </div>
            </form>
        </div>
    </div>"""

new_modal_create_user = """    <!-- Create New User Modal (Director Master Authority) -->
    <div id="modal-create-user" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header">
                <div>
                    <h3 class="modal-title">👑➕ Create User ID & Role (Director Authority)</h3>
                    <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Director creates user IDs and assigns roles. If no person name is assigned, no gender is shown.</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-create-user')">&times;</button>
            </div>
            <form onsubmit="submitCreateUser(event)">
                <div class="modal-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Assigned Person's Full Name</label>
                            <input type="text" id="create-user-name" class="form-control" placeholder="Leave blank if unassigned role ID" oninput="handleCreateUserNameChange(this.value)">
                            <small style="font-size:0.73rem; color:#64748b;">(Optional: if unassigned, ID will carry no gender)</small>
                        </div>
                        <div class="form-group">
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
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Gender (Rule: Disabled if no person name is assigned)</label>
                        <select id="create-user-gender" class="form-control" disabled>
                            <option value="">— No Gender (Unassigned Role ID) —</option>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                        </select>
                        <small id="create-user-gender-hint" style="font-size:0.73rem; color:#64748b;">🔒 Disabled: Provide assigned person's name to set gender.</small>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Unique User ID / Username *</label>
                            <input type="text" id="create-user-username" class="form-control" required placeholder="e.g. GS_faculty_math" style="font-family:monospace;">
                        </div>
                        <div class="form-group">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
                                <label class="form-label" style="margin-bottom:0;">Password *</label>
                                <button type="button" class="btn btn-outline btn-sm" style="padding:2px 8px; font-size:0.72rem;" onclick="generateStrongPassword('create-user-password')">
                                    🎲 Auto
                                </button>
                            </div>
                            <input type="text" id="create-user-password" class="form-control" required placeholder="e.g. Greenland@2026" style="font-family:monospace;">
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Email Address</label>
                            <input type="email" id="create-user-email" class="form-control" placeholder="user@greenlandschool.net">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Phone</label>
                            <input type="text" id="create-user-phone" class="form-control" placeholder="+91 761 700 5055">
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-create-user')">Cancel</button>
                    <button type="submit" class="btn btn-primary">👑 Create User Account</button>
                </div>
            </form>
        </div>
    </div>"""

if old_modal_create_user in content:
    content = content.replace(old_modal_create_user, new_modal_create_user)
    print("3. Updated modal-create-user")
else:
    # Try normalizing CRLF
    content_norm = content.replace('\r\n', '\n')
    old_norm = old_modal_create_user.replace('\r\n', '\n')
    if old_norm in content_norm:
        content_norm = content_norm.replace(old_norm, new_modal_create_user.replace('\r\n', '\n'))
        content = content_norm
        print("3. Updated modal-create-user (after line ending normalization)")
    else:
        print("WARNING: modal-create-user not found")

# 4. Append new modals right before <!-- Application Scripts -->
new_modals = """
    <!-- Modal: Director Assign Role & Person to User ID -->
    <div id="modal-assign-user-role" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header">
                <div>
                    <h3 class="modal-title">🎭 Assign Role & Person to User ID</h3>
                    <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Director Master Privilege: Reassign role, identity, and gender</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-assign-user-role')">&times;</button>
            </div>
            <form onsubmit="submitAssignUserRole(event)">
                <div class="modal-body">
                    <input type="hidden" id="assign-role-user-id">
                    <div class="form-group">
                        <label class="form-label">User ID / Username</label>
                        <input type="text" id="assign-role-username" class="form-control" readonly style="background:#f1f5f9; font-family:monospace; font-weight:700;">
                    </div>
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Assigned Role *</label>
                            <select id="assign-role-role" class="form-control" required>
                                <option value="it_admin">💻 IT Support Administrator (Top-Level Role)</option>
                                <option value="teacher">👨‍🏫 Faculty / Teacher</option>
                                <option value="accountant">💰 Accountant</option>
                                <option value="admin">🛡️ Principal (Admin)</option>
                                <option value="librarian">📚 Librarian</option>
                                <option value="student">🎓 Student</option>
                                <option value="parent">👨‍👩‍👧 Parent</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Assigned Person's Name</label>
                            <input type="text" id="assign-role-person-name" class="form-control" placeholder="Leave blank if unassigned" oninput="handleAssignPersonNameChange(this.value)">
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Gender (Rule: Disabled if unassigned)</label>
                        <select id="assign-role-gender" class="form-control" disabled>
                            <option value="">— No Gender (Unassigned ID) —</option>
                            <option value="Male">Male</option>
                            <option value="Female">Female</option>
                        </select>
                        <small id="assign-role-gender-hint" style="font-size:0.75rem; color:#64748b;">🔒 Disabled: Provide person's name to assign gender.</small>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-assign-user-role')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Role & Identity</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal: Teacher Report Computer Lab Problem -->
    <div id="modal-report-lab-complaint" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header" style="background:#dc2626; color:white;">
                <div>
                    <h3 class="modal-title" style="color:white;"><i class="fas fa-exclamation-triangle"></i> Report Computer Lab Problem</h3>
                    <p style="font-size:0.78rem; color:#fee2e2; margin-top:2px;">Dispatches immediate repair ticket to IT Support Administrator</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-report-lab-complaint')" style="color:white;">&times;</button>
            </div>
            <form onsubmit="submitReportLabComplaint(event)">
                <div class="modal-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Computer Lab *</label>
                            <select id="complaint-lab-name" class="form-control" required onchange="updateComputerOptionsForComplaint()">
                                <option value="Computer Lab 1 (Main Lab)">Computer Lab 1 (Main Lab - 20 PCs)</option>
                                <option value="Computer Lab 2 (Junior Lab)">Computer Lab 2 (Junior Lab - 15 PCs)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Select Faulty Computer (PC Number) *</label>
                            <select id="complaint-pc-number" class="form-control" required>
                                <!-- Populated dynamically from lab computers -->
                            </select>
                        </div>
                    </div>
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Issue Category *</label>
                            <select id="complaint-issue-cat" class="form-control" required>
                                <option value="Hardware / CPU / Power">Hardware / CPU / Not Powering On</option>
                                <option value="Peripherals (Monitor/Keyboard/Mouse)">Peripherals (Monitor / Keyboard / Mouse)</option>
                                <option value="Software / OS Crash / BlueScreen">Software / OS Crash / Blue Screen</option>
                                <option value="Network / Internet Connectivity">Network / Internet Connectivity</option>
                                <option value="Slow Performance / Virus">System Lag / Possible Virus</option>
                                <option value="Other">Other Hardware/Software Problem</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Urgency / Priority *</label>
                            <select id="complaint-priority" class="form-control" required>
                                <option value="High">🔴 High (Lab Class Impeded)</option>
                                <option value="Medium" selected>🟡 Medium (Standard)</option>
                                <option value="Low">🟢 Low (Minor Glitch)</option>
                                <option value="Critical">🔥 Critical (Immediate Action)</option>
                            </select>
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Problem Description & Symptoms *</label>
                        <textarea id="complaint-desc" class="form-control" rows="3" required placeholder="Describe what happens (e.g. PC-04 screen flickers and system restarts repeatedly, mouse cursor frozen)..."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-report-lab-complaint')">Cancel</button>
                    <button type="submit" class="btn btn-danger" style="background:#dc2626; border-color:#b91c1c;">🚨 Dispatch Complaint to IT Support</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal: IT Support Admin Assign Technician to Repair -->
    <div id="modal-assign-lab-repair" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header" style="background:#2563eb; color:white;">
                <div>
                    <h3 class="modal-title" style="color:white;"><i class="fas fa-tools"></i> Assign Technician for Repair</h3>
                    <p style="font-size:0.78rem; color:#bfdbfe; margin-top:2px;">IT Support Administrator Dispatch & Assignment</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-assign-lab-repair')" style="color:white;">&times;</button>
            </div>
            <form onsubmit="submitAssignLabRepair(event)">
                <div class="modal-body">
                    <input type="hidden" id="assign-repair-complaint-id">
                    <div class="form-group">
                        <div id="assign-repair-summary-card" style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:12px 16px; margin-bottom:14px; font-size:0.85rem;">
                            <!-- Filled dynamically -->
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Assign Technician / User to Repair *</label>
                        <select id="assign-repair-technician-name" class="form-control" required>
                            <option value="Ramesh Kumar (Hardware Tech)">Ramesh Kumar (Hardware Tech)</option>
                            <option value="Suresh Verma (Network Engineer)">Suresh Verma (Network Engineer)</option>
                            <option value="Pooja Sharma (Software & OS Specialist)">Pooja Sharma (Software & OS Specialist)</option>
                            <option value="Anand Patel (Peripherals & Lab Assistant)">Anand Patel (Peripherals & Lab Assistant)</option>
                            <option value="IT Support Administrator (Self)">IT Support Administrator (Self)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Repair Instructions / Technician Notes</label>
                        <textarea id="assign-repair-notes" class="form-control" rows="3" placeholder="e.g. Inspect RAM seating, replace display cable or test power supply unit..."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-assign-lab-repair')">Cancel</button>
                    <button type="submit" class="btn btn-primary">🛠️ Assign & Mark In Repair</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal: IT Support Admin Resolve Complaint & Test Computer -->
    <div id="modal-resolve-lab-complaint" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header" style="background:#16a34a; color:white;">
                <div>
                    <h3 class="modal-title" style="color:white;"><i class="fas fa-check-circle"></i> Complete Repair & Mark Computer Operational</h3>
                    <p style="font-size:0.78rem; color:#bbf7d0; margin-top:2px;">IT Support Administrator: Verify resolution and restore PC to Working status</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-resolve-lab-complaint')" style="color:white;">&times;</button>
            </div>
            <form onsubmit="submitResolveLabComplaint(event)">
                <div class="modal-body">
                    <input type="hidden" id="resolve-repair-complaint-id">
                    <div class="form-group">
                        <div id="resolve-repair-summary-card" style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:12px 16px; margin-bottom:14px; font-size:0.85rem;">
                            <!-- Filled dynamically -->
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Resolution Details & Verification Summary *</label>
                        <textarea id="resolve-repair-notes" class="form-control" rows="3" required placeholder="e.g. Replaced faulty RAM module. System rebooted, stress tested, verified 100% operational."></textarea>
                    </div>
                    <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:6px; padding:10px 14px; font-size:0.82rem; color:#1e40af;">
                        ℹ️ <strong>Status Change:</strong> Upon completing this action, the complaint ticket will be marked <strong>Resolved</strong> and this computer will immediately be restored to <strong>Operational (Working)</strong> status in the lab inventory.
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-resolve-lab-complaint')">Cancel</button>
                    <button type="submit" class="btn btn-success" style="background:#16a34a; border-color:#15803d;">✅ Confirm Repair & Restore to Working</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal: Add / Configure Computer in Lab -->
    <div id="modal-add-lab-pc" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header">
                <h3 class="modal-title">🖥️ Add / Update Lab Computer</h3>
                <button class="modal-close" onclick="closeModal('modal-add-lab-pc')">&times;</button>
            </div>
            <form onsubmit="submitAddLabPC(event)">
                <div class="modal-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Lab Location *</label>
                            <select id="pc-lab-name" class="form-control" required>
                                <option value="Computer Lab 1 (Main Lab)">Computer Lab 1 (Main Lab)</option>
                                <option value="Computer Lab 2 (Junior Lab)">Computer Lab 2 (Junior Lab)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">PC Number / Identifier *</label>
                            <input type="text" id="pc-number-val" class="form-control" required placeholder="e.g. PC-36" style="font-family:monospace; font-weight:700;">
                        </div>
                    </div>
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">IP Address</label>
                            <input type="text" id="pc-ip-val" class="form-control" placeholder="192.168.10.136">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Operating System</label>
                            <input type="text" id="pc-os-val" class="form-control" value="Windows 11 Pro">
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Hardware Specifications (Processor & RAM)</label>
                        <input type="text" id="pc-specs-val" class="form-control" value="Intel Core i5-12400 / 16GB RAM / 512GB SSD">
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-add-lab-pc')">Cancel</button>
                    <button type="submit" class="btn btn-primary">Save Computer</button>
                </div>
            </form>
        </div>
    </div>

    <!-- Modal: Director Sanction & Issue Accountant Salary Payslip -->
    <div id="modal-issue-accountant-slip" class="modal-overlay">
        <div class="modal-box">
            <div class="modal-header" style="background:linear-gradient(135deg, #1e3a8a, #0f172a); color:white;">
                <div>
                    <h3 class="modal-title" style="color:white;">👑 Sanction & Issue Accountant Salary Payslip</h3>
                    <p style="font-size:0.78rem; color:#bfdbfe; margin-top:2px;">Exclusive Director (Owner) Authority: Accountant payslip issuance</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-issue-accountant-slip')" style="color:white;">&times;</button>
            </div>
            <form onsubmit="submitIssueAccountantSlip(event)">
                <div class="modal-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Pay Period Month *</label>
                            <select id="issue-acc-month" class="form-control" required>
                                <option value="1">January</option>
                                <option value="2">February</option>
                                <option value="3">March</option>
                                <option value="4">April</option>
                                <option value="5">May</option>
                                <option value="6">June</option>
                                <option value="7">July</option>
                                <option value="8">August</option>
                                <option value="9">September</option>
                                <option value="10">October</option>
                                <option value="11" selected>November</option>
                                <option value="12">December</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Pay Period Year *</label>
                            <input type="number" id="issue-acc-year" class="form-control" value="2026" required>
                        </div>
                    </div>
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Base Monthly Salary (₹) *</label>
                            <input type="number" id="issue-acc-base" class="form-control" value="55000" required step="500">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Director Special Incentive / Bonus (₹)</label>
                            <input type="number" id="issue-acc-bonus" class="form-control" value="5000" step="500">
                        </div>
                    </div>
                    <div class="form-group">
                        <label class="form-label">Bonus Title / Reason</label>
                        <input type="text" id="issue-acc-bonus-title" class="form-control" value="Director Executive Performance Award & Festival Allowance">
                    </div>
                    <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:12px 16px; font-size:0.83rem; color:#334155;">
                        <div>🏛️ <strong>Institutional Rule:</strong> By policy, the Account Department is prohibited from preparing their own salary slip. This slip will be recorded as <code>Sanctioned by Director</code> and signed by <strong>Owner (Director) Rajeev Sinha</strong>.</div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-issue-accountant-slip')">Cancel</button>
                    <button type="submit" class="btn btn-primary" style="background:#1e3a8a; font-weight:700;">✍️ Sanction & Issue Payslip</button>
                </div>
            </form>
        </div>
    </div>
"""

tag = '    <!-- Application Scripts -->'
if tag in content:
    content = content.replace(tag, new_modals + "\n" + tag)
    print("4. Appended new modals before script tag")
else:
    print("WARNING: Application Scripts tag not found")

with open('school_website/index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("Successfully saved school_website/index.html")
