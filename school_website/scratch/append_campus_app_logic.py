import sys

app_js_code = '''

// =====================================================================
// GREENLAND CAMPUS MOBILE & WEB APP (STUDENT • PARENT • TEACHER)
// Dual Login by Registered Phone Number OR User ID
// =====================================================================

window.appCurrentUser = null;
window.appActiveTab = 'home';
window.appFrameMode = 'phone';
window.appParentSelectedChildId = null;

function openCampusApp() {
    const pub = document.getElementById('public-website');
    const port = document.getElementById('portal-container');
    const login = document.getElementById('portal-login-view');
    const appView = document.getElementById('campus-app-view');

    if (pub) pub.style.display = 'none';
    if (port) port.style.display = 'none';
    if (login) login.style.display = 'none';
    if (appView) appView.style.display = 'block';

    window.location.hash = '#app';

    // If already logged in as a student, parent, or teacher in portal, sync with app
    if (currentUser && ['student', 'parent', 'teacher'].includes(currentUser.user_type)) {
        window.appCurrentUser = currentUser;
    }

    renderCampusApp();
}

function exitCampusApp() {
    const appView = document.getElementById('campus-app-view');
    if (appView) appView.style.display = 'none';

    if (currentUser) {
        openPortal();
    } else {
        openPublicSite();
    }
}

function toggleAppDeviceFrame() {
    const wrapper = document.getElementById('app-device-wrapper');
    const chassis = document.getElementById('app-mobile-chassis');
    const btn = document.getElementById('app-frame-toggle-btn');

    if (window.appFrameMode === 'phone') {
        window.appFrameMode = 'fullscreen';
        wrapper.style.maxWidth = '920px';
        chassis.style.borderRadius = '16px';
        chassis.style.boxShadow = '0 12px 40px rgba(0,0,0,0.4)';
        btn.innerHTML = '🖥️ Fullscreen Mode (Switch to Phone)';
    } else {
        window.appFrameMode = 'phone';
        wrapper.style.maxWidth = '440px';
        chassis.style.borderRadius = '36px';
        chassis.style.boxShadow = '0 25px 60px -15px rgba(0,0,0,0.8), 0 0 0 10px #1e293b, 0 0 0 12px #334155';
        btn.innerHTML = '📱 Phone Mockup Mode';
    }
}

function fillAppDemoLogin(userOrPhone, password, role) {
    const usrInput = document.getElementById('app-login-input');
    const pwdInput = document.getElementById('app-login-password');
    if (usrInput) usrInput.value = userOrPhone;
    if (pwdInput) {
        pwdInput.value = password;
        pwdInput.focus();
    }
}

async function handleAppLogin(e) {
    if (e) e.preventDefault();
    const usrOrPhone = (document.getElementById('app-login-input') ? document.getElementById('app-login-input').value : '').trim();
    const pwd = (document.getElementById('app-login-password') ? document.getElementById('app-login-password').value : '').trim();
    const alertBox = document.getElementById('app-login-alert');

    if (!usrOrPhone || !pwd) {
        if (alertBox) {
            alertBox.style.display = 'block';
            alertBox.innerText = 'Please enter both your User ID (or Phone Number) and Password.';
        }
        return;
    }

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: usrOrPhone, password: pwd })
        });
        const data = await res.json();

        if (data.success && data.user) {
            // Verify role
            const u = data.user;
            if (!['student', 'parent', 'teacher'].includes(u.user_type)) {
                if (alertBox) {
                    alertBox.style.display = 'block';
                    alertBox.innerText = `⚠️ Notice: User ID '${u.username}' is an administrative account (${u.user_type}). Please sign in via the SMS Master Portal.`;
                }
                return;
            }

            window.appCurrentUser = u;
            window.appActiveTab = 'home';
            renderCampusApp();
        } else {
            if (alertBox) {
                alertBox.style.display = 'block';
                alertBox.innerText = data.message || 'Invalid User ID, Phone Number, or Password.';
            }
        }
    } catch (err) {
        if (alertBox) {
            alertBox.style.display = 'block';
            alertBox.innerText = 'Login server connection error. Please try again.';
        }
    }
}

function handleAppLogout() {
    window.appCurrentUser = null;
    window.appActiveTab = 'home';
    window.appParentSelectedChildId = null;
    renderCampusApp();
}

function switchAppTab(tabName) {
    window.appActiveTab = tabName;
    renderCampusApp();
}

function switchAppParentChild(childId) {
    window.appParentSelectedChildId = childId;
    renderCampusApp();
}

async function handleDirectorApprove(origin, reqId, action) {
    const callerUname = currentUser ? currentUser.username : 'Owner(Directer)';
    const callerRole = currentRole || 'super_admin';

    if (callerRole !== 'super_admin' && callerUname !== 'Owner(Directer)') {
        alert("🔒 Access Denied: Only Director (Owner) Rajeev Sinha has authority to approve requests created by Teachers or IT Team.");
        return;
    }

    const note = prompt(`Enter Director Approval Notes (or leave default):`, action === 'approve' ? 'Approved by Director Rajeev Sinha' : 'Rejected by Director');
    if (note === null) return;

    try {
        const res = await fetch('/api/director/approve_request', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                origin: origin,
                request_id: reqId,
                action: action,
                notes: note,
                caller_username: callerUname,
                caller_role: callerRole
            })
        }).then(r => r.json());

        if (res.success) {
            alert(`✓ ${res.message}`);
            renderSuperAdminDashboard();
        } else {
            alert(`❌ Error: ${res.error || res.message}`);
        }
    } catch (err) {
        alert('Failed to process approval: ' + err.message);
    }
}

async function submitAppTeacherLeave(e) {
    e.preventDefault();
    if (!window.appCurrentUser) return;

    const lType = document.getElementById('app-leave-type').value;
    const sDate = document.getElementById('app-leave-start').value;
    const eDate = document.getElementById('app-leave-end').value;
    const days = parseInt(document.getElementById('app-leave-days').value) || 1;
    const reason = document.getElementById('app-leave-reason').value.trim();

    try {
        const res = await fetch('/api/leaves/apply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: window.appCurrentUser.id,
                leave_type: lType,
                start_date: sDate,
                end_date: eDate,
                days_count: days,
                reason: reason,
                applicant_role: 'teacher'
            })
        }).then(r => r.json());

        if (res.success) {
            alert("✓ Teacher Leave Application Submitted successfully!\\n\\nPolicy Status: ⏳ Sent to Director Rajeev Sinha for Approval.");
            renderCampusApp();
        } else {
            alert("Error: " + res.message);
        }
    } catch (err) {
        alert("Failed to submit leave: " + err.message);
    }
}

async function submitAppTeacherComplaint(e) {
    e.preventDefault();
    if (!window.appCurrentUser) return;

    const lab = document.getElementById('app-comp-lab').value;
    const pc = document.getElementById('app-comp-pc').value.trim();
    const cat = document.getElementById('app-comp-cat').value;
    const prio = document.getElementById('app-comp-priority').value;
    const desc = document.getElementById('app-comp-desc').value.trim();

    try {
        const res = await fetch('/api/lab/complaints', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lab_name: lab,
                pc_number: pc,
                issue_category: cat,
                priority: prio,
                problem_description: desc,
                reported_by_id: window.appCurrentUser.id,
                reported_by_name: window.appCurrentUser.name || 'Teacher Chike',
                teacher_role: 'Computer Teacher'
            })
        }).then(r => r.json());

        if (res.success) {
            alert(`✓ Faulty Computer Complaint ${res.ticket_no} logged!\\n\\nPolicy Status: ⏳ Dispatched to IT Support Administrator & Director for Repair Approval.`);
            renderCampusApp();
        } else {
            alert("Error: " + res.message);
        }
    } catch (err) {
        alert("Failed to report complaint: " + err.message);
    }
}

// Main Render Function for Campus Mobile & Web App
async function renderCampusApp() {
    const screenBody = document.getElementById('app-screen-body');
    const bottomNav = document.getElementById('app-bottom-nav');
    if (!screenBody) return;

    // 1. NOT LOGGED IN: Render App Dual Login Portal
    if (!window.appCurrentUser) {
        if (bottomNav) bottomNav.style.display = 'none';

        screenBody.innerHTML = `
            <div style="padding:24px 20px; display:flex; flex-direction:column; justify-content:center; flex:1; background:#ffffff;">
                <div style="text-align:center; margin-bottom:20px;">
                    <div style="width:64px; height:64px; margin:0 auto 12px auto; background:#1e3a8a; border-radius:18px; display:flex; align-items:center; justify-content:center; box-shadow:0 8px 20px rgba(30,58,138,0.25);">
                        <img src="assets/Logo_Greenland_School.png" style="width:80%; height:80%; object-fit:contain;" alt="GS">
                    </div>
                    <h3 style="font-size:1.3rem; font-weight:800; color:#0f172a; margin:0;">Greenland Campus App</h3>
                    <p style="font-size:0.78rem; color:#64748b; margin-top:4px;">Official Mobile Connect for Student, Parent & Teacher</p>
                    <div style="margin-top:10px;">
                        <span style="font-size:0.72rem; background:#eff6ff; color:#1d4ed8; padding:3px 10px; border-radius:50px; font-weight:700; border:1px solid #bfdbfe;">
                            📱 Dual Login: Use Phone Number OR User ID
                        </span>
                    </div>
                </div>

                <div id="app-login-alert" style="display:none; background:#fef2f2; color:#991b1b; border:1px solid #fecaca; border-radius:8px; padding:10px 12px; font-size:0.75rem; margin-bottom:14px;"></div>

                <form onsubmit="handleAppLogin(event)">
                    <div class="form-group" style="margin-bottom:14px;">
                        <label style="font-size:0.78rem; font-weight:700; color:#334155; display:block; margin-bottom:5px;">
                            📱 Phone Number or 👤 User ID *
                        </label>
                        <input type="text" id="app-login-input" class="form-control" placeholder="Enter Phone No (e.g. 8004125223) or User ID" required style="font-size:0.85rem; padding:10px 14px; border-radius:8px;">
                        <span style="font-size:0.68rem; color:#64748b; display:block; margin-top:3px;">
                            💡 Both your Registered Phone Number and User ID are supported.
                        </span>
                    </div>
                    <div class="form-group" style="margin-bottom:18px;">
                        <label style="font-size:0.78rem; font-weight:700; color:#334155; display:block; margin-bottom:5px;">
                            🔑 Password *
                        </label>
                        <input type="password" id="app-login-password" class="form-control" placeholder="Enter password" required style="font-size:0.85rem; padding:10px 14px; border-radius:8px;">
                    </div>
                    <button type="submit" class="btn btn-primary" style="width:100%; padding:11px; font-size:0.9rem; font-weight:700; background:#2563eb; border:none; border-radius:8px; box-shadow:0 4px 12px rgba(37,99,235,0.3);">
                        🚀 Sign In to Campus App
                    </button>
                </form>

                <!-- Quick One-Tap Test Fill Cards -->
                <div style="margin-top:24px; border-top:1px solid #f1f5f9; padding-top:16px;">
                    <div style="font-size:0.72rem; font-weight:800; color:#64748b; text-transform:uppercase; margin-bottom:10px; letter-spacing:0.5px;">
                        ✨ Instant One-Tap Demo Access:
                    </div>
                    <div style="display:flex; flex-direction:column; gap:8px;">
                        <button type="button" class="btn btn-outline btn-sm" style="text-align:left; padding:8px 10px; font-size:0.75rem; border-color:#cbd5e1; background:#f8fafc;" onclick="fillAppDemoLogin('8004125223', 'Viratsingh@2004', 'student')">
                            🎓 <strong>Student: Virat Singh</strong><br>
                            <span style="color:#2563eb; font-size:0.68rem;">Phone: <code>8004125223</code> | User ID: <code>Viratsingh60vs7</code></span>
                        </button>
                        <button type="button" class="btn btn-outline btn-sm" style="text-align:left; padding:8px 10px; font-size:0.75rem; border-color:#cbd5e1; background:#f8fafc;" onclick="fillAppDemoLogin('9876543210', 'Greenland@2026', 'teacher')">
                            👨‍🏫 <strong>Teacher: Teacher Chike</strong><br>
                            <span style="color:#2563eb; font-size:0.68rem;">Phone: <code>9876543210</code> | User ID: <code>GS_teacher</code></span>
                        </button>
                        <button type="button" class="btn btn-outline btn-sm" style="text-align:left; padding:8px 10px; font-size:0.75rem; border-color:#cbd5e1; background:#f8fafc;" onclick="fillAppDemoLogin('9812345678', 'Greenland@2026', 'parent')">
                            👨‍👩‍👧 <strong>Parent: Marcus Kaba (Multi-child: Alex & Clara)</strong><br>
                            <span style="color:#2563eb; font-size:0.68rem;">Phone: <code>9812345678</code> | User ID: <code>GS_parent_Alex_and_Clara</code></span>
                        </button>
                    </div>
                </div>
            </div>
        `;
        return;
    }

    // 2. AUTHENTICATED USER IN APP
    if (bottomNav) bottomNav.style.display = 'flex';

    const u = window.appCurrentUser;
    const role = u.user_type;

    // Build Bottom Navigation
    let navItems = [
        { id: 'home', label: 'Home', icon: 'fas fa-home' },
        { id: 'fees', label: 'Fees', icon: 'fas fa-credit-card' },
        { id: 'timetable', label: 'Timetable', icon: 'fas fa-calendar-alt' },
        { id: 'library', label: 'Library', icon: 'fas fa-book-reader' }
    ];

    if (role === 'student' || role === 'parent') {
        navItems.push({ id: 'marks', label: 'Marks', icon: 'fas fa-file-alt' });
    } else if (role === 'teacher') {
        navItems.push({ id: 'requests', label: 'Requests', icon: 'fas fa-clipboard-check' });
    }

    bottomNav.innerHTML = navItems.map(item => `
        <button type="button" 
                style="background:none; border:none; display:flex; flex-direction:column; align-items:center; gap:2px; font-size:0.72rem; color:${window.appActiveTab === item.id ? '#2563eb' : '#64748b'}; font-weight:${window.appActiveTab === item.id ? '700' : '500'}; cursor:pointer; padding:4px 8px;"
                onclick="switchAppTab('${item.id}')">
            <i class="${item.icon}" style="font-size:1.1rem; color:${window.appActiveTab === item.id ? '#2563eb' : '#94a3b8'};"></i>
            <span>${item.label}</span>
        </button>
    `).join('');

    // Common App Header
    const appHeaderHtml = `
        <div style="background:linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%); color:white; padding:16px 16px 12px 16px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <img src="${u.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150'}" style="width:38px; height:38px; border-radius:50%; object-fit:cover; border:2px solid rgba(255,255,255,0.8);">
                    <div>
                        <div style="font-size:0.9rem; font-weight:800; line-height:1.2;">${u.name || u.username}</div>
                        <span style="font-size:0.65rem; background:rgba(255,255,255,0.2); padding:1px 6px; border-radius:10px; font-weight:700; text-transform:uppercase;">
                            ${role === 'super_admin' ? 'Director' : role}
                        </span>
                    </div>
                </div>
                <div style="display:flex; gap:6px;">
                    <button class="btn btn-sm" style="background:rgba(255,255,255,0.2); color:white; border:none; border-radius:50px; font-size:0.75rem; padding:4px 10px;" onclick="handleAppLogout()" title="Log out from App">
                        🚪 Exit
                    </button>
                </div>
            </div>
        </div>
    `;

    // -----------------------------------------------------------------
    // ROLE A: STUDENT EXPERIENCE
    // -----------------------------------------------------------------
    if (role === 'student') {
        const sData = await fetch(`/api/app/student_dashboard?user_id=${u.id}`).then(r => r.json());
        const stu = sData.student || {};
        const fees = sData.fees || [];
        const books = sData.issued_books || [];
        const timetable = sData.timetable || [];
        const marks = sData.marks || [];

        let tabContent = '';

        if (window.appActiveTab === 'home') {
            tabContent = `
                <!-- Digital Student ID Card -->
                <div style="background:linear-gradient(135deg, #0f172a 0%, #1e3a8a 100%); border-radius:14px; padding:16px; color:white; margin-bottom:14px; box-shadow:0 8px 20px rgba(15,23,42,0.2);">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div style="font-size:0.65rem; color:#93c5fd; text-transform:uppercase; font-weight:700; letter-spacing:0.5px;">Greenland Student Card</div>
                            <div style="font-size:1.1rem; font-weight:800; margin-top:2px;">${stu.name}</div>
                            <div style="font-size:0.75rem; color:#cbd5e1;">${stu.class_name} • ${stu.section_name}</div>
                        </div>
                        <span style="font-size:0.72rem; background:#dc2626; color:white; padding:2px 8px; border-radius:6px; font-weight:700;">Blood: ${stu.blood_group}</span>
                    </div>
                    <div style="margin-top:14px; display:flex; justify-content:space-between; font-size:0.72rem; border-top:1px solid rgba(255,255,255,0.15); padding-top:8px;">
                        <div>Adm No: <strong>${stu.adm_no}</strong></div>
                        <div>Attendance: <strong style="color:#4ade80;">${stu.attendance_pct}%</strong></div>
                    </div>
                </div>

                <!-- Quick Action Stats Grid -->
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:14px;">
                    <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:12px; padding:12px; cursor:pointer;" onclick="switchAppTab('fees')">
                        <div style="font-size:1.2rem; color:#2563eb;">💳</div>
                        <div style="font-size:0.72rem; color:#64748b; margin-top:4px;">Tuition Fees</div>
                        <div style="font-size:0.95rem; font-weight:800; color:#1e40af;">${fees.length > 0 && fees[0].status === 'Paid' ? 'Paid in Full' : 'Due Soon'}</div>
                    </div>
                    <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:12px; padding:12px; cursor:pointer;" onclick="switchAppTab('library')">
                        <div style="font-size:1.2rem; color:#16a34a;">📚</div>
                        <div style="font-size:0.72rem; color:#64748b; margin-top:4px;">Issued Books</div>
                        <div style="font-size:0.95rem; font-weight:800; color:#15803d;">${books.length} Books Active</div>
                    </div>
                </div>

                <!-- Today's Schedule Overview -->
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:14px; margin-bottom:14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                        <span style="font-size:0.8rem; font-weight:800; color:#0f172a;">📅 Today's Classes</span>
                        <a href="javascript:void(0)" onclick="switchAppTab('timetable')" style="font-size:0.72rem; color:#2563eb; font-weight:700;">View All</a>
                    </div>
                    ${timetable.slice(0, 3).map((tt, i) => `
                        <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid #f1f5f9; font-size:0.78rem;">
                            <div>
                                <span style="font-weight:700; color:#1e293b;">Period ${i+1}: ${tt.subject_name}</span>
                                <div style="font-size:0.68rem; color:#64748b;">Teacher: ${tt.teacher_name || 'Assigned Faculty'}</div>
                            </div>
                            <span style="font-size:0.7rem; background:#f1f5f9; padding:2px 6px; border-radius:4px; font-weight:600;">Room 102</span>
                        </div>
                    `).join('')}
                </div>
            `;
        } else if (window.appActiveTab === 'fees') {
            tabContent = `
                <div style="padding:4px 0;">
                    <div style="font-size:0.95rem; font-weight:800; color:#0f172a; margin-bottom:10px;">💳 Tuition & Academic Fees</div>
                    ${fees.length > 0 ? fees.map(f => `
                        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:14px; margin-bottom:10px;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <strong style="font-size:0.85rem; color:#0f172a;">${f.title}</strong>
                                <span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700; font-size:0.72rem;">${f.status}</span>
                            </div>
                            <div style="font-size:1.15rem; font-weight:800; color:#1e40af; margin-top:6px;">₦${Number(f.amount).toLocaleString('en-US', {minimumFractionDigits:2})}</div>
                            <div style="display:flex; justify-content:space-between; font-size:0.72rem; color:#64748b; margin-top:8px; border-top:1px dashed #e2e8f0; padding-top:6px;">
                                <span>Ref: <code>${f.ref_no || 'REC-2026-001'}</code></span>
                                <span>Method: ${f.method || 'Online'}</span>
                            </div>
                        </div>
                    `).join('') : '<div style="text-align:center; padding:20px; color:#64748b;">No fees recorded.</div>'}
                </div>
            `;
        } else if (window.appActiveTab === 'timetable') {
            tabContent = `
                <div style="padding:4px 0;">
                    <div style="font-size:0.95rem; font-weight:800; color:#0f172a; margin-bottom:10px;">📅 Weekly Academic Timetable</div>
                    ${timetable.map((tt, i) => `
                        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:10px; padding:10px 14px; margin-bottom:8px; display:flex; justify-content:space-between; align-items:center;">
                            <div>
                                <span style="font-size:0.68rem; font-weight:800; color:#2563eb; text-transform:uppercase;">Period ${i+1} (09:${(i+1)*45} - 10:${(i+1)*45})</span>
                                <div style="font-weight:700; color:#0f172a; font-size:0.85rem;">${tt.subject_name}</div>
                                <div style="font-size:0.72rem; color:#64748b;">Faculty: ${tt.teacher_name || 'Faculty Assigned'}</div>
                            </div>
                            <span style="font-size:0.72rem; background:#eff6ff; color:#1d4ed8; padding:3px 8px; border-radius:6px; font-weight:700;">Lab Room</span>
                        </div>
                    `).join('')}
                </div>
            `;
        } else if (window.appActiveTab === 'library') {
            tabContent = `
                <div style="padding:4px 0;">
                    <div style="font-size:0.95rem; font-weight:800; color:#0f172a; margin-bottom:10px;">📚 My E-Library Booklet (Issued Books)</div>
                    ${books.length > 0 ? books.map(b => `
                        <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:14px; margin-bottom:10px;">
                            <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                                <div>
                                    <strong style="font-size:0.88rem; color:#0f172a;">${b.book_title}</strong>
                                    <div style="font-size:0.74rem; color:#64748b;">Author: ${b.author}</div>
                                </div>
                                <span class="badge" style="background:#dbeafe; color:#1e40af; font-weight:700; font-size:0.7rem;">${b.status}</span>
                            </div>
                            <div style="margin-top:10px; background:#f8fafc; border-radius:8px; padding:8px 10px; font-size:0.72rem; display:flex; justify-content:space-between;">
                                <span>Bookshelf: <strong>${b.bookshelf_no || 'Shelf A-3'}</strong></span>
                                <span>Due: <strong style="color:#dc2626;">${b.due_date || '2026-11-20'}</strong></span>
                            </div>
                        </div>
                    `).join('') : '<div style="text-align:center; padding:20px; color:#64748b;">No books currently issued. Visit the library to issue books.</div>'}
                </div>
            `;
        } else if (window.appActiveTab === 'marks') {
            tabContent = `
                <div style="padding:4px 0;">
                    <div style="font-size:0.95rem; font-weight:800; color:#0f172a; margin-bottom:10px;">📄 Official Academic Marksheet</div>
                    <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:14px; margin-bottom:12px;">
                        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #f1f5f9; padding-bottom:8px;">
                            <div>
                                <strong style="font-size:0.85rem;">Term 1 Examination Marksheet</strong>
                                <div style="font-size:0.72rem; color:#64748b;">Academic Year: 2026 / 2027</div>
                            </div>
                            <span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700;">GPA: 3.85 (A)</span>
                        </div>
                        <div style="margin-top:10px;">
                            <div style="display:flex; justify-content:space-between; font-size:0.78rem; padding:4px 0;">
                                <span>Mathematics & Advanced Calculus</span>
                                <strong style="color:#15803d;">94 / 100 (A+)</strong>
                            </div>
                            <div style="display:flex; justify-content:space-between; font-size:0.78rem; padding:4px 0;">
                                <span>Computer Science & Coding</span>
                                <strong style="color:#15803d;">98 / 100 (A+)</strong>
                            </div>
                            <div style="display:flex; justify-content:space-between; font-size:0.78rem; padding:4px 0;">
                                <span>Physics & Laboratory Practicals</span>
                                <strong style="color:#15803d;">89 / 100 (A)</strong>
                            </div>
                            <div style="display:flex; justify-content:space-between; font-size:0.78rem; padding:4px 0;">
                                <span>English Language & Literature</span>
                                <strong style="color:#15803d;">91 / 100 (A)</strong>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }

        screenBody.innerHTML = `
            ${appHeaderHtml}
            <div style="padding:14px; flex:1; background:#f8fafc;">
                ${tabContent}
            </div>
        `;
        return;
    }

    // -----------------------------------------------------------------
    // ROLE B: PARENT EXPERIENCE (MULTI-CHILD ONE LOGIN SEPARATE ACCESS)
    // -----------------------------------------------------------------
    if (role === 'parent') {
        const pData = await fetch(`/api/app/parent_dashboard?user_id=${u.id}`).then(r => r.json());
        const children = pData.children || [];
        
        if (!window.appParentSelectedChildId && children.length > 0) {
            window.appParentSelectedChildId = children[0].student_id;
        }

        const selChild = children.find(c => c.student_id === window.appParentSelectedChildId) || children[0] || {};
        const fees = selChild.fees || [];
        const books = selChild.issued_books || [];

        screenBody.innerHTML = `
            ${appHeaderHtml}
            <div style="padding:14px; flex:1; background:#f8fafc;">
                <!-- Parent Multi-Child Selector Banner -->
                <div style="margin-bottom:14px;">
                    <div style="font-size:0.72rem; font-weight:800; color:#64748b; text-transform:uppercase; margin-bottom:6px; letter-spacing:0.5px;">
                        👨‍👩‍👧 Select Enrolled Child (One Parent Login):
                    </div>
                    <div style="display:flex; gap:8px; overflow-x:auto; padding-bottom:4px;">
                        ${children.map(c => `
                            <button type="button" 
                                    class="btn btn-sm" 
                                    style="padding:6px 14px; font-size:0.78rem; border-radius:20px; font-weight:700; border:none; ${c.student_id === selChild.student_id ? 'background:#1e3a8a; color:white; box-shadow:0 3px 8px rgba(30,58,138,0.3);' : 'background:#e2e8f0; color:#334155;'}" 
                                    onclick="switchAppParentChild(${c.student_id})">
                                👦 ${c.name} (${c.class_name})
                            </button>
                        `).join('')}
                    </div>
                </div>

                <!-- Child Selected Overview Card -->
                <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:14px; padding:14px; margin-bottom:14px; box-shadow:0 4px 12px rgba(0,0,0,0.03);">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <img src="${selChild.photo || 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150'}" style="width:48px; height:48px; border-radius:50%; object-fit:cover; border:2px solid #3b82f6;">
                        <div>
                            <div style="font-size:1rem; font-weight:800; color:#0f172a;">${selChild.name}</div>
                            <div style="font-size:0.75rem; color:#64748b;">${selChild.class_name} • ${selChild.section_name} • Adm: ${selChild.adm_no}</div>
                            <div style="font-size:0.72rem; color:#15803d; font-weight:700; margin-top:2px;">Attendance: ${selChild.attendance_pct}% Present</div>
                        </div>
                    </div>
                </div>

                <!-- Child Fee Breakdown -->
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:14px; margin-bottom:12px;">
                    <div style="font-size:0.85rem; font-weight:800; color:#0f172a; margin-bottom:8px;">💳 ${selChild.name}'s Fee Ledger</div>
                    ${fees.length > 0 ? fees.map(f => `
                        <div style="display:flex; justify-content:space-between; align-items:center; padding:6px 0; border-bottom:1px solid #f1f5f9; font-size:0.78rem;">
                            <div>
                                <span style="font-weight:700; color:#1e293b;">${f.title}</span>
                                <div style="font-size:0.68rem; color:#64748b;">Ref: ${f.ref_no || 'REC-2026-001'}</div>
                            </div>
                            <span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700;">₦${Number(f.amount).toLocaleString('en-US', {minimumFractionDigits:2})} (Paid)</span>
                        </div>
                    `).join('') : '<div style="font-size:0.75rem; color:#64748b;">No outstanding fees.</div>'}
                </div>

                <!-- Child Library Booklet -->
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:14px;">
                    <div style="font-size:0.85rem; font-weight:800; color:#0f172a; margin-bottom:8px;">📚 ${selChild.name}'s E-Library Booklet</div>
                    ${books.length > 0 ? books.map(b => `
                        <div style="padding:6px 0; border-bottom:1px solid #f1f5f9; font-size:0.78rem;">
                            <strong style="color:#0f172a;">${b.book_title}</strong>
                            <div style="font-size:0.7rem; color:#64748b;">Bookshelf: ${b.bookshelf_no || 'Shelf A-3'} • Due: <span style="color:#dc2626; font-weight:700;">${b.due_date || '2026-11-20'}</span></div>
                        </div>
                    `).join('') : '<div style="font-size:0.75rem; color:#64748b;">No books currently checked out.</div>'}
                </div>
            </div>
        `;
        return;
    }

    // -----------------------------------------------------------------
    // ROLE C: TEACHER EXPERIENCE (ATTENDANCE, LEAVE, LAB COMPLAINTS)
    // -----------------------------------------------------------------
    if (role === 'teacher') {
        const tData = await fetch(`/api/app/teacher_dashboard?user_id=${u.id}`).then(r => r.json());
        const leaves = tData.leaves || [];
        const complaints = tData.lab_complaints || [];

        let tabContent = '';

        if (window.appActiveTab === 'home') {
            tabContent = `
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:14px; padding:16px; margin-bottom:14px;">
                    <div style="font-size:0.75rem; color:#2563eb; font-weight:800; text-transform:uppercase;">Faculty Dashboard</div>
                    <div style="font-size:1.15rem; font-weight:800; color:#0f172a; margin-top:2px;">Welcome, ${u.name}!</div>
                    <div style="font-size:0.75rem; color:#64748b;">Class Teacher: Grade 5-A • Computer Science In-Charge</div>
                </div>

                <!-- Teacher Actions Grid -->
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:14px;">
                    <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:12px; padding:12px; cursor:pointer;" onclick="switchAppTab('requests')">
                        <div style="font-size:1.3rem; color:#2563eb;">🏖️</div>
                        <div style="font-size:0.8rem; font-weight:800; color:#1e40af; margin-top:4px;">Apply for Leave</div>
                        <div style="font-size:0.68rem; color:#1d4ed8;">Director Approval</div>
                    </div>
                    <div style="background:#fef2f2; border:1px solid #fecaca; border-radius:12px; padding:12px; cursor:pointer;" onclick="switchAppTab('complaints')">
                        <div style="font-size:1.3rem; color:#dc2626;">💻</div>
                        <div style="font-size:0.8rem; font-weight:800; color:#991b1b; margin-top:4px;">Report Broken PC</div>
                        <div style="font-size:0.68rem; color:#b91c1c;">Lab Hardware Ticket</div>
                    </div>
                </div>

                <!-- Recent Leave Applications Status -->
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:14px; margin-bottom:12px;">
                    <div style="font-size:0.85rem; font-weight:800; color:#0f172a; margin-bottom:8px;">📋 Leave Status (Director Approvals)</div>
                    ${leaves.length > 0 ? leaves.slice(0, 3).map(l => `
                        <div style="padding:6px 0; border-bottom:1px solid #f1f5f9; font-size:0.78rem;">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <strong style="color:#0f172a;">${l.leave_type} (${l.days_count} days)</strong>
                                <span class="badge" style="background:${l.status.includes('Approved') ? '#dcfce7' : '#fef3c7'}; color:${l.status.includes('Approved') ? '#15803d' : '#b45309'}; font-weight:700; font-size:0.7rem;">
                                    ${l.status}
                                </span>
                            </div>
                            <div style="font-size:0.7rem; color:#64748b; margin-top:2px;">Dates: ${l.start_date} to ${l.end_date} • Reason: ${l.reason}</div>
                        </div>
                    `).join('') : '<div style="font-size:0.75rem; color:#64748b;">No recent leaves applied.</div>'}
                </div>
            `;
        } else if (window.appActiveTab === 'requests') {
            tabContent = `
                <!-- Teacher Apply For Leave Form -->
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px; margin-bottom:14px;">
                    <div style="font-size:0.95rem; font-weight:800; color:#0f172a;">🏖️ Apply for Faculty Leave</div>
                    <div style="font-size:0.72rem; color:#2563eb; font-weight:600; margin-bottom:12px;">
                        STRICT REQUIREMENT: All teacher leaves are submitted directly to Director Rajeev Sinha for approval.
                    </div>
                    <form onsubmit="submitAppTeacherLeave(event)">
                        <div class="form-group" style="margin-bottom:10px;">
                            <label style="font-size:0.75rem; font-weight:700;">Leave Type *</label>
                            <select id="app-leave-type" class="form-control" style="font-size:0.8rem; padding:6px 10px;">
                                <option value="Casual Leave (CL)">Casual Leave (CL)</option>
                                <option value="Sick Leave (SL)">Sick Leave (SL)</option>
                                <option value="Earned Leave (EL)">Earned Leave (EL)</option>
                            </select>
                        </div>
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px;">
                            <div class="form-group">
                                <label style="font-size:0.75rem; font-weight:700;">Start Date *</label>
                                <input type="date" id="app-leave-start" class="form-control" required style="font-size:0.8rem; padding:6px 10px;">
                            </div>
                            <div class="form-group">
                                <label style="font-size:0.75rem; font-weight:700;">End Date *</label>
                                <input type="date" id="app-leave-end" class="form-control" required style="font-size:0.8rem; padding:6px 10px;">
                            </div>
                        </div>
                        <div class="form-group" style="margin-bottom:10px;">
                            <label style="font-size:0.75rem; font-weight:700;">Days Count *</label>
                            <input type="number" id="app-leave-days" class="form-control" value="1" min="1" required style="font-size:0.8rem; padding:6px 10px;">
                        </div>
                        <div class="form-group" style="margin-bottom:14px;">
                            <label style="font-size:0.75rem; font-weight:700;">Reason *</label>
                            <textarea id="app-leave-reason" class="form-control" rows="2" placeholder="State reason for leave" required style="font-size:0.8rem; padding:6px 10px;"></textarea>
                        </div>
                        <button type="submit" class="btn btn-primary" style="width:100%; font-size:0.85rem; font-weight:700; background:#2563eb; border:none; border-radius:6px; padding:9px;">
                            📤 Submit Leave to Director Rajeev Sinha
                        </button>
                    </form>
                </div>
            `;
        } else if (window.appActiveTab === 'complaints') {
            tabContent = `
                <!-- Teacher Report Broken Computer in Lab -->
                <div style="background:#ffffff; border:1px solid #e2e8f0; border-radius:12px; padding:16px;">
                    <div style="font-size:0.95rem; font-weight:800; color:#0f172a;">💻 Report Faulty Computer in Lab</div>
                    <div style="font-size:0.72rem; color:#dc2626; font-weight:600; margin-bottom:12px;">
                        Submitted to IT Support Administrator & Director for Repair Order Authorization.
                    </div>
                    <form onsubmit="submitAppTeacherComplaint(event)">
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px;">
                            <div class="form-group">
                                <label style="font-size:0.75rem; font-weight:700;">Lab Room *</label>
                                <select id="app-comp-lab" class="form-control" style="font-size:0.8rem; padding:6px 10px;">
                                    <option value="Computer Lab 1">Computer Lab 1</option>
                                    <option value="Computer Lab 2">Computer Lab 2</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label style="font-size:0.75rem; font-weight:700;">PC Number *</label>
                                <input type="text" id="app-comp-pc" class="form-control" placeholder="e.g. PC-04" required style="font-size:0.8rem; padding:6px 10px;">
                            </div>
                        </div>
                        <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px;">
                            <div class="form-group">
                                <label style="font-size:0.75rem; font-weight:700;">Issue Category *</label>
                                <select id="app-comp-cat" class="form-control" style="font-size:0.8rem; padding:6px 10px;">
                                    <option value="Hardware / Power">Hardware / Power</option>
                                    <option value="Display / Monitor">Display / Monitor</option>
                                    <option value="OS / Boot Failure">OS / Boot Failure</option>
                                    <option value="Networking / LAN">Networking / LAN</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label style="font-size:0.75rem; font-weight:700;">Priority *</label>
                                <select id="app-comp-priority" class="form-control" style="font-size:0.8rem; padding:6px 10px;">
                                    <option value="High">High</option>
                                    <option value="Critical">Critical</option>
                                    <option value="Medium">Medium</option>
                                    <option value="Low">Low</option>
                                </select>
                            </div>
                        </div>
                        <div class="form-group" style="margin-bottom:14px;">
                            <label style="font-size:0.75rem; font-weight:700;">Problem Description *</label>
                            <textarea id="app-comp-desc" class="form-control" rows="2" placeholder="Describe the hardware defect in detail" required style="font-size:0.8rem; padding:6px 10px;"></textarea>
                        </div>
                        <button type="submit" class="btn btn-danger" style="width:100%; font-size:0.85rem; font-weight:700; background:#dc2626; border:none; border-radius:6px; padding:9px;">
                            🚨 Submit Complaint to IT & Director
                        </button>
                    </form>
                </div>
            `;
        }

        screenBody.innerHTML = `
            ${appHeaderHtml}
            <div style="padding:14px; flex:1; background:#f8fafc;">
                ${tabContent}
            </div>
        `;
        return;
    }
}
'''

with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    orig = f.read()

if 'function renderCampusApp' not in orig:
    with open('school_website/js/app.js', 'a', encoding='utf-8') as f:
        f.write('\n' + app_js_code)
    print("✓ Appended Campus App code to app.js!")
else:
    print("! renderCampusApp already in app.js")
