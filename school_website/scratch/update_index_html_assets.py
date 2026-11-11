import sys

with open('school_website/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add sidebar link
sidebar_marker = '''                    <li data-tab="lab_complaints">
                        <a href="javascript:void(0)" data-tab="lab_complaints" onclick="showTab('lab_complaints')">
                            <span>🛠️</span> Lab Complaints & Repairs
                        </a>
                    </li>'''

sidebar_new_item = '''                    <li data-tab="lab_complaints">
                        <a href="javascript:void(0)" data-tab="lab_complaints" onclick="showTab('lab_complaints')">
                            <span>🛠️</span> Lab Complaints & Repairs
                        </a>
                    </li>
                    <li data-tab="asset_management">
                        <a href="javascript:void(0)" data-tab="asset_management" onclick="showTab('asset_management')" style="color:#38bdf8; font-weight:700;">
                            <span>💻</span> Laptop & PC Asset Manager
                        </a>
                    </li>'''

if sidebar_marker in html and 'data-tab="asset_management"' not in html:
    html = html.replace(sidebar_marker, sidebar_new_item, 1)
    print("✓ Added Laptop & PC Asset Manager to sidebar in index.html")
else:
    print("! sidebar_marker not found or already added")

# 2. Add Modals before <!-- Application Scripts -->
modals_marker = '    <!-- Application Scripts -->'
modals_code = '''    <!-- ===================================================================== -->
    <!-- IT ASSET MANAGEMENT MODALS (LAPTOP & COMPUTER SYSTEM)                   -->
    <!-- ===================================================================== -->

    <!-- 1. Modal: Register New Laptop / Computer Asset -->
    <div id="modal-add-it-asset" class="modal-overlay">
        <div class="modal-box" style="max-width:680px;">
            <div class="modal-header" style="background:linear-gradient(135deg, #0f172a, #1e3a8a); color:white;">
                <div>
                    <h3 class="modal-title" style="color:white;"><i class="fas fa-laptop"></i> Register New Laptop / Computer Asset</h3>
                    <p style="font-size:0.78rem; color:#bfdbfe; margin-top:2px;">Institutional IT Inventory: Add hardware specifications, serial number & location</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-add-it-asset')" style="color:white;">&times;</button>
            </div>
            <form onsubmit="submitCreateITAsset(event)">
                <div class="modal-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Device Type *</label>
                            <select id="asset-new-type" class="form-control" required onchange="handleDeviceTypeChange(this.value)">
                                <option value="Laptop">💻 Laptop</option>
                                <option value="Desktop Computer">🖥️ Desktop Computer</option>
                                <option value="Workstation">🏢 Workstation / High-End Tower</option>
                                <option value="All-in-One PC">🖥️ All-in-One PC</option>
                                <option value="Tablet / 2-in-1">📱 Tablet / 2-in-1 Convertible</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Brand / Manufacturer *</label>
                            <select id="asset-new-brand" class="form-control" required>
                                <option value="Lenovo">Lenovo</option>
                                <option value="Dell">Dell</option>
                                <option value="HP">HP (Hewlett-Packard)</option>
                                <option value="Apple">Apple</option>
                                <option value="Acer">Acer</option>
                                <option value="ASUS">ASUS</option>
                                <option value="Custom / OEM Assembled">Custom / OEM Assembled</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Model Name / Series *</label>
                            <input type="text" id="asset-new-model" class="form-control" required placeholder="e.g. ThinkPad T14 Gen 4 / Latitude 5430">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Serial Number (S/N) *</label>
                            <input type="text" id="asset-new-serial" class="form-control" required placeholder="e.g. SN-LN-992140" style="font-family:monospace; font-weight:700;">
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Processor (CPU) *</label>
                            <input type="text" id="asset-new-cpu" class="form-control" required placeholder="e.g. Intel Core i5-1345U / Ryzen 5 5500U / Apple M2">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Memory (RAM) *</label>
                            <input type="text" id="asset-new-ram" class="form-control" required placeholder="e.g. 16 GB DDR5 / 16 GB DDR4">
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Storage (Drive) *</label>
                            <input type="text" id="asset-new-storage" class="form-control" required placeholder="e.g. 512 GB NVMe SSD / 1 TB SSD">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Operating System (OS) *</label>
                            <select id="asset-new-os" class="form-control" required>
                                <option value="Windows 11 Pro">Windows 11 Pro (64-bit)</option>
                                <option value="Windows 10 Pro">Windows 10 Pro (64-bit)</option>
                                <option value="macOS Sonoma">macOS Sonoma (Apple Silicon)</option>
                                <option value="Ubuntu 24.04 LTS">Ubuntu 24.04 LTS Linux</option>
                                <option value="Dual Boot (Windows & Linux)">Dual Boot (Windows 11 & Linux)</option>
                                <option value="ChromeOS">ChromeOS</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Ownership Type *</label>
                            <select id="asset-new-ownership" class="form-control" required>
                                <option value="Owned (Institutional Purchase)">Owned (Institutional Purchase)</option>
                                <option value="Rented / Leased from Vendor">Rented / Leased from Vendor</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Initial Physical Condition *</label>
                            <select id="asset-new-condition" class="form-control" required>
                                <option value="Brand New">✨ Brand New in Box</option>
                                <option value="Excellent" selected>⭐ Excellent / Like New</option>
                                <option value="Good">Good / Operational</option>
                                <option value="Fair / Minor Blemishes">Fair / Minor Wear</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Current Storage Location *</label>
                            <input type="text" id="asset-new-location" class="form-control" required value="IT Support Depot" placeholder="e.g. IT Support Depot / Computer Lab 1">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Purchase Date & Cost (₦)</label>
                            <div style="display:flex; gap:8px;">
                                <input type="date" id="asset-new-purchase-date" class="form-control" style="flex:1;">
                                <input type="number" id="asset-new-purchase-cost" class="form-control" placeholder="Cost ₦" style="flex:1;">
                            </div>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Administrative Notes / Hardware Remarks</label>
                        <textarea id="asset-new-notes" class="form-control" rows="2" placeholder="e.g. Purchased with 3-year warranty; includes 65W USB-C charger."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-add-it-asset')">Cancel</button>
                    <button type="submit" class="btn btn-primary" style="background:#0f172a; font-weight:700;"><i class="fas fa-plus"></i> Register Asset</button>
                </div>
            </form>
        </div>
    </div>

    <!-- 2. Modal: Edit IT Asset Details & Movement -->
    <div id="modal-edit-it-asset" class="modal-overlay">
        <div class="modal-box" style="max-width:640px;">
            <div class="modal-header" style="background:#1e40af; color:white;">
                <div>
                    <h3 class="modal-title" style="color:white;"><i class="fas fa-edit"></i> Update Asset Details & Location</h3>
                    <p id="edit-asset-header-tag" style="font-size:0.78rem; color:#bfdbfe; margin-top:2px;">Asset Tag: LAP-2026-001</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-edit-it-asset')" style="color:white;">&times;</button>
            </div>
            <form onsubmit="submitUpdateITAsset(event)">
                <div class="modal-body">
                    <input type="hidden" id="edit-asset-id">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Brand</label>
                            <input type="text" id="edit-asset-brand" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Model Name</label>
                            <input type="text" id="edit-asset-model" class="form-control" required>
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Current Status *</label>
                            <select id="edit-asset-status" class="form-control" required>
                                <option value="In Stock / Available">🟢 In Stock / Available</option>
                                <option value="Allocated to Employee">🔵 Allocated to Employee</option>
                                <option value="On Rental">🟣 On Rental</option>
                                <option value="In Service / Repair">🟠 In Service / Repair</option>
                                <option value="Decommissioned / Retired">⚫ Decommissioned / Retired</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Physical Condition *</label>
                            <select id="edit-asset-condition" class="form-control" required>
                                <option value="Brand New">✨ Brand New</option>
                                <option value="Excellent">⭐ Excellent / Like New</option>
                                <option value="Good">Good / Functional</option>
                                <option value="Fair / Minor Blemishes">Fair / Scratches</option>
                                <option value="Under Repair">⚠️ Under Repair</option>
                                <option value="Damaged">❌ Damaged</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Current Physical Location *</label>
                        <input type="text" id="edit-asset-location" class="form-control" required placeholder="e.g. IT Support Depot / Senior Staff Room">
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Processor Specs</label>
                            <input type="text" id="edit-asset-cpu" class="form-control">
                        </div>
                        <div class="form-group">
                            <label class="form-label">RAM & Storage</label>
                            <input type="text" id="edit-asset-ram-storage" class="form-control" placeholder="e.g. 16GB RAM / 512GB SSD">
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Maintenance / Administrative Notes</label>
                        <textarea id="edit-asset-notes" class="form-control" rows="2"></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-edit-it-asset')">Cancel</button>
                    <button type="submit" class="btn btn-primary" style="background:#1e40af; font-weight:700;">Save Updates</button>
                </div>
            </form>
        </div>
    </div>

    <!-- 3. Modal: Asset Lifecycle History & Full Audit Trail -->
    <div id="modal-it-asset-history" class="modal-overlay">
        <div class="modal-box" style="max-width:760px;">
            <div class="modal-header" style="background:#0f172a; color:white;">
                <div>
                    <h3 class="modal-title" style="color:white;"><i class="fas fa-history"></i> Asset Lifecycle & Tracking Audit Trail</h3>
                    <p id="history-asset-header" style="font-size:0.78rem; color:#94a3b8; margin-top:2px;">Complete chronological timeline of movement, handovers & services</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-it-asset-history')" style="color:white;">&times;</button>
            </div>
            <div class="modal-body" style="max-height:550px; overflow-y:auto; padding:20px;">
                <div id="history-asset-card" style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:14px; margin-bottom:18px;">
                    <!-- Populated dynamically -->
                </div>
                <h5 style="font-size:0.88rem; font-weight:700; color:#1e293b; margin-bottom:12px; border-bottom:2px solid #e2e8f0; padding-bottom:6px;">
                    📜 Movement & Custody Timeline
                </h5>
                <div id="history-timeline-content">
                    <!-- Populated dynamically -->
                </div>
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-primary" onclick="closeModal('modal-it-asset-history')">Close Audit Log</button>
            </div>
        </div>
    </div>

    <!-- 4. Modal: Handover Asset to Employee (Allocation) -->
    <div id="modal-it-handover-asset" class="modal-overlay">
        <div class="modal-box" style="max-width:680px;">
            <div class="modal-header" style="background:linear-gradient(135deg, #1e3a8a, #2563eb); color:white;">
                <div>
                    <h3 class="modal-title" style="color:white;"><i class="fas fa-handshake"></i> Employee Laptop / Computer Handover</h3>
                    <p style="font-size:0.78rem; color:#bfdbfe; margin-top:2px;">Institutional custody issuance: Assign equipment and generate formal Handover Undertaking Slip</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-it-handover-asset')" style="color:white;">&times;</button>
            </div>
            <form onsubmit="submitHandoverITAsset(event)">
                <div class="modal-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Select Available Device *</label>
                            <select id="handover-asset-id" class="form-control" required>
                                <!-- Populated dynamically with available devices -->
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Handover Date *</label>
                            <input type="date" id="handover-date" class="form-control" required>
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Select Faculty / Employee *</label>
                            <select id="handover-employee-id" class="form-control" required onchange="handleHandoverEmployeeSelect(this)">
                                <!-- Populated from siteData.users -->
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Employee Full Name *</label>
                            <input type="text" id="handover-employee-name" class="form-control" required placeholder="Employee Name">
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Employee Role / Designation *</label>
                            <input type="text" id="handover-employee-role" class="form-control" required placeholder="e.g. Senior Teacher / Principal / Accountant">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Department *</label>
                            <input type="text" id="handover-department" class="form-control" required value="Academics & Faculty" placeholder="e.g. Senior Secondary / Admin">
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Expected Return Date (Term / Annual)</label>
                            <input type="date" id="handover-expected-return" class="form-control">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Handover Physical Condition *</label>
                            <select id="handover-condition" class="form-control" required>
                                <option value="Brand New in Box">✨ Brand New in Box</option>
                                <option value="Pristine / Like New" selected>⭐ Pristine / Like New</option>
                                <option value="Good / Tested Working">Good / Tested Working</option>
                                <option value="Minor Cosmetic Wear">Minor Cosmetic Wear</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Accessories & Peripherals Issued *</label>
                        <input type="text" id="handover-accessories" class="form-control" required value="Original 65W USB-C Charger, Heavy Duty Laptop Bag, Wireless Optical Mouse" placeholder="List all accessories provided">
                    </div>

                    <div class="form-group">
                        <label class="form-label">Issuance Purpose & Institutional Undertaking Terms</label>
                        <textarea id="handover-notes" class="form-control" rows="2" placeholder="e.g. Issued for classroom multimedia lessons and academic record keeping. Employee agrees to safeguard device."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-it-handover-asset')">Cancel</button>
                    <button type="submit" class="btn btn-primary" style="background:#1e3a8a; font-weight:700;"><i class="fas fa-check-circle"></i> Complete Handover & Generate Slip</button>
                </div>
            </form>
        </div>
    </div>

    <!-- 5. Modal: Receive Asset Return (Handover Back) -->
    <div id="modal-it-return-asset" class="modal-overlay">
        <div class="modal-box" style="max-width:600px;">
            <div class="modal-header" style="background:#16a34a; color:white;">
                <div>
                    <h3 class="modal-title" style="color:white;"><i class="fas fa-undo"></i> Process Device Return (Handover Back)</h3>
                    <p id="return-asset-header-tag" style="font-size:0.78rem; color:#dcfce7; margin-top:2px;">Check equipment back into IT Support Depot inventory</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-it-return-asset')" style="color:white;">&times;</button>
            </div>
            <form onsubmit="submitReturnITAsset(event)">
                <div class="modal-body">
                    <input type="hidden" id="return-allocation-id">
                    <div id="return-allocation-info" style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:12px; margin-bottom:16px;">
                        <!-- Populated dynamically -->
                    </div>

                    <div class="form-group">
                        <label class="form-label">Inspected Physical & Screen Condition *</label>
                        <select id="return-condition" class="form-control" required>
                            <option value="Excellent">⭐ Excellent / Clean</option>
                            <option value="Good" selected>Good / Normal Operational Wear</option>
                            <option value="Fair / Scratches">Fair / Minor Scratches</option>
                            <option value="Damaged / Needs Repair">⚠️ Damaged / Requires Technician Service</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Return Inspection Checklist</label>
                        <div style="font-size:0.82rem; color:#334155; display:flex; flex-direction:column; gap:6px; background:#f1f5f9; padding:10px 14px; border-radius:6px;">
                            <label style="cursor:pointer;"><input type="checkbox" checked required> Original power adapter / charger returned</label>
                            <label style="cursor:pointer;"><input type="checkbox" checked required> Laptop bag & accessories accounted for</label>
                            <label style="cursor:pointer;"><input type="checkbox" checked required> Display screen, keyboard & trackpad fully operational</label>
                            <label style="cursor:pointer;"><input type="checkbox" checked required> User session logged out & personal data verified</label>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Inspection & Verification Notes</label>
                        <textarea id="return-notes" class="form-control" rows="2" placeholder="e.g. Device returned in clean condition. Battery health 98%. Replaced into depot shelf."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-it-return-asset')">Cancel</button>
                    <button type="submit" class="btn btn-success" style="background:#16a34a; font-weight:700;"><i class="fas fa-check-double"></i> Confirm Return to Depot</button>
                </div>
            </form>
        </div>
    </div>

    <!-- 6. Modal: Register Rental Agreement -->
    <div id="modal-it-add-rental" class="modal-overlay">
        <div class="modal-box" style="max-width:660px;">
            <div class="modal-header" style="background:#7c3aed; color:white;">
                <div>
                    <h3 class="modal-title" style="color:white;"><i class="fas fa-file-contract"></i> Register Hardware Rental Agreement</h3>
                    <p style="font-size:0.78rem; color:#ede9fe; margin-top:2px;">Rental Fleet Management: Vendor agreements, payment terms & schedule</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-it-add-rental')" style="color:white;">&times;</button>
            </div>
            <form onsubmit="submitCreateITRental(event)">
                <div class="modal-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Rental Type *</label>
                            <select id="rental-type" class="form-control" required>
                                <option value="Inward (Rented from Vendor)">Inward (Leased from Vendor for School Use)</option>
                                <option value="Outward (Leased to Client / Staff)">Outward (Leased to Examination Body / Event)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Link to Inventory Device (Optional)</label>
                            <select id="rental-asset-id" class="form-control">
                                <option value="">— Generic / Bulk Fleet Agreement —</option>
                                <!-- Populated dynamically -->
                            </select>
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Vendor / Client Organization Name *</label>
                            <input type="text" id="rental-vendor-name" class="form-control" required placeholder="e.g. Apex IT Infrastructure Ltd">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Contact Phone & Email</label>
                            <input type="text" id="rental-contact" class="form-control" placeholder="+91 761 400 9011 / rentals@vendor.com">
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Agreement Start Date *</label>
                            <input type="date" id="rental-start-date" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Agreement End Date *</label>
                            <input type="date" id="rental-end-date" class="form-control" required>
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Billing Cycle *</label>
                            <select id="rental-billing-cycle" class="form-control" required>
                                <option value="Monthly">Monthly</option>
                                <option value="Quarterly">Quarterly</option>
                                <option value="Half-Yearly">Half-Yearly</option>
                                <option value="Annually">Annually</option>
                                <option value="Project Basis">Project Basis (One-time)</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Rental Amount per Cycle (₦) *</label>
                            <input type="number" id="rental-amount" class="form-control" required placeholder="e.g. 45000">
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Security Deposit (₦)</label>
                            <input type="number" id="rental-deposit" class="form-control" value="0" placeholder="e.g. 50000">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Next Payment Due Date *</label>
                            <input type="date" id="rental-next-due" class="form-control" required>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Terms & Conditions / Agreement Notes</label>
                        <textarea id="rental-terms" class="form-control" rows="2" placeholder="e.g. Includes onsite replacement within 24 hours. Maintenance covered by vendor."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-it-add-rental')">Cancel</button>
                    <button type="submit" class="btn btn-primary" style="background:#7c3aed; font-weight:700;"><i class="fas fa-check"></i> Register Agreement & Payment Reminder</button>
                </div>
            </form>
        </div>
    </div>

    <!-- 7. Modal: Record Payment for Rental / AMC / Repair -->
    <div id="modal-it-record-payment" class="modal-overlay">
        <div class="modal-box" style="max-width:550px;">
            <div class="modal-header" style="background:#059669; color:white;">
                <div>
                    <h3 class="modal-title" style="color:white;"><i class="fas fa-credit-card"></i> Record Asset Payment Settlement</h3>
                    <p style="font-size:0.78rem; color:#d1fae5; margin-top:2px;">Discharge rental installment, AMC renewal or hardware repair invoice</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-it-record-payment')" style="color:white;">&times;</button>
            </div>
            <form onsubmit="submitRecordITPayment(event)">
                <div class="modal-body">
                    <input type="hidden" id="pay-record-id">
                    <div id="pay-record-info" style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:12px; margin-bottom:16px;">
                        <!-- Populated dynamically -->
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Payment Date *</label>
                            <input type="date" id="pay-record-date" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Payment Method *</label>
                            <select id="pay-record-method" class="form-control" required>
                                <option value="Bank Transfer / NEFT">Bank Transfer / NEFT</option>
                                <option value="Cheque / Draft">Cheque / Demand Draft</option>
                                <option value="Corporate Card">Corporate Debit / Credit Card</option>
                                <option value="UPI / QR Payment">UPI / QR Payment</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Transaction Reference / Cheque No. *</label>
                        <input type="text" id="pay-record-txref" class="form-control" required placeholder="e.g. NEFT-GS-9901428 / CHQ-104928" style="font-family:monospace; font-weight:700;">
                    </div>

                    <div class="form-group">
                        <label class="form-label">Bursar Remarks / Payment Voucher Notes</label>
                        <textarea id="pay-record-notes" class="form-control" rows="2" placeholder="e.g. Settled via First Bank of Nigeria school corporate account. Receipt filed."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-it-record-payment')">Cancel</button>
                    <button type="submit" class="btn btn-success" style="background:#059669; font-weight:700;"><i class="fas fa-check-circle"></i> Confirm Payment Settlement</button>
                </div>
            </form>
        </div>
    </div>

    <!-- 8. Modal: Add / Renew Warranty & AMC -->
    <div id="modal-it-add-warranty" class="modal-overlay">
        <div class="modal-box" style="max-width:620px;">
            <div class="modal-header" style="background:#0284c7; color:white;">
                <div>
                    <h3 class="modal-title" style="color:white;"><i class="fas fa-shield-alt"></i> Register Warranty / AMC Policy</h3>
                    <p style="font-size:0.78rem; color:#e0f2fe; margin-top:2px;">OEM Standard Warranty, Annual Maintenance Contract (AMC) & Coverage</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-it-add-warranty')" style="color:white;">&times;</button>
            </div>
            <form onsubmit="submitCreateITWarranty(event)">
                <div class="modal-body">
                    <div class="form-group">
                        <label class="form-label">Select Equipment Asset *</label>
                        <select id="warranty-asset-id" class="form-control" required>
                            <!-- Populated dynamically -->
                        </select>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Provider Name *</label>
                            <input type="text" id="warranty-provider" class="form-control" required placeholder="e.g. Dell ProSupport / HP Care Pack / AppleCare+">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Policy / Contract Number *</label>
                            <input type="text" id="warranty-policy-no" class="form-control" required placeholder="e.g. DEL-PSP-88319" style="font-family:monospace; font-weight:700;">
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Warranty / Contract Type *</label>
                        <select id="warranty-type" class="form-control" required>
                            <option value="OEM Standard + Onsite Support">OEM Standard Hardware + Onsite NBD Support</option>
                            <option value="Accidental Damage Protection (ADP)">Accidental Damage Protection (ADP)</option>
                            <option value="Extended Annual Maintenance Contract (AMC)">Extended Annual Maintenance Contract (AMC)</option>
                            <option value="Comprehensive 3-Year Corporate Coverage">Comprehensive 3-Year Corporate Coverage</option>
                        </select>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Coverage Start Date *</label>
                            <input type="date" id="warranty-start-date" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Coverage End Date *</label>
                            <input type="date" id="warranty-end-date" class="form-control" required>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Direct Support Contact (Toll-Free / Email) *</label>
                        <input type="text" id="warranty-contact" class="form-control" required placeholder="e.g. 1800-425-4026 / prosupport@dell.com">
                    </div>

                    <div class="form-group">
                        <label class="form-label">Coverage Inclusions & Policy Notes</label>
                        <textarea id="warranty-notes" class="form-control" rows="2" placeholder="e.g. Covers motherboard, screen, battery, and unlimited parts replacement."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-it-add-warranty')">Cancel</button>
                    <button type="submit" class="btn btn-primary" style="background:#0284c7; font-weight:700;"><i class="fas fa-shield-alt"></i> Save Warranty Policy</button>
                </div>
            </form>
        </div>
    </div>

    <!-- 9. Modal: Log Maintenance / Service Ticket -->
    <div id="modal-it-log-service" class="modal-overlay">
        <div class="modal-box" style="max-width:640px;">
            <div class="modal-header" style="background:#ea580c; color:white;">
                <div>
                    <h3 class="modal-title" style="color:white;"><i class="fas fa-tools"></i> Log Hardware Maintenance & Service Ticket</h3>
                    <p style="font-size:0.78rem; color:#ffedd5; margin-top:2px;">Dispatches device to service center or internal diagnostics lab</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-it-log-service')" style="color:white;">&times;</button>
            </div>
            <form onsubmit="submitLogITService(event)">
                <div class="modal-body">
                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Select Equipment Asset *</label>
                            <select id="service-asset-id" class="form-control" required>
                                <!-- Populated dynamically -->
                            </select>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Service Type *</label>
                            <select id="service-type" class="form-control" required>
                                <option value="Hardware Repair / Display Screen">Hardware Repair (Screen / Panel)</option>
                                <option value="Hardware Repair / Motherboard & GPU">Hardware Repair (Motherboard / GPU / Power)</option>
                                <option value="Battery / Power Charging System">Battery / Power Adapter Fault</option>
                                <option value="Keyboard & Trackpad Replacement">Keyboard / Trackpad Replacement</option>
                                <option value="RAM / SSD Storage Upgrade">Hardware Upgrade (RAM / SSD)</option>
                                <option value="OS & Firmware Reinstallation">OS, BIOS & Software Re-imaging</option>
                                <option value="Preventive Maintenance & Thermal Cleaning">Preventive Maintenance & Thermal Paste</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Reported Symptoms & Hardware Defect *</label>
                        <textarea id="service-issue" class="form-control" rows="2" required placeholder="Describe exact symptoms, error codes, or damage observed."></textarea>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Authorized Service Center / Vendor *</label>
                            <input type="text" id="service-center" class="form-control" required value="HP / Dell Authorized Service Hub" placeholder="e.g. Authorized Depot / Internal Lab">
                        </div>
                        <div class="form-group">
                            <label class="form-label">Assigned Technician Name</label>
                            <input type="text" id="service-tech-name" class="form-control" placeholder="e.g. Technician Rajesh Kumar">
                        </div>
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Service Dispatch Date *</label>
                            <input type="date" id="service-start-date" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Estimated Repair Cost (₦)</label>
                            <input type="number" id="service-cost" class="form-control" value="0" placeholder="e.g. 15000">
                        </div>
                    </div>

                    <div class="form-group" style="background:#fff7ed; border:1px solid #fed7aa; padding:10px 14px; border-radius:6px;">
                        <label style="cursor:pointer; display:flex; align-items:center; gap:8px; font-size:0.84rem; color:#9a3412; font-weight:700;">
                            <input type="checkbox" id="service-warranty-covered" checked>
                            🛡️ Check if repair is expected to be covered under active OEM Warranty / AMC (Zero Cost)
                        </label>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-it-log-service')">Cancel</button>
                    <button type="submit" class="btn btn-primary" style="background:#ea580c; font-weight:700;"><i class="fas fa-wrench"></i> Open Service Ticket & Move Device</button>
                </div>
            </form>
        </div>
    </div>

    <!-- 10. Modal: Mark Maintenance Service Completed -->
    <div id="modal-it-complete-service" class="modal-overlay">
        <div class="modal-box" style="max-width:580px;">
            <div class="modal-header" style="background:#16a34a; color:white;">
                <div>
                    <h3 class="modal-title" style="color:white;"><i class="fas fa-check-circle"></i> Complete Service & Return to Depot</h3>
                    <p id="complete-service-header-ticket" style="font-size:0.78rem; color:#dcfce7; margin-top:2px;">Verify repairs, test hardware and restore asset to inventory</p>
                </div>
                <button class="modal-close" onclick="closeModal('modal-it-complete-service')" style="color:white;">&times;</button>
            </div>
            <form onsubmit="submitCompleteITService(event)">
                <div class="modal-body">
                    <input type="hidden" id="complete-service-ticket-id">
                    <div id="complete-service-info" style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:12px; margin-bottom:16px;">
                        <!-- Populated dynamically -->
                    </div>

                    <div class="form-grid">
                        <div class="form-group">
                            <label class="form-label">Completion Date *</label>
                            <input type="date" id="complete-service-date" class="form-control" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Final Actual Repair Cost (₦)</label>
                            <input type="number" id="complete-service-cost" class="form-control" value="0" placeholder="0 if covered by warranty">
                        </div>
                    </div>

                    <div class="form-group">
                        <label class="form-label">Parts Replaced / Hardware Installed</label>
                        <input type="text" id="complete-service-parts" class="form-control" placeholder="e.g. System Motherboard Part #HP-MB-800G6, Thermal Paste">
                    </div>

                    <div class="form-group">
                        <label class="form-label">Return Destination Location *</label>
                        <input type="text" id="complete-service-location" class="form-control" required value="IT Support Depot">
                    </div>

                    <div class="form-group">
                        <label class="form-label">Technician Diagnostic & Operational Test Results</label>
                        <textarea id="complete-service-remarks" class="form-control" rows="2" placeholder="e.g. POST passed, 24-hour burn-in stress test passed with zero errors. Restored to depot."></textarea>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-outline" onclick="closeModal('modal-it-complete-service')">Cancel</button>
                    <button type="submit" class="btn btn-success" style="background:#16a34a; font-weight:700;"><i class="fas fa-check-double"></i> Mark Completed & Restore Asset</button>
                </div>
            </form>
        </div>
    </div>
'''

if modals_marker in html and 'id="modal-add-it-asset"' not in html:
    html = html.replace(modals_marker, modals_code + '\n' + modals_marker, 1)
    print("✓ Added 10 Asset Management Modals to index.html")
else:
    print("! modals_marker not found or already added")

with open('school_website/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Updated index.html successfully!")
