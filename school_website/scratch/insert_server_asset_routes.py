import sys

with open('school_website/server.py', 'r', encoding='utf-8') as f:
    code = f.read()

# Marker in do_GET
get_marker = '            else:\n                self.send_json({"error": "Endpoint not found"}, 404)'
get_routes = '''            # =====================================================================
            # LAPTOP & COMPUTER ASSET MANAGEMENT GET ENDPOINTS
            # =====================================================================
            elif path == '/api/it_assets':
                device_type = query.get('device_type', ['all'])[0]
                status_f = query.get('status', ['all'])[0]
                ownership_f = query.get('ownership', ['all'])[0]
                search = query.get('search', [''])[0].strip().lower()

                sql = """
                    SELECT a.*, 
                           alc.employee_name as allocated_to,
                           alc.employee_role,
                           alc.handover_slip_no,
                           r.rental_agreement_no,
                           r.vendor_or_client_name as rental_vendor
                    FROM it_assets a
                    LEFT JOIN it_asset_allocations alc ON a.id = alc.asset_id AND alc.handover_status = 'Active (With Employee)'
                    LEFT JOIN it_rentals r ON a.id = r.asset_id AND r.rental_status = 'Active Agreement'
                    WHERE 1=1
                """
                params = []
                if device_type != 'all' and device_type:
                    sql += " AND a.device_type = ?"
                    params.append(device_type)
                if status_f != 'all' and status_f:
                    sql += " AND a.status = ?"
                    params.append(status_f)
                if ownership_f != 'all' and ownership_f:
                    sql += " AND a.ownership_type LIKE ?"
                    params.append(f"%{ownership_f}%")
                if search:
                    sql += " AND (LOWER(a.asset_tag) LIKE ? OR LOWER(a.brand) LIKE ? OR LOWER(a.model_name) LIKE ? OR LOWER(a.serial_number) LIKE ? OR LOWER(a.current_location) LIKE ?)"
                    s_param = f"%{search}%"
                    params.extend([s_param, s_param, s_param, s_param, s_param])
                
                sql += " ORDER BY a.id ASC"
                cur.execute(sql, params)
                assets = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT COUNT(*) FROM it_assets")
                total = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE device_type = 'Laptop'")
                laptops = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE device_type LIKE '%Desktop%' OR device_type = 'Workstation'")
                desktops = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE status = 'In Stock / Available'")
                available = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE status = 'Allocated to Employee'")
                allocated = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE status = 'On Rental'")
                on_rent = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE status = 'In Service / Repair'")
                in_service = cur.fetchone()[0]
                cur.execute("SELECT COALESCE(SUM(purchase_cost), 0) FROM it_assets WHERE ownership_type LIKE '%Owned%'")
                total_val = cur.fetchone()[0]

                self.send_json({
                    "assets": assets,
                    "summary": {
                        "total": total,
                        "laptops": laptops,
                        "desktops": desktops,
                        "available": available,
                        "allocated": allocated,
                        "on_rent": on_rent,
                        "in_service": in_service,
                        "total_valuation": total_val
                    }
                })

            elif path == '/api/it_assets/history':
                asset_id = query.get('asset_id', [None])[0]
                if not asset_id:
                    self.send_json({"error": "asset_id is required"}, 400)
                    return
                
                cur.execute("SELECT * FROM it_assets WHERE id = ?", (asset_id,))
                asset = cur.fetchone()
                if not asset:
                    self.send_json({"error": "Asset not found"}, 404)
                    return
                
                cur.execute("SELECT * FROM it_asset_logs WHERE asset_id = ? ORDER BY id DESC", (asset_id,))
                logs = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT * FROM it_asset_allocations WHERE asset_id = ? ORDER BY id DESC", (asset_id,))
                allocations = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT * FROM it_maintenance_service WHERE asset_id = ? ORDER BY id DESC", (asset_id,))
                services = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT * FROM it_warranties WHERE asset_id = ? ORDER BY id DESC", (asset_id,))
                warranties = [dict(r) for r in cur.fetchall()]

                self.send_json({
                    "asset": dict(asset),
                    "logs": logs,
                    "allocations": allocations,
                    "services": services,
                    "warranties": warranties
                })

            elif path == '/api/it_rentals':
                cur.execute("""
                    SELECT r.*, a.asset_tag, a.brand, a.model_name, a.device_type, a.serial_number
                    FROM it_rentals r
                    LEFT JOIN it_assets a ON r.asset_id = a.id
                    ORDER BY r.id DESC
                """)
                rentals = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT COUNT(*) FROM it_rentals")
                total_rentals = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_rentals WHERE rental_status = 'Active Agreement'")
                active_rentals = cur.fetchone()[0]
                cur.execute("SELECT COALESCE(SUM(rental_amount), 0) FROM it_rentals WHERE rental_status = 'Active Agreement'")
                monthly_commitment = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_rentals WHERE payment_status IN ('Due Soon', 'Overdue')")
                due_payments = cur.fetchone()[0]

                self.send_json({
                    "rentals": rentals,
                    "summary": {
                        "total": total_rentals,
                        "active": active_rentals,
                        "monthly_commitment": monthly_commitment,
                        "due_payments": due_payments
                    }
                })

            elif path == '/api/it_allocations':
                cur.execute("""
                    SELECT alc.*, a.asset_tag, a.brand, a.model_name, a.device_type, a.serial_number, a.condition as asset_condition
                    FROM it_asset_allocations alc
                    JOIN it_assets a ON alc.asset_id = a.id
                    ORDER BY alc.id DESC
                """)
                allocations = [dict(r) for r in cur.fetchall()]

                total_alc = len(allocations)
                active_alc = sum(1 for x in allocations if x['handover_status'] == 'Active (With Employee)')
                returned_alc = sum(1 for x in allocations if x['handover_status'] == 'Returned & Verified')
                
                today_str = datetime.now().strftime("%Y-%m-%d")
                overdue_alc = sum(1 for x in allocations if x['handover_status'] == 'Active (With Employee)' and x['expected_return_date'] and x['expected_return_date'] < today_str)

                self.send_json({
                    "allocations": allocations,
                    "summary": {
                        "total": total_alc,
                        "active": active_alc,
                        "returned": returned_alc,
                        "overdue_returns": overdue_alc
                    }
                })

            elif path == '/api/it_warranties':
                cur.execute("""
                    SELECT w.*, a.asset_tag, a.brand, a.model_name, a.serial_number, a.device_type,
                           ROUND(julianday(w.end_date) - julianday('now')) as days_remaining
                    FROM it_warranties w
                    JOIN it_assets a ON w.asset_id = a.id
                    ORDER BY w.end_date ASC
                """)
                warranties = []
                for row in cur.fetchall():
                    item = dict(row)
                    days = item.get('days_remaining')
                    if days is not None:
                        if days < 0:
                            item['calculated_status'] = 'Expired'
                        elif days <= 30:
                            item['calculated_status'] = 'Expiring Soon (< 30 Days)'
                        else:
                            item['calculated_status'] = 'Active'
                    else:
                        item['calculated_status'] = item['status']
                    warranties.append(item)

                total_w = len(warranties)
                active_w = sum(1 for w in warranties if w['calculated_status'] == 'Active')
                expiring_soon_w = sum(1 for w in warranties if w['calculated_status'] == 'Expiring Soon (< 30 Days)')
                expired_w = sum(1 for w in warranties if w['calculated_status'] == 'Expired')

                self.send_json({
                    "warranties": warranties,
                    "summary": {
                        "total": total_w,
                        "active": active_w,
                        "expiring_soon": expiring_soon_w,
                        "expired": expired_w
                    }
                })

            elif path == '/api/it_maintenance':
                cur.execute("""
                    SELECT s.*, a.asset_tag, a.brand, a.model_name, a.serial_number, a.device_type
                    FROM it_maintenance_service s
                    JOIN it_assets a ON s.asset_id = a.id
                    ORDER BY s.id DESC
                """)
                tickets = [dict(r) for r in cur.fetchall()]

                total_s = len(tickets)
                in_repair_s = sum(1 for t in tickets if t['service_status'] in ('Under Diagnostics', 'In Repair / Awaiting Parts'))
                completed_s = sum(1 for t in tickets if t['service_status'] == 'Completed & Tested')
                total_cost = sum(t['repair_cost'] or 0.0 for t in tickets)

                self.send_json({
                    "tickets": tickets,
                    "summary": {
                        "total": total_s,
                        "in_repair": in_repair_s,
                        "completed": completed_s,
                        "total_cost": total_cost
                    }
                })

            elif path == '/api/it_payments':
                cur.execute("""
                    SELECT p.*, r.rental_agreement_no, s.service_ticket_no
                    FROM it_asset_payments p
                    LEFT JOIN it_rentals r ON p.related_rental_id = r.id
                    LEFT JOIN it_maintenance_service s ON p.related_service_id = s.id
                    ORDER BY p.due_date ASC
                """)
                today_str = datetime.now().strftime("%Y-%m-%d")
                payments = []
                for r in cur.fetchall():
                    item = dict(r)
                    if item['payment_status'] != 'Paid':
                        if item['due_date'] < today_str:
                            item['calculated_status'] = 'Overdue'
                        elif item['due_date'] == today_str:
                            item['calculated_status'] = 'Due Today'
                        else:
                            item['calculated_status'] = 'Upcoming Due'
                    else:
                        item['calculated_status'] = 'Paid'
                    payments.append(item)

                total_p = len(payments)
                upcoming_p = sum(1 for p in payments if p['calculated_status'] in ('Upcoming Due', 'Due Today'))
                overdue_p = sum(1 for p in payments if p['calculated_status'] == 'Overdue')
                paid_p = sum(1 for p in payments if p['calculated_status'] == 'Paid')
                pending_amount = sum(p['amount'] for p in payments if p['calculated_status'] != 'Paid')

                self.send_json({
                    "payments": payments,
                    "summary": {
                        "total": total_p,
                        "upcoming": upcoming_p,
                        "overdue": overdue_p,
                        "paid": paid_p,
                        "pending_amount": pending_amount
                    }
                })

            elif path == '/api/it_assets/analytics':
                cur.execute("SELECT COUNT(*) FROM it_assets")
                total_assets = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE device_type = 'Laptop'")
                total_laptops = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE device_type LIKE '%Desktop%' OR device_type = 'Workstation'")
                total_desktops = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE status = 'Allocated to Employee'")
                total_allocated = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE status = 'In Stock / Available'")
                total_in_stock = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE status = 'On Rental'")
                total_on_rent = cur.fetchone()[0]
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE status = 'In Service / Repair'")
                total_in_service = cur.fetchone()[0]
                cur.execute("SELECT COALESCE(SUM(purchase_cost), 0) FROM it_assets WHERE ownership_type LIKE '%Owned%'")
                total_asset_value = cur.fetchone()[0]

                cur.execute("SELECT brand, COUNT(*) as count FROM it_assets GROUP BY brand ORDER BY count DESC")
                brands = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT current_location, COUNT(*) as count FROM it_assets GROUP BY current_location ORDER BY count DESC")
                locations = [dict(r) for r in cur.fetchall()]

                cur.execute("SELECT condition, COUNT(*) as count FROM it_assets GROUP BY condition ORDER BY count DESC")
                conditions = [dict(r) for r in cur.fetchall()]

                cur.execute("""
                    SELECT l.*, a.asset_tag, a.model_name
                    FROM it_asset_logs l
                    JOIN it_assets a ON l.asset_id = a.id
                    ORDER BY l.id DESC LIMIT 10
                """)
                recent_logs = [dict(r) for r in cur.fetchall()]

                cur.execute("""
                    SELECT w.*, a.asset_tag, a.brand, a.model_name,
                           ROUND(julianday(w.end_date) - julianday('now')) as days_remaining
                    FROM it_warranties w
                    JOIN it_assets a ON w.asset_id = a.id
                    WHERE w.end_date <= date('now', '+30 days')
                    ORDER BY w.end_date ASC
                """)
                expiring_warranties = [dict(r) for r in cur.fetchall()]

                cur.execute("""
                    SELECT p.*
                    FROM it_asset_payments p
                    WHERE p.payment_status != 'Paid'
                    ORDER BY p.due_date ASC
                """)
                due_payments = [dict(r) for r in cur.fetchall()]

                self.send_json({
                    "metrics": {
                        "total_assets": total_assets,
                        "total_laptops": total_laptops,
                        "total_desktops": total_desktops,
                        "total_allocated": total_allocated,
                        "total_in_stock": total_in_stock,
                        "total_on_rent": total_on_rent,
                        "total_in_service": total_in_service,
                        "total_asset_value": total_asset_value
                    },
                    "brands": brands,
                    "locations": locations,
                    "conditions": conditions,
                    "recent_logs": recent_logs,
                    "expiring_warranties": expiring_warranties,
                    "due_payments": due_payments
                })
'''

if get_marker in code and "elif path == '/api/it_assets':" not in code:
    code = code.replace(get_marker, get_routes + '\n' + get_marker, 1)
    print("✓ Added IT Asset Management GET endpoints to server.py")
else:
    print("! get_marker not found or already added")

# Marker in do_POST
post_marker = '            else:\n                self.send_json({"error": "Action not supported"}, 404)'
post_routes = '''            # =====================================================================
            # LAPTOP & COMPUTER ASSET MANAGEMENT POST ENDPOINTS
            # =====================================================================
            elif path == '/api/it_assets/create':
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                device_type = body.get('device_type', 'Laptop').strip()
                brand = body.get('brand', '').strip()
                model_name = body.get('model_name', '').strip()
                serial_number = body.get('serial_number', '').strip()
                processor = body.get('specs_processor', '').strip()
                ram = body.get('specs_ram', '').strip()
                storage = body.get('specs_storage', '').strip()
                os_name = body.get('specs_os', 'Windows 11 Pro').strip()
                ownership = body.get('ownership_type', 'Owned (Institutional Purchase)').strip()
                condition = body.get('condition', 'Excellent').strip()
                purchase_date = body.get('purchase_date') or datetime.now().strftime("%Y-%m-%d")
                purchase_cost = float(body.get('purchase_cost') or 0.0)
                location = body.get('current_location', 'IT Support Depot').strip()
                status = body.get('status', 'In Stock / Available').strip()
                notes = body.get('notes', '').strip()
                creator = body.get('created_by', 'IT Support Administrator').strip()

                prefix = 'LAP' if 'laptop' in device_type.lower() else 'PC'
                cur.execute("SELECT COUNT(*) FROM it_assets WHERE asset_tag LIKE ?", (f"{prefix}-2026-%",))
                next_num = cur.fetchone()[0] + 1
                asset_tag = body.get('asset_tag') or f"{prefix}-2026-{next_num:03d}"

                cur.execute("""
                    INSERT INTO it_assets (
                        asset_tag, device_type, brand, model_name, serial_number, specs_processor, specs_ram,
                        specs_storage, specs_os, ownership_type, condition, purchase_date, purchase_cost,
                        current_location, status, notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (asset_tag, device_type, brand, model_name, serial_number, processor, ram, storage, os_name, ownership, condition, purchase_date, purchase_cost, location, status, notes, now))
                asset_id = cur.lastrowid

                cur.execute("""
                    INSERT INTO it_asset_logs (asset_id, action_type, from_location, to_location, assigned_to, performed_by, details, timestamp)
                    VALUES (?, 'Asset Registered / Added to Inventory', 'Procurement / Delivery', ?, 'IT Support Depot', ?, ?, ?)
                """, (asset_id, location, creator, f"Device registered: {brand} {model_name} ({processor or 'Standard Specs'}). Initial status: {status}.", now))
                conn.commit()

                self.send_json({
                    "success": True,
                    "message": f"Asset '{asset_tag}' ({brand} {model_name}) successfully registered in inventory!",
                    "asset_id": asset_id,
                    "asset_tag": asset_tag
                })

            elif path == '/api/it_assets/update':
                asset_id = body.get('id')
                if not asset_id:
                    self.send_json({"success": False, "message": "Asset ID is required."}, 400)
                    return
                
                cur.execute("SELECT * FROM it_assets WHERE id = ?", (asset_id,))
                old_asset = cur.fetchone()
                if not old_asset:
                    self.send_json({"success": False, "message": "Asset not found."}, 404)
                    return

                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                brand = body.get('brand', old_asset['brand']).strip()
                model_name = body.get('model_name', old_asset['model_name']).strip()
                processor = body.get('specs_processor', old_asset['specs_processor']).strip()
                ram = body.get('specs_ram', old_asset['specs_ram']).strip()
                storage = body.get('specs_storage', old_asset['specs_storage']).strip()
                os_name = body.get('specs_os', old_asset['specs_os']).strip()
                condition = body.get('condition', old_asset['condition']).strip()
                new_location = body.get('current_location', old_asset['current_location']).strip()
                new_status = body.get('status', old_asset['status']).strip()
                notes = body.get('notes', old_asset['notes']).strip()
                updated_by = body.get('updated_by', 'IT Support Administrator').strip()

                cur.execute("""
                    UPDATE it_assets
                    SET brand = ?, model_name = ?, specs_processor = ?, specs_ram = ?, specs_storage = ?,
                        specs_os = ?, condition = ?, current_location = ?, status = ?, notes = ?
                    WHERE id = ?
                """, (brand, model_name, processor, ram, storage, os_name, condition, new_location, new_status, notes, asset_id))

                if new_location != old_asset['current_location'] or new_status != old_asset['status']:
                    cur.execute("""
                        INSERT INTO it_asset_logs (asset_id, action_type, from_location, to_location, assigned_to, performed_by, details, timestamp)
                        VALUES (?, 'Location / Status Movement', ?, ?, ?, ?, ?, ?)
                    """, (asset_id, old_asset['current_location'], new_location, new_status, updated_by, f"Status updated to '{new_status}'. Condition: '{condition}'.", now))

                conn.commit()
                self.send_json({"success": True, "message": f"Asset '{old_asset['asset_tag']}' updated successfully!"})

            elif path == '/api/it_assets/delete':
                asset_id = body.get('id')
                cur.execute("SELECT asset_tag FROM it_assets WHERE id = ?", (asset_id,))
                row = cur.fetchone()
                if row:
                    cur.execute("DELETE FROM it_assets WHERE id = ?", (asset_id,))
                    cur.execute("DELETE FROM it_asset_logs WHERE asset_id = ?", (asset_id,))
                    conn.commit()
                    self.send_json({"success": True, "message": f"Asset '{row['asset_tag']}' removed from inventory."})
                else:
                    self.send_json({"success": False, "message": "Asset not found."}, 404)

            elif path == '/api/it_rentals/create':
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                rental_type = body.get('rental_type', 'Inward (Rented from Vendor)').strip()
                asset_id = body.get('asset_id')
                vendor_name = body.get('vendor_or_client_name', '').strip()
                phone = body.get('contact_phone', '').strip()
                email = body.get('contact_email', '').strip()
                start_date = body.get('start_date', '').strip()
                end_date = body.get('end_date', '').strip()
                billing_cycle = body.get('billing_cycle', 'Monthly').strip()
                rental_amount = float(body.get('rental_amount') or 0.0)
                deposit = float(body.get('deposit_amount') or 0.0)
                next_due = body.get('next_payment_due_date') or end_date
                terms = body.get('terms_notes', '').strip()

                cur.execute("SELECT COUNT(*) FROM it_rentals")
                r_num = cur.fetchone()[0] + 1
                agreement_no = f"RNT-2026-{r_num:03d}"

                cur.execute("""
                    INSERT INTO it_rentals (
                        rental_agreement_no, rental_type, asset_id, vendor_or_client_name, contact_phone,
                        contact_email, start_date, end_date, billing_cycle, rental_amount, deposit_amount,
                        next_payment_due_date, payment_status, rental_status, terms_notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Due Soon', 'Active Agreement', ?, ?)
                """, (agreement_no, rental_type, asset_id, vendor_name, phone, email, start_date, end_date, billing_cycle, rental_amount, deposit, next_due, terms, now))
                rental_id = cur.lastrowid

                if asset_id:
                    cur.execute("""
                        UPDATE it_assets 
                        SET status = 'On Rental', 
                            ownership_type = 'Rented / Leased from Vendor',
                            current_location = ?
                        WHERE id = ?
                    """, (f"On Rental ({vendor_name})", asset_id))
                    cur.execute("""
                        INSERT INTO it_asset_logs (asset_id, action_type, from_location, to_location, assigned_to, performed_by, details, timestamp)
                        VALUES (?, 'Rental Agreement Activated', 'IT Support Depot', ?, ?, 'IT Support Administrator', ?, ?)
                    """, (asset_id, f"On Rental ({vendor_name})", vendor_name, f"Agreement #{agreement_no}. Rate: ₦{rental_amount:,.2f}.", now))

                cur.execute("SELECT COUNT(*) FROM it_asset_payments")
                p_num = cur.fetchone()[0] + 1
                pmt_ref = f"PMT-2026-{p_num:03d}"
                cur.execute("""
                    INSERT INTO it_asset_payments (
                        ref_no, payment_category, related_rental_id, vendor_name, amount, due_date, payment_status, notes, created_at
                    ) VALUES (?, 'Rental Invoice', ?, ?, ?, ?, 'Upcoming Due', ?, ?)
                """, (pmt_ref, rental_id, vendor_name, rental_amount, next_due, f"Scheduled rental fee under agreement #{agreement_no}.", now))

                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Rental Agreement '{agreement_no}' with '{vendor_name}' successfully created!",
                    "rental_id": rental_id,
                    "agreement_no": agreement_no
                })

            elif path == '/api/it_rentals/update':
                rental_id = body.get('id')
                status = body.get('rental_status')
                pay_status = body.get('payment_status')
                end_date = body.get('end_date')
                terms = body.get('terms_notes')

                cur.execute("""
                    UPDATE it_rentals
                    SET rental_status = COALESCE(?, rental_status),
                        payment_status = COALESCE(?, payment_status),
                        end_date = COALESCE(?, end_date),
                        terms_notes = COALESCE(?, terms_notes)
                    WHERE id = ?
                """, (status, pay_status, end_date, terms, rental_id))
                conn.commit()
                self.send_json({"success": True, "message": "Rental agreement updated successfully."})

            elif path == '/api/it_allocations/handover':
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                asset_id = body.get('asset_id')
                employee_id = body.get('employee_id')
                employee_name = body.get('employee_name', '').strip()
                employee_role = body.get('employee_role', 'Faculty / Staff').strip()
                department = body.get('department', 'Academics').strip()
                handover_date = body.get('handover_date', datetime.now().strftime("%Y-%m-%d"))
                expected_return = body.get('expected_return_date')
                condition = body.get('handover_condition', 'Pristine / Like New').strip()
                accessories = body.get('accessories_included', 'Original Charger, Laptop Bag, Wireless Mouse').strip()
                notes = body.get('handover_notes', '').strip()
                officer = body.get('handover_by', 'IT Support Administrator').strip()

                if not asset_id or not employee_name:
                    self.send_json({"success": False, "message": "Asset and employee name are required."}, 400)
                    return

                cur.execute("SELECT asset_tag, brand, model_name, current_location FROM it_assets WHERE id = ?", (asset_id,))
                asset_row = cur.fetchone()
                if not asset_row:
                    self.send_json({"success": False, "message": "Asset not found."}, 404)
                    return

                cur.execute("SELECT COUNT(*) FROM it_asset_allocations")
                h_num = cur.fetchone()[0] + 1
                slip_no = f"HND-2026-{h_num:03d}"

                cur.execute("""
                    INSERT INTO it_asset_allocations (
                        handover_slip_no, asset_id, employee_id, employee_name, employee_role, department,
                        handover_date, expected_return_date, handover_condition, accessories_included,
                        handover_notes, handover_status, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'Active (With Employee)', ?)
                """, (slip_no, asset_id, employee_id, employee_name, employee_role, department, handover_date, expected_return, condition, accessories, notes, now))

                cur.execute("""
                    UPDATE it_assets
                    SET status = 'Allocated to Employee',
                        current_location = ?
                    WHERE id = ?
                """, (f"With Employee ({employee_name})", asset_id))

                cur.execute("""
                    INSERT INTO it_asset_logs (asset_id, action_type, from_location, to_location, assigned_to, performed_by, details, timestamp)
                    VALUES (?, 'Handover to Employee', ?, ?, ?, ?, ?, ?)
                """, (asset_id, asset_row['current_location'], f"With Employee ({employee_name})", employee_name, officer, f"Formally allocated under Handover Slip #{slip_no}. Accessories: {accessories}.", now))

                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Asset '{asset_row['asset_tag']}' successfully handed over to {employee_name}! Handover Slip #{slip_no} generated.",
                    "handover_slip_no": slip_no
                })

            elif path == '/api/it_allocations/return':
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                today_str = datetime.now().strftime("%Y-%m-%d")
                allocation_id = body.get('allocation_id')
                return_condition = body.get('return_condition', 'Good').strip()
                verified_by = body.get('return_verified_by', 'IT Support Administrator').strip()
                return_notes = body.get('return_notes', 'Inspection verified. System in full working order.').strip()

                cur.execute("SELECT alc.*, a.asset_tag, a.current_location FROM it_asset_allocations alc JOIN it_assets a ON alc.asset_id = a.id WHERE alc.id = ?", (allocation_id,))
                alc = cur.fetchone()
                if not alc:
                    self.send_json({"success": False, "message": "Allocation record not found."}, 404)
                    return

                cur.execute("""
                    UPDATE it_asset_allocations
                    SET handover_status = 'Returned & Verified',
                        actual_return_date = ?,
                        return_condition = ?,
                        return_verified_by = ?
                    WHERE id = ?
                """, (today_str, return_condition, verified_by, allocation_id))

                cur.execute("""
                    UPDATE it_assets
                    SET status = 'In Stock / Available',
                        condition = ?,
                        current_location = 'IT Support Depot'
                    WHERE id = ?
                """, (return_condition, alc['asset_id']))

                cur.execute("""
                    INSERT INTO it_asset_logs (asset_id, action_type, from_location, to_location, assigned_to, performed_by, details, timestamp)
                    VALUES (?, 'Asset Handover Return', ?, 'IT Support Depot', 'IT Support Depot', ?, ?, ?)
                """, (alc['asset_id'], alc['current_location'], verified_by, f"Device returned by {alc['employee_name']}. Condition: '{return_condition}'. Notes: {return_notes}", now))

                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Asset '{alc['asset_tag']}' return confirmed and checked back into IT Support Depot inventory!"
                })

            elif path == '/api/it_warranties/create':
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                asset_id = body.get('asset_id')
                provider = body.get('provider_name', '').strip()
                policy_no = body.get('policy_number', '').strip()
                w_type = body.get('warranty_type', 'OEM Standard Warranty').strip()
                start_date = body.get('start_date', '').strip()
                end_date = body.get('end_date', '').strip()
                contact = body.get('support_contact', '').strip()
                notes = body.get('notes', '').strip()

                cur.execute("""
                    INSERT INTO it_warranties (
                        asset_id, provider_name, policy_number, warranty_type, start_date, end_date,
                        support_contact, status, claim_count, notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Active', 0, ?, ?)
                """, (asset_id, provider, policy_no, w_type, start_date, end_date, contact, notes, now))
                conn.commit()
                self.send_json({"success": True, "message": f"Warranty policy '{policy_no}' registered successfully!"})

            elif path == '/api/it_warranties/claim':
                warranty_id = body.get('warranty_id')
                claim_notes = body.get('notes', 'Warranty claim filed by IT Support').strip()
                cur.execute("UPDATE it_warranties SET claim_count = claim_count + 1, notes = notes || ' | ' || ? WHERE id = ?", (claim_notes, warranty_id))
                conn.commit()
                self.send_json({"success": True, "message": "Warranty claim logged and registered with provider."})

            elif path == '/api/it_maintenance/create':
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                asset_id = body.get('asset_id')
                s_type = body.get('service_type', 'Hardware Repair').strip()
                issue = body.get('reported_issue', '').strip()
                center = body.get('service_center_or_vendor', 'Authorized Service Hub').strip()
                tech = body.get('technician_name', '').strip()
                start_d = body.get('start_date', datetime.now().strftime("%Y-%m-%d")).strip()
                cost = float(body.get('repair_cost') or 0.0)
                is_warranty = 1 if body.get('warranty_claim_covered') else 0
                remarks = body.get('remarks', '').strip()

                cur.execute("SELECT COUNT(*) FROM it_maintenance_service")
                s_num = cur.fetchone()[0] + 1
                ticket_no = f"SVC-2026-{s_num:03d}"

                cur.execute("""
                    INSERT INTO it_maintenance_service (
                        service_ticket_no, asset_id, service_type, reported_issue, service_center_or_vendor,
                        technician_name, start_date, repair_cost, service_status, warranty_claim_covered, remarks, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'In Repair / Awaiting Parts', ?, ?, ?)
                """, (ticket_no, asset_id, s_type, issue, center, tech, start_d, cost, is_warranty, remarks, now))

                cur.execute("""
                    UPDATE it_assets 
                    SET status = 'In Service / Repair',
                        current_location = ?
                    WHERE id = ?
                """, (f"Service Center ({center})", asset_id))

                cur.execute("""
                    INSERT INTO it_asset_logs (asset_id, action_type, from_location, to_location, assigned_to, performed_by, details, timestamp)
                    VALUES (?, 'Dispatched for Service / Repair', 'IT Support Depot', ?, ?, 'IT Support Administrator', ?, ?)
                """, (asset_id, f"Service Center ({center})", center, f"Ticket #{ticket_no}. Type: {s_type}. Issue: {issue}.", now))

                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Service ticket '{ticket_no}' opened! Device marked 'In Service / Repair'.",
                    "ticket_no": ticket_no
                })

            elif path == '/api/it_maintenance/complete':
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                ticket_id = body.get('ticket_id')
                comp_date = body.get('completion_date', datetime.now().strftime("%Y-%m-%d")).strip()
                actual_cost = float(body.get('repair_cost') or 0.0)
                parts = body.get('parts_replaced', '').strip()
                remarks = body.get('remarks', 'Repair and operational diagnostic testing verified.').strip()
                location = body.get('return_location', 'IT Support Depot').strip()

                cur.execute("SELECT s.*, a.asset_tag FROM it_maintenance_service s JOIN it_assets a ON s.asset_id = a.id WHERE s.id = ?", (ticket_id,))
                t_row = cur.fetchone()
                if not t_row:
                    self.send_json({"success": False, "message": "Ticket not found."}, 404)
                    return

                cur.execute("""
                    UPDATE it_maintenance_service
                    SET service_status = 'Completed & Tested',
                        completion_date = ?,
                        repair_cost = ?,
                        parts_replaced = ?,
                        remarks = COALESCE(remarks || ' | ' || ?, remarks)
                    WHERE id = ?
                """, (comp_date, actual_cost, parts, remarks, ticket_id))

                cur.execute("""
                    UPDATE it_assets
                    SET status = 'In Stock / Available',
                        condition = 'Good',
                        current_location = ?
                    WHERE id = ?
                """, (location, t_row['asset_id']))

                cur.execute("""
                    INSERT INTO it_asset_logs (asset_id, action_type, from_location, to_location, assigned_to, performed_by, details, timestamp)
                    VALUES (?, 'Service Completed & Tested', ?, ?, 'IT Support Depot', 'IT Support Administrator', ?, ?)
                """, (t_row['asset_id'], t_row['service_center_or_vendor'], location, f"Ticket #{t_row['service_ticket_no']} completed. Parts: {parts or 'None'}. Cost: ₦{actual_cost:,.2f}.", now))

                if actual_cost > 0 and not t_row['warranty_claim_covered']:
                    cur.execute("SELECT COUNT(*) FROM it_asset_payments")
                    p_num = cur.fetchone()[0] + 1
                    pmt_ref = f"PMT-2026-{p_num:03d}"
                    cur.execute("""
                        INSERT INTO it_asset_payments (
                            ref_no, payment_category, related_service_id, vendor_name, amount, due_date, payment_status, notes, created_at
                        ) VALUES (?, 'Hardware Repair Bill', ?, ?, ?, date('now', '+7 days'), 'Upcoming Due', ?, ?)
                    """, (pmt_ref, ticket_id, t_row['service_center_or_vendor'], actual_cost, f"Invoice for completed repair on ticket #{t_row['service_ticket_no']}.", now))

                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Service ticket '{t_row['service_ticket_no']}' marked completed! Device tested and restored to '{location}'."
                })

            elif path == '/api/it_payments/create':
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cat = body.get('payment_category', 'Rental Invoice').strip()
                vendor = body.get('vendor_name', '').strip()
                amount = float(body.get('amount') or 0.0)
                due = body.get('due_date', '').strip()
                rental_id = body.get('related_rental_id')
                service_id = body.get('related_service_id')
                notes = body.get('notes', '').strip()

                cur.execute("SELECT COUNT(*) FROM it_asset_payments")
                p_num = cur.fetchone()[0] + 1
                pmt_ref = f"PMT-2026-{p_num:03d}"

                cur.execute("""
                    INSERT INTO it_asset_payments (
                        ref_no, payment_category, related_rental_id, related_service_id, vendor_name,
                        amount, due_date, payment_status, notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 'Upcoming Due', ?, ?)
                """, (pmt_ref, cat, rental_id, service_id, vendor, amount, due, notes, now))
                conn.commit()
                self.send_json({"success": True, "message": f"Payment schedule '{pmt_ref}' created successfully!", "ref_no": pmt_ref})

            elif path == '/api/it_payments/record':
                payment_id = body.get('payment_id')
                paid_date = body.get('paid_date', datetime.now().strftime("%Y-%m-%d"))
                method = body.get('payment_method', 'Bank Transfer / NEFT').strip()
                tx_ref = body.get('transaction_ref', '').strip()
                notes = body.get('notes', '').strip()

                cur.execute("""
                    UPDATE it_asset_payments
                    SET payment_status = 'Paid',
                        paid_date = ?,
                        payment_method = ?,
                        transaction_ref = ?,
                        notes = COALESCE(notes || ' | ' || ?, notes)
                    WHERE id = ?
                """, (paid_date, method, tx_ref, notes, payment_id))
                conn.commit()
                self.send_json({"success": True, "message": "Payment recorded successfully as Paid in Full!"})

            elif path == '/api/it_payments/send_reminder':
                payment_id = body.get('payment_id')
                cur.execute("SELECT * FROM it_asset_payments WHERE id = ?", (payment_id,))
                p = cur.fetchone()
                if p:
                    self.send_json({
                        "success": True,
                        "message": f"Payment reminder notification dispatched to School Bursar & Finance Desk for {p['vendor_name']} (₦{p['amount']:,.2f} due on {p['due_date']})!"
                    })
                else:
                    self.send_json({"success": False, "message": "Payment record not found."}, 404)
'''

if post_marker in code and "elif path == '/api/it_assets/create':" not in code:
    code = code.replace(post_marker, post_routes + '\n' + post_marker, 1)
    print("✓ Added IT Asset Management POST endpoints to server.py")
else:
    print("! post_marker not found or already added")

with open('school_website/server.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("All endpoints added to server.py!")
