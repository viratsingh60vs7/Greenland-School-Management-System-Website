# Append all new helper and lab management functions to app.js
with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

new_functions = """
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
    openModal('modal-assign-user-role');
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

    try {
        const res = await fetch('/api/users/assign_role', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                user_id: userId,
                role: newRole,
                name: personName,
                gender: gender,
                assigned_by: currentUser ? (currentUser.name || currentUser.username) : 'Owner(Directer)'
            })
        });
        const data = await res.json();
        if (data.success) {
            alert(`✅ ${data.message}`);
            closeModal('modal-assign-user-role');
            renderUsersTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to reassign role: ' + err.message);
    }
}

async function confirmCleanTestData() {
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
                                                    <button class="btn btn-primary btn-sm" style="font-size:0.72rem; padding:3px 8px;" onclick="openAssignLabRepairModal(${c.id})">Assign Tech</button>
                                                ` : `
                                                    <button class="btn btn-success btn-sm" style="font-size:0.72rem; padding:3px 8px; background:#16a34a;" onclick="openResolveLabComplaintModal(${c.id})">Mark Fixed</button>
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
                        <button class="btn btn-secondary" onclick="showTab('lab_manager')" style="text-align:left; display:flex; align-items:center; gap:10px;">
                            <span>🖥️</span> Explore Computer Lab Grid
                        </button>
                        <button class="btn btn-secondary" onclick="showTab('lab_complaints')" style="text-align:left; display:flex; align-items:center; gap:10px;">
                            <span>🛠️</span> Repair Dispatch Ledger
                        </button>
                        <button class="btn btn-secondary" onclick="openModal('modal-add-lab-pc')" style="text-align:left; display:flex; align-items:center; gap:10px;">
                            <span>➕</span> Add / Configure Lab PC
                        </button>
                        <button class="btn btn-secondary" onclick="openModal('modal-report-lab-complaint')" style="text-align:left; display:flex; align-items:center; gap:10px;">
                            <span>🚨</span> Log Lab Hardware Fault
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
                            <option value="Computer Lab 2 (Junior Lab)" ${labManagerFilterLab === 'Computer Lab 2 (Junior Lab)' ? 'selected' : ''}>Computer Lab 2 (Junior Lab)</option>
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
                                <div style="border:2px solid ${borderCol}; background:${bgCol}; border-radius:8px; padding:10px 8px; text-align:center; transition:transform 0.15s ease; cursor:pointer;" onclick="handleClickLabComputer(${c.id}, '${c.pc_number}', '${c.status}', ${c.active_complaint_id || 'null'})" title="${c.pc_number} - ${c.lab_name} (${c.status})">
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
                                                <button class="btn btn-primary btn-sm" style="font-size:0.72rem; padding:3px 8px;" onclick="openAssignLabRepairModal(${c.active_complaint_id})">
                                                    🛠️ Assign Tech
                                                </button>
                                            ` : (c.status === 'In Repair' ? `
                                                <button class="btn btn-success btn-sm" style="font-size:0.72rem; padding:3px 8px; background:#16a34a;" onclick="openResolveLabComplaintModal(${c.active_complaint_id})">
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

function handleClickLabComputer(id, pcNumber, status, complaintId) {
    if (status === 'Faulty' && complaintId) {
        openAssignLabRepairModal(complaintId);
    } else if (status === 'In Repair' && complaintId) {
        openResolveLabComplaintModal(complaintId);
    } else {
        prefillReportComplaint('Computer Lab 1 (Main Lab)', pcNumber);
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
        const res = await fetch('/api/lab/complaints');
        const data = await res.json();
        const complaints = data.complaints || [];
        const isITAdminOrOwner = ['it_admin', 'super_admin'].includes(currentRole);

        const pendingCount = complaints.filter(c => c.status === 'Pending').length;
        const assignedCount = complaints.filter(c => c.status === 'Assigned').length;
        const resolvedCount = complaints.filter(c => c.status === 'Resolved').length;

        const html = `
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
                                    if (c.status === 'Assigned') {
                                        statusBadge = `<span class="badge" style="background:#eff6ff; color:#2563eb; font-weight:700;">🛠️ In Repair</span>`;
                                    } else if (c.status === 'Resolved') {
                                        statusBadge = `<span class="badge" style="background:#dcfce7; color:#15803d; font-weight:700;">✅ Resolved</span>`;
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
                                                    ${c.status === 'Pending' && isITAdminOrOwner ? `
                                                        <button class="btn btn-primary btn-sm" style="font-size:0.72rem; padding:4px 8px; font-weight:700;" onclick="openAssignLabRepairModal(${c.id})">
                                                            🛠️ Assign Tech
                                                        </button>
                                                    ` : ''}
                                                    ${c.status === 'Assigned' && isITAdminOrOwner ? `
                                                        <button class="btn btn-success btn-sm" style="font-size:0.72rem; padding:4px 8px; background:#16a34a; font-weight:700;" onclick="openResolveLabComplaintModal(${c.id})">
                                                            ✅ Mark Fixed
                                                        </button>
                                                    ` : ''}
                                                    ${c.status === 'Resolved' ? `
                                                        <span style="font-size:0.72rem; color:#15803d; font-weight:700;">✓ Operational</span>
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

        const filtered = computers.filter(c => c.lab_name === labName);
        select.innerHTML = filtered.map(c => `
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

async function openAssignLabRepairModal(complaintId) {
    try {
        const res = await fetch('/api/lab/complaints');
        const data = await res.json();
        const complaints = data.complaints || [];
        const c = complaints.find(x => x.id === complaintId);
        if (!c) {
            alert('Ticket not found.');
            return;
        }
        document.getElementById('assign-repair-complaint-id').value = c.id;
        document.getElementById('assign-repair-summary-card').innerHTML = `
            <div><strong>Ticket:</strong> <code style="color:#1e3a8a; font-weight:700;">${c.ticket_no}</code></div>
            <div style="margin-top:2px;"><strong>Workstation:</strong> <code>${c.pc_number}</code> (${c.lab_name})</div>
            <div style="margin-top:2px;"><strong>Reported Issue:</strong> ${c.issue_category} - <em>${c.problem_description}</em></div>
            <div style="margin-top:2px;"><strong>Reported By:</strong> ${c.reported_by_name} (Urgency: <strong>${c.priority}</strong>)</div>
        `;
        openModal('modal-assign-lab-repair');
    } catch (err) {
        alert('Failed to load complaint: ' + err.message);
    }
}

async function submitAssignLabRepair(e) {
    e.preventDefault();
    const complaintId = parseInt(document.getElementById('assign-repair-complaint-id').value);
    const techName = document.getElementById('assign-repair-technician-name').value;
    const notes = document.getElementById('assign-repair-notes').value.trim();

    try {
        const res = await fetch('/api/lab/complaints/assign', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                complaint_id: complaintId,
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
            else renderLabComplaintsTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to assign repair: ' + err.message);
    }
}

async function openResolveLabComplaintModal(complaintId) {
    try {
        const res = await fetch('/api/lab/complaints');
        const data = await res.json();
        const complaints = data.complaints || [];
        const c = complaints.find(x => x.id === complaintId);
        if (!c) {
            alert('Ticket not found.');
            return;
        }
        document.getElementById('resolve-repair-complaint-id').value = c.id;
        document.getElementById('resolve-repair-summary-card').innerHTML = `
            <div><strong>Ticket:</strong> <code style="color:#1e3a8a; font-weight:700;">${c.ticket_no}</code></div>
            <div style="margin-top:2px;"><strong>Workstation:</strong> <code>${c.pc_number}</code> (${c.lab_name})</div>
            <div style="margin-top:2px;"><strong>Assigned Technician:</strong> <strong>${c.assigned_to_name || 'IT Support'}</strong></div>
            <div style="margin-top:2px;"><strong>Reported Issue:</strong> ${c.problem_description}</div>
        `;
        openModal('modal-resolve-lab-complaint');
    } catch (err) {
        alert('Failed to load complaint: ' + err.message);
    }
}

async function submitResolveLabComplaint(e) {
    e.preventDefault();
    const complaintId = parseInt(document.getElementById('resolve-repair-complaint-id').value);
    const notes = document.getElementById('resolve-repair-notes').value.trim();

    try {
        const res = await fetch('/api/lab/complaints/resolve', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                complaint_id: complaintId,
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
            else renderLabComplaintsTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to resolve complaint: ' + err.message);
    }
}

async function submitAddLabPC(e) {
    e.preventDefault();
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
            e.target.reset();
            renderLabManagerTab();
        } else {
            alert(`❌ Error: ${data.message || data.error}`);
        }
    } catch (err) {
        alert('Failed to add PC: ' + err.message);
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
"""

code = code + "\n" + new_functions

with open('school_website/js/app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Part 3 (new functions) appended successfully!")
