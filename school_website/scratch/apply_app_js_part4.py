# Python script to update renderPayrollTab in app.js
with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    code = f.read()

old_payroll_pre = """    const monthNames = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

    let content = `"""

new_payroll_pre = """    const monthNames = ['', 'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];

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

    let content = `"""

old_month_controls_end = """                <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
                    ${!isTeacher ? `
                        <button class="btn btn-primary" style="font-weight:700; display:inline-flex; align-items:center; gap:8px;" onclick="triggerAutoGeneratePayroll(${currentPayrollMonth}, ${currentPayrollYear})">
                            <i class="fas fa-sync-alt"></i> ⚡ Auto-Generate Monthly Payroll
                        </button>
                    ` : ''}
                </div>
            </div>
        </div>"""

new_month_controls_end = """                <div style="display:flex; gap:10px; align-items:center; flex-wrap:wrap;">
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
        ` : ''}"""

if old_payroll_pre in code:
    code = code.replace(old_payroll_pre, new_payroll_pre)
    print("1. Added accSlip fetch before content template")
else:
    code_norm = code.replace('\r\n', '\n')
    old_norm = old_payroll_pre.replace('\r\n', '\n')
    if old_norm in code_norm:
        code = code_norm.replace(old_norm, new_payroll_pre.replace('\r\n', '\n'))
        print("1. Added accSlip fetch (after normalization)")
    else:
        print("WARNING: old_payroll_pre not found")

if old_month_controls_end in code:
    code = code.replace(old_month_controls_end, new_month_controls_end)
    print("2. Added Accountant personal card and Director sanction card to payroll tab")
else:
    code_norm = code.replace('\r\n', '\n')
    old_norm = old_month_controls_end.replace('\r\n', '\n')
    if old_norm in code_norm:
        code = code_norm.replace(old_norm, new_month_controls_end.replace('\r\n', '\n'))
        print("2. Added Accountant cards (after normalization)")
    else:
        print("WARNING: old_month_controls_end not found")

with open('school_website/js/app.js', 'w', encoding='utf-8') as f:
    f.write(code)

print("Payroll updates completed.")
