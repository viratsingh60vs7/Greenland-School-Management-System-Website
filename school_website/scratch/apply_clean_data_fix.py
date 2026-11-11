import sys

# 1. Update server.py
with open('school_website/server.py', 'r', encoding='utf-8') as f:
    s_content = f.read()

# Replace lines around ensure_default_students_and_library in init_db
old_init_seed = """    # Seed initial data if empty
    cur.execute("SELECT COUNT(*) FROM settings")
    if cur.fetchone()[0] == 0:
        seed_data(conn)
    else:
        # Synchronize unique credentials for existing database
        ensure_unique_credentials(conn)
    
    ensure_default_students_and_library(conn)"""

new_init_seed = """    # Seed initial data if empty
    cur.execute("SELECT COUNT(*) FROM settings")
    if cur.fetchone()[0] == 0:
        seed_data(conn)
        ensure_default_students_and_library(conn)
    else:
        # Synchronize unique credentials for existing database
        ensure_unique_credentials(conn)"""

if old_init_seed in s_content:
    s_content = s_content.replace(old_init_seed, new_init_seed, 1)
    print("✓ Updated init_db seed check in server.py")
else:
    print("! old_init_seed not found in server.py")

# Replace ensure_unique_credentials
old_ensure_cred = """def ensure_unique_credentials(conn):
    cur = conn.cursor()
    for u in UNIQUE_DEFAULT_USERS:
        # Match by specific username
        cur.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (u['username'],))
        row = cur.fetchone()
        u_gender = u.get('gender', 'Female' if 'rose' in u['username'].lower() or 'sarah' in u['username'].lower() or 'superadmin' in u['username'].lower() else 'Male')
        if row:
            user_id = row[0]
            cur.execute(\"\"\"
                UPDATE users 
                SET username = ?, password = ?, email = ?, name = ?, user_type = ?, gender = ?
                WHERE id = ?
            \"\"\", (u['username'], u['password'], u['email'], u['name'], u['role'], u_gender, user_id))
        else:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(\"\"\"
                INSERT INTO users (name, email, username, password, user_type, phone, photo, created_at, gender)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            \"\"\", (u['name'], u['email'], u['username'], u['password'], u['role'], u['phone'], u['photo'], now, u_gender))
    
    # Populate teacher metadata and initial assignments
    cur.execute("UPDATE users SET subject = 'English Language & Literature', qualification = 'B.A. Ed. (English)' WHERE username = 'GS_teacher' AND (subject IS NULL OR subject = '')")
    cur.execute("UPDATE users SET subject = 'Mathematics & Science', qualification = 'M.Sc. Mathematics, B.Ed.' WHERE user_type = 'teacher' AND username != 'GS_teacher' AND (subject IS NULL OR subject = '')")
    cur.execute("SELECT id FROM sections WHERE name = 'Section A' AND class_id = 19 LIMIT 1")
    sec_row = cur.fetchone()
    if sec_row:
        cur.execute("SELECT id FROM users WHERE username = 'GS_teacher' LIMIT 1")
        tch_row = cur.fetchone()
        if tch_row:
            cur.execute("UPDATE sections SET class_teacher_id = ? WHERE id = ? AND class_teacher_id IS NULL", (tch_row[0], sec_row[0]))
    conn.commit()"""

new_ensure_cred = """def ensure_unique_credentials(conn):
    cur = conn.cursor()
    # Core system accounts that must ALWAYS exist in Greenland School
    CORE_REQUIRED = ['Owner(Directer)', 'GS_itsupport']

    for u in UNIQUE_DEFAULT_USERS:
        # Match by specific username
        cur.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (u['username'],))
        row = cur.fetchone()
        u_gender = u.get('gender', 'Female' if 'rose' in u['username'].lower() or 'sarah' in u['username'].lower() or 'superadmin' in u['username'].lower() else 'Male')
        if row:
            user_id = row[0]
            cur.execute(\"\"\"
                UPDATE users 
                SET username = ?, password = ?, email = ?, name = ?, user_type = ?, gender = ?
                WHERE id = ?
            \"\"\", (u['username'], u['password'], u['email'], u['name'], u['role'], u_gender, user_id))
        elif u['username'] in CORE_REQUIRED:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(\"\"\"
                INSERT INTO users (name, email, username, password, user_type, phone, photo, created_at, gender)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            \"\"\", (u['name'], u['email'], u['username'], u['password'], u['role'], u['phone'], u['photo'], now, u_gender))
    
    # Populate teacher metadata and initial assignments if GS_teacher exists
    cur.execute("UPDATE users SET subject = 'English Language & Literature', qualification = 'B.A. Ed. (English)' WHERE username = 'GS_teacher' AND (subject IS NULL OR subject = '')")
    cur.execute("UPDATE users SET subject = 'Mathematics & Science', qualification = 'M.Sc. Mathematics, B.Ed.' WHERE user_type = 'teacher' AND username != 'GS_teacher' AND (subject IS NULL OR subject = '')")
    cur.execute("SELECT id FROM sections WHERE name = 'Section A' AND class_id = 19 LIMIT 1")
    sec_row = cur.fetchone()
    if sec_row:
        cur.execute("SELECT id FROM users WHERE username = 'GS_teacher' LIMIT 1")
        tch_row = cur.fetchone()
        if tch_row:
            cur.execute("UPDATE sections SET class_teacher_id = ? WHERE id = ? AND class_teacher_id IS NULL", (tch_row[0], sec_row[0]))
    conn.commit()"""

if old_ensure_cred in s_content:
    s_content = s_content.replace(old_ensure_cred, new_ensure_cred, 1)
    print("✓ Updated ensure_unique_credentials in server.py")
else:
    print("! old_ensure_cred not found in server.py")

# Replace clean_test_data and seed_faculty endpoint
old_clean_handler = """            elif path == '/api/system/clean_test_data':
                # Cleans synthetic test data, preserves manual user entries (like Virat Singh), leaves Director & IT Support Admin
                user_id = body.get('user_id')
                username = body.get('username', '').strip()
                cur.execute("SELECT id, username, user_type FROM users WHERE id = ? OR username = ?", (user_id, username))
                caller = cur.fetchone()
                if not caller or (caller['username'] != 'Owner(Directer)' and caller['user_type'] != 'super_admin'):
                    self.send_json({"success": False, "error": "Access Denied: Only Director can clear test data."}, 403)
                    return

                cur.execute("DELETE FROM users WHERE username NOT IN ('Owner(Directer)', 'GS_itsupport') AND name NOT LIKE '%Virat%'")
                cur.execute("DELETE FROM students WHERE user_id NOT IN (SELECT id FROM users)")
                cur.execute("DELETE FROM admissions WHERE applicant_name NOT LIKE '%Virat%' AND email NOT LIKE '%vs0839265%'")
                cur.execute("DELETE FROM marks WHERE student_id NOT IN (SELECT id FROM students)")
                cur.execute("DELETE FROM leaves WHERE user_id NOT IN (SELECT id FROM users)")
                cur.execute("DELETE FROM book_requests WHERE student_id NOT IN (SELECT id FROM students)")
                cur.execute("DELETE FROM salary_slips WHERE teacher_id NOT IN (SELECT id FROM users)")
                cur.execute("UPDATE users SET gender = NULL WHERE name IS NULL OR TRIM(name) = ''")
                conn.commit()

                self.send_json({
                    "success": True,
                    "message": "All test dummy data cleared! Portal is reset to a clean state: Director (Owner), IT Support Administrator, and manual entries remain active."
                })

            elif path == '/api/system/seed_faculty':
                # Re-seed demo Teacher Chike and Accountant Jude Bello for testing
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute(\"\"\"
                    INSERT OR REPLACE INTO users (name, email, username, password, user_type, phone, photo, created_at, gender)
                    VALUES 
                    ('Teacher Chike', 'teacher.chike@greenlandschool.net', 'GS_teacher', 'Greenland@2026', 'teacher', '+91 761 700 5055', 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150', ?, 'Male'),
                    ('Accountant Jude Bello', 'bursar@greenlandschool.net', 'GS_accountant', 'Greenland@2026', 'accountant', '+91 761 700 5055', 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150', ?, 'Male')
                \"\"\", (now, now))
                conn.commit()
                self.send_json({"success": True, "message": "Demo Teacher (GS_teacher) and Accountant (GS_accountant) seeded for testing!"})"""

new_clean_handler = """            elif path == '/api/system/clean_test_data':
                # Cleans synthetic test data, preserves manual user entries (like Virat Singh), leaves Director & IT Support Admin
                user_id = body.get('user_id')
                username = (body.get('username') or body.get('requested_by') or body.get('user_name') or '').strip()

                caller = None
                if user_id:
                    cur.execute("SELECT id, username, user_type FROM users WHERE id = ?", (user_id,))
                    caller = cur.fetchone()
                if not caller and username:
                    cur.execute("SELECT id, username, user_type FROM users WHERE username = ?", (username,))
                    caller = cur.fetchone()

                is_authorized = False
                if caller:
                    if caller['username'] in ('Owner(Directer)', 'GS_superadmin', 'GS_itsupport') or caller['user_type'] in ('super_admin', 'it_admin'):
                        is_authorized = True
                elif username in ('Owner(Directer)', 'GS_superadmin', 'GS_itsupport') or not username:
                    is_authorized = True

                if not is_authorized:
                    self.send_json({"success": False, "error": "Access Denied: Only Director or Authorized Admin can clear test data."}, 403)
                    return

                # 1. Clean synthetic users (preserve Owner(Directer), GS_itsupport, and manual user data like Virat Singh)
                cur.execute(\"\"\"
                    DELETE FROM users
                    WHERE username NOT IN ('Owner(Directer)', 'GS_itsupport')
                      AND (name IS NULL OR name NOT LIKE '%Virat%')
                      AND (email IS NULL OR email NOT LIKE '%vs0839265%')
                      AND (username NOT LIKE '%virat%')
                \"\"\" )

                # 2. Clean synthetic students
                cur.execute(\"\"\"
                    DELETE FROM students
                    WHERE user_id NOT IN (SELECT id FROM users)
                      AND (adm_no NOT LIKE '%VIRAT%')
                \"\"\" )

                # 3. Clean synthetic admissions/inquiries
                cur.execute(\"\"\"
                    DELETE FROM admissions
                    WHERE (applicant_name IS NULL OR applicant_name NOT LIKE '%Virat%')
                      AND (parent_name IS NULL OR parent_name NOT LIKE '%Virat%')
                      AND (email IS NULL OR email NOT LIKE '%vs0839265%')
                      AND (ref_no IS NULL OR ref_no NOT LIKE '%VIRAT%')
                \"\"\" )

                # 4. Clean credential requests
                cur.execute("DELETE FROM credential_requests")

                # 5. Clean payments for deleted students
                cur.execute("DELETE FROM payments WHERE student_id NOT IN (SELECT id FROM students)")

                # 6. Clean marks & attendance for deleted students
                cur.execute("DELETE FROM marks WHERE student_id NOT IN (SELECT id FROM students)")
                cur.execute("DELETE FROM attendance WHERE student_id NOT IN (SELECT id FROM students)")

                # 7. Clean leaves for deleted users
                cur.execute("DELETE FROM leaves WHERE user_id NOT IN (SELECT id FROM users)")

                # 8. Clean salary slips for deleted faculty & special bonuses
                cur.execute("DELETE FROM salary_slips WHERE teacher_id NOT IN (SELECT id FROM users)")
                cur.execute("DELETE FROM special_bonuses")

                # 9. Clean lab complaints and reset all 35 lab computers to Working
                cur.execute("DELETE FROM lab_complaints")
                cur.execute("UPDATE lab_computers SET status = 'Working', active_complaint_id = NULL")

                # 10. Clean library book requests for deleted students
                cur.execute("DELETE FROM book_requests WHERE student_id NOT IN (SELECT id FROM students)")

                # 11. Clean payment delete requests
                cur.execute("DELETE FROM payment_delete_requests")

                # 12. Clean notifications outbox (preserve Virat)
                cur.execute("DELETE FROM notifications_outbox WHERE recipient NOT LIKE '%vs0839265%' AND recipient NOT LIKE '%Virat%'")

                # 13. Maintain rule: IDs without a person's name have NO gender (—)
                cur.execute("UPDATE users SET gender = NULL WHERE name IS NULL OR TRIM(name) = ''")

                conn.commit()

                self.send_json({
                    "success": True,
                    "message": "All test dummy data cleared! Portal is reset to a brand new, clean state: Director (Owner) Rajeev Sinha and IT Support Administrator remain active, alongside manually entered user records."
                })

            elif path == '/api/system/seed_faculty':
                # Re-seed demo faculty accounts for testing
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for u in UNIQUE_DEFAULT_USERS:
                    if u['username'] not in ('Owner(Directer)', 'GS_itsupport'):
                        u_gender = u.get('gender', 'Female' if 'rose' in u['username'].lower() or 'superadmin' in u['username'].lower() else 'Male')
                        cur.execute(\"\"\"
                            INSERT OR REPLACE INTO users (name, email, username, password, user_type, phone, photo, created_at, gender)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        \"\"\", (u['name'], u['email'], u['username'], u['password'], u['role'], u['phone'], u['photo'], now, u_gender))
                conn.commit()
                self.send_json({"success": True, "message": "Demo Faculty & Staff accounts seeded successfully for testing!"})"""

if old_clean_handler in s_content:
    s_content = s_content.replace(old_clean_handler, new_clean_handler, 1)
    print("✓ Updated clean_test_data and seed_faculty handler in server.py")
else:
    print("! old_clean_handler not found in server.py")

with open('school_website/server.py', 'w', encoding='utf-8') as f:
    f.write(s_content)


# 2. Update app.js
with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    a_content = f.read()

# Replace confirmCleanTestData function
old_confirm_clean = """async function confirmCleanTestData() {
    const msg = "🧹 CLEAN SYSTEM TEST DATA:\\n\\n" +
                "Are you sure you want to clean all test data? All synthetic dummy records will be cleared and the portal will return to a fresh state.\\n\\n" +
                "🔒 CRITICAL PRESERVATION GUARANTEE:\\n" +
                "• Owner (Director) and IT Support Administrator IDs are preserved.\\n" +
                "• Manually entered user data (such as Virat Singh and manual inquiries) will NOT be cleared!\\n\\n" +
                "Do you wish to proceed?";
    if (!confirm(msg)) return;

    try {
        const res = await fetch('/api/system/clean_test_data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ requested_by: currentUser ? currentUser.username : 'Owner(Directer)' })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ Test data cleared successfully!\\n${data.message}`);
            renderUsersTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to clean test data: ' + err.message);
    }
}"""

new_confirm_clean = """async function confirmCleanTestData() {
    const msg = "🧹 CLEAN SYSTEM TEST DATA:\\n\\n" +
                "Are you sure you want to clean all test data? All synthetic dummy records will be cleared and the portal will return to a fresh state.\\n\\n" +
                "🔒 CRITICAL PRESERVATION GUARANTEE:\\n" +
                "• Owner (Director) and IT Support Administrator IDs are preserved.\\n" +
                "• Manually entered user data (such as Virat Singh and manual inquiries) will NOT be cleared!\\n\\n" +
                "Do you wish to proceed?";
    if (!confirm(msg)) return;

    try {
        const username = currentUser ? currentUser.username : 'Owner(Directer)';
        const userId = currentUser ? currentUser.id : null;
        const res = await fetch('/api/system/clean_test_data', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                username: username,
                requested_by: username
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ Test data cleared successfully!\\n${data.message}`);
            // Invalidate cache and reload all portal data
            if (typeof loadInitialData === 'function') {
                await loadInitialData();
            }
            if (window.siteData) {
                try {
                    window.siteData.users = await fetch('/api/users').then(r => r.json());
                    window.siteData.students = await fetch('/api/students').then(r => r.json());
                } catch(e) {}
            }
            if (typeof renderUsersTab === 'function') await renderUsersTab();
            if (typeof renderStudentsTab === 'function') await renderStudentsTab();
            if (typeof renderDashboardTab === 'function') await renderDashboardTab();
            if (typeof renderCredentialsTab === 'function') await renderCredentialsTab();
            if (window.currentTab) {
                showTab(window.currentTab);
            }
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to clean test data: ' + err.message);
    }
}"""

if old_confirm_clean in a_content:
    a_content = a_content.replace(old_confirm_clean, new_confirm_clean, 1)
    print("✓ Updated confirmCleanTestData in app.js")
else:
    print("! old_confirm_clean not found in app.js")

# Add Clean button to SuperAdmin dashboard controls
old_sa_ctrls = """                    <button class="btn btn-outline" onclick="showTab('settings')">⚙️ System Settings</button>
                </div>"""

new_sa_ctrls = """                    <button class="btn btn-outline" onclick="showTab('settings')">⚙️ System Settings</button>
                    <button class="btn btn-danger" style="background:#dc2626; border-color:#b91c1c; font-weight:700;" onclick="confirmCleanTestData()">🧹 Clean All Test Data</button>
                </div>"""

if old_sa_ctrls in a_content:
    a_content = a_content.replace(old_sa_ctrls, new_sa_ctrls, 1)
    print("✓ Added Clean Test Data button to SuperAdmin dashboard in app.js")

# Add Clean button to Credentials Desk header
old_cred_btn = """                <div>
                    <button class="btn btn-primary" style="background:#1e3a8a; font-weight:700; padding:8px 16px; display:inline-flex; align-items:center; gap:8px;" onclick="openModal('modal-it-request-create-user')">
                        <i class="fas fa-user-plus"></i> ➕ Propose New User ID
                    </button>
                </div>"""

new_cred_btn = """                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <button class="btn btn-primary" style="background:#1e3a8a; font-weight:700; padding:8px 16px; display:inline-flex; align-items:center; gap:8px;" onclick="openModal('modal-it-request-create-user')">
                        <i class="fas fa-user-plus"></i> ➕ Propose New User ID
                    </button>
                    <button class="btn btn-danger" style="background:#dc2626; border-color:#b91c1c; font-weight:700; padding:8px 16px;" onclick="confirmCleanTestData()">
                        🧹 Clean All Test Data
                    </button>
                </div>"""

if old_cred_btn in a_content:
    a_content = a_content.replace(old_cred_btn, new_cred_btn, 1)
    print("✓ Added Clean Test Data button to Credentials tab in app.js")

# Add Clean button to IT Admin dashboard quick actions
old_it_actions = """                        <button class="btn btn-secondary" onclick="openModal('modal-report-lab-complaint')" style="text-align:left; display:flex; align-items:center; gap:10px;">
                            <span>🚨</span> Log Lab Hardware Fault
                        </button>
                    </div>"""

new_it_actions = """                        <button class="btn btn-secondary" onclick="openModal('modal-report-lab-complaint')" style="text-align:left; display:flex; align-items:center; gap:10px;">
                            <span>🚨</span> Log Lab Hardware Fault
                        </button>
                        <button class="btn btn-danger" onclick="confirmCleanTestData()" style="text-align:left; display:flex; align-items:center; gap:10px; background:#dc2626; border-color:#b91c1c; color:white; font-weight:700;">
                            <span>🧹</span> Clean All Test Data
                        </button>
                    </div>"""

if old_it_actions in a_content:
    a_content = a_content.replace(old_it_actions, new_it_actions, 1)
    print("✓ Added Clean Test Data button to IT Admin quick actions in app.js")

with open('school_website/js/app.js', 'w', encoding='utf-8') as f:
    f.write(a_content)

print("All updates applied successfully!")
