with open('school_website/server.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. it_assets/delete: accept id or asset_id
code = code.replace(
    "asset_id = body.get('id')",
    "asset_id = body.get('id') or body.get('asset_id')"
)

# 2. it_allocations/handover: capture alloc_id right after INSERT INTO it_asset_allocations
old_alloc_insert = '''                cur.execute("""
                    INSERT INTO it_asset_allocations (
                        handover_slip_no, asset_id, employee_id, employee_name, employee_role, department,
                        handover_date, expected_return_date, handover_condition, accessories_included,
                        handover_notes, handover_status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active (With Employee)', ?)
                """, (slip_no, asset_id, employee_id, employee_name, employee_role, department, handover_date, expected_return, condition, accessories, notes, now))'''

new_alloc_insert = '''                cur.execute("""
                    INSERT INTO it_asset_allocations (
                        handover_slip_no, asset_id, employee_id, employee_name, employee_role, department,
                        handover_date, expected_return_date, handover_condition, accessories_included,
                        handover_notes, handover_status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active (With Employee)', ?)
                """, (slip_no, asset_id, employee_id, employee_name, employee_role, department, handover_date, expected_return, condition, accessories, notes, now))
                alloc_id = cur.lastrowid'''

if old_alloc_insert in code:
    code = code.replace(old_alloc_insert, new_alloc_insert, 1)

# 3. it_maintenance/create: capture ticket_id right after INSERT INTO it_maintenance_service
old_maint_insert = '''                cur.execute("""
                    INSERT INTO it_maintenance_service (
                        service_ticket_no, asset_id, service_type, reported_issue, service_center_or_vendor,
                        technician_name, start_date, repair_cost, service_status, warranty_claim_covered, remarks, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'In Repair / Awaiting Parts', ?, ?, ?)
                """, (ticket_no, asset_id, s_type, issue, center, tech, start_d, cost, is_warranty, remarks, now))'''

new_maint_insert = '''                cur.execute("""
                    INSERT INTO it_maintenance_service (
                        service_ticket_no, asset_id, service_type, reported_issue, service_center_or_vendor,
                        technician_name, start_date, repair_cost, service_status, warranty_claim_covered, remarks, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'In Repair / Awaiting Parts', ?, ?, ?)
                """, (ticket_no, asset_id, s_type, issue, center, tech, start_d, cost, is_warranty, remarks, now))
                ticket_id = cur.lastrowid'''

if old_maint_insert in code:
    code = code.replace(old_maint_insert, new_maint_insert, 1)

with open('school_website/server.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ Successfully patched rowids and delete asset parameter!")
