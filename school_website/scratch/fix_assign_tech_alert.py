import re

# 1. Update server.py
with open('school_website/server.py', 'r', encoding='utf-8') as f:
    server_code = f.read()

target_server = """                # Resilient self-healing: if complaint_id is missing or 0, locate active ticket or generate one
                if (not complaint_id or str(complaint_id) in ('0', 'null', 'None')) and (pc_number or computer_id):
                    cur.execute("SELECT id FROM lab_complaints WHERE (computer_id = ? OR pc_number = ?) AND status != 'Resolved' ORDER BY id DESC LIMIT 1", (computer_id, pc_number))
                    t_match = cur.fetchone()
                    if t_match:
                        complaint_id = t_match[0]
                    else:
                        tkt_no = f"TKT-LAB-{datetime.now().strftime('%y%m%d')}-{os.urandom(2).hex().upper()}"
                        cur.execute(\"\"\"
                            INSERT INTO lab_complaints (ticket_no, computer_id, pc_number, lab_name, reported_by_name, teacher_role, issue_category, problem_description, priority, status, created_at)
                            VALUES (?, ?, ?, 'Computer Lab', 'IT Support Administrator', 'IT Hardware Dispatch', 'Hardware Repair', 'Technician assigned for hardware fault.', 'High', 'Assigned', ?)
                        \"\"\", (tkt_no, computer_id or 1, pc_number or 'Workstation', now))
                        complaint_id = cur.lastrowid"""

repl_server = """                # Resilient self-healing: if complaint_id is missing or 0, locate active ticket or generate one
                if (not complaint_id or str(complaint_id) in ('0', 'null', 'None')) and (pc_number or computer_id):
                    cur.execute("SELECT id FROM lab_complaints WHERE (computer_id = ? OR pc_number = ?) AND status != 'Resolved' ORDER BY id DESC LIMIT 1", (computer_id, pc_number))
                    t_match = cur.fetchone()
                    if t_match:
                        complaint_id = t_match[0]
                    else:
                        detected_lab = 'Computer Lab'
                        if pc_number or computer_id:
                            cur.execute("SELECT lab_name, id, pc_number FROM lab_computers WHERE id = ? OR pc_number = ?", (computer_id, pc_number))
                            c_info = cur.fetchone()
                            if c_info:
                                detected_lab = c_info[0] or 'Computer Lab'
                                if not computer_id:
                                    computer_id = c_info[1]
                                if not pc_number:
                                    pc_number = c_info[2]
                        tkt_no = f"TKT-LAB-{datetime.now().strftime('%y%m%d')}-{os.urandom(2).hex().upper()}"
                        cur.execute(\"\"\"
                            INSERT INTO lab_complaints (ticket_no, computer_id, pc_number, lab_name, reported_by_name, teacher_role, issue_category, problem_description, priority, status, created_at)
                            VALUES (?, ?, ?, ?, 'IT Support Administrator', 'IT Hardware Dispatch', 'Hardware Repair', 'Technician assigned for hardware fault.', 'High', 'Assigned', ?)
                        \"\"\", (tkt_no, computer_id or 1, pc_number or 'Workstation', detected_lab, now))
                        complaint_id = cur.lastrowid"""

server_code_norm = server_code.replace('\r\n', '\n')
target_server_norm = target_server.replace('\r\n', '\n')
repl_server_norm = repl_server.replace('\r\n', '\n')

if target_server_norm in server_code_norm:
    server_code_norm = server_code_norm.replace(target_server_norm, repl_server_norm)
    with open('school_website/server.py', 'w', encoding='utf-8', newline='\r\n') as f:
        f.write(server_code_norm)
    print("Successfully patched server.py")
else:
    print("Target not found in server.py!")

# 2. Update app.js
with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    app_code = f.read()

app_code_norm = app_code.replace('\r\n', '\n')

# Patch line 7524 & 7526 in renderLabManagerTab
target_quick_btns = """                                                ${c.status === 'Pending' ? `
                                                    <button class="btn btn-primary btn-sm" style="font-size:0.72rem; padding:3px 8px;" onclick="openAssignLabRepairModal(${c.id})">Assign Tech</button>
                                                ` : `
                                                    <button class="btn btn-success btn-sm" style="font-size:0.72rem; padding:3px 8px; background:#16a34a;" onclick="openResolveLabComplaintModal(${c.id})">Mark Fixed</button>
                                                `}"""

repl_quick_btns = """                                                ${c.status === 'Pending' ? `
                                                    <button class="btn btn-primary btn-sm" style="font-size:0.72rem; padding:3px 8px;" onclick="openAssignLabRepairModal(${c.id}, '${c.pc_number}', '${c.lab_name}', ${c.computer_id || 'null'})">Assign Tech</button>
                                                ` : `
                                                    <button class="btn btn-success btn-sm" style="font-size:0.72rem; padding:3px 8px; background:#16a34a;" onclick="openResolveLabComplaintModal(${c.id}, '${c.pc_number}', '${c.lab_name}', ${c.computer_id || 'null'})">Mark Fixed</button>
                                                `}"""

if target_quick_btns in app_code_norm:
    app_code_norm = app_code_norm.replace(target_quick_btns, repl_quick_btns)
    print("Successfully patched quick fault buttons in app.js")
else:
    print("Quick fault buttons target not found in app.js!")

# Patch openAssignLabRepairModal in app.js
assign_modal_pattern = re.compile(r'async function openAssignLabRepairModal\(complaintId, pcNumber = \'\', labName = \'\', computerId = null\) \{[\s\S]*?openModal\(\'modal-assign-lab-repair\'\);\s*\}\s*catch\s*\(err\)\s*\{\s*alert\(\'Failed to load complaint: \' \+ err\.message\);\s*\}\s*\}')

repl_assign_modal = """async function openAssignLabRepairModal(complaintId, pcNumber = '', labName = '', computerId = null) {
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
}"""

match = assign_modal_pattern.search(app_code_norm)
if match:
    app_code_norm = app_code_norm[:match.start()] + repl_assign_modal + app_code_norm[match.end():]
    print("Successfully replaced openAssignLabRepairModal in app.js")
else:
    print("Regex match failed for openAssignLabRepairModal!")

# Patch openResolveLabComplaintModal in app.js
target_resolve_alert = """        if (!c) {
            alert('Notice: No active ticket found to resolve for this workstation.');
            return;
        }"""

repl_resolve_fallback = """        if (!c) {
            const finalPc = pcNumber || (computerId ? `PC-${String(computerId).padStart(2, '0')}` : 'Workstation');
            c = {
                id: targetId || 0,
                ticket_no: 'TKT-DIRECT-RESOLVE',
                pc_number: finalPc,
                lab_name: labName || 'Computer Lab 1 (Main Lab)',
                assigned_to_name: 'IT Support Administrator',
                problem_description: `Hardware inspected, repaired, and confirmed operational for ${finalPc}.`
            };
        }"""

if target_resolve_alert in app_code_norm:
    app_code_norm = app_code_norm.replace(target_resolve_alert, repl_resolve_fallback)
    print("Successfully patched openResolveLabComplaintModal in app.js")
else:
    print("Target resolve alert not found in app.js!")

with open('school_website/js/app.js', 'w', encoding='utf-8', newline='\r\n') as f:
    f.write(app_code_norm)
print("Saved updated app.js")
