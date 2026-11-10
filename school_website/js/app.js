
// State variables for Multi-Child Parent Portal & E-Library Management
let parentOverviewData = null;
let parentSelectedChildIndex = 0;
let parentTimetableChildIndex = 0;
let libraryDataCache = null;
let libraryStudentsCache = null;

function isAdministrationUser() {
    if (!currentUser) return false;
    const r = currentRole;
    return r === 'librarian' || r === 'super_admin' || r === 'admin' ||
           currentUser.username === 'Owner(Directer)' ||
           (currentUser.name && (currentUser.name.includes('Rajeev Sinha') || currentUser.name.includes('Director')));
}

function switchParentActiveChild(idx) {
    parentSelectedChildIndex = idx;
    parentTimetableChildIndex = idx;
    renderParentDashboard();
}

function switchParentTimetableChild(idx) {
    parentTimetableChildIndex = idx;
    renderTimetableTab();
}

function generateClientClassTimetable(className, sectionName = 'Section A') {
    const c = (className || '').toLowerCase();
    const periods = ['08:00 - 08:45', '08:45 - 09:30', '09:30 - 10:15', '10:45 - 11:30', '11:30 - 12:15', '12:15 - 01:00', '01:30 - 02:15'];
    if (c.includes('science')) {
        return {
            periods,
            days: [
                { day: 'Monday', subjects: ['Physics (Mechanics)', 'Chemistry (Organic)', 'Mathematics / Biology', 'English Core', 'Computer Science', 'Physical Education', 'Physics Lab'] },
                { day: 'Tuesday', subjects: ['Chemistry Lab', 'Chemistry (Inorganic)', 'Physics', 'Mathematics', 'English Core', 'Biology / IP', 'Library & Research'] },
                { day: 'Wednesday', subjects: ['Mathematics', 'Physics', 'Biology Lab', 'Chemistry', 'English Core', 'STEM Projects', 'Sports / Games'] },
                { day: 'Thursday', subjects: ['Physics (Optics)', 'Mathematics', 'Chemistry (Physical)', 'English', 'Biology / CS', 'Doubt Clearing', 'Practical Lab'] },
                { day: 'Friday', subjects: ['Computer Science Lab', 'Mathematics', 'Physics', 'Chemistry', 'English Debate', 'Moral Education', 'Club Activities'] }
            ]
        };
    } else if (c.includes('commerce')) {
        return {
            periods,
            days: [
                { day: 'Monday', subjects: ['Accountancy', 'Business Studies', 'Economics', 'English Core', 'Informatics Practices', 'Mathematics', 'Commerce Lab'] },
                { day: 'Tuesday', subjects: ['Business Studies', 'Accountancy', 'Economics', 'English Core', 'Applied Maths', 'Library Period', 'Financial Literacy'] },
                { day: 'Wednesday', subjects: ['Economics (Macro)', 'Accountancy', 'Business Studies', 'English', 'Informatics Lab', 'Physical Edu.', 'Case Study Seminar'] },
                { day: 'Thursday', subjects: ['Accountancy Workshop', 'Economics', 'Business Law', 'Applied Maths', 'English', 'Career Guidance', 'Project Work'] },
                { day: 'Friday', subjects: ['Business Studies', 'Accountancy', 'Economics', 'English', 'Entrepreneurship', 'Assembly / Quiz', 'Sports & Games'] }
            ]
        };
    } else if (c.includes('humanities') || c.includes('arts')) {
        return {
            periods,
            days: [
                { day: 'Monday', subjects: ['History', 'Political Science', 'Geography', 'English Core', 'Sociology / Economics', 'Psychology', 'Library Research'] },
                { day: 'Tuesday', subjects: ['Political Science', 'History', 'Geography Lab', 'English Core', 'Economics', 'Creative Writing', 'Debate Society'] },
                { day: 'Wednesday', subjects: ['Geography', 'Sociology', 'History', 'Political Science', 'English Literature', 'Fine Arts', 'Social Service / SUPW'] },
                { day: 'Thursday', subjects: ['History Seminar', 'Political Science', 'Economics', 'Geography', 'English Core', 'Heritage Studies', 'Project Work'] },
                { day: 'Friday', subjects: ['English Literature', 'History', 'Geography', 'Political Science', 'Current Affairs', 'Assembly', 'Music & Drama'] }
            ]
        };
    } else if (c.includes('class 9') || c.includes('class 10')) {
        return {
            periods,
            days: [
                { day: 'Monday', subjects: ['Mathematics', 'English Lang.', 'Physics', 'Chemistry', 'Biology', 'Social Science (History)', 'Computer Lab'] },
                { day: 'Tuesday', subjects: ['English Lang.', 'Mathematics', 'Social Science (Civics)', 'Physics', 'Chemistry', 'Biology', 'Library Period'] },
                { day: 'Wednesday', subjects: ['Chemistry', 'Physics', 'Mathematics', 'Computer Science', 'English Lang.', 'Physical Edu.', 'STEM Workshop'] },
                { day: 'Thursday', subjects: ['Biology', 'Social Science (Geography)', 'Chemistry', 'Mathematics', 'Physics', 'Moral Science', 'Science Practical'] },
                { day: 'Friday', subjects: ['Mathematics', 'English Lang.', 'Computer Lab', 'Science Composite Lab', 'Social Science', 'Assembly', 'Sports & Games'] }
            ]
        };
    } else if (c.includes('class 6') || c.includes('class 7') || c.includes('class 8')) {
        return {
            periods,
            days: [
                { day: 'Monday', subjects: ['Foundational Mathematics', 'English Grammar', 'General Science', 'Social Studies', 'Hindi / Language II', 'Arts & Crafts', 'Games & Physical Edu.'] },
                { day: 'Tuesday', subjects: ['English Literature', 'Mathematics', 'Social Studies', 'General Science', 'Hindi', 'Library Reading', 'Music & Yoga'] },
                { day: 'Wednesday', subjects: ['General Science', 'Social Studies', 'Mathematics', 'Computer ICT', 'English', 'Physical Education', 'Activity Club'] },
                { day: 'Thursday', subjects: ['Social Studies', 'Mathematics', 'General Science', 'Hindi', 'English', 'Moral Science', 'Science Discovery Lab'] },
                { day: 'Friday', subjects: ['Mathematics', 'English Comprehension', 'Computer Lab', 'General Science', 'Art & Craft', 'Assembly / Quiz', 'Sports & PT'] }
            ]
        };
    } else {
        return {
            periods,
            days: [
                { day: 'Monday', subjects: ['English Phonics & Reading', 'Mathematics (Numeracy)', 'Environmental Studies', 'Hindi / Regional', 'Drawing & Colouring', 'Rhymes & Storytelling', 'Playground Games'] },
                { day: 'Tuesday', subjects: ['Mathematics', 'English Handwriting', 'Environmental Studies', 'Hindi', 'Activity Worksheet', 'Library Picture Books', 'Music & Dance'] },
                { day: 'Wednesday', subjects: ['Environmental Studies', 'Mathematics', 'English Rhymes', 'Basic Computer Basics', 'Hindi', 'Clay Modelling / Craft', 'Physical Exercises'] },
                { day: 'Thursday', subjects: ['English Conversation', 'Mathematics Fun', 'EVS Practical', 'Moral Stories', 'Hindi', 'Games & Fun Activities', 'Free Play'] },
                { day: 'Friday', subjects: ['Mathematics Puzzles', 'English Story Time', 'Environmental Quiz', 'Art & Origami', 'Children Assembly', 'Moral Education', 'Sports & Recreation'] }
            ]
        };
    }
}

// State Management
let currentUser = null;
let currentRole = 'super_admin';
let currentTab = 'dashboard';
let currentStudentId = 1;
let siteData = {
    stats: {},
    students: [],
    teachers: [],
    classes: [],
    subjects: [],
    payments: [],
    notices: [],
    books: [],
    settings: {},
    users: []
};

// IT Access Helper: Checks if current user is IT Support (GS_itsupport or any future IT User ID)
function isITUser(user) {
    if (!user) return false;
    const role = (user.user_type || '').toLowerCase();
    const uname = (user.username || '').toLowerCase();
    return role === 'it_admin' || role === 'it_support' || role.includes('it_') || uname.startsWith('gs_it') || uname.startsWith('it_') || uname.includes('itsupport');
}

// 7 Distinct Roles with Strict Allowed Navigation Menus
// STRICT REQUIREMENT: Laptop & PC Asset Manager is exclusively used by ONLY IT Support (or any future IT User ID)
const ROLE_ALLOWED_TABS = {
    'super_admin': ['dashboard', 'users', 'credentials', 'teachers', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'lab_manager', 'lab_complaints', 'notices', 'settings'],
    'admin': ['dashboard', 'students', 'classes', 'marks', 'payments', 'leaves', 'payroll', 'inquiries', 'library', 'lab_manager', 'lab_complaints', 'notices'],
    'teacher': ['dashboard', 'attendance', 'marks', 'timetable', 'leaves', 'payroll', 'library', 'lab_complaints', 'notices'],
    'student': ['dashboard', 'marksheet', 'timetable', 'payments', 'library', 'notices'],
    'parent': ['dashboard', 'marksheet', 'timetable', 'attendance', 'payments', 'notices'],
    'accountant': ['dashboard', 'payments', 'leaves', 'payroll', 'students', 'notices'],
    'librarian': ['dashboard', 'library', 'notices'],
    'it_admin': ['dashboard', 'users', 'credentials', 'asset_management', 'lab_manager', 'lab_complaints', 'notices'],
    'common_id': ['dashboard', 'lab_complaints', 'notices']
};

// 7 Unique Role Profiles & Login Credentials Directory for Greenland School
const UNIQUE_ROLE_ACCOUNTS = [
    {
        roleKey: 'super_admin',
        roleTitle: 'Owner (Director)',
        name: 'Owner (Director) Rajeev Sinha',
        username: 'Owner(Directer)',
        password: 'Viratsingh@2004',
        email: 'director@greenlandschool.net',
        badgeClass: 'role-super_admin',
        icon: '👑',
        photo: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150',
        desc: 'Master institutional executive oversight, faculty bonus & permissions'
    },
    {
        roleKey: 'super_admin',
        roleTitle: 'Super Admin',
        name: 'Super Admin',
        username: 'GS_superadmin',
        password: 'Greenland@2026',
        email: 'superadmin@greenlandschool.net',
        badgeClass: 'role-super_admin',
        icon: '👑',
        photo: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150',
        desc: 'Master system control, user accounts & credential override'
    },
    {
        roleKey: 'admin',
        roleTitle: 'Administrator',
        name: 'Admin',
        username: 'GS_admin',
        password: 'Greenland@2026',
        email: 'admin@greenlandschool.net',
        badgeClass: 'role-admin',
        icon: '🛡️',
        photo: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150',
        desc: 'Academic structures, students, class arms & timetable'
    },
    {
        roleKey: 'teacher',
        roleTitle: 'Teacher',
        name: 'Teacher Chike',
        username: 'GS_teacher',
        password: 'Greenland@2026',
        email: 'teacher.chike@greenlandschool.net',
        badgeClass: 'role-teacher',
        icon: '👨‍🏫',
        photo: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=150',
        desc: 'Daily attendance register & exam scores continuous assessment'
    },
    {
        roleKey: 'student',
        roleTitle: 'Student',
        name: 'Student Alex Morgan',
        username: 'GS_student',
        password: 'Greenland@2026',
        email: 'student.alex@greenlandschool.net',
        badgeClass: 'role-student',
        icon: '🎓',
        photo: 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=150',
        desc: 'Personal terminal report card, schedule & fee receipts'
    },
    {
        roleKey: 'parent',
        roleTitle: 'Parent',
        name: 'Parent Marcus Kaba',
        username: 'GS_parent_Alex_and_Clara',
        password: 'Greenland@2026',
        email: 'parent.kaba@greenlandschool.net',
        badgeClass: 'role-parent',
        icon: '👨‍👩‍👧',
        photo: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=150',
        desc: 'Child academic progress, attendance percentage & fee invoice'
    },
    {
        roleKey: 'accountant',
        roleTitle: 'Accountant',
        name: 'Accountant Jude Bello',
        username: 'GS_accountant',
        password: 'Greenland@2026',
        email: 'bursar@greenlandschool.net',
        badgeClass: 'role-accountant',
        icon: '💰',
        photo: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?w=150',
        desc: 'Tuition fees ledger, invoice generation & payment receipts'
    },
    {
        roleKey: 'it_admin',
        roleTitle: 'IT Support Administrator',
        name: 'IT Support Administrator',
        username: 'GS_itsupport',
        password: 'Greenland@2026',
        email: 'itsupport@greenlandschool.net',
        badgeClass: 'role-it_admin',
        icon: '💻',
        photo: 'https://images.unsplash.com/photo-1531482615713-2afd69097998?w=150',
        desc: 'Top-level IT administrative oversight, computer lab infrastructure & repair dispatch'
    },
    {
        roleKey: 'librarian',
        roleTitle: 'Librarian',
        name: 'Librarian Rose Davies',
        username: 'GS_librarian',
        password: 'Greenland@2026',
        email: 'library@greenlandschool.net',
        badgeClass: 'role-librarian',
        icon: '📚',
        photo: 'https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=150',
        desc: 'Books catalogue, inventory management & issue requests'
    }
];

function handleHashNavigation() {
    const hash = window.location.hash;
    const path = window.location.pathname;
    if (hash === '#app' || hash === '#campus-app' || path === '/app') {
        openCampusApp();
    } else if (hash === '#portal' || path === '/portal') {
        if (currentUser) {
            openPortal();
        } else {
            openPortalLogin();
        }
    } else if (hash === '#login' || path === '/login') {
        openPortalLogin();
    } else if (hash === '' || hash === '#home') {
        if (!currentUser) {
            openPublicSite();
        }
    }
}

// Initialize Application
document.addEventListener('DOMContentLoaded', () => {
    loadInitialData();

    // Check saved session
    const saved = localStorage.getItem('gs_auth_user') || localStorage.getItem('cjia_auth_user');
    if (saved) {
        try {
            currentUser = JSON.parse(saved);
            currentRole = currentUser.user_type;
        } catch (e) {
            currentUser = null;
        }
    }

    handleHashNavigation();
    window.addEventListener('hashchange', handleHashNavigation);

    // Online admission inquiry listener
    const admForm = document.getElementById('admission-inquiry-form');
    if (admForm) {
        admForm.addEventListener('submit', handleAdmissionSubmit);
    }
});

// Load core data from backend
async function loadInitialData() {
    try {
        const [statsRes, classesRes, noticesRes, settingsRes] = await Promise.all([
            fetch('/api/stats').then(r => r.json()),
            fetch('/api/classes').then(r => r.json()),
            fetch('/api/notices').then(r => r.json()),
            fetch('/api/settings').then(r => r.json())
        ]);

        siteData.stats = statsRes;
        siteData.classes = classesRes;
        siteData.notices = noticesRes;
        siteData.settings = settingsRes;

        renderPublicNotices();
    } catch (err) {
        console.error('Error loading initial data:', err);
    }
}

// Render notices on the public website
function renderPublicNotices() {
    const container = document.getElementById('public-notices-grid');
    if (!container || !siteData.notices) return;

    container.innerHTML = siteData.notices.slice(0, 4).map(n => `
        <div class="notice-card">
            <div class="notice-meta">
                <span class="notice-tag">${n.category}</span>
                <span class="notice-date">${n.date}</span>
            </div>
            <h4 class="notice-title">${n.title}</h4>
            <p class="notice-snippet">${n.content}</p>
        </div>
    `).join('');
}

// =====================================================================
// AUTHENTICATION & STRICT ISOLATION
// =====================================================================
function openPublicSite() {
    const login = document.getElementById('portal-login-view');
    const port = document.getElementById('portal-container');
    const appView = document.getElementById('campus-app-view');
    const pub = document.getElementById('public-website');
    if (login) login.style.display = 'none';
    if (port) port.style.display = 'none';
    if (appView) appView.style.display = 'none';
    if (pub) pub.style.display = 'block';
    window.location.hash = '';
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function openPortalLogin(e) {
    if (e && e.preventDefault) e.preventDefault();
    const pub = document.getElementById('public-website');
    const port = document.getElementById('portal-container');
    const appView = document.getElementById('campus-app-view');
    const login = document.getElementById('portal-login-view');
    if (pub) pub.style.display = 'none';
    if (port) port.style.display = 'none';
    if (appView) appView.style.display = 'none';
    if (login) login.style.display = 'flex';
    if (window.location.hash !== '#login') {
        window.location.hash = '#login';
    }

    const err = document.getElementById('login-error-msg');
    if (err) err.style.display = 'none';
    const success = document.getElementById('login-success-msg');
    if (success) success.style.display = 'none';
    const usr = document.getElementById('login-username');
    if (usr) usr.focus();
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

    const confirmMsg = `Are you sure you want to permanently delete User ID '${username}'?\n\n• This account will no longer be able to log in.\n• The User ID will be immediately removed from the Login Page Directory.`;
    if (!confirm(confirmMsg)) return;

    try {
        const res = await fetch('/api/users/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ user_id: userId, username: username })
        }).then(r => r.json());

        if (res.success) {
            alert(`✓ ${res.message}`);
            closeModal('modal-assign-user-role');
            closeModal('modal-it-request-change-creds');
            if (typeof renderUsersTab === 'function' && currentTab === 'users') renderUsersTab();
            if (typeof renderCredentialsTab === 'function' && currentTab === 'credentials') renderCredentialsTab();
            if (typeof loadLoginDirectory === 'function') loadLoginDirectory();
        } else {
            alert(`❌ Error: ${res.error || res.message || 'Failed to delete user ID.'}`);
        }
    } catch (err) {
        alert(`❌ Network or server error while deleting user ID: ${err.message}`);
    }
}

function fillLoginUsername(username) {
    const usr = document.getElementById('login-username');
    const pwd = document.getElementById('login-password');
    if (usr) {
        usr.value = username;
    }
    if (pwd) {
        if (username === 'GS_teacher' || username.startsWith('GS_teacher')) {
            pwd.value = 'Greenland@2026';
        } else {
            pwd.value = '';
        }
        pwd.focus();
    }
    const err = document.getElementById('login-error-msg');
    if (err) err.style.display = 'none';
    const success = document.getElementById('login-success-msg');
    if (success) {
        success.innerText = `Teacher account selected (${username}). Click 'Sign In' or press Enter to continue.`;
        success.style.display = 'block';
    }
}

function fillLoginCredentials(username, password) {
    fillLoginUsername(username);
}

function openPortal() {
    if (!currentUser) {
        openPortalLogin();
        return;
    }

    currentRole = currentUser.user_type;

    const pub = document.getElementById('public-website');
    const login = document.getElementById('portal-login-view');
    const appView = document.getElementById('campus-app-view');
    const port = document.getElementById('portal-container');
    if (pub) pub.style.display = 'none';
    if (login) login.style.display = 'none';
    if (appView) appView.style.display = 'none';
    if (port) port.style.display = 'block';
    window.location.hash = '#portal';

    updatePortalHeaderAndSession();
    updateSidebarForRole(currentRole);

    // Automatically navigate to default tab
    showTab('dashboard');
}

async function handlePortalLogin(e) {
    e.preventDefault();
    const username = document.getElementById('login-username').value.trim();
    const password = document.getElementById('login-password').value.trim();
    executeLogin(username, password);
}

async function executeLogin(username, password) {
    const errorDiv = document.getElementById('login-error-msg');
    const successDiv = document.getElementById('login-success-msg');
    const submitBtn = document.getElementById('btn-portal-login');
    if (errorDiv) errorDiv.style.display = 'none';
    if (successDiv) successDiv.style.display = 'none';

    if (!username || !password) {
        if (errorDiv) {
            errorDiv.innerText = 'Please enter both your User ID and Password.';
            errorDiv.style.display = 'block';
        }
        return;
    }

    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerText = 'Signing in...';
    }

    try {
        const res = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        const data = await res.json();

        if (data.success && data.user) {
            currentUser = data.user;
            currentRole = data.user.user_type;
            localStorage.setItem('gs_auth_user', JSON.stringify(data.user));
            localStorage.removeItem('cjia_auth_user');

            if (successDiv) {
                successDiv.innerText = `Welcome, ${data.user.name}! Opening ${formatRoleName(data.user.user_type)} Portal...`;
                successDiv.style.display = 'block';
            }

            setTimeout(() => {
                openPortal();
            }, 300);
        } else {
            if (errorDiv) {
                errorDiv.innerText = data.message || 'Invalid User ID or Password.';
                errorDiv.style.display = 'block';
            }
        }
    } catch (err) {
        if (errorDiv) {
            errorDiv.innerText = 'Unable to connect to school authentication server. Please ensure the server is running (python run_website.py).';
            errorDiv.style.display = 'block';
        }
    } finally {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerText = '🔐 Sign In to Portal';
        }
    }
}

function handlePortalLogout() {
    currentUser = null;
    localStorage.removeItem('gs_auth_user');
    localStorage.removeItem('cjia_auth_user');
    openPortalLogin();
}

// =====================================================================
// FORGOT PASSWORD & SELF-SERVICE RECOVERY MODAL
// =====================================================================
let forgotVerifiedUserId = null;

function openForgotPasswordModal() {
    forgotVerifiedUserId = null;
    const alertDiv = document.getElementById('forgot-alert-msg');
    if (alertDiv) alertDiv.style.display = 'none';

    const step1 = document.getElementById('forgot-step-1');
    const step2 = document.getElementById('forgot-step-2');
    if (step1) step1.style.display = 'block';
    if (step2) step2.style.display = 'none';

    const inp = document.getElementById('forgot-username-input');
    if (inp) {
        inp.value = '';
        setTimeout(() => inp.focus(), 150);
    }
    const newPass = document.getElementById('forgot-new-pass');
    if (newPass) newPass.value = '';
    const confPass = document.getElementById('forgot-confirm-pass');
    if (confPass) confPass.value = '';

    openModal('modal-forgot-password');
}

async function handleVerifyForgotUser() {
    const alertDiv = document.getElementById('forgot-alert-msg');
    if (alertDiv) alertDiv.style.display = 'none';

    const inputVal = document.getElementById('forgot-username-input').value.trim();
    if (!inputVal) {
        if (alertDiv) {
            alertDiv.className = 'login-alert error';
            alertDiv.innerText = 'Please enter your User ID or registered Email address.';
            alertDiv.style.display = 'block';
        }
        return;
    }

    const btn = document.getElementById('btn-verify-forgot');
    if (btn) {
        btn.disabled = true;
        btn.innerText = 'Verifying Account...';
    }

    try {
        const res = await fetch('/api/forgot-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'verify', username_or_email: inputVal })
        });
        const data = await res.json();

        if (data.success && data.user_id) {
            forgotVerifiedUserId = data.user_id;
            const nameEl = document.getElementById('forgot-user-name-display');
            const metaEl = document.getElementById('forgot-user-meta-display');
            if (nameEl) nameEl.innerText = data.name;
            if (metaEl) metaEl.innerText = `Role: ${data.role} | User ID: ${data.username} | Email: ${data.email}`;

            document.getElementById('forgot-step-1').style.display = 'none';
            document.getElementById('forgot-step-2').style.display = 'block';
            setTimeout(() => {
                const p = document.getElementById('forgot-new-pass');
                if (p) p.focus();
            }, 100);
        } else {
            if (alertDiv) {
                alertDiv.className = 'login-alert error';
                alertDiv.innerText = data.message || 'No matching account found.';
                alertDiv.style.display = 'block';
            }
        }
    } catch (e) {
        if (alertDiv) {
            alertDiv.className = 'login-alert error';
            alertDiv.innerText = 'Unable to connect to school server. Please try again.';
            alertDiv.style.display = 'block';
        }
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerText = '🔍 Verify Account Identity';
        }
    }
}

async function handleResetForgotPass() {
    const alertDiv = document.getElementById('forgot-alert-msg');
    if (alertDiv) alertDiv.style.display = 'none';

    if (!forgotVerifiedUserId) {
        if (alertDiv) {
            alertDiv.className = 'login-alert error';
            alertDiv.innerText = 'Verification expired. Please re-enter your User ID.';
            alertDiv.style.display = 'block';
        }
        return;
    }

    const newPass = document.getElementById('forgot-new-pass').value.trim();
    const confPass = document.getElementById('forgot-confirm-pass').value.trim();

    if (!newPass) {
        if (alertDiv) {
            alertDiv.className = 'login-alert error';
            alertDiv.innerText = 'Please enter a new password.';
            alertDiv.style.display = 'block';
        }
        return;
    }

    if (newPass.length < 4) {
        if (alertDiv) {
            alertDiv.className = 'login-alert error';
            alertDiv.innerText = 'Password must be at least 4 characters long.';
            alertDiv.style.display = 'block';
        }
        return;
    }

    if (newPass !== confPass) {
        if (alertDiv) {
            alertDiv.className = 'login-alert error';
            alertDiv.innerText = 'Passwords do not match. Please re-enter carefully.';
            alertDiv.style.display = 'block';
        }
        return;
    }

    const btn = document.getElementById('btn-reset-forgot');
    if (btn) {
        btn.disabled = true;
        btn.innerText = 'Saving Password...';
    }

    try {
        const res = await fetch('/api/forgot-password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                action: 'reset',
                user_id: forgotVerifiedUserId,
                new_password: newPass
            })
        });
        const data = await res.json();

        if (data.success) {
            closeModal('modal-forgot-password');
            const loginSuccessDiv = document.getElementById('login-success-msg');
            if (loginSuccessDiv) {
                loginSuccessDiv.innerText = data.message || 'Password reset successfully! Log in with your new password.';
                loginSuccessDiv.style.display = 'block';
            }
            if (data.username) {
                const usrInp = document.getElementById('login-username');
                if (usrInp) usrInp.value = data.username;
            }
            const pwdInp = document.getElementById('login-password');
            if (pwdInp) {
                pwdInp.value = '';
                pwdInp.focus();
            }
        } else {
            if (alertDiv) {
                alertDiv.className = 'login-alert error';
                alertDiv.innerText = data.message || 'Password reset failed.';
                alertDiv.style.display = 'block';
            }
        }
    } catch (e) {
        if (alertDiv) {
            alertDiv.className = 'login-alert error';
            alertDiv.innerText = 'Server error during password reset. Please try again.';
            alertDiv.style.display = 'block';
        }
    } finally {
        if (btn) {
            btn.disabled = false;
            btn.innerText = '💾 Save New Password & Proceed';
        }
    }
}

function togglePasswordVisibility(inputId) {
    const input = document.getElementById(inputId);
    if (input) {
        input.type = input.type === 'password' ? 'text' : 'password';
    }
}

function updatePortalHeaderAndSession() {
    if (!currentUser) return;
    const nameEl = document.getElementById('banner-current-user-name');
    const roleEl = document.getElementById('banner-current-user-role');
    const idEl = document.getElementById('banner-current-user-id');
    const avatarEl = document.getElementById('portal-user-avatar');
    const userNameEl = document.getElementById('portal-user-name');
    const userBadgeEl = document.getElementById('portal-user-badge');

    if (nameEl) nameEl.innerText = currentUser.name;
    if (roleEl) roleEl.innerText = `${formatRoleName(currentUser.user_type).toUpperCase()} PORTAL`;
    if (idEl) idEl.innerText = currentUser.username;
    if (avatarEl) avatarEl.src = currentUser.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150';
    if (userNameEl) userNameEl.innerText = currentUser.name;
    if (userBadgeEl) userBadgeEl.innerText = formatRoleName(currentUser.user_type);
}

function formatRoleName(role) {
    if (currentUser && (currentUser.username === 'Owner(Directer)' || (currentUser.name && (currentUser.name.includes('Rajeev Sinha') || currentUser.name.includes('Director'))))) {
        return 'Owner (Director)';
    }
    const map = {
        'super_admin': 'Super Admin',
        'admin': 'Administrator',
        'teacher': 'Teacher',
        'student': 'Student',
        'parent': 'Parent',
        'accountant': 'Accountant',
        'librarian': 'Librarian',
        'it_admin': 'IT Support Administrator',
        'common_id': '🏷️ Common ID (Lab Fleet)'
    };
    return map[role] || role;
}

// Strictly configure sidebar tabs according to the logged-in role
function updateSidebarForRole(role) {
    const allowed = ROLE_ALLOWED_TABS[role] || ROLE_ALLOWED_TABS['super_admin'];

    document.querySelectorAll('.sidebar-nav li').forEach(li => {
        const tab = li.dataset.tab;
        if (tab) {
            let isPermitted = allowed.includes(tab);
            // STRICT REQUIREMENT: Laptop & PC Asset Manager is accessible by ONLY IT Support (current and future IT User IDs)
            if (tab === 'asset_management') {
                isPermitted = isITUser(currentUser);
            }
            li.style.display = isPermitted ? 'block' : 'none';
        }
    });
}

// Enforce tab-level authorization
function showTab(tabName) {
    if (!currentUser) {
        openPortalLogin();
        return;
    }

    // STRICT REQUIREMENT: Laptop & PC Asset Manager can ONLY be used by IT Support
    if (tabName === 'asset_management') {
        if (!isITUser(currentUser)) {
            alert("🔒 Access Restricted: The Laptop & PC Asset Management System is exclusively reserved for IT Support Administrator accounts (and any future IT User IDs).");
            tabName = 'dashboard';
        }
    }

    const allowed = ROLE_ALLOWED_TABS[currentRole] || [];
    if (!allowed.includes(tabName) && !(tabName === 'marksheet' && (currentRole === 'super_admin' || currentRole === 'admin')) && !(tabName === 'asset_management' && isITUser(currentUser))) {
        tabName = 'dashboard';
    }

    currentTab = tabName;

    // Update active nav link
    document.querySelectorAll('.sidebar-nav a').forEach(a => {
        a.classList.toggle('active', a.dataset.tab === tabName);
    });

    const main = document.getElementById('portal-tab-content');
    main.innerHTML = `<div style="text-align:center; padding:40px; color:#64748b;">Loading ${tabName}...</div>`;

    switch (tabName) {
        case 'dashboard':
            renderDashboardTab();
            break;
        case 'users':
            if (['super_admin', 'it_admin'].includes(currentRole)) {
                renderUsersTab();
            } else {
                renderDashboardTab();
            }
            break;
        case 'teachers':
            if (currentRole === 'super_admin') {
                renderTeachersTab();
            } else {
                renderDashboardTab();
            }
            break;
        case 'leaves':
            if (['teacher', 'admin', 'super_admin', 'accountant'].includes(currentRole)) {
                renderLeavesTab();
            } else {
                renderDashboardTab();
            }
            break;
        case 'payroll':
            if (['teacher', 'admin', 'super_admin', 'accountant'].includes(currentRole)) {
                renderPayrollTab();
            } else {
                renderDashboardTab();
            }
            break;
        case 'inquiries':
            if (['admin', 'super_admin'].includes(currentRole)) {
                renderInquiriesTab();
            } else {
                renderDashboardTab();
            }
            break;
        case 'credentials':
            if (['it_admin', 'super_admin'].includes(currentRole)) {
                renderCredentialsTab();
            } else {
                renderDashboardTab();
            }
            break;
        case 'asset_management':
            if (['it_admin', 'super_admin', 'admin'].includes(currentRole)) {
                renderAssetManagementTab();
            } else {
                renderDashboardTab();
            }
            break;
        case 'lab_manager':
            if (['it_admin', 'super_admin', 'admin'].includes(currentRole)) {
                renderLabManagerTab();
            } else {
                renderDashboardTab();
            }
            break;
        case 'lab_complaints':
            if (['it_admin', 'super_admin', 'admin', 'teacher'].includes(currentRole)) {
                renderLabComplaintsTab();
            } else {
                renderDashboardTab();
            }
            break;
        case 'students':
            renderStudentsTab();
            break;
        case 'classes':
            renderClassesTab();
            break;
        case 'marks':
            renderMarksTab();
            break;
        case 'marksheet':
            renderMarksheetTab(currentStudentId);
            break;
        case 'attendance':
            renderAttendanceTab();
            break;
        case 'payments':
            renderPaymentsTab();
            break;
        case 'timetable':
            renderTimetableTab();
            break;
        case 'library':
            renderLibraryTab();
            break;
        case 'notices':
            renderNoticesTab();
            break;
        case 'settings':
            renderSettingsTab();
            break;
        default:
            renderDashboardTab();
    }
}

// =====================================================================
// ROLE-SPECIFIC DASHBOARD VIEWS (STRICT ISOLATION)
// =====================================================================
async function renderDashboardTab() {
    if (currentRole === 'super_admin') {
        renderSuperAdminDashboard();
    } else if (currentRole === 'it_admin') {
        renderITAdminDashboard();
    } else if (currentRole === 'teacher') {
        renderTeacherDashboard();
    } else if (currentRole === 'student') {
        renderStudentDashboard();
    } else if (currentRole === 'parent') {
        renderParentDashboard();
    } else if (currentRole === 'accountant') {
        renderAccountantDashboard();
    } else if (currentRole === 'librarian') {
        renderLibrarianDashboard();
    } else {
        renderAdminDashboard();
    }
}

// 1. SUPER ADMIN EXCLUSIVE DASHBOARD
async function renderSuperAdminDashboard() {
    const stats = await fetch('/api/stats').then(r => r.json());
    const notices = await fetch('/api/notices').then(r => r.json());

    document.getElementById('portal-header-title').innerText = 'Director Executive Master Dashboard';
    document.getElementById('portal-header-desc').innerText = 'Director Rajeev Sinha: Institutional Governance, Teacher & IT Request Approvals Center';

    // Fetch unified pending requests from Teachers and IT Team
    let pendingData = { total_pending: 0, requests: [] };
    try {
        pendingData = await fetch('/api/director/pending_requests').then(r => r.json());
    } catch (e) {
        console.error("Failed to load director pending requests:", e);
    }

    const approvalDeskHtml = `
        <!-- DIRECTOR EXCLUSIVE APPROVAL DESK (TEACHER & IT TEAM REQUESTS) -->
        <div class="card" style="margin-bottom:22px; border:2px solid #3b82f6; box-shadow:0 8px 24px rgba(37,99,235,0.12);">
            <div class="card-header" style="background:linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%); color:white; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:1.6rem;">👑</span>
                    <div>
                        <div style="font-size:1.05rem; font-weight:800; letter-spacing:0.3px;">Director Exclusive Approvals Desk</div>
                        <div style="font-size:0.75rem; color:#bfdbfe;">
                            Policy Enforcement: Only Director Rajeev Sinha has authority to approve requests created by Teachers or IT Team.
                        </div>
                    </div>
                </div>
                <div>
                    <span style="font-size:0.78rem; font-weight:800; background:${pendingData.total_pending > 0 ? '#ef4444' : '#10b981'}; color:white; padding:4px 12px; border-radius:50px;">
                        ${pendingData.total_pending > 0 ? `🔔 ${pendingData.total_pending} Pending Approvals` : '✅ All Requests Cleared'}
                    </span>
                </div>
            </div>
            <div class="card-body" style="padding:16px;">
                ${pendingData.requests && pendingData.requests.length > 0 ? `
                    <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(310px, 1fr)); gap:12px;">
                        ${pendingData.requests.map(req => {
                            let originBadge = req.origin.includes('Teacher') ? 
                                '<span class="badge" style="background:#eff6ff; color:#1d4ed8; font-weight:700;">👨‍🏫 Teacher Request</span>' :
                                '<span class="badge" style="background:#fef3c7; color:#b45309; font-weight:700;">💻 IT Team Request</span>';
                            
                            let reqTypeKey = 'it_asset';
                            if (req.request_type.includes('Leave')) reqTypeKey = 'teacher_leave';
                            else if (req.request_type.includes('Lab')) reqTypeKey = 'lab_complaint';
                            else if (req.request_type.includes('Credential')) reqTypeKey = 'it_credential';

                            return `
                                <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:10px; padding:14px; display:flex; flex-direction:column; justify-content:space-between; gap:10px;">
                                    <div>
                                        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                                            ${originBadge}
                                            <span style="font-size:0.72rem; color:#64748b; font-family:monospace;">${req.created_at || 'Today'}</span>
                                        </div>
                                        <div style="font-weight:700; color:#0f172a; font-size:0.9rem;">${req.title}</div>
                                        <div style="font-size:0.78rem; color:#475569; margin-top:3px;">${req.description || 'No description provided'}</div>
                                        <div style="font-size:0.74rem; color:#2563eb; margin-top:4px; font-weight:600;">${req.details}</div>
                                        <div style="font-size:0.72rem; color:#64748b; margin-top:3px;">Initiated by: <strong>${req.creator_name}</strong> (${req.creator_username})</div>
                                    </div>
                                    <div style="display:flex; gap:8px; border-top:1px dashed #cbd5e1; padding-top:10px; justify-content:flex-end;">
                                        <button class="btn btn-sm" style="background:#15803d; color:white; font-size:0.76rem; font-weight:700; border:none; padding:5px 12px; cursor:pointer;" onclick="handleDirectorApprove('${reqTypeKey}', ${req.id}, 'approve')">
                                            ✅ Approve Request
                                        </button>
                                        <button class="btn btn-sm" style="background:#dc2626; color:white; font-size:0.76rem; font-weight:700; border:none; padding:5px 10px; cursor:pointer;" onclick="handleDirectorApprove('${reqTypeKey}', ${req.id}, 'reject')">
                                            ❌ Reject
                                        </button>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                ` : `
                    <div style="text-align:center; padding:24px; color:#64748b;">
                        <span style="font-size:2.4rem;">🎉</span>
                        <div style="font-weight:700; color:#1e293b; margin-top:8px;">No Pending Requests from Teachers or IT Team</div>
                        <div style="font-size:0.8rem; color:#94a3b8; margin-top:2px;">All faculty leaves, lab repair authorizations, and IT requests are currently up to date.</div>
                    </div>
                `}
            </div>
        </div>
    `;

    const html = `
        ${approvalDeskHtml}
        <div class="metrics-row">
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Enrolled Students</h5>
                    <h2>${stats.students}</h2>
                    <span style="font-size:0.75rem; color:#10b981;">Active Enrollment</span>
                </div>
                <div class="metric-icon metric-blue">🎓</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Faculty & Staff</h5>
                    <h2>${stats.teachers}</h2>
                    <span style="font-size:0.75rem; color:#64748b;">All Certified</span>
                </div>
                <div class="metric-icon metric-purple">👨‍🏫</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Classes & Arms</h5>
                    <h2>${stats.classes}</h2>
                    <span style="font-size:0.75rem; color:#64748b;">Nursery to SSS 3</span>
                </div>
                <div class="metric-icon metric-amber">🏫</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Total Fee Revenue</h5>
                    <h2>₦${(stats.revenue || 0).toLocaleString()}</h2>
                    <span style="font-size:0.75rem; color:#10b981;">Fee Total</span>
                </div>
                <div class="metric-icon metric-green">💰</div>
            </div>
        </div>

        <div style="display:grid; grid-template-columns: 2fr 1fr; gap:24px;">
            <div class="card">
                <div class="card-header">
                    <span class="card-title">Super Admin Master Controls</span>
                </div>
                <div class="card-body" style="display:flex; gap:12px; flex-wrap:wrap;">
                    <button class="btn btn-secondary" onclick="showTab('users')">🔑 Manage Users & Passwords</button>
                    <button class="btn btn-secondary" onclick="showTab('teachers')">👨‍🏫 Faculty & Teachers</button>
                    <button class="btn btn-secondary" onclick="showTab('leaves')">🏖️ Leave Approvals</button>
                    <button class="btn btn-secondary" onclick="openModal('modal-upload-excel-student')">📊 Upload Student Excel</button>
                    <button class="btn btn-primary" onclick="openModal('modal-admit-student')">➕ Admit New Student</button>
                    <button class="btn btn-outline" onclick="showTab('classes')">🏫 Classes & Arms</button>
                    <button class="btn btn-outline" onclick="showTab('marks')">📝 Terminal Exam Scores</button>
                    <button class="btn btn-outline" onclick="showTab('payments')">💳 Fee Records</button>
                    <button class="btn btn-outline" onclick="openModal('modal-post-notice')">📢 Broadcast Circular</button>
                    <button class="btn btn-outline" onclick="showTab('settings')">⚙️ System Settings</button>
                    <button class="btn btn-danger" style="background:#dc2626; border-color:#b91c1c; font-weight:700;" onclick="confirmCleanTestData()">🧹 Clean All Test Data</button>
                </div>
            </div>

            <div class="card">
                <div class="card-header">
                    <span class="card-title">Recent Circulars</span>
                </div>
                <div class="card-body" style="padding:12px;">
                    ${notices.slice(0, 3).map(n => `
                        <div style="padding:10px 0; border-bottom:1px solid #f1f5f9;">
                            <div style="font-weight:700; font-size:0.85rem; color:#1e3a8a;">${n.title}</div>
                            <div style="font-size:0.78rem; color:#64748b; margin-top:2px;">${n.content.substring(0, 75)}...</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    document.getElementById('portal-tab-content').innerHTML = html;
}

// 2. TEACHER DASHBOARD
async function renderTeacherDashboard() {
    document.getElementById('portal-header-title').innerText = 'Teacher Academic Dashboard';
    document.getElementById('portal-header-desc').innerText = `Teacher: ${currentUser.name} | Assigned Arm: Senior Secondary 3 (SSS 3 - Gold)`;

    const html = `
        <div class="metrics-row">
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Assigned Class</h5>
                    <h2>SSS 3 (Gold)</h2>
                    <span style="font-size:0.75rem; color:#10b981;">Class Teacher</span>
                </div>
                <div class="metric-icon metric-blue">🏫</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Assigned Subjects</h5>
                    <h2>Mathematics, Physics</h2>
                    <span style="font-size:0.75rem; color:#64748b;">Senior Secondary</span>
                </div>
                <div class="metric-icon metric-purple">📐</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Today's Roll Call</h5>
                    <h2>Mark Attendance</h2>
                    <span style="font-size:0.75rem; color:#ca8a04;">Pending Submission</span>
                </div>
                <div class="metric-icon metric-amber">📋</div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">Teacher Quick Actions</span>
            </div>
            <div class="card-body" style="display:flex; gap:12px; flex-wrap:wrap;">
                <button class="btn btn-primary" onclick="showTab('attendance')">📋 Take Class Attendance</button>
                <button class="btn btn-secondary" onclick="openModal('modal-enter-marks')">📝 Enter Subject Exam Scores</button>
                <button class="btn btn-outline" onclick="showTab('timetable')">📅 View Teaching Schedule</button>
                <button class="btn btn-outline" onclick="showTab('notices')">📢 View Circulars</button>
            </div>
        </div>
    `;
    document.getElementById('portal-tab-content').innerHTML = html;
}

// 3. STUDENT DASHBOARD
async function renderStudentDashboard() {
    document.getElementById('portal-header-title').innerText = 'Student Personal Dashboard';
    document.getElementById('portal-header-desc').innerText = `Student: ${currentUser.name} | Greenland School Student Portal`;

    let libData = { library_booklet: [] };
    try {
        libData = await fetch(`/api/library?user_id=${currentUser.id}`).then(r => r.json());
    } catch (e) {
        libData = { library_booklet: [] };
    }
    const myBooklet = libData.library_booklet || [];
    const activeLoans = myBooklet.filter(b => b.status === 'Issued');

    const html = `
        <div class="metrics-row">
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Enrollment Status</h5>
                    <h2>Registered</h2>
                    <span style="font-size:0.75rem; color:#10b981;">Account Active</span>
                </div>
                <div class="metric-icon metric-blue">🎓</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Academic Term</h5>
                    <h2>Term 1</h2>
                    <span style="font-size:0.75rem; color:#15803d;">Session 2026-2027</span>
                </div>
                <div class="metric-icon metric-green">⭐</div>
            </div>
            <div class="metric-card" style="border-left:4px solid #7c3aed;">
                <div class="metric-info">
                    <h5>Library Books In-Hand</h5>
                    <h2>${activeLoans.length}</h2>
                    <span style="font-size:0.75rem; color:#7c3aed;">Active Issued Loans</span>
                </div>
                <div class="metric-icon metric-purple">📚</div>
            </div>
        </div>

        <!-- Student Digital Library Booklet Card (Personalized) -->
        <div class="card" style="margin-bottom:20px; border-left:4px solid #1e3a8a;">
            <div class="card-header" style="display:flex; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:1.2rem;">📘</span>
                    <div>
                        <strong style="color:#0f172a; font-size:1rem;">My Digital Library Booklet</strong>
                        <div style="font-size:0.75rem; color:#64748b;">Showing books strictly issued in your name</div>
                    </div>
                </div>
                <div style="display:flex; gap:8px;">
                    <button class="btn btn-outline btn-sm" onclick="openLibraryBookletModal(${currentUser.id}, '${escapeJs(currentUser.name)}')">
                        🖨️ Print Library Booklet
                    </button>
                    <button class="btn btn-primary btn-sm" onclick="showTab('library')">
                        📚 E-Library Catalogue
                    </button>
                </div>
            </div>
            <div class="card-body" style="padding:0; overflow-x:auto;">
                <table class="data-table" style="font-size:0.83rem;">
                    <thead>
                        <tr>
                            <th>Book Title & Author</th>
                            <th>ISBN</th>
                            <th>Bookshelf Location</th>
                            <th>Issue Date & Exact Time</th>
                            <th>Due Return Date</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${myBooklet.length === 0 ? `
                            <tr>
                                <td colspan="6" style="text-align:center; padding:24px; color:#64748b;">
                                    No books currently issued in your library booklet. Visit the E-Library to borrow textbooks!
                                </td>
                            </tr>
                        ` : myBooklet.map(b => `
                            <tr>
                                <td style="font-weight:700; color:#0f172a;">
                                    ${b.book_title}<br>
                                    <span style="font-size:0.73rem; color:#64748b; font-weight:normal;">by ${b.book_author || 'Author'}</span>
                                </td>
                                <td><code>${b.isbn || '—'}</code></td>
                                <td>
                                    <span class="badge" style="background:#e0e7ff; color:#3730a3; font-weight:700;">
                                        <i class="fas fa-layer-group"></i> ${b.bookshelf_no || 'Shelf A-1'}
                                    </span>
                                </td>
                                <td>
                                    <span style="font-weight:700; color:#1e3a8a;">
                                        <i class="fas fa-clock" style="color:#2563eb; font-size:0.75rem;"></i> ${b.issue_date}
                                    </span>
                                    <div style="font-size:0.72rem; color:#64748b; font-family:monospace;">${b.issue_time || '10:00:00'}</div>
                                </td>
                                <td><span style="color:#b91c1c; font-weight:600;">${b.due_date}</span></td>
                                <td>
                                    <span class="status-pill status-${(b.status || 'Issued').toLowerCase()}">
                                        ${b.status}
                                    </span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card" style="margin-bottom:20px;">
            <div class="card-header">
                <span class="card-title">Student Quick Navigation</span>
            </div>
            <div class="card-body">
                <div style="display:flex; gap:12px; flex-wrap:wrap;">
                    <button class="btn btn-primary" onclick="showTab('marksheet')">📜 Marksheet / Report Sheet</button>
                    <button class="btn btn-outline" onclick="showTab('timetable')">📅 View Class Timetable</button>
                    <button class="btn btn-outline" onclick="showTab('payments')">💳 View My Fee Invoices</button>
                    <button class="btn btn-outline" onclick="showTab('library')">📚 Search E-Library Books</button>
                    <button class="btn btn-outline" onclick="showTab('notices')">📢 School Notices</button>
                </div>
            </div>
        </div>
    `;
    document.getElementById('portal-tab-content').innerHTML = html;
}

// 4. PARENT DASHBOARD (MULTI-CHILD FULL ACCESS)
async function renderParentDashboard() {
    document.getElementById('portal-header-title').innerText = 'Parent & Guardian Portal';
    document.getElementById('portal-header-desc').innerText = `Parent: ${currentUser.name} | Greenland School Guardian Services`;

    let overview = null;
    try {
        overview = await fetch(`/api/parent/overview?parent_id=${currentUser.id || 8}`).then(r => r.json());
        parentOverviewData = overview;
    } catch (e) {
        overview = null;
    }

    if (!overview || !overview.has_student || (!overview.student && (!overview.children || overview.children.length === 0))) {
        document.getElementById('portal-tab-content').innerHTML = `
            <div class="metrics-row">
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Guardian Account</h5>
                        <h2>${currentUser.name}</h2>
                        <span style="font-size:0.75rem; color:#10b981;">Authorized Guardian</span>
                    </div>
                    <div class="metric-icon metric-blue">👨‍👩‍👧</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Academic Session</h5>
                        <h2>2026-2027</h2>
                        <span style="font-size:0.75rem; color:#15803d;">Greenland School</span>
                    </div>
                    <div class="metric-icon metric-green">🏫</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Ward Enrollment</h5>
                        <h2>No Ward Linked</h2>
                        <span style="font-size:0.75rem; color:#e11d48;">Aadhaar Admission Required</span>
                    </div>
                    <div class="metric-icon metric-amber">📋</div>
                </div>
            </div>

            <div class="card" style="text-align:center; padding:45px 25px;">
                <div style="font-size:2.8rem; margin-bottom:12px;">👨‍👩‍👧</div>
                <h3 style="color:#0f172a; margin-bottom:8px; font-weight:800;">No Student Ward Currently Linked</h3>
                <p style="color:#64748b; font-size:0.95rem; max-width:540px; margin:0 auto 20px auto; line-height:1.6;">
                    Welcome, <strong>${currentUser.name}</strong>. No student record is currently linked to your parent portal. Once your child is admitted via the School Admission Desk with their mandatory 12-digit Aadhaar number, their fee due ledger, online payment gateway (UPI QR & Net Banking), and Aadhaar-verified official name editor will appear here automatically.
                </p>
                <div style="display:flex; justify-content:center; gap:12px; flex-wrap:wrap;">
                    <button class="btn btn-primary" onclick="enrollDemoWardForParent()">
                        <i class="fas fa-magic"></i> Enroll Demo Ward: Alex Kaba (Aadhaar: 548962147801)
                    </button>
                    <button class="btn btn-outline" onclick="showTab('notices')">
                        📢 View School Circulars
                    </button>
                </div>
            </div>
        `;
        return;
    }

    const children = overview.children && overview.children.length > 0 ? overview.children : [overview.student];
    if (parentSelectedChildIndex >= children.length) parentSelectedChildIndex = 0;
    const student = children[parentSelectedChildIndex];
    const fee_summary = student.fee_summary || { total_billed: 45000, total_paid: 30000, due_amount: 15000 };
    const payments = student.payments || [];
    const attendance = student.attendance || { total_days: 45, present_days: 44, percentage: 97.8 };
    const timetable = student.timetable || generateClientClassTimetable(student.class_name, student.section_name);
    const dueAmount = fee_summary.due_amount || 0;
    const isDue = dueAmount > 0;

    const html = `
        <!-- Multi-Child Selector Banner (if parent has multiple children) -->
        ${children.length > 1 ? `
            <div class="card" style="background:#f8fafc; border:1.5px solid #93c5fd; border-radius:12px; padding:16px 20px; margin-bottom:20px; box-shadow:0 4px 12px rgba(30,58,138,0.06);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; flex-wrap:wrap; gap:8px;">
                    <div>
                        <span style="font-size:0.85rem; font-weight:800; color:#1e3a8a; text-transform:uppercase; letter-spacing:0.5px;">
                            <i class="fas fa-users" style="color:#2563eb;"></i> Select Enrolled Child / Ward (${children.length} Enrolled under Guardian Account)
                        </span>
                        <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">
                            Switch between your children to view their distinct fees, timetables, and academic records
                        </div>
                    </div>
                    <span style="font-size:0.75rem; background:#eff6ff; color:#1d4ed8; font-weight:700; padding:4px 10px; border-radius:50px; border:1px solid #bfdbfe;">
                        🔒 Single Login Parent Account: <code>${currentUser.username}</code>
                    </span>
                </div>
                <div style="display:flex; gap:12px; flex-wrap:wrap;">
                    ${children.map((c, idx) => `
                        <button type="button" class="btn ${idx === parentSelectedChildIndex ? 'btn-primary' : 'btn-outline'}" 
                                style="display:flex; align-items:center; gap:12px; padding:10px 18px; border-radius:10px; text-align:left; cursor:pointer; ${idx !== parentSelectedChildIndex ? 'background:#fff;' : 'box-shadow:0 4px 12px rgba(30,58,138,0.25);'}"
                                onclick="switchParentActiveChild(${idx})">
                            <span style="font-size:1.6rem;">${c.gender === 'Female' ? '👧' : '👦'}</span>
                            <div>
                                <div style="font-size:0.92rem; font-weight:800;">${c.student_name}</div>
                                <div style="font-size:0.73rem; opacity:0.9; margin-top:2px;">${c.class_name} • ${c.section_name || 'Section A'} (Adm: ${c.adm_no})</div>
                                <div style="margin-top:4px;">
                                    ${(c.fee_summary && c.fee_summary.due_amount > 0) ? `
                                        <span class="badge" style="background:#fee2e2; color:#b91c1c; font-size:0.68rem; font-weight:700; padding:2px 6px; border-radius:4px;">
                                            Fee Due: ₹${c.fee_summary.due_amount.toLocaleString()}
                                        </span>
                                    ` : `
                                        <span class="badge" style="background:#dcfce7; color:#15803d; font-size:0.68rem; font-weight:700; padding:2px 6px; border-radius:4px;">
                                            ✓ Fees Settled
                                        </span>
                                    `}
                                </div>
                            </div>
                        </button>
                    `).join('')}
                </div>
            </div>
        ` : ''}

        <!-- Metrics Row for Active Child -->
        <div class="metrics-row">
            <!-- Ward Profile Card -->
            <div class="metric-card" style="border-left:4px solid #1e3a8a;">
                <div class="metric-info">
                    <h5>Active Student Ward</h5>
                    <h2 style="font-size:1.35rem;">${student.student_name}</h2>
                    <span style="font-size:0.76rem; color:#1e3a8a; font-weight:700;">
                        ${student.class_name} • ${student.section_name || 'Section A'} (Adm: ${student.adm_no})
                    </span>
                    <div style="font-size:0.72rem; color:#64748b; margin-top:3px; font-family:monospace;">
                        ${student.student_email || ''}
                    </div>
                </div>
                <div class="metric-icon metric-blue">${student.gender === 'Female' ? '👧' : '👦'}</div>
            </div>

            <!-- Aadhaar Identity Card -->
            <div class="metric-card" style="border-left:4px solid #10b981;">
                <div class="metric-info">
                    <h5>Official Aadhaar Record</h5>
                    <h2 style="font-size:1.25rem; font-family:monospace; letter-spacing:1px; color:#0f172a;">
                        ${student.masked_aadhaar}
                    </h2>
                    <span style="font-size:0.75rem; color:#15803d; font-weight:700;">
                        <i class="fas fa-shield-alt"></i> Verified 12-Digit Government ID
                    </span>
                    <div style="margin-top:6px;">
                        <button class="btn btn-sm btn-outline" style="font-size:0.74rem; padding:3px 8px; border-color:#94a3b8;"
                                onclick="openParentEditNameModal(${student.student_id}, '${escapeJs(student.student_name)}')">
                            ✏️ Edit Child's Official Name (Verify Aadhaar)
                        </button>
                    </div>
                </div>
                <div class="metric-icon metric-green">🪪</div>
            </div>

            <!-- Outstanding Fee Due Card -->
            <div class="metric-card" style="border-left:4px solid ${isDue ? '#e11d48' : '#16a34a'}; background:${isDue ? '#fff5f5' : '#f0fdf4'};">
                <div class="metric-info">
                    <h5 style="color:${isDue ? '#be123c' : '#15803d'}; font-weight:700;">Outstanding Fee Due</h5>
                    <h2 style="font-size:1.55rem; color:${isDue ? '#b91c1c' : '#15803d'};">
                        ₹${dueAmount.toLocaleString()}
                    </h2>
                    <span style="font-size:0.75rem; color:#475569;">
                        Total Billed: ₹${(fee_summary.total_billed || 0).toLocaleString()} | Paid: ₹${(fee_summary.total_paid || 0).toLocaleString()}
                    </span>
                    <div style="margin-top:8px;">
                        ${isDue ? `
                            <button class="btn btn-sm btn-primary" style="background:#16a34a; border-color:#16a34a; font-weight:700; font-size:0.78rem; padding:6px 12px; box-shadow:0 2px 6px rgba(22,163,74,0.3);"
                                    onclick="openOnlinePaymentModal(${student.student_id}, '${escapeJs(student.student_name)}', '${student.class_name}', '${student.adm_no}', ${dueAmount})">
                                💳 Pay Due Online (UPI / Net Banking)
                            </button>
                        ` : `
                            <span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700; padding:4px 8px; border-radius:4px; font-size:0.75rem;">
                                ✓ Fees Fully Settled
                            </span>
                        `}
                    </div>
                </div>
                <div class="metric-icon" style="background:${isDue ? '#ffe4e6' : '#dcfce7'}; color:${isDue ? '#be123c' : '#15803d'};">
                    ${isDue ? '💳' : '✅'}
                </div>
            </div>
        </div>

        <!-- Quick Access Actions -->
        <div class="card" style="margin-top:16px;">
            <div class="card-header" style="display:flex; justify-content:space-between; align-items:center;">
                <span class="card-title"><i class="fas fa-user-shield"></i> Guardian Services for ${student.student_name}</span>
                <span style="font-size:0.78rem; background:#eff6ff; color:#1d4ed8; font-weight:700; padding:4px 10px; border-radius:12px; border:1px solid #bfdbfe;">
                    Ward Full Access (Marks Read-Only Sealed)
                </span>
            </div>
            <div class="card-body">
                <div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:18px;">
                    <button class="btn btn-primary" onclick="renderMarksheetTab(${student.student_id})">
                        📜 View Ward Marksheet (Read-Only)
                    </button>
                    <button class="btn btn-outline" onclick="openParentEditNameModal(${student.student_id}, '${escapeJs(student.student_name)}')">
                        ✏️ Edit Child's Official Name (Verify Aadhaar)
                    </button>
                    ${isDue ? `
                        <button class="btn btn-outline" style="color:#15803d; border-color:#86efac; font-weight:700;"
                                onclick="openOnlinePaymentModal(${student.student_id}, '${escapeJs(student.student_name)}', '${student.class_name}', '${student.adm_no}', ${dueAmount})">
                            💳 Pay Outstanding Fee Due (₹${dueAmount.toLocaleString()})
                        </button>
                    ` : ''}
                    <button class="btn btn-outline" onclick="showTab('attendance')">
                        📅 Check Daily Attendance (${attendance.percentage}%)
                    </button>
                    <button class="btn btn-outline" onclick="showTab('notices')">
                        📢 School Circulars & Notices
                    </button>
                </div>

                <!-- Child Class Timetable Section (Separately for This Child) -->
                <div class="card" style="border:1px solid #e2e8f0; margin-bottom:20px; box-shadow:none;">
                    <div class="card-header" style="background:#f8fafc; display:flex; justify-content:space-between; align-items:center;">
                        <span class="card-title" style="font-size:0.95rem;">
                            📅 Weekly Class Timetable: <strong>${student.student_name}</strong> (${student.class_name} • ${student.section_name || 'Section A'})
                        </span>
                        <button class="btn btn-outline btn-sm" onclick="showTab('timetable')">
                            Expand Timetable View
                        </button>
                    </div>
                    <div class="card-body" style="padding:0; overflow-x:auto;">
                        <table class="data-table" style="font-size:0.8rem;">
                            <thead>
                                <tr>
                                    <th>Day</th>
                                    ${(timetable.periods || []).map(p => `<th>${p}</th>`).join('')}
                                </tr>
                            </thead>
                            <tbody>
                                ${(timetable.days || []).map(d => `
                                    <tr>
                                        <td style="font-weight:800; color:#1e3a8a;">${d.day}</td>
                                        ${(d.subjects || []).map(s => `
                                            <td style="background:#f8fafc; font-size:0.77rem; font-weight:600; text-align:center;">
                                                <div style="color:#0f172a;">${s}</div>
                                            </td>
                                        `).join('')}
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>

                <!-- Ward Fee Ledger & Payment Receipts for This Child -->
                <h4 style="font-size:0.95rem; font-weight:700; color:#0f172a; margin-bottom:10px; display:flex; justify-content:space-between; align-items:center;">
                    <span>📜 ${student.student_name}'s Fee Ledger & Official Receipts</span>
                    ${isDue ? `
                        <button class="btn btn-sm btn-primary" style="background:#16a34a; border-color:#16a34a;"
                                onclick="openOnlinePaymentModal(${student.student_id}, '${escapeJs(student.student_name)}', '${student.class_name}', '${student.adm_no}', ${dueAmount})">
                            ➕ Pay Online (UPI / Net Banking)
                        </button>
                    ` : ''}
                </h4>

                <div style="overflow-x:auto;">
                    <table class="data-table" style="font-size:0.83rem;">
                        <thead>
                            <tr>
                                <th>Receipt / Invoice Ref</th>
                                <th>Payment Description</th>
                                <th>Payment Method</th>
                                <th>Total Bill (₹)</th>
                                <th>Paid (₹)</th>
                                <th>Status</th>
                                <th>Date</th>
                                <th>Official Receipt</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${payments.length === 0 ? `
                                <tr>
                                    <td colspan="8" style="text-align:center; padding:25px; color:#64748b;">
                                        No payment records on file for ${student.student_name}. Outstanding fee due: <strong>₹${dueAmount.toLocaleString()}</strong>.
                                    </td>
                                </tr>
                            ` : payments.map(p => `
                                <tr>
                                    <td><span style="font-family:monospace; font-weight:700; color:#1e3a8a;">${p.ref_no}</span></td>
                                    <td>${p.title}</td>
                                    <td>
                                        <span class="badge" style="background:#f1f5f9; color:#334155; font-weight:600; padding:2px 8px; border-radius:4px;">
                                            ${p.method_disp || 'Offline / Cash'}
                                        </span>
                                    </td>
                                    <td>₹${(p.amount || 0).toLocaleString()}</td>
                                    <td style="font-weight:700; color:#15803d;">₹${(p.paid || 0).toLocaleString()}</td>
                                    <td><span class="status-pill status-${(p.status || 'Paid').toLowerCase()}">${p.status}</span></td>
                                    <td>${p.date}</td>
                                    <td>
                                        <button class="btn btn-outline btn-sm" onclick="printReceipt('${p.ref_no}', '${escapeJs(student.student_name)}', '${escapeJs(p.title)}', ${p.amount}, ${p.paid}, '${p.date}')">
                                            🖨️ Print Receipt
                                        </button>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;
    document.getElementById('portal-tab-content').innerHTML = html;
}

// 5. ACCOUNTANT DASHBOARD
async function renderAccountantDashboard() {
    const stats = await fetch('/api/stats').then(r => r.json());
    document.getElementById('portal-header-title').innerText = 'Fee & Accounts Dashboard';
    document.getElementById('portal-header-desc').innerText = `Accountant: ${currentUser.name} | Session: 2026-2027`;

    const html = `
        <div class="metrics-row">
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Total Collected Fees</h5>
                    <h2>₹${(stats.revenue || 0).toLocaleString()}</h2>
                    <span style="font-size:0.75rem; color:#10b981;">Term 1 Total</span>
                </div>
                <div class="metric-icon metric-green">💰</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Enrolled Students</h5>
                    <h2>${stats.students}</h2>
                    <span style="font-size:0.75rem; color:#64748b;">Billing Database</span>
                </div>
                <div class="metric-icon metric-blue">🎓</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Faculty Leave Ledger</h5>
                    <h2>Active</h2>
                    <span style="font-size:0.75rem; color:#f59e0b;">Quota Balances Live</span>
                </div>
                <div class="metric-icon metric-amber">🏖️</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Staff Payroll</h5>
                    <h2>Automated</h2>
                    <span style="font-size:0.75rem; color:#7c3aed;">System Computed Slips</span>
                </div>
                <div class="metric-icon metric-purple">💵</div>
            </div>
        </div>

        <div class="card" style="margin-bottom:20px;">
            <div class="card-header">
                <span class="card-title">Accounts & Financial Operations</span>
            </div>
            <div class="card-body" style="display:flex; gap:12px; flex-wrap:wrap;">
                <button class="btn btn-primary" onclick="openModal('modal-record-payment')">➕ Record Fee Payment</button>
                <button class="btn btn-outline" onclick="showTab('payments')">📜 View Payment Receipts</button>
                <button class="btn btn-outline" onclick="showTab('students')">🎓 Student Billing List</button>
                <button class="btn btn-outline" style="border-color:#f59e0b; color:#b45309; font-weight:700;" onclick="showTab('leaves')">
                    🏖️ View Faculty Leave Balances (Used & Remaining)
                </button>
                <button class="btn btn-outline" style="border-color:#7c3aed; color:#6d28d9; font-weight:700;" onclick="showTab('payroll')">
                    💵 Faculty Payroll & Salary Slips
                </button>
            </div>
        </div>
    `;
    document.getElementById('portal-tab-content').innerHTML = html;
}

// 6. LIBRARIAN DASHBOARD
async function renderLibrarianDashboard() {
    const data = await fetch('/api/library').then(r => r.json());
    document.getElementById('portal-header-title').innerText = 'E-Library Resource Center';
    document.getElementById('portal-header-desc').innerText = `Head Librarian: ${currentUser.name} | Total Titles: ${data.books.length}`;

    const html = `
        <div class="metrics-row">
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Catalogued Titles</h5>
                    <h2>${data.books.length}</h2>
                    <span style="font-size:0.75rem; color:#10b981;">In Stock</span>
                </div>
                <div class="metric-icon metric-blue">📚</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Active Borrow Requests</h5>
                    <h2>${data.requests.length}</h2>
                    <span style="font-size:0.75rem; color:#64748b;">Loan Tracking</span>
                </div>
                <div class="metric-icon metric-purple">📖</div>
            </div>
        </div>

        <div class="card">
            <div class="card-header">
                <span class="card-title">Library Actions</span>
            </div>
            <div class="card-body" style="display:flex; gap:12px; flex-wrap:wrap;">
                <button class="btn btn-primary" onclick="openModal('modal-add-book')">➕ Add New Book</button>
                <button class="btn btn-outline" onclick="showTab('library')">📚 Browse Catalogue</button>
            </div>
        </div>
    `;
    document.getElementById('portal-tab-content').innerHTML = html;
}

// 7. ADMINISTRATOR DASHBOARD
async function renderAdminDashboard() {
    renderSuperAdminDashboard();
}

// =====================================================================
// SUPER ADMIN: USER ACCOUNTS & CREDENTIALS MANAGEMENT
// =====================================================================
async function renderUsersTab() {
    if (!['super_admin', 'it_admin'].includes(currentRole)) {
        showTab('dashboard');
        return;
    }

    document.getElementById('portal-header-title').innerText = 'User Accounts & Roles Governance Hub';
    document.getElementById('portal-header-desc').innerText = 'IT Support Administrator & Director Governance: Create User IDs, Assign & Change Roles, Enforce Name/Gender Rules';

    try {
        const users = await fetch('/api/users').then(r => r.json());
        siteData.users = users;

        const html = `
            <!-- Top Action Header & Policy Callout -->
            <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:16px 20px; margin-bottom:20px; color:#1e40af; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:2rem;">👑</span>
                    <div>
                        <strong style="font-size:0.98rem;">Director Exclusive Governance & Name/Gender Policy:</strong>
                        <div style="font-size:0.83rem; color:#1d4ed8; margin-top:2px;">
                            • Every ID is created by the Director, who can assign any ID to any role.<br>
                            • <strong>Name & Gender Rule:</strong> Any ID with no assigned person name will have <strong>no gender</strong> (—). If a role is assigned to a person, their gender is displayed.<br>
                            • <strong>Top-Level Roles:</strong> Director (Owner) & IT Support Administrator (Computer Lab Master).
                        </div>
                    </div>
                </div>
                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <button class="btn btn-success" style="font-weight:700; padding:8px 16px; background:#15803d; border-color:#166534; color:white; display:inline-flex; align-items:center; gap:6px;" onclick="window.location.href='/api/it/export_credentials_excel'">
                        <span>📥</span> Export All User IDs & Passwords (Excel)
                    </button>
                    <button class="btn btn-primary" style="font-weight:700; padding:8px 16px; background:#1e3a8a;" onclick="openModal('modal-create-user')">
                        👑➕ Create User ID & Role
                    </button>
                    <button class="btn btn-danger" style="background:#dc2626; border-color:#b91c1c; font-weight:700; padding:8px 16px;" onclick="confirmCleanTestData()">
                        🧹 Clean All Test Data
                    </button>
                    <button class="btn btn-outline" style="font-weight:700; padding:8px 14px;" onclick="seedFacultyDemo()" title="Re-seed demo teacher & accountant for testing">
                        🔄 Seed Demo Faculty
                    </button>
                </div>
            </div>

            <div class="card">
                <div class="card-header" style="justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span class="card-title">All System Accounts (${users.length})</span>
                        <span style="font-size:0.75rem; background:#1e3a8a; color:white; padding:2px 8px; border-radius:4px; font-weight:700;">
                            Director & IT Oversight
                        </span>
                    </div>
                    <div>
                        <input type="text" id="user-search-input" placeholder="Search user ID, name, role..." class="form-control" style="padding:6px 12px; width:260px;" onkeyup="filterUsersTable()">
                    </div>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    <table class="data-table" id="users-table">
                        <thead>
                            <tr>
                                <th>User / Name</th>
                                <th>Gender</th>
                                <th>Assigned Role</th>
                                <th>Common ID / Fleet</th>
                                <th>Unique User ID</th>
                                <th>Password</th>
                                <th>Email Service</th>
                                <th>Phone</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${users.map(u => {
                                const hasName = u.name && u.name.trim().length > 0;
                                const genderBadge = hasName && u.gender ? `
                                    <span class="badge" style="background:#eff6ff; color:#1e40af; font-weight:700;">
                                        ${u.gender === 'Female' ? '👩 Female' : '👨 Male'}
                                    </span>
                                ` : `<span style="color:#94a3b8; font-style:italic;">— (No Gender)</span>`;

                                return `
                                    <tr>
                                        <td style="display:flex; align-items:center; gap:10px;">
                                            <img src="${u.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150'}" style="width:34px; height:34px; border-radius:50%; object-fit:cover;">
                                            <div>
                                                <div style="font-weight:700; color:#0f172a;">${u.name || '<span style="color:#94a3b8; font-style:italic;">(Unassigned ID)</span>'}</div>
                                                <div style="font-size:0.72rem; color:#64748b;">ID #${u.id}</div>
                                            </div>
                                        </td>
                                        <td>${genderBadge}</td>
                                        <td>
                                            <span class="cred-role-badge role-${u.user_type}">
                                                ${formatRoleName(u.user_type)}
                                            </span>
                                        </td>
                                        <td>
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
                                        </td>
                                        <td>
                                            <span class="pwd-badge" style="color:#1e40af; font-weight:700; font-family:monospace;">${u.username}</span>
                                        </td>
                                        <td>
                                            <div style="display:flex; align-items:center; gap:6px;">
                                                <span class="pwd-badge" id="pwd-display-${u.id}">••••••••</span>
                                                <button type="button" class="btn-icon" onclick="toggleTablePassword(${u.id}, '${u.password}')" title="Show / Hide Password">
                                                    👁️
                                                </button>
                                            </div>
                                        </td>
                                        <td>
                                            ${u.has_mail_services === 0 || u.is_common_id || u.username === 'GS_teacher' ? `
                                                <span style="color:#dc2626; font-size:0.74rem; font-weight:700; display:block;">📭 No Mail Service</span>
                                                <small style="color:#64748b; font-size:0.68rem;">(Common Lab ID)</small>
                                            ` : `
                                                <span style="font-size:0.82rem; color:#475569;">${u.email || '—'}</span>
                                            `}
                                        </td>
                                        <td><span style="font-size:0.82rem; color:#475569;">${u.phone || '—'}</span></td>
                                        <td>
                                            <div style="display:flex; gap:6px;">
                                                <button class="btn btn-secondary btn-sm" style="font-size:0.73rem; padding:3px 8px; background:#475569; color:white;" onclick="openAssignUserRoleModal(${u.id})">
                                                    🎭 Assign Role
                                                </button>
                                                <button class="btn btn-outline btn-sm" style="font-size:0.73rem; padding:3px 8px; color:#2563eb; border-color:#93c5fd;" onclick="showTab('credentials')">
                                                    🔐 IT & Owner Credential Desk
                                                </button>
                                                ${(!['Owner(Directer)', 'GS_itsupport'].includes(u.username)) ? `
                                                    <button class="btn btn-danger btn-sm" style="font-size:0.73rem; padding:3px 8px; background:#dc2626; border-color:#b91c1c; color:white;" onclick="confirmDeleteUser(${u.id}, '${u.username}')" title="Delete User ID permanently">
                                                        🗑️ Delete ID
                                                    </button>
                                                ` : ''}
                                            </div>
                                        </td>
                                    </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        document.getElementById('portal-tab-content').innerHTML = html;
    } catch (err) {
        document.getElementById('portal-tab-content').innerHTML = `<div style="padding:20px; color:red;">Error loading users: ${err.message}</div>`;
    }
}

function filterUsersTable() {
    const q = document.getElementById('user-search-input').value.toLowerCase();
    const rows = document.querySelectorAll('#users-table tbody tr');
    rows.forEach(r => {
        r.style.display = r.innerText.toLowerCase().includes(q) ? '' : 'none';
    });
}

function toggleTablePassword(userId, actualPassword) {
    const el = document.getElementById(`pwd-display-${userId}`);
    if (el) {
        if (el.innerText === '••••••••') {
            el.innerText = actualPassword;
            el.style.color = '#dc2626';
            el.style.fontWeight = 'bold';
        } else {
            el.innerText = '••••••••';
            el.style.color = '';
            el.style.fontWeight = '';
        }
    }
}

function openEditCredentialsModal(userId) {
    const user = siteData.users.find(u => u.id === userId);
    if (!user) return;

    document.getElementById('edit-user-id').value = user.id;
    document.getElementById('edit-user-display-name').innerText = user.name;
    document.getElementById('edit-user-display-role').innerText = formatRoleName(user.user_type);
    document.getElementById('edit-user-username').value = user.username;
    document.getElementById('edit-user-password').value = user.password;
    document.getElementById('edit-user-name').value = user.name;
    document.getElementById('edit-user-email').value = user.email;
    document.getElementById('edit-user-phone').value = user.phone || '';
    document.getElementById('edit-user-role').value = user.user_type;

    openModal('modal-edit-credentials');
}

async function submitUpdateCredentials(e) {
    e.preventDefault();
    const userId = parseInt(document.getElementById('edit-user-id').value);
    const newUsername = document.getElementById('edit-user-username').value.trim();
    const newPassword = document.getElementById('edit-user-password').value.trim();
    const newName = document.getElementById('edit-user-name').value.trim();
    const newEmail = document.getElementById('edit-user-email').value.trim();
    const newRole = document.getElementById('edit-user-role').value;
    const newPhone = document.getElementById('edit-user-phone').value.trim();

    try {
        const res = await fetch('/api/users/update_credentials', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                username: newUsername,
                password: newPassword,
                name: newName,
                email: newEmail,
                user_type: newRole,
                phone: newPhone
            })
        });
        const data = await res.json();

        if (data.success) {
            alert(`✅ ${data.message}\n\n• User ID: ${newUsername}\n• Password: ${newPassword}\n\nThe user can now log in with these new credentials immediately!`);
            closeModal('modal-edit-credentials');

            // If updated user is current user, update session
            if (currentUser && currentUser.id === userId) {
                currentUser = data.user;
                localStorage.setItem('gs_auth_user', JSON.stringify(data.user));
                updatePortalHeaderAndSession();
            }

            renderUsersTab();
            if (typeof loadLoginDirectory === 'function') loadLoginDirectory();
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    } catch (err) {
        alert('Could not update user credentials. Please try again.');
    }
}

function handleCreateUserNameChange(val) {
    const sel = document.getElementById('create-user-gender');
    const hint = document.getElementById('create-user-gender-hint');
    if (!val || !val.trim()) {
        if (sel) {
            sel.disabled = true;
            sel.value = '';
        }
        if (hint) hint.innerHTML = '🔒 Disabled: Role ID has no assigned person name (no gender shown).';
    } else {
        if (sel) sel.disabled = false;
        if (hint) hint.innerHTML = '✅ Enabled: Assigned person gender can now be specified.';
    }
}

async function submitCreateUser(e) {
    e.preventDefault();
    const personName = document.getElementById('create-user-name').value.trim();
    const genderSel = document.getElementById('create-user-gender');
    const genderVal = personName && genderSel ? genderSel.value : null;

    const roleVal = document.getElementById('create-user-role').value;
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
    };

    try {
        const res = await fetch('/api/users/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-create-user');
            e.target.reset();
            renderUsersTab();
            if (typeof loadLoginDirectory === 'function') loadLoginDirectory();
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    } catch (err) {
        alert('Failed to create account.');
    }
}

function generateStrongPassword(targetInputId) {
    const prefixes = ['Pass', 'Secure', 'Bright', 'Excel', 'Leader', 'Academy', 'GS', 'Smart'];
    const p = prefixes[Math.floor(Math.random() * prefixes.length)];
    const num = Math.floor(100 + Math.random() * 900);
    const symbols = ['@', '#', '$', '!'];
    const s = symbols[Math.floor(Math.random() * symbols.length)];
    const strongPwd = `${p}${s}${num}`;

    const input = document.getElementById(targetInputId);
    if (input) {
        input.value = strongPwd;
    }
}

// =====================================================================
// STUDENTS DIRECTORY & OFFICIAL MARKSHEET
// =====================================================================
let cachedStudentsList = [];
let studentFilterClass = 'ALL';
let studentFilterSection = 'ALL';
let studentFilterGender = 'ALL';
let studentSearchQuery = '';
let studentViewMode = 'grouped'; // 'grouped' or 'table'

async function renderStudentsTab() {
    const students = await fetch('/api/students').then(r => r.json());
    cachedStudentsList = students;
    document.getElementById('portal-header-title').innerText = 'Student Directory';
    document.getElementById('portal-header-desc').innerText = 'Manage enrolled students, class allocations, search, and admission records';

    // Unique class names with counts
    const classCountMap = {};
    students.forEach(s => {
        const cName = s.class_name || 'Unassigned';
        classCountMap[cName] = (classCountMap[cName] || 0) + 1;
    });

    const standardClasses = [
        "Class 1", "Class 2", "Class 3", "Class 4", "Class 5", 
        "Class 6", "Class 7", "Class 8", "Class 9", "Class 10", 
        "Class 11", "Class 12", "Class 12 - Science", "Class 12 - Commerce", "Class 12 - Humanities (Arts)"
    ];

    const html = `
        <div class="card" style="margin-bottom:16px;">
            <div class="card-header" style="justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <span class="card-title">Enrolled Students (<span id="students-total-count">${students.length}</span>)</span>
                    <p style="font-size:0.78rem; color:#64748b; margin:2px 0 0;">Greenland School Complete Student Master Register</p>
                </div>
                <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
                    ${currentRole === 'super_admin' || currentRole === 'admin' ? `
                        <button class="btn btn-secondary btn-sm" onclick="openModal('modal-upload-excel-student')">📊 Upload Student Excel</button>
                        <button class="btn btn-primary btn-sm" onclick="openModal('modal-admit-student')">➕ Admit Student</button>
                        <button class="btn btn-sm" style="background:#dc2626; color:white; border:none; padding:7px 14px; font-weight:700; cursor:pointer;" onclick="confirmDeleteAllStudents()" title="Permanently delete all student records">🗑️ Delete All Students</button>
                    ` : ''}
                </div>
            </div>

            <!-- Class Separation Pill Bar -->
            <div style="padding:14px 20px 10px; border-bottom:1px solid #f1f5f9; background:#f8fafc;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <span style="font-size:0.75rem; font-weight:700; color:#64748b; text-transform:uppercase; letter-spacing:0.5px;">
                        🏫 Quick Class Separation Navigation
                    </span>
                    <span style="font-size:0.75rem; color:#1e40af; font-weight:600;">Click any class pill to isolate</span>
                </div>
                <div style="display:flex; gap:8px; overflow-x:auto; padding-bottom:6px; flex-wrap:nowrap;" id="class-pill-bar">
                    <button class="class-pill ${studentFilterClass === 'ALL' ? 'active' : ''}" onclick="selectClassPill('ALL')" style="padding:6px 14px; border-radius:20px; font-size:0.8rem; font-weight:700; cursor:pointer; border:1px solid ${studentFilterClass === 'ALL' ? '#1e40af' : '#cbd5e1'}; background:${studentFilterClass === 'ALL' ? '#1e40af' : '#ffffff'}; color:${studentFilterClass === 'ALL' ? '#ffffff' : '#334155'}; white-space:nowrap; transition:all 0.2s;">
                        All Classes (${students.length})
                    </button>
                    ${standardClasses.map(c => `
                        <button class="class-pill ${studentFilterClass === c ? 'active' : ''}" onclick="selectClassPill('${c}')" style="padding:6px 14px; border-radius:20px; font-size:0.8rem; font-weight:700; cursor:pointer; border:1px solid ${studentFilterClass === c ? '#1e40af' : '#cbd5e1'}; background:${studentFilterClass === c ? '#1e40af' : '#ffffff'}; color:${studentFilterClass === c ? '#ffffff' : '#334155'}; white-space:nowrap; transition:all 0.2s;">
                            ${c} <span style="background:${studentFilterClass === c ? '#3b82f6' : '#f1f5f9'}; color:${studentFilterClass === c ? '#ffffff' : '#475569'}; padding:2px 7px; border-radius:10px; font-size:0.72rem; margin-left:4px;">${classCountMap[c] || 0}</span>
                        </button>
                    `).join('')}
                </div>
            </div>

            <!-- Search & Filter Options Toolbar -->
            <div style="padding:14px 20px; background:#ffffff; border-bottom:1px solid #e2e8f0; display:flex; flex-wrap:wrap; gap:12px; align-items:center; justify-content:space-between;">
                <div style="display:flex; flex-wrap:wrap; gap:10px; align-items:center; flex:1;">
                    <div style="position:relative; min-width:240px; flex:1;">
                        <input type="text" id="student-search-input" placeholder="🔍 Search name, adm no, email, guardian..." class="form-control" style="padding:7px 12px; width:100%; font-size:0.85rem;" value="${studentSearchQuery}" oninput="handleStudentSearch(this.value)">
                    </div>
                    <select id="student-filter-class-select" class="form-control" style="width:170px; padding:7px 10px; font-size:0.85rem;" onchange="handleClassFilterChange(this.value)">
                        <option value="ALL">All Classes</option>
                        ${standardClasses.map(c => `<option value="${c}" ${studentFilterClass === c ? 'selected' : ''}>${c}</option>`).join('')}
                    </select>
                    <select id="student-filter-section-select" class="form-control" style="width:140px; padding:7px 10px; font-size:0.85rem;" onchange="handleSectionFilterChange(this.value)">
                        <option value="ALL">All Sections</option>
                        <option value="Section A" ${studentFilterSection === 'Section A' ? 'selected' : ''}>Section A</option>
                        <option value="Section B" ${studentFilterSection === 'Section B' ? 'selected' : ''}>Section B</option>
                        <option value="Section C" ${studentFilterSection === 'Section C' ? 'selected' : ''}>Section C</option>
                        <option value="Section D" ${studentFilterSection === 'Section D' ? 'selected' : ''}>Section D</option>
                    </select>
                    <select id="student-filter-gender-select" class="form-control" style="width:130px; padding:7px 10px; font-size:0.85rem;" onchange="handleGenderFilterChange(this.value)">
                        <option value="ALL">All Genders</option>
                        <option value="Male" ${studentFilterGender === 'Male' ? 'selected' : ''}>Male</option>
                        <option value="Female" ${studentFilterGender === 'Female' ? 'selected' : ''}>Female</option>
                    </select>
                    <button class="btn btn-outline btn-sm" onclick="clearStudentFilters()" style="padding:6px 12px; font-size:0.8rem;">✕ Clear</button>
                </div>

                <div style="display:flex; gap:12px; align-items:center;">
                    <button class="btn btn-outline btn-sm" onclick="toggleStudentViewMode()" style="padding:6px 14px; font-size:0.8rem; font-weight:700;">
                        ${studentViewMode === 'grouped' ? '📋 Switch to Flat Table' : '📑 Switch to Class Groups'}
                    </button>
                    <span style="font-size:0.8rem; color:#64748b; white-space:nowrap;" id="student-filter-summary">
                        Showing <strong id="student-showing-count">${students.length}</strong> of ${students.length}
                    </span>
                </div>
            </div>

            <!-- Student Data Container -->
            <div id="student-records-container" style="padding:0;"></div>
        </div>
    `;

    document.getElementById('portal-tab-content').innerHTML = html;
    renderStudentRows();
}

function getFilteredStudents() {
    return cachedStudentsList.filter(s => {
        if (studentSearchQuery) {
            const q = studentSearchQuery.toLowerCase();
            const match = (
                (s.name && s.name.toLowerCase().includes(q)) ||
                (s.adm_no && s.adm_no.toLowerCase().includes(q)) ||
                (s.email && s.email.toLowerCase().includes(q)) ||
                (s.username && s.username.toLowerCase().includes(q)) ||
                (s.parent_name && s.parent_name.toLowerCase().includes(q)) ||
                (s.phone && s.phone.toLowerCase().includes(q))
            );
            if (!match) return false;
        }
        if (studentFilterClass !== 'ALL' && s.class_name !== studentFilterClass) {
            return false;
        }
        if (studentFilterSection !== 'ALL' && s.section_name !== studentFilterSection) {
            return false;
        }
        if (studentFilterGender !== 'ALL' && s.gender !== studentFilterGender) {
            return false;
        }
        return true;
    });
}

function renderStudentRows() {
    const container = document.getElementById('student-records-container');
    if (!container) return;

    const filtered = getFilteredStudents();
    const countEl = document.getElementById('student-showing-count');
    if (countEl) countEl.innerText = filtered.length;

    if (filtered.length === 0) {
        container.innerHTML = `
            <div style="text-align:center; padding:50px 20px; color:#64748b;">
                <div style="font-size:2.4rem; margin-bottom:10px;">📋</div>
                <div style="font-size:1.1rem; font-weight:700; color:#0f172a;">No Matching Student Records</div>
                <div style="font-size:0.85rem; margin-top:4px; max-width:440px; margin-left:auto; margin-right:auto;">
                    No student records match the active search query or class filter. Try clearing filters or admit new students.
                </div>
                <div style="margin-top:16px;">
                    <button class="btn btn-outline btn-sm" onclick="clearStudentFilters()">Reset Filters</button>
                    ${currentRole === 'super_admin' || currentRole === 'admin' ? `
                        <button class="btn btn-primary btn-sm" onclick="openModal('modal-admit-student')" style="margin-left:8px;">➕ Admit Student</button>
                    ` : ''}
                </div>
            </div>
        `;
        return;
    }

    if (studentViewMode === 'grouped') {
        // Group students by Class Name
        const groups = {};
        filtered.forEach(s => {
            const cName = s.class_name || 'Unassigned';
            if (!groups[cName]) groups[cName] = [];
            groups[cName].push(s);
        });

        const sortedGroupNames = Object.keys(groups).sort();

        let html = '';
        sortedGroupNames.forEach(className => {
            const list = groups[className];
            html += `
                <div style="border-bottom:2px solid #e2e8f0;">
                    <div style="background:#f1f5f9; padding:12px 20px; display:flex; justify-content:space-between; align-items:center;">
                        <div style="display:flex; align-items:center; gap:10px;">
                            <span style="font-size:1.2rem;">🏫</span>
                            <strong style="font-size:1rem; color:#1e3a8a;">${className}</strong>
                            <span class="badge" style="background:#dbeafe; color:#1d4ed8; font-weight:700; padding:2px 8px; border-radius:12px; font-size:0.75rem;">
                                ${list.length} Student${list.length > 1 ? 's' : ''}
                            </span>
                        </div>
                    </div>
                    <div style="overflow-x:auto;">
                        <table class="data-table" style="margin-bottom:0;">
                            <thead>
                                <tr>
                                    <th>Student</th>
                                    <th>Adm No.</th>
                                    <th>Section (Arm)</th>
                                    <th>User ID</th>
                                    <th>Gender</th>
                                    <th>Admission Status</th>
                                    <th>Guardian</th>
                                    <th>Blood Group</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${list.map(s => renderSingleStudentRow(s)).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        });
        container.innerHTML = html;
    } else {
        // Unified Flat Table View
        container.innerHTML = `
            <div style="overflow-x:auto;">
                <table class="data-table" id="students-table">
                    <thead>
                        <tr>
                            <th>Student</th>
                            <th>Adm No.</th>
                            <th>Class & Section</th>
                            <th>User ID</th>
                            <th>Gender</th>
                            <th>Admission Status</th>
                            <th>Guardian</th>
                            <th>Blood Group</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${filtered.map(s => renderSingleStudentRow(s)).join('')}
                    </tbody>
                </table>
            </div>
        `;
    }
}

function renderSingleStudentRow(s) {
    return `
        <tr>
            <td style="display:flex; align-items:center; gap:10px;">
                <img src="${s.photo}" style="width:34px; height:34px; border-radius:50%; object-fit:cover; border:1px solid #cbd5e1;">
                <div>
                    <div style="font-weight:700; color:#0f172a;">${s.name}</div>
                    <div style="font-size:0.73rem; color:#64748b;">${s.email}</div>
                </div>
            </td>
            <td><span style="font-family:monospace; font-weight:700; color:#1e40af;">${s.adm_no}</span></td>
            <td>
                <span style="font-weight:600;">${s.class_name}</span>
                <span style="font-size:0.78rem; color:#64748b;">(${s.section_name || 'Section A'})</span>
            </td>
            <td><code>${s.username || '—'}</code></td>
            <td><span style="font-size:0.82rem; color:#475569;">${s.gender || '—'}</span></td>
            <td>
                <span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700; padding:3px 8px; border-radius:6px; font-size:0.74rem; display:inline-flex; align-items:center; gap:4px;">
                    <i class="fas fa-check-circle"></i> ${s.admission_status || 'Approved for New Admission'}
                </span>
                <div style="font-size:0.7rem; color:#64748b; margin-top:2px;">by ${s.approved_by || 'Administration'}</div>
            </td>
            <td>
                <div style="font-size:0.83rem; font-weight:600;">${s.parent_name || 'Guardian'}</div>
                <div style="font-size:0.72rem; color:#64748b;">${s.phone || '—'}</div>
            </td>
            <td><span style="font-weight:700; color:#dc2626;">${s.blood_group}</span></td>
            <td>
                <div style="display:flex; gap:6px;">
                    <button class="btn btn-outline btn-sm" onclick="renderMarksheetTab(${s.id})" title="Official Marksheet">📄 Marksheet</button>
                    ${currentRole === 'super_admin' || currentRole === 'admin' ? `
                        <button class="btn btn-outline btn-sm" style="color:#dc2626; border-color:#fca5a5; padding:4px 8px; font-size:0.76rem;" onclick="confirmDeleteOneStudent(${s.id}, '${s.name.replace(/'/g, "\\'")}')" title="Delete Student Record">
                            🗑️ Delete
                        </button>
                    ` : ''}
                </div>
            </td>
        </tr>
    `;
}

function selectClassPill(className) {
    studentFilterClass = className;
    const select = document.getElementById('student-filter-class-select');
    if (select) select.value = className;
    renderStudentsTab();
}

function handleClassFilterChange(val) {
    studentFilterClass = val;
    renderStudentsTab();
}

function handleSectionFilterChange(val) {
    studentFilterSection = val;
    renderStudentRows();
}

function handleGenderFilterChange(val) {
    studentFilterGender = val;
    renderStudentRows();
}

function handleStudentSearch(val) {
    studentSearchQuery = val;
    renderStudentRows();
}

function toggleStudentViewMode() {
    studentViewMode = studentViewMode === 'grouped' ? 'table' : 'grouped';
    renderStudentsTab();
}

function clearStudentFilters() {
    studentFilterClass = 'ALL';
    studentFilterSection = 'ALL';
    studentFilterGender = 'ALL';
    studentSearchQuery = '';
    const searchInput = document.getElementById('student-search-input');
    if (searchInput) searchInput.value = '';
    renderStudentsTab();
}

async function confirmDeleteOneStudent(studentId, studentName) {
    if (!confirm(`Are you sure you want to permanently delete student "${studentName}"?\n\nThis will remove their enrollment profile, exam marks, attendance records, and user login.`)) {
        return;
    }
    try {
        const res = await fetch('/api/students/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ student_id: studentId })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✓ ${data.message}`);
            renderStudentsTab();
            loadInitialData();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (e) {
        alert('Failed to delete student record.');
    }
}

async function confirmDeleteAllStudents() {
    const promptText = prompt("⚠️ CRITICAL WARNING: You are about to permanently delete ALL student records, admission data, exam marks, and login accounts from Greenland School.\n\nType 'DELETE ALL' to confirm:");
    if (promptText !== 'DELETE ALL') {
        if (promptText !== null) alert("Action cancelled. You must type 'DELETE ALL' exactly to confirm.");
        return;
    }
    try {
        const res = await fetch('/api/students/delete_all', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ confirm: 'DELETE_ALL' })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✓ ${data.message}`);
            renderStudentsTab();
            loadInitialData();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (e) {
        alert('Failed to delete all student records.');
    }
}

// 3. OFFICIAL PRINTABLE REPORT SHEET / MARKSHEET VIEW
async function renderMarksheetTab(studentId = 1) {
    currentStudentId = studentId;
    let data = { error: 'No student records available' };
    try {
        data = await fetch(`/api/marksheet/${studentId}`).then(r => r.json());
    } catch (e) {
        data = { error: 'Unable to load marksheet data' };
    }

    if (data.error || !data.student) {
        document.getElementById('portal-header-title').innerText = 'Student Academic Marksheet';
        document.getElementById('portal-header-desc').innerText = 'Official Termly Progress & Assessment Sheet';
        document.getElementById('portal-tab-content').innerHTML = `
            <div class="card" style="text-align:center; padding:55px 20px;">
                <div style="font-size:2.8rem; margin-bottom:12px;">📜</div>
                <h3 style="color:#0f172a; margin-bottom:8px; font-weight:800;">No Marksheet Available</h3>
                <p style="color:#64748b; font-size:0.95rem; max-width:480px; margin:0 auto 20px auto; line-height:1.6;">
                    All previous student records have been cleared from the database. When a student is enrolled and continuous assessment marks are recorded, official printable report cards will be generated here.
                </p>
                ${currentRole === 'super_admin' || currentRole === 'admin' ? `
                    <button class="btn btn-primary" onclick="showTab('students')">Go to Student Directory</button>
                ` : `
                    <button class="btn btn-outline" onclick="showTab('dashboard')">Back to Dashboard</button>
                `}
            </div>
        `;
        return;
    }

    const { student, marks, total_score, average, term, position, traits, teacher_comment, principal_comment } = data;

    document.getElementById('portal-header-title').innerText = 'Student Academic Marksheet';
    document.getElementById('portal-header-desc').innerText = `Official Termly Progress & Assessment Sheet - ${student.name}`;

    const html = `
        <div style="margin-bottom:16px; display:flex; justify-content:space-between; align-items:center;" class="no-print">
            ${currentRole === 'super_admin' || currentRole === 'admin' ? `
                <button class="btn btn-outline" onclick="showTab('students')">← Back to Students Directory</button>
            ` : `
                <button class="btn btn-outline" onclick="showTab('dashboard')">← Back to Dashboard</button>
            `}
            <button class="btn btn-primary" onclick="window.print()">🖨️ Print / Save Official Report Card</button>
        </div>

        <div class="report-sheet-container">
            <div class="watermark">GREENLAND SCHOOL EXCELLENCE</div>

            <div class="report-header">
                <div class="report-crest">GS</div>
                <div class="report-school-info">
                    <h2>GREENLAND SCHOOL</h2>
                    <p>Khadpathar, Renukoot, Sonbhadra, Uttar Pradesh - 231217</p>
                    <p style="font-weight:700; color:#1e3a8a; margin-top:4px; font-size:1rem; text-transform:uppercase;">
                        STUDENT CONTINUOUS ASSESSMENT & TERMINAL REPORT SHEET
                    </p>
                </div>
                <img src="${student.photo}" style="width:75px; height:75px; border-radius:8px; border:2px solid #1e3a8a; object-fit:cover;">
            </div>

            <div class="report-student-meta">
                <div class="meta-field"><strong>Student Name:</strong> ${student.name}</div>
                <div class="meta-field"><strong>Admission No:</strong> ${student.adm_no}</div>
                <div class="meta-field"><strong>Class & Section:</strong> ${student.class_name} (${student.section_name || 'Gold'})</div>
                <div class="meta-field"><strong>Academic Session:</strong> ${term}</div>
                <div class="meta-field"><strong>Class Position:</strong> <span style="font-weight:bold; color:#1e40af;">${position}</span></div>
                <div class="meta-field"><strong>Attendance:</strong> ${data.attendance}</div>
                <div class="meta-field"><strong>Total Marks:</strong> ${total_score}</div>
                <div class="meta-field"><strong>Term Average:</strong> <span style="font-weight:bold; color:#16a34a;">${average}%</span></div>
            </div>

            <table class="marks-table">
                <thead>
                    <tr>
                        <th style="width:40px;">#</th>
                        <th>Subject Title</th>
                        <th style="width:80px;">CA (40)</th>
                        <th style="width:80px;">Exam (60)</th>
                        <th style="width:90px;">Total (100)</th>
                        <th style="width:70px;">Grade</th>
                        <th>Remark</th>
                    </tr>
                </thead>
                <tbody>
                    ${marks.map((m, idx) => `
                        <tr>
                            <td>${idx + 1}</td>
                            <td>${m.subject_name}</td>
                            <td>${m.ca_score}</td>
                            <td>${m.exam_score}</td>
                            <td style="font-weight:bold; color:#1e3a8a;">${m.total}</td>
                            <td><strong style="color:${m.grade === 'A' ? '#15803d' : '#1e40af'}">${m.grade}</strong></td>
                            <td>${m.remark}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>

            <div class="grading-keys">
                <span><strong>A</strong>: 70-100% (Excellent)</span>
                <span><strong>B</strong>: 60-69% (Very Good)</span>
                <span><strong>C</strong>: 50-59% (Good)</span>
                <span><strong>D</strong>: 45-49% (Pass)</span>
                <span><strong>E</strong>: 40-44% (Poor)</span>
                <span><strong>F</strong>: 0-39% (Fail)</span>
            </div>

            <div style="font-size:0.85rem; font-weight:700; margin-bottom:8px; color:#1e3a8a;">BEHAVIOURAL & PSYCHOMOTOR TRAITS ASSESSMENT (1-5 SCALE):</div>
            <div class="skills-ratings">
                ${Object.entries(traits).map(([trait, score]) => `
                    <div class="skill-row">
                        <span>${trait}</span>
                        <span><strong>${'★'.repeat(score)}${'☆'.repeat(5 - score)}</strong> (${score}/5)</span>
                    </div>
                `).join('')}
            </div>

            <div class="remarks-section">
                <div class="remark-box">
                    <strong style="color:#1e3a8a; display:block; margin-bottom:4px;">Class Teacher's Remarks:</strong>
                    <em>"${teacher_comment}"</em>
                </div>
                <div class="remark-box">
                    <strong style="color:#1e3a8a; display:block; margin-bottom:4px;">Principal's Remarks:</strong>
                    <em>"${principal_comment}"</em>
                </div>
            </div>

            <div class="signatures">
                <div class="sig-block">
                    <div>Teacher Chike</div>
                    <div>Class Teacher Signature</div>
                </div>
                <div style="text-align:center;">
                    <div style="display:inline-block; border:2px solid #16a34a; color:#16a34a; font-weight:900; padding:6px 16px; border-radius:6px; transform:rotate(-5deg); font-size:0.85rem;">
                        OFFICIAL VERIFIED
                    </div>
                </div>
                <div class="sig-block">
                    <div>Principal, Greenland School</div>
                    <div>Principal / Administrator</div>
                </div>
            </div>
        </div>
    `;
    document.getElementById('portal-tab-content').innerHTML = html;
}

// 4. MARKS ENTRY VIEW
async function renderMarksTab() {
    const marks = await fetch('/api/marks?exam_id=1').then(r => r.json());
    document.getElementById('portal-header-title').innerText = 'Exam Marks & Grading Manager';
    document.getElementById('portal-header-desc').innerText = 'Continuous Assessment (CA) and Exam terminal grading sheet';

    const html = `
        <div class="card">
            <div class="card-header">
                <span class="card-title">Term Exam Mark Sheets (Term 1)</span>
                <button class="btn btn-primary btn-sm" onclick="openModal('modal-enter-marks')">➕ Record / Update Marks</button>
            </div>
            <div class="card-body" style="padding:0; overflow-x:auto;">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Student</th>
                            <th>Adm No.</th>
                            <th>Subject</th>
                            <th>CA Score (40)</th>
                            <th>Exam Score (60)</th>
                            <th>Total (100)</th>
                            <th>Grade</th>
                            <th>Remark</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${marks.length === 0 ? `
                            <tr>
                                <td colspan="8" style="text-align:center; padding:45px 20px; color:#64748b;">
                                    <div style="font-size:2.4rem; margin-bottom:10px;">📝</div>
                                    <div style="font-size:1.1rem; font-weight:700; color:#0f172a;">No Exam Marks Recorded</div>
                                    <div style="font-size:0.85rem; margin-top:4px; max-width:480px; margin-left:auto; margin-right:auto;">
                                        All student mark records have been cleared from the database. Click <strong>"➕ Record / Update Marks"</strong> above to input continuous assessment and exam scores.
                                    </div>
                                </td>
                            </tr>
                        ` : marks.map(m => `
                            <tr>
                                <td style="font-weight:700;">${m.student_name}</td>
                                <td><code>${m.adm_no}</code></td>
                                <td>${m.subject_name} (${m.subject_code})</td>
                                <td>${m.ca_score}</td>
                                <td>${m.exam_score}</td>
                                <td><strong style="color:#1e40af;">${m.total}</strong></td>
                                <td><span style="font-weight:bold; color:${m.grade === 'A' ? '#15803d' : '#1e3a8a'}">${m.grade}</span></td>
                                <td>${m.remark}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
    document.getElementById('portal-tab-content').innerHTML = html;
}

// 5. ATTENDANCE VIEW
async function renderAttendanceTab() {
    const records = await fetch('/api/attendance?class_id=9').then(r => r.json());
    document.getElementById('portal-header-title').innerText = 'Daily Class Attendance Register';
    document.getElementById('portal-header-desc').innerText = 'SSS 3 (Senior Secondary) | Date: Today';

    const html = `
        <div class="card">
            <div class="card-header">
                <span class="card-title">Roll Call: Senior Secondary Class 3 (Gold)</span>
                ${currentRole === 'teacher' || currentRole === 'super_admin' ? `
                    <div style="display:flex; gap:10px;">
                        <button class="btn btn-outline btn-sm" onclick="markAllAttendance('Present')">Mark All Present</button>
                        <button class="btn btn-primary btn-sm" onclick="saveAttendance()">💾 Save Attendance</button>
                    </div>
                ` : ''}
            </div>
            <div class="card-body" style="padding:0;">
                <table class="data-table" id="attendance-table">
                    <thead>
                        <tr>
                            <th>Student</th>
                            <th>Admission No</th>
                            <th>Status Option</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${records.length === 0 ? `
                            <tr>
                                <td colspan="3" style="text-align:center; padding:45px 20px; color:#64748b;">
                                    <div style="font-size:2.4rem; margin-bottom:10px;">📅</div>
                                    <div style="font-size:1.1rem; font-weight:700; color:#0f172a;">No Attendance Records</div>
                                    <div style="font-size:0.85rem; margin-top:4px; max-width:480px; margin-left:auto; margin-right:auto;">
                                        No students are currently enrolled in this class arm. Admit students in the Student Directory to begin daily roll call.
                                    </div>
                                </td>
                            </tr>
                        ` : records.map(r => `
                            <tr data-student-id="${r.student_id}">
                                <td style="font-weight:700;">${r.name}</td>
                                <td><code>${r.adm_no}</code></td>
                                <td>
                                    ${currentRole === 'teacher' || currentRole === 'super_admin' ? `
                                        <label style="margin-right:15px; cursor:pointer;">
                                            <input type="radio" name="att_${r.student_id}" value="Present" ${r.status === 'Present' ? 'checked' : ''}> <span style="color:#16a34a; font-weight:600;">Present</span>
                                        </label>
                                        <label style="margin-right:15px; cursor:pointer;">
                                            <input type="radio" name="att_${r.student_id}" value="Late" ${r.status === 'Late' ? 'checked' : ''}> <span style="color:#ca8a04; font-weight:600;">Late</span>
                                        </label>
                                        <label style="cursor:pointer;">
                                            <input type="radio" name="att_${r.student_id}" value="Absent" ${r.status === 'Absent' ? 'checked' : ''}> <span style="color:#dc2626; font-weight:600;">Absent</span>
                                        </label>
                                    ` : `
                                        <span class="status-pill status-${r.status.toLowerCase()}">${r.status}</span>
                                    `}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
    document.getElementById('portal-tab-content').innerHTML = html;
}

function markAllAttendance(status) {
    document.querySelectorAll('#attendance-table input[type="radio"]').forEach(radio => {
        if (radio.value === status) radio.checked = true;
    });
}

async function saveAttendance() {
    const rows = document.querySelectorAll('#attendance-table tbody tr');
    const records = [];
    rows.forEach(r => {
        const studentId = r.dataset.studentId;
        const selected = r.querySelector(`input[name="att_${studentId}"]:checked`);
        if (selected) {
            records.push({ student_id: parseInt(studentId), status: selected.value });
        }
    });

    try {
        const res = await fetch('/api/attendance', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ records, class_id: 9 })
        });
        const data = await res.json();
        alert(data.message || 'Attendance saved!');
    } catch (err) {
        alert('Failed to save attendance.');
    }
}

// 6. PAYMENTS & FEE VIEW
async function renderPaymentsTab() {
    let payments = [];
    let deleteRequests = [];
    try {
        const [pRes, drRes] = await Promise.all([
            fetch('/api/payments').then(r => r.json()),
            fetch('/api/payments/delete_requests').then(r => r.json())
        ]);
        payments = Array.isArray(pRes) ? pRes : [];
        deleteRequests = Array.isArray(drRes) ? drRes : [];
    } catch (e) {
        payments = [];
        deleteRequests = [];
    }

    document.getElementById('portal-header-title').innerText = 'Fee Payments & Accounts Ledger';
    document.getElementById('portal-header-desc').innerText = 'Tuition fee transactions, online payment gateway & multi-tier deletion authorization';

    // 1. Accountant View: Payment Deletion Approval Live Tracker
    let accountantTrackerHtml = '';
    if (currentRole === 'accountant') {
        accountantTrackerHtml = `
            <div class="card" style="margin-bottom:20px; border-left:4px solid #b91c1c;">
                <div class="card-header" style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span class="card-title" style="color:#b91c1c;"><i class="fas fa-satellite-dish"></i> Payment Deletion Approval Live Tracker</span>
                        <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">
                            Dual-Authorization Workflow: Admin (Principal) must approve first ➔ Super Admin must approve ➔ Permanent DB Deletion
                        </div>
                    </div>
                    <button class="btn btn-outline btn-sm" onclick="renderPaymentsTab()" style="font-size:0.75rem;">
                        🔄 Refresh Live Status
                    </button>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    <table class="data-table" style="font-size:0.82rem; margin:0;">
                        <thead>
                            <tr style="background:#f8fafc;">
                                <th>Req #</th>
                                <th>Receipt Ref</th>
                                <th>Student</th>
                                <th>Amount (₹)</th>
                                <th>Reason for Deletion</th>
                                <th>1. Admin (Principal)</th>
                                <th>2. Super Admin</th>
                                <th>Database Record Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${deleteRequests.length === 0 ? `
                                <tr>
                                    <td colspan="8" style="text-align:center; padding:20px; color:#64748b;">
                                        No active or historical payment deletion requests. Click <strong>"⚠️ Request Deletion"</strong> on any erroneous transaction below to initiate the dual-approval deletion process.
                                    </td>
                                </tr>
                            ` : deleteRequests.map(r => `
                                <tr>
                                    <td><span style="font-family:monospace; font-weight:700;">#${r.id}</span></td>
                                    <td><span style="font-family:monospace; font-weight:700; color:#1e3a8a;">${r.receipt_no || r.payment_ref}</span></td>
                                    <td style="font-weight:600;">${r.student_name}</td>
                                    <td style="font-weight:700; color:#b91c1c;">₹${(r.paid || r.amount || 0).toLocaleString()}</td>
                                    <td style="max-width:200px; color:#475569;" title="${escapeJs(r.reason)}">${r.reason}</td>
                                    <td>
                                        ${r.admin_status === 'Approved' ? `
                                            <span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700; padding:4px 8px; border-radius:4px;">
                                                <i class="fas fa-check-circle"></i> Approved (${r.admin_name || 'Admin'})
                                            </span>
                                        ` : r.admin_status === 'Rejected' ? `
                                            <span class="badge" style="background:#fee2e2; color:#b91c1c; font-weight:700; padding:4px 8px; border-radius:4px;">
                                                <i class="fas fa-times-circle"></i> Rejected by Principal
                                            </span>
                                        ` : `
                                            <span class="badge" style="background:#fef3c7; color:#92400e; font-weight:700; padding:4px 8px; border-radius:4px;">
                                                <i class="fas fa-hourglass-half"></i> Pending Principal
                                            </span>
                                        `}
                                    </td>
                                    <td>
                                        ${r.superadmin_status === 'Approved' ? `
                                            <span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700; padding:4px 8px; border-radius:4px;">
                                                <i class="fas fa-check-double"></i> Approved (${r.superadmin_name || 'Super Admin'})
                                            </span>
                                        ` : r.superadmin_status === 'Rejected' ? `
                                            <span class="badge" style="background:#fee2e2; color:#b91c1c; font-weight:700; padding:4px 8px; border-radius:4px;">
                                                <i class="fas fa-times-circle"></i> Rejected
                                            </span>
                                        ` : r.superadmin_status === 'Pending' ? `
                                            <span class="badge" style="background:#fef3c7; color:#92400e; font-weight:700; padding:4px 8px; border-radius:4px;">
                                                <i class="fas fa-hourglass-half"></i> Pending Super Admin
                                            </span>
                                        ` : `
                                            <span class="badge" style="background:#f1f5f9; color:#64748b; font-weight:600; padding:4px 8px; border-radius:4px;">
                                                <i class="fas fa-lock"></i> Awaiting Admin First
                                            </span>
                                        `}
                                    </td>
                                    <td>
                                        ${r.final_status === 'Approved & Deleted' ? `
                                            <span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700; padding:4px 8px; border-radius:4px;">
                                                <i class="fas fa-trash-alt"></i> Permanently Deleted
                                            </span>
                                        ` : (r.final_status && r.final_status.includes('Direct')) ? `
                                            <span class="badge" style="background:#e0e7ff; color:#3730a3; font-weight:700; padding:4px 8px; border-radius:4px;">
                                                <i class="fas fa-bolt"></i> Direct Super Admin Delete
                                            </span>
                                        ` : r.final_status === 'Rejected' ? `
                                            <span class="badge" style="background:#fee2e2; color:#b91c1c; font-weight:700; padding:4px 8px; border-radius:4px;">
                                                <i class="fas fa-ban"></i> Retained (Rejected)
                                            </span>
                                        ` : `
                                            <span class="badge" style="background:#eff6ff; color:#1d4ed8; font-weight:700; padding:4px 8px; border-radius:4px;">
                                                <i class="fas fa-sync fa-spin"></i> Active in Flow
                                            </span>
                                        `}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    // 2. Admin (Principal) Tier 1 Review Section
    let adminReviewHtml = '';
    if (currentRole === 'admin') {
        const pendingAdmin = deleteRequests.filter(r => r.admin_status === 'Pending' && r.final_status === 'In Progress');
        if (pendingAdmin.length > 0) {
            adminReviewHtml = `
                <div class="card" style="margin-bottom:20px; border-left:4px solid #f59e0b; background:#fffbeb;">
                    <div class="card-header" style="background:#fef3c7;">
                        <span class="card-title" style="color:#92400e;">
                            <i class="fas fa-bell"></i> Payment Deletion Requests (Tier 1 Review - Principal Approval)
                        </span>
                        <span class="badge" style="background:#b45309; color:#fff; font-weight:700; padding:2px 8px; border-radius:10px;">
                            ${pendingAdmin.length} Pending
                        </span>
                    </div>
                    <div class="card-body" style="padding:0; overflow-x:auto;">
                        <table class="data-table" style="font-size:0.83rem; margin:0;">
                            <thead>
                                <tr>
                                    <th>Req #</th>
                                    <th>Receipt Ref</th>
                                    <th>Student</th>
                                    <th>Amount</th>
                                    <th>Accountant Reason</th>
                                    <th>Requested By</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${pendingAdmin.map(r => `
                                    <tr>
                                        <td><span style="font-family:monospace; font-weight:700;">#${r.id}</span></td>
                                        <td><span style="font-family:monospace; font-weight:700; color:#1e3a8a;">${r.receipt_no || r.payment_ref}</span></td>
                                        <td style="font-weight:700;">${r.student_name}</td>
                                        <td style="font-weight:700; color:#b91c1c;">₹${(r.paid || r.amount || 0).toLocaleString()}</td>
                                        <td style="color:#0f172a; font-weight:600;">${r.reason}</td>
                                        <td style="color:#64748b;">${r.requested_by_name || 'Accountant'}</td>
                                        <td style="white-space:nowrap;">
                                            <button class="btn btn-sm btn-primary" style="background:#16a34a; border-color:#16a34a; padding:4px 10px; font-weight:700; margin-right:4px;"
                                                    onclick="openReviewPaymentDeleteModal(${r.id}, 'approve', 'admin', '${r.receipt_no || r.payment_ref}', '${escapeJs(r.student_name)}', ${r.paid || r.amount})">
                                                ✅ Approve (Forward to Super Admin)
                                            </button>
                                            <button class="btn btn-sm btn-outline" style="color:#b91c1c; border-color:#fca5a5; padding:4px 10px; font-weight:600;"
                                                    onclick="openReviewPaymentDeleteModal(${r.id}, 'reject', 'admin', '${r.receipt_no || r.payment_ref}', '${escapeJs(r.student_name)}', ${r.paid || r.amount})">
                                                ❌ Reject
                                            </button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }
    }

    // 3. Super Admin Tier 2 Final Review Section
    let superAdminReviewHtml = '';
    if (currentRole === 'super_admin') {
        const readyForSuperAdmin = deleteRequests.filter(r => r.admin_status === 'Approved' && r.superadmin_status === 'Pending' && r.final_status === 'In Progress');
        const lockedAwaitingAdmin = deleteRequests.filter(r => r.admin_status === 'Pending' && r.final_status === 'In Progress');

        if (readyForSuperAdmin.length > 0 || lockedAwaitingAdmin.length > 0) {
            superAdminReviewHtml = `
                <div class="card" style="margin-bottom:20px; border-left:4px solid #b91c1c;">
                    <div class="card-header" style="display:flex; justify-content:space-between; align-items:center;">
                        <span class="card-title" style="color:#b91c1c;">
                            <i class="fas fa-shield-alt"></i> Payment Deletion Approvals (Tier 2 - Final Super Admin Authority)
                        </span>
                        <span style="font-size:0.75rem; color:#64748b;">
                            * Admin (Principal) must approve first. Process will not flow until Admin approves.
                        </span>
                    </div>
                    <div class="card-body" style="padding:0; overflow-x:auto;">
                        <table class="data-table" style="font-size:0.83rem; margin:0;">
                            <thead>
                                <tr>
                                    <th>Req #</th>
                                    <th>Receipt Ref</th>
                                    <th>Student</th>
                                    <th>Amount</th>
                                    <th>Accountant Reason</th>
                                    <th>Tier 1 (Admin/Principal)</th>
                                    <th>Super Admin Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${readyForSuperAdmin.map(r => `
                                    <tr style="background:#f0fdf4;">
                                        <td><span style="font-family:monospace; font-weight:700;">#${r.id}</span></td>
                                        <td><span style="font-family:monospace; font-weight:700; color:#1e3a8a;">${r.receipt_no || r.payment_ref}</span></td>
                                        <td style="font-weight:700;">${r.student_name}</td>
                                        <td style="font-weight:700; color:#b91c1c;">₹${(r.paid || r.amount || 0).toLocaleString()}</td>
                                        <td>${r.reason}</td>
                                        <td>
                                            <span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700; padding:4px 8px; border-radius:4px;">
                                                <i class="fas fa-check-circle"></i> Approved by Principal
                                            </span>
                                            <div style="font-size:0.72rem; color:#64748b; margin-top:2px;">${r.admin_notes || ''}</div>
                                        </td>
                                        <td style="white-space:nowrap;">
                                            <button class="btn btn-sm btn-primary" style="background:#b91c1c; border-color:#b91c1c; padding:5px 12px; font-weight:700; margin-right:4px;"
                                                    onclick="openReviewPaymentDeleteModal(${r.id}, 'approve', 'super_admin', '${r.receipt_no || r.payment_ref}', '${escapeJs(r.student_name)}', ${r.paid || r.amount})">
                                                🗑️ Final Approve & Delete from Database
                                            </button>
                                            <button class="btn btn-sm btn-outline" style="padding:5px 10px; font-weight:600;"
                                                    onclick="openReviewPaymentDeleteModal(${r.id}, 'reject', 'super_admin', '${r.receipt_no || r.payment_ref}', '${escapeJs(r.student_name)}', ${r.paid || r.amount})">
                                                ❌ Reject
                                            </button>
                                        </td>
                                    </tr>
                                `).join('')}

                                ${lockedAwaitingAdmin.map(r => `
                                    <tr style="opacity:0.65; background:#f8fafc;">
                                        <td><span style="font-family:monospace; font-weight:700;">#${r.id}</span></td>
                                        <td><span style="font-family:monospace; font-weight:700; color:#64748b;">${r.receipt_no || r.payment_ref}</span></td>
                                        <td>${r.student_name}</td>
                                        <td>₹${(r.paid || r.amount || 0).toLocaleString()}</td>
                                        <td>${r.reason}</td>
                                        <td>
                                            <span class="badge" style="background:#fef3c7; color:#92400e; font-weight:700; padding:4px 8px; border-radius:4px;">
                                                ⏳ Awaiting Admin First
                                            </span>
                                        </td>
                                        <td>
                                            <button class="btn btn-sm btn-outline" disabled style="opacity:0.6; cursor:not-allowed; font-size:0.75rem;"
                                                    title="Admin (Principal) must approve first. Process will not flow until Admin approves.">
                                                <i class="fas fa-lock"></i> Blocked (Awaiting Admin)
                                            </button>
                                        </td>
                                    </tr>
                                `).join('')}
                            </tbody>
                        </table>
                    </div>
                </div>
            `;
        }
    }

    const html = `
        ${accountantTrackerHtml}
        ${adminReviewHtml}
        ${superAdminReviewHtml}

        <div class="card">
            <div class="card-header" style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span class="card-title">Fee Payment Transactions</span>
                    <div style="font-size:0.76rem; color:#64748b; margin-top:2px;">
                        ${payments.length} transactions recorded | Currency: Indian Rupee (₹)
                    </div>
                </div>
                <div style="display:flex; gap:8px;">
                    ${currentRole === 'super_admin' || currentRole === 'accountant' ? `
                        <button class="btn btn-primary btn-sm" onclick="openModal('modal-record-payment')">➕ Record Fee Payment</button>
                    ` : ''}
                </div>
            </div>
            <div class="card-body" style="padding:0; overflow-x:auto;">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Receipt Ref</th>
                            <th>Student</th>
                            <th>Fee Description</th>
                            <th>Payment Method</th>
                            <th>Total (₹)</th>
                            <th>Paid (₹)</th>
                            <th>Status</th>
                            <th>Date</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${payments.length === 0 ? `
                            <tr>
                                <td colspan="9" style="text-align:center; padding:45px 20px; color:#64748b;">
                                    <div style="font-size:2.4rem; margin-bottom:10px;">💳</div>
                                    <div style="font-size:1.1rem; font-weight:700; color:#0f172a;">No Payment Transactions Found</div>
                                    <div style="font-size:0.85rem; margin-top:4px; max-width:480px; margin-left:auto; margin-right:auto;">
                                        All previous payment and fee records have been cleared. Click <strong>"➕ Record Fee Payment"</strong> above to record a fee transaction and print a receipt.
                                    </div>
                                </td>
                            </tr>
                        ` : payments.map(p => `
                            <tr>
                                <td><span style="font-family:monospace; font-weight:700; color:#1e3a8a;">${p.ref_no}</span></td>
                                <td style="font-weight:700;">${p.student_name} <br><small style="color:#64748b;">${p.class_name}</small></td>
                                <td>${p.title}</td>
                                <td>
                                    <span class="badge" style="background:#f1f5f9; color:#334155; font-weight:600; padding:2px 8px; border-radius:4px; font-size:0.75rem;">
                                        ${p.payment_method || 'Offline / Cash'}
                                    </span>
                                </td>
                                <td>₹${(p.amount || 0).toLocaleString()}</td>
                                <td style="font-weight:700; color:#15803d;">₹${(p.paid || 0).toLocaleString()}</td>
                                <td><span class="status-pill status-${(p.status || 'Paid').toLowerCase()}">${p.status}</span></td>
                                <td>${p.date}</td>
                                <td style="white-space:nowrap;">
                                    <button class="btn btn-outline btn-sm" onclick="printReceipt('${p.ref_no}', '${escapeJs(p.student_name)}', '${escapeJs(p.title)}', ${p.amount}, ${p.paid}, '${p.date}')">🖨️ Receipt</button>
                                    
                                    <!-- Accountant Deletion Request Button -->
                                    ${currentRole === 'accountant' ? `
                                        ${p.pending_delete_request_id ? `
                                            <span class="badge" style="background:#fef3c7; color:#92400e; font-size:0.72rem; padding:4px 8px; border-radius:4px; font-weight:700; margin-left:4px;">
                                                <i class="fas fa-hourglass-half"></i> Deletion Req #${p.pending_delete_request_id}
                                            </span>
                                        ` : `
                                            <button class="btn btn-outline btn-sm" style="color:#b91c1c; border-color:#fca5a5; font-size:0.75rem; margin-left:4px;"
                                                    onclick="openRequestPaymentDeleteModal(${p.id}, '${p.ref_no}', '${escapeJs(p.student_name)}', ${p.paid})">
                                                ⚠️ Request Deletion
                                            </button>
                                        `}
                                    ` : ''}

                                    <!-- Super Admin Direct Deletion Privilege -->
                                    ${currentRole === 'super_admin' ? `
                                        <button class="btn btn-sm" style="background:#fee2e2; color:#b91c1c; border:1px solid #fca5a5; font-weight:700; font-size:0.75rem; margin-left:4px;"
                                                onclick="superAdminDirectDeletePayment(${p.id}, '${p.ref_no}', '${escapeJs(p.student_name)}')">
                                            🗑️ Direct Delete (Super Admin)
                                        </button>
                                    ` : ''}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
    document.getElementById('portal-tab-content').innerHTML = html;
}

function printReceipt(ref, student, title, amount, paid, date) {
    const w = window.open('', '_blank');
    w.document.write(`
        <html>
        <head>
            <title>Receipt - ${ref}</title>
            <style>
                body { font-family: sans-serif; padding: 40px; color: #1e293b; }
                .receipt-box { max-width: 600px; margin: 0 auto; border: 2px solid #1e3a8a; padding: 30px; border-radius: 8px; }
                .header { text-align: center; border-bottom: 2px solid #1e3a8a; padding-bottom: 16px; margin-bottom: 20px; }
                .header h2 { color: #1e3a8a; margin: 0; }
                .row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e2e8f0; }
                .stamp { border: 2px solid #16a34a; color: #16a34a; font-weight: bold; padding: 8px 16px; display: inline-block; margin-top: 20px; transform: rotate(-5deg); border-radius: 4px; }
            </style>
        </head>
        <body>
            <div class="receipt-box">
                <div class="header">
                    <h2>GREENLAND SCHOOL</h2>
                    <p>OFFICIAL FEE PAYMENT RECEIPT</p>
                </div>
                <div class="row"><strong>Receipt No:</strong> <span>${ref}</span></div>
                <div class="row"><strong>Student:</strong> <span>${student}</span></div>
                <div class="row"><strong>Purpose:</strong> <span>${title}</span></div>
                <div class="row"><strong>Total Bill:</strong> <span>₹${amount.toLocaleString()}</span></div>
                <div class="row"><strong>Amount Paid:</strong> <span style="font-weight:bold; color:#15803d;">₹${paid.toLocaleString()}</span></div>
                <div class="row"><strong>Balance:</strong> <span>₹${(amount - paid).toLocaleString()}</span></div>
                <div class="row"><strong>Payment Date:</strong> <span>${date}</span></div>
                <div style="text-align:center;">
                    <div class="stamp">PAYMENT CONFIRMED - FEE</div>
                </div>
            </div>
            <script>window.print();</script>
        </body>
        </html>
    `);
    w.document.close();
}

// 7. TIMETABLE VIEW (MULTI-CHILD & STREAM AWARE)
async function renderTimetableTab() {
    document.getElementById('portal-header-title').innerText = 'Academic Timetable Schedule';
    document.getElementById('portal-header-desc').innerText = 'Weekly lecture, laboratory, and tutorial schedule';

    let activeClass = 'Class 10';
    let activeSection = 'Section A';
    let targetName = currentUser.name;
    let childSelectorHtml = '';

    if (currentRole === 'parent') {
        if (!parentOverviewData) {
            try {
                parentOverviewData = await fetch(`/api/parent/overview?parent_id=${currentUser.id || 8}`).then(r => r.json());
            } catch (e) {
                parentOverviewData = null;
            }
        }
        const children = (parentOverviewData && parentOverviewData.children) || [];
        if (children.length > 0) {
            if (parentTimetableChildIndex >= children.length) parentTimetableChildIndex = 0;
            const ch = children[parentTimetableChildIndex];
            activeClass = ch.class_name;
            activeSection = ch.section_name || 'Section A';
            targetName = ch.student_name;

            if (children.length > 1) {
                childSelectorHtml = `
                    <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:10px; padding:12px 16px; margin-bottom:16px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;">
                        <span style="font-size:0.82rem; font-weight:800; color:#1e3a8a; text-transform:uppercase;">
                            <i class="fas fa-users"></i> Child Timetable Switcher:
                        </span>
                        <div style="display:flex; gap:8px;">
                            ${children.map((c, idx) => `
                                <button type="button" class="btn btn-sm ${idx === parentTimetableChildIndex ? 'btn-primary' : 'btn-outline'}"
                                        onclick="switchParentTimetableChild(${idx})">
                                    ${c.gender === 'Female' ? '👧' : '👦'} ${c.student_name} (${c.class_name})
                                </button>
                            `).join('')}
                        </div>
                    </div>
                `;
            }
        }
    } else if (currentRole === 'student') {
        activeClass = 'Class 10';
        activeSection = 'Section A';
    }

    const tt = generateClientClassTimetable(activeClass, activeSection);

    const html = `
        ${childSelectorHtml}
        <div class="card">
            <div class="card-header" style="display:flex; justify-content:space-between; align-items:center;">
                <span class="card-title">Weekly Schedule: <strong>${targetName}</strong> (${activeClass} • ${activeSection})</span>
                <button class="btn btn-outline btn-sm" onclick="printElement('portal-tab-content')">
                    🖨️ Print Timetable Grid
                </button>
            </div>
            <div class="card-body" style="padding:0; overflow-x:auto;">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Day</th>
                            ${(tt.periods || []).map(p => `<th>${p}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${(tt.days || []).map(d => `
                            <tr>
                                <td style="font-weight:800; color:#1e3a8a;">${d.day}</td>
                                ${(d.subjects || []).map(s => `
                                    <td style="background:#f8fafc; font-size:0.8rem; font-weight:600; text-align:center;">
                                        <div style="color:#0f172a;">${s}</div>
                                    </td>
                                `).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
    document.getElementById('portal-tab-content').innerHTML = html;
}

// 8. E-LIBRARY & RESOURCE CENTER (BOOKSHELF MANAGEMENT & BOOK ISSUE TRACKING)
async function renderLibraryTab() {
    let data = { books: [], bookshelves: [], issued_books: [], library_booklet: [] };
    try {
        data = await fetch(`/api/library?user_id=${currentUser.id || ''}`).then(r => r.json());
        libraryDataCache = data;
    } catch (e) {
        data = { books: [], bookshelves: [], issued_books: [], library_booklet: [] };
    }

    document.getElementById('portal-header-title').innerText = 'E-Library & Resource Center';
    document.getElementById('portal-header-desc').innerText = `Physical Bookshelf Arrangement, Digital Book Loans & Student Booklet`;

    const isStudent = currentRole === 'student';
    const canManage = isAdministrationUser();
    const myBooklet = data.library_booklet || [];
    const books = data.books || [];
    const issuedBooks = data.issued_books || [];
    const bookshelves = data.bookshelves || [];

    const html = `
        <!-- 1. STUDENT PERSONAL LIBRARY BOOKLET (ONLY FOR STUDENT) -->
        ${isStudent ? `
            <div class="card" style="border-left:4px solid #1e3a8a; margin-bottom:20px;">
                <div class="card-header" style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span class="card-title">📘 My Digital Library Booklet (Student Official Card)</span>
                        <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">
                            Strictly filtered: displays books currently and previously issued in <strong>${currentUser.name}</strong>'s name
                        </div>
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="openLibraryBookletModal(${currentUser.id}, '${escapeJs(currentUser.name)}')">
                        🖨️ Print Full Library Booklet
                    </button>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    <table class="data-table" style="font-size:0.83rem;">
                        <thead>
                            <tr>
                                <th>Book Title & Author</th>
                                <th>ISBN</th>
                                <th>Bookshelf Location</th>
                                <th>Exact Issue Date & Time</th>
                                <th>Due Return Date</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${myBooklet.length === 0 ? `
                                <tr>
                                    <td colspan="6" style="text-align:center; padding:24px; color:#64748b;">
                                        No library books are currently issued in your name. Explore the catalogue below!
                                    </td>
                                </tr>
                            ` : myBooklet.map(b => `
                                <tr>
                                    <td style="font-weight:700; color:#0f172a;">
                                        ${b.book_title}<br>
                                        <span style="font-size:0.73rem; color:#64748b; font-weight:normal;">by ${b.book_author || 'Author'}</span>
                                    </td>
                                    <td><code>${b.isbn || '—'}</code></td>
                                    <td>
                                        <span class="badge" style="background:#e0e7ff; color:#3730a3; font-weight:700;">
                                            <i class="fas fa-layer-group"></i> ${b.bookshelf_no || 'Shelf A-1'}
                                        </span>
                                    </td>
                                    <td>
                                        <span style="font-weight:700; color:#1e3a8a;">
                                            <i class="fas fa-clock" style="color:#2563eb; font-size:0.75rem;"></i> ${b.issue_date}
                                        </span>
                                        <div style="font-size:0.72rem; color:#64748b; font-family:monospace;">${b.issue_time || '10:00:00'}</div>
                                    </td>
                                    <td><span style="color:#b91c1c; font-weight:600;">${b.due_date}</span></td>
                                    <td>
                                        <span class="status-pill status-${(b.status || 'Issued').toLowerCase()}">
                                            ${b.status}
                                        </span>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        ` : ''}

        <!-- 2. BOOKSHELF SEARCH & FILTER CONTROLS -->
        <div class="card" style="margin-bottom:20px;">
            <div class="card-header" style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <span class="card-title">📚 Library Catalogue & Bookshelf Directory (${books.length} Titles)</span>
                    <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">
                        Arranged across physical library racks and bookshelves
                    </div>
                </div>
                ${canManage ? `
                    <div style="display:flex; gap:8px; flex-wrap:wrap;">
                        <button class="btn btn-outline btn-sm" onclick="openIssueBookModal()">
                            📖 Issue Book to Student
                        </button>
                        <button class="btn btn-primary btn-sm" onclick="openModal('modal-add-book')">
                            ➕ Add New Book
                        </button>
                    </div>
                ` : ''}
            </div>
            <div class="card-body">
                <!-- Search & Bookshelf Filter Bar -->
                <div style="display:grid; grid-template-columns: 2fr 1.2fr 1fr; gap:12px; margin-bottom:16px;">
                    <div>
                        <label class="form-label" style="font-size:0.75rem; font-weight:700; text-transform:uppercase;">🔍 Search Title, Author, or ISBN</label>
                        <input type="text" id="lib-search-input" class="form-control" placeholder="Search books..." oninput="applyLibraryFilters()">
                    </div>
                    <div>
                        <label class="form-label" style="font-size:0.75rem; font-weight:700; text-transform:uppercase;">🗄️ Filter by Bookshelf Number</label>
                        <select id="lib-shelf-select" class="form-control" onchange="applyLibraryFilters()">
                            <option value="all">All Bookshelves</option>
                            ${bookshelves.map(s => `<option value="${s}">${s}</option>`).join('')}
                        </select>
                    </div>
                    <div>
                        <label class="form-label" style="font-size:0.75rem; font-weight:700; text-transform:uppercase;">📑 Category</label>
                        <select id="lib-cat-select" class="form-control" onchange="applyLibraryFilters()">
                            <option value="all">All Categories</option>
                            <option value="Mathematics">Mathematics</option>
                            <option value="Sciences">Sciences</option>
                            <option value="Physics">Physics</option>
                            <option value="Chemistry">Chemistry</option>
                            <option value="Biology">Biology</option>
                            <option value="Computer Science">Computer Science</option>
                            <option value="Literature">Literature</option>
                        </select>
                    </div>
                </div>

                <!-- Bookshelf Quick Badges -->
                <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center; margin-bottom:16px; padding:10px 14px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px;">
                    <span style="font-size:0.75rem; font-weight:800; color:#475569; text-transform:uppercase;">
                        <i class="fas fa-layer-group" style="color:#2563eb;"></i> Quick Bookshelf Filter:
                    </span>
                    <button type="button" class="btn btn-xs btn-primary lib-shelf-pill" onclick="selectShelfPill('all', this)" style="font-size:0.73rem; padding:3px 10px; border-radius:50px;">
                        All Shelves (${books.length})
                    </button>
                    ${bookshelves.map(s => {
                        const count = books.filter(b => b.bookshelf_no === s).length;
                        return `
                            <button type="button" class="btn btn-xs btn-outline lib-shelf-pill" onclick="selectShelfPill('${s}', this)" style="font-size:0.73rem; padding:3px 10px; border-radius:50px; background:#fff;">
                                🗄️ ${s} (${count})
                            </button>
                        `;
                    }).join('')}
                </div>

                <!-- Catalog Table -->
                <div style="overflow-x:auto;">
                    <table class="data-table" id="lib-catalog-table">
                        <thead>
                            <tr>
                                <th>Book Title</th>
                                <th>Author</th>
                                <th>ISBN</th>
                                <th>Category</th>
                                <th>Bookshelf Location</th>
                                <th>Stock (Avail / Total)</th>
                                <th>Status</th>
                                ${canManage ? `<th>Actions</th>` : ''}
                            </tr>
                        </thead>
                        <tbody id="lib-catalog-tbody">
                            ${books.map(b => `
                                <tr class="lib-book-row" data-title="${(b.title || '').toLowerCase()}" data-author="${(b.author || '').toLowerCase()}" data-isbn="${(b.isbn || '').toLowerCase()}" data-shelf="${b.bookshelf_no || 'Shelf A-1'}" data-cat="${b.category || ''}">
                                    <td style="font-weight:700; color:#0f172a;">${b.title}</td>
                                    <td>${b.author}</td>
                                    <td><code>${b.isbn}</code></td>
                                    <td><span style="background:#e0f2fe; color:#0369a1; padding:2px 8px; border-radius:4px; font-size:0.75rem; font-weight:bold;">${b.category}</span></td>
                                    <td>
                                        <span class="badge" style="background:#e0e7ff; color:#3730a3; font-weight:800; font-family:monospace; padding:4px 8px; border-radius:4px;">
                                            <i class="fas fa-layer-group"></i> ${b.bookshelf_no || 'Shelf A-1'}
                                        </span>
                                    </td>
                                    <td style="font-weight:700;">${b.available_copies} / ${b.total_copies}</td>
                                    <td>
                                        <span class="status-pill ${b.available_copies > 0 ? 'status-paid' : 'status-unpaid'}">
                                            ${b.available_copies > 0 ? 'In Stock' : 'Out of Stock'}
                                        </span>
                                    </td>
                                    ${canManage ? `
                                        <td>
                                            <div style="display:flex; gap:6px;">
                                                <button class="btn btn-outline btn-xs" style="font-size:0.72rem; padding:3px 8px;" onclick="openIssueBookModal(${b.id})" ${b.available_copies <= 0 ? 'disabled' : ''}>
                                                    📖 Issue
                                                </button>
                                                <button class="btn btn-outline btn-xs" style="font-size:0.72rem; padding:3px 6px; color:#dc2626; border-color:#fca5a5;" onclick="submitDeleteBook(${b.id}, '${escapeJs(b.title)}')">
                                                    🗑️
                                                </button>
                                            </div>
                                        </td>
                                    ` : ''}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>

        <!-- 3. ISSUED BOOKS LOG WITH EXACT TIME & BOOKSHELF (ADMINISTRATION & FACULTY) -->
        ${canManage || currentRole === 'teacher' ? `
            <div class="card" style="margin-top:20px;">
                <div class="card-header" style="display:flex; justify-content:space-between; align-items:center;">
                    <div>
                        <span class="card-title">📖 Issued Books Register & Loan Log (${issuedBooks.length} Records)</span>
                        <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">
                            Tracks which student has borrowed books, exact issue timestamps, and source bookshelf
                        </div>
                    </div>
                    ${canManage ? `
                        <button class="btn btn-primary btn-sm" onclick="openIssueBookModal()">
                            ➕ New Book Issue
                        </button>
                    ` : ''}
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    <table class="data-table" style="font-size:0.82rem;">
                        <thead>
                            <tr>
                                <th>Student Borrower</th>
                                <th>Book Title</th>
                                <th>Arranged Bookshelf</th>
                                <th>Exact Issue Date & Time</th>
                                <th>Due Return Date</th>
                                <th>Issued By</th>
                                <th>Status</th>
                                ${canManage ? `<th>Action</th>` : ''}
                            </tr>
                        </thead>
                        <tbody>
                            ${issuedBooks.length === 0 ? `
                                <tr>
                                    <td colspan="${canManage ? '8' : '7'}" style="text-align:center; padding:25px; color:#64748b;">
                                        No active or historical book issue records found in the library database.
                                    </td>
                                </tr>
                            ` : issuedBooks.map(b => `
                                <tr>
                                    <td style="font-weight:700; color:#0f172a;">
                                        ${b.student_name}<br>
                                        <span style="font-size:0.73rem; color:#64748b; font-weight:normal;">${b.adm_no || 'GS/2026'} • ${b.class_name || ''}</span>
                                    </td>
                                    <td>
                                        <strong>${b.book_title}</strong><br>
                                        <code style="font-size:0.7rem;">${b.isbn || ''}</code>
                                    </td>
                                    <td>
                                        <span class="badge" style="background:#e0e7ff; color:#3730a3; font-weight:800; font-family:monospace;">
                                            <i class="fas fa-layer-group"></i> ${b.bookshelf_no || 'Shelf A-1'}
                                        </span>
                                    </td>
                                    <td>
                                        <span style="font-weight:700; color:#1e3a8a;">
                                            <i class="fas fa-clock" style="color:#2563eb;"></i> ${b.issue_date}
                                        </span>
                                        <div style="font-size:0.72rem; color:#64748b; font-family:monospace; font-weight:bold;">${b.issue_time || '10:00:00'}</div>
                                    </td>
                                    <td><span style="color:#b91c1c; font-weight:600;">${b.due_date}</span></td>
                                    <td style="font-size:0.75rem; color:#475569;">${b.issuer_name || 'Administration Desk'}</td>
                                    <td>
                                        <span class="status-pill status-${(b.status || 'Issued').toLowerCase()}">
                                            ${b.status}
                                        </span>
                                        ${b.return_date ? `
                                            <div style="font-size:0.68rem; color:#15803d; margin-top:2px;">Returned: ${b.return_date}</div>
                                        ` : ''}
                                    </td>
                                    ${canManage ? `
                                        <td>
                                            ${b.status === 'Issued' ? `
                                                <button class="btn btn-sm btn-primary" style="background:#15803d; border-color:#15803d; font-size:0.72rem; padding:3px 8px;" onclick="submitReturnBook(${b.id})">
                                                    📥 Return Book
                                                </button>
                                            ` : `
                                                <span style="color:#64748b; font-size:0.75rem;">✓ Returned</span>
                                            `}
                                        </td>
                                    ` : ''}
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        ` : ''}
    `;
    document.getElementById('portal-tab-content').innerHTML = html;
}

function selectShelfPill(shelf, btn) {
    document.querySelectorAll('.lib-shelf-pill').forEach(b => {
        b.className = 'btn btn-xs btn-outline lib-shelf-pill';
        b.style.background = '#fff';
    });
    btn.className = 'btn btn-xs btn-primary lib-shelf-pill';
    btn.style.background = '';
    const select = document.getElementById('lib-shelf-select');
    if (select) {
        select.value = shelf;
        applyLibraryFilters();
    }
}

function applyLibraryFilters() {
    const searchVal = (document.getElementById('lib-search-input')?.value || '').toLowerCase();
    const shelfVal = document.getElementById('lib-shelf-select')?.value || 'all';
    const catVal = document.getElementById('lib-cat-select')?.value || 'all';

    const rows = document.querySelectorAll('.lib-book-row');
    rows.forEach(r => {
        const title = r.getAttribute('data-title') || '';
        const author = r.getAttribute('data-author') || '';
        const isbn = r.getAttribute('data-isbn') || '';
        const shelf = r.getAttribute('data-shelf') || '';
        const cat = r.getAttribute('data-cat') || '';

        const matchesSearch = !searchVal || title.includes(searchVal) || author.includes(searchVal) || isbn.includes(searchVal) || shelf.toLowerCase().includes(searchVal);
        const matchesShelf = shelfVal === 'all' || shelf.toLowerCase() === shelfVal.toLowerCase();
        const matchesCat = catVal === 'all' || cat.toLowerCase() === catVal.toLowerCase();

        if (matchesSearch && matchesShelf && matchesCat) {
            r.style.display = '';
        } else {
            r.style.display = 'none';
        }
    });
}

async function openIssueBookModal(preselectedBookId = null) {
    if (!isAdministrationUser()) {
        alert('Access Denied: Only administration users (Owner, Super Admin, Principal, Librarian) can issue books.');
        return;
    }
    try {
        const [libRes, stdRes] = await Promise.all([
            fetch('/api/library').then(r => r.json()),
            fetch('/api/students').then(r => r.json())
        ]);
        libraryDataCache = libRes;
        libraryStudentsCache = stdRes;

        const bookSelect = document.getElementById('issue-book-id');
        if (bookSelect) {
            bookSelect.innerHTML = (libRes.books || []).map(b => `
                <option value="${b.id}" data-shelf="${b.bookshelf_no || 'Shelf A-1'}" data-stock="${b.available_copies}" ${preselectedBookId == b.id ? 'selected' : ''}>
                    ${b.title} (${b.author}) — ${b.bookshelf_no || 'Shelf A-1'} [Stock: ${b.available_copies}]
                </option>
            `).join('');
        }

        const studentSelect = document.getElementById('issue-student-id');
        if (studentSelect) {
            studentSelect.innerHTML = (stdRes || []).map(s => `
                <option value="${s.user_id}">
                    ${s.name} (${s.adm_no} • ${s.class_name || ''})
                </option>
            `).join('');
        }

        const now = new Date();
        const dateStr = now.toISOString().split('T')[0];
        const timeStr = now.toTimeString().split(' ')[0];
        const dueDate = new Date();
        dueDate.setDate(dueDate.getDate() + 14);
        const dueStr = dueDate.toISOString().split('T')[0];

        const issueDateInput = document.getElementById('issue-date');
        const issueTimeInput = document.getElementById('issue-time');
        const issueDueInput = document.getElementById('issue-due-date');
        const issueNotesInput = document.getElementById('issue-notes');

        if (issueDateInput) issueDateInput.value = dateStr;
        if (issueTimeInput) issueTimeInput.value = timeStr;
        if (issueDueInput) issueDueInput.value = dueStr;
        if (issueNotesInput) issueNotesInput.value = `Authorized by ${currentUser ? currentUser.name : 'Administration'}`;

        onIssueBookSelectionChange();
        openModal('modal-issue-book');
    } catch (err) {
        alert('Error loading book issue form: ' + err.message);
    }
}

function onIssueBookSelectionChange() {
    const bookSelect = document.getElementById('issue-book-id');
    const shelfDisp = document.getElementById('issue-book-shelf-disp');
    const stockDisp = document.getElementById('issue-book-stock-disp');
    if (!bookSelect) return;
    const opt = bookSelect.options[bookSelect.selectedIndex];
    if (opt) {
        const shelf = opt.getAttribute('data-shelf') || 'Shelf A-1';
        const stock = parseInt(opt.getAttribute('data-stock') || '0');
        if (shelfDisp) shelfDisp.innerText = shelf;
        if (stockDisp) {
            stockDisp.innerText = stock > 0 ? `${stock} Copies Available` : 'Out of Stock';
            stockDisp.style.background = stock > 0 ? '#dcfce7' : '#fee2e2';
            stockDisp.style.color = stock > 0 ? '#15803d' : '#b91c1c';
        }
    }
}

async function submitIssueBook(e) {
    e.preventDefault();
    const bookSelect = document.getElementById('issue-book-id');
    const studentSelect = document.getElementById('issue-student-id');
    const issueDateInput = document.getElementById('issue-date');
    const issueTimeInput = document.getElementById('issue-time');
    const issueDueInput = document.getElementById('issue-due-date');
    const issueNotesInput = document.getElementById('issue-notes');
    const shelfDisp = document.getElementById('issue-book-shelf-disp');

    const payload = {
        book_id: parseInt(bookSelect.value),
        student_user_id: parseInt(studentSelect.value),
        issue_date: issueDateInput.value,
        issue_time: issueTimeInput.value,
        due_date: issueDueInput.value,
        bookshelf_no: shelfDisp ? shelfDisp.innerText : 'Shelf A-1',
        issuer_name: issueNotesInput ? issueNotesInput.value : currentUser.name
    };

    try {
        const res = await fetch('/api/library/issue', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(data.message || 'Book successfully issued to student!');
            closeModal('modal-issue-book');
            if (currentTab === 'library') renderLibraryTab();
            else if (currentTab === 'dashboard') renderDashboardTab();
        } else {
            alert(data.message || 'Could not issue book.');
        }
    } catch (err) {
        alert('Server communication error: ' + err.message);
    }
}

async function submitReturnBook(requestId) {
    if (!confirm('Confirm return of this book to its assigned bookshelf? Available stock will be restored.')) return;
    try {
        const res = await fetch('/api/library/return', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ request_id: requestId })
        });
        const data = await res.json();
        if (data.success) {
            alert(data.message || 'Book marked as returned successfully!');
            if (currentTab === 'library') renderLibraryTab();
        } else {
            alert(data.message || 'Error processing return');
        }
    } catch (err) {
        alert('Server communication error: ' + err.message);
    }
}

async function submitDeleteBook(bookId, bookTitle) {
    if (!confirm(`Are you sure you want to remove '${bookTitle}' from the library catalogue?`)) return;
    try {
        const res = await fetch('/api/library/delete', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ book_id: bookId })
        });
        const data = await res.json();
        if (data.success) {
            alert(data.message || 'Book removed from catalogue.');
            if (currentTab === 'library') renderLibraryTab();
        } else {
            alert(data.message || 'Could not delete book.');
        }
    } catch (err) {
        alert('Server error: ' + err.message);
    }
}

async function openLibraryBookletModal(userId, studentName) {
    const targetUserId = userId || (currentUser ? currentUser.id : 25);
    const targetName = studentName || (currentUser ? currentUser.name : 'Student');
    try {
        const res = await fetch(`/api/library?user_id=${targetUserId}`);
        const data = await res.json();
        const booklet = data.library_booklet || [];

        const html = `
            <div style="border:2px solid #1e3a8a; border-radius:12px; padding:20px; font-family:'Segoe UI', sans-serif;">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:2px solid #1e3a8a; padding-bottom:12px; margin-bottom:16px;">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <img src="assets/Logo_Greenland_School.png" style="width:48px; height:48px; object-fit:contain;" alt="GS">
                        <div>
                            <h2 style="margin:0; font-size:1.3rem; color:#1e3a8a; font-weight:800;">GREENLAND SCHOOL</h2>
                            <p style="margin:0; font-size:0.8rem; color:#64748b;">E-LIBRARY BORROWER BOOKLET & ISSUE REGISTER</p>
                        </div>
                    </div>
                    <div style="text-align:right;">
                        <span style="font-size:0.75rem; background:#eff6ff; color:#1e40af; border:1px solid #bfdbfe; padding:4px 10px; border-radius:4px; font-weight:700;">
                            OFFICIAL DIGITAL CARD
                        </span>
                    </div>
                </div>

                <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; background:#f8fafc; border:1px solid #e2e8f0; padding:12px; border-radius:8px; margin-bottom:16px; font-size:0.85rem;">
                    <div><strong>Student Name:</strong> <span style="color:#0f172a;">${targetName}</span></div>
                    <div><strong>Session:</strong> <span>2026-2027</span></div>
                    <div><strong>Borrower Account:</strong> <code style="color:#1e40af;">Active</code></div>
                    <div><strong>Card Generated:</strong> <span>${new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' })}</span></div>
                </div>

                <h4 style="font-size:0.95rem; font-weight:700; color:#0f172a; margin-bottom:10px;">
                    📚 Personal Issued Books Register (${booklet.length} Entries)
                </h4>
                <div style="overflow-x:auto;">
                    <table class="data-table" style="font-size:0.82rem; width:100%;">
                        <thead>
                            <tr>
                                <th>Book Title & Author</th>
                                <th>ISBN</th>
                                <th>Bookshelf Location</th>
                                <th>Exact Issue Date & Time</th>
                                <th>Due Return Date</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${booklet.length === 0 ? `
                                <tr>
                                    <td colspan="6" style="text-align:center; padding:20px; color:#64748b;">
                                        No books currently recorded in this student's library booklet.
                                    </td>
                                </tr>
                            ` : booklet.map(b => `
                                <tr>
                                    <td style="font-weight:700; color:#0f172a;">
                                        ${b.book_title}<br>
                                        <span style="font-size:0.73rem; color:#64748b; font-weight:normal;">by ${b.book_author || 'Author'}</span>
                                    </td>
                                    <td><code>${b.isbn || '—'}</code></td>
                                    <td>
                                        <span class="badge" style="background:#e0e7ff; color:#3730a3; font-weight:700;">
                                            <i class="fas fa-layer-group"></i> ${b.bookshelf_no || 'Shelf A-1'}
                                        </span>
                                    </td>
                                    <td>
                                        <span style="font-weight:700; color:#1e3a8a;">
                                            <i class="fas fa-clock" style="color:#2563eb; font-size:0.75rem;"></i> ${b.issue_date}
                                        </span>
                                        <div style="font-size:0.72rem; color:#64748b; font-family:monospace;">${b.issue_time || '10:00:00'}</div>
                                    </td>
                                    <td><span style="color:#b91c1c; font-weight:600;">${b.due_date}</span></td>
                                    <td>
                                        <span class="status-pill status-${(b.status || 'Issued').toLowerCase()}">
                                            ${b.status}
                                        </span>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>

                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:24px; padding-top:16px; border-top:1px solid #e2e8f0; font-size:0.75rem; color:#64748b;">
                    <div>Authorized by: <strong>Librarian Rose Davies</strong> & Administration</div>
                    <div>Valid across all Greenland School Reading Rooms</div>
                </div>
            </div>
        `;
        document.getElementById('library-booklet-printable-content').innerHTML = html;
        openModal('modal-library-booklet');
    } catch (err) {
        alert('Could not open library booklet: ' + err.message);
    }
}

// 9. CLASSES & SECTIONS VIEW
async function renderClassesTab() {
    const classes = await fetch('/api/classes').then(r => r.json());
    document.getElementById('portal-header-title').innerText = 'Classes & Sections Configuration';
    document.getElementById('portal-header-desc').innerText = 'Manage school classes from Class 1 to Class 12 (Science, Commerce, Arts) and configured sections';

    const html = `
        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:20px;">
            ${classes.map(c => `
                <div class="card" style="margin-bottom:0;">
                    <div class="card-header">
                        <span class="card-title">${c.name}</span>
                        <span style="font-size:0.75rem; background:#1e3a8a; color:white; padding:2px 8px; border-radius:4px;">${c.class_type}</span>
                    </div>
                    <div class="card-body">
                        <div style="font-size:0.85rem; color:#64748b; margin-bottom:12px;">Enrolled Students: <strong>${c.student_count || 18}</strong></div>
                        <div style="font-weight:700; font-size:0.8rem; margin-bottom:6px;">Configured Sections / Arms:</div>
                        <div style="display:flex; gap:6px; flex-wrap:wrap;">
                            ${(c.sections || []).map(sec => `
                                <span style="background:#f1f5f9; border:1px solid #cbd5e1; padding:3px 8px; border-radius:4px; font-size:0.75rem; font-weight:600;">
                                    ${sec.name}
                                </span>
                            `).join('')}
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
    document.getElementById('portal-tab-content').innerHTML = html;
}

// 10. NOTICES VIEW
async function renderNoticesTab() {
    const notices = await fetch('/api/notices').then(r => r.json());
    document.getElementById('portal-header-title').innerText = 'Noticeboard & Circulars';
    document.getElementById('portal-header-desc').innerText = 'Broadcast official updates to parents, faculty, and students';

    const html = `
        <div class="card">
            <div class="card-header">
                <span class="card-title">Circulars & Announcements</span>
                ${currentRole === 'super_admin' || currentRole === 'admin' ? `
                    <button class="btn btn-primary btn-sm" onclick="openModal('modal-post-notice')">📢 Post Announcement</button>
                ` : ''}
            </div>
            <div class="card-body">
                <div class="notices-grid">
                    ${notices.map(n => `
                        <div class="notice-card">
                            <div class="notice-meta">
                                <span class="notice-tag">${n.category}</span>
                                <span class="notice-date">${n.date}</span>
                            </div>
                            <h4 class="notice-title">${n.title}</h4>
                            <p class="notice-snippet">${n.content}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
    document.getElementById('portal-tab-content').innerHTML = html;
}

// 11. SETTINGS VIEW
async function renderSettingsTab() {
    if (currentRole !== 'super_admin') {
        showTab('dashboard');
        return;
    }

    const s = await fetch('/api/settings').then(r => r.json());
    document.getElementById('portal-header-title').innerText = 'System Configuration & Settings';
    document.getElementById('portal-header-desc').innerText = 'Institutional settings, live SMTP email dispatch gateway, and carrier SMS configuration';

    const html = `
        <div style="display:grid; grid-template-columns: 1fr; gap:20px; max-width:920px;">
            <!-- Institutional Settings Card -->
            <div class="card">
                <div class="card-header" style="background:#0f172a; color:#fff;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <i class="fas fa-school" style="color:#60a5fa;"></i>
                        <span class="card-title" style="color:#fff;">Greenland School Institutional Settings</span>
                    </div>
                </div>
                <div class="card-body">
                    <form id="settings-form" onsubmit="saveSettings(event)">
                        <div class="form-group">
                            <label class="form-label">School Full Name</label>
                            <input type="text" name="system_name" class="form-control" value="${s.system_name || 'Greenland School'}">
                        </div>
                        <div class="form-grid">
                            <div class="form-group">
                                <label class="form-label">Academic Session</label>
                                <input type="text" name="current_session" class="form-control" value="${s.current_session || '2026-2027'}">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Current Term</label>
                                <input type="text" name="current_term" class="form-control" value="${s.current_term || 'First Term'}">
                            </div>
                        </div>
                        <div class="form-grid">
                            <div class="form-group">
                                <label class="form-label">Official Phone</label>
                                <input type="text" name="phone" class="form-control" value="${s.phone || '+91 761 700 5055, +91 761 700 5056'}">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Official Email</label>
                                <input type="email" name="system_email" class="form-control" value="${s.system_email || 'info@greenlandschool.net'}">
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Campus Physical Address</label>
                            <input type="text" name="address" class="form-control" value="${s.address || 'Khadpathar, Renukoot, Sonbhadra, Uttar Pradesh - 231217'}">
                        </div>
                        <button type="submit" class="btn btn-primary" style="margin-top:10px;">💾 Save Institutional Changes</button>
                    </form>
                </div>
            </div>

            <!-- Email (SMTP) Dispatch Gateway Configuration Card -->
            <div class="card">
                <div class="card-header" style="background:#1e3a8a; color:#fff;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <i class="fas fa-envelope-open-text" style="color:#93c5fd; font-size:1.15rem;"></i>
                        <div>
                            <span class="card-title" style="color:#fff;">Email (SMTP) Dispatch Gateway</span>
                            <div style="font-size:0.75rem; color:#cbd5e1;">Configure live SMTP server to dispatch official approval emails directly to candidate inboxes</div>
                        </div>
                    </div>
                </div>
                <div class="card-body">
                    <!-- Helper Banner -->
                    <div style="background:#eff6ff; border-left:4px solid #2563eb; padding:12px 16px; border-radius:6px; margin-bottom:18px; font-size:0.83rem; color:#1e40af; line-height:1.5;">
                        <strong><i class="fas fa-info-circle"></i> Gmail Live Delivery Instructions:</strong>
                        To deliver emails from your Gmail account (e.g. <code>your-email@gmail.com</code>):
                        <ol style="margin:6px 0 0 18px; padding:0; font-size:0.8rem; color:#334155; line-height:1.6;">
                            <li>Ensure 2-Step Verification is active on your Google Account.</li>
                            <li>Go to <strong>Google Account &gt; Security &gt; 2-Step Verification &gt; App passwords</strong>.</li>
                            <li>Create an App Password (name it "Greenland School") and copy the 16-character code.</li>
                            <li>Paste into <strong>SMTP Password</strong> below and click Save!</li>
                        </ol>
                    </div>

                    <form id="smtp-settings-form" onsubmit="saveSettings(event)">
                        <div class="form-grid">
                            <div class="form-group">
                                <label class="form-label">SMTP Server Host</label>
                                <input type="text" id="smtp-host" name="smtp_host" class="form-control" value="${s.smtp_host || 'smtp.gmail.com'}" placeholder="e.g. smtp.gmail.com">
                            </div>
                            <div class="form-group">
                                <label class="form-label">SMTP Port</label>
                                <input type="number" id="smtp-port" name="smtp_port" class="form-control" value="${s.smtp_port || '587'}" placeholder="587 (TLS) or 465 (SSL)">
                            </div>
                        </div>
                        <div class="form-grid">
                            <div class="form-group">
                                <label class="form-label">SMTP Username / Email Address</label>
                                <input type="text" id="smtp-user" name="smtp_user" class="form-control" value="${s.smtp_user || ''}" placeholder="e.g. your_email@gmail.com">
                            </div>
                            <div class="form-group">
                                <label class="form-label">SMTP App Password / Auth Secret</label>
                                <div style="display:flex; gap:6px;">
                                    <input type="password" id="smtp-pass" name="smtp_pass" class="form-control" value="${s.smtp_pass || ''}" placeholder="16-character App Password">
                                    <button type="button" class="btn btn-outline btn-sm" onclick="togglePasswordVisibility('smtp-pass')">👁️</button>
                                </div>
                            </div>
                        </div>
                        <div class="form-grid">
                            <div class="form-group">
                                <label class="form-label">Sender Display Name</label>
                                <input type="text" id="smtp-sender-name" name="smtp_sender_name" class="form-control" value="${s.smtp_sender_name || 'Greenland School Admissions'}">
                            </div>
                            <div class="form-group">
                                <label class="form-label">Sender From Email</label>
                                <input type="text" id="smtp-sender-email" name="smtp_sender_email" class="form-control" value="${s.smtp_sender_email || ''}" placeholder="admissions@greenlandschool.net">
                            </div>
                        </div>
                        <div class="form-grid" style="grid-template-columns: 1fr 1fr; margin-top:6px;">
                            <label style="display:flex; align-items:center; gap:8px; font-size:0.85rem; cursor:pointer;">
                                <input type="checkbox" name="smtp_tls" value="1" ${(s.smtp_tls === undefined || s.smtp_tls === '1') ? 'checked' : ''}> Enable STARTTLS (Recommended for Port 587)
                            </label>
                            <label style="display:flex; align-items:center; gap:8px; font-size:0.85rem; cursor:pointer;">
                                <input type="checkbox" name="smtp_ssl" value="1" ${s.smtp_ssl === '1' ? 'checked' : ''}> Use Direct SSL (For Port 465)
                            </label>
                        </div>
                        <div style="display:flex; gap:10px; margin-top:16px; flex-wrap:wrap; align-items:center;">
                            <button type="submit" class="btn btn-primary">💾 Save SMTP Gateway Credentials</button>
                            <div style="display:flex; gap:6px; align-items:center; margin-left:auto;">
                                <input type="email" id="test-email-target" class="form-control" style="max-width:220px; font-size:0.82rem;" placeholder="Test to: email@example.com" value="${s.smtp_user || (currentUser ? currentUser.email : 'vs0839265@gmail.com')}">
                                <button type="button" class="btn btn-outline" style="font-weight:700;" onclick="testEmailSettings()">🧪 Send Test Email</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>

            <!-- SMS Gateway & WhatsApp Configuration Card -->
            <div class="card">
                <div class="card-header" style="background:#0f172a; color:#fff;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        <i class="fas fa-mobile-alt" style="color:#4ade80; font-size:1.15rem;"></i>
                        <div>
                            <span class="card-title" style="color:#fff;">SMS Gateway &amp; WhatsApp Transmission</span>
                            <div style="font-size:0.75rem; color:#94a3b8;">Automatic Carrier SMS and 1-Click WhatsApp Instant Web Dispatches</div>
                        </div>
                    </div>
                </div>
                <div class="card-body">
                    <form id="sms-settings-form" onsubmit="saveSettings(event)">
                        <div class="form-grid">
                            <div class="form-group">
                                <label class="form-label">SMS Provider Service</label>
                                <select id="sms-provider" name="sms_provider" class="form-control">
                                    <option value="none" ${(!s.sms_provider || s.sms_provider === 'none') ? 'selected' : ''}>Direct WhatsApp &amp; Device SMS Protocol (Zero API cost)</option>
                                    <option value="fast2sms" ${s.sms_provider === 'fast2sms' ? 'selected' : ''}>Fast2SMS (Quick SMS Gateway for India)</option>
                                    <option value="webhook" ${s.sms_provider === 'webhook' ? 'selected' : ''}>Custom HTTP Webhook URL</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Sender ID / Route Header</label>
                                <input type="text" id="sms-sender-id" name="sms_sender_id" class="form-control" value="${s.sms_sender_id || 'GRNSCH'}" placeholder="e.g. GRNSCH">
                            </div>
                        </div>
                        <div class="form-group">
                            <label class="form-label">SMS Provider API Key / Auth Token</label>
                            <input type="password" id="sms-api-key" name="sms_api_key" class="form-control" value="${s.sms_api_key || ''}" placeholder="Enter Fast2SMS or gateway authorization key">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Custom SMS Webhook URL (For Webhook mode)</label>
                            <input type="text" id="sms-webhook-url" name="sms_webhook_url" class="form-control" value="${s.sms_webhook_url || ''}" placeholder="https://api.gateway.com/send?to={phone}&msg={message}&apikey={api_key}">
                            <small style="color:#64748b;">Supports placeholders: <code>{phone}</code>, <code>{message}</code>, <code>{api_key}</code></small>
                        </div>
                        <div style="display:flex; gap:10px; margin-top:16px; flex-wrap:wrap; align-items:center;">
                            <button type="submit" class="btn btn-primary">💾 Save SMS Settings</button>
                            <div style="display:flex; gap:6px; align-items:center; margin-left:auto;">
                                <input type="text" id="test-sms-target" class="form-control" style="max-width:180px; font-size:0.82rem;" placeholder="Test to: +91..." value="${(currentUser && currentUser.phone) ? currentUser.phone : '+918004125223'}">
                                <button type="button" class="btn btn-outline" style="font-weight:700;" onclick="testSmsSettings()">🧪 Send Test SMS / WA</button>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        </div>
    `;
    document.getElementById('portal-tab-content').innerHTML = html;
}

function togglePasswordVisibility(fieldId) {
    const f = document.getElementById(fieldId);
    if (!f) return;
    f.type = f.type === 'password' ? 'text' : 'password';
}

async function testEmailSettings() {
    const targetEmail = (document.getElementById('test-email-target')?.value || '').trim();
    if (!targetEmail) {
        alert('Please enter a destination email address to test.');
        return;
    }
    const smtpHost = document.getElementById('smtp-host')?.value || '';
    const smtpPort = document.getElementById('smtp-port')?.value || '587';
    const smtpUser = document.getElementById('smtp-user')?.value || '';
    const smtpPass = document.getElementById('smtp-pass')?.value || '';
    const senderName = document.getElementById('smtp-sender-name')?.value || '';
    const senderEmail = document.getElementById('smtp-sender-email')?.value || '';

    if (!smtpUser || !smtpPass) {
        alert('⚠️ Please enter your SMTP Username and Password/App Password before testing live transmission.');
        return;
    }

    try {
        const res = await fetch('/api/settings/test_email', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                to_email: targetEmail,
                smtp_host: smtpHost,
                smtp_port: smtpPort,
                smtp_user: smtpUser,
                smtp_pass: smtpPass,
                smtp_sender_name: senderName,
                smtp_sender_email: senderEmail,
                smtp_tls: '1'
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ SMTP DISPATCH SUCCESS!

${data.message}`);
        } else {
            alert(`❌ SMTP DISPATCH FAILED:

${data.error || 'Connection error'}

Please check host, port, username, and ensure you use a valid 16-character Google App Password if using Gmail.`);
        }
    } catch (err) {
        alert('Could not test email dispatch: ' + err.message);
    }
}

async function testSmsSettings() {
    const targetPhone = (document.getElementById('test-sms-target')?.value || '').trim();
    if (!targetPhone) {
        alert('Please enter a destination phone number to test.');
        return;
    }
    const provider = document.getElementById('sms-provider')?.value || 'none';
    const apiKey = document.getElementById('sms-api-key')?.value || '';
    const webhookUrl = document.getElementById('sms-webhook-url')?.value || '';

    try {
        const res = await fetch('/api/settings/test_sms', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                target_phone: targetPhone,
                sms_provider: provider,
                sms_api_key: apiKey,
                sms_webhook_url: webhookUrl
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ SMS TEST RESULT:

${data.message}`);
            if (data.whatsapp_url) {
                if (confirm('Would you like to open the WhatsApp test message link now?')) {
                    window.open(data.whatsapp_url, '_blank');
                }
            }
        } else {
            alert(`⚠️ SMS GATEWAY REPORT:

${data.error || 'Failed to dispatch test message'}`);
        }
    } catch (err) {
        alert('Could not test SMS dispatch: ' + err.message);
    }
}

async function saveSettings(e) {
    e.preventDefault();
    const formData = new FormData(e.target);
    const obj = {};
    formData.forEach((val, key) => obj[key] = val);
    try {
        const res = await fetch('/api/settings', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(obj)
        });
        const data = await res.json();
        alert(data.message || 'Settings saved successfully!');
    } catch (err) {
        alert('Failed to update settings: ' + err.message);
    }
}

// =====================================================================
// MODAL CONTROLS & FORM ACTIONS
// =====================================================================
async function openModal(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = 'flex';

    if (id === 'modal-create-user') {
        await populateAdminIdOptions('create-user-admin-id');
    }
    if (id === 'modal-it-request-create-user') {
        await populateAdminIdOptions('it-create-admin-id');
    }
    if (id === 'modal-assign-user-role') {
        await populateAdminIdOptions('assign-role-admin-id');
    }

    if (id === 'modal-record-payment' || id === 'modal-enter-marks') {
        try {
            const students = await fetch('/api/students').then(r => r.json());
            const targetSelect = id === 'modal-record-payment' ? document.getElementById('pay-student-id') : document.getElementById('mark-student-id');
            if (targetSelect) {
                if (!students || students.length === 0) {
                    targetSelect.innerHTML = '<option value="" disabled selected>No students enrolled yet - Admit student first</option>';
                } else {
                    targetSelect.innerHTML = '<option value="" disabled selected>-- Select Enrolled Student --</option>' +
                        students.map(s => `<option value="${s.id}">${s.name} (${s.adm_no} - ${s.class_name})</option>`).join('');
                }
            }
        } catch (e) {
            console.error('Error populating students in modal:', e);
        }
    }
}

function closeModal(id) {
    const el = document.getElementById(id);
    if (el) el.style.display = 'none';
}

// Admission inquiry submission
async function handleAdmissionSubmit(e) {
    e.preventDefault();
    const btn = e.target.querySelector('button[type="submit"]');
    btn.disabled = true;
    btn.innerText = 'Submitting Application...';

    const selectedPref = (document.querySelector('input[name="notification_pref"]:checked') ? document.querySelector('input[name="notification_pref"]:checked').value : 'both');
    const secVal = document.getElementById('adm-section') ? document.getElementById('adm-section').value : 'Section A';

    const payload = {
        applicant_name: document.getElementById('adm-student-name').value,
        parent_name: document.getElementById('adm-parent-name').value,
        email: document.getElementById('adm-email').value,
        phone: document.getElementById('adm-phone').value,
        grade_applying: document.getElementById('adm-grade').value,
        preferred_section: secVal,
        previous_school: document.getElementById('adm-prev-school').value,
        message: document.getElementById('adm-notes').value,
        notification_pref: selectedPref
    };

    try {
        const res = await fetch('/api/admissions/inquire', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            const channelText = selectedPref === 'both' ? 'Both Phone Number & Email Address' : (selectedPref === 'phone' ? 'Phone Number Only (SMS/WhatsApp)' : 'Email Address Only');
            document.getElementById('admission-result-msg').innerHTML = `
                <div style="background:#dcfce7; color:#166534; padding:18px 20px; border-radius:10px; margin-top:18px; border-left:5px solid #10b981; box-shadow:0 2px 8px rgba(16, 185, 129, 0.15);">
                    <div style="font-weight:800; font-size:1.05rem; display:flex; align-items:center; gap:8px;">
                        <span>✅</span> Application Submitted & Registered!
                    </div>
                    <div style="margin-top:6px; font-size:0.92rem;">
                        Inquiry Reference Number: <strong style="color:#0f172a; font-size:1.15rem; letter-spacing:1px;">${data.ref_no}</strong>
                    </div>
                    <div style="margin-top:8px; padding-top:8px; border-top:1px solid #bbf7d0; font-size:0.86rem; color:#14532d;">
                        <i class="fas fa-bell"></i> <strong>Selected Notification Channel:</strong> <span class="badge" style="background:#15803d; color:#fff; padding:3px 8px; border-radius:4px; font-weight:700;">${channelText}</span><br>
                        Once reviewed and approved by the <strong>Owner (Director)</strong>, <strong>Super Admin</strong>, or <strong>Principal</strong>, official admission clearance will be dispatched to <strong>${selectedPref === 'both' ? `${payload.phone} & ${payload.email}` : (selectedPref === 'phone' ? payload.phone : payload.email)}</strong>.
                    </div>
                </div>
            `;
            e.target.reset();
        } else {
            alert(data.error || 'Failed to submit admission inquiry.');
        }
    } catch (err) {
        alert('Could not submit inquiry. Please try again.');
    } finally {
        btn.disabled = false;
        btn.innerText = 'Submit Admission Inquiry';
    }
}

function handleClassChange(classVal) {
    const streamContainer = document.getElementById('class12-stream-container');
    if (!streamContainer) return;
    if (classVal === 'Class 12') {
        streamContainer.style.display = 'block';
    } else {
        streamContainer.style.display = 'none';
    }
}

// Admit student submission (Mandatory 12-Digit Aadhaar Enforcement)
async function submitAdmitStudent(e) {
    e.preventDefault();
    const classVal = document.getElementById('new-std-class').value;
    const sectionVal = document.getElementById('new-std-section') ? document.getElementById('new-std-section').value : 'Section A';
    const streamVal = (classVal === 'Class 12' && document.getElementById('new-std-stream')) ? document.getElementById('new-std-stream').value : '';
    const aadhaarVal = (document.getElementById('new-std-aadhaar')?.value || '').trim().replace(/[\s\-]/g, '');

    // Strict 12-digit Aadhaar validation
    if (!aadhaarVal || aadhaarVal.length !== 12 || !/^\d{12}$/.test(aadhaarVal)) {
        alert("⚠️ Admission Blocked: A strictly 12-digit numeric Aadhaar number is mandatory for school admission. No admission can be processed without a valid Aadhaar number.");
        document.getElementById('new-std-aadhaar')?.focus();
        return;
    }

    const payload = {
        name: document.getElementById('new-std-name').value,
        class_name: classVal,
        section: sectionVal,
        stream: streamVal,
        aadhaar_no: aadhaarVal,
        blood_group: document.getElementById('new-std-blood').value,
        gender: document.getElementById('new-std-gender').value,
        phone: document.getElementById('new-std-phone').value,
        approved_by: currentUser ? (currentUser.name || currentUser.username) : 'Super Admin',
        admission_status: 'Approved for New Admission'
    };

    try {
        const res = await fetch('/api/students', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`🎉 ${data.message}`);
            closeModal('modal-admit-student');
            if (currentTab === 'students') renderStudentsTab();
            loadInitialData();
        } else {
            alert(`⚠️ Admission Blocked: ${data.message}`);
        }
    } catch (err) {
        alert('Could not admit student: ' + err.message);
    }
}

// Record fee payment submission
async function submitRecordPayment(e) {
    e.preventDefault();
    const payload = {
        student_id: parseInt(document.getElementById('pay-student-id').value),
        title: document.getElementById('pay-title').value,
        amount: parseFloat(document.getElementById('pay-amount').value),
        paid: parseFloat(document.getElementById('pay-paid').value)
    };

    try {
        const res = await fetch('/api/payments', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        alert(`Payment recorded! Ref: ${data.ref_no}`);
        closeModal('modal-record-payment');
        if (currentTab === 'payments') renderPaymentsTab();
    } catch (err) {
        alert('Could not record payment');
    }
}

// Enter marks submission
async function submitEnterMarks(e) {
    e.preventDefault();
    const payload = {
        student_id: parseInt(document.getElementById('mark-student-id').value),
        subject_id: parseInt(document.getElementById('mark-subject-id').value),
        ca_score: parseFloat(document.getElementById('mark-ca').value),
        exam_score: parseFloat(document.getElementById('mark-exam').value)
    };

    try {
        const res = await fetch('/api/marks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        alert(`Mark saved! Total: ${data.total}, Grade: ${data.grade} (${data.remark})`);
        closeModal('modal-enter-marks');
        if (currentTab === 'marks') renderMarksTab();
    } catch (err) {
        alert('Could not save mark');
    }
}

// Post notice submission
async function submitPostNotice(e) {
    e.preventDefault();
    const payload = {
        title: document.getElementById('notice-title').value,
        content: document.getElementById('notice-content').value,
        category: document.getElementById('notice-category').value
    };

    try {
        const res = await fetch('/api/notices', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        alert(data.message || 'Notice published!');
        closeModal('modal-post-notice');
        if (currentTab === 'notices') renderNoticesTab();
    } catch (err) {
        alert('Could not post notice');
    }
}

// Add book submission
async function submitAddBook(e) {
    e.preventDefault();
    const payload = {
        title: document.getElementById('book-title').value,
        author: document.getElementById('book-author').value,
        isbn: document.getElementById('book-isbn').value,
        category: document.getElementById('book-category').value,
        total_copies: parseInt(document.getElementById('book-copies').value),
        bookshelf_no: document.getElementById('book-bookshelf') ? document.getElementById('book-bookshelf').value : 'Shelf A-1'
    };

    try {
        const res = await fetch('/api/library/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        alert(data.message || 'Book cataloged!');
        closeModal('modal-add-book');
        if (currentTab === 'library') renderLibraryTab();
    } catch (err) {
        alert('Could not add book');
    }
}

// =====================================================================
// BULK STUDENT EXCEL ADMISSION & SMART EMAIL GENERATION
// =====================================================================
let uploadedExcelBase64 = null;
let uploadedExcelFileName = null;

function downloadStudentExcelTemplate() {
    window.location.href = '/api/students/sample_excel';
}

function handleExcelFileSelect(e) {
    const file = e.target.files ? e.target.files[0] : null;
    if (!file) return;

    uploadedExcelFileName = file.name;
    const label = document.getElementById('excel-file-name-label');
    const submitBtn = document.getElementById('btn-submit-excel-upload');
    const previewWrap = document.getElementById('excel-preview-wrap');
    const resultBox = document.getElementById('excel-result-box');
    if (resultBox) resultBox.style.display = 'none';

    if (label) {
        label.innerHTML = `📄 <strong>${file.name}</strong> (${(file.size / 1024).toFixed(1)} KB)`;
    }

    const reader = new FileReader();
    reader.onload = function(evt) {
        uploadedExcelBase64 = evt.target.result;
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerText = `🚀 Import & Admit Students from ${file.name}`;
        }
        
        if (file.name.toLowerCase().endsWith('.csv')) {
            showCsvClientPreview(evt.target.result);
        } else {
            if (previewWrap) {
                previewWrap.style.display = 'block';
                document.getElementById('excel-preview-count').innerText = `Spreadsheet Attached: ${file.name}`;
                document.getElementById('excel-preview-tbody').innerHTML = `
                    <tr>
                        <td colspan="6" style="text-align:center; padding:16px; color:#1e40af;">
                            Ready to parse and admit students. Click the blue <strong>"Import & Admit Students"</strong> button below.
                        </td>
                    </tr>
                `;
            }
        }
    };
    reader.readAsDataURL(file);
}

function showCsvClientPreview(dataUrl) {
    try {
        const base64Data = dataUrl.split(',')[1];
        const text = atob(base64Data);
        const lines = text.split(/\r?\n/).filter(l => l.trim().length > 0);
        if (lines.length < 2) return;
        
        const previewWrap = document.getElementById('excel-preview-wrap');
        const tbody = document.getElementById('excel-preview-tbody');
        const countSpan = document.getElementById('excel-preview-count');
        
        previewWrap.style.display = 'block';
        countSpan.innerText = `Detected Students in CSV (${lines.length - 1})`;
        
        let html = '';
        for (let i = 1; i < Math.min(lines.length, 6); i++) {
            const cols = lines[i].split(',').map(c => c.trim().replace(/^["']|["']$/g, ''));
            const fn = cols[0] || 'Student';
            const ln = cols[1] || '';
            const cl = cols[2] || 'Class';
            const gender = cols[3] || '—';
            const parent = cols[5] || cols[6] || 'Guardian';
            const cleanFn = fn.replace(/[^a-zA-Z0-9]/g, '');
            const cleanLn = ln.replace(/[^a-zA-Z0-9]/g, '');
            const cleanCl = cl.replace(/[^a-zA-Z0-9]/g, '');
            const predictedEmail = `GS_student_${cleanFn}_${cleanLn}_${cleanCl}@greenlandschool.net`;
            
            html += `
                <tr>
                    <td>${i}</td>
                    <td><strong>${fn} ${ln}</strong></td>
                    <td><span class="badge" style="background:#e0e7ff; color:#3730a3; padding:2px 6px; border-radius:4px; font-weight:700;">${cl}</span></td>
                    <td>${gender}</td>
                    <td>${parent}</td>
                    <td><code style="color:#1d4ed8; font-weight:600;">${predictedEmail}</code></td>
                </tr>
            `;
        }
        if (lines.length > 6) {
            html += `<tr><td colspan="6" style="text-align:center; color:#64748b; font-style:italic;">+ ${lines.length - 6} more student record(s)...</td></tr>`;
        }
        tbody.innerHTML = html;
    } catch (e) {
        console.warn('CSV preview parse error:', e);
    }
}

async function submitBulkExcelUpload() {
    if (!uploadedExcelBase64) {
        alert('Please select an Excel or CSV file first.');
        return;
    }

    const submitBtn = document.getElementById('btn-submit-excel-upload');
    const resultBox = document.getElementById('excel-result-box');
    submitBtn.disabled = true;
    submitBtn.innerText = '⏳ Processing Admission & Generating Accounts...';

    try {
        const res = await fetch('/api/students/upload_excel', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                filename: uploadedExcelFileName,
                file_data: uploadedExcelBase64,
                approved_by: currentUser ? (currentUser.name || currentUser.username) : 'Super Admin'
            })
        });
        const data = await res.json();

        if (data.success && data.students) {
            resultBox.style.display = 'block';
            let studentRows = data.students.map((s, idx) => `
                <tr>
                    <td>${idx + 1}</td>
                    <td><strong>${s.name}</strong></td>
                    <td><span style="font-weight:700; color:#1e40af;">${s.adm_no}</span></td>
                    <td><span class="badge" style="background:#e0e7ff; color:#3730a3; padding:2px 6px; border-radius:4px; font-weight:700;">${s.class_name}</span></td>
                    <td><code style="color:#15803d; font-weight:bold;">${s.email}</code></td>
                    <td><code>${s.username}</code></td>
                    <td><span style="background:#dcfce7; color:#166534; padding:2px 6px; border-radius:4px; font-weight:700; font-size:0.75rem;">✓ Admitted</span></td>
                </tr>
            `).join('');

            resultBox.innerHTML = `
                <div style="background:#f0fdf4; border:1px solid #86efac; border-radius:8px; padding:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                        <div>
                            <div style="font-weight:800; font-size:1rem; color:#166534;">🎉 Admission Batch Complete!</div>
                            <div style="font-size:0.82rem; color:#15803d; margin-top:2px;">
                                Successfully admitted <strong>${data.count}</strong> student(s). All accounts created with password <strong>Greenland@2026</strong>.
                            </div>
                        </div>
                    </div>
                    <div style="max-height:220px; overflow-y:auto; border:1px solid #bbf7d0; border-radius:6px; background:white;">
                        <table class="data-table" style="font-size:0.78rem; margin:0;">
                            <thead>
                                <tr>
                                    <th>#</th>
                                    <th>Student</th>
                                    <th>Adm No.</th>
                                    <th>Class</th>
                                    <th>Generated Email ID</th>
                                    <th>User ID</th>
                                    <th>Status</th>
                                </tr>
                            </thead>
                            <tbody>${studentRows}</tbody>
                        </table>
                    </div>
                </div>
            `;

            submitBtn.innerText = '✓ Admission Successful';
            submitBtn.style.background = '#16a34a';

            const freshStudents = await fetch('/api/students').then(r => r.json());
            siteData.students = freshStudents;
            cachedStudentsList = freshStudents;
            if (currentTab === 'students') {
                renderStudentsTab();
            }
            loadInitialData();
        } else {
            alert(data.message || 'Excel import failed');
            submitBtn.disabled = false;
            submitBtn.innerText = '🚀 Retry Import';
        }
    } catch (err) {
        alert('Network or server error during upload: ' + err.message);
        submitBtn.disabled = false;
        submitBtn.innerText = '🚀 Retry Import';
    }
}

// =====================================================================
// SUPER ADMIN: FACULTY & TEACHERS MANAGEMENT
// =====================================================================
let cachedTeachersList = [];

async function renderTeachersTab() {
    if (currentRole !== 'super_admin') {
        showTab('dashboard');
        return;
    }
    document.getElementById('portal-header-title').innerText = 'Faculty & Teacher Management';
    document.getElementById('portal-header-desc').innerText = 'Add new teachers, assign class teachers to classes/arms, and manage credentials';

    const teachers = await fetch('/api/teachers').then(r => r.json());
    cachedTeachersList = teachers;
    const classes = await fetch('/api/classes').then(r => r.json());

    const assignedCount = teachers.filter(t => t.assigned_class).length;
    const unassignedCount = teachers.length - assignedCount;

    const html = `
        <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); margin-bottom:20px;">
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Total Faculty Members</h5>
                    <h2>${teachers.length}</h2>
                    <span style="font-size:0.75rem; color:#2563eb;">Registered Teachers</span>
                </div>
                <div class="metric-icon metric-blue">👨‍🏫</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Assigned Class Teachers</h5>
                    <h2>${assignedCount}</h2>
                    <span style="font-size:0.75rem; color:#16a34a;">Heading a Class Arm</span>
                </div>
                <div class="metric-icon metric-green">🏫</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>General Faculty</h5>
                    <h2>${unassignedCount}</h2>
                    <span style="font-size:0.75rem; color:#f59e0b;">Subject Specialists</span>
                </div>
                <div class="metric-icon metric-amber">📚</div>
            </div>
        </div>

        <div class="card">
            <div class="card-header" style="flex-wrap:wrap; gap:12px; justify-content:space-between; align-items:center;">
                <div>
                    <span class="card-title">Faculty Members Directory (<span id="teachers-count">${teachers.length}</span>)</span>
                    <p style="font-size:0.78rem; color:#64748b; margin:2px 0 0;">Greenland School Teaching Staff & Class Teacher Allocations</p>
                </div>
                <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:center;">
                    <input type="text" id="teacher-search-input" placeholder="🔍 Search teacher, subject, class..." class="form-control" style="width:230px; padding:7px 12px; font-size:0.85rem;" oninput="filterTeachersTable()">
                    <button class="btn btn-outline btn-sm" onclick="openAssignClassTeacherModal()">🏫 Assign Class Teacher</button>
                    <button class="btn btn-primary btn-sm" onclick="openModal('modal-add-teacher')">➕ Add New Teacher</button>
                </div>
            </div>
            <div class="card-body" style="padding:0; overflow-x:auto;">
                <table class="data-table" id="teachers-table">
                    <thead>
                        <tr>
                            <th>Faculty Member</th>
                            <th>Subject / Dept</th>
                            <th>Qualification</th>
                            <th>User ID & Password</th>
                            <th>Assigned Class Teacher Role</th>
                            <th>Phone Number</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${teachers.length === 0 ? `
                            <tr>
                                <td colspan="7" style="text-align:center; padding:40px; color:#64748b;">
                                    No teachers registered yet. Click <strong>"➕ Add New Teacher"</strong> above to add faculty.
                                </td>
                            </tr>
                        ` : teachers.map(t => `
                            <tr>
                                <td style="display:flex; align-items:center; gap:10px;">
                                    <img src="${t.photo}" style="width:36px; height:36px; border-radius:50%; object-fit:cover; border:2px solid #e2e8f0;">
                                    <div>
                                        <div style="font-weight:700; color:#0f172a;">${t.name}</div>
                                        <div style="font-size:0.75rem; color:#64748b;">${t.email}</div>
                                    </div>
                                </td>
                                <td><span style="font-weight:600; color:#1e40af;">${t.subject || 'General'}</span></td>
                                <td><span style="font-size:0.83rem; color:#475569;">${t.qualification || 'Certified'}</span></td>
                                <td>
                                    <div style="font-family:monospace; font-size:0.8rem; font-weight:700; color:#0369a1;">${t.username}</div>
                                    <div style="font-size:0.73rem; color:#64748b;">Pass: <code>${t.password || 'Greenland@2026'}</code></div>
                                </td>
                                <td>
                                    ${t.assigned_class ? `
                                        <span class="badge" style="background:#dcfce7; color:#15803d; border:1px solid #bbf7d0; font-weight:700; padding:4px 8px; border-radius:6px; display:inline-flex; align-items:center; gap:5px;">
                                            <i class="fas fa-check-circle"></i> ${t.assigned_class}
                                        </span>
                                    ` : `
                                        <span class="badge" style="background:#f1f5f9; color:#94a3b8; padding:4px 8px; border-radius:6px; font-size:0.75rem;">
                                            Not Assigned
                                        </span>
                                    `}
                                </td>
                                <td><span style="font-size:0.82rem; color:#475569;">${t.phone || '—'}</span></td>
                                <td>
                                    <div style="display:flex; gap:6px;">
                                        <button class="btn btn-outline btn-sm" style="padding:4px 8px; font-size:0.76rem;" onclick="openAssignClassTeacherModal(${t.id})" title="Assign / Change Class Teacher">🏫 Assign</button>
                                        <button class="btn btn-outline btn-sm" style="padding:4px 8px; font-size:0.76rem;" onclick="openEditTeacherModal(${t.id})" title="Edit Details">✏️ Edit</button>
                                        <button class="btn btn-outline btn-sm" style="padding:4px 8px; font-size:0.76rem; color:#dc2626; border-color:#fca5a5;" onclick="confirmDeleteTeacher(${t.id}, '${t.name.replace(/'/g, "\\'")}')" title="Remove Faculty">🗑️</button>
                                    </div>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    document.getElementById('portal-tab-content').innerHTML = html;
    populateClassSectionDropdowns(classes);
}

// =====================================================================
// LEAVE MANAGEMENT SYSTEM (TEACHER, PRINCIPAL & SUPER ADMIN)
// =====================================================================

function renderLeaveQuotaBanner(b, gender) {
    if (!b) return '';
    const isFemale = (gender || '').toLowerCase() === 'female';
    return `
        <!-- Official Annual Leave Balance Quotas -->
        <div class="card" style="margin-bottom:20px; background:linear-gradient(135deg, #f8fafc 0%, #eff6ff 100%); border:1px solid #bfdbfe;">
            <div class="card-header" style="justify-content:space-between; align-items:center; border-bottom:1px solid #dbeafe;">
                <div>
                    <span class="card-title" style="color:#1e3a8a;"><i class="fas fa-calendar-check"></i> Official Annual Leave Balance Quotas (Year ${b.year || 2026})</span>
                    <p style="font-size:0.78rem; color:#475569; margin-top:2px;">
                        Gender Classification: <strong style="color:#1e40af;">${gender || 'Staff'}</strong> | Credited automatically as per Greenland School Service Guidelines
                    </p>
                </div>
                <span class="badge" style="background:#2563eb; color:white; padding:5px 12px; border-radius:6px; font-weight:700;">
                    ${isFemale ? '♀ Female Employee Quota' : '♂ Male Employee Quota'}
                </span>
            </div>
            <div class="card-body" style="padding:16px;">
                <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:12px; margin-bottom:14px;">
                    <!-- CL -->
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:8px; padding:12px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                        <div style="font-size:0.74rem; font-weight:700; color:#64748b; text-transform:uppercase;">Casual Leave (CL)</div>
                        <div style="font-size:1.55rem; font-weight:800; color:#1e3a8a; margin:4px 0;">${b.cl_remaining} <span style="font-size:0.82rem; font-weight:500; color:#64748b;">/ ${b.cl_total} d</span></div>
                        <div style="font-size:0.72rem; color:#16a34a;">Used: ${b.cl_used} d • Full Pay Executive</div>
                    </div>
                    <!-- EL -->
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:8px; padding:12px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                        <div style="font-size:0.74rem; font-weight:700; color:#64748b; text-transform:uppercase;">Earned Leave (EL)</div>
                        <div style="font-size:1.55rem; font-weight:800; color:#059669; margin:4px 0;">${b.el_remaining} <span style="font-size:0.82rem; font-weight:500; color:#64748b;">/ ${b.el_total} d</span></div>
                        <div style="font-size:0.72rem; color:#059669;">Used: ${b.el_used} d • 15d Jan 1 & July 1</div>
                    </div>
                    <!-- HPL -->
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:8px; padding:12px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                        <div style="font-size:0.74rem; font-weight:700; color:#64748b; text-transform:uppercase;">Half Pay Leave (HPL)</div>
                        <div style="font-size:1.55rem; font-weight:800; color:#d97706; margin:4px 0;">${b.hpl_remaining} <span style="font-size:0.82rem; font-weight:500; color:#64748b;">/ ${b.hpl_total} d</span></div>
                        <div style="font-size:0.72rem; color:#d97706;">Used: ${b.hpl_used} d • 10d bi-annually</div>
                    </div>
                    <!-- Maternity or Paternity based on gender -->
                    ${isFemale ? `
                        <div style="background:#fff1f2; border:1px solid #fecdd3; border-radius:8px; padding:12px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                            <div style="font-size:0.74rem; font-weight:700; color:#be185d; text-transform:uppercase;">Maternity Leave</div>
                            <div style="font-size:1.55rem; font-weight:800; color:#db2777; margin:4px 0;">${b.maternity_remaining} <span style="font-size:0.82rem; font-weight:500; color:#be185d;">/ ${b.maternity_total} d</span></div>
                            <div style="font-size:0.72rem; color:#be185d;">Used: ${b.maternity_used} d • Female Only (Up to 2 children)</div>
                        </div>
                    ` : `
                        <div style="background:#eef2ff; border:1px solid #c7d2fe; border-radius:8px; padding:12px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                            <div style="font-size:0.74rem; font-weight:700; color:#4338ca; text-transform:uppercase;">Paternity Leave</div>
                            <div style="font-size:1.55rem; font-weight:800; color:#4f46e5; margin:4px 0;">${b.paternity_remaining} <span style="font-size:0.82rem; font-weight:500; color:#4338ca;">/ ${b.paternity_total} d</span></div>
                            <div style="font-size:0.72rem; color:#4f46e5;">Used: ${b.paternity_used} d • Male Only (15 Days)</div>
                        </div>
                    `}
                    <!-- CCL -->
                    <div style="background:white; border:1px solid #e2e8f0; border-radius:8px; padding:12px 14px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
                        <div style="font-size:0.74rem; font-weight:700; color:#6d28d9; text-transform:uppercase;">Child Care Leave (CCL)</div>
                        <div style="font-size:1.55rem; font-weight:800; color:#7c3aed; margin:4px 0;">${b.ccl_remaining} <span style="font-size:0.82rem; font-weight:500; color:#64748b;">/ ${b.ccl_total} d</span></div>
                        <div style="font-size:0.72rem; color:#7c3aed;">Used: ${b.ccl_used} d • 730d career quota</div>
                    </div>
                </div>

                <!-- Official Bracket Policy Information Details -->
                <div style="background:#ffffff; border:1px solid #cbd5e1; border-radius:8px; padding:12px 16px; font-size:0.82rem; color:#334155; line-height:1.6;">
                    <div style="font-weight:700; color:#1e3a8a; margin-bottom:6px; display:flex; align-items:center; gap:6px;">
                        <span>📋 Greenland School Leave Quota Policy Guidelines:</span>
                    </div>
                    <ul style="margin:0; padding-left:18px; display:flex; flex-direction:column; gap:4px;">
                        <li><strong>Casual Leave (CL):</strong> Set at 8 days per calendar year. It is an executive instruction rather than a recognized form of leave, meaning your pay does not stop, and it cannot be combined with regular leave types.</li>
                        <li><strong>Earned Leave (EL):</strong> Credited in advance twice a year (15 days each on January 1 and July 1). You can accumulate a maximum of 300 days in your career, which can also be encashed at the time of retirement.</li>
                        <li><strong>Half Pay Leave (HPL):</strong> Credited at a rate of 10 days every half-year. This is calculated based on completed service periods and can be commuted onto medical grounds.</li>
                        <li><strong>Maternity & Paternity Leave:</strong> Female employees are eligible for 180 days of Maternity Leave (up to 2 surviving children). Male employees are allowed 15 days of Paternity Leave.</li>
                        <li><strong>Child Care Leave (CCL):</strong> Available to female employees and single male employees for up to 730 days across their entire service to look after minor children.</li>
                    </ul>
                    <div style="margin-top:8px; padding-top:8px; border-top:1px dashed #cbd5e1; font-size:0.78rem; color:#b91c1c; font-weight:600;">
                        ⚠️ <strong>Deletion Rule:</strong> Teachers can cancel/delete their leave before approval by Principal or Super Admin. Once approved, leaves can only be deleted by the Super Admin account (or Owner/Director).
                    </div>
                </div>
            </div>
        </div>
    `;
}

async function deleteLeaveRequest(leaveId) {
    if (!confirm('Are you sure you want to delete this leave record?')) return;
    try {
        const res = await fetch('/api/leaves/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                leave_id: leaveId,
                user_id: currentUser ? currentUser.id : null,
                username: currentUser ? currentUser.username : '',
                role: currentRole
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✓ ${data.message}`);
            renderLeavesTab();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (err) {
        alert('Could not delete leave record: ' + err.message);
    }
}

async function renderLeavesTab() {
    if (!['teacher', 'admin', 'super_admin', 'accountant'].includes(currentRole)) {
        showTab('dashboard');
        return;
    }

    document.getElementById('portal-header-title').innerText = 'Leave Management System';
    document.getElementById('portal-header-desc').innerText = 'Faculty leave applications, quota allocations, principal delegation, and executive approval routing';

    const userIdParam = currentUser ? currentUser.id : '';
    const data = await fetch(`/api/leaves?user_id=${userIdParam}`).then(r => r.json());
    const leaves = data.leaves || [];
    const principalOnLeave = data.principal_on_leave || false;
    const activePrincipalLeave = data.active_principal_leave;
    const balances = data.balances || null;
    const userGender = data.gender || (currentUser && currentUser.gender ? currentUser.gender : 'Male');
    const allStaffBalances = data.all_staff_balances || [];

    let contentHtml = '';

    if (currentRole === 'teacher') {
        const myLeaves = leaves.filter(l => l.user_id === currentUser.id);
        const pendingCount = myLeaves.filter(l => l.status === 'Pending').length;
        const approvedCount = myLeaves.filter(l => l.status === 'Approved').length;

        contentHtml = `
            ${renderLeaveQuotaBanner(balances, userGender)}

            <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); margin-bottom:20px;">
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Total Applications</h5>
                        <h2>${myLeaves.length}</h2>
                        <span style="font-size:0.75rem; color:#2563eb;">Leave Requests</span>
                    </div>
                    <div class="metric-icon metric-blue">🏖️</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Approved Leaves</h5>
                        <h2>${approvedCount}</h2>
                        <span style="font-size:0.75rem; color:#16a34a;">Granted Absences</span>
                    </div>
                    <div class="metric-icon metric-green">✓</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Pending Review</h5>
                        <h2>${pendingCount}</h2>
                        <span style="font-size:0.75rem; color:#f59e0b;">Awaiting Decision</span>
                    </div>
                    <div class="metric-icon metric-amber">⏳</div>
                </div>
            </div>

            <div class="card">
                <div class="card-header" style="justify-content:space-between; align-items:center;">
                    <div>
                        <span class="card-title">My Leave History & Status</span>
                        <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Track your submitted leave requests and official approvals</p>
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="openApplyLeaveModal('teacher')">➕ Apply for Leave</button>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Leave Category</th>
                                <th>From - To Dates</th>
                                <th>Duration</th>
                                <th>Reason / Purpose</th>
                                <th>Status</th>
                                <th>Approved / Reviewed By</th>
                                <th>Applied On</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${myLeaves.length === 0 ? `
                                <tr>
                                    <td colspan="8" style="text-align:center; padding:40px; color:#64748b;">
                                        You have not submitted any leave applications yet. Click <strong>"➕ Apply for Leave"</strong> to submit one.
                                    </td>
                                </tr>
                            ` : myLeaves.map(l => `
                                <tr>
                                    <td><span style="font-weight:700; color:#1e3a8a;">${l.leave_type}</span></td>
                                    <td><strong>${l.start_date}</strong> to <strong>${l.end_date}</strong></td>
                                    <td><span class="badge" style="background:#e0f2fe; color:#0369a1; padding:3px 8px; border-radius:4px; font-weight:700;">${l.days_count} Day${l.days_count > 1 ? 's' : ''}</span></td>
                                    <td style="max-width:240px;">${l.reason}</td>
                                    <td>
                                        <span class="badge" style="padding:4px 10px; border-radius:6px; font-weight:700; ${
                                            l.status === 'Approved' ? 'background:#dcfce7; color:#15803d; border:1px solid #bbf7d0;' :
                                            (l.status === 'Rejected' ? 'background:#fee2e2; color:#b91c1c; border:1px solid #fecaca;' :
                                            'background:#fef3c7; color:#b45309; border:1px solid #fde68a;')
                                        }">
                                            ${l.status === 'Approved' ? '✓ Approved' : (l.status === 'Rejected' ? '✕ Rejected' : '⏳ Pending Review')}
                                        </span>
                                    </td>
                                    <td>
                                        ${l.approver_name || l.approver_role ? `
                                            <div style="font-weight:600; font-size:0.83rem;">${l.approver_name || (l.approver_role === 'super_admin' ? 'Super Admin' : 'Principal')}</div>
                                            ${l.approver_notes ? `<div style="font-size:0.75rem; color:#64748b; font-style:italic;">"${l.approver_notes}"</div>` : ''}
                                        ` : '<span style="color:#94a3b8; font-size:0.8rem;">Awaiting Review</span>'}
                                    </td>
                                    <td><span style="font-size:0.78rem; color:#64748b;">${l.created_at ? l.created_at.split(' ')[0] : '—'}</span></td>
                                    <td>
                                        ${l.status === 'Pending' ? `
                                            <button class="btn btn-outline btn-sm" style="color:#dc2626; border-color:#fca5a5; font-weight:700; font-size:0.75rem; padding:4px 8px;" onclick="deleteLeaveRequest(${l.id})">
                                                🗑️ Cancel / Delete
                                            </button>
                                        ` : (l.status === 'Approved' ? `
                                            <span style="font-size:0.75rem; color:#64748b; font-weight:600;">
                                                <i class="fas fa-lock"></i> Super Admin Only
                                            </span>
                                        ` : `
                                            <button class="btn btn-outline btn-sm" style="color:#64748b; border-color:#cbd5e1; font-size:0.75rem; padding:4px 8px;" onclick="deleteLeaveRequest(${l.id})">
                                                🗑️ Delete
                                            </button>
                                        `)}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    } else if (currentRole === 'admin') {
        const teacherLeaves = leaves.filter(l => l.applicant_role === 'teacher');
        const principalLeaves = leaves.filter(l => l.user_id === currentUser.id);

        contentHtml = `
            ${renderLeaveQuotaBanner(balances, userGender)}

            ${principalOnLeave ? `
                <div style="background:#fef3c7; border:2px solid #f59e0b; color:#92400e; padding:16px 20px; border-radius:10px; margin-bottom:20px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span style="font-size:1.8rem;">🏖️</span>
                        <div>
                            <strong style="font-size:1rem;">You are currently on APPROVED LEAVE!</strong>
                            <div style="font-size:0.84rem; margin-top:2px;">While you are on leave, teacher leave approval authority is automatically delegated directly to the Super Admin.</div>
                        </div>
                    </div>
                    <span class="badge" style="background:#b45309; color:white; padding:6px 14px; border-radius:6px; font-weight:700;">Active Principal Leave</span>
                </div>
            ` : `
                <div style="background:#eff6ff; border:1px solid #bfdbfe; color:#1e40af; padding:12px 18px; border-radius:10px; margin-bottom:20px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;">
                    <div>
                        <strong>Principal Duty Status: ON DUTY (Active)</strong>
                        <div style="font-size:0.82rem; margin-top:2px;">You are currently managing all teacher leave approvals. If you take leave, approvals will automatically route to Super Admin.</div>
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="openApplyLeaveModal('principal')">🏖️ Apply for Principal Leave</button>
                </div>
            `}

            <!-- Teacher Leave Approvals for Principal -->
            <div class="card" style="margin-bottom:24px;">
                <div class="card-header" style="justify-content:space-between; align-items:center;">
                    <div>
                        <span class="card-title">👨‍🏫 Teacher Leave Approval Requests</span>
                        <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Review and decide on faculty leave applications</p>
                    </div>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Teacher Name</th>
                                <th>Leave Category</th>
                                <th>Dates & Days</th>
                                <th>Reason / Purpose</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${teacherLeaves.length === 0 ? `
                                <tr>
                                    <td colspan="6" style="text-align:center; padding:35px; color:#64748b;">
                                        No teacher leave requests currently on file.
                                    </td>
                                </tr>
                            ` : teacherLeaves.map(l => `
                                <tr>
                                    <td>
                                        <div style="font-weight:700; color:#0f172a;">${l.applicant_name}</div>
                                        <div style="font-size:0.75rem; color:#64748b;"><code>${l.applicant_username}</code> (${l.applicant_gender || 'Staff'})</div>
                                    </td>
                                    <td><span style="font-weight:600; color:#1e40af;">${l.leave_type}</span></td>
                                    <td>
                                        <div>${l.start_date} to ${l.end_date}</div>
                                        <span class="badge" style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:4px; font-size:0.72rem; font-weight:700;">${l.days_count} Days</span>
                                    </td>
                                    <td style="max-width:240px; font-size:0.85rem;">${l.reason}</td>
                                    <td>
                                        <span class="badge" style="padding:4px 10px; border-radius:6px; font-weight:700; ${
                                            l.status === 'Approved' ? 'background:#dcfce7; color:#15803d;' :
                                            (l.status === 'Rejected' ? 'background:#fee2e2; color:#b91c1c;' :
                                            'background:#fef3c7; color:#b45309;')
                                        }">
                                            ${l.status}
                                        </span>
                                    </td>
                                    <td>
                                        ${l.status === 'Pending' ? `
                                            ${principalOnLeave ? `
                                                <span style="font-size:0.75rem; color:#b45309; font-weight:700; background:#fef3c7; padding:4px 8px; border-radius:4px;">
                                                    Routed to Super Admin
                                                </span>
                                            ` : `
                                                <div style="display:flex; gap:6px;">
                                                    <button class="btn btn-outline btn-sm" style="color:#15803d; border-color:#86efac; padding:4px 10px;" onclick="openLeaveActionModal(${l.id}, 'approve', '${l.applicant_name}', '${l.leave_type}', '${l.start_date} to ${l.end_date}')">
                                                        ✓ Approve
                                                    </button>
                                                    <button class="btn btn-outline btn-sm" style="color:#b91c1c; border-color:#fca5a5; padding:4px 10px;" onclick="openLeaveActionModal(${l.id}, 'reject', '${l.applicant_name}', '${l.leave_type}', '${l.start_date} to ${l.end_date}')">
                                                        ✕ Reject
                                                    </button>
                                                </div>
                                            `}
                                        ` : `
                                            <span style="font-size:0.8rem; color:#64748b;">Decided (${l.approver_name || l.approver_role})</span>
                                        `}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Principal's Own Leave History -->
            <div class="card">
                <div class="card-header" style="justify-content:space-between; align-items:center;">
                    <div>
                        <span class="card-title">🏖️ My Principal Leave History</span>
                        <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Principal leave requests are approved directly by the Super Admin</p>
                    </div>
                    <button class="btn btn-primary btn-sm" onclick="openApplyLeaveModal('principal')">➕ Apply for Leave</button>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Category</th>
                                <th>Period</th>
                                <th>Duration</th>
                                <th>Reason</th>
                                <th>Super Admin Status</th>
                                <th>Notes</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${principalLeaves.length === 0 ? `
                                <tr>
                                    <td colspan="7" style="text-align:center; padding:30px; color:#64748b;">
                                        No principal leave requests submitted yet.
                                    </td>
                                </tr>
                            ` : principalLeaves.map(pl => `
                                <tr>
                                    <td><strong>${pl.leave_type}</strong></td>
                                    <td>${pl.start_date} to ${pl.end_date}</td>
                                    <td><span class="badge" style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:4px; font-weight:700;">${pl.days_count} Days</span></td>
                                    <td>${pl.reason}</td>
                                    <td>
                                        <span class="badge" style="padding:4px 10px; border-radius:6px; font-weight:700; ${
                                            pl.status === 'Approved' ? 'background:#dcfce7; color:#15803d;' :
                                            (pl.status === 'Rejected' ? 'background:#fee2e2; color:#b91c1c;' :
                                            'background:#fef3c7; color:#b45309;')
                                        }">
                                            ${pl.status}
                                        </span>
                                    </td>
                                    <td style="font-size:0.78rem; color:#64748b;">${pl.approver_notes || '—'}</td>
                                    <td>
                                        ${pl.status === 'Pending' ? `
                                            <button class="btn btn-outline btn-sm" style="color:#dc2626; border-color:#fca5a5; font-size:0.75rem; padding:4px 8px;" onclick="deleteLeaveRequest(${pl.id})">
                                                🗑️ Cancel / Delete
                                            </button>
                                        ` : (pl.status === 'Approved' ? `
                                            <span style="font-size:0.75rem; color:#64748b;"><i class="fas fa-lock"></i> Super Admin Only</span>
                                        ` : `
                                            <button class="btn btn-outline btn-sm" style="color:#64748b; border-color:#cbd5e1; font-size:0.75rem; padding:4px 8px;" onclick="deleteLeaveRequest(${pl.id})">
                                                🗑️ Remove
                                            </button>
                                        `)}
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    } else if (currentRole === 'super_admin') {
        const principalLeaves = leaves.filter(l => l.applicant_role === 'admin');
        const teacherLeaves = leaves.filter(l => l.applicant_role === 'teacher');
        const pendingTeacherCount = teacherLeaves.filter(l => l.status === 'Pending').length;
        const pendingPrincipalCount = principalLeaves.filter(l => l.status === 'Pending').length;

        contentHtml = `
            ${renderLeaveQuotaBanner(balances, userGender)}

            <!-- Direct Routing Indicator Banner -->
            ${principalOnLeave ? `
                <div style="background:#fef3c7; border:2px solid #f59e0b; color:#92400e; padding:18px 24px; border-radius:12px; margin-bottom:24px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:14px; box-shadow:0 4px 12px rgba(245, 158, 11, 0.15);">
                    <div style="display:flex; align-items:center; gap:16px;">
                        <span style="font-size:2.2rem;">⚡</span>
                        <div>
                            <div style="font-size:1.1rem; font-weight:800; color:#b45309;">
                                DIRECT ROUTING ACTIVE: Principal is currently ON LEAVE!
                            </div>
                            <div style="font-size:0.88rem; margin-top:3px; color:#92400e;">
                                All Teacher leave approval requests have been automatically routed directly to the Super Admin panel for your executive decision.
                            </div>
                        </div>
                    </div>
                    <div style="display:flex; align-items:center; gap:10px;">
                        <span class="badge" style="background:#b45309; color:white; padding:8px 14px; border-radius:6px; font-weight:700;">Direct Routing Active</span>
                        <button class="btn btn-outline btn-sm" style="background:white; color:#b45309; border-color:#f59e0b;" onclick="togglePrincipalDutyStatus(false)">
                            ↩️ Mark Principal As Resumed Duty
                        </button>
                    </div>
                </div>
            ` : `
                <div style="background:#eff6ff; border:1px solid #bfdbfe; color:#1e40af; padding:16px 20px; border-radius:12px; margin-bottom:24px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
                    <div style="display:flex; align-items:center; gap:12px;">
                        <span style="font-size:1.8rem;">ℹ️</span>
                        <div>
                            <strong style="font-size:0.95rem;">Normal Administrative Delegation Active</strong>
                            <div style="font-size:0.83rem; margin-top:2px;">
                                Principal (<code>GS_admin</code>) is currently on active duty and handling teacher leave approvals. Whenever the Principal is approved for leave, teacher approval requests will instantly route here to your panel.
                            </div>
                        </div>
                    </div>
                    <button class="btn btn-outline btn-sm" style="background:white; color:#1e40af; border-color:#93c5fd;" onclick="togglePrincipalDutyStatus(true)">
                        🧪 Simulate Principal On Leave
                    </button>
                </div>
            `}

            <!-- 1. Principal Leave Applications Card (Super Admin Approves) -->
            <div class="card" style="margin-bottom:24px;">
                <div class="card-header" style="justify-content:space-between; align-items:center;">
                    <div>
                        <span class="card-title">👑 Principal Leave Requests (Super Admin Approval Required)</span>
                        <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Only Super Admin has authority to approve Principal absence</p>
                    </div>
                    <span class="badge" style="background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:6px; font-weight:700;">${pendingPrincipalCount} Pending</span>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Principal</th>
                                <th>Category</th>
                                <th>Dates & Days</th>
                                <th>Reason</th>
                                <th>Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${principalLeaves.length === 0 ? `
                                <tr>
                                    <td colspan="6" style="text-align:center; padding:35px; color:#64748b;">
                                        No leave applications from the Principal yet.
                                    </td>
                                </tr>
                            ` : principalLeaves.map(pl => `
                                <tr>
                                    <td>
                                        <div style="font-weight:700; color:#0f172a;">${pl.applicant_name}</div>
                                        <div style="font-size:0.75rem; color:#64748b;">Principal (GS_admin)</div>
                                    </td>
                                    <td><span style="font-weight:600; color:#1e40af;">${pl.leave_type}</span></td>
                                    <td>
                                        <div><strong>${pl.start_date}</strong> to <strong>${pl.end_date}</strong></div>
                                        <span class="badge" style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:4px; font-size:0.72rem; font-weight:700;">${pl.days_count} Days</span>
                                    </td>
                                    <td style="max-width:240px;">${pl.reason}</td>
                                    <td>
                                        <span class="badge" style="padding:4px 10px; border-radius:6px; font-weight:700; ${
                                            pl.status === 'Approved' ? 'background:#dcfce7; color:#15803d; border:1px solid #bbf7d0;' :
                                            (pl.status === 'Rejected' ? 'background:#fee2e2; color:#b91c1c; border:1px solid #fecaca;' :
                                            'background:#fef3c7; color:#b45309; border:1px solid #fde68a;')
                                        }">
                                            ${pl.status}
                                        </span>
                                    </td>
                                    <td>
                                        <div style="display:flex; gap:6px; align-items:center; flex-wrap:wrap;">
                                            ${pl.status === 'Pending' ? `
                                                <button class="btn btn-outline btn-sm" style="color:#15803d; border-color:#86efac; padding:4px 8px; font-weight:700;" onclick="openLeaveActionModal(${pl.id}, 'approve', '${pl.applicant_name} (Principal)', '${pl.leave_type}', '${pl.start_date} to ${pl.end_date}')">
                                                    ✓ Approve
                                                </button>
                                                <button class="btn btn-outline btn-sm" style="color:#b91c1c; border-color:#fca5a5; padding:4px 8px; font-weight:700;" onclick="openLeaveActionModal(${pl.id}, 'reject', '${pl.applicant_name} (Principal)', '${pl.leave_type}', '${pl.start_date} to ${pl.end_date}')">
                                                    ✕ Reject
                                                </button>
                                            ` : `
                                                <span style="font-size:0.78rem; color:#64748b;">${pl.approver_role || 'Super Admin'}</span>
                                            `}
                                            <button class="btn btn-outline btn-sm" style="color:#dc2626; border-color:#fca5a5; padding:4px 8px; font-size:0.74rem; font-weight:700;" onclick="deleteLeaveRequest(${pl.id})">
                                                🗑️ Delete
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- 2. Teacher Leave Requests Card -->
            <div class="card">
                <div class="card-header" style="justify-content:space-between; align-items:center;">
                    <div>
                        <span class="card-title">👨‍🏫 Teacher Leave Approval Queue</span>
                        <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">
                            ${principalOnLeave ? '⚡ Direct approval active due to Principal leave of absence' : 'Standard faculty leave applications'}
                        </p>
                    </div>
                    <span class="badge" style="background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:6px; font-weight:700;">${pendingTeacherCount} Pending</span>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Teacher</th>
                                <th>Category</th>
                                <th>Dates & Days</th>
                                <th>Reason</th>
                                <th>Status</th>
                                <th>Super Admin Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${teacherLeaves.length === 0 ? `
                                <tr>
                                    <td colspan="6" style="text-align:center; padding:35px; color:#64748b;">
                                        No teacher leave requests recorded.
                                    </td>
                                </tr>
                            ` : teacherLeaves.map(tl => `
                                <tr>
                                    <td>
                                        <div style="font-weight:700; color:#0f172a;">${tl.applicant_name}</div>
                                        <div style="font-size:0.75rem; color:#64748b;"><code>${tl.applicant_username}</code> (${tl.applicant_gender || 'Staff'})</div>
                                    </td>
                                    <td><span style="font-weight:600; color:#1e40af;">${tl.leave_type}</span></td>
                                    <td>
                                        <div><strong>${tl.start_date}</strong> to <strong>${tl.end_date}</strong></div>
                                        <span class="badge" style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:4px; font-size:0.72rem; font-weight:700;">${tl.days_count} Days</span>
                                    </td>
                                    <td style="max-width:240px;">${tl.reason}</td>
                                    <td>
                                        <span class="badge" style="padding:4px 10px; border-radius:6px; font-weight:700; ${
                                            tl.status === 'Approved' ? 'background:#dcfce7; color:#15803d;' :
                                            (tl.status === 'Rejected' ? 'background:#fee2e2; color:#b91c1c;' :
                                            'background:#fef3c7; color:#b45309;')
                                        }">
                                            ${tl.status}
                                        </span>
                                    </td>
                                    <td>
                                        <div style="display:flex; gap:6px; align-items:center; flex-wrap:wrap;">
                                            ${tl.status === 'Pending' ? `
                                                <button class="btn btn-outline btn-sm" style="color:#15803d; border-color:#86efac; padding:4px 8px; font-weight:700;" onclick="openLeaveActionModal(${tl.id}, 'approve', '${tl.applicant_name}', '${tl.leave_type}', '${tl.start_date} to ${tl.end_date}')">
                                                    ✓ Approve
                                                </button>
                                                <button class="btn btn-outline btn-sm" style="color:#b91c1c; border-color:#fca5a5; padding:4px 8px; font-weight:700;" onclick="openLeaveActionModal(${tl.id}, 'reject', '${tl.applicant_name}', '${tl.leave_type}', '${tl.start_date} to ${tl.end_date}')">
                                                    ✕ Reject
                                                </button>
                                                ${principalOnLeave ? `<span style="font-size:0.72rem; color:#b45309; font-weight:700; background:#fef3c7; padding:2px 6px; border-radius:4px;">Direct</span>` : ''}
                                            ` : `
                                                <span style="font-size:0.78rem; color:#64748b;">${tl.approver_name || tl.approver_role}</span>
                                            `}
                                            <button class="btn btn-outline btn-sm" style="color:#dc2626; border-color:#fca5a5; padding:4px 8px; font-size:0.74rem; font-weight:700;" onclick="deleteLeaveRequest(${tl.id})">
                                                🗑️ Delete Leave
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Full Faculty Leave Balance & Quota Ledger for Super Admin -->
            <div style="margin-top:24px;">
                ${renderStaffLeaveLedger(allStaffBalances)}
            </div>
        `;
    } else if (currentRole === 'accountant') {
        const totalTeachers = allStaffBalances.length;
        const totalUsed = allStaffBalances.reduce((acc, s) => acc + (s.total_used || 0), 0);
        const totalRemaining = allStaffBalances.reduce((acc, s) => acc + (s.total_remaining || 0), 0);
        const teachersOnLeave = leaves.filter(l => l.status === 'Approved').length;

        contentHtml = `
            <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:10px; padding:16px 20px; margin-bottom:20px; color:#92400e; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:1.8rem;">💰</span>
                    <div>
                        <strong style="font-size:0.98rem;">Account Department Faculty Leave & Quota Ledger:</strong>
                        <div style="font-size:0.84rem; margin-top:2px;">
                            Full visibility into all teacher leave quotas (Used & Remaining). Approved leaves (CL, EL, Maternity, Paternity, CCL) are fully paid. Half Pay Leaves (HPL) and unexcused absences trigger automatic payroll deductions in the automated salary slip engine.
                        </div>
                    </div>
                </div>
                <button class="btn btn-primary btn-sm" style="background:#7c3aed; border-color:#7c3aed; font-weight:700;" onclick="showTab('payroll')">
                    💵 View Staff Payroll Slips
                </button>
            </div>

            <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); margin-bottom:20px;">
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Teaching Faculty</h5>
                        <h2>${totalTeachers}</h2>
                        <span style="font-size:0.75rem; color:#2563eb;">Monitored Staff</span>
                    </div>
                    <div class="metric-icon metric-blue">👨‍🏫</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Total Leaves Used</h5>
                        <h2>${totalUsed} Days</h2>
                        <span style="font-size:0.75rem; color:#b45309;">Year 2026 Quota</span>
                    </div>
                    <div class="metric-icon metric-amber">🏖️</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Total Quota Remaining</h5>
                        <h2>${totalRemaining} Days</h2>
                        <span style="font-size:0.75rem; color:#16a34a;">Available to Staff</span>
                    </div>
                    <div class="metric-icon metric-green">✓</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Approved Leave Grants</h5>
                        <h2>${teachersOnLeave}</h2>
                        <span style="font-size:0.75rem; color:#7c3aed;">Synchronized with Payroll</span>
                    </div>
                    <div class="metric-icon metric-purple">📜</div>
                </div>
            </div>

            <!-- Master Faculty Leave Quota Ledger Table -->
            ${renderStaffLeaveLedger(allStaffBalances)}

            <!-- Complete Faculty Leave Request History -->
            <div class="card" style="margin-top:24px;">
                <div class="card-header" style="justify-content:space-between; align-items:center;">
                    <div>
                        <span class="card-title">📜 Complete Faculty Leave Applications & Status Log</span>
                        <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Audit trail of all faculty leave requests across the school</p>
                    </div>
                    <span class="badge" style="background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:6px; font-weight:700;">${leaves.length} Applications</span>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Teacher</th>
                                <th>Leave Category</th>
                                <th>Dates</th>
                                <th>Days</th>
                                <th>Reason</th>
                                <th>Status</th>
                                <th>Approver</th>
                                <th>Applied Date</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${leaves.length === 0 ? `
                                <tr>
                                    <td colspan="8" style="text-align:center; padding:35px; color:#64748b;">No leave records found.</td>
                                </tr>
                            ` : leaves.map(l => `
                                <tr>
                                    <td>
                                        <strong>${l.applicant_name}</strong>
                                        <div style="font-size:0.74rem; color:#64748b;"><code>${l.applicant_username}</code> (${l.applicant_gender || 'Staff'})</div>
                                    </td>
                                    <td><span style="font-weight:600; color:#1e40af;">${l.leave_type}</span></td>
                                    <td>${l.start_date} to ${l.end_date}</td>
                                    <td><span class="badge" style="background:#e0f2fe; color:#0369a1; padding:2px 6px; border-radius:4px; font-weight:700;">${l.days_count}d</span></td>
                                    <td style="max-width:200px;">${l.reason}</td>
                                    <td>
                                        <span class="badge" style="padding:4px 8px; border-radius:6px; font-weight:700; ${
                                            l.status === 'Approved' ? 'background:#dcfce7; color:#15803d;' :
                                            (l.status === 'Rejected' ? 'background:#fee2e2; color:#b91c1c;' : 'background:#fef3c7; color:#b45309;')
                                        }">
                                            ${l.status === 'Approved' ? '✓ Approved' : (l.status === 'Rejected' ? '✕ Rejected' : '⏳ Pending')}
                                        </span>
                                    </td>
                                    <td style="font-size:0.8rem;">${l.approver_name || l.approver_role || '—'}</td>
                                    <td style="font-size:0.75rem; color:#64748b;">${l.created_at ? l.created_at.split(' ')[0] : '—'}</td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }

    document.getElementById('portal-tab-content').innerHTML = contentHtml;
}

function renderStaffLeaveLedger(allStaffBalances) {
    if (!allStaffBalances || allStaffBalances.length === 0) {
        return `<div class="card" style="padding:30px; text-align:center; color:#64748b;">No faculty members registered in system.</div>`;
    }

    return `
        <div class="card">
            <div class="card-header" style="justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <span class="card-title">📊 Faculty Leave Quota & Balance Ledger (Year 2026)</span>
                    <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">
                        Individual teacher quota breakdown: <strong>Casual (8d)</strong>, <strong>Earned (30d)</strong>, <strong>Half Pay (20d)</strong>, <strong>Maternity (180d F)</strong>, <strong>Paternity (15d M)</strong>, <strong>Child Care (730d)</strong>
                    </p>
                </div>
                <div style="display:flex; gap:8px;">
                    <input type="text" id="filter-staff-ledger" class="form-control" placeholder="🔍 Search teacher..." style="width:200px; padding:6px 12px; font-size:0.82rem;" onkeyup="filterStaffLeaveLedger()">
                </div>
            </div>
            <div class="card-body" style="padding:0; overflow-x:auto;">
                <table class="data-table" id="staff-leave-ledger-table">
                    <thead>
                        <tr style="background:#f1f5f9;">
                            <th style="min-width:180px;">Teacher & Details</th>
                            <th>Gender</th>
                            <th style="text-align:center;">Casual (CL)<br><small style="color:#64748b;">8d Allowed</small></th>
                            <th style="text-align:center;">Earned (EL)<br><small style="color:#64748b;">30d Allowed</small></th>
                            <th style="text-align:center;">Half Pay (HPL)<br><small style="color:#64748b;">20d Allowed</small></th>
                            <th style="text-align:center;">Maternity / Paternity<br><small style="color:#64748b;">180d F / 15d M</small></th>
                            <th style="text-align:center;">Child Care (CCL)<br><small style="color:#64748b;">730d Allowed</small></th>
                            <th style="text-align:center; background:#f8fafc;">Total Used</th>
                            <th style="text-align:center; background:#ecfdf5;">Total Remaining</th>
                            <th>Quota Health</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${allStaffBalances.map(s => {
                            const isFemale = s.gender === 'Female';
                            const matPatAllowed = isFemale ? s.maternity_total : s.paternity_total;
                            const matPatUsed = isFemale ? s.maternity_used : s.paternity_used;
                            const matPatRem = isFemale ? s.maternity_remaining : s.paternity_remaining;
                            const matPatLabel = isFemale ? 'Maternity' : 'Paternity';
                            const usagePct = s.total_allowed > 0 ? Math.round((s.total_used / s.total_allowed) * 100) : 0;

                            return `
                                <tr class="staff-ledger-row" data-name="${s.name.toLowerCase()} ${s.username.toLowerCase()}">
                                    <td>
                                        <div style="font-weight:700; color:#0f172a;">${s.name}</div>
                                        <div style="font-size:0.75rem; color:#64748b;">
                                            <code>${s.username}</code>
                                        </div>
                                    </td>
                                    <td>
                                        <span class="badge" style="background:${isFemale ? '#fce7f3; color:#9d174d;' : '#e0f2fe; color:#0369a1;'} font-weight:700; padding:2px 8px; border-radius:4px;">
                                            ${s.gender}
                                        </span>
                                    </td>
                                    <td style="text-align:center;">
                                        <div><strong style="color:#b45309;">${s.cl_used}</strong> / ${s.cl_total}</div>
                                        <div style="font-size:0.72rem; color:#15803d; font-weight:600;">${s.cl_remaining} left</div>
                                    </td>
                                    <td style="text-align:center;">
                                        <div><strong style="color:#b45309;">${s.el_used}</strong> / ${s.el_total}</div>
                                        <div style="font-size:0.72rem; color:#15803d; font-weight:600;">${s.el_remaining} left</div>
                                    </td>
                                    <td style="text-align:center;">
                                        <div><strong style="color:#b45309;">${s.hpl_used}</strong> / ${s.hpl_total}</div>
                                        <div style="font-size:0.72rem; color:#15803d; font-weight:600;">${s.hpl_remaining} left</div>
                                    </td>
                                    <td style="text-align:center;">
                                        <div><strong style="color:#b45309;">${matPatUsed}</strong> / ${matPatAllowed}</div>
                                        <div style="font-size:0.72rem; color:#15803d; font-weight:600;">${matPatRem} left (${matPatLabel})</div>
                                    </td>
                                    <td style="text-align:center;">
                                        <div><strong style="color:#b45309;">${s.ccl_used}</strong> / ${s.ccl_total}</div>
                                        <div style="font-size:0.72rem; color:#15803d; font-weight:600;">${s.ccl_remaining} left</div>
                                    </td>
                                    <td style="text-align:center; background:#f8fafc; font-weight:700; color:#b91c1c;">
                                        ${s.total_used} Days
                                    </td>
                                    <td style="text-align:center; background:#ecfdf5; font-weight:800; color:#15803d;">
                                        ${s.total_remaining} Days
                                    </td>
                                    <td>
                                        <span class="badge" style="background:${usagePct > 50 ? '#fee2e2; color:#b91c1c;' : '#dcfce7; color:#15803d;'} font-weight:700; padding:4px 8px; border-radius:6px;">
                                            ${usagePct}% Used (${100 - usagePct}% Left)
                                        </span>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

function filterStaffLeaveLedger() {
    const q = (document.getElementById('filter-staff-ledger') ? document.getElementById('filter-staff-ledger').value : '').toLowerCase();
    document.querySelectorAll('.staff-ledger-row').forEach(row => {
        const text = row.getAttribute('data-name') || '';
        row.style.display = text.includes(q) ? '' : 'none';
    });
}

// =====================================================================
// AUTOMATED PAYROLL & SALARY SLIPS SYSTEM
// =====================================================================
let currentPayrollMonth = 11;
let currentPayrollYear = 2026;

async function renderPayrollTab() {
    document.getElementById('portal-header-title').innerText = 'Staff Payroll & Salary Slips';
    document.getElementById('portal-header-desc').innerText = 'Automated salary slip generation based on attendance, paid leaves, HPL deductions, and executive bonuses';

    const isTeacher = currentRole === 'teacher';
    const teacherParam = isTeacher && currentUser ? `&teacher_id=${currentUser.id}` : '';
    const res = await fetch(`/api/payroll/slips?month=${currentPayrollMonth}&year=${currentPayrollYear}${teacherParam}`);
    const data = await res.json();
    const slips = data.slips || [];
    const bonuses = data.bonuses || [];
    const summary = data.summary || { total_gross: 0, total_net: 0, total_deductions: 0, total_bonus: 0 };
    const isOwner = currentUser && (currentUser.username === 'Owner(Directer)' || (currentUser.name && (currentUser.name.includes('Rajeev Sinha') || currentUser.name.includes('Director'))));

    const monthNames = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

    let accSlip = null;
    try {
        const accRes = await fetch(`/api/payroll/accountant_slip?month=${currentPayrollMonth}&year=${currentPayrollYear}`);
        const accData = await accRes.json();
        if (accData.success && accData.slip) {
            accSlip = accData.slip;
        }
    } catch (e) {
        console.error('Error fetching accountant slip', e);
    }

    let content = `
        <!-- Information Banner on Automated Payroll Rules -->
        <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:16px 20px; margin-bottom:20px; color:#1e40af; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:12px;">
            <div style="display:flex; align-items:center; gap:14px;">
                <span style="font-size:2rem;">⚡</span>
                <div>
                    <strong style="font-size:1rem;">Automated Mathematical Salary Engine (Policy Compliant)</strong>
                    <div style="font-size:0.84rem; margin-top:2px; color:#1d4ed8; line-height:1.4;">
                        Salary slips are <strong>automatically generated</strong> according to verified attendance, approved paid leaves (CL, EL, Maternity, Paternity, CCL), Half Pay Leave (HPL) deductions, and absent days. 
                        <strong>Account department cannot arbitrarily forge or modify figures.</strong> Only the <strong>Owner (Director)</strong> has the executive right to authorize special salary supplements (e.g. Diwali Bonus).
                    </div>
                </div>
            </div>
            ${isOwner ? `
                <button class="btn btn-primary" style="background:linear-gradient(135deg, #7c3aed, #4c1d95); border:none; font-weight:700; padding:10px 18px; display:inline-flex; align-items:center; gap:8px;" onclick="openSpecialBonusModal()">
                    <i class="fas fa-gift"></i> 🎁 Add Special Salary / Diwali Bonus (Owner Only)
                </button>
            ` : `
                <div style="font-size:0.8rem; color:#64748b; background:#fff; padding:6px 12px; border-radius:6px; border:1px solid #e2e8f0;">
                    <i class="fas fa-lock" style="color:#7c3aed;"></i> Special bonus (e.g. Diwali Bonus) restricted to <strong>Owner (Director)</strong>
                </div>
            `}
        </div>

        <!-- Month & Year Controls + Actions -->
        <div class="card" style="margin-bottom:20px;">
            <div class="card-body" style="padding:16px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px;">
                <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
                    <label style="font-weight:700; color:#0f172a; font-size:0.9rem;">Payroll Period:</label>
                    <select id="payroll-month-select" class="form-control" style="width:160px;" onchange="changePayrollPeriod(this.value, null)">
                        ${[1,2,3,4,5,6,7,8,9,10,11,12].map(m => `
                            <option value="${m}" ${m === currentPayrollMonth ? 'selected' : ''}>${monthNames[m]} ${currentPayrollYear}</option>
                        `).join('')}
                    </select>
                    <span class="badge" style="background:#e0f2fe; color:#0369a1; padding:6px 12px; border-radius:6px; font-weight:700;">
                        ${monthNames[currentPayrollMonth]} ${currentPayrollYear} Pay Cycle
                    </span>
                </div>

                <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
                    ${!isTeacher ? `
                        <button class="btn btn-primary" style="font-weight:700; display:inline-flex; align-items:center; gap:8px;" onclick="triggerAutoGeneratePayroll(${currentPayrollMonth}, ${currentPayrollYear})">
                            <i class="fas fa-sync-alt"></i> ⚡ Auto-Generate Monthly Payroll
                        </button>
                    ` : ''}
                </div>
            </div>
        </div>

        <!-- Dedicated Accountant Personal Payslip View (Director Sanctioned) -->
        ${currentRole === 'accountant' ? `
            <div class="card" style="margin-bottom:20px; border-left:4px solid #1e3a8a;">
                <div class="card-header" style="justify-content:space-between; align-items:center; background:#f8fafc;">
                    <div>
                        <span class="card-title" style="color:#1e3a8a;"><i class="fas fa-file-invoice-dollar"></i> My Personal Salary Payslip (Sanctioned by Director)</span>
                        <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Institutional Rule: Account department cannot generate their own salary; issued exclusively by Owner (Director) Rajeev Sinha</p>
                    </div>
                    ${accSlip ? `
                        <span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700; padding:6px 12px; border-radius:6px;">
                            ✓ Official Sanction Confirmed
                        </span>
                    ` : `
                        <span class="badge" style="background:#fef3c7; color:#d97706; font-weight:700; padding:6px 12px; border-radius:6px;">
                            ⏳ Pending Director Sanction
                        </span>
                    `}
                </div>
                <div class="card-body">
                    ${accSlip ? `
                        <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap:16px; align-items:center;">
                            <div>
                                <span style="font-size:0.75rem; color:#64748b;">Slip Number:</span>
                                <div style="font-weight:700; font-family:monospace; color:#1e3a8a;">${accSlip.slip_no}</div>
                            </div>
                            <div>
                                <span style="font-size:0.75rem; color:#64748b;">Gross Salary:</span>
                                <div style="font-weight:800; font-size:1.1rem; color:#0f172a;">₹${(accSlip.gross_salary || 0).toLocaleString()}</div>
                            </div>
                            <div>
                                <span style="font-size:0.75rem; color:#64748b;">Director Special Bonus:</span>
                                <div style="font-weight:700; color:#7c3aed;">₹${(accSlip.special_bonus || 0).toLocaleString()}</div>
                            </div>
                            <div>
                                <span style="font-size:0.75rem; color:#64748b;">Net Payout:</span>
                                <div style="font-weight:800; font-size:1.15rem; color:#16a34a;">₹${(accSlip.net_salary || 0).toLocaleString()}</div>
                            </div>
                            <div>
                                <button class="btn btn-primary" onclick="viewSalarySlip(${accSlip.id})" style="font-weight:700; display:inline-flex; align-items:center; gap:6px;">
                                    <i class="fas fa-print"></i> 📜 View & Print My Slip
                                </button>
                            </div>
                        </div>
                    ` : `
                        <div style="padding:10px 0; color:#475569; font-size:0.86rem;">
                            ⚠️ <strong>Your salary slip for ${monthNames[currentPayrollMonth]} ${currentPayrollYear} has not been issued yet.</strong><br>
                            By school policy, Accountant payslips must be sanctioned directly by <strong>Owner (Director) Rajeev Sinha</strong>.
                        </div>
                    `}
                </div>
            </div>
        ` : ''}

        <!-- Director Executive Accountant Sanction Desk -->
        ${isOwner ? `
            <div class="card" style="margin-bottom:20px; border-left:4px solid #7c3aed;">
                <div class="card-header" style="justify-content:space-between; align-items:center; background:#faf5ff;">
                    <div>
                        <span class="card-title" style="color:#6b21a8;"><i class="fas fa-user-shield"></i> Director Executive Authority: Sanction Accountant Salary Payslip</span>
                        <p style="font-size:0.78rem; color:#7e22ce; margin-top:2px;">Only the Director can issue official compensation and bonuses to the Account Department</p>
                    </div>
                    <button class="btn btn-primary btn-sm" style="background:#7c3aed; border:none; font-weight:700; display:inline-flex; align-items:center; gap:6px;" onclick="openModal('modal-issue-accountant-slip')">
                        ✍️ Sanction / Update Accountant Payslip
                    </button>
                </div>
                <div class="card-body">
                    <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                        <div>
                            <strong>Accountant: Jude Bello (Head Bursar)</strong>
                            <div style="font-size:0.82rem; color:#64748b; margin-top:2px;">
                                ${accSlip ? `Status for ${monthNames[currentPayrollMonth]} ${currentPayrollYear}: <strong style="color:#16a34a;">Sanctioned (Net ₹${(accSlip.net_salary || 0).toLocaleString()})</strong> - Slip <code>${accSlip.slip_no}</code>` : `<span style="color:#d97706;">Pending Sanction for ${monthNames[currentPayrollMonth]} ${currentPayrollYear}</span>`}
                            </div>
                        </div>
                        ${accSlip ? `
                            <button class="btn btn-outline btn-sm" onclick="viewSalarySlip(${accSlip.id})">
                                📜 View Issued Accountant Slip
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>
        ` : ''}

        <!-- Active Special Bonuses Callout if Present -->
        ${bonuses.length > 0 ? `
            <div style="background:#faf5ff; border:1px solid #e9d5ff; border-radius:10px; padding:14px 18px; margin-bottom:20px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px;">
                <div style="display:flex; align-items:center; gap:10px;">
                    <span style="font-size:1.6rem;">🎁</span>
                    <div>
                        <strong style="color:#6b21a8; font-size:0.95rem;">Active Owner Special Bonus Active for this Period:</strong>
                        <div style="font-size:0.82rem; color:#7e22ce;">
                            ${bonuses.map(b => `<strong>${b.title} (₹${b.amount.toLocaleString()})</strong> sanctioned by <em>${b.granted_by}</em>`).join(' | ')}
                        </div>
                    </div>
                </div>
                <span class="badge" style="background:#7c3aed; color:#fff; font-weight:700; padding:6px 12px; border-radius:6px;">
                    Executive Sanction Active
                </span>
            </div>
        ` : ''}

        <!-- Metrics Overview -->
        <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); margin-bottom:20px;">
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Total Gross Payroll</h5>
                    <h2>₹${(summary.total_gross || 0).toLocaleString()}</h2>
                    <span style="font-size:0.75rem; color:#2563eb;">Base + Allowances + Bonus</span>
                </div>
                <div class="metric-icon metric-blue">💵</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Total Net Payout</h5>
                    <h2>₹${(summary.total_net || 0).toLocaleString()}</h2>
                    <span style="font-size:0.75rem; color:#16a34a;">Final Disbursed</span>
                </div>
                <div class="metric-icon metric-green">✓</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Total Deductions</h5>
                    <h2>₹${(summary.total_deductions || 0).toLocaleString()}</h2>
                    <span style="font-size:0.75rem; color:#b91c1c;">Leave Ded + PF + Tax</span>
                </div>
                <div class="metric-icon metric-red">🔻</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Owner Special Bonuses</h5>
                    <h2>₹${(summary.total_bonus || 0).toLocaleString()}</h2>
                    <span style="font-size:0.75rem; color:#7c3aed;">Diwali & Special Incentives</span>
                </div>
                <div class="metric-icon metric-purple">🎁</div>
            </div>
        </div>

        <!-- Salary Slips Table -->
        <div class="card">
            <div class="card-header" style="justify-content:space-between; align-items:center;">
                <div>
                    <span class="card-title">📜 Verified Faculty Salary Slips (${monthNames[currentPayrollMonth]} ${currentPayrollYear})</span>
                    <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Individual payslip breakdown computed from attendance, approved leaves, and bonuses</p>
                </div>
                <span class="badge" style="background:#e0f2fe; color:#0369a1; padding:4px 10px; border-radius:6px; font-weight:700;">${slips.length} Slips Generated</span>
            </div>
            <div class="card-body" style="padding:0; overflow-x:auto;">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Slip #</th>
                            <th>Faculty Member</th>
                            <th>Base Salary</th>
                            <th>Attendance Breakdown</th>
                            <th>Allowances</th>
                            <th>Owner Bonus</th>
                            <th>Deductions</th>
                            <th>Gross Pay</th>
                            <th>Net Pay</th>
                            <th>Action</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${slips.length === 0 ? `
                            <tr>
                                <td colspan="10" style="text-align:center; padding:40px; color:#64748b;">
                                    No salary slips generated for ${monthNames[currentPayrollMonth]} ${currentPayrollYear} yet.
                                    <div style="margin-top:10px;">
                                        <button class="btn btn-primary btn-sm" onclick="triggerAutoGeneratePayroll(${currentPayrollMonth}, ${currentPayrollYear})">⚡ Auto-Generate Now</button>
                                    </div>
                                </td>
                            </tr>
                        ` : slips.map(s => `
                            <tr>
                                <td><code style="font-weight:700; color:#1e3a8a;">${s.slip_no}</code></td>
                                <td>
                                    <div style="font-weight:700; color:#0f172a;">${s.teacher_name}</div>
                                    <div style="font-size:0.74rem; color:#64748b;">${s.designation || 'Faculty'}</div>
                                </td>
                                <td><strong>₹${(s.base_salary || 0).toLocaleString()}</strong></td>
                                <td>
                                    <div style="font-size:0.78rem;">
                                        <span style="color:#16a34a; font-weight:700;">Pres: ${s.present_days}d</span> | 
                                        <span style="color:#2563eb; font-weight:700;">Paid Lv: ${s.paid_leave_days}d</span>
                                    </div>
                                    <div style="font-size:0.72rem; color:#64748b;">
                                        HPL: ${s.hpl_days}d | Absent: ${s.absent_days}d
                                    </div>
                                </td>
                                <td>
                                    <div style="font-size:0.78rem; color:#0f172a;">
                                        +₹${((s.hra || 0) + (s.da || 0) + (s.transport_allowance || 0)).toLocaleString()}
                                    </div>
                                    <div style="font-size:0.7rem; color:#64748b;">HRA+DA+Trans</div>
                                </td>
                                <td>
                                    ${s.special_bonus > 0 ? `
                                        <span class="badge" style="background:#faf5ff; color:#7c3aed; border:1px solid #d8b4fe; font-weight:700; padding:3px 6px; border-radius:4px;">
                                            +₹${s.special_bonus.toLocaleString()}
                                        </span>
                                        <div style="font-size:0.68rem; color:#6b21a8; font-weight:600; margin-top:2px;">${s.special_bonus_title || 'Owner Bonus'}</div>
                                    ` : '<span style="color:#94a3b8; font-size:0.8rem;">—</span>'}
                                </td>
                                <td>
                                    <div style="font-size:0.78rem; color:#b91c1c; font-weight:600;">
                                        -₹${((s.leave_deduction || 0) + (s.pf_deduction || 0) + (s.tax_deduction || 0)).toLocaleString()}
                                    </div>
                                    <div style="font-size:0.7rem; color:#64748b;">
                                        ${s.leave_deduction > 0 ? `Lv Ded: ₹${s.leave_deduction.toLocaleString()} | ` : ''}PF+Tax: ₹${((s.pf_deduction || 0) + (s.tax_deduction || 0)).toLocaleString()}
                                    </div>
                                </td>
                                <td><strong>₹${(s.gross_salary || 0).toLocaleString()}</strong></td>
                                <td>
                                    <strong style="color:#15803d; font-size:1.05rem;">₹${(s.net_salary || 0).toLocaleString()}</strong>
                                </td>
                                <td>
                                    <button class="btn btn-outline btn-sm" style="font-weight:700; color:#1e3a8a; border-color:#93c5fd; padding:5px 10px;" onclick="viewSalarySlipDetails('${s.slip_no}')">
                                        🖨️ View & Print
                                    </button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    document.getElementById('portal-tab-content').innerHTML = content;
}

function changePayrollPeriod(month, year) {
    if (month) currentPayrollMonth = parseInt(month);
    if (year) currentPayrollYear = parseInt(year);
    renderPayrollTab();
}

async function triggerAutoGeneratePayroll(month, year) {
    try {
        const res = await fetch('/api/payroll/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                month: month || currentPayrollMonth,
                year: year || currentPayrollYear,
                user_id: currentUser ? currentUser.id : null,
                user_name: currentUser ? currentUser.name : 'Account Department'
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✓ ${data.message}`);
            renderPayrollTab();
        } else {
            alert(`Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Could not auto-generate payroll: ' + err.message);
    }
}

function openSpecialBonusModal() {
    // STRICT CHECK: Only Owner can access!
    if (!currentUser || (currentUser.username !== 'Owner(Directer)' && !(currentUser.name && (currentUser.name.includes('Rajeev Sinha') || currentUser.name.includes('Director'))))) {
        alert('Access Denied: Only Owner (Director) has the executive right to grant special salary bonuses (e.g. Diwali Bonus).');
        return;
    }
    const modal = document.getElementById('modal-add-special-bonus');
    if (modal) modal.style.display = 'flex';
}

async function submitAddSpecialBonus(e) {
    e.preventDefault();
    if (!currentUser || (currentUser.username !== 'Owner(Directer)' && !(currentUser.name && (currentUser.name.includes('Rajeev Sinha') || currentUser.name.includes('Director'))))) {
        alert('Access Denied: Only Owner (Director) can authorize special salary bonuses.');
        return;
    }

    const payload = {
        user_id: currentUser.id,
        username: currentUser.username,
        title: document.getElementById('special-bonus-title').value.trim(),
        amount: parseFloat(document.getElementById('special-bonus-amount').value),
        month: parseInt(document.getElementById('special-bonus-month').value),
        year: parseInt(document.getElementById('special-bonus-year').value),
        teacher_id: document.getElementById('special-bonus-teacher').value,
        notes: document.getElementById('special-bonus-notes').value.trim()
    };

    try {
        const res = await fetch('/api/payroll/special_bonus', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✓ ${data.message}`);
            closeModal('modal-add-special-bonus');
            currentPayrollMonth = payload.month;
            currentPayrollYear = payload.year;
            renderPayrollTab();
        } else {
            alert(`Error: ${data.error || 'Failed to authorize bonus.'}`);
        }
    } catch (err) {
        alert('Could not authorize special bonus: ' + err.message);
    }
}

async function viewSalarySlipDetails(slipNo) {
    try {
        const res = await fetch(`/api/payroll/slips?month=${currentPayrollMonth}&year=${currentPayrollYear}`);
        const data = await res.json();
        const slip = (data.slips || []).find(s => s.slip_no === slipNo);
        if (!slip) {
            alert('Salary slip record not found.');
            return;
        }

        const monthNames = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
        const totalEarnings = slip.gross_salary;
        const totalDeductions = slip.leave_deduction + slip.pf_deduction + slip.tax_deduction;

        const html = `
            <div style="font-family:'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color:#0f172a; padding:10px;">
                <!-- Header -->
                <div style="text-align:center; border-bottom:2px solid #1e3a8a; padding-bottom:14px; margin-bottom:16px;">
                    <div style="font-size:1.6rem; font-weight:900; color:#1e3a8a; letter-spacing:0.5px;">GREENLAND SCHOOL</div>
                    <div style="font-size:0.82rem; color:#475569; margin-top:2px;">
                        Affiliated to CBSE, New Delhi | Affiliation No. 2132450 | School Code: 71201
                    </div>
                    <div style="font-size:0.82rem; color:#475569;">
                        Post Box No. 12, Main Road, Renukoot, Sonbhadra, Uttar Pradesh - 231217
                    </div>
                    <div style="display:inline-block; margin-top:8px; background:#1e3a8a; color:#fff; font-weight:800; font-size:0.86rem; padding:4px 16px; border-radius:4px; letter-spacing:0.5px;">
                        OFFICIAL FACULTY SALARY PAYSLIP - ${monthNames[slip.month].toUpperCase()} ${slip.year}
                    </div>
                </div>

                <!-- Faculty Meta Information Grid -->
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:12px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:14px 16px; margin-bottom:18px; font-size:0.86rem;">
                    <div><strong>Faculty Name:</strong> ${slip.teacher_name}</div>
                    <div><strong>Payslip Ref No:</strong> <code style="color:#1e3a8a; font-weight:700;">${slip.slip_no}</code></div>
                    <div><strong>Designation:</strong> ${slip.designation || 'Teaching Faculty'}</div>
                    <div><strong>Bank:</strong> State Bank of India (Renukoot)</div>
                    <div><strong>Pay Period:</strong> 01/${String(slip.month).padStart(2,'0')}/${slip.year} to 30/${String(slip.month).padStart(2,'0')}/${slip.year}</div>
                    <div><strong>Account No:</strong> 34892019482 (Direct Credit)</div>
                    <div><strong>Total Working Days:</strong> ${slip.total_days} Days</div>
                    <div><strong>Days Present:</strong> ${slip.present_days} Days</div>
                    <div><strong>Approved Paid Leaves:</strong> ${slip.paid_leave_days} Days (CL/EL/Maternity/Paternity/CCL)</div>
                    <div><strong>Half Pay / Absent Days:</strong> HPL: ${slip.hpl_days}d | Absent: ${slip.absent_days}d</div>
                </div>

                <!-- Earnings & Deductions Tables -->
                <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:18px;">
                    <!-- Earnings -->
                    <div style="border:1px solid #cbd5e1; border-radius:6px; overflow:hidden;">
                        <div style="background:#1e3a8a; color:#fff; font-weight:700; padding:8px 12px; font-size:0.88rem;">
                            EARNINGS (₹)
                        </div>
                        <table style="width:100%; font-size:0.85rem; border-collapse:collapse;">
                            <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 12px;">Basic Pay</td><td style="text-align:right; padding:8px 12px; font-weight:600;">₹${slip.base_salary.toLocaleString()}</td></tr>
                            <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 12px;">House Rent Allowance (HRA)</td><td style="text-align:right; padding:8px 12px; font-weight:600;">₹${slip.hra.toLocaleString()}</td></tr>
                            <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 12px;">Dearness Allowance (DA)</td><td style="text-align:right; padding:8px 12px; font-weight:600;">₹${slip.da.toLocaleString()}</td></tr>
                            <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 12px;">Transport Allowance</td><td style="text-align:right; padding:8px 12px; font-weight:600;">₹${slip.transport_allowance.toLocaleString()}</td></tr>
                            ${slip.special_bonus > 0 ? `
                                <tr style="background:#f5f3ff; color:#6b21a8; font-weight:700;">
                                    <td style="padding:8px 12px;">🎁 ${slip.special_bonus_title || 'Owner Diwali Bonus'}</td>
                                    <td style="text-align:right; padding:8px 12px;">+₹${slip.special_bonus.toLocaleString()}</td>
                                </tr>
                            ` : ''}
                            <tr style="background:#f8fafc; font-weight:800; border-top:2px solid #cbd5e1;">
                                <td style="padding:10px 12px;">TOTAL GROSS EARNINGS</td>
                                <td style="text-align:right; padding:10px 12px; color:#1e3a8a;">₹${totalEarnings.toLocaleString()}</td>
                            </tr>
                        </table>
                    </div>

                    <!-- Deductions -->
                    <div style="border:1px solid #cbd5e1; border-radius:6px; overflow:hidden;">
                        <div style="background:#b91c1c; color:#fff; font-weight:700; padding:8px 12px; font-size:0.88rem;">
                            DEDUCTIONS (₹)
                        </div>
                        <table style="width:100%; font-size:0.85rem; border-collapse:collapse;">
                            <tr style="border-bottom:1px solid #f1f5f9;">
                                <td style="padding:8px 12px;">Leave Deductions (HPL/Absent)</td>
                                <td style="text-align:right; padding:8px 12px; font-weight:600; color:${slip.leave_deduction > 0 ? '#b91c1c' : '#0f172a'};">
                                    ₹${slip.leave_deduction.toLocaleString()}
                                </td>
                            </tr>
                            <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 12px;">Employees' Provident Fund (EPF)</td><td style="text-align:right; padding:8px 12px; font-weight:600;">₹${slip.pf_deduction.toLocaleString()}</td></tr>
                            <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 12px;">Professional Tax (PT)</td><td style="text-align:right; padding:8px 12px; font-weight:600;">₹${slip.tax_deduction.toLocaleString()}</td></tr>
                            <tr style="border-bottom:1px solid #f1f5f9;"><td style="padding:8px 12px; color:#64748b;">Income Tax (TDS)</td><td style="text-align:right; padding:8px 12px; color:#64748b;">₹0.00</td></tr>
                            <tr style="background:#f8fafc; font-weight:800; border-top:2px solid #cbd5e1;">
                                <td style="padding:10px 12px;">TOTAL DEDUCTIONS</td>
                                <td style="text-align:right; padding:10px 12px; color:#b91c1c;">₹${totalDeductions.toLocaleString()}</td>
                            </tr>
                        </table>
                    </div>
                </div>

                <!-- Net Pay Box -->
                <div style="background:#ecfdf5; border:2px solid #10b981; border-radius:8px; padding:14px 20px; display:flex; justify-content:space-between; align-items:center; margin-bottom:20px;">
                    <div>
                        <div style="font-size:0.82rem; color:#065f46; font-weight:700; text-transform:uppercase; letter-spacing:0.5px;">Net Salary Disbursed (Take-Home)</div>
                        <div style="font-size:0.82rem; color:#047857; margin-top:2px; font-style:italic;">Transferred electronically to employee bank account</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:1.6rem; font-weight:900; color:#047857;">₹${slip.net_salary.toLocaleString()}</div>
                    </div>
                </div>

                <!-- Signatures -->
                <div style="display:flex; justify-content:space-between; align-items:flex-end; padding-top:24px; border-top:1px dashed #cbd5e1; font-size:0.82rem; color:#475569;">
                    <div style="text-align:center;">
                        <div style="font-family:'Courier New', monospace; font-weight:bold; color:#1e3a8a;">[DIGITALLY VERIFIED]</div>
                        <div style="border-top:1px solid #475569; width:170px; margin-top:4px; padding-top:4px;">
                            <strong>Accountant Jude Bello</strong><br>
                            Accounts & Fee Dept
                        </div>
                    </div>
                    <div style="text-align:center;">
                        <div style="font-family:'Courier New', monospace; font-weight:bold; color:#7c3aed;">[EXECUTIVE SEAL]</div>
                        <div style="border-top:1px solid #475569; width:170px; margin-top:4px; padding-top:4px;">
                            <strong>Rajeev Sinha</strong><br>
                            Owner & Director
                        </div>
                    </div>
                </div>
            </div>
        `;

        document.getElementById('salary-slip-printable-content').innerHTML = html;
        const modal = document.getElementById('modal-view-salary-slip');
        if (modal) modal.style.display = 'flex';
    } catch (err) {
        alert('Could not load salary slip: ' + err.message);
    }
}

// =====================================================================
// ONLINE ADMISSION INQUIRIES & MULTI-CHANNEL APPROVALS
// =====================================================================
async function renderInquiriesTab() {
    if (!['super_admin', 'admin'].includes(currentRole)) {
        showTab('dashboard');
        return;
    }

    document.getElementById('portal-header-title').innerText = 'Online Admission Inquiries';
    document.getElementById('portal-header-desc').innerText = 'Public website inquiry records, applicant notification channels, and multi-role executive approval routing';

    try {
        const res = await fetch(`/api/admissions?role=${currentRole}&user_id=${currentUser.id}&username=${encodeURIComponent(currentUser.username)}`);
        if (res.status === 403) {
            document.getElementById('portal-tab-content').innerHTML = `
                <div class="card" style="padding:40px; text-align:center; color:#b91c1c;">
                    <h3>⛔ Access Denied</h3>
                    <p>Candidate online admission inquiries are strictly confidential and visible ONLY to Owner, Super Admin, or Principal.</p>
                </div>
            `;
            return;
        }
        const inquiries = await res.json();

        const pendingList = inquiries.filter(i => i.status === 'Pending');
        const approvedList = inquiries.filter(i => i.status === 'Approved');
        const bothCount = inquiries.filter(i => (i.notification_pref || 'both') === 'both').length;
        const phoneCount = inquiries.filter(i => i.notification_pref === 'phone').length;
        const emailCount = inquiries.filter(i => i.notification_pref === 'email').length;

        const html = `
            <!-- Policy Callout -->
            <div style="background:#f8fafc; border:1px solid #e2e8f0; border-left:4px solid #2563eb; border-radius:8px; padding:14px 18px; margin-bottom:20px; font-size:0.86rem; color:#1e293b; line-height:1.5;">
                <i class="fas fa-satellite-dish" style="color:#2563eb;"></i> <strong>Executive Approval & Instant Dispatch Rule:</strong> 
                Online inquiries submitted on the public website are visible strictly to the <strong>Owner (Director)</strong>, <strong>Superadmin</strong>, or <strong>Admin (Principal)</strong>. 
                If <strong>ANY ONE of them approves</strong> the inquiry, an official clearance message is immediately dispatched to the applicant's <strong>Phone Number</strong>, <strong>Email Address</strong>, or <strong>Both</strong> as chosen during submission.
            </div>

            <!-- Metrics -->
            <div class="metrics-grid" style="grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); margin-bottom:20px;">
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Total Inquiries</h5>
                        <h2>${inquiries.length}</h2>
                        <span style="font-size:0.75rem; color:#2563eb;">All Submissions</span>
                    </div>
                    <div class="metric-icon metric-blue">📩</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Pending Decision</h5>
                        <h2>${pendingList.length}</h2>
                        <span style="font-size:0.75rem; color:#f59e0b;">Awaiting Approval</span>
                    </div>
                    <div class="metric-icon metric-amber">⏳</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Approved & Dispatched</h5>
                        <h2>${approvedList.length}</h2>
                        <span style="font-size:0.75rem; color:#16a34a;">Notified to Candidates</span>
                    </div>
                    <div class="metric-icon metric-green">✓</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Dispatch Channels</h5>
                        <h2>${bothCount} Both</h2>
                        <span style="font-size:0.75rem; color:#7c3aed;">📱 ${phoneCount} Phone | ✉️ ${emailCount} Email</span>
                    </div>
                    <div class="metric-icon metric-purple">📡</div>
                </div>
            </div>

            <!-- Inquiries Ledger Table -->
            <div class="card">
                <div class="card-header" style="justify-content:space-between; align-items:center;">
                    <div>
                        <span class="card-title">Candidate Online Admission Inquiries</span>
                        <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Click "Approve & Dispatch" to sanction admission and transmit notification to preferred channel</p>
                    </div>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Ref #</th>
                                <th>Candidate & Parent</th>
                                <th>Class & Section</th>
                                <th>Contact Targets</th>
                                <th>Preferred Notification Channel</th>
                                <th>Status</th>
                                <th>Approver & Dispatch Proof</th>
                                <th>Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${inquiries.length === 0 ? `
                                <tr>
                                    <td colspan="8" style="text-align:center; padding:40px; color:#64748b;">No online inquiries submitted yet.</td>
                                </tr>
                            ` : inquiries.map(inq => {
                                const pref = inq.notification_pref || 'both';
                                return `
                                    <tr>
                                        <td><code style="font-weight:700; color:#1e3a8a;">${inq.ref_no}</code></td>
                                        <td>
                                            <div style="font-weight:700; color:#0f172a;">${inq.applicant_name}</div>
                                            <div style="font-size:0.75rem; color:#64748b;">Parent: ${inq.parent_name || 'Guardian'}</div>
                                            ${inq.previous_school ? `<div style="font-size:0.72rem; color:#94a3b8;">Prev: ${inq.previous_school}</div>` : ''}
                                        </td>
                                        <td>
                                            <div style="font-weight:600; color:#1e3a8a;">${inq.grade_applying}</div>
                                            <span class="badge" style="background:#f1f5f9; color:#475569; font-size:0.72rem; padding:2px 6px; border-radius:4px;">${inq.preferred_section || 'Section A'}</span>
                                        </td>
                                        <td>
                                            <div style="font-size:0.8rem;">📱 ${inq.phone}</div>
                                            <div style="font-size:0.8rem; color:#64748b;">✉️ ${inq.email}</div>
                                        </td>
                                        <td>
                                            ${pref === 'both' ? `
                                                <span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700; padding:4px 8px; border-radius:4px;">
                                                    📱✉️ Both Phone & Email
                                                </span>
                                            ` : (pref === 'phone' ? `
                                                <span class="badge" style="background:#e0f2fe; color:#0369a1; font-weight:700; padding:4px 8px; border-radius:4px;">
                                                    📱 Phone Number Only
                                                </span>
                                            ` : `
                                                <span class="badge" style="background:#f3e8ff; color:#7e22ce; font-weight:700; padding:4px 8px; border-radius:4px;">
                                                    ✉️ Email Address Only
                                                </span>
                                            `)}
                                        </td>
                                        <td>
                                            <span class="badge" style="padding:4px 10px; border-radius:6px; font-weight:700; ${
                                                inq.status === 'Approved' ? 'background:#dcfce7; color:#15803d;' :
                                                (inq.status === 'Declined' ? 'background:#fee2e2; color:#b91c1c;' : 'background:#fef3c7; color:#b45309;')
                                            }">
                                                ${inq.status === 'Approved' ? '✓ Approved' : (inq.status === 'Declined' ? '✕ Declined' : '⏳ Pending Review')}
                                            </span>
                                        </td>
                                        <td>
                                            ${inq.status === 'Approved' ? `
                                                <div style="font-weight:700; font-size:0.82rem; color:#15803d;">${inq.approved_by || 'Executive Office'}</div>
                                                <div style="font-size:0.72rem; color:#64748b; margin-top:2px;">${inq.approved_at || ''}</div>
                                                ${(pref === 'both' || pref === 'email') ? `
                                                    <div style="font-size:0.73rem; margin-top:4px;">
                                                        ✉️ <span class="badge" style="background:#e0f2fe; color:#0369a1; font-weight:600; font-size:0.72rem; padding:2px 6px;">
                                                            ${inq.email_dispatch_status ? inq.email_dispatch_status.split('(')[0] : 'Email Outbox'}
                                                        </span>
                                                    </div>
                                                ` : ''}
                                                ${(pref === 'both' || pref === 'phone') ? `
                                                    <div style="font-size:0.73rem; margin-top:3px;">
                                                        📱 <span class="badge" style="background:#dcfce7; color:#15803d; font-weight:600; font-size:0.72rem; padding:2px 6px;">
                                                            ${inq.sms_dispatch_status ? inq.sms_dispatch_status.split('(')[0] : 'WhatsApp / SMS Ready'}
                                                        </span>
                                                    </div>
                                                ` : ''}
                                            ` : '<span style="color:#94a3b8; font-size:0.8rem;">Awaiting Review</span>'}
                                        </td>
                                        <td>
                                            <div style="display:flex; gap:6px; align-items:center; flex-wrap:wrap;">
                                                ${inq.status === 'Pending' ? `
                                                    <button class="btn btn-primary btn-sm" style="font-weight:700; padding:5px 10px; font-size:0.76rem; background:#16a34a; border-color:#16a34a;" onclick="submitInquiryAction(${inq.id}, 'approve')">
                                                        ✓ Approve & Dispatch
                                                    </button>
                                                    <button class="btn btn-outline btn-sm" style="font-weight:700; padding:5px 8px; font-size:0.76rem; color:#b91c1c; border-color:#fca5a5;" onclick="submitInquiryAction(${inq.id}, 'decline')">
                                                        ✕ Decline
                                                    </button>
                                                ` : `
                                                    <button class="btn btn-primary btn-sm" style="font-weight:700; padding:5px 10px; font-size:0.76rem; background:#1e3a8a; border-color:#1e3a8a;" onclick="viewInquiryDispatchModal(${inq.id})">
                                                        📩 View Dispatch
                                                    </button>
                                                    ${inq.whatsapp_url ? `
                                                        <a href="${inq.whatsapp_url}" target="_blank" class="btn btn-sm" style="background:#25d366; color:#fff; font-weight:700; text-decoration:none; padding:4px 8px; font-size:0.74rem; border-radius:4px; display:inline-flex; align-items:center; gap:4px;" title="Send WhatsApp Message">
                                                            <i class="fab fa-whatsapp"></i> WA
                                                        </a>
                                                    ` : ''}
                                                    <a href="/api/admissions/outbox_preview?id=${inq.id}&type=email" target="_blank" class="btn btn-outline btn-sm" style="font-weight:700; padding:4px 8px; font-size:0.74rem;" title="View Official HTML Email Letterhead">
                                                        ✉️ HTML
                                                    </a>
                                                    <button class="btn btn-outline btn-sm" style="font-weight:700; padding:4px 8px; font-size:0.74rem;" onclick="resendInquiryNotification(${inq.id})" title="Re-dispatch notification via SMTP & SMS">
                                                        🔄 Resend
                                                    </button>
                                                `}
                                            </div>
                                        </td>
                                    </tr>
                                `;
                            }).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;
        document.getElementById('portal-tab-content').innerHTML = html;
    } catch (err) {
        alert('Could not load admissions inquiries: ' + err.message);
    }
}

async function submitInquiryAction(admissionId, action) {
    const actionLabel = action === 'approve' ? 'APPROVE and DISPATCH official notice' : 'DECLINE';
    if (!confirm(`Are you sure you want to ${actionLabel} for this admission inquiry?`)) return;

    try {
        const res = await fetch('/api/admissions/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                admission_id: admissionId,
                action: action,
                user_id: currentUser ? currentUser.id : null,
                username: currentUser ? currentUser.username : ''
            })
        });
        const data = await res.json();
        if (data.success) {
            if (action === 'approve') {
                alert(`✅ OFFICIAL CLEARANCE DISPATCHED!\n\n${data.message}\n\nDispatch Log:\n${data.dispatch_message}`);
            } else {
                alert(`✓ ${data.message}`);
            }
            renderInquiriesTab();
        } else {
            alert(`Error: ${data.error || 'Failed to complete action.'}`);
        }
    } catch (err) {
        alert('Could not submit inquiry action: ' + err.message);
    }
}

async function viewInquiryDispatchModal(admissionId) {
    try {
        const res = await fetch(`/api/admissions?role=${currentRole}&user_id=${currentUser.id}&username=${encodeURIComponent(currentUser.username)}`);
        const inquiries = await res.json();
        const inq = inquiries.find(i => i.id === admissionId);
        if (!inq) {
            alert('Inquiry record not found.');
            return;
        }

        const pref = inq.notification_pref || 'both';
        const channelLabel = pref === 'both' ? 'Both Phone Number & Email Address' : (pref === 'phone' ? 'Phone Number Only (SMS/WhatsApp)' : 'Email Address Only');
        const cleanDigits = (inq.phone || '').replace(/[^0-9]/g, '');
        const waLink = inq.whatsapp_url || `https://wa.me/${cleanDigits ? (cleanDigits.length === 10 ? '91' + cleanDigits : cleanDigits) : ''}`;
        const smsLink = inq.sms_link || `sms:${inq.phone || ''}`;

        const bodyHtml = `
            <div style="font-size:0.88rem; line-height:1.5;">
                <!-- Candidate Overview Card -->
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:14px; margin-bottom:16px;">
                    <div style="display:flex; justify-content:space-between; align-items:flex-start;">
                        <div>
                            <div style="font-weight:800; color:#0f172a; font-size:1.1rem;">${inq.applicant_name}</div>
                            <div style="color:#64748b; font-size:0.82rem; margin-top:2px;">
                                Ref: <code style="font-weight:700; color:#1e3a8a;">${inq.ref_no}</code> &nbsp;|&nbsp; 
                                Applying: <strong>${inq.grade_applying} (${inq.preferred_section || 'Section A'})</strong>
                            </div>
                            <div style="color:#64748b; font-size:0.82rem; margin-top:2px;">Parent / Guardian: <strong>${inq.parent_name || '—'}</strong></div>
                        </div>
                        <span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700; padding:5px 10px; font-size:0.8rem;">
                            ✓ Approved &amp; Dispatched
                        </span>
                    </div>
                    <div style="margin-top:10px; padding-top:10px; border-top:1px solid #e2e8f0; font-size:0.82rem; display:flex; gap:16px; flex-wrap:wrap;">
                        <span>📱 Phone: <strong>${inq.phone}</strong></span>
                        <span>✉️ Email: <strong>${inq.email}</strong></span>
                        <span>📡 Preferred: <strong>${channelLabel}</strong></span>
                    </div>
                </div>

                <!-- Channel 1: Email Dispatch Proof -->
                <div style="background:#f0fdf4; border:1px solid #bbf7d0; border-radius:8px; padding:14px; margin-bottom:14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-weight:700; color:#166534; display:flex; align-items:center; gap:6px;">
                            <i class="fas fa-envelope"></i> 1. Official Email Notice Delivery
                        </div>
                        <span class="badge" style="background:#15803d; color:#fff; font-size:0.75rem; font-weight:700;">
                            ${inq.email_dispatch_status || 'Dispatched to Outbox'}
                        </span>
                    </div>
                    <div style="font-size:0.82rem; color:#374151; margin-top:6px;">
                        Target Email: <strong>${inq.email || 'None'}</strong>
                    </div>
                    <div style="display:flex; gap:8px; margin-top:10px; flex-wrap:wrap;">
                        <a href="/api/admissions/outbox_preview?id=${inq.id}&type=email" target="_blank" class="btn btn-primary btn-sm" style="font-weight:700; padding:6px 12px; font-size:0.8rem; text-decoration:none; display:inline-flex; align-items:center; gap:6px;">
                            <i class="fas fa-file-invoice"></i> Open Official Email Letterhead
                        </a>
                        <a href="mailto:${inq.email}?subject=${encodeURIComponent('Official Admission Approval Notice — Greenland School')}&body=${encodeURIComponent('Dear Candidate, your admission inquiry has been approved. Please visit the portal or school administrative office to complete enrollment.')}" class="btn btn-outline btn-sm" style="font-weight:700; padding:6px 10px; font-size:0.8rem; text-decoration:none;">
                            ✉️ Send via Email Client (mailto:)
                        </a>
                    </div>
                    <div style="margin-top:12px; border:1px solid #cbd5e1; border-radius:6px; overflow:hidden;">
                        <iframe src="/api/admissions/outbox_preview?id=${inq.id}&type=email" style="width:100%; height:220px; border:none; background:#ffffff;"></iframe>
                    </div>
                </div>

                <!-- Channel 2: Phone & WhatsApp Dispatch Proof -->
                <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:8px; padding:14px; margin-bottom:14px;">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div style="font-weight:700; color:#1e40af; display:flex; align-items:center; gap:6px;">
                            <i class="fas fa-mobile-alt"></i> 2. Mobile Phone (SMS &amp; WhatsApp) Delivery
                        </div>
                        <span class="badge" style="background:#2563eb; color:#fff; font-size:0.75rem; font-weight:700;">
                            ${inq.sms_dispatch_status || 'WhatsApp / SMS Active'}
                        </span>
                    </div>
                    <div style="font-size:0.82rem; color:#374151; margin-top:6px;">
                        Target Phone: <strong>${inq.phone || 'None'}</strong>
                    </div>
                    <div style="display:flex; gap:8px; margin-top:10px; flex-wrap:wrap;">
                        <a href="${waLink}" target="_blank" class="btn btn-sm" style="background:#25d366; color:#fff; font-weight:700; text-decoration:none; padding:6px 12px; font-size:0.8rem; border-radius:4px; display:inline-flex; align-items:center; gap:6px;">
                            <i class="fab fa-whatsapp"></i> 📱 Open WhatsApp to Transmit Now
                        </a>
                        <a href="${smsLink}" class="btn btn-outline btn-sm" style="font-weight:700; padding:6px 10px; font-size:0.8rem; text-decoration:none;">
                            💬 Send Device SMS
                        </a>
                        <button type="button" class="btn btn-outline btn-sm" style="font-weight:700;" onclick="copySmsText(${inq.id})">
                            📋 Copy SMS Text
                        </button>
                    </div>
                    <div style="margin-top:10px; background:#ffffff; border:1px solid #d1d5db; border-radius:6px; padding:10px; font-size:0.8rem; font-family:monospace; color:#1f2937;" id="sms-text-box-${inq.id}">
                        GREENLAND SCHOOL ALERT: Admission inquiry ${inq.ref_no} for ${inq.applicant_name} (${inq.grade_applying} - ${inq.preferred_section || 'Section A'}) has been OFFICIALLY APPROVED by ${inq.approved_by || 'Executive Office'}. Please report to school administrative office or login to complete enrollment. Helpline: +91 761 700 5055.
                    </div>
                </div>

                <!-- Re-dispatch Notification Tool -->
                <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:14px; margin-bottom:12px;">
                    <div style="font-weight:700; color:#0f172a; margin-bottom:6px;">
                        <i class="fas fa-sync-alt"></i> Re-dispatch Notification
                    </div>
                    <div style="font-size:0.8rem; color:#64748b; margin-bottom:8px;">
                        Transmit the official admission clearance again via live SMTP email &amp; SMS gateway:
                    </div>
                    <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
                        <select id="resend-channel-${inq.id}" class="form-control" style="max-width:200px; font-size:0.82rem;">
                            <option value="both" ${pref === 'both' ? 'selected' : ''}>Both Phone &amp; Email</option>
                            <option value="email" ${pref === 'email' ? 'selected' : ''}>Email Address Only</option>
                            <option value="phone" ${pref === 'phone' ? 'selected' : ''}>Phone Number Only</option>
                        </select>
                        <button type="button" class="btn btn-primary btn-sm" style="font-weight:700;" onclick="resendInquiryNotification(${inq.id}, document.getElementById('resend-channel-${inq.id}').value)">
                            🔄 Transmit Notification Now
                        </button>
                    </div>
                </div>

                <!-- SMTP Tips Alert -->
                <div style="background:#fef3c7; border:1px solid #fde68a; border-radius:8px; padding:10px 14px; font-size:0.8rem; color:#92400e;">
                    💡 <strong>Live Delivery Tip:</strong> To deliver real emails directly into candidate Gmail inboxes, configure your Gmail SMTP settings (Server: <code>smtp.gmail.com</code>, Port: <code>587</code>, Gmail address &amp; 16-character Google App Password) in <a href="javascript:void(0)" onclick="closeModal('modal-view-inquiry'); showTab('settings');" style="color:#b45309; font-weight:700; text-decoration:underline;">System Settings</a>.
                </div>
            </div>
        `;

        document.getElementById('inq-modal-body').innerHTML = bodyHtml;
        const modal = document.getElementById('modal-view-inquiry');
        if (modal) modal.style.display = 'flex';
    } catch (err) {
        alert('Could not view inquiry details: ' + err.message);
    }
}

async function resendInquiryNotification(admissionId, channel = 'both') {
    if (!confirm('Re-dispatch official admission clearance notice to candidate?')) return;
    try {
        const res = await fetch('/api/admissions/resend', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                admission_id: admissionId,
                channel: channel,
                user_id: currentUser ? currentUser.id : null,
                username: currentUser ? currentUser.username : ''
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ NOTIFICATION RE-DISPATCHED!

${data.message}

Email Status: ${data.email_status}
Phone Status: ${data.sms_status}`);
            viewInquiryDispatchModal(admissionId);
            renderInquiriesTab();
        } else {
            alert(`Error: ${data.error || 'Failed to re-dispatch notification.'}`);
        }
    } catch (err) {
        alert('Could not re-dispatch notification: ' + err.message);
    }
}

function copySmsText(admissionId) {
    const el = document.getElementById(`sms-text-box-${admissionId}`);
    if (!el) return;
    const text = el.innerText.trim();
    navigator.clipboard.writeText(text).then(() => {
        alert('✓ SMS message copied to clipboard!');
    }).catch(() => {
        prompt('Copy the SMS message below:', text);
    });
}

function printElement(elementId) {
    const el = document.getElementById(elementId);
    if (!el) return;
    const printWindow = window.open('', '', 'height=750,width=900');
    printWindow.document.write('<html><head><title>Greenland School Official Salary Slip</title>');
    printWindow.document.write('<style>body{font-family:Segoe UI, sans-serif; margin:20px; color:#0f172a;} table{border-collapse:collapse; width:100%;} @media print {.no-print{display:none !important;}}</style>');
    printWindow.document.write('</head><body>');
    printWindow.document.write(el.innerHTML);
    printWindow.document.write('</body></html>');
    printWindow.document.close();
    printWindow.focus();
    setTimeout(() => {
        printWindow.print();
        printWindow.close();
    }, 400);
}

// =====================================================================
// TEACHER & LEAVE MODAL & SUBMISSION ACTIONS
// =====================================================================
function autoFillTeacherUsername(name) {
    if (!name) return;
    const parts = name.trim().split(/\s+/);
    const first = parts[0] || 'Teacher';
    const last = parts.length > 1 ? parts[parts.length - 1] : '';
    const slug = `${first}_${last}`.replace(/_+$/, '');
    const userField = document.getElementById('add-teacher-username');
    const emailField = document.getElementById('add-teacher-email');
    if (userField) userField.value = `GS_teacher_${slug}`;
    if (emailField) emailField.value = `gs_teacher_${slug.toLowerCase()}@greenlandschool.net`;
}

function populateClassSectionDropdowns(classes) {
    const addSelect = document.getElementById('add-teacher-section-assign');
    const assignSelect = document.getElementById('assign-section-select');
    if (!classes || !classes.length) return;

    let optionsHtml = '<option value="">-- No Class Teacher Assignment (General Faculty) --</option>';
    let assignOptionsHtml = '<option value="" disabled selected>-- Select Class and Section --</option><option value="0">❌ Unassign / Remove Current Class Teacher Role</option>';

    classes.forEach(c => {
        if (c.sections && c.sections.length) {
            optionsHtml += `<optgroup label="${c.name}">`;
            assignOptionsHtml += `<optgroup label="${c.name}">`;
            c.sections.forEach(s => {
                optionsHtml += `<option value="${s.id}">${c.name} - ${s.name}</option>`;
                assignOptionsHtml += `<option value="${s.id}">${c.name} - ${s.name}</option>`;
            });
            optionsHtml += `</optgroup>`;
            assignOptionsHtml += `</optgroup>`;
        }
    });

    if (addSelect) addSelect.innerHTML = optionsHtml;
    if (assignSelect) assignSelect.innerHTML = assignOptionsHtml;
}

function openAssignClassTeacherModal(teacherId = null) {
    const teacherSelect = document.getElementById('assign-teacher-select');
    if (teacherSelect && cachedTeachersList.length) {
        teacherSelect.innerHTML = '<option value="" disabled selected>-- Select Faculty Member --</option>' + 
            cachedTeachersList.map(t => `<option value="${t.id}" ${teacherId && teacherId == t.id ? 'selected' : ''}>${t.name} (${t.username})</option>`).join('');
    }
    if (teacherId) {
        handleAssignTeacherSelect(teacherId);
    } else {
        const hint = document.getElementById('assign-current-status-box');
        if (hint) hint.style.display = 'none';
    }
    openModal('modal-assign-class-teacher');
}

function handleAssignTeacherSelect(teacherId) {
    const teacher = cachedTeachersList.find(t => t.id == teacherId);
    const hint = document.getElementById('assign-current-status-box');
    const assignSelect = document.getElementById('assign-section-select');
    if (teacher) {
        if (assignSelect && teacher.assigned_section_id) {
            assignSelect.value = teacher.assigned_section_id;
        } else if (assignSelect) {
            assignSelect.value = "0";
        }
        if (hint) {
            hint.style.display = 'block';
            hint.innerHTML = `Current Assignment: <strong>${teacher.assigned_class ? teacher.assigned_class : 'None (General Faculty)'}</strong>`;
        }
    }
}

async function submitAddTeacher(e) {
    e.preventDefault();
    const payload = {
        name: document.getElementById('add-teacher-name').value.trim(),
        subject: document.getElementById('add-teacher-subject').value.trim(),
        qualification: document.getElementById('add-teacher-qualification').value.trim(),
        gender: document.getElementById('add-teacher-gender') ? document.getElementById('add-teacher-gender').value : 'Male',
        phone: document.getElementById('add-teacher-phone').value.trim(),
        email: document.getElementById('add-teacher-email').value.trim(),
        username: document.getElementById('add-teacher-username').value.trim(),
        password: document.getElementById('add-teacher-password').value.trim(),
        assign_section_id: document.getElementById('add-teacher-section-assign').value
    };

    try {
        const res = await fetch('/api/teachers/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`🎉 ${data.message}`);
            closeModal('modal-add-teacher');
            renderTeachersTab();
            loadInitialData();
            if (typeof loadLoginDirectory === 'function') loadLoginDirectory();
            if (typeof loadLoginDirectory === 'function') loadLoginDirectory();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (err) {
        alert('Could not add teacher');
    }
}

async function submitAssignClassTeacher(e) {
    e.preventDefault();
    const payload = {
        teacher_id: document.getElementById('assign-teacher-select').value,
        section_id: document.getElementById('assign-section-select').value
    };

    try {
        const res = await fetch('/api/teachers/assign_class_teacher', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`🎉 ${data.message}`);
            closeModal('modal-assign-class-teacher');
            renderTeachersTab();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (err) {
        alert('Could not update class assignment');
    }
}

function openEditTeacherModal(teacherId) {
    const teacher = cachedTeachersList.find(t => t.id == teacherId);
    if (!teacher) return;
    document.getElementById('edit-teacher-id').value = teacher.id;
    document.getElementById('edit-teacher-name').value = teacher.name;
    document.getElementById('edit-teacher-subject').value = teacher.subject || '';
    document.getElementById('edit-teacher-qualification').value = teacher.qualification || '';
    document.getElementById('edit-teacher-phone').value = teacher.phone || '';
    document.getElementById('edit-teacher-email').value = teacher.email || '';
    document.getElementById('edit-teacher-username').value = teacher.username || '';
    document.getElementById('edit-teacher-password').value = teacher.password || '';
    openModal('modal-edit-teacher');
}

async function submitEditTeacher(e) {
    e.preventDefault();
    const payload = {
        teacher_id: document.getElementById('edit-teacher-id').value,
        name: document.getElementById('edit-teacher-name').value.trim(),
        subject: document.getElementById('edit-teacher-subject').value.trim(),
        qualification: document.getElementById('edit-teacher-qualification').value.trim(),
        phone: document.getElementById('edit-teacher-phone').value.trim(),
        email: document.getElementById('edit-teacher-email').value.trim(),
        username: document.getElementById('edit-teacher-username').value.trim(),
        password: document.getElementById('edit-teacher-password').value.trim()
    };

    try {
        const res = await fetch('/api/teachers/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✓ ${data.message}`);
            closeModal('modal-edit-teacher');
            renderTeachersTab();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (err) {
        alert('Could not update teacher');
    }
}

async function confirmDeleteTeacher(teacherId, teacherName) {
    if (!confirm(`Are you sure you want to delete teacher "${teacherName}"?\n\nThis will remove their faculty assignment and login credentials.`)) {
        return;
    }
    try {
        const res = await fetch('/api/teachers/delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ teacher_id: teacherId })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✓ ${data.message}`);
            renderTeachersTab();
            loadInitialData();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (err) {
        alert('Could not delete teacher');
    }
}

function filterTeachersTable() {
    const q = document.getElementById('teacher-search-input').value.toLowerCase();
    const rows = document.querySelectorAll('#teachers-table tbody tr');
    rows.forEach(r => {
        r.style.display = r.innerText.toLowerCase().includes(q) ? '' : 'none';
    });
}

// LEAVE APPLICATION & DECISION HELPERS
function openApplyLeaveModal(role = 'teacher') {
    const titleEl = document.getElementById('leave-modal-title');
    const noticeEl = document.getElementById('leave-authority-notice');
    const typeSelect = document.getElementById('leave-type-select');
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('leave-start-date').value = today;
    document.getElementById('leave-end-date').value = today;
    calculateLeaveDays();

    const gender = (currentUser && currentUser.gender) ? currentUser.gender : 'Male';
    const isFemale = (gender || '').toLowerCase() === 'female';

    if (typeSelect) {
        typeSelect.innerHTML = `
            <option value="Casual Leave">Casual Leave (CL) - 8 days/yr</option>
            <option value="Earned Leave">Earned Leave (EL) - 30 days/yr (15d bi-annual)</option>
            <option value="Half Pay Leave">Half Pay Leave (HPL) - 20 days/yr (10d bi-annual)</option>
            ${isFemale ? `
                <option value="Maternity Leave">Maternity Leave - 180 days (Female Employees Only)</option>
            ` : `
                <option value="Paternity Leave">Paternity Leave - 15 days (Male Employees Only)</option>
            `}
            <option value="Child Care Leave">Child Care Leave (CCL) - 730 days career total</option>
        `;
    }

    if (role === 'principal' || currentRole === 'admin') {
        if (titleEl) titleEl.innerText = '🏖️ Principal Leave Application';
        if (noticeEl) noticeEl.innerHTML = '<strong>Executive Delegation:</strong> Principal leave applications are reviewed and approved directly by the <strong>Super Admin</strong>. While approved on leave, all teacher approvals will route automatically to Super Admin.';
    } else {
        if (titleEl) titleEl.innerText = '🏖️ Faculty Leave Application';
        if (noticeEl) noticeEl.innerHTML = `<strong>Leave Approval Routing:</strong> Your leave request will be submitted to the <strong>Principal</strong> for approval. If the Principal is currently on leave, it will route directly to <strong>Super Admin</strong>. (Gender: <strong>${gender}</strong>)`;
    }

    onLeaveCategoryChanged();
    openModal('modal-apply-leave');
}

function onLeaveCategoryChanged() {
    const sel = document.getElementById('leave-type-select');
    const callout = document.getElementById('leave-type-policy-callout');
    if (!sel || !callout) return;
    const val = sel.value;

    const policies = {
        'Casual Leave': '<strong>Casual Leave (CL):</strong> Set at 8 days per calendar year. It is an executive instruction rather than a recognized form of leave, meaning your pay does not stop, and it cannot be combined with regular leave types.',
        'Earned Leave': '<strong>Earned Leave (EL):</strong> Credited in advance twice a year (15 days each on January 1 and July 1). You can accumulate a maximum of 300 days in your career, which can also be encashed at the time of retirement.',
        'Half Pay Leave': '<strong>Half Pay Leave (HPL):</strong> Credited at a rate of 10 days every half-year. This is calculated based on completed service periods and can be commuted onto medical grounds.',
        'Maternity Leave': '<strong>Maternity Leave:</strong> Female employees are eligible for 180 days of Maternity Leave (up to 2 surviving children). Male employees cannot apply.',
        'Paternity Leave': '<strong>Paternity Leave:</strong> Male employees are allowed 15 days of Paternity Leave. Female employees cannot apply.',
        'Child Care Leave': '<strong>Child Care Leave (CCL):</strong> Available to female employees and single male employees for up to 730 days across their entire service to look after minor children.'
    };

    callout.innerHTML = policies[val] || 'Official leave policy applies to this category.';
}

function calculateLeaveDays() {
    const d1Str = document.getElementById('leave-start-date').value;
    const d2Str = document.getElementById('leave-end-date').value;
    const display = document.getElementById('leave-days-display');
    if (!d1Str || !d2Str || !display) return;
    const d1 = new Date(d1Str);
    const d2 = new Date(d2Str);
    const diffTime = d2 - d1;
    const diffDays = Math.max(1, Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1);
    display.innerText = `Duration: ${diffDays} Day${diffDays > 1 ? 's' : ''}`;
}

async function submitApplyLeave(e) {
    e.preventDefault();
    const payload = {
        user_id: currentUser ? currentUser.id : 3,
        leave_type: document.getElementById('leave-type-select').value,
        start_date: document.getElementById('leave-start-date').value,
        end_date: document.getElementById('leave-end-date').value,
        reason: document.getElementById('leave-reason').value.trim()
    };

    try {
        const res = await fetch('/api/leaves/apply', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✓ ${data.message}`);
            closeModal('modal-apply-leave');
            renderLeavesTab();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (err) {
        alert('Could not submit leave application');
    }
}

function openLeaveActionModal(leaveId, action, applicantName, leaveType, dates) {
    document.getElementById('action-leave-id').value = leaveId;
    document.getElementById('action-leave-type').value = action;
    const titleEl = document.getElementById('action-leave-title');
    const summaryEl = document.getElementById('action-leave-summary');
    const submitBtn = document.getElementById('btn-submit-leave-decision');

    const isApprove = action === 'approve';
    if (titleEl) titleEl.innerText = isApprove ? '✓ Approve Leave Request' : '✕ Reject Leave Request';
    if (submitBtn) {
        submitBtn.innerText = isApprove ? 'Confirm Approval' : 'Confirm Rejection';
        submitBtn.className = isApprove ? 'btn btn-primary' : 'btn btn-danger';
        submitBtn.style.background = isApprove ? '#16a34a' : '#dc2626';
    }
    if (summaryEl) {
        summaryEl.innerHTML = `
            <div>Applicant: <strong>${applicantName}</strong></div>
            <div>Category: <strong>${leaveType}</strong></div>
            <div>Dates: <strong>${dates}</strong></div>
            <div style="margin-top:4px; font-size:0.8rem; color:${isApprove ? '#15803d' : '#b91c1c'}; font-weight:700;">
                Action: ${isApprove ? 'Grant Official Leave' : 'Decline Leave Request'}
            </div>
        `;
    }
    openModal('modal-action-leave');
}

async function submitLeaveDecision(e) {
    e.preventDefault();
    const payload = {
        leave_id: document.getElementById('action-leave-id').value,
        action: document.getElementById('action-leave-type').value,
        approver_id: currentUser ? currentUser.id : 1,
        approver_role: currentRole,
        notes: document.getElementById('action-leave-notes').value.trim()
    };

    try {
        const res = await fetch('/api/leaves/action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✓ ${data.message}`);
            closeModal('modal-action-leave');
            renderLeavesTab();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (err) {
        alert('Could not record decision');
    }
}

async function togglePrincipalDutyStatus(setOnLeave) {
    try {
        const res = await fetch('/api/leaves/toggle_principal_status', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ on_leave: setOnLeave })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✓ ${data.message}`);
            renderLeavesTab();
        }
    } catch (err) {
        alert('Failed to update principal status');
    }
}

// ---------------------------------------------------------
// AADHAAR VALIDATION, PARENT SERVICES & FEE DELETION SYSTEM
// ---------------------------------------------------------

function escapeJs(str) {
    if (!str) return '';
    return String(str).replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

function checkAadhaarLength(input) {
    const clean = input.value.replace(/[^0-9]/g, '').slice(0, 12);
    input.value = clean;
    const counter = document.getElementById('aadhaar-counter');
    if (!counter) return;
    if (clean.length === 12) {
        counter.innerHTML = `<span style="color:#15803d; font-weight:700;">✓ 12 / 12 digits (Valid)</span>`;
        input.style.borderColor = '#16a34a';
    } else {
        counter.innerHTML = `<span style="color:#be123c;">${clean.length} / 12 digits</span>`;
        input.style.borderColor = '#fb7185';
    }
}

// Online Payment Gateway Handlers
let currentOnlinePayMode = 'qr';

function openOnlinePaymentModal(studentId, studentName, className, admNo, dueAmount) {
    document.getElementById('online-pay-student-id').value = studentId;
    document.getElementById('online-pay-student-name').innerText = studentName;
    document.getElementById('online-pay-student-class').innerText = `${className} (${admNo || 'Enrolled'})`;
    document.getElementById('online-pay-due-amount').innerText = `₹${(dueAmount || 0).toLocaleString()}`;
    document.getElementById('online-pay-amount').value = dueAmount || 15000;
    document.getElementById('online-pay-amount').max = dueAmount || 999999;
    document.getElementById('online-pay-utr').value = '';
    document.getElementById('online-pay-nb-ref').value = '';
    selectOnlinePayTab('qr');
    openModal('modal-pay-fee-online');
}

function selectOnlinePayTab(tab) {
    currentOnlinePayMode = tab;
    const qrBtn = document.getElementById('pay-tab-qr');
    const nbBtn = document.getElementById('pay-tab-nb');
    const qrPanel = document.getElementById('panel-pay-qr');
    const nbPanel = document.getElementById('panel-pay-nb');

    if (tab === 'qr') {
        qrBtn.style.border = '2px solid #16a34a';
        qrBtn.style.background = '#f0fdf4';
        qrBtn.style.color = '#16a34a';
        nbBtn.style.border = '2px solid #cbd5e1';
        nbBtn.style.background = '#f8fafc';
        nbBtn.style.color = '#64748b';
        qrPanel.style.display = 'block';
        nbPanel.style.display = 'none';
    } else {
        nbBtn.style.border = '2px solid #1e3a8a';
        nbBtn.style.background = '#eff6ff';
        nbBtn.style.color = '#1e3a8a';
        qrBtn.style.border = '2px solid #cbd5e1';
        qrBtn.style.background = '#f8fafc';
        qrBtn.style.color = '#64748b';
        qrPanel.style.display = 'none';
        nbPanel.style.display = 'block';
    }
}

async function submitOnlineFeePayment(e) {
    e.preventDefault();
    const studentId = parseInt(document.getElementById('online-pay-student-id').value);
    const amount = parseFloat(document.getElementById('online-pay-amount').value);
    const method = currentOnlinePayMode === 'qr' ? 'QR Code / UPI' : 'Net Banking';
    const bankName = currentOnlinePayMode === 'nb' ? document.getElementById('online-pay-bank').value : '';
    const txnRef = currentOnlinePayMode === 'qr' ? 
        document.getElementById('online-pay-utr').value.trim() : 
        document.getElementById('online-pay-nb-ref').value.trim();

    if (!txnRef) {
        alert(currentOnlinePayMode === 'qr' ? 'Please enter the 12-digit UPI Transaction / UTR number.' : 'Please enter the Net Banking Transaction Reference / UTR.');
        return;
    }

    const payload = {
        student_id: studentId,
        amount: amount,
        method: method,
        bank_name: bankName,
        transaction_ref: txnRef
    };

    try {
        const res = await fetch('/api/payments/pay_online', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`🎉 ${data.message}`);
            closeModal('modal-pay-fee-online');
            if (currentRole === 'parent') {
                renderParentDashboard();
            } else if (currentTab === 'payments') {
                renderPaymentsTab();
            }
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (err) {
        alert('Could not process online fee payment: ' + err.message);
    }
}

// Parent Edit Child Official Name (Aadhaar Verification)
function openParentEditNameModal(studentId, currentName) {
    document.getElementById('edit-child-student-id').value = studentId;
    document.getElementById('edit-child-current-name').value = currentName;
    document.getElementById('edit-child-new-name').value = currentName;
    document.getElementById('edit-child-aadhaar-verify').value = '';
    openModal('modal-parent-edit-student-name');
    document.getElementById('edit-child-aadhaar-verify').focus();
}

async function submitParentEditChildName(e) {
    e.preventDefault();
    const studentId = parseInt(document.getElementById('edit-child-student-id').value);
    const newName = document.getElementById('edit-child-new-name').value.trim();
    const aadhaarNo = document.getElementById('edit-child-aadhaar-verify').value.trim().replace(/[\s\-]/g, '');

    if (!aadhaarNo || aadhaarNo.length !== 12 || !/^\d{12}$/.test(aadhaarNo)) {
        alert('⚠️ Verification Error: Please enter the exact 12-digit Aadhaar number recorded for this child.');
        return;
    }

    const payload = {
        student_id: studentId,
        new_name: newName,
        aadhaar_no: aadhaarNo
    };

    try {
        const res = await fetch('/api/parent/update_child_name', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-parent-edit-student-name');
            if (currentRole === 'parent') {
                renderParentDashboard();
            } else {
                loadInitialData();
            }
        } else {
            alert(`❌ Aadhaar Verification Failed:\n${data.message}`);
        }
    } catch (err) {
        alert('Verification request failed: ' + err.message);
    }
}

async function enrollDemoWardForParent() {
    try {
        const res = await fetch('/api/parent/enroll_demo_ward', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ parent_id: currentUser.id || 8 })
        });
        const data = await res.json();
        if (data.success) {
            alert(`🎉 ${data.message}`);
            renderParentDashboard();
        } else {
            alert(data.message);
        }
    } catch (e) {
        alert('Could not enroll demo ward');
    }
}

// Accountant Payment Deletion Request
function openRequestPaymentDeleteModal(paymentId, refNo, studentName, amount) {
    document.getElementById('req-del-payment-id').value = paymentId;
    document.getElementById('req-del-ref').innerText = refNo;
    document.getElementById('req-del-student').innerText = studentName;
    document.getElementById('req-del-amount').innerText = `₹${(amount || 0).toLocaleString()}`;
    document.getElementById('req-del-reason').value = '';
    openModal('modal-request-payment-delete');
    document.getElementById('req-del-reason').focus();
}

async function submitRequestPaymentDelete(e) {
    e.preventDefault();
    const paymentId = parseInt(document.getElementById('req-del-payment-id').value);
    const reason = document.getElementById('req-del-reason').value.trim();

    const payload = {
        payment_id: paymentId,
        reason: reason,
        requested_by_id: currentUser.id,
        requested_by_name: currentUser.name || 'Accountant Jude Bello'
    };

    try {
        const res = await fetch('/api/payments/request_delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✓ ${data.message}`);
            closeModal('modal-request-payment-delete');
            renderPaymentsTab();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (err) {
        alert('Failed to submit deletion request: ' + err.message);
    }
}

// Multi-Tier Review Payment Deletion Modal (Admin & Super Admin)
let currentReviewRole = 'admin';

function openReviewPaymentDeleteModal(requestId, action, role, refNo, studentName, amount) {
    currentReviewRole = role;
    document.getElementById('review-del-request-id').value = requestId;
    document.getElementById('review-del-action').value = action;
    document.getElementById('review-del-notes').value = '';

    const isApprove = action === 'approve';
    const isSuperAdmin = role === 'super_admin';

    const header = document.getElementById('review-del-header');
    const title = document.getElementById('review-del-title');
    const subtitle = document.getElementById('review-del-subtitle');
    const confirmBtn = document.getElementById('review-del-confirm-btn');

    if (isSuperAdmin) {
        header.style.background = isApprove ? '#b91c1c' : '#334155';
        title.innerHTML = isApprove ? 
            '<i class="fas fa-trash-alt"></i> Final Super Admin Approval & Permanent DB Deletion' : 
            '<i class="fas fa-times-circle"></i> Reject Payment Deletion Request';
        subtitle.innerText = 'Tier 2 Final Authority: Greenland School Executive Governance';
        confirmBtn.style.background = isApprove ? '#b91c1c' : '#475569';
        confirmBtn.style.borderColor = isApprove ? '#b91c1c' : '#475569';
        confirmBtn.innerText = isApprove ? '🗑️ Permanently Delete from Database' : 'Reject Request';
    } else {
        header.style.background = isApprove ? '#16a34a' : '#b91c1c';
        title.innerHTML = isApprove ? 
            '<i class="fas fa-check-circle"></i> Tier 1 Principal Approval (Forward to Super Admin)' : 
            '<i class="fas fa-times-circle"></i> Reject Payment Deletion Request';
        subtitle.innerText = 'Tier 1 Review: Principal Academic & Operational Sanction';
        confirmBtn.style.background = isApprove ? '#16a34a' : '#b91c1c';
        confirmBtn.style.borderColor = isApprove ? '#16a34a' : '#b91c1c';
        confirmBtn.innerText = isApprove ? 'Approve & Forward to Super Admin' : 'Reject Deletion';
    }

    document.getElementById('review-del-summary-card').innerHTML = `
        <div style="font-size:0.85rem; line-height:1.6;">
            <div><strong>Request ID:</strong> #${requestId}</div>
            <div><strong>Receipt Ref:</strong> <span style="font-family:monospace; font-weight:700; color:#1e3a8a;">${refNo || '-'}</span></div>
            <div><strong>Student:</strong> ${studentName || '-'}</div>
            <div><strong>Paid Amount:</strong> <span style="color:#b91c1c; font-weight:700;">₹${(amount || 0).toLocaleString()}</span></div>
            <div style="margin-top:6px; padding-top:6px; border-top:1px dashed #cbd5e1; color:#0f172a;">
                <strong>Action:</strong> <span style="font-weight:700; color:${isApprove ? '#15803d' : '#b91c1c'};">${isApprove ? 'APPROVE' : 'REJECT'}</span>
                ${isSuperAdmin && isApprove ? '<br><span style="color:#b91c1c; font-weight:700;">⚠️ This action will immediately and irreversibly delete the payment record from the database!</span>' : ''}
            </div>
        </div>
    `;

    openModal('modal-review-payment-delete');
}

async function submitReviewPaymentDelete(e) {
    e.preventDefault();
    const requestId = parseInt(document.getElementById('review-del-request-id').value);
    const action = document.getElementById('review-del-action').value;
    const notes = document.getElementById('review-del-notes').value.trim();

    const payload = {
        request_id: requestId,
        role: currentReviewRole,
        action: action,
        notes: notes,
        reviewer_id: currentUser.id,
        reviewer_name: currentUser.name || (currentReviewRole === 'super_admin' ? 'Super Admin' : 'Admin Principal')
    };

    try {
        const res = await fetch('/api/payments/approve_delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✓ ${data.message}`);
            closeModal('modal-review-payment-delete');
            renderPaymentsTab();
        } else {
            alert(`Workflow Alert: ${data.message}`);
        }
    } catch (err) {
        alert('Review submission failed: ' + err.message);
    }
}

// Super Admin Direct Deletion Privilege
async function superAdminDirectDeletePayment(paymentId, refNo, studentName) {
    if (currentRole !== 'super_admin') {
        alert('Unauthorized: Direct payment deletion is reserved exclusively for Super Admin.');
        return;
    }

    const confirmMsg = `⚠️ Super Admin Direct Delete Authorization:\n\nAre you sure you want to permanently delete payment record '${refNo}' for student '${studentName}' immediately from the database?\n\nThis will bypass the multi-step approval workflow and remove the record permanently.`;
    if (!confirm(confirmMsg)) return;

    try {
        const res = await fetch('/api/payments/direct_delete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                payment_id: paymentId,
                role: 'super_admin',
                reason: 'Direct deletion authorized by Super Admin',
                user_id: currentUser.id,
                user_name: currentUser.name || 'Super Admin'
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✓ ${data.message}`);
            renderPaymentsTab();
        } else {
            alert(`Error: ${data.message}`);
        }
    } catch (err) {
        alert('Could not delete payment: ' + err.message);
    }
}


// =====================================================================
// DIRECTOR USER ROLE ASSIGNMENT & SYSTEM TEST DATA CLEANUP
// =====================================================================
function openAssignUserRoleModal(userId) {
    const u = (siteData.users || []).find(x => x.id === userId);
    if (!u) return;
    document.getElementById('assign-role-user-id').value = u.id;
    document.getElementById('assign-role-username').value = u.username;
    document.getElementById('assign-role-role').value = u.user_type || 'teacher';
    document.getElementById('assign-role-person-name').value = u.name || '';
    handleAssignPersonNameChange(u.name || '');
    if (u.name && u.gender) {
        document.getElementById('assign-role-gender').value = u.gender;
    }

    const isCommon = Boolean(u.is_common_id || u.username === 'GS_teacher');
    const commonCheck = document.getElementById('assign-role-is-common');
    if (commonCheck) commonCheck.checked = isCommon;
    const commonName = document.getElementById('assign-role-common-name');
    if (commonName) commonName.value = u.common_id_name || (isCommon ? 'Computer Teacher Lab Fleet' : '');
    const fleetSel = document.getElementById('assign-role-lab-fleet');
    if (fleetSel) {
        fleetSel.value = (u.username === 'GS_teacher' || (u.assigned_lab_count && u.assigned_lab_count >= 100)) ? 'both' : 'none';
    }
    populateAdminIdOptions('assign-role-admin-id', u.admin_user_id || u.admin_username);
    toggleAssignRoleCommon(isCommon);

    const assignDelBtn = document.getElementById('assign-role-delete-btn');
    if (assignDelBtn) {
        assignDelBtn.style.display = (['Owner(Directer)', 'GS_itsupport'].includes(u.username)) ? 'none' : 'inline-block';
    }

    openModal('modal-assign-user-role');
}


async function populateAdminIdOptions(selectId, selectedId = null) {
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

    let opts = '<option value="">— Select Staff/Teacher Admin (Students & Parents ineligible) —</option>';
    let matched = false;

    const rolePriority = { 'teacher': 1, 'it_admin': 2, 'super_admin': 3, 'admin': 4, 'accountant': 5, 'librarian': 6 };
    const sorted = [...users].sort((a, b) => {
        const pa = rolePriority[a.user_type] || 99;
        const pb = rolePriority[b.user_type] || 99;
        return pa - pb;
    });

    sorted.forEach(u => {
        // STRICT INSTITUTIONAL POLICY: Students and Parents cannot be assigned as Admin for a Common ID
        // (even if an Admin or Owner assigned a person name to that student/parent ID).
        // Only Faculty/Teachers, IT Support, Principal/Admin, Director/Owner, Accountant, and Librarian are permitted.
        if (['student', 'parent', 'common_id'].includes(u.user_type)) {
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
}

function toggleAssignRoleCommon(isCommon) {
    const fields = document.getElementById('assign-role-common-fields');
    const badge = document.getElementById('assign-role-mail-badge');
    if (fields) fields.style.display = isCommon ? 'block' : 'none';
    if (badge) badge.style.display = isCommon ? 'inline-block' : 'none';
    if (isCommon) {
        populateAdminIdOptions('assign-role-admin-id');
    }
}

function handleAssignPersonNameChange(val) {
    const sel = document.getElementById('assign-role-gender');
    const hint = document.getElementById('assign-role-gender-hint');
    if (!val || !val.trim()) {
        if (sel) {
            sel.disabled = true;
            sel.value = '';
        }
        if (hint) hint.innerHTML = '🔒 Disabled: Role ID has no assigned person name (no gender shown).';
    } else {
        if (sel) sel.disabled = false;
        if (hint) hint.innerHTML = '✅ Enabled: Assigned person gender can now be set (Male / Female).';
    }
}

async function submitAssignUserRole(e) {
    e.preventDefault();
    const userId = parseInt(document.getElementById('assign-role-user-id').value);
    const newRole = document.getElementById('assign-role-role').value;
    const personName = document.getElementById('assign-role-person-name').value.trim();
    const genderSel = document.getElementById('assign-role-gender');
    const gender = personName && genderSel ? genderSel.value : null;

    const isCommon = (newRole === 'common_id') || (document.getElementById('assign-role-is-common') ? document.getElementById('assign-role-is-common').checked : false);
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
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-assign-user-role');
            if (window.siteData) {
                try {
                    window.siteData.users = await fetch('/api/users').then(r => r.json());
                } catch(e) {}
            }
            if (typeof renderUsersTab === 'function' && currentTab === 'users') renderUsersTab();
            if (typeof renderCredentialsTab === 'function' && currentTab === 'credentials') renderCredentialsTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to reassign role: ' + err.message);
    }
}

async function confirmCleanTestData() {
    const msg = "🧹 CLEAN SYSTEM TEST DATA:\n\n" +
                "Are you sure you want to clean all test data? All synthetic dummy records will be cleared and the portal will return to a fresh state.\n\n" +
                "🔒 CRITICAL PRESERVATION GUARANTEE:\n" +
                "• Owner (Director) and IT Support Administrator IDs are preserved.\n" +
                "• Manually entered user data (such as Virat Singh and manual inquiries) will NOT be cleared!\n\n" +
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
            alert(`✅ Test data cleared successfully!\n${data.message}`);
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
}

async function seedFacultyDemo() {
    try {
        const res = await fetch('/api/system/seed_faculty', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            renderUsersTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to seed faculty: ' + err.message);
    }
}

// =====================================================================
// IT SUPPORT ADMINISTRATOR DASHBOARD
// =====================================================================
async function renderITAdminDashboard() {
    document.getElementById('portal-header-title').innerText = 'IT Support Administrator Control Hub';
    document.getElementById('portal-header-desc').innerText = 'Top-Level Administrative Oversight: Computer Lab Hardware, System Health & Repair Dispatch';

    try {
        const compData = await fetch('/api/lab/computers').then(r => r.json());
        const compSummary = compData.summary || { total: 0, working: 0, faulty: 0, in_repair: 0 };
        const complaintsData = await fetch('/api/lab/complaints').then(r => r.json());
        const complaints = complaintsData.complaints || [];
        const pendingComplaints = complaints.filter(c => c.status === 'Pending' || c.status === 'Assigned');
        
        let assetAnalytics = { metrics: { total_assets: 0, total_allocated: 0, total_on_rent: 0, total_in_service: 0 }, due_payments: [], expiring_warranties: [] };
        try {
            assetAnalytics = await fetch('/api/it_assets/analytics').then(r => r.json());
        } catch(e) {}

        const html = `
            <div class="metrics-row">
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Total Lab Workstations</h5>
                        <h2>${compSummary.total}</h2>
                        <span style="font-size:0.75rem; color:#2563eb;">Lab 1 & Lab 2 Total</span>
                    </div>
                    <div class="metric-icon metric-blue">🖥️</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Operational (Working)</h5>
                        <h2>${compSummary.working}</h2>
                        <span style="font-size:0.75rem; color:#10b981;">Ready for Student Labs</span>
                    </div>
                    <div class="metric-icon metric-green">✓</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Fault Reported</h5>
                        <h2>${compSummary.faulty}</h2>
                        <span style="font-size:0.75rem; color:#ef4444;">Needs Technician Action</span>
                    </div>
                    <div class="metric-icon metric-red">⚠️</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>In Repair / Assigned</h5>
                        <h2>${compSummary.in_repair}</h2>
                        <span style="font-size:0.75rem; color:#f59e0b;">Technician Dispatched</span>
                    </div>
                    <div class="metric-icon metric-amber">🛠️</div>
                </div>
            </div>

            <div style="display:grid; grid-template-columns: 2fr 1fr; gap:24px; margin-top:20px;">
                <div class="card">
                    <div class="card-header" style="justify-content:space-between;">
                        <span class="card-title">🚨 Active Lab Fault Reports Requiring IT Support (${pendingComplaints.length})</span>
                        <button class="btn btn-primary btn-sm" onclick="showTab('lab_complaints')">View All Tickets →</button>
                    </div>
                    <div class="card-body" style="padding:0; overflow-x:auto;">
                        ${pendingComplaints.length === 0 ? `
                            <div style="text-align:center; padding:30px; color:#10b981;">
                                <div style="font-size:2rem; margin-bottom:8px;">✅</div>
                                <strong>All Computer Lab Systems Operational</strong>
                                <p style="font-size:0.8rem; color:#64748b; margin-top:4px;">No pending hardware or software fault tickets reported by teachers.</p>
                            </div>
                        ` : `
                            <table class="data-table" style="font-size:0.83rem;">
                                <thead>
                                    <tr>
                                        <th>Ticket #</th>
                                        <th>Computer</th>
                                        <th>Issue Category</th>
                                        <th>Reported By</th>
                                        <th>Status</th>
                                        <th>Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${pendingComplaints.slice(0, 5).map(c => `
                                        <tr>
                                            <td><code style="font-weight:700; color:#1e3a8a;">${c.ticket_no}</code></td>
                                            <td><strong>${c.pc_number}</strong><br><span style="font-size:0.73rem; color:#64748b;">${c.lab_name}</span></td>
                                            <td>${c.issue_category}</td>
                                            <td>${c.reported_by_name}</td>
                                            <td>
                                                <span class="badge" style="background:${c.status === 'Pending' ? '#fee2e2; color:#dc2626;' : '#eff6ff; color:#2563eb;'}">
                                                    ${c.status === 'Pending' ? '⚠️ Pending Dispatch' : '🛠️ In Repair'}
                                                </span>
                                            </td>
                                            <td>
                                                ${c.status === 'Pending' ? `
                                                    <button class="btn btn-primary btn-sm" style="font-size:0.72rem; padding:3px 8px;" onclick="openAssignLabRepairModal(${c.id}, '${c.pc_number}', '${c.lab_name}', ${c.computer_id || 'null'})">Assign Tech</button>
                                                ` : `
                                                    <button class="btn btn-success btn-sm" style="font-size:0.72rem; padding:3px 8px; background:#16a34a;" onclick="openResolveLabComplaintModal(${c.id}, '${c.pc_number}', '${c.lab_name}', ${c.computer_id || 'null'})">Mark Fixed</button>
                                                `}
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        `}
                    </div>
                </div>

                <div class="card">
                    <div class="card-header">
                        <span class="card-title">⚡ Quick IT Actions</span>
                    </div>
                    <div class="card-body" style="display:flex; flex-direction:column; gap:10px;">
                        <button class="btn btn-primary" onclick="showTab('asset_management')" style="text-align:left; display:flex; align-items:center; gap:10px; background:linear-gradient(135deg, #0284c7, #1e3a8a); color:white; font-weight:700;">
                            <span>💻</span> Laptop & PC Asset Manager (Full System)
                        </button>
                        <button class="btn btn-secondary" onclick="showTab('lab_manager')" style="text-align:left; display:flex; align-items:center; gap:10px;">
                            <span>🖥️</span> Explore Computer Lab Grid
                        </button>
                        <button class="btn btn-secondary" onclick="showTab('lab_complaints')" style="text-align:left; display:flex; align-items:center; gap:10px;">
                            <span>🛠️</span> Repair Dispatch Ledger
                        </button>
                        <button class="btn btn-secondary" onclick="showTab('users')" style="text-align:left; display:flex; align-items:center; gap:10px; background:#eff6ff; border-color:#93c5fd; color:#1e40af; font-weight:700;">
                            <span>🎭</span> Assign & Change User Roles
                        </button>
                        <button class="btn btn-secondary" onclick="openModal('modal-add-lab-pc')" style="text-align:left; display:flex; align-items:center; gap:10px;">
                            <span>➕</span> Add / Configure Lab PC
                        </button>
                        <button class="btn btn-success" onclick="window.location.href='/api/it/export_credentials_excel'" style="text-align:left; display:flex; align-items:center; gap:10px; background:#15803d; border-color:#166534; color:white; font-weight:700; box-shadow:0 2px 4px rgba(21,128,61,0.2);">
                            <span>📊</span> Download All User IDs & Passwords (Excel)
                        </button>
                        <button class="btn btn-secondary" onclick="openModal('modal-report-lab-complaint')" style="text-align:left; display:flex; align-items:center; gap:10px;">
                            <span>🚨</span> Log Lab Hardware Fault
                        </button>
                        <button class="btn btn-danger" onclick="confirmCleanTestData()" style="text-align:left; display:flex; align-items:center; gap:10px; background:#dc2626; border-color:#b91c1c; color:white; font-weight:700;">
                            <span>🧹</span> Clean All Test Data
                        </button>
                    </div>
                </div>
            </div>
        `;
        document.getElementById('portal-tab-content').innerHTML = html;
    } catch (err) {
        document.getElementById('portal-tab-content').innerHTML = `<div style="padding:20px; color:red;">Error loading IT Support dashboard: ${err.message}</div>`;
    }
}

// =====================================================================
// COMPUTER LAB INFRASTRUCTURE & WORKSTATIONS MANAGER
// =====================================================================
let labManagerFilterLab = 'ALL';
let labManagerFilterStatus = 'ALL';

async function renderLabManagerTab() {
    document.getElementById('portal-header-title').innerText = 'Computer Lab Infrastructure & Device Management';
    document.getElementById('portal-header-desc').innerText = 'IT Support Administrator: Real-time inventory and operational status of all student workstations across Computer Labs';

    try {
        const res = await fetch('/api/lab/computers');
        const data = await res.json();
        const computers = data.computers || [];
        const summary = data.summary || { total: 0, working: 0, faulty: 0, in_repair: 0 };
        siteData.labComputers = computers;

        // Apply filters
        let filtered = computers.filter(c => {
            if (labManagerFilterLab !== 'ALL' && c.lab_name !== labManagerFilterLab) return false;
            if (labManagerFilterStatus !== 'ALL' && c.status !== labManagerFilterStatus) return false;
            return true;
        });

        const html = `
            <!-- Metrics Row -->
            <div class="metrics-row" style="margin-bottom:20px;">
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Total Workstations</h5>
                        <h2>${summary.total}</h2>
                        <span style="font-size:0.75rem; color:#2563eb;">Configured PCs</span>
                    </div>
                    <div class="metric-icon metric-blue">🖥️</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Operational (Working)</h5>
                        <h2>${summary.working}</h2>
                        <span style="font-size:0.75rem; color:#10b981;">100% Online</span>
                    </div>
                    <div class="metric-icon metric-green">✓</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Fault Reported</h5>
                        <h2>${summary.faulty}</h2>
                        <span style="font-size:0.75rem; color:#ef4444;">Needs Repair</span>
                    </div>
                    <div class="metric-icon metric-red">⚠️</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>In Repair</h5>
                        <h2>${summary.in_repair}</h2>
                        <span style="font-size:0.75rem; color:#f59e0b;">Assigned to Tech</span>
                    </div>
                    <div class="metric-icon metric-amber">🛠️</div>
                </div>
            </div>

            <!-- Filter Controls & Action Header -->
            <div class="card" style="margin-bottom:20px;">
                <div class="card-body" style="padding:16px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px;">
                    <div style="display:flex; align-items:center; gap:12px; flex-wrap:wrap;">
                        <label style="font-weight:700; color:#0f172a; font-size:0.88rem;">Filter Lab:</label>
                        <select class="form-control" style="width:200px;" onchange="filterLabComputers('lab', this.value)">
                            <option value="ALL" ${labManagerFilterLab === 'ALL' ? 'selected' : ''}>All Computer Labs</option>
                            <option value="Computer Lab 1 (Main Lab)" ${labManagerFilterLab === 'Computer Lab 1 (Main Lab)' ? 'selected' : ''}>Computer Lab 1 (Main Lab)</option>
                            <option value="Computer Lab 2 (Senior Coding Lab)" ${labManagerFilterLab === 'Computer Lab 2 (Senior Coding Lab)' ? 'selected' : ''}>Computer Lab 2 (Senior Coding Lab)</option>
                        </select>

                        <label style="font-weight:700; color:#0f172a; font-size:0.88rem; margin-left:8px;">Status:</label>
                        <select class="form-control" style="width:160px;" onchange="filterLabComputers('status', this.value)">
                            <option value="ALL" ${labManagerFilterStatus === 'ALL' ? 'selected' : ''}>All Statuses</option>
                            <option value="Working" ${labManagerFilterStatus === 'Working' ? 'selected' : ''}>Operational (Working)</option>
                            <option value="Faulty" ${labManagerFilterStatus === 'Faulty' ? 'selected' : ''}>Faulty</option>
                            <option value="In Repair" ${labManagerFilterStatus === 'In Repair' ? 'selected' : ''}>In Repair</option>
                        </select>
                    </div>

                    <div style="display:flex; gap:10px;">
                        <button class="btn btn-outline btn-sm" onclick="openModal('modal-report-lab-complaint')">
                            🚨 Report Computer Fault
                        </button>
                        ${['it_admin', 'super_admin'].includes(currentRole) ? `
                            <button class="btn btn-primary btn-sm" onclick="openModal('modal-add-lab-pc')">
                                ➕ Add New Workstation
                            </button>
                        ` : ''}
                    </div>
                </div>
            </div>

            <!-- Computer Visual Workstation Grid -->
            <div class="card" style="margin-bottom:24px;">
                <div class="card-header" style="justify-content:space-between;">
                    <span class="card-title">🖥️ Computer Workstation Status Grid (${filtered.length} Workstations)</span>
                    <span style="font-size:0.75rem; color:#64748b;">Click on any faulty PC to inspect or assign repair</span>
                </div>
                <div class="card-body" style="padding:16px;">
                    <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(130px, 1fr)); gap:12px;">
                        ${filtered.map(c => {
                            let borderCol = '#10b981';
                            let bgCol = '#f0fdf4';
                            let icon = '🖥️';
                            let badgeTxt = 'Working';
                            let badgeStyle = 'background:#dcfce7; color:#15803d;';

                            if (c.status === 'Faulty') {
                                borderCol = '#ef4444';
                                bgCol = '#fef2f2';
                                icon = '⚠️';
                                badgeTxt = 'Faulty';
                                badgeStyle = 'background:#fee2e2; color:#dc2626;';
                            } else if (c.status === 'In Repair') {
                                borderCol = '#f59e0b';
                                bgCol = '#fffbeb';
                                icon = '🛠️';
                                badgeTxt = 'In Repair';
                                badgeStyle = 'background:#fef3c7; color:#d97706;';
                            }

                            return `
                                <div style="border:2px solid ${borderCol}; background:${bgCol}; border-radius:8px; padding:10px 8px; text-align:center; transition:transform 0.15s ease; cursor:pointer;" onclick="handleClickLabComputer(${c.id}, '${c.pc_number}', '${c.status}', ${c.active_complaint_id || 'null'}, '${c.lab_name}')" title="${c.pc_number} - ${c.lab_name} (${c.status})">
                                    <div style="font-size:1.6rem; margin-bottom:4px;">${icon}</div>
                                    <div style="font-weight:800; font-size:0.95rem; color:#0f172a; font-family:monospace;">${c.pc_number}</div>
                                    <div style="font-size:0.68rem; color:#64748b; margin-top:2px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${c.ip_address || 'DHCP'}</div>
                                    <div style="margin-top:6px;">
                                        <span class="badge" style="font-size:0.68rem; padding:2px 6px; border-radius:4px; font-weight:700; ${badgeStyle}">
                                            ${badgeTxt}
                                        </span>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>

            <!-- Detailed Inventory Table -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">📋 Workstation Specifications & Maintenance Ledger</span>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    <table class="data-table" style="font-size:0.83rem;">
                        <thead>
                            <tr>
                                <th>PC Number</th>
                                <th>Lab Name</th>
                                <th>IP Address</th>
                                <th>Processor & RAM</th>
                                <th>Operating System</th>
                                <th>Operational Status</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${filtered.map(c => `
                                <tr>
                                    <td><strong style="font-family:monospace; color:#1e3a8a; font-size:0.92rem;">${c.pc_number}</strong></td>
                                    <td>${c.lab_name}</td>
                                    <td><code style="font-size:0.78rem;">${c.ip_address || '—'}</code></td>
                                    <td><span style="font-size:0.78rem; color:#475569;">${c.processor || 'Intel Core i5'}</span></td>
                                    <td>${c.os || 'Windows 11'}</td>
                                    <td>
                                        <span class="badge" style="${c.status === 'Working' ? 'background:#dcfce7; color:#15803d;' : (c.status === 'Faulty' ? 'background:#fee2e2; color:#dc2626;' : 'background:#fef3c7; color:#d97706;')}">
                                            ${c.status}
                                        </span>
                                    </td>
                                    <td>
                                        <div style="display:flex; gap:6px;">
                                            ${c.status === 'Faulty' ? `
                                                <button class="btn btn-primary btn-sm" style="font-size:0.72rem; padding:3px 8px;" onclick="openAssignLabRepairModal(${c.active_complaint_id || 'null'}, '${c.pc_number}', '${c.lab_name}', ${c.id})">
                                                    🛠️ Assign Tech
                                                </button>
                                            ` : (c.status === 'In Repair' ? `
                                                <button class="btn btn-success btn-sm" style="font-size:0.72rem; padding:3px 8px; background:#16a34a;" onclick="openResolveLabComplaintModal(${c.active_complaint_id || 'null'}, '${c.pc_number}', '${c.lab_name}', ${c.id})">
                                                    ✅ Mark Fixed
                                                </button>
                                            ` : `
                                                <button class="btn btn-outline btn-sm" style="font-size:0.72rem; padding:3px 8px;" onclick="prefillReportComplaint('${c.lab_name}', '${c.pc_number}')">
                                                    🚨 Report Issue
                                                </button>
                                            `)}
                                        </div>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>
        `;

        document.getElementById('portal-tab-content').innerHTML = html;
    } catch (err) {
        document.getElementById('portal-tab-content').innerHTML = `<div style="padding:20px; color:red;">Error loading Lab Manager: ${err.message}</div>`;
    }
}

function filterLabComputers(type, val) {
    if (type === 'lab') labManagerFilterLab = val;
    if (type === 'status') labManagerFilterStatus = val;
    renderLabManagerTab();
}

function handleClickLabComputer(id, pcNumber, status, complaintId, labName) {
    const isIT = isITUser(currentUser);
    if (status === 'Faulty' && isIT) {
        openAssignLabRepairModal(complaintId, pcNumber, labName, id);
    } else if (status === 'In Repair' && isIT) {
        openResolveLabComplaintModal(complaintId, pcNumber, labName, id);
    } else {
        prefillReportComplaint(labName || 'Computer Lab 1 (Main Lab)', pcNumber);
    }
}

function prefillReportComplaint(labName, pcNumber) {
    openModal('modal-report-lab-complaint');
    setTimeout(() => {
        const labSel = document.getElementById('complaint-lab-name');
        if (labSel) labSel.value = labName;
        updateComputerOptionsForComplaint(pcNumber);
    }, 100);
}

// =====================================================================
// COMPUTER LAB COMPLAINTS & REPAIR DISPATCH
// =====================================================================
async function renderLabComplaintsTab() {
    document.getElementById('portal-header-title').innerText = 'Computer Lab Fault Complaints & Repair Dispatch';
    document.getElementById('portal-header-desc').innerText = 'Computer Teachers lodge faulty computer tickets; IT Support Administrator assigns repair technicians and restores machines to operational status';

    try {
        const [compRes, complaintsRes] = await Promise.all([
            fetch('/api/lab/computers').then(r => r.json()).catch(() => ({ computers: [] })),
            fetch('/api/lab/complaints').then(r => r.json()).catch(() => ({ complaints: [] }))
        ]);

        const computers = compRes.computers || [];
        const complaints = complaintsRes.complaints || [];
        const isITAdminOrOwner = isITUser(currentUser) || ['it_admin', 'super_admin', 'admin'].includes(currentRole);
        const isTeacher = currentRole === 'teacher';

        const pendingCount = complaints.filter(c => ['Pending', 'Open', 'Pending Director Approval', 'Repair Approved by Director'].includes(c.status)).length;
        const assignedCount = complaints.filter(c => ['Assigned', 'In Repair', 'In Progress'].includes(c.status)).length;
        const resolvedCount = complaints.filter(c => c.status === 'Resolved').length;

        const html = `
            <!-- Computer Teacher Access & Security Callout -->
            <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:14px 18px; margin-bottom:18px; color:#1e40af; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:10px;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:1.8rem;">🖥️</span>
                    <div>
                        <strong style="font-size:0.95rem;">Computer Teacher Access & Lab Governance Policy:</strong>
                        <div style="font-size:0.82rem; color:#1d4ed8; margin-top:2px;">
                            • <strong>Computer Teacher:</strong> Authorized access to <strong>view complaints of all computers</strong> in the computer lab and lodge fault reports.<br>
                            • <strong>Hardware Lock:</strong> Computer Teachers <strong>cannot edit computer name, IP address, or configuration</strong>. Device administration is strictly reserved for IT Support Administrator.
                        </div>
                    </div>
                </div>
                <button class="btn btn-danger" style="background:#dc2626; border-color:#b91c1c; font-weight:700; padding:8px 16px; display:inline-flex; align-items:center; gap:8px;" onclick="openReportLabComplaintModal()">
                    <i class="fas fa-exclamation-circle"></i> 🚨 Lodge Workstation Complaint
                </button>
            </div>

            <!-- Lab Workstations Status Grid (Overview of all computers in Lab) -->
            <div class="card" style="margin-bottom:20px;">
                <div class="card-header" style="justify-content:space-between; align-items:center;">
                    <div>
                        <span class="card-title">🖥️ Computer Lab Workstations Health (${computers.length} PCs)</span>
                        <p style="font-size:0.75rem; color:#64748b; margin-top:2px;">Click on any workstation to log a complaint or view active issue</p>
                    </div>
                    <span style="font-size:0.75rem; background:#f1f5f9; color:#475569; padding:4px 10px; border-radius:6px; font-weight:600;">
                        🔒 Config & IP Edit: IT Support Admin Only
                    </span>
                </div>
                <div class="card-body" style="padding:14px;">
                    <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(110px, 1fr)); gap:10px;">
                        ${computers.map(c => {
                            let borderCol = '#10b981';
                            let bgCol = '#f0fdf4';
                            let icon = '🖥️';
                            let badgeTxt = 'Working';
                            let badgeStyle = 'background:#dcfce7; color:#15803d;';

                            if (c.status === 'Faulty') {
                                borderCol = '#ef4444';
                                bgCol = '#fef2f2';
                                icon = '⚠️';
                                badgeTxt = 'Faulty';
                                badgeStyle = 'background:#fee2e2; color:#dc2626;';
                            } else if (c.status === 'In Repair') {
                                borderCol = '#f59e0b';
                                bgCol = '#fffbeb';
                                icon = '🛠️';
                                badgeTxt = 'Repairing';
                                badgeStyle = 'background:#fef3c7; color:#d97706;';
                            }

                            return `
                                <div style="border:1.5px solid ${borderCol}; background:${bgCol}; border-radius:8px; padding:8px 6px; text-align:center; cursor:pointer; transition:transform 0.15s ease;" 
                                     onclick="handleClickLabComputer(${c.id}, '${c.pc_number}', '${c.status}', ${c.active_complaint_id || 'null'}, '${c.lab_name}')" 
                                     title="${c.pc_number} (${c.lab_name}) - Status: ${c.status}. Click to report issue.">
                                    <div style="font-size:1.3rem;">${icon}</div>
                                    <div style="font-weight:800; font-size:0.85rem; color:#0f172a; font-family:monospace; margin-top:2px;">${c.pc_number}</div>
                                    <div style="font-size:0.62rem; color:#64748b; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">${c.ip_address || 'DHCP'}</div>
                                    <div style="margin-top:4px;">
                                        <span class="badge" style="font-size:0.62rem; padding:1px 5px; border-radius:4px; font-weight:700; ${badgeStyle}">
                                            ${badgeTxt}
                                        </span>
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            </div>

            <!-- Metrics Row -->
            <div class="metrics-row" style="margin-bottom:20px;">
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Total Tickets Logged</h5>
                        <h2>${complaints.length}</h2>
                        <span style="font-size:0.75rem; color:#2563eb;">All Time Complaints</span>
                    </div>
                    <div class="metric-icon metric-blue">📑</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Pending IT Action</h5>
                        <h2>${pendingCount}</h2>
                        <span style="font-size:0.75rem; color:#ef4444;">Awaiting Tech Assignment</span>
                    </div>
                    <div class="metric-icon metric-red">⚠️</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Under Repair</h5>
                        <h2>${assignedCount}</h2>
                        <span style="font-size:0.75rem; color:#f59e0b;">Technician Dispatched</span>
                    </div>
                    <div class="metric-icon metric-amber">🛠️</div>
                </div>
                <div class="metric-card">
                    <div class="metric-info">
                        <h5>Resolved & Restored</h5>
                        <h2>${resolvedCount}</h2>
                        <span style="font-size:0.75rem; color:#10b981;">Operational Again</span>
                    </div>
                    <div class="metric-icon metric-green">✓</div>
                </div>
            </div>

            <!-- Action Toolbar -->
            <div class="card" style="margin-bottom:20px;">
                <div class="card-body" style="padding:16px 20px; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px;">
                    <div>
                        <strong style="color:#0f172a; font-size:0.95rem;">Computer Teacher & IT Support Ticket System</strong>
                        <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">
                            ${isITAdminOrOwner ? '👨‍💻 IT Administrator Mode: Review tickets, assign repair technicians, and confirm operational testing.' : '👨‍🏫 Teacher Mode: Report any non-functional lab PC directly to IT Support Administrator.'}
                        </div>
                    </div>
                    <button class="btn btn-danger" style="background:#dc2626; border-color:#b91c1c; font-weight:700; display:inline-flex; align-items:center; gap:8px;" onclick="openReportLabComplaintModal()">
                        <i class="fas fa-exclamation-circle"></i> 🚨 Report Faulty Computer
                    </button>
                </div>
            </div>

            <!-- Complaints Table -->
            <div class="card">
                <div class="card-header" style="justify-content:space-between;">
                    <span class="card-title">📋 Maintenance & Repair Ticket Ledger (${complaints.length})</span>
                    <button class="btn btn-outline btn-sm" onclick="renderLabComplaintsTab()">🔄 Refresh Tickets</button>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    ${complaints.length === 0 ? `
                        <div style="text-align:center; padding:40px; color:#64748b;">
                            <div style="font-size:2.5rem; margin-bottom:10px;">🎉</div>
                            <strong>No Computer Lab Complaints on Record</strong>
                            <p style="font-size:0.82rem; margin-top:4px;">All computers in Lab 1 and Lab 2 are running smoothly.</p>
                        </div>
                    ` : `
                        <table class="data-table" style="font-size:0.83rem;">
                            <thead>
                                <tr>
                                    <th>Ticket #</th>
                                    <th>Workstation</th>
                                    <th>Issue Category & Description</th>
                                    <th>Urgency</th>
                                    <th>Reported By</th>
                                    <th>Status</th>
                                    <th>Assigned Technician</th>
                                    <th>Resolution</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${complaints.map(c => {
                                    let statusBadge = `<span class="badge" style="background:#fee2e2; color:#dc2626; font-weight:700;">⚠️ Pending</span>`;
                                    if (['Assigned', 'In Repair', 'In Progress'].includes(c.status)) {
                                        statusBadge = `<span class="badge" style="background:#eff6ff; color:#2563eb; font-weight:700;">🛠️ In Repair</span>`;
                                    } else if (c.status === 'Resolved') {
                                        statusBadge = `<span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700;">✅ Resolved</span>`;
                                    } else if (c.status === 'Repair Approved by Director') {
                                        statusBadge = `<span class="badge" style="background:#fef3c7; color:#b45309; font-weight:700;">👑 Director Approved</span>`;
                                    } else if (c.status === 'Repair Order Rejected') {
                                        statusBadge = `<span class="badge" style="background:#f1f5f9; color:#64748b; font-weight:700;">❌ Rejected</span>`;
                                    }

                                    return `
                                        <tr>
                                            <td><code style="font-weight:700; color:#1e3a8a;">${c.ticket_no}</code></td>
                                            <td>
                                                <strong style="color:#0f172a; font-family:monospace; font-size:0.92rem;">${c.pc_number}</strong>
                                                <div style="font-size:0.73rem; color:#64748b;">${c.lab_name}</div>
                                            </td>
                                            <td style="max-width:240px;">
                                                <strong style="color:#334155;">${c.issue_category}</strong>
                                                <div style="font-size:0.76rem; color:#64748b; margin-top:2px;">${c.problem_description}</div>
                                            </td>
                                            <td>
                                                <span style="font-weight:700; color:${c.priority === 'Critical' ? '#dc2626' : (c.priority === 'High' ? '#ea580c' : '#2563eb')};">
                                                    ${c.priority}
                                                </span>
                                            </td>
                                            <td>
                                                <div style="font-weight:700; color:#0f172a;">${c.reported_by_name}</div>
                                                <div style="font-size:0.72rem; color:#64748b;">${c.created_at || 'Recently'}</div>
                                            </td>
                                            <td>${statusBadge}</td>
                                            <td>
                                                ${c.assigned_to_name ? `
                                                    <strong>${c.assigned_to_name}</strong>
                                                    <div style="font-size:0.72rem; color:#64748b;">by ${c.assigned_by || 'IT Support'}</div>
                                                ` : '<span style="color:#94a3b8; font-style:italic;">Unassigned</span>'}
                                            </td>
                                            <td style="max-width:200px;">
                                                ${c.resolution_notes ? `
                                                    <div style="font-size:0.76rem; color:#15803d;">${c.resolution_notes}</div>
                                                    <div style="font-size:0.7rem; color:#64748b;">Resolved by ${c.resolved_by || 'IT Tech'}</div>
                                                ` : '<span style="color:#94a3b8; font-style:italic;">Pending</span>'}
                                            </td>
                                            <td>
                                                <div style="display:flex; gap:6px; flex-direction:column;">
                                                    ${c.status !== 'Resolved' && isITAdminOrOwner ? `
                                                        <button class="btn btn-primary btn-sm" style="font-size:0.72rem; padding:4px 8px; font-weight:700;" onclick="openAssignLabRepairModal(${c.id}, '${c.pc_number}', '${c.lab_name}', ${c.computer_id || 'null'})">
                                                            🛠️ ${['Assigned', 'In Repair', 'In Progress'].includes(c.status) ? 'Re-assign Tech' : 'Assign Tech'}
                                                        </button>
                                                        <button class="btn btn-success btn-sm" style="font-size:0.72rem; padding:4px 8px; background:#16a34a; font-weight:700;" onclick="openResolveLabComplaintModal(${c.id}, '${c.pc_number}', '${c.lab_name}', ${c.computer_id || 'null'})">
                                                            ✅ Mark Fixed / Resolve
                                                        </button>
                                                    ` : ''}
                                                    ${c.status === 'Resolved' ? `
                                                        <span style="font-size:0.72rem; color:#15803d; font-weight:700;">✓ Operational</span>
                                                        ${isITAdminOrOwner ? `
                                                            <button class="btn btn-outline btn-sm" style="font-size:0.68rem; padding:2px 6px; color:#dc2626; border-color:#fca5a5;" onclick="openAssignLabRepairModal(${c.id}, '${c.pc_number}', '${c.lab_name}', ${c.computer_id || 'null'})" title="Re-open if still experiencing issues">
                                                                🔄 Re-open
                                                            </button>
                                                        ` : ''}
                                                    ` : ''}
                                                </div>
                                            </td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    `}
                </div>
            </div>
        `;
        document.getElementById('portal-tab-content').innerHTML = html;
    } catch (err) {
        document.getElementById('portal-tab-content').innerHTML = `<div style="padding:20px; color:red;">Error loading Lab Complaints: ${err.message}</div>`;
    }
}

async function openReportLabComplaintModal() {
    openModal('modal-report-lab-complaint');
    await updateComputerOptionsForComplaint();
}

async function updateComputerOptionsForComplaint(selectedPc = null) {
    const labSel = document.getElementById('complaint-lab-name');
    const labName = labSel ? labSel.value : 'Computer Lab 1 (Main Lab)';
    const select = document.getElementById('complaint-pc-number');
    if (!select) return;
    select.innerHTML = '<option value="">Loading PCs...</option>';

    try {
        let computers = siteData.labComputers;
        if (!computers) {
            const res = await fetch('/api/lab/computers');
            const data = await res.json();
            computers = data.computers || [];
            siteData.labComputers = computers;
        }

        const isLab1 = labName.includes('1') || labName.includes('Main');
        const filtered = computers.filter(c => {
            if (c.lab_name === labName) return true;
            if (isLab1 && (c.lab_name.includes('1') || c.lab_name.includes('Main'))) return true;
            if (!isLab1 && (c.lab_name.includes('2') || c.lab_name.includes('Senior') || c.lab_name.includes('Junior'))) return true;
            return false;
        });

        select.innerHTML = (filtered.length > 0 ? filtered : computers).map(c => `
            <option value="${c.pc_number}" ${selectedPc === c.pc_number ? 'selected' : ''}>
                ${c.pc_number} - Status: ${c.status} (${c.ip_address || 'DHCP'})
            </option>
        `).join('');
    } catch (err) {
        select.innerHTML = '<option value="PC-01">PC-01</option><option value="PC-02">PC-02</option>';
    }
}

async function submitReportLabComplaint(e) {
    e.preventDefault();
    const labName = document.getElementById('complaint-lab-name').value;
    const pcNumber = document.getElementById('complaint-pc-number').value;
    const issueCategory = document.getElementById('complaint-issue-cat').value;
    const priority = document.getElementById('complaint-priority').value;
    const desc = document.getElementById('complaint-desc').value.trim();

    try {
        const res = await fetch('/api/lab/complaints', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                lab_name: labName,
                pc_number: pcNumber,
                issue_category: issueCategory,
                problem_description: desc,
                priority: priority,
                user_id: currentUser ? currentUser.id : null,
                username: currentUser ? currentUser.username : 'GS_teacher'
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`🚨 ${data.message}`);
            closeModal('modal-report-lab-complaint');
            e.target.reset();
            if (currentTab === 'lab_manager') renderLabManagerTab();
            else renderLabComplaintsTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to submit complaint: ' + err.message);
    }
}

async function openAssignLabRepairModal(complaintId, pcNumber = '', labName = '', computerId = null) {
    try {
        const targetId = (complaintId && complaintId !== 'null' && complaintId !== 'undefined') ? parseInt(complaintId) : null;
        let targetComputerId = (computerId && computerId !== 'null' && computerId !== 'undefined') ? parseInt(computerId) : null;
        let targetPcNumber = (pcNumber && pcNumber !== 'null' && pcNumber !== 'undefined') ? String(pcNumber).trim() : '';
        let targetLabName = (labName && labName !== 'null' && labName !== 'undefined') ? String(labName).trim() : '';

        let complaints = [];
        try {
            const res = await fetch('/api/lab/complaints');
            const data = await res.json();
            complaints = data.complaints || [];
        } catch (fetchErr) {
            console.warn('Could not fetch complaints:', fetchErr);
        }

        let c = null;

        // 1. Match by numeric ticket ID if present
        if (targetId) {
            c = complaints.find(x => x.id === targetId);
        }

        // 2. If targetId wasn't found in complaints, maybe targetId is actually computer_id
        if (!c && targetId) {
            c = complaints.find(x => x.computer_id === targetId && x.status !== 'Resolved');
            if (!targetComputerId && c) targetComputerId = c.computer_id;
        }

        // 3. Match active ticket by pc_number or computer_id if ticket ID didn't match
        if (!c && (targetPcNumber || targetComputerId)) {
            c = complaints.find(x => (targetPcNumber && x.pc_number === targetPcNumber && x.status !== 'Resolved') || (targetComputerId && x.computer_id === targetComputerId && x.status !== 'Resolved'));
        }

        // 4. Fill in computer details if we found a complaint or have local siteData
        if (c) {
            if (!targetPcNumber && c.pc_number) targetPcNumber = c.pc_number;
            if (!targetLabName && c.lab_name) targetLabName = c.lab_name;
            if (!targetComputerId && c.computer_id) targetComputerId = c.computer_id;
        } else {
            if (window.siteData && window.siteData.labComputers) {
                const compMatch = window.siteData.labComputers.find(x => (targetComputerId && x.id === targetComputerId) || (targetPcNumber && x.pc_number === targetPcNumber));
                if (compMatch) {
                    if (!targetPcNumber) targetPcNumber = compMatch.pc_number;
                    if (!targetLabName) targetLabName = compMatch.lab_name;
                    if (!targetComputerId) targetComputerId = compMatch.id;
                }
            }
        }

        // 5. Always synthesize/guarantee a valid c object without ever blocking the user
        if (!c) {
            const finalPc = targetPcNumber || (targetComputerId ? `PC-${String(targetComputerId).padStart(2, '0')}` : 'Workstation');
            const finalLab = targetLabName || 'Computer Lab 1 (Main Lab)';
            c = {
                id: targetId || 0,
                ticket_no: 'TKT-DIRECT-ASSIGN',
                pc_number: finalPc,
                lab_name: finalLab,
                issue_category: 'Hardware / Functional Fault',
                problem_description: `Workstation ${finalPc} detected not working / hardware fault reported. Direct IT technician assignment.`,
                reported_by_name: currentUser ? `${currentUser.name} (IT Support)` : 'IT Support Administrator',
                assigned_to_name: '',
                computer_id: targetComputerId || null
            };
        }

        // Populate modal inputs safely
        const complaintIdInput = document.getElementById('assign-repair-complaint-id');
        if (complaintIdInput) complaintIdInput.value = c.id || 0;

        const pcNumberInput = document.getElementById('assign-repair-pc-number');
        if (pcNumberInput) pcNumberInput.value = c.pc_number || targetPcNumber || '';

        const computerIdInput = document.getElementById('assign-repair-computer-id');
        if (computerIdInput) computerIdInput.value = c.computer_id || targetComputerId || '';

        const labNameInput = document.getElementById('assign-repair-lab-name');
        if (labNameInput) labNameInput.value = c.lab_name || targetLabName || '';

        const customTechInput = document.getElementById('assign-repair-custom-tech');
        if (customTechInput) customTechInput.value = c.assigned_to_name || '';

        const summaryCard = document.getElementById('assign-repair-summary-card');
        if (summaryCard) {
            summaryCard.innerHTML = `
                <div><strong>Ticket:</strong> <code style="color:#1e3a8a; font-weight:700;">${c.ticket_no || 'TKT-DIRECT-ASSIGN'}</code></div>
                <div style="margin-top:2px;"><strong>Workstation:</strong> <code>${c.pc_number || targetPcNumber || 'Workstation'}</code> (${c.lab_name || targetLabName || 'Computer Lab'})</div>
                <div style="margin-top:2px;"><strong>Reported Issue:</strong> ${c.issue_category || 'Hardware Fault'} - <em>${c.problem_description || 'Fault reported'}</em></div>
                <div style="margin-top:2px;"><strong>Current Tech:</strong> <strong>${c.assigned_to_name || 'None Assigned'}</strong></div>
            `;
        }

        // Instantly open modal on first click without any blocking alert
        openModal('modal-assign-lab-repair');
    } catch (err) {
        console.error('Error in openAssignLabRepairModal:', err);
        // Resilient fallback: open modal anyway
        const complaintIdInput = document.getElementById('assign-repair-complaint-id');
        if (complaintIdInput) complaintIdInput.value = complaintId || 0;
        const pcNumberInput = document.getElementById('assign-repair-pc-number');
        if (pcNumberInput) pcNumberInput.value = pcNumber || '';
        const computerIdInput = document.getElementById('assign-repair-computer-id');
        if (computerIdInput) computerIdInput.value = computerId || '';
        const labNameInput = document.getElementById('assign-repair-lab-name');
        if (labNameInput) labNameInput.value = labName || '';
        openModal('modal-assign-lab-repair');
    }
}

async function submitAssignLabRepair(e) {
    e.preventDefault();
    const complaintId = parseInt(document.getElementById('assign-repair-complaint-id').value) || 0;
    const pcNumber = document.getElementById('assign-repair-pc-number') ? document.getElementById('assign-repair-pc-number').value : '';
    const computerId = document.getElementById('assign-repair-computer-id') ? parseInt(document.getElementById('assign-repair-computer-id').value) : null;
    const customTech = document.getElementById('assign-repair-custom-tech') ? document.getElementById('assign-repair-custom-tech').value.trim() : '';
    const selTech = document.getElementById('assign-repair-technician-name').value;
    const techName = customTech || selTech;
    const notes = document.getElementById('assign-repair-notes').value.trim();

    try {
        const res = await fetch('/api/lab/complaints/assign', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                complaint_id: complaintId,
                pc_number: pcNumber,
                computer_id: computerId,
                assigned_to_name: techName,
                technician_notes: notes,
                user_id: currentUser ? currentUser.id : null,
                username: currentUser ? currentUser.username : 'GS_itsupport'
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`🛠️ ${data.message}`);
            closeModal('modal-assign-lab-repair');
            e.target.reset();
            if (currentTab === 'lab_manager') renderLabManagerTab();
            else if (currentTab === 'asset_management') renderAssetManagementTab();
            else renderLabComplaintsTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to assign repair: ' + err.message);
    }
}

async function openResolveLabComplaintModal(complaintId, pcNumber = '', labName = '', computerId = null) {
    try {
        const res = await fetch('/api/lab/complaints');
        const data = await res.json();
        const complaints = data.complaints || [];

        const targetId = (complaintId && complaintId !== 'null' && complaintId !== 'undefined') ? parseInt(complaintId) : null;
        let c = null;

        if (targetId) {
            c = complaints.find(x => x.id === targetId);
        }

        if (!c && (pcNumber || computerId)) {
            c = complaints.find(x => (pcNumber && x.pc_number === pcNumber && x.status !== 'Resolved') || (computerId && x.computer_id === computerId && x.status !== 'Resolved'));
        }

        if (!c && (computerId || pcNumber)) {
            c = {
                id: targetId || 0,
                ticket_no: 'TKT-DIRECT-RESOLVE',
                pc_number: pcNumber || 'Workstation',
                lab_name: labName || 'Computer Lab',
                assigned_to_name: 'IT Support Administrator',
                problem_description: 'Hardware inspected, repaired, and confirmed operational.'
            };
        }

        if (!c) {
            const finalPc = pcNumber || (computerId ? `PC-${String(computerId).padStart(2, '0')}` : 'Workstation');
            c = {
                id: targetId || 0,
                ticket_no: 'TKT-DIRECT-RESOLVE',
                pc_number: finalPc,
                lab_name: labName || 'Computer Lab 1 (Main Lab)',
                assigned_to_name: 'IT Support Administrator',
                problem_description: `Hardware inspected, repaired, and confirmed operational for ${finalPc}.`
            };
        }

        document.getElementById('resolve-repair-complaint-id').value = c.id;
        if (document.getElementById('resolve-repair-pc-number')) document.getElementById('resolve-repair-pc-number').value = c.pc_number || pcNumber || '';
        if (document.getElementById('resolve-repair-computer-id')) document.getElementById('resolve-repair-computer-id').value = c.computer_id || computerId || '';
        if (document.getElementById('resolve-repair-lab-name')) document.getElementById('resolve-repair-lab-name').value = c.lab_name || labName || '';

        document.getElementById('resolve-repair-summary-card').innerHTML = `
            <div><strong>Ticket:</strong> <code style="color:#1e3a8a; font-weight:700;">${c.ticket_no || 'TKT-DIRECT-RESOLVE'}</code></div>
            <div style="margin-top:2px;"><strong>Workstation:</strong> <code>${c.pc_number || pcNumber}</code> (${c.lab_name || labName})</div>
            <div style="margin-top:2px;"><strong>Assigned Technician:</strong> <strong>${c.assigned_to_name || 'IT Support'}</strong></div>
            <div style="margin-top:2px;"><strong>Reported Issue:</strong> ${c.problem_description || 'Hardware defect'}</div>
        `;
        openModal('modal-resolve-lab-complaint');
    } catch (err) {
        alert('Failed to load complaint: ' + err.message);
    }
}

async function submitResolveLabComplaint(e) {
    e.preventDefault();
    const complaintId = parseInt(document.getElementById('resolve-repair-complaint-id').value) || 0;
    const pcNumber = document.getElementById('resolve-repair-pc-number') ? document.getElementById('resolve-repair-pc-number').value : '';
    const computerId = document.getElementById('resolve-repair-computer-id') ? parseInt(document.getElementById('resolve-repair-computer-id').value) : null;
    const notes = document.getElementById('resolve-repair-notes').value.trim();

    try {
        const res = await fetch('/api/lab/complaints/resolve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                complaint_id: complaintId,
                pc_number: pcNumber,
                computer_id: computerId,
                resolution_notes: notes,
                user_id: currentUser ? currentUser.id : null,
                username: currentUser ? currentUser.username : 'GS_itsupport'
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-resolve-lab-complaint');
            e.target.reset();
            if (currentTab === 'lab_manager') renderLabManagerTab();
            else if (currentTab === 'asset_management') renderAssetManagementTab();
            else renderLabComplaintsTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to resolve complaint: ' + err.message);
    }
}

function openEditLabPC(id, pcNumber, labName, ip, os, processor) {
    if (!['it_admin', 'super_admin'].includes(currentRole)) {
        alert("🔒 Access Restricted: Computer Lab Computer IDs can ONLY be changed by IT Support Administrator.");
        return;
    }
    const editId = document.getElementById('pc-edit-id');
    if (editId) editId.value = id;
    const labInput = document.getElementById('pc-lab-name');
    if (labInput) labInput.value = labName;
    const numInput = document.getElementById('pc-number-val');
    if (numInput) numInput.value = pcNumber;
    const ipInput = document.getElementById('pc-ip-val');
    if (ipInput) ipInput.value = ip || '';
    const osInput = document.getElementById('pc-os-val');
    if (osInput) osInput.value = os || 'Windows 11 Pro';
    const specsInput = document.getElementById('pc-specs-val');
    if (specsInput) specsInput.value = processor || '';

    const titleEl = document.querySelector('#modal-add-lab-pc .modal-title');
    if (titleEl) titleEl.innerText = `🖥️ Change Computer ID: ${pcNumber} (IT Support Only)`;
    openModal('modal-add-lab-pc');
}

async function submitAddLabPC(e) {
    e.preventDefault();
    if (!['it_admin', 'super_admin'].includes(currentRole)) {
        alert("🔒 Access Restricted: Computer Lab Computer IDs and hardware configurations can ONLY be changed by IT Support Administrator.");
        closeModal('modal-add-lab-pc');
        return;
    }
    const editId = document.getElementById('pc-edit-id') ? document.getElementById('pc-edit-id').value : '';
    const labName = document.getElementById('pc-lab-name').value;
    const pcNumber = document.getElementById('pc-number-val').value.trim();
    const ip = document.getElementById('pc-ip-val').value.trim();
    const os = document.getElementById('pc-os-val').value.trim();
    const processor = document.getElementById('pc-specs-val').value.trim();

    try {
        const res = await fetch('/api/lab/computers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                id: editId || null,
                caller_role: currentRole,
                caller_username: currentUser ? currentUser.username : '',
                lab_name: labName,
                pc_number: pcNumber,
                ip_address: ip,
                os: os,
                processor: processor,
                status: 'Working'
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-add-lab-pc');
            if (document.getElementById('pc-edit-id')) document.getElementById('pc-edit-id').value = '';
            e.target.reset();
            renderLabManagerTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert(`❌ Failed to save Computer ID: ${err.message}`);
    }
}

async function submitIssueAccountantSlip(e) {
    e.preventDefault();
    const month = parseInt(document.getElementById('issue-acc-month').value);
    const year = parseInt(document.getElementById('issue-acc-year').value);
    const baseSalary = parseFloat(document.getElementById('issue-acc-base').value);
    const bonus = parseFloat(document.getElementById('issue-acc-bonus').value || 0);
    const bonusTitle = document.getElementById('issue-acc-bonus-title').value.trim();

    try {
        const res = await fetch('/api/payroll/generate_accountant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                month: month,
                year: year,
                base_salary: baseSalary,
                special_bonus: bonus,
                bonus_title: bonusTitle,
                director_name: currentUser ? (currentUser.name || 'Owner (Director) Rajeev Sinha') : 'Owner (Director) Rajeev Sinha'
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`👑 ${data.message}`);
            closeModal('modal-issue-accountant-slip');
            renderPayrollTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to sanction payslip: ' + err.message);
    }
}


// =====================================================================
// CREDENTIAL MANAGEMENT & OWNER EXECUTIVE APPROVAL SYSTEM
// =====================================================================
async function renderCredentialsTab() {
    if (!['it_admin', 'super_admin'].includes(currentRole)) {
        showTab('dashboard');
        return;
    }

    const isOwner = currentUser && (currentUser.username === 'Owner(Directer)' || (currentUser.name && currentUser.name.includes('Rajeev Sinha')));
    const isITAdmin = currentRole === 'it_admin';

    document.getElementById('portal-header-title').innerText = isOwner ? 'Owner Credential & User ID Executive Approval Center' : 'User ID & Password Management Desk (IT Support)';
    document.getElementById('portal-header-desc').innerText = isOwner 
        ? 'Director Authority: Review and approve/reject IT Support credential modifications and new account creations'
        : 'IT Support Administrator: Propose User ID/Password modifications and create new accounts subject to Owner approval';

    try {
        const users = await fetch('/api/users').then(r => r.json());
        siteData.users = users;

        const reqData = await fetch('/api/credentials/requests').then(r => r.json());
        const allRequests = reqData.requests || [];
        const pendingRequests = allRequests.filter(r => r.status === 'Pending Owner Approval');

        const html = `
            <!-- Policy Callout -->
            <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:16px 20px; margin-bottom:20px; color:#1e40af; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div style="display:flex; align-items:center; gap:14px;">
                    <span style="font-size:2rem;">🔐</span>
                    <div>
                        <strong style="font-size:1rem;">Strict Institutional Password & Identity Governance Policy</strong>
                        <div style="font-size:0.84rem; color:#1d4ed8; margin-top:2px; line-height:1.4;">
                            • <strong>Self-service password change is removed from everyone.</strong><br>
                            • <strong>Only IT Support Administrator</strong> can initiate User ID and Password modifications or propose new User IDs.<br>
                            • Every credential modification and new User ID creation strictly requires <strong>Executive Approval by Owner (Director) Rajeev Sinha</strong>.
                        </div>
                    </div>
                </div>
                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <button class="btn btn-success" style="background:#15803d; border-color:#166534; font-weight:700; padding:8px 16px; color:white; display:inline-flex; align-items:center; gap:8px;" onclick="window.location.href='/api/it/export_credentials_excel'">
                        <i class="fas fa-file-excel"></i> 📥 Download Credentials Master (Excel)
                    </button>
                    <button class="btn btn-primary" style="background:#1e3a8a; font-weight:700; padding:8px 16px; display:inline-flex; align-items:center; gap:8px;" onclick="openModal('modal-it-request-create-user')">
                        <i class="fas fa-user-plus"></i> ➕ Propose New User ID
                    </button>
                    <button class="btn btn-danger" style="background:#dc2626; border-color:#b91c1c; font-weight:700; padding:8px 16px;" onclick="confirmCleanTestData()">
                        🧹 Clean All Test Data
                    </button>
                </div>
            </div>

            <!-- OWNER PENDING APPROVAL QUEUE (Prominently displayed to Director) -->
            ${isOwner ? `
                <div class="card" style="margin-bottom:24px; border:2px solid #7c3aed;">
                    <div class="card-header" style="background:#faf5ff; justify-content:space-between; align-items:center;">
                        <div>
                            <span class="card-title" style="color:#6b21a8;"><i class="fas fa-crown"></i> 👑 Director Executive Approval Queue (${pendingRequests.length} Pending)</span>
                            <p style="font-size:0.78rem; color:#7e22ce; margin-top:2px;">Pending credential updates and user creations submitted by IT Support Administrator awaiting your authorization</p>
                        </div>
                        <span class="badge" style="background:${pendingRequests.length > 0 ? '#ef4444' : '#10b981'}; color:white; font-weight:700; padding:5px 12px; border-radius:12px;">
                            ${pendingRequests.length > 0 ? `${pendingRequests.length} Action(s) Required` : 'Queue Clear'}
                        </span>
                    </div>
                    <div class="card-body" style="padding:0; overflow-x:auto;">
                        ${pendingRequests.length === 0 ? `
                            <div style="text-align:center; padding:30px; color:#10b981;">
                                <div style="font-size:2rem; margin-bottom:6px;">✓</div>
                                <strong>No Pending Credential Requests</strong>
                                <p style="font-size:0.8rem; color:#64748b; margin-top:4px;">All User ID and password requests submitted by IT Support have been reviewed.</p>
                            </div>
                        ` : `
                            <table class="data-table" style="font-size:0.83rem;">
                                <thead>
                                    <tr>
                                        <th>Request #</th>
                                        <th>Request Type</th>
                                        <th>Target Identity</th>
                                        <th>Proposed User ID</th>
                                        <th>Proposed Password</th>
                                        <th>Requested By</th>
                                        <th>Reason / Justification</th>
                                        <th>Executive Action</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${pendingRequests.map(r => `
                                        <tr>
                                            <td><code>REQ-${r.id}</code></td>
                                            <td>
                                                <span class="badge" style="background:${r.request_type === 'create_user' ? '#f0fdf4; color:#15803d;' : '#eff6ff; color:#1e40af;'} font-weight:700;">
                                                    ${r.request_type === 'create_user' ? '➕ New User Creation' : '✏️ Credential Change'}
                                                </span>
                                            </td>
                                            <td>
                                                <strong>${r.proposed_name || r.current_name_db || r.target_username || 'Role Account'}</strong>
                                                <div style="font-size:0.72rem; color:#64748b;">Role: <code>${r.proposed_role || r.current_role_db}</code></div>
                                            </td>
                                            <td><code style="font-weight:700; color:#1e3a8a;">${r.proposed_username}</code></td>
                                            <td><code style="font-weight:700; color:#b91c1c;">${r.proposed_password}</code></td>
                                            <td>
                                                <div style="font-weight:700;">${r.requested_by_name || 'IT Support Admin'}</div>
                                                <div style="font-size:0.72rem; color:#64748b;">${r.created_at || 'Recently'}</div>
                                            </td>
                                            <td style="max-width:200px;"><span style="font-size:0.78rem; color:#334155;">${r.reason || '—'}</span></td>
                                            <td>
                                                <div style="display:flex; gap:6px;">
                                                    <button class="btn btn-success btn-sm" style="font-size:0.74rem; padding:4px 10px; background:#16a34a; font-weight:700;" onclick="approveCredentialRequest(${r.id})">
                                                        ✅ Approve & Apply
                                                    </button>
                                                    <button class="btn btn-danger btn-sm" style="font-size:0.74rem; padding:4px 8px; background:#dc2626;" onclick="rejectCredentialRequest(${r.id})">
                                                        ❌ Reject
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    `).join('')}
                                </tbody>
                            </table>
                        `}
                    </div>
                </div>
            ` : ''}

            <!-- ALL SYSTEM ACCOUNTS DIRECTORY -->
            <div class="card" style="margin-bottom:24px;">
                <div class="card-header" style="justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                    <div>
                        <span class="card-title">👥 All System User Accounts (${users.length})</span>
                        <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Select any user to propose a User ID or Password modification</p>
                    </div>
                    <div>
                        <input type="text" id="cred-user-search" placeholder="Search user ID, name, role..." class="form-control" style="padding:6px 12px; width:260px;" onkeyup="filterCredentialsTable()">
                    </div>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    <table class="data-table" id="credentials-table" style="font-size:0.83rem;">
                        <thead>
                            <tr>
                                <th>User / Name</th>
                                <th>Role</th>
                                <th>Current User ID</th>
                                <th>Current Password</th>
                                <th>Email</th>
                                <th>Phone</th>
                                <th>Security Action</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${users.map(u => `
                                <tr>
                                    <td style="display:flex; align-items:center; gap:10px;">
                                        <img src="${u.photo || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=150'}" style="width:34px; height:34px; border-radius:50%; object-fit:cover;">
                                        <div>
                                            <div style="font-weight:700; color:#0f172a;">${u.name || '(Unassigned Role ID)'}</div>
                                            <div style="font-size:0.72rem; color:#64748b;">ID #${u.id}</div>
                                        </div>
                                    </td>
                                    <td>
                                        <span class="cred-role-badge role-${u.user_type}">
                                            ${formatRoleName(u.user_type)}
                                        </span>
                                    </td>
                                    <td>
                                        <span class="pwd-badge" style="color:#1e40af; font-weight:700; font-family:monospace;">${u.username}</span>
                                    </td>
                                    <td>
                                        <div style="display:flex; align-items:center; gap:6px;">
                                            <span class="pwd-badge" id="cred-pwd-${u.id}">••••••••</span>
                                            <button type="button" class="btn-icon" onclick="toggleTablePassword('cred-pwd-${u.id}', '${u.password}', true)" title="Show / Hide Password">
                                                👁️
                                            </button>
                                        </div>
                                    </td>
                                    <td><span style="font-size:0.8rem; color:#475569;">${u.email || '—'}</span></td>
                                    <td><span style="font-size:0.8rem; color:#475569;">${u.phone || '—'}</span></td>
                                    <td>
                                        <div style="display:flex; gap:6px; flex-wrap:wrap;">
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
                                        </div>
                                    </td>
                                </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- CREDENTIAL REQUESTS AUDIT & STATUS TRACKER -->
            <div class="card">
                <div class="card-header" style="justify-content:space-between; align-items:center;">
                    <div>
                        <span class="card-title">📜 Credential Modification Requests Audit Trail (${allRequests.length})</span>
                        <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Complete record of all User ID and Password modifications and Owner approvals</p>
                    </div>
                    <button class="btn btn-outline btn-sm" onclick="renderCredentialsTab()">🔄 Refresh Log</button>
                </div>
                <div class="card-body" style="padding:0; overflow-x:auto;">
                    ${allRequests.length === 0 ? `
                        <div style="text-align:center; padding:30px; color:#64748b;">
                            No credential modification requests on record yet.
                        </div>
                    ` : `
                        <table class="data-table" style="font-size:0.82rem;">
                            <thead>
                                <tr>
                                    <th>Request #</th>
                                    <th>Type</th>
                                    <th>Target / Identity</th>
                                    <th>Proposed User ID</th>
                                    <th>Requested By</th>
                                    <th>Status</th>
                                    <th>Executive Approver</th>
                                    <th>Date / Time</th>
                                </tr>
                            </thead>
                            <tbody>
                                ${allRequests.map(r => {
                                    let statusBadge = `<span class="badge" style="background:#fef3c7; color:#d97706; font-weight:700;">⏳ Pending Owner Approval</span>`;
                                    if (r.status === 'Approved') {
                                        statusBadge = `<span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700;">✅ Approved & Applied</span>`;
                                    } else if (r.status === 'Rejected') {
                                        statusBadge = `<span class="badge" style="background:#fee2e2; color:#dc2626; font-weight:700;">❌ Rejected</span>`;
                                    }

                                    return `
                                        <tr>
                                            <td><code>REQ-${r.id}</code></td>
                                            <td><strong>${r.request_type === 'create_user' ? '➕ Create User' : '✏️ Change Credentials'}</strong></td>
                                            <td><strong>${r.proposed_name || r.current_name_db || r.target_username}</strong></td>
                                            <td><code style="font-weight:700; color:#1e3a8a;">${r.proposed_username}</code></td>
                                            <td>${r.requested_by_name || 'IT Support'}</td>
                                            <td>${statusBadge}</td>
                                            <td>${r.approved_by || '<span style="color:#94a3b8; font-style:italic;">Awaiting Owner</span>'}</td>
                                            <td><span style="font-size:0.74rem; color:#64748b;">${r.created_at || 'Recently'}</span></td>
                                        </tr>
                                    `;
                                }).join('')}
                            </tbody>
                        </table>
                    `}
                </div>
            </div>
        `;

        document.getElementById('portal-tab-content').innerHTML = html;
    } catch (err) {
        document.getElementById('portal-tab-content').innerHTML = `<div style="padding:20px; color:red;">Error loading Credentials tab: ${err.message}</div>`;
    }
}

function filterCredentialsTable() {
    const q = document.getElementById('cred-user-search').value.toLowerCase();
    const rows = document.querySelectorAll('#credentials-table tbody tr');
    rows.forEach(r => {
        r.style.display = r.innerText.toLowerCase().includes(q) ? '' : 'none';
    });
}

function openITSupportChangeCredsModal(userId) {
    const u = (siteData.users || []).find(x => x.id === userId);
    if (!u) {
        alert('User account not found.');
        return;
    }
    document.getElementById('it-cred-user-id').value = u.id;
    document.getElementById('it-cred-new-username').value = u.username;
    document.getElementById('it-cred-new-password').value = '';
    document.getElementById('it-cred-reason').value = '';

    document.getElementById('it-cred-target-info').innerHTML = `
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

    openModal('modal-it-request-change-creds');
}

async function submitITSupportChangeCreds(e) {
    e.preventDefault();
    const userId = parseInt(document.getElementById('it-cred-user-id').value);
    const newUsername = document.getElementById('it-cred-new-username').value.trim();
    const newPassword = document.getElementById('it-cred-new-password').value.trim();
    const reason = document.getElementById('it-cred-reason').value.trim();

    try {
        const res = await fetch('/api/credentials/request_change', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                username: newUsername,
                password: newPassword,
                reason: reason,
                requested_by_id: currentUser ? currentUser.id : null,
                requested_by_name: currentUser ? (currentUser.name || currentUser.username) : 'IT Support Administrator',
                requested_by_username: currentUser ? currentUser.username : 'GS_itsupport',
                role: currentRole
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-it-request-change-creds');
            e.target.reset();
            renderCredentialsTab();
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    } catch (err) {
        alert('Failed to submit credential change: ' + err.message);
    }
}

function handleITCreateUserNameChange(val) {
    const sel = document.getElementById('it-create-gender');
    const hint = document.getElementById('it-create-gender-hint');
    if (!val || !val.trim()) {
        if (sel) {
            sel.disabled = true;
            sel.value = '';
        }
        if (hint) hint.innerHTML = '🔒 Disabled: Role ID has no assigned person name (no gender shown).';
    } else {
        if (sel) sel.disabled = false;
        if (hint) hint.innerHTML = '✅ Enabled: Assigned person gender can now be set (Male / Female).';
    }
}

async function submitITSupportCreateUser(e) {
    e.preventDefault();
    const name = document.getElementById('it-create-name').value.trim();
    const role = document.getElementById('it-create-role').value;
    const genderSel = document.getElementById('it-create-gender');
    const gender = name && genderSel ? genderSel.value : null;
    const username = document.getElementById('it-create-username').value.trim();
    const password = document.getElementById('it-create-password').value.trim();
    const email = document.getElementById('it-create-email').value.trim();
    const phone = document.getElementById('it-create-phone').value.trim();
    const reason = document.getElementById('it-create-reason').value.trim();

    const isCommon = (role === 'common_id') || (document.getElementById('it-create-is-common') ? document.getElementById('it-create-is-common').checked : false);
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
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-it-request-create-user');
            e.target.reset();
            renderCredentialsTab();
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    } catch (err) {
        alert('Failed to submit user creation request: ' + err.message);
    }
}

async function approveCredentialRequest(requestId) {
    const approverName = currentUser ? (currentUser.name || 'Owner (Director) Rajeev Sinha') : 'Owner (Director) Rajeev Sinha';
    try {
        const res = await fetch('/api/credentials/approve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                request_id: requestId,
                name: approverName,
                username: currentUser ? currentUser.username : 'Owner(Directer)'
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`👑 ${data.message}`);
            renderCredentialsTab();
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    } catch (err) {
        alert('Failed to approve request: ' + err.message);
    }
}

async function rejectCredentialRequest(requestId) {
    const reason = prompt('Please enter reason for rejecting this credential request:', 'Declined by Owner (Director) Rajeev Sinha');
    if (!reason) return;

    try {
        const res = await fetch('/api/credentials/reject', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                request_id: requestId,
                rejection_reason: reason,
                name: currentUser ? (currentUser.name || 'Owner (Director) Rajeev Sinha') : 'Owner (Director) Rajeev Sinha'
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✓ ${data.message}`);
            renderCredentialsTab();
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    } catch (err) {
        alert('Failed to reject request: ' + err.message);
    }
}

async function approveStudentAdmission(studentId) {
    const approver = currentUser ? (currentUser.name || currentUser.username) : 'Super Admin';
    try {
        const res = await fetch('/api/students/approve_admission', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_id: studentId,
                approved_by: approver
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            renderStudentsTab();
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    } catch (err) {
        alert('Failed to approve admission: ' + err.message);
    }
}



// =====================================================================
// LAPTOP & COMPUTER ASSET MANAGEMENT SYSTEM (ITAM)
// =====================================================================

window.currentAssetSubTab = window.currentAssetSubTab || 'overview';
window.assetFilterState = {
    search: '',
    deviceType: 'all',
    status: 'all',
    ownership: 'all'
};

async function renderAssetManagementTab() {
    if (!['it_admin', 'super_admin', 'admin'].includes(currentRole)) {
        showTab('dashboard');
        return;
    }

    document.getElementById('portal-header-title').innerText = 'Laptop & Computer IT Asset Management System';
    document.getElementById('portal-header-desc').innerText = 'Institutional Equipment Lifecycle: Inventory, Rentals, Allocations, Tracking, Warranties, Maintenance & Payment Reminders';

    const html = `
        <!-- Main Top Bar & Sub-Navigation -->
        <div style="background:#fff; border:1px solid #e2e8f0; border-radius:12px; padding:16px 20px; margin-bottom:20px; box-shadow:0 1px 3px rgba(0,0,0,0.05);">
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:14px; margin-bottom:14px;">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:2rem; background:#eff6ff; padding:8px 12px; border-radius:10px; border:1px solid #bfdbfe;">💻</span>
                    <div>
                        <h4 style="margin:0; font-weight:800; color:#0f172a; font-size:1.15rem;">Institutional IT Asset & Fleet Management</h4>
                        <div style="font-size:0.8rem; color:#64748b; margin-top:2px;">
                            Active Custodian: <strong style="color:#1e40af;">${currentUser ? (currentUser.name || currentUser.username) : 'IT Support Administrator'}</strong> | Role: <span class="badge" style="background:#0284c7; color:white; font-size:0.7rem;">${formatRoleName(currentRole)}</span>
                        </div>
                    </div>
                </div>
                <div style="display:flex; gap:8px; flex-wrap:wrap;">
                    <button class="btn btn-primary" style="background:#0f172a; font-weight:700; padding:7px 14px; display:inline-flex; align-items:center; gap:6px;" onclick="openModal('modal-add-it-asset')">
                        <i class="fas fa-plus"></i> ➕ Register Asset
                    </button>
                    <button class="btn btn-primary" style="background:#1e3a8a; font-weight:700; padding:7px 14px; display:inline-flex; align-items:center; gap:6px;" onclick="openModalHandoverAsset()">
                        <i class="fas fa-handshake"></i> 🤝 Issue Handover
                    </button>
                    <button class="btn btn-secondary" style="background:#7c3aed; border-color:#6d28d9; color:white; font-weight:700; padding:7px 14px; display:inline-flex; align-items:center; gap:6px;" onclick="openModal('modal-it-add-rental')">
                        <i class="fas fa-file-contract"></i> 🏢 Rental Agreement
                    </button>
                    <button class="btn btn-outline" style="font-weight:700; padding:7px 12px;" onclick="renderAssetManagementTab()">
                        🔄 Refresh Fleet
                    </button>
                </div>
            </div>

            <!-- Sub-Tabs Navigation Pills -->
            <div style="display:flex; gap:6px; flex-wrap:wrap; border-top:1px solid #f1f5f9; padding-top:12px;">
                <button class="btn btn-sm ${window.currentAssetSubTab === 'overview' ? 'btn-primary' : 'btn-outline'}" style="font-weight:700;" onclick="switchAssetSubTab('overview')">
                    📊 Overview & Analytics
                </button>
                <button class="btn btn-sm ${window.currentAssetSubTab === 'inventory' ? 'btn-primary' : 'btn-outline'}" style="font-weight:700;" onclick="switchAssetSubTab('inventory')">
                    💻 Device Inventory
                </button>
                <button class="btn btn-sm ${window.currentAssetSubTab === 'allocations' ? 'btn-primary' : 'btn-outline'}" style="font-weight:700;" onclick="switchAssetSubTab('allocations')">
                    🤝 Handover & Allocations
                </button>
                <button class="btn btn-sm ${window.currentAssetSubTab === 'rentals' ? 'btn-primary' : 'btn-outline'}" style="font-weight:700;" onclick="switchAssetSubTab('rentals')">
                    🏢 Rental Management
                </button>
                <button class="btn btn-sm ${window.currentAssetSubTab === 'payments' ? 'btn-primary' : 'btn-outline'}" style="font-weight:700;" onclick="switchAssetSubTab('payments')">
                    ⏰ Payment Reminders
                </button>
                <button class="btn btn-sm ${window.currentAssetSubTab === 'warranties' ? 'btn-primary' : 'btn-outline'}" style="font-weight:700;" onclick="switchAssetSubTab('warranties')">
                    🛡️ Warranty & AMC
                </button>
                <button class="btn btn-sm ${window.currentAssetSubTab === 'maintenance' ? 'btn-primary' : 'btn-outline'}" style="font-weight:700;" onclick="switchAssetSubTab('maintenance')">
                    🛠️ Service & Maintenance
                </button>
                <button class="btn btn-sm ${window.currentAssetSubTab === 'tracking' ? 'btn-primary' : 'btn-outline'}" style="font-weight:700;" onclick="switchAssetSubTab('tracking')">
                    📜 Asset Tracking Logs
                </button>
                <button class="btn btn-sm ${window.currentAssetSubTab === 'reports' ? 'btn-primary' : 'btn-outline'}" style="font-weight:700;" onclick="switchAssetSubTab('reports')">
                    📑 Reports Center
                </button>
            </div>
        </div>

        <!-- Sub-Tab Content Mount Point -->
        <div id="asset-subtab-container">
            <div style="text-align:center; padding:50px; color:#64748b;">
                <div style="font-size:2rem; margin-bottom:10px;">⏳</div>
                Loading asset management data...
            </div>
        </div>
    `;

    document.getElementById('portal-tab-content').innerHTML = html;
    loadAssetSubTabContent(window.currentAssetSubTab);
}

function switchAssetSubTab(tabKey) {
    window.currentAssetSubTab = tabKey;
    renderAssetManagementTab();
}

async function loadAssetSubTabContent(tabKey) {
    const container = document.getElementById('asset-subtab-container');
    if (!container) return;

    try {
        if (tabKey === 'overview') {
            await renderAssetOverviewSubTab(container);
        } else if (tabKey === 'inventory') {
            await renderAssetInventorySubTab(container);
        } else if (tabKey === 'allocations') {
            await renderAssetAllocationsSubTab(container);
        } else if (tabKey === 'rentals') {
            await renderAssetRentalsSubTab(container);
        } else if (tabKey === 'payments') {
            await renderAssetPaymentsSubTab(container);
        } else if (tabKey === 'warranties') {
            await renderAssetWarrantiesSubTab(container);
        } else if (tabKey === 'maintenance') {
            await renderAssetMaintenanceSubTab(container);
        } else if (tabKey === 'tracking') {
            await renderAssetTrackingSubTab(container);
        } else if (tabKey === 'reports') {
            await renderAssetReportsSubTab(container);
        }
    } catch (err) {
        container.innerHTML = `<div style="padding:30px; color:#dc2626; background:#fef2f2; border:1px solid #fecaca; border-radius:8px;">Error loading module: ${err.message}</div>`;
    }
}

// =====================================================================
// 1. OVERVIEW & ANALYTICS SUB-TAB
// =====================================================================
async function renderAssetOverviewSubTab(container) {
    const analytics = await fetch('/api/it_assets/analytics').then(r => r.json());
    const m = analytics.metrics || {};
    const duePayments = analytics.due_payments || [];
    const expiringWarranties = analytics.expiring_warranties || [];

    const html = `
        <!-- Metrics Row -->
        <div class="metrics-row" style="grid-template-columns:repeat(auto-fit, minmax(200px, 1fr));">
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Total IT Fleet</h5>
                    <h2>${m.total_assets || 0}</h2>
                    <span style="font-size:0.75rem; color:#10b981;">₦${((m.total_asset_value || 0)).toLocaleString()} Valuation</span>
                </div>
                <div class="metric-icon metric-blue">💻</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Laptops</h5>
                    <h2>${m.total_laptops || 0}</h2>
                    <span style="font-size:0.75rem; color:#2563eb;">Portable Hardware</span>
                </div>
                <div class="metric-icon metric-purple">💻</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Desktops & Towers</h5>
                    <h2>${m.total_desktops || 0}</h2>
                    <span style="font-size:0.75rem; color:#64748b;">Workstations & PCs</span>
                </div>
                <div class="metric-icon metric-amber">🖥️</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Allocated to Staff</h5>
                    <h2>${m.total_allocated || 0}</h2>
                    <span style="font-size:0.75rem; color:#3b82f6;">Active Custody</span>
                </div>
                <div class="metric-icon metric-green">🤝</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>In Depot Stock</h5>
                    <h2>${m.total_in_stock || 0}</h2>
                    <span style="font-size:0.75rem; color:#10b981;">Ready to Issue</span>
                </div>
                <div class="metric-icon metric-green">📦</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>On Rental</h5>
                    <h2>${m.total_on_rent || 0}</h2>
                    <span style="font-size:0.75rem; color:#7c3aed;">Leased Hardware</span>
                </div>
                <div class="metric-icon metric-purple">🏢</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>In Repair / Service</h5>
                    <h2>${m.total_in_service || 0}</h2>
                    <span style="font-size:0.75rem; color:#f59e0b;">Diagnostic Depot</span>
                </div>
                <div class="metric-icon metric-red">🛠️</div>
            </div>
            <div class="metric-card">
                <div class="metric-info">
                    <h5>Payment Reminders</h5>
                    <h2>${duePayments.length}</h2>
                    <span style="font-size:0.75rem; color:${duePayments.length > 0 ? '#ef4444' : '#10b981'};">Action Required</span>
                </div>
                <div class="metric-icon metric-red">⏰</div>
            </div>
        </div>

        <!-- URGENT ALERTS BANNER IF PAYMENTS / WARRANTIES PENDING -->
        ${(duePayments.length > 0 || expiringWarranties.length > 0) ? `
            <div style="background:#fff7ed; border:1px solid #fed7aa; border-radius:10px; padding:16px 20px; margin-bottom:24px;">
                <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                    <div>
                        <strong style="color:#c2410c; font-size:0.95rem;"><i class="fas fa-bell"></i> IT Management Action Alerts:</strong>
                        <div style="font-size:0.83rem; color:#9a3412; margin-top:4px;">
                            ${duePayments.length > 0 ? `• <strong>${duePayments.length} Payment Schedule(s)</strong> due for rental leasing or service invoices.<br>` : ''}
                            ${expiringWarranties.length > 0 ? `• <strong>${expiringWarranties.length} Hardware Warranty/AMC Policy</strong> expiring within 30 days.` : ''}
                        </div>
                    </div>
                    <div style="display:flex; gap:8px;">
                        ${duePayments.length > 0 ? `<button class="btn btn-sm" style="background:#ea580c; color:white; font-weight:700;" onclick="switchAssetSubTab('payments')">Review Payments</button>` : ''}
                        ${expiringWarranties.length > 0 ? `<button class="btn btn-sm" style="background:#0284c7; color:white; font-weight:700;" onclick="switchAssetSubTab('warranties')">Review Warranties</button>` : ''}
                    </div>
                </div>
            </div>
        ` : ''}

        <!-- Breakdown Charts & Visual Cards -->
        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(320px, 1fr)); gap:20px; margin-bottom:24px;">
            <!-- Brand Distribution -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">🏷️ Fleet by Brand & Manufacturer</span>
                </div>
                <div class="card-body" style="padding:16px;">
                    ${(analytics.brands || []).map(b => `
                        <div style="margin-bottom:12px;">
                            <div style="display:flex; justify-content:space-between; font-size:0.83rem; margin-bottom:4px;">
                                <strong style="color:#1e293b;">${b.brand}</strong>
                                <span style="color:#64748b;">${b.count} units</span>
                            </div>
                            <div style="background:#f1f5f9; border-radius:6px; height:8px; overflow:hidden;">
                                <div style="background:#2563eb; height:100%; width:${Math.min(100, (b.count / (m.total_assets || 1)) * 100)}%;"></div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <!-- Location Distribution -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">📍 Asset Locations & Deployment</span>
                </div>
                <div class="card-body" style="padding:16px;">
                    ${(analytics.locations || []).map(l => `
                        <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #f1f5f9; font-size:0.83rem;">
                            <span style="color:#334155;">📍 ${l.current_location}</span>
                            <span class="badge" style="background:#e0f2fe; color:#0369a1; font-weight:700;">${l.count} devices</span>
                        </div>
                    `).join('')}
                </div>
            </div>

            <!-- Condition Breakdown -->
            <div class="card">
                <div class="card-header">
                    <span class="card-title">✨ Physical Condition Breakdown</span>
                </div>
                <div class="card-body" style="padding:16px;">
                    ${(analytics.conditions || []).map(c => `
                        <div style="display:flex; justify-content:space-between; align-items:center; padding:8px 0; border-bottom:1px solid #f1f5f9; font-size:0.83rem;">
                            <span style="color:#334155;">${c.condition}</span>
                            <span class="badge" style="background:#f1f5f9; color:#475569; font-weight:700;">${c.count} units</span>
                        </div>
                    `).join('')}
                </div>
            </div>
        </div>

        <!-- Recent Activity Feed -->
        <div class="card">
            <div class="card-header" style="justify-content:space-between; align-items:center;">
                <span class="card-title">📜 Recent Movement, Handover & Service Activity</span>
                <button class="btn btn-outline btn-sm" onclick="switchAssetSubTab('tracking')">View Complete Tracking Log</button>
            </div>
            <div class="card-body" style="padding:0; overflow-x:auto;">
                <table class="data-table" style="font-size:0.82rem;">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Asset</th>
                            <th>Action Type</th>
                            <th>From Location</th>
                            <th>Destination / Custody</th>
                            <th>Performed By</th>
                            <th>Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${(analytics.recent_logs || []).slice(0, 6).map(l => `
                            <tr>
                                <td style="white-space:nowrap; color:#64748b;">${l.timestamp}</td>
                                <td><strong style="color:#1e40af; font-family:monospace;">${l.asset_tag}</strong></td>
                                <td><span class="badge" style="background:#eff6ff; color:#1e40af;">${l.action_type}</span></td>
                                <td style="color:#64748b;">${l.from_location || '—'}</td>
                                <td><strong>${l.to_location || '—'}</strong></td>
                                <td style="color:#475569;">${l.performed_by}</td>
                                <td style="max-width:240px; color:#475569;">${l.details}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// =====================================================================
// 2. DEVICE INVENTORY SUB-TAB
// =====================================================================
async function renderAssetInventorySubTab(container) {
    const q = new URLSearchParams();
    if (window.assetFilterState.search) q.append('search', window.assetFilterState.search);
    if (window.assetFilterState.deviceType !== 'all') q.append('device_type', window.assetFilterState.deviceType);
    if (window.assetFilterState.status !== 'all') q.append('status', window.assetFilterState.status);
    if (window.assetFilterState.ownership !== 'all') q.append('ownership', window.assetFilterState.ownership);

    const data = await fetch(`/api/it_assets?${q.toString()}`).then(r => r.json());
    const assets = data.assets || [];
    const sum = data.summary || {};

    const html = `
        <div class="card">
            <!-- Filter Bar -->
            <div class="card-header" style="flex-wrap:wrap; gap:12px; justify-content:space-between; align-items:center;">
                <div style="display:flex; align-items:center; gap:10px; flex-wrap:wrap; flex:1;">
                    <input type="text" id="asset-search-input" class="form-control" placeholder="🔍 Search Tag, Serial, Brand, Model..." value="${window.assetFilterState.search}" style="max-width:260px; font-size:0.83rem;" oninput="handleAssetFilterChange('search', this.value)">
                    <select class="form-control" style="width:auto; font-size:0.83rem;" onchange="handleAssetFilterChange('deviceType', this.value)">
                        <option value="all" ${window.assetFilterState.deviceType === 'all' ? 'selected' : ''}>All Device Types</option>
                        <option value="Laptop" ${window.assetFilterState.deviceType === 'Laptop' ? 'selected' : ''}>💻 Laptops</option>
                        <option value="Desktop Computer" ${window.assetFilterState.deviceType === 'Desktop Computer' ? 'selected' : ''}>🖥️ Desktops</option>
                        <option value="Workstation" ${window.assetFilterState.deviceType === 'Workstation' ? 'selected' : ''}>🏢 Workstations</option>
                    </select>
                    <select class="form-control" style="width:auto; font-size:0.83rem;" onchange="handleAssetFilterChange('status', this.value)">
                        <option value="all" ${window.assetFilterState.status === 'all' ? 'selected' : ''}>All Statuses</option>
                        <option value="In Stock / Available" ${window.assetFilterState.status === 'In Stock / Available' ? 'selected' : ''}>🟢 In Stock</option>
                        <option value="Allocated to Employee" ${window.assetFilterState.status === 'Allocated to Employee' ? 'selected' : ''}>🔵 Allocated</option>
                        <option value="On Rental" ${window.assetFilterState.status === 'On Rental' ? 'selected' : ''}>🟣 On Rental</option>
                        <option value="In Service / Repair" ${window.assetFilterState.status === 'In Service / Repair' ? 'selected' : ''}>🟠 In Service</option>
                    </select>
                    <select class="form-control" style="width:auto; font-size:0.83rem;" onchange="handleAssetFilterChange('ownership', this.value)">
                        <option value="all" ${window.assetFilterState.ownership === 'all' ? 'selected' : ''}>All Ownership</option>
                        <option value="Owned" ${window.assetFilterState.ownership === 'Owned' ? 'selected' : ''}>Owned</option>
                        <option value="Rented" ${window.assetFilterState.ownership === 'Rented' ? 'selected' : ''}>Rented / Leased</option>
                    </select>
                </div>
                <div style="display:flex; gap:8px;">
                    <button class="btn btn-outline btn-sm" onclick="printFormalAssetReport('inventory')" title="Print formal inventory report">
                        🖨️ Print Sheet
                    </button>
                    <button class="btn btn-outline btn-sm" onclick="exportAssetCSV('inventory')" title="Export CSV for Excel">
                        📊 Export CSV
                    </button>
                    <button class="btn btn-primary btn-sm" style="background:#0f172a; font-weight:700;" onclick="openModal('modal-add-it-asset')">
                        ➕ Add Device
                    </button>
                </div>
            </div>

            <!-- Table of Assets -->
            <div class="card-body" style="padding:0; overflow-x:auto;">
                <table class="data-table" id="it-asset-table" style="font-size:0.82rem;">
                    <thead>
                        <tr>
                            <th>Asset Tag</th>
                            <th>Device & Model</th>
                            <th>Specifications</th>
                            <th>Serial Number</th>
                            <th>Ownership</th>
                            <th>Location / Custody</th>
                            <th>Condition</th>
                            <th>Status</th>
                            <th style="text-align:right;">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${assets.length === 0 ? `
                            <tr><td colspan="9" style="text-align:center; padding:30px; color:#64748b;">No devices matching your search criteria.</td></tr>
                        ` : assets.map(a => {
                            let statusBadge = '<span class="badge" style="background:#dcfce7; color:#15803d;">Available</span>';
                            if (a.status === 'Allocated to Employee') {
                                statusBadge = `<span class="badge" style="background:#dbeafe; color:#1d4ed8;">Allocated (${a.allocated_to || 'Staff'})</span>`;
                            } else if (a.status === 'On Rental') {
                                statusBadge = `<span class="badge" style="background:#f3e8ff; color:#7e22ce;">On Rental (${a.rental_agreement_no || 'Agreement'})</span>`;
                            } else if (a.status === 'In Service / Repair') {
                                statusBadge = '<span class="badge" style="background:#fef3c7; color:#b45309;">In Service</span>';
                            } else if (a.status === 'Decommissioned / Retired') {
                                statusBadge = '<span class="badge" style="background:#f1f5f9; color:#475569;">Retired</span>';
                            }

                            return `
                                <tr>
                                    <td>
                                        <div style="font-family:monospace; font-weight:800; color:#1e40af; cursor:pointer;" onclick="openModalAssetHistory(${a.id})" title="View complete history log">
                                            ${a.asset_tag}
                                        </div>
                                        <div style="font-size:0.7rem; color:#64748b;">ID #${a.id}</div>
                                    </td>
                                    <td>
                                        <div style="font-weight:700; color:#0f172a;">${a.brand} ${a.model_name}</div>
                                        <div style="font-size:0.73rem; color:#64748b;">${a.device_type}</div>
                                    </td>
                                    <td style="max-width:220px;">
                                        <div style="font-size:0.78rem; font-weight:600; color:#334155;">${a.specs_processor || 'Standard CPU'}</div>
                                        <div style="font-size:0.72rem; color:#64748b;">${a.specs_ram || ''} | ${a.specs_storage || ''} | ${a.specs_os || ''}</div>
                                    </td>
                                    <td>
                                        <span class="pwd-badge" style="font-size:0.73rem; color:#334155;">${a.serial_number || '—'}</span>
                                    </td>
                                    <td>
                                        <span style="font-size:0.75rem; color:${a.ownership_type.includes('Rented') ? '#7c3aed' : '#1e3a8a'}; font-weight:600;">
                                            ${a.ownership_type.includes('Rented') ? '🟣 Rented' : '🟢 Owned'}
                                        </span>
                                    </td>
                                    <td>
                                        <div style="font-size:0.8rem; font-weight:600; color:#1e293b;">${a.current_location}</div>
                                    </td>
                                    <td>
                                        <span style="font-size:0.78rem; color:#475569;">${a.condition}</span>
                                    </td>
                                    <td>${statusBadge}</td>
                                    <td style="text-align:right;">
                                        <div style="display:flex; justify-content:flex-end; gap:5px; flex-wrap:wrap;">
                                            ${a.status === 'In Stock / Available' ? `
                                                <button class="btn btn-primary btn-sm" style="font-size:0.7rem; padding:3px 7px; background:#1e3a8a;" onclick="openModalHandoverAsset(${a.id})" title="Issue Handover to Employee">
                                                    🤝 Handover
                                                </button>
                                            ` : ''}
                                            <button class="btn btn-outline btn-sm" style="font-size:0.7rem; padding:3px 7px;" onclick="openModalEditAsset(${a.id})" title="Edit specs / move location">
                                                ✏️ Edit
                                            </button>
                                            <button class="btn btn-outline btn-sm" style="font-size:0.7rem; padding:3px 7px;" onclick="openModalAssetHistory(${a.id})" title="View tracking audit trail">
                                                📜 History
                                            </button>
                                            <button class="btn btn-outline btn-sm" style="font-size:0.7rem; padding:3px 7px; color:#ea580c;" onclick="openModalLogService(${a.id})" title="Dispatch for service">
                                                🛠️ Service
                                            </button>
                                        </div>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

function handleAssetFilterChange(key, val) {
    window.assetFilterState[key] = val;
    const container = document.getElementById('asset-subtab-container');
    renderAssetInventorySubTab(container);
}

// =====================================================================
// 3. EMPLOYEE ALLOCATIONS & HANDOVER SUB-TAB
// =====================================================================
async function renderAssetAllocationsSubTab(container) {
    const data = await fetch('/api/it_allocations').then(r => r.json());
    const allocations = data.allocations || [];
    const sum = data.summary || {};

    const html = `
        <div class="card" style="margin-bottom:20px;">
            <div class="card-header" style="justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <span class="card-title">🤝 Employee Laptop & Computer Handover Ledger (${sum.active || 0} In Custody)</span>
                    <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Track official hardware issuances to faculty and staff with formal Handover Slips</p>
                </div>
                <div style="display:flex; gap:8px;">
                    <button class="btn btn-outline btn-sm" onclick="printFormalAssetReport('allocations')">🖨️ Print Ledger</button>
                    <button class="btn btn-outline btn-sm" onclick="exportAssetCSV('allocations')">📊 Export CSV</button>
                    <button class="btn btn-primary btn-sm" style="background:#1e3a8a; font-weight:700;" onclick="openModalHandoverAsset()">
                        ➕ Issue New Handover
                    </button>
                </div>
            </div>
            <div class="card-body" style="padding:0; overflow-x:auto;">
                <table class="data-table" style="font-size:0.82rem;">
                    <thead>
                        <tr>
                            <th>Handover Slip</th>
                            <th>Device Tag & Model</th>
                            <th>Employee Name</th>
                            <th>Role & Department</th>
                            <th>Handover Date</th>
                            <th>Expected Return</th>
                            <th>Accessories Included</th>
                            <th>Status</th>
                            <th style="text-align:right;">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${allocations.length === 0 ? `
                            <tr><td colspan="9" style="text-align:center; padding:30px; color:#64748b;">No handover records found.</td></tr>
                        ` : allocations.map(alc => {
                            const isOverdue = alc.handover_status === 'Active (With Employee)' && alc.expected_return_date && alc.expected_return_date < (new Date().toISOString().split('T')[0]);
                            return `
                                <tr>
                                    <td>
                                        <strong style="color:#1e40af; font-family:monospace;">${alc.handover_slip_no}</strong>
                                    </td>
                                    <td>
                                        <div style="font-weight:700; color:#0f172a;">${alc.asset_tag}</div>
                                        <div style="font-size:0.73rem; color:#64748b;">${alc.brand} ${alc.model_name}</div>
                                    </td>
                                    <td>
                                        <div style="font-weight:700; color:#1e293b;">${alc.employee_name}</div>
                                    </td>
                                    <td>
                                        <div style="font-size:0.78rem; color:#334155;">${alc.employee_role}</div>
                                        <div style="font-size:0.7rem; color:#64748b;">${alc.department || ''}</div>
                                    </td>
                                    <td>${alc.handover_date}</td>
                                    <td>
                                        <span style="color:${isOverdue ? '#dc2626; font-weight:700;' : '#475569;'}">
                                            ${alc.expected_return_date || 'Permanent / Ongoing'}
                                            ${isOverdue ? ' (Overdue!)' : ''}
                                        </span>
                                    </td>
                                    <td style="max-width:200px; color:#475569; font-size:0.75rem;">${alc.accessories_included || '—'}</td>
                                    <td>
                                        ${alc.handover_status === 'Active (With Employee)' ? 
                                            `<span class="badge" style="background:${isOverdue ? '#fee2e2' : '#eff6ff'}; color:${isOverdue ? '#b91c1c' : '#1d4ed8'}; font-weight:700;">In Custody</span>` : 
                                            `<span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700;">Returned</span>`
                                        }
                                    </td>
                                    <td style="text-align:right;">
                                        <div style="display:flex; justify-content:flex-end; gap:6px;">
                                            <button class="btn btn-outline btn-sm" style="font-size:0.7rem; padding:3px 8px;" onclick="printHandoverSlip(${alc.id})" title="Print formal undertaking slip">
                                                🖨️ Slip
                                            </button>
                                            ${alc.handover_status === 'Active (With Employee)' ? `
                                                <button class="btn btn-success btn-sm" style="font-size:0.7rem; padding:3px 8px; background:#16a34a;" onclick="openModalReturnAsset(${alc.id})">
                                                    📥 Return
                                                </button>
                                            ` : ''}
                                        </div>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// =====================================================================
// 4. RENTAL MANAGEMENT SUB-TAB
// =====================================================================
async function renderAssetRentalsSubTab(container) {
    const data = await fetch('/api/it_rentals').then(r => r.json());
    const rentals = data.rentals || [];
    const sum = data.summary || {};

    const html = `
        <div class="card" style="margin-bottom:20px;">
            <div class="card-header" style="justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <span class="card-title">🏢 Laptop & PC Rental Fleet Agreements (${sum.active || 0} Active)</span>
                    <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Inward and outward hardware leases: terms, billing schedules & deposits</p>
                </div>
                <div style="display:flex; gap:8px;">
                    <button class="btn btn-outline btn-sm" onclick="printFormalAssetReport('rentals')">🖨️ Print Report</button>
                    <button class="btn btn-outline btn-sm" onclick="exportAssetCSV('rentals')">📊 Export CSV</button>
                    <button class="btn btn-primary btn-sm" style="background:#7c3aed; border-color:#6d28d9; font-weight:700;" onclick="openModal('modal-it-add-rental')">
                        ➕ New Agreement
                    </button>
                </div>
            </div>
            <div class="card-body" style="padding:0; overflow-x:auto;">
                <table class="data-table" style="font-size:0.82rem;">
                    <thead>
                        <tr>
                            <th>Agreement #</th>
                            <th>Vendor / Partner</th>
                            <th>Rental Type</th>
                            <th>Linked Equipment</th>
                            <th>Period</th>
                            <th>Billing Rate</th>
                            <th>Next Payment Due</th>
                            <th>Payment Status</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${rentals.length === 0 ? `
                            <tr><td colspan="9" style="text-align:center; padding:30px; color:#64748b;">No rental agreements registered.</td></tr>
                        ` : rentals.map(r => `
                            <tr>
                                <td><strong style="color:#7c3aed; font-family:monospace;">${r.rental_agreement_no}</strong></td>
                                <td>
                                    <div style="font-weight:700; color:#0f172a;">${r.vendor_or_client_name}</div>
                                    <div style="font-size:0.72rem; color:#64748b;">${r.contact_phone || ''}</div>
                                </td>
                                <td><span style="font-size:0.75rem; color:#334155;">${r.rental_type}</span></td>
                                <td>
                                    ${r.asset_tag ? `<strong style="color:#1e40af; font-family:monospace;">${r.asset_tag}</strong> (${r.brand || ''})` : '<span style="color:#64748b;">Fleet Lease</span>'}
                                </td>
                                <td>
                                    <div style="font-size:0.78rem; color:#334155;">${r.start_date} to ${r.end_date}</div>
                                    <div style="font-size:0.7rem; color:#64748b;">Cycle: ${r.billing_cycle}</div>
                                </td>
                                <td>
                                    <strong style="color:#0f172a;">₦${(r.rental_amount || 0).toLocaleString()}</strong>
                                    <div style="font-size:0.7rem; color:#64748b;">Deposit: ₦${(r.deposit_amount || 0).toLocaleString()}</div>
                                </td>
                                <td><strong style="color:#ea580c;">${r.next_payment_due_date || '—'}</strong></td>
                                <td>
                                    <span class="badge" style="background:${r.payment_status === 'Paid in Full' ? '#dcfce7' : '#fef3c7'}; color:${r.payment_status === 'Paid in Full' ? '#15803d' : '#b45309'}; font-weight:700;">
                                        ${r.payment_status}
                                    </span>
                                </td>
                                <td>
                                    <span class="badge" style="background:#f3e8ff; color:#7e22ce; font-weight:700;">${r.rental_status}</span>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// =====================================================================
// 5. PAYMENT REMINDERS SUB-TAB
// =====================================================================
async function renderAssetPaymentsSubTab(container) {
    const data = await fetch('/api/it_payments').then(r => r.json());
    const payments = data.payments || [];
    const sum = data.summary || {};

    const html = `
        <div class="card" style="margin-bottom:20px;">
            <div class="card-header" style="justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <span class="card-title">⏰ Hardware Payment Reminders & Schedules (${sum.upcoming || 0} Pending)</span>
                    <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Track rental installments, AMC renewals, and hardware maintenance bills</p>
                </div>
                <div style="display:flex; gap:8px;">
                    <button class="btn btn-primary btn-sm" style="background:#059669; font-weight:700;" onclick="openModalAddPaymentReminder()">
                        ➕ Schedule Payment
                    </button>
                </div>
            </div>
            <div class="card-body" style="padding:0; overflow-x:auto;">
                <table class="data-table" style="font-size:0.82rem;">
                    <thead>
                        <tr>
                            <th>Ref #</th>
                            <th>Category</th>
                            <th>Payee / Vendor</th>
                            <th>Amount (₦)</th>
                            <th>Due Date</th>
                            <th>Status</th>
                            <th>Payment Settlement</th>
                            <th style="text-align:right;">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${payments.length === 0 ? `
                            <tr><td colspan="8" style="text-align:center; padding:30px; color:#64748b;">No payment reminders scheduled.</td></tr>
                        ` : payments.map(p => {
                            let badge = '<span class="badge" style="background:#dbeafe; color:#1d4ed8; font-weight:700;">Upcoming</span>';
                            if (p.calculated_status === 'Overdue') {
                                badge = '<span class="badge" style="background:#fee2e2; color:#b91c1c; font-weight:700;">⚠️ Overdue</span>';
                            } else if (p.calculated_status === 'Due Today') {
                                badge = '<span class="badge" style="background:#fef3c7; color:#b45309; font-weight:700;">🚨 Due Today</span>';
                            } else if (p.calculated_status === 'Paid') {
                                badge = '<span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700;">✓ Paid</span>';
                            }

                            return `
                                <tr>
                                    <td><strong style="color:#0f172a; font-family:monospace;">${p.ref_no}</strong></td>
                                    <td><span style="font-weight:600; color:#334155;">${p.payment_category}</span></td>
                                    <td><strong>${p.vendor_name}</strong></td>
                                    <td><strong style="font-size:0.9rem; color:#0f172a;">₦${(p.amount || 0).toLocaleString()}</strong></td>
                                    <td>
                                        <strong style="color:${p.calculated_status === 'Overdue' ? '#dc2626;' : '#334155;'}">${p.due_date}</strong>
                                    </td>
                                    <td>${badge}</td>
                                    <td>
                                        ${p.payment_status === 'Paid' ? `
                                            <div style="font-size:0.75rem; color:#16a34a; font-weight:600;">Paid on ${p.paid_date}</div>
                                            <div style="font-size:0.7rem; color:#64748b;">Ref: ${p.transaction_ref || p.payment_method}</div>
                                        ` : '<span style="color:#94a3b8;">Pending Settlement</span>'}
                                    </td>
                                    <td style="text-align:right;">
                                        <div style="display:flex; justify-content:flex-end; gap:6px;">
                                            ${p.payment_status !== 'Paid' ? `
                                                <button class="btn btn-outline btn-sm" style="font-size:0.7rem; padding:3px 8px; color:#ea580c; border-color:#fdba74;" onclick="sendPaymentReminder(${p.id})">
                                                    🔔 Alert Bursar
                                                </button>
                                                <button class="btn btn-success btn-sm" style="font-size:0.7rem; padding:3px 8px; background:#059669;" onclick="openModalRecordPayment(${p.id})">
                                                    💳 Settle
                                                </button>
                                            ` : `
                                                <span style="font-size:0.75rem; color:#15803d; font-weight:700;">Settled</span>
                                            `}
                                        </div>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// =====================================================================
// 6. WARRANTY & AMC SUB-TAB
// =====================================================================
async function renderAssetWarrantiesSubTab(container) {
    const data = await fetch('/api/it_warranties').then(r => r.json());
    const warranties = data.warranties || [];
    const sum = data.summary || {};

    const html = `
        <div class="card" style="margin-bottom:20px;">
            <div class="card-header" style="justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <span class="card-title">🛡️ Hardware Warranty & AMC Management (${sum.active || 0} Active Coverage)</span>
                    <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">OEM Standard Warranties, Extended AMC & Accidental Damage Protection Tracking</p>
                </div>
                <div style="display:flex; gap:8px;">
                    <button class="btn btn-outline btn-sm" onclick="printFormalAssetReport('warranties')">🖨️ Print Schedule</button>
                    <button class="btn btn-primary btn-sm" style="background:#0284c7; font-weight:700;" onclick="openModalAddWarranty()">
                        ➕ Register Warranty / AMC
                    </button>
                </div>
            </div>
            <div class="card-body" style="padding:0; overflow-x:auto;">
                <table class="data-table" style="font-size:0.82rem;">
                    <thead>
                        <tr>
                            <th>Equipment Tag</th>
                            <th>Provider & Policy #</th>
                            <th>Coverage Type</th>
                            <th>Validity Period</th>
                            <th>Days Remaining</th>
                            <th>Status</th>
                            <th>Support Contact</th>
                            <th style="text-align:right;">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${warranties.length === 0 ? `
                            <tr><td colspan="8" style="text-align:center; padding:30px; color:#64748b;">No warranties registered.</td></tr>
                        ` : warranties.map(w => {
                            let badge = '<span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700;">Active</span>';
                            if (w.calculated_status.includes('Expiring Soon')) {
                                badge = '<span class="badge" style="background:#fef3c7; color:#b45309; font-weight:700;">⚠️ Expiring Soon</span>';
                            } else if (w.calculated_status === 'Expired') {
                                badge = '<span class="badge" style="background:#fee2e2; color:#b91c1c; font-weight:700;">Expired</span>';
                            }

                            return `
                                <tr>
                                    <td>
                                        <strong style="color:#1e40af; font-family:monospace;">${w.asset_tag}</strong>
                                        <div style="font-size:0.73rem; color:#64748b;">${w.brand} ${w.model_name}</div>
                                    </td>
                                    <td>
                                        <div style="font-weight:700; color:#0f172a;">${w.provider_name}</div>
                                        <span class="pwd-badge" style="font-size:0.72rem;">${w.policy_number}</span>
                                    </td>
                                    <td><span style="font-size:0.75rem; color:#334155;">${w.warranty_type}</span></td>
                                    <td>
                                        <div style="font-size:0.78rem; color:#334155;">${w.start_date} to ${w.end_date}</div>
                                    </td>
                                    <td>
                                        <strong style="color:${(w.days_remaining || 0) <= 30 ? '#dc2626;' : '#10b981;'}">
                                            ${(w.days_remaining || 0) < 0 ? '0 (Expired)' : `${w.days_remaining} Days`}
                                        </strong>
                                    </td>
                                    <td>${badge}</td>
                                    <td style="font-size:0.75rem; color:#475569;">${w.support_contact || '—'}</td>
                                    <td style="text-align:right;">
                                        <button class="btn btn-outline btn-sm" style="font-size:0.7rem; padding:3px 8px; color:#0284c7;" onclick="logWarrantyClaim(${w.id})">
                                            📞 Log Claim
                                        </button>
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// =====================================================================
// 7. MAINTENANCE & SERVICE TRACKING SUB-TAB
// =====================================================================
async function renderAssetMaintenanceSubTab(container) {
    const data = await fetch('/api/it_maintenance').then(r => r.json());
    const tickets = data.tickets || [];
    const sum = data.summary || {};

    const html = `
        <div class="card" style="margin-bottom:20px;">
            <div class="card-header" style="justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <span class="card-title">🛠️ Hardware Maintenance & Service Tracking (${sum.in_repair || 0} In Service)</span>
                    <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Authorized repair tickets, diagnostics, technician assignments & parts replacement</p>
                </div>
                <div style="display:flex; gap:8px;">
                    <button class="btn btn-outline btn-sm" onclick="printFormalAssetReport('maintenance')">🖨️ Print Service Log</button>
                    <button class="btn btn-primary btn-sm" style="background:#ea580c; font-weight:700;" onclick="openModalLogService()">
                        ➕ Open Service Ticket
                    </button>
                </div>
            </div>
            <div class="card-body" style="padding:0; overflow-x:auto;">
                <table class="data-table" style="font-size:0.82rem;">
                    <thead>
                        <tr>
                            <th>Ticket #</th>
                            <th>Equipment Tag</th>
                            <th>Service Category</th>
                            <th>Reported Defect</th>
                            <th>Service Center / Tech</th>
                            <th>Start Date</th>
                            <th>Repair Cost</th>
                            <th>Status</th>
                            <th style="text-align:right;">Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${tickets.length === 0 ? `
                            <tr><td colspan="9" style="text-align:center; padding:30px; color:#64748b;">No maintenance tickets found.</td></tr>
                        ` : tickets.map(t => {
                            let badge = '<span class="badge" style="background:#fef3c7; color:#b45309; font-weight:700;">In Repair</span>';
                            if (t.service_status === 'Completed & Tested') {
                                badge = '<span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700;">✓ Completed</span>';
                            }

                            return `
                                <tr>
                                    <td><strong style="color:#ea580c; font-family:monospace;">${t.service_ticket_no}</strong></td>
                                    <td>
                                        <strong style="color:#1e40af; font-family:monospace;">${t.asset_tag}</strong>
                                        <div style="font-size:0.73rem; color:#64748b;">${t.brand} ${t.model_name}</div>
                                    </td>
                                    <td><span style="font-weight:600; color:#334155;">${t.service_type}</span></td>
                                    <td style="max-width:200px; color:#475569; font-size:0.75rem;">${t.reported_issue}</td>
                                    <td>
                                        <div style="font-size:0.78rem; font-weight:600; color:#0f172a;">${t.service_center_or_vendor}</div>
                                        <div style="font-size:0.7rem; color:#64748b;">${t.technician_name || ''}</div>
                                    </td>
                                    <td>${t.start_date}</td>
                                    <td>
                                        <strong>₦${(t.repair_cost || 0).toLocaleString()}</strong>
                                        <div style="font-size:0.7rem; color:${t.warranty_claim_covered ? '#15803d' : '#ea580c'}; font-weight:600;">
                                            ${t.warranty_claim_covered ? '🛡️ Under Warranty' : 'Institutional Bill'}
                                        </div>
                                    </td>
                                    <td>${badge}</td>
                                    <td style="text-align:right;">
                                        ${t.service_status !== 'Completed & Tested' ? `
                                            <button class="btn btn-success btn-sm" style="font-size:0.7rem; padding:3px 8px; background:#16a34a;" onclick="openModalCompleteService(${t.id})">
                                                ✅ Mark Fixed
                                            </button>
                                        ` : `
                                            <span style="font-size:0.75rem; color:#15803d; font-weight:700;">Tested & Restored</span>
                                        `}
                                    </td>
                                </tr>
                            `;
                        }).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// =====================================================================
// 8. ASSET TRACKING LOGS SUB-TAB
// =====================================================================
async function renderAssetTrackingSubTab(container) {
    const analytics = await fetch('/api/it_assets/analytics').then(r => r.json());
    const logs = analytics.recent_logs || [];

    const html = `
        <div class="card" style="margin-bottom:20px;">
            <div class="card-header" style="justify-content:space-between; align-items:center;">
                <div>
                    <span class="card-title">📜 Real-Time Equipment Location & Custody Movement Ledger</span>
                    <p style="font-size:0.78rem; color:#64748b; margin-top:2px;">Complete immutable audit trail of hardware dispatch, relocation, and handover events</p>
                </div>
            </div>
            <div class="card-body" style="padding:0; overflow-x:auto;">
                <table class="data-table" style="font-size:0.82rem;">
                    <thead>
                        <tr>
                            <th>Timestamp</th>
                            <th>Asset Tag</th>
                            <th>Device Model</th>
                            <th>Action Type</th>
                            <th>Origin Location</th>
                            <th>Destination / Custodian</th>
                            <th>Authorizing Officer</th>
                            <th>Audit Details</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${logs.length === 0 ? `
                            <tr><td colspan="8" style="text-align:center; padding:30px; color:#64748b;">No tracking events recorded yet.</td></tr>
                        ` : logs.map(l => `
                            <tr>
                                <td style="white-space:nowrap; color:#64748b;">${l.timestamp}</td>
                                <td><strong style="color:#1e40af; font-family:monospace;">${l.asset_tag}</strong></td>
                                <td style="color:#334155;">${l.model_name || '—'}</td>
                                <td><span class="badge" style="background:#eff6ff; color:#1e40af; font-weight:700;">${l.action_type}</span></td>
                                <td style="color:#64748b;">${l.from_location || '—'}</td>
                                <td><strong style="color:#0f172a;">${l.to_location || '—'}</strong></td>
                                <td style="color:#334155;">${l.performed_by}</td>
                                <td style="color:#475569; max-width:280px;">${l.details}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// =====================================================================
// 9. REPORTS & ANALYTICS CENTER SUB-TAB
// =====================================================================
async function renderAssetReportsSubTab(container) {
    const html = `
        <div style="margin-bottom:20px;">
            <div style="background:#eff6ff; border:1px solid #bfdbfe; border-radius:10px; padding:16px 20px; color:#1e40af; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <strong style="font-size:1rem;"><i class="fas fa-file-invoice"></i> Greenland School IT Asset Reports & Audit Center</strong>
                    <div style="font-size:0.83rem; color:#1d4ed8; margin-top:2px;">
                        Generate formal print-ready administrative reports with institutional letterhead, serial numbers, and sign-off blocks.
                    </div>
                </div>
            </div>
        </div>

        <div style="display:grid; grid-template-columns:repeat(auto-fit, minmax(320px, 1fr)); gap:20px;">
            <!-- Report 1: Master Inventory -->
            <div class="card">
                <div class="card-header" style="background:#f8fafc;">
                    <span class="card-title">🖨️ 1. Master Equipment Fleet Inventory Sheet</span>
                </div>
                <div class="card-body" style="padding:16px;">
                    <p style="font-size:0.82rem; color:#64748b; margin-bottom:16px;">
                        Full asset register of all institutionally owned and leased laptops, desktops, and workstations with specifications, purchase cost, and condition.
                    </p>
                    <div style="display:flex; gap:10px;">
                        <button class="btn btn-primary btn-sm" style="flex:1; background:#0f172a; font-weight:700;" onclick="printFormalAssetReport('inventory')">
                            🖨️ Print Report
                        </button>
                        <button class="btn btn-outline btn-sm" style="flex:1;" onclick="exportAssetCSV('inventory')">
                            📊 Export CSV
                        </button>
                    </div>
                </div>
            </div>

            <!-- Report 2: Allocations Ledger -->
            <div class="card">
                <div class="card-header" style="background:#f8fafc;">
                    <span class="card-title">🖨️ 2. Employee Handover & Custody Ledger</span>
                </div>
                <div class="card-body" style="padding:16px;">
                    <p style="font-size:0.82rem; color:#64748b; margin-bottom:16px;">
                        Complete roster of all hardware issued to faculty members, administrators, and teachers with handover dates, accessories, and return statuses.
                    </p>
                    <div style="display:flex; gap:10px;">
                        <button class="btn btn-primary btn-sm" style="flex:1; background:#1e3a8a; font-weight:700;" onclick="printFormalAssetReport('allocations')">
                            🖨️ Print Report
                        </button>
                        <button class="btn btn-outline btn-sm" style="flex:1;" onclick="exportAssetCSV('allocations')">
                            📊 Export CSV
                        </button>
                    </div>
                </div>
            </div>

            <!-- Report 3: Rental Fleet Statement -->
            <div class="card">
                <div class="card-header" style="background:#f8fafc;">
                    <span class="card-title">🖨️ 3. Rental Fleet & Financial Liabilities</span>
                </div>
                <div class="card-body" style="padding:16px;">
                    <p style="font-size:0.82rem; color:#64748b; margin-bottom:16px;">
                        Audit statement of all hardware rental agreements, leased equipment, monthly rates, deposits, and payment schedule obligations.
                    </p>
                    <div style="display:flex; gap:10px;">
                        <button class="btn btn-primary btn-sm" style="flex:1; background:#7c3aed; font-weight:700;" onclick="printFormalAssetReport('rentals')">
                            🖨️ Print Report
                        </button>
                        <button class="btn btn-outline btn-sm" style="flex:1;" onclick="exportAssetCSV('rentals')">
                            📊 Export CSV
                        </button>
                    </div>
                </div>
            </div>

            <!-- Report 4: Service History -->
            <div class="card">
                <div class="card-header" style="background:#f8fafc;">
                    <span class="card-title">🖨️ 4. Maintenance & Service Expenditure Log</span>
                </div>
                <div class="card-body" style="padding:16px;">
                    <p style="font-size:0.82rem; color:#64748b; margin-bottom:16px;">
                        Detailed maintenance and repair history: defects reported, service centers utilized, repair costs, and warranty claim recoveries.
                    </p>
                    <div style="display:flex; gap:10px;">
                        <button class="btn btn-primary btn-sm" style="flex:1; background:#ea580c; font-weight:700;" onclick="printFormalAssetReport('maintenance')">
                            🖨️ Print Report
                        </button>
                        <button class="btn btn-outline btn-sm" style="flex:1;" onclick="exportAssetCSV('maintenance')">
                            📊 Export CSV
                        </button>
                    </div>
                </div>
            </div>

            <!-- Report 5: Warranty Schedule -->
            <div class="card">
                <div class="card-header" style="background:#f8fafc;">
                    <span class="card-title">🖨️ 5. Warranty & AMC Expiration Schedule</span>
                </div>
                <div class="card-body" style="padding:16px;">
                    <p style="font-size:0.82rem; color:#64748b; margin-bottom:16px;">
                        Hardware warranty policy expiration matrix, AMC coverage timeline, and pending renewal dates for school leadership review.
                    </p>
                    <div style="display:flex; gap:10px;">
                        <button class="btn btn-primary btn-sm" style="flex:1; background:#0284c7; font-weight:700;" onclick="printFormalAssetReport('warranties')">
                            🖨️ Print Report
                        </button>
                        <button class="btn btn-outline btn-sm" style="flex:1;" onclick="exportAssetCSV('warranties')">
                            📊 Export CSV
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    container.innerHTML = html;
}

// =====================================================================
// MODAL ACTIONS & EVENT HANDLERS
// =====================================================================

function handleDeviceTypeChange(val) {
    const osSel = document.getElementById('asset-new-os');
    if (!osSel) return;
    if (val === 'Laptop' || val === 'Desktop Computer' || val === 'Workstation') {
        osSel.value = 'Windows 11 Pro';
    }
}

async function submitCreateITAsset(e) {
    e.preventDefault();
    const payload = {
        device_type: document.getElementById('asset-new-type').value,
        brand: document.getElementById('asset-new-brand').value,
        model_name: document.getElementById('asset-new-model').value.trim(),
        serial_number: document.getElementById('asset-new-serial').value.trim(),
        specs_processor: document.getElementById('asset-new-cpu').value.trim(),
        specs_ram: document.getElementById('asset-new-ram').value.trim(),
        specs_storage: document.getElementById('asset-new-storage').value.trim(),
        specs_os: document.getElementById('asset-new-os').value,
        ownership_type: document.getElementById('asset-new-ownership').value,
        condition: document.getElementById('asset-new-condition').value,
        current_location: document.getElementById('asset-new-location').value.trim(),
        purchase_date: document.getElementById('asset-new-purchase-date').value,
        purchase_cost: document.getElementById('asset-new-purchase-cost').value || 0,
        notes: document.getElementById('asset-new-notes').value.trim(),
        created_by: currentUser ? (currentUser.name || currentUser.username) : 'IT Support Administrator'
    };

    try {
        const res = await fetch('/api/it_assets/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-add-it-asset');
            e.target.reset();
            renderAssetManagementTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to register asset: ' + err.message);
    }
}

async function openModalEditAsset(assetId) {
    try {
        const data = await fetch(`/api/it_assets/history?asset_id=${assetId}`).then(r => r.json());
        const a = data.asset;
        if (!a) return;

        document.getElementById('edit-asset-id').value = a.id;
        document.getElementById('edit-asset-header-tag').innerText = `Asset Tag: ${a.asset_tag} | S/N: ${a.serial_number || 'N/A'}`;
        document.getElementById('edit-asset-brand').value = a.brand;
        document.getElementById('edit-asset-model').value = a.model_name;
        document.getElementById('edit-asset-status').value = a.status;
        document.getElementById('edit-asset-condition').value = a.condition;
        document.getElementById('edit-asset-location').value = a.current_location;
        document.getElementById('edit-asset-cpu').value = a.specs_processor || '';
        document.getElementById('edit-asset-ram-storage').value = `${a.specs_ram || ''} / ${a.specs_storage || ''}`;
        document.getElementById('edit-asset-notes').value = a.notes || '';

        openModal('modal-edit-it-asset');
    } catch (err) {
        alert('Failed to load asset details: ' + err.message);
    }
}

async function submitUpdateITAsset(e) {
    e.preventDefault();
    const assetId = document.getElementById('edit-asset-id').value;
    const payload = {
        id: assetId,
        brand: document.getElementById('edit-asset-brand').value.trim(),
        model_name: document.getElementById('edit-asset-model').value.trim(),
        status: document.getElementById('edit-asset-status').value,
        condition: document.getElementById('edit-asset-condition').value,
        current_location: document.getElementById('edit-asset-location').value.trim(),
        specs_processor: document.getElementById('edit-asset-cpu').value.trim(),
        notes: document.getElementById('edit-asset-notes').value.trim(),
        updated_by: currentUser ? (currentUser.name || currentUser.username) : 'IT Support Administrator'
    };

    try {
        const res = await fetch('/api/it_assets/update', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-edit-it-asset');
            renderAssetManagementTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to update asset: ' + err.message);
    }
}

async function openModalAssetHistory(assetId) {
    try {
        const data = await fetch(`/api/it_assets/history?asset_id=${assetId}`).then(r => r.json());
        const a = data.asset;
        const logs = data.logs || [];
        const alc = data.allocations || [];
        const svc = data.services || [];
        const war = data.warranties || [];

        document.getElementById('history-asset-header').innerText = `Tag: ${a.asset_tag} | Model: ${a.brand} ${a.model_name} | S/N: ${a.serial_number || 'N/A'}`;
        document.getElementById('history-asset-card').innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px;">
                <div>
                    <h4 style="margin:0; color:#0f172a; font-weight:800;">${a.brand} ${a.model_name} (${a.device_type})</h4>
                    <div style="font-size:0.8rem; color:#64748b; margin-top:3px;">
                        Specs: <strong>${a.specs_processor || ''} | ${a.specs_ram || ''} | ${a.specs_storage || ''}</strong>
                    </div>
                </div>
                <div>
                    <span class="badge" style="background:#eff6ff; color:#1e40af; font-weight:700; font-size:0.8rem;">📍 Location: ${a.current_location}</span>
                    <span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700; font-size:0.8rem;">Status: ${a.status}</span>
                </div>
            </div>
        `;

        if (logs.length === 0) {
            document.getElementById('history-timeline-content').innerHTML = '<div style="color:#64748b; padding:20px; text-align:center;">No tracking events recorded yet.</div>';
        } else {
            document.getElementById('history-timeline-content').innerHTML = `
                <div style="border-left:2px solid #cbd5e1; margin-left:14px; padding-left:20px; display:flex; flex-direction:column; gap:16px;">
                    ${logs.map(l => `
                        <div style="position:relative;">
                            <div style="position:absolute; left:-27px; top:2px; width:12px; height:12px; border-radius:50%; background:#2563eb; border:2px solid #fff;"></div>
                            <div style="font-size:0.75rem; color:#64748b;">${l.timestamp}</div>
                            <div style="font-weight:700; font-size:0.88rem; color:#0f172a; margin-top:1px;">${l.action_type}</div>
                            <div style="font-size:0.8rem; color:#334155; margin-top:2px;">
                                <strong>${l.from_location || '—'}</strong> ➔ <strong>${l.to_location || '—'}</strong> (Custodian: ${l.assigned_to || 'None'})
                            </div>
                            <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">
                                <em>"${l.details}"</em> — By: <strong>${l.performed_by}</strong>
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        openModal('modal-it-asset-history');
    } catch (err) {
        alert('Failed to load asset history: ' + err.message);
    }
}

async function openModalHandoverAsset(preferredAssetId) {
    try {
        const assetsData = await fetch('/api/it_assets').then(r => r.json());
        const assets = assetsData.assets || [];
        const availableAssets = assets.filter(a => a.status === 'In Stock / Available' || a.id === preferredAssetId);

        const assetSel = document.getElementById('handover-asset-id');
        assetSel.innerHTML = availableAssets.map(a => `
            <option value="${a.id}" ${a.id === preferredAssetId ? 'selected' : ''}>
                ${a.asset_tag} — ${a.brand} ${a.model_name} (${a.device_type})
            </option>
        `).join('');

        if (availableAssets.length === 0) {
            alert('⚠️ No available devices in stock! Please add devices to inventory or return allocated units first.');
            return;
        }

        const users = await fetch('/api/users').then(r => r.json());
        siteData.users = users;
        const empSel = document.getElementById('handover-employee-id');
        empSel.innerHTML = `
            <option value="">— Select Registered Faculty / Employee —</option>
            ${users.map(u => `
                <option value="${u.id}" data-name="${u.name || u.username}" data-role="${u.user_type}">
                    ${u.name || u.username} (${formatRoleName(u.user_type)}) — ${u.username}
                </option>
            `).join('')}
        `;

        document.getElementById('handover-date').value = new Date().toISOString().split('T')[0];
        openModal('modal-it-handover-asset');
    } catch (err) {
        alert('Failed to prepare handover form: ' + err.message);
    }
}

function handleHandoverEmployeeSelect(sel) {
    const opt = sel.options[sel.selectedIndex];
    if (!opt || !opt.value) return;
    document.getElementById('handover-employee-name').value = opt.dataset.name || '';
    document.getElementById('handover-employee-role').value = formatRoleName(opt.dataset.role || 'Staff');
}

async function submitHandoverITAsset(e) {
    e.preventDefault();
    const payload = {
        asset_id: parseInt(document.getElementById('handover-asset-id').value),
        employee_id: parseInt(document.getElementById('handover-employee-id').value) || null,
        employee_name: document.getElementById('handover-employee-name').value.trim(),
        employee_role: document.getElementById('handover-employee-role').value.trim(),
        department: document.getElementById('handover-department').value.trim(),
        handover_date: document.getElementById('handover-date').value,
        expected_return_date: document.getElementById('handover-expected-return').value || null,
        handover_condition: document.getElementById('handover-condition').value,
        accessories_included: document.getElementById('handover-accessories').value.trim(),
        handover_notes: document.getElementById('handover-notes').value.trim(),
        handover_by: currentUser ? (currentUser.name || currentUser.username) : 'IT Support Administrator'
    };

    try {
        const res = await fetch('/api/it_allocations/handover', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-it-handover-asset');
            renderAssetManagementTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to complete handover: ' + err.message);
    }
}

async function openModalReturnAsset(allocationId) {
    try {
        const data = await fetch('/api/it_allocations').then(r => r.json());
        const alc = (data.allocations || []).find(x => x.id === allocationId);
        if (!alc) return;

        document.getElementById('return-allocation-id').value = alc.id;
        document.getElementById('return-asset-header-tag').innerText = `Return Equipment: ${alc.asset_tag} (${alc.brand} ${alc.model_name})`;
        document.getElementById('return-allocation-info').innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <strong>Custodian: ${alc.employee_name}</strong> (${alc.employee_role})
                    <div style="font-size:0.75rem; color:#64748b; margin-top:2px;">Handover Slip: <code>${alc.handover_slip_no}</code> | Handed over on: ${alc.handover_date}</div>
                </div>
                <span class="badge" style="background:#eff6ff; color:#1e40af; font-weight:700;">${alc.asset_tag}</span>
            </div>
        `;

        openModal('modal-it-return-asset');
    } catch (err) {
        alert('Failed to load return details: ' + err.message);
    }
}

async function submitReturnITAsset(e) {
    e.preventDefault();
    const payload = {
        allocation_id: parseInt(document.getElementById('return-allocation-id').value),
        return_condition: document.getElementById('return-condition').value,
        return_verified_by: currentUser ? (currentUser.name || currentUser.username) : 'IT Support Administrator',
        return_notes: document.getElementById('return-notes').value.trim()
    };

    try {
        const res = await fetch('/api/it_allocations/return', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-it-return-asset');
            renderAssetManagementTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to process return: ' + err.message);
    }
}

async function submitCreateITRental(e) {
    e.preventDefault();
    const payload = {
        rental_type: document.getElementById('rental-type').value,
        asset_id: parseInt(document.getElementById('rental-asset-id').value) || null,
        vendor_or_client_name: document.getElementById('rental-vendor-name').value.trim(),
        contact_phone: document.getElementById('rental-contact').value.trim(),
        start_date: document.getElementById('rental-start-date').value,
        end_date: document.getElementById('rental-end-date').value,
        billing_cycle: document.getElementById('rental-billing-cycle').value,
        rental_amount: parseFloat(document.getElementById('rental-amount').value || 0),
        deposit_amount: parseFloat(document.getElementById('rental-deposit').value || 0),
        next_payment_due_date: document.getElementById('rental-next-due').value,
        terms_notes: document.getElementById('rental-terms').value.trim()
    };

    try {
        const res = await fetch('/api/it_rentals/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-it-add-rental');
            renderAssetManagementTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to register rental: ' + err.message);
    }
}

async function openModalRecordPayment(paymentId) {
    try {
        const data = await fetch('/api/it_payments').then(r => r.json());
        const p = (data.payments || []).find(x => x.id === paymentId);
        if (!p) return;

        document.getElementById('pay-record-id').value = p.id;
        document.getElementById('pay-record-date').value = new Date().toISOString().split('T')[0];
        document.getElementById('pay-record-info').innerHTML = `
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <strong style="color:#0f172a; font-size:0.95rem;">${p.vendor_name}</strong>
                    <div style="font-size:0.75rem; color:#64748b;">Ref: <code>${p.ref_no}</code> | Category: <strong>${p.payment_category}</strong></div>
                </div>
                <div style="text-align:right;">
                    <div style="font-size:1.1rem; font-weight:800; color:#059669;">₦${(p.amount || 0).toLocaleString()}</div>
                    <div style="font-size:0.72rem; color:#dc2626; font-weight:700;">Due: ${p.due_date}</div>
                </div>
            </div>
        `;
        openModal('modal-it-record-payment');
    } catch (err) {
        alert('Failed to load payment: ' + err.message);
    }
}

async function submitRecordITPayment(e) {
    e.preventDefault();
    const payload = {
        payment_id: parseInt(document.getElementById('pay-record-id').value),
        paid_date: document.getElementById('pay-record-date').value,
        payment_method: document.getElementById('pay-record-method').value,
        transaction_ref: document.getElementById('pay-record-txref').value.trim(),
        notes: document.getElementById('pay-record-notes').value.trim()
    };

    try {
        const res = await fetch('/api/it_payments/record', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-it-record-payment');
            renderAssetManagementTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to record payment: ' + err.message);
    }
}

async function sendPaymentReminder(paymentId) {
    try {
        const res = await fetch('/api/it_payments/send_reminder', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ payment_id: paymentId })
        });
        const data = await res.json();
        if (data.success) {
            alert(`🔔 ${data.message}`);
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    } catch (err) {
        alert('Failed to dispatch reminder: ' + err.message);
    }
}

async function openModalAddWarranty() {
    try {
        const assetsData = await fetch('/api/it_assets').then(r => r.json());
        const assets = assetsData.assets || [];
        document.getElementById('warranty-asset-id').innerHTML = assets.map(a => `
            <option value="${a.id}">${a.asset_tag} — ${a.brand} ${a.model_name} (S/N: ${a.serial_number || 'N/A'})</option>
        `).join('');

        document.getElementById('warranty-start-date').value = new Date().toISOString().split('T')[0];
        openModal('modal-it-add-warranty');
    } catch (err) {
        alert('Failed to open warranty form: ' + err.message);
    }
}

async function submitCreateITWarranty(e) {
    e.preventDefault();
    const payload = {
        asset_id: parseInt(document.getElementById('warranty-asset-id').value),
        provider_name: document.getElementById('warranty-provider').value.trim(),
        policy_number: document.getElementById('warranty-policy-no').value.trim(),
        warranty_type: document.getElementById('warranty-type').value,
        start_date: document.getElementById('warranty-start-date').value,
        end_date: document.getElementById('warranty-end-date').value,
        support_contact: document.getElementById('warranty-contact').value.trim(),
        notes: document.getElementById('warranty-notes').value.trim()
    };

    try {
        const res = await fetch('/api/it_warranties/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-it-add-warranty');
            renderAssetManagementTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to register warranty: ' + err.message);
    }
}

async function logWarrantyClaim(warrantyId) {
    const claimNotes = prompt("Enter warranty claim reference / RMA ticket number or reason:", "Claim filed by IT Support Desk for hardware diagnostic review");
    if (!claimNotes) return;

    try {
        const res = await fetch('/api/it_warranties/claim', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ warranty_id: warrantyId, notes: claimNotes })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            renderAssetManagementTab();
        } else {
            alert(`❌ Error: ${data.message}`);
        }
    } catch (err) {
        alert('Failed to log claim: ' + err.message);
    }
}

async function openModalLogService(preferredAssetId) {
    try {
        const assetsData = await fetch('/api/it_assets').then(r => r.json());
        const assets = assetsData.assets || [];
        document.getElementById('service-asset-id').innerHTML = assets.map(a => `
            <option value="${a.id}" ${a.id === preferredAssetId ? 'selected' : ''}>
                ${a.asset_tag} — ${a.brand} ${a.model_name} (Current: ${a.current_location})
            </option>
        `).join('');

        document.getElementById('service-start-date').value = new Date().toISOString().split('T')[0];
        openModal('modal-it-log-service');
    } catch (err) {
        alert('Failed to open service ticket modal: ' + err.message);
    }
}

async function submitLogITService(e) {
    e.preventDefault();
    const payload = {
        asset_id: parseInt(document.getElementById('service-asset-id').value),
        service_type: document.getElementById('service-type').value,
        reported_issue: document.getElementById('service-issue').value.trim(),
        service_center_or_vendor: document.getElementById('service-center').value.trim(),
        technician_name: document.getElementById('service-tech-name').value.trim(),
        start_date: document.getElementById('service-start-date').value,
        repair_cost: parseFloat(document.getElementById('service-cost').value || 0),
        warranty_claim_covered: document.getElementById('service-warranty-covered').checked,
        remarks: 'Service ticket dispatched via IT Support Administrator'
    };

    try {
        const res = await fetch('/api/it_maintenance/create', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-it-log-service');
            renderAssetManagementTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to log service ticket: ' + err.message);
    }
}

async function openModalCompleteService(ticketId) {
    try {
        const data = await fetch('/api/it_maintenance').then(r => r.json());
        const t = (data.tickets || []).find(x => x.id === ticketId);
        if (!t) return;

        document.getElementById('complete-service-ticket-id').value = t.id;
        document.getElementById('complete-service-header-ticket').innerText = `Ticket #${t.service_ticket_no} | Equipment: ${t.asset_tag} (${t.brand} ${t.model_name})`;
        document.getElementById('complete-service-date').value = new Date().toISOString().split('T')[0];
        document.getElementById('complete-service-cost').value = t.repair_cost || 0;
        document.getElementById('complete-service-info').innerHTML = `
            <div style="font-size:0.85rem;">
                <strong>Reported Issue:</strong> ${t.reported_issue}<br>
                <span style="font-size:0.75rem; color:#64748b;">Service Center: ${t.service_center_or_vendor} | Tech: ${t.technician_name || 'N/A'}</span>
            </div>
        `;

        openModal('modal-it-complete-service');
    } catch (err) {
        alert('Failed to open service completion: ' + err.message);
    }
}

async function submitCompleteITService(e) {
    e.preventDefault();
    const payload = {
        ticket_id: parseInt(document.getElementById('complete-service-ticket-id').value),
        completion_date: document.getElementById('complete-service-date').value,
        repair_cost: parseFloat(document.getElementById('complete-service-cost').value || 0),
        parts_replaced: document.getElementById('complete-service-parts').value.trim(),
        return_location: document.getElementById('complete-service-location').value.trim(),
        remarks: document.getElementById('complete-service-remarks').value.trim()
    };

    try {
        const res = await fetch('/api/it_maintenance/complete', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-it-complete-service');
            renderAssetManagementTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to complete service: ' + err.message);
    }
}

// =====================================================================
// FORMAL PRINTABLE REPORT & CSV EXPORT GENERATOR
// =====================================================================

async function printFormalAssetReport(reportType) {
    let title = "Greenland School - IT Asset Management Report";
    let printHtml = "";
    const today = new Date().toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });

    if (reportType === 'inventory') {
        title = "MASTER LAPTOP & COMPUTER FLEET INVENTORY REGISTER";
        const data = await fetch('/api/it_assets').then(r => r.json());
        const assets = data.assets || [];
        printHtml = `
            <table style="width:100%; border-collapse:collapse; font-size:11px; margin-top:14px;" border="1">
                <thead style="background:#f1f5f9;">
                    <tr>
                        <th style="padding:6px;">Asset Tag</th>
                        <th style="padding:6px;">Type</th>
                        <th style="padding:6px;">Brand & Model</th>
                        <th style="padding:6px;">Serial Number</th>
                        <th style="padding:6px;">Processor & RAM</th>
                        <th style="padding:6px;">Storage & OS</th>
                        <th style="padding:6px;">Ownership</th>
                        <th style="padding:6px;">Location / Custodian</th>
                        <th style="padding:6px;">Condition</th>
                        <th style="padding:6px;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${assets.map(a => `
                        <tr>
                            <td style="padding:6px; font-weight:bold; font-family:monospace;">${a.asset_tag}</td>
                            <td style="padding:6px;">${a.device_type}</td>
                            <td style="padding:6px;">${a.brand} ${a.model_name}</td>
                            <td style="padding:6px; font-family:monospace;">${a.serial_number || '—'}</td>
                            <td style="padding:6px;">${a.specs_processor || ''} (${a.specs_ram || ''})</td>
                            <td style="padding:6px;">${a.specs_storage || ''} / ${a.specs_os || ''}</td>
                            <td style="padding:6px;">${a.ownership_type}</td>
                            <td style="padding:6px;">${a.current_location}</td>
                            <td style="padding:6px;">${a.condition}</td>
                            <td style="padding:6px; font-weight:bold;">${a.status}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } else if (reportType === 'allocations') {
        title = "EMPLOYEE LAPTOP & COMPUTER ASSET ALLOCATION & HANDOVER LEDGER";
        const data = await fetch('/api/it_allocations').then(r => r.json());
        const allocs = data.allocations || [];
        printHtml = `
            <table style="width:100%; border-collapse:collapse; font-size:11px; margin-top:14px;" border="1">
                <thead style="background:#f1f5f9;">
                    <tr>
                        <th style="padding:6px;">Slip #</th>
                        <th style="padding:6px;">Asset Tag</th>
                        <th style="padding:6px;">Model</th>
                        <th style="padding:6px;">Employee Name</th>
                        <th style="padding:6px;">Role / Dept</th>
                        <th style="padding:6px;">Handover Date</th>
                        <th style="padding:6px;">Expected Return</th>
                        <th style="padding:6px;">Accessories Issued</th>
                        <th style="padding:6px;">Custody Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${allocs.map(a => `
                        <tr>
                            <td style="padding:6px; font-weight:bold; font-family:monospace;">${a.handover_slip_no}</td>
                            <td style="padding:6px; font-weight:bold;">${a.asset_tag}</td>
                            <td style="padding:6px;">${a.brand} ${a.model_name}</td>
                            <td style="padding:6px; font-weight:bold;">${a.employee_name}</td>
                            <td style="padding:6px;">${a.employee_role} (${a.department || ''})</td>
                            <td style="padding:6px;">${a.handover_date}</td>
                            <td style="padding:6px;">${a.expected_return_date || 'Ongoing'}</td>
                            <td style="padding:6px;">${a.accessories_included || 'None'}</td>
                            <td style="padding:6px; font-weight:bold;">${a.handover_status}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } else if (reportType === 'rentals') {
        title = "HARDWARE RENTAL AGREEMENTS & FINANCIAL OBLIGATIONS STATEMENT";
        const data = await fetch('/api/it_rentals').then(r => r.json());
        const rentals = data.rentals || [];
        printHtml = `
            <table style="width:100%; border-collapse:collapse; font-size:11px; margin-top:14px;" border="1">
                <thead style="background:#f1f5f9;">
                    <tr>
                        <th style="padding:6px;">Agreement #</th>
                        <th style="padding:6px;">Vendor Name</th>
                        <th style="padding:6px;">Type</th>
                        <th style="padding:6px;">Linked Asset</th>
                        <th style="padding:6px;">Validity Period</th>
                        <th style="padding:6px;">Billing Rate</th>
                        <th style="padding:6px;">Next Due Date</th>
                        <th style="padding:6px;">Payment Status</th>
                        <th style="padding:6px;">Agreement Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${rentals.map(r => `
                        <tr>
                            <td style="padding:6px; font-weight:bold; font-family:monospace;">${r.rental_agreement_no}</td>
                            <td style="padding:6px; font-weight:bold;">${r.vendor_or_client_name}</td>
                            <td style="padding:6px;">${r.rental_type}</td>
                            <td style="padding:6px;">${r.asset_tag || 'Fleet'}</td>
                            <td style="padding:6px;">${r.start_date} to ${r.end_date}</td>
                            <td style="padding:6px; font-weight:bold;">₦${(r.rental_amount || 0).toLocaleString()} (${r.billing_cycle})</td>
                            <td style="padding:6px;">${r.next_payment_due_date || '—'}</td>
                            <td style="padding:6px;">${r.payment_status}</td>
                            <td style="padding:6px; font-weight:bold;">${r.rental_status}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } else if (reportType === 'maintenance') {
        title = "HARDWARE MAINTENANCE & SERVICE EXPENDITURE LOG";
        const data = await fetch('/api/it_maintenance').then(r => r.json());
        const tickets = data.tickets || [];
        printHtml = `
            <table style="width:100%; border-collapse:collapse; font-size:11px; margin-top:14px;" border="1">
                <thead style="background:#f1f5f9;">
                    <tr>
                        <th style="padding:6px;">Ticket #</th>
                        <th style="padding:6px;">Asset Tag</th>
                        <th style="padding:6px;">Service Category</th>
                        <th style="padding:6px;">Defect / Symptoms</th>
                        <th style="padding:6px;">Service Hub / Tech</th>
                        <th style="padding:6px;">Start Date</th>
                        <th style="padding:6px;">Repair Cost (₦)</th>
                        <th style="padding:6px;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${tickets.map(t => `
                        <tr>
                            <td style="padding:6px; font-weight:bold; font-family:monospace;">${t.service_ticket_no}</td>
                            <td style="padding:6px; font-weight:bold;">${t.asset_tag} (${t.brand} ${t.model_name})</td>
                            <td style="padding:6px;">${t.service_type}</td>
                            <td style="padding:6px;">${t.reported_issue}</td>
                            <td style="padding:6px;">${t.service_center_or_vendor} (${t.technician_name || 'N/A'})</td>
                            <td style="padding:6px;">${t.start_date}</td>
                            <td style="padding:6px; font-weight:bold;">₦${(t.repair_cost || 0).toLocaleString()}</td>
                            <td style="padding:6px; font-weight:bold;">${t.service_status}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    } else if (reportType === 'warranties') {
        title = "HARDWARE OEM WARRANTY & AMC CONTRACT SCHEDULE";
        const data = await fetch('/api/it_warranties').then(r => r.json());
        const wars = data.warranties || [];
        printHtml = `
            <table style="width:100%; border-collapse:collapse; font-size:11px; margin-top:14px;" border="1">
                <thead style="background:#f1f5f9;">
                    <tr>
                        <th style="padding:6px;">Asset Tag</th>
                        <th style="padding:6px;">Model</th>
                        <th style="padding:6px;">Provider Name</th>
                        <th style="padding:6px;">Policy #</th>
                        <th style="padding:6px;">Coverage Type</th>
                        <th style="padding:6px;">Validity Period</th>
                        <th style="padding:6px;">Days Remaining</th>
                        <th style="padding:6px;">Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${wars.map(w => `
                        <tr>
                            <td style="padding:6px; font-weight:bold;">${w.asset_tag}</td>
                            <td style="padding:6px;">${w.brand} ${w.model_name}</td>
                            <td style="padding:6px; font-weight:bold;">${w.provider_name}</td>
                            <td style="padding:6px; font-family:monospace;">${w.policy_number}</td>
                            <td style="padding:6px;">${w.warranty_type}</td>
                            <td style="padding:6px;">${w.start_date} to ${w.end_date}</td>
                            <td style="padding:6px; font-weight:bold;">${w.days_remaining} Days</td>
                            <td style="padding:6px; font-weight:bold;">${w.calculated_status}</td>
                        </tr>
                    `).join('')}
                </tbody>
            </table>
        `;
    }

    const printWin = window.open('', '_blank', 'width=950,height=700');
    printWin.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>${title}</title>
            <style>
                body { font-family: 'Segoe UI', Arial, sans-serif; padding: 24px; color: #0f172a; }
                .header { text-align: center; border-bottom: 3px double #0f172a; padding-bottom: 12px; margin-bottom: 16px; }
                .school-title { font-size: 20px; font-weight: 900; letter-spacing: 0.5px; text-transform: uppercase; color: #1e3a8a; }
                .doc-title { font-size: 15px; font-weight: 800; color: #0f172a; margin-top: 4px; }
                .meta { font-size: 11px; color: #64748b; margin-top: 4px; }
                .sign-block { display: flex; justify-content: space-between; margin-top: 45px; font-size: 12px; }
                .sign-line { border-top: 1px solid #334155; width: 220px; text-align: center; padding-top: 6px; }
                @media print {
                    button { display: none; }
                }
            </style>
        </head>
        <body>
            <div style="text-align:right; margin-bottom:10px;">
                <button onclick="window.print()" style="padding:6px 16px; font-weight:bold; cursor:pointer;">🖨️ Print This Document</button>
            </div>
            <div class="header">
                <div class="school-title">GREENLAND SCHOOL</div>
                <div style="font-size:12px; color:#475569;">Khadpathar, Renukoot, Sonbhadra, Uttar Pradesh - 231217</div>
                <div class="doc-title">${title}</div>
                <div class="meta">Generated by IT Support Administration | Audit Date: ${today} | Official Directorate Record</div>
            </div>

            ${printHtml}

            <div class="sign-block">
                <div class="sign-line">
                    <strong>IT Support Administrator</strong><br>
                    Greenland School IT Depot
                </div>
                <div class="sign-line">
                    <strong>Bursar & Finance Desk</strong><br>
                    Internal Audit Verification
                </div>
                <div class="sign-line">
                    <strong>Director / Super Admin</strong><br>
                    Executive Directorate Approval
                </div>
            </div>
        </body>
        </html>
    `);
    printWin.document.close();
}

async function printHandoverSlip(allocationId) {
    try {
        const data = await fetch('/api/it_allocations').then(r => r.json());
        const alc = (data.allocations || []).find(x => x.id === allocationId);
        if (!alc) return;

        const printWin = window.open('', '_blank', 'width=800,height=750');
        printWin.document.write(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>Equipment Handover Slip - ${alc.handover_slip_no}</title>
                <style>
                    body { font-family: 'Segoe UI', Arial, sans-serif; padding: 28px; color: #0f172a; line-height: 1.4; }
                    .header { text-align: center; border-bottom: 2px solid #1e3a8a; padding-bottom: 12px; margin-bottom: 20px; }
                    .school { font-size: 22px; font-weight: 900; color: #1e3a8a; text-transform: uppercase; }
                    .slip-title { font-size: 15px; font-weight: 800; color: #0f172a; margin-top: 4px; }
                    .grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 18px; font-size: 13px; }
                    .field { background: #f8fafc; border: 1px solid #cbd5e1; padding: 10px 14px; border-radius: 6px; }
                    .undertaking { background: #eff6ff; border: 1px solid #bfdbfe; padding: 14px; font-size: 12px; border-radius: 6px; margin: 20px 0; color: #1e40af; }
                    .signs { display: flex; justify-content: space-between; margin-top: 50px; font-size: 12px; }
                    .sign-box { border-top: 1px solid #0f172a; width: 220px; text-align: center; padding-top: 6px; }
                    @media print { button { display: none; } }
                </style>
            </head>
            <body>
                <div style="text-align:right; margin-bottom:10px;">
                    <button onclick="window.print()" style="padding:6px 16px; font-weight:bold; cursor:pointer;">🖨️ Print Handover Slip</button>
                </div>
                <div class="header">
                    <div class="school">GREENLAND SCHOOL</div>
                    <div style="font-size:12px; color:#475569;">Information Technology & Infrastructure Operations Department</div>
                    <div class="slip-title">FORMAL IT HARDWARE HANDOVER & RESPONSIBILITY SLIP</div>
                    <div style="font-size:12px; color:#64748b; font-family:monospace; margin-top:3px;">SLIP REF: ${alc.handover_slip_no} | DATE: ${alc.handover_date}</div>
                </div>

                <div class="grid">
                    <div class="field">
                        <strong>EQUIPMENT DETAILS:</strong><br>
                        Asset Tag: <strong style="color:#1e40af; font-family:monospace;">${alc.asset_tag}</strong><br>
                        Device: ${alc.brand} ${alc.model_name} (${alc.device_type})<br>
                        Serial Number: <span style="font-family:monospace;">${alc.serial_number || 'N/A'}</span><br>
                        Physical Condition: <strong>${alc.handover_condition}</strong>
                    </div>
                    <div class="field">
                        <strong>CUSTODIAN EMPLOYEE:</strong><br>
                        Employee Name: <strong>${alc.employee_name}</strong><br>
                        Designation / Role: ${alc.employee_role}<br>
                        Department: ${alc.department || 'Academics & Faculty'}<br>
                        Expected Return Date: <strong>${alc.expected_return_date || 'Permanent Academic Year'}</strong>
                    </div>
                </div>

                <div class="field" style="margin-bottom:18px; font-size:13px;">
                    <strong>PERIPHERALS & ACCESSORIES DELIVERED:</strong><br>
                    ${alc.accessories_included || 'Original 65W Charger, Laptop Bag, Wireless Optical Mouse'}<br><br>
                    <strong>HANDOVER & USAGE NOTES:</strong><br>
                    ${alc.handover_notes || 'Issued for academic curriculum delivery and institutional administrative operations.'}
                </div>

                <div class="undertaking">
                    <strong>EMPLOYEE INSTITUTIONAL RESPONSIBILITY UNDERTAKING:</strong><br>
                    I hereby acknowledge receipt of the aforementioned laptop/computer equipment in verified working order. I agree to safeguard the hardware, ensure anti-virus protection remains active, use the device in accordance with Greenland School IT Acceptable Use Policies, and return the device with all issued accessories upon demand or completion of my tenure.
                </div>

                <div class="signs">
                    <div class="sign-box">
                        <strong>${alc.employee_name}</strong><br>
                        Recipient Faculty / Employee
                    </div>
                    <div class="sign-box">
                        <strong>IT Support Administrator</strong><br>
                        Authorizing Issuance Officer
                    </div>
                    <div class="sign-box">
                        <strong>Owner (Director) Rajeev Sinha</strong><br>
                        Directorate Executive Seal
                    </div>
                </div>
            </body>
            </html>
        `);
        printWin.document.close();
    } catch (err) {
        alert('Failed to generate handover slip: ' + err.message);
    }
}

async function exportAssetCSV(reportType) {
    let rows = [];
    let filename = `Greenland_School_${reportType}_${new Date().toISOString().split('T')[0]}.csv`;

    if (reportType === 'inventory') {
        const data = await fetch('/api/it_assets').then(r => r.json());
        rows = [["Asset Tag", "Device Type", "Brand", "Model", "Serial Number", "Processor", "RAM", "Storage", "OS", "Ownership", "Condition", "Location", "Status"]];
        (data.assets || []).forEach(a => {
            rows.push([a.asset_tag, a.device_type, a.brand, a.model_name, a.serial_number || '', a.specs_processor || '', a.specs_ram || '', a.specs_storage || '', a.specs_os || '', a.ownership_type, a.condition, a.current_location, a.status]);
        });
    } else if (reportType === 'allocations') {
        const data = await fetch('/api/it_allocations').then(r => r.json());
        rows = [["Handover Slip", "Asset Tag", "Brand", "Model", "Employee Name", "Role", "Department", "Handover Date", "Expected Return", "Accessories", "Status"]];
        (data.allocations || []).forEach(a => {
            rows.push([a.handover_slip_no, a.asset_tag, a.brand, a.model_name, a.employee_name, a.employee_role, a.department || '', a.handover_date, a.expected_return_date || '', a.accessories_included || '', a.handover_status]);
        });
    }

    const csvContent = "data:text/csv;charset=utf-8," + rows.map(e => e.map(x => `"${(x + '').replace(/"/g, '""')}"`).join(",")).join("\n");
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", filename);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function openModalAddPaymentReminder() {
    openModal('modal-it-record-payment');
}



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
    const callerRole = currentRole || (currentUser ? currentUser.user_type : 'super_admin');

    const isDirector = (
        callerRole === 'super_admin' ||
        callerRole === 'director' ||
        (callerUname && (callerUname.toLowerCase().includes('direct') || callerUname.toLowerCase().includes('owner')))
    );

    if (!isDirector) {
        alert("🔒 Access Denied: Only Director (Owner) Rajeev Sinha has authority to approve requests created by Teachers or IT Team.");
        return;
    }

    let defaultNote = action === 'approve' ? 'Approved by Director Rajeev Sinha' : 'Rejected by Director';
    let note = defaultNote;
    try {
        const inputNote = prompt(`Enter Director Approval Notes (or leave default):`, defaultNote);
        if (inputNote && inputNote.trim()) note = inputNote.trim();
    } catch (e) {
        note = defaultNote;
    }

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
            alert("✓ Teacher Leave Application Submitted successfully!\n\nPolicy Status: ⏳ Sent to Director Rajeev Sinha for Approval.");
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

    let lab = document.getElementById('app-comp-lab').value;
    if (lab === 'Computer Lab 1') lab = 'Computer Lab 1 (Main Lab)';
    else if (lab === 'Computer Lab 2') lab = 'Computer Lab 2 (Senior Coding Lab)';
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
            alert(`✓ Faulty Computer Complaint ${res.ticket_no} logged!\n\nPolicy Status: ⏳ Dispatched to IT Support Administrator & Director for Repair Approval.`);
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
