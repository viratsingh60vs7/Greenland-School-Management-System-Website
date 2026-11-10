import sqlite3
from datetime import datetime

def setup_db():
    conn = sqlite3.connect('school_website/school.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # 1. Create it_assets
    cur.execute("""
    CREATE TABLE IF NOT EXISTS it_assets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_tag TEXT UNIQUE NOT NULL,
        device_type TEXT NOT NULL,
        brand TEXT NOT NULL,
        model_name TEXT NOT NULL,
        serial_number TEXT UNIQUE,
        specs_processor TEXT,
        specs_ram TEXT,
        specs_storage TEXT,
        specs_os TEXT,
        ownership_type TEXT DEFAULT 'Owned (Institutional Purchase)',
        condition TEXT DEFAULT 'Excellent',
        purchase_date TEXT,
        purchase_cost REAL DEFAULT 0.0,
        current_location TEXT DEFAULT 'IT Support Depot',
        status TEXT DEFAULT 'In Stock / Available',
        notes TEXT,
        created_at TEXT
    )
    """)

    # 2. Create it_rentals
    cur.execute("""
    CREATE TABLE IF NOT EXISTS it_rentals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rental_agreement_no TEXT UNIQUE NOT NULL,
        rental_type TEXT DEFAULT 'Inward (Rented from Vendor)',
        asset_id INTEGER,
        vendor_or_client_name TEXT NOT NULL,
        contact_phone TEXT,
        contact_email TEXT,
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        billing_cycle TEXT DEFAULT 'Monthly',
        rental_amount REAL DEFAULT 0.0,
        deposit_amount REAL DEFAULT 0.0,
        next_payment_due_date TEXT,
        payment_status TEXT DEFAULT 'Current / Up to Date',
        rental_status TEXT DEFAULT 'Active Agreement',
        terms_notes TEXT,
        created_at TEXT
    )
    """)

    # 3. Create it_asset_allocations
    cur.execute("""
    CREATE TABLE IF NOT EXISTS it_asset_allocations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        handover_slip_no TEXT UNIQUE NOT NULL,
        asset_id INTEGER NOT NULL,
        employee_id INTEGER,
        employee_name TEXT NOT NULL,
        employee_role TEXT NOT NULL,
        department TEXT DEFAULT 'Academics & Faculty',
        handover_date TEXT NOT NULL,
        expected_return_date TEXT,
        actual_return_date TEXT,
        handover_condition TEXT DEFAULT 'Pristine / Like New',
        accessories_included TEXT DEFAULT 'Original Charger, Laptop Bag, Wireless Mouse',
        handover_notes TEXT,
        handover_status TEXT DEFAULT 'Active (With Employee)',
        return_condition TEXT,
        return_verified_by TEXT,
        created_at TEXT,
        FOREIGN KEY (asset_id) REFERENCES it_assets(id)
    )
    """)

    # 4. Create it_warranties
    cur.execute("""
    CREATE TABLE IF NOT EXISTS it_warranties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER NOT NULL,
        provider_name TEXT NOT NULL,
        policy_number TEXT NOT NULL,
        warranty_type TEXT DEFAULT 'OEM Standard Warranty',
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        support_contact TEXT,
        status TEXT DEFAULT 'Active',
        claim_count INTEGER DEFAULT 0,
        notes TEXT,
        created_at TEXT,
        FOREIGN KEY (asset_id) REFERENCES it_assets(id)
    )
    """)

    # 5. Create it_maintenance_service
    cur.execute("""
    CREATE TABLE IF NOT EXISTS it_maintenance_service (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_ticket_no TEXT UNIQUE NOT NULL,
        asset_id INTEGER NOT NULL,
        service_type TEXT NOT NULL,
        reported_issue TEXT NOT NULL,
        service_center_or_vendor TEXT NOT NULL,
        technician_name TEXT,
        start_date TEXT NOT NULL,
        completion_date TEXT,
        repair_cost REAL DEFAULT 0.0,
        parts_replaced TEXT,
        service_status TEXT DEFAULT 'Under Diagnostics',
        warranty_claim_covered INTEGER DEFAULT 0,
        remarks TEXT,
        created_at TEXT,
        FOREIGN KEY (asset_id) REFERENCES it_assets(id)
    )
    """)

    # 6. Create it_asset_payments
    cur.execute("""
    CREATE TABLE IF NOT EXISTS it_asset_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ref_no TEXT UNIQUE NOT NULL,
        payment_category TEXT NOT NULL,
        related_rental_id INTEGER,
        related_service_id INTEGER,
        vendor_name TEXT NOT NULL,
        amount REAL NOT NULL,
        due_date TEXT NOT NULL,
        paid_date TEXT,
        payment_status TEXT DEFAULT 'Upcoming Due',
        payment_method TEXT,
        transaction_ref TEXT,
        notes TEXT,
        created_at TEXT
    )
    """)

    # 7. Create it_asset_logs
    cur.execute("""
    CREATE TABLE IF NOT EXISTS it_asset_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        asset_id INTEGER NOT NULL,
        action_type TEXT NOT NULL,
        from_location TEXT,
        to_location TEXT,
        assigned_to TEXT,
        performed_by TEXT,
        details TEXT,
        timestamp TEXT,
        FOREIGN KEY (asset_id) REFERENCES it_assets(id)
    )
    """)

    conn.commit()

    # Seed data if empty
    cur.execute("SELECT COUNT(*) FROM it_assets")
    if cur.fetchone()[0] == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1. Assets
        assets = [
            ('LAP-2026-001', 'Laptop', 'Lenovo', 'ThinkPad T14 Gen 4', 'SN-LN-992140', 'Intel Core i5-1345U (10 Cores, up to 4.7GHz)', '16 GB DDR5 5200MHz', '512 GB NVMe PCIe 4.0 SSD', 'Windows 11 Pro (64-bit)', 'Owned (Institutional Purchase)', 'Excellent', '2026-01-15', 1250000.0, 'Director Executive Office', 'Allocated to Employee', 'Assigned to Director Rajeev Sinha for institutional leadership and administrative governance.', now),
            ('LAP-2026-002', 'Laptop', 'Dell', 'Latitude 5430 Business Edition', 'SN-DL-883192', 'Intel Core i5-1235U (10 Cores, up to 4.4GHz)', '16 GB DDR4 3200MHz', '512 GB NVMe M.2 SSD', 'Windows 11 Pro', 'Owned (Institutional Purchase)', 'Like New', '2026-02-10', 980000.0, 'IT Support Depot', 'Allocated to Employee', 'Assigned to IT Support Administrator for network and system infrastructure management.', now),
            ('LAP-2026-003', 'Laptop', 'HP', 'ProBook 450 G9 Business Laptop', 'SN-HP-771234', 'Intel Core i5-1235U', '8 GB DDR4', '512 GB NVMe SSD', 'Windows 11 Pro', 'Owned (Institutional Purchase)', 'Excellent', '2026-03-01', 820000.0, 'IT Support Depot', 'In Stock / Available', 'Available in IT Support Depot for immediate faculty or exam allocation.', now),
            ('LAP-2026-004', 'Laptop', 'Lenovo', 'ThinkPad E14 Gen 3', 'SN-LN-441209', 'AMD Ryzen 5 5500U (6 Cores / 12 Threads)', '16 GB DDR4', '512 GB NVMe SSD', 'Windows 11 Pro', 'Rented / Leased from Vendor', 'Good', '2026-10-01', 0.0, 'Senior Computer Science Arm', 'On Rental', 'Leased under Vendor Agreement RNT-2026-001 with Apex IT Infrastructure Ltd for STEM and coding labs.', now),
            ('LAP-2026-005', 'Laptop', 'Apple', 'MacBook Air M2 13.6-inch', 'SN-AP-M28912', 'Apple M2 Chip (8-Core CPU / 8-Core GPU)', '16 GB Unified Memory', '256 GB Fast SSD', 'macOS Sonoma 14.5', 'Owned (Institutional Purchase)', 'Excellent', '2026-01-20', 1450000.0, 'Faculty Staff Room', 'Allocated to Employee', 'Assigned to Teacher Chike for Senior Secondary lesson preparation and digital curriculum.', now),
            ('PC-2026-001', 'Desktop Computer', 'Dell', 'OptiPlex 7090 Micro Desktop', 'SN-DL-OP7090', 'Intel Core i7-11700 (8 Cores, 2.5GHz to 4.9GHz)', '16 GB DDR4', '1 TB NVMe SSD', 'Windows 11 Pro', 'Owned (Institutional Purchase)', 'Good', '2025-11-10', 750000.0, 'Accounts & Bursar Office', 'Allocated to Employee', 'Dedicated workstation assigned to Accountant Jude Bello for school fees, ledger, and payroll processing.', now),
            ('PC-2026-002', 'Desktop Computer', 'HP', 'EliteDesk 800 G6 Tower Workstation', 'SN-HP-ED800G', 'Intel Core i5-10500', '16 GB DDR4', '512 GB SSD + 1 TB HDD', 'Windows 10 Pro', 'Owned (Institutional Purchase)', 'Under Repair', '2025-08-15', 680000.0, 'HP Authorized Service Depot', 'In Service / Repair', 'Motherboard onboard video display failure; ticket SVC-2026-001 opened with HP Support Center.', now),
            ('PC-2026-003', 'Workstation', 'Acer', 'Veriton S2680G Compact Desktop', 'SN-AC-VT2680', 'Intel Core i5-11400', '16 GB DDR4', '512 GB NVMe SSD', 'Windows 11 Pro', 'Owned (Institutional Purchase)', 'Excellent', '2026-02-28', 580000.0, 'IT Support Depot', 'In Stock / Available', 'General spare workstation available in IT Support inventory.', now)
        ]

        cur.executemany("""
            INSERT INTO it_assets (
                asset_tag, device_type, brand, model_name, serial_number, specs_processor, specs_ram,
                specs_storage, specs_os, ownership_type, condition, purchase_date, purchase_cost,
                current_location, status, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, assets)

        # 2. Allocations
        cur.execute("SELECT id FROM users WHERE username = 'Owner(Directer)' LIMIT 1")
        dir_row = cur.fetchone()
        dir_id = dir_row[0] if dir_row else 27

        cur.execute("SELECT id FROM users WHERE username = 'GS_itsupport' LIMIT 1")
        it_row = cur.fetchone()
        it_id = it_row[0] if it_row else 37

        allocations = [
            ('HND-2026-001', 1, dir_id, 'Owner (Director) Rajeev Sinha', 'Director (Owner)', 'Executive Directorate', '2026-01-20', '2027-01-20', None, 'Pristine / Like New', '65W USB-C Fast Charger, Premium Executive Leather Briefcase, Wireless Bluetooth Mouse, USB-C Multiport Hub', 'Institutional executive issuance authorized by Directorate. Full administrative privileges enabled.', 'Active (With Employee)', None, None, now),
            ('HND-2026-002', 2, it_id, 'IT Support Administrator', 'IT Support Administrator', 'IT & Systems Administration', '2026-02-15', '2027-02-15', None, 'Brand New in Box', '65W USB-C Charger, Heavy Duty Water-Resistant Bag, Cat6 Ethernet Cable, Console Cable', 'Primary IT Support Administrator diagnostic and management workstation.', 'Active (With Employee)', None, None, now),
            ('HND-2026-003', 5, 55, 'Teacher Chike', 'Teacher', 'Senior Secondary Academics', '2026-02-01', '2026-12-15', None, 'Pristine / Like New', '35W Dual USB-C Adapter, Apple MagSafe 3 Cable, Laptop Sleeve', 'Class Teacher and Senior Secondary English curriculum planning issuance.', 'Active (With Employee)', None, None, now),
            ('HND-2026-004', 6, 83, 'Accountant Jude Bello', 'Accountant', 'Finance & Bursar Department', '2025-11-15', '2026-11-30', None, 'Good', 'Dell 24-inch UltraSharp Monitor, Keyboard, Optical Mouse, Power Cords', 'Dedicated desktop workstation for Greenland School fee ledger and accounting.', 'Active (With Employee)', None, None, now)
        ]

        cur.executemany("""
            INSERT INTO it_asset_allocations (
                handover_slip_no, asset_id, employee_id, employee_name, employee_role, department,
                handover_date, expected_return_date, actual_return_date, handover_condition,
                accessories_included, handover_notes, handover_status, return_condition,
                return_verified_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, allocations)

        # 3. Rental Agreement
        cur.execute("""
            INSERT INTO it_rentals (
                rental_agreement_no, rental_type, asset_id, vendor_or_client_name, contact_phone, contact_email,
                start_date, end_date, billing_cycle, rental_amount, deposit_amount, next_payment_due_date,
                payment_status, rental_status, terms_notes, created_at
            ) VALUES (
                'RNT-2026-001', 'Inward (Rented from Vendor)', 4, 'Apex IT Infrastructure Solutions Ltd',
                '+91 761 400 9011', 'rentals@apexinfotech.com', '2026-10-01', '2027-03-31',
                'Monthly', 45000.0, 50000.0, '2026-11-15', 'Due Soon', 'Active Agreement',
                'Term leasing for 5 Lenovo ThinkPad units for senior STEM coding labs and examination simulation.', ?
            )
        """, (now,))

        # 4. Warranties
        warranties = [
            (1, 'Lenovo Premier Support & Onsite Warranty', 'LEN-PREM-90214', 'OEM Standard + Onsite Next Business Day', '2026-01-15', '2029-01-14', '1800-419-7555 / support@lenovo.com', 'Active', 0, 'Covers motherboard, battery, screen, and all internal hardware components.', now),
            (2, 'Dell ProSupport Plus 3-Year Onsite', 'DEL-PSP-88319', 'OEM Standard + Accidental Damage Protection', '2026-02-10', '2029-02-09', '1800-425-4026 / prosupport@dell.com', 'Active', 0, '24x7 priority support with onsite technician dispatch within 4 hours.', now),
            (5, 'AppleCare+ for Mac (3 Years)', 'AC-MAC-M2891', 'OEM Comprehensive + Accidental Coverage', '2026-01-20', '2029-01-19', '000800 1009009 / applecare@apple.com', 'Active', 0, 'Comprehensive coverage with unlimited accidental damage incidents.', now),
            (7, 'HP Care Pack 3-Year Commercial Warranty', 'HP-CP-ED800G', 'OEM Standard Hardware Support', '2023-11-25', '2026-11-25', '1800-258-7170 / support@hp.com', 'Expiring Soon (< 30 Days)', 1, 'Expiring in less than 30 days! Renewal or AMC extension required.', now)
        ]
        cur.executemany("""
            INSERT INTO it_warranties (
                asset_id, provider_name, policy_number, warranty_type, start_date, end_date,
                support_contact, status, claim_count, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, warranties)

        # 5. Maintenance Service Tickets
        cur.execute("""
            INSERT INTO it_maintenance_service (
                service_ticket_no, asset_id, service_type, reported_issue, service_center_or_vendor,
                technician_name, start_date, completion_date, repair_cost, parts_replaced,
                service_status, warranty_claim_covered, remarks, created_at
            ) VALUES (
                'SVC-2026-001', 7, 'Hardware Repair / Display GPU', 'Display output no signal through HDMI / DisplayPort. System fans spin but POST fails.',
                'HP Authorized Service Center (Sonbhadra Hub)', 'Technician Rajesh Kumar (Badge #HP-912)',
                '2026-11-01', NULL, 18500.0, 'Awaiting replacement system board part #HP-MB-800G6',
                'In Repair / Awaiting Parts', 1, 'Claim submitted under HP Care Pack. Estimated dispatch Nov 12.', ?
            )
        """, (now,))

        # 6. Payment Reminders
        payments = [
            ('PMT-2026-001', 'Rental Invoice', 1, None, 'Apex IT Infrastructure Solutions Ltd', 45000.0, '2026-11-15', None, 'Upcoming Due', None, None, 'Monthly lease installment for November 2026 under agreement RNT-2026-001.', now),
            ('PMT-2026-002', 'AMC Renewal', None, None, 'CompServe Technology Solutions Ltd', 120000.0, '2026-11-20', None, 'Upcoming Due', None, None, 'Annual Maintenance Contract renewal for Computer Lab 1 & Lab 2 core switching & UPS equipment.', now),
            ('PMT-2026-003', 'Hardware Repair Bill', None, 1, 'HP Authorized Service Hub', 4500.0, '2026-11-08', '2026-11-04', 'Paid', 'Bank Transfer / NEFT', 'NEFT-GS-9901428', 'Out-of-warranty labor and thermal compound diagnostic charge.', now)
        ]
        cur.executemany("""
            INSERT INTO it_asset_payments (
                ref_no, payment_category, related_rental_id, related_service_id, vendor_name,
                amount, due_date, paid_date, payment_status, payment_method, transaction_ref, notes, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, payments)

        # 7. Asset Logs
        logs = [
            (1, 'Asset Registered / Added to Inventory', 'Vendor Delivery', 'IT Support Depot', 'IT Support Administrator', 'IT Support Administrator', 'Initial procurement check passed. Specs verified: i5-1345U / 16GB / 512GB SSD.', '2026-01-15 10:00:00'),
            (1, 'Handover to Employee', 'IT Support Depot', 'Director Executive Office', 'Owner (Director) Rajeev Sinha', 'IT Support Administrator', 'Formally allocated under Handover Slip HND-2026-001.', '2026-01-20 11:30:00'),
            (2, 'Asset Registered / Added to Inventory', 'Vendor Delivery', 'IT Support Depot', 'IT Support Administrator', 'IT Support Administrator', 'Dell Latitude 5430 deployed for IT Administrator management workstation.', '2026-02-10 09:15:00'),
            (5, 'Handover to Employee', 'IT Support Depot', 'Faculty Staff Room', 'Teacher Chike', 'IT Support Administrator', 'Allocated for Senior Secondary lesson planning.', '2026-02-01 14:00:00'),
            (7, 'Dispatched to Service Center', 'Accounts Office', 'HP Authorized Service Depot', 'HP Technician Rajesh Kumar', 'IT Support Administrator', 'Dispatched for motherboard diagnostics under ticket SVC-2026-001.', '2026-11-01 16:45:00')
        ]
        cur.executemany("""
            INSERT INTO it_asset_logs (
                asset_id, action_type, from_location, to_location, assigned_to, performed_by, details, timestamp
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, logs)

        conn.commit()
        print("✓ Successfully created tables and seeded IT Assets data!")
    else:
        print("✓ Tables already present and populated.")

    conn.close()

if __name__ == '__main__':
    setup_db()
