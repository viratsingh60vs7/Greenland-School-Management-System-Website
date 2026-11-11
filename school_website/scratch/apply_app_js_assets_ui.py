import sys

# Create the comprehensive Asset Management JavaScript functions
js_code = '''

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

    const csvContent = "data:text/csv;charset=utf-8," + rows.map(e => e.map(x => `"${(x + '').replace(/"/g, '""')}"`).join(",")).join("\\n");
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
'''

with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    orig = f.read()

if 'function renderAssetManagementTab' not in orig:
    with open('school_website/js/app.js', 'a', encoding='utf-8') as f:
        f.write('\n' + js_code)
    print("✓ Appended Asset Management UI code to app.js!")
else:
    print("! renderAssetManagementTab already in app.js")
