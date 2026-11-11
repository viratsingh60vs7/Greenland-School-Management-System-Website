with open('school_website/server.py', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update handover return JSON
old_handover_ret = '''                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Asset '{asset_row['asset_tag']}' successfully handed over to {employee_name}! Handover Slip #{slip_no} generated.",
                    "handover_slip_no": slip_no
                })'''

new_handover_ret = '''                alloc_id = cur.lastrowid
                conn.commit()
                self.send_json({
                    "success": True,
                    "message": f"Asset '{asset_row['asset_tag']}' successfully handed over to {employee_name}! Handover Slip #{slip_no} generated.",
                    "allocation_id": alloc_id,
                    "handover_slip_no": slip_no
                })'''

assert old_handover_ret in code, "old_handover_ret not found"
code = code.replace(old_handover_ret, new_handover_ret, 1)

# 2. Update warranty create return JSON
old_warr_ret = '''                self.send_json({"success": True, "message": f"Warranty policy '{policy_no}' registered successfully!"})'''
new_warr_ret = '''                wid = cur.lastrowid
                self.send_json({"success": True, "message": f"Warranty policy '{policy_no}' registered successfully!", "warranty_id": wid})'''

assert old_warr_ret in code, "old_warr_ret not found"
code = code.replace(old_warr_ret, new_warr_ret, 1)

# 3. Update maintenance create return JSON
old_maint_ret = '''                self.send_json({
                    "success": True,
                    "message": f"Service ticket '{ticket_no}' opened! Device marked 'In Service / Repair'.",
                    "ticket_no": ticket_no
                })'''

new_maint_ret = '''                ticket_id = cur.lastrowid
                self.send_json({
                    "success": True,
                    "message": f"Service ticket '{ticket_no}' opened! Device marked 'In Service / Repair'.",
                    "ticket_id": ticket_id,
                    "ticket_no": ticket_no
                })'''

assert old_maint_ret in code, "old_maint_ret not found"
code = code.replace(old_maint_ret, new_maint_ret, 1)

# 4. Update payments create SQL and return JSON
old_pmt_code = '''                cur.execute("""
                    INSERT INTO it_asset_payments (
                        ref_no, payment_category, related_rental_id, related_service_id, vendor_name,
                        amount, due_date, payment_status, notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, 'Upcoming Due', ?, ?)
                """, (pmt_ref, cat, rental_id, service_id, vendor, amount, due, notes, now))
                conn.commit()
                self.send_json({"success": True, "message": f"Payment schedule '{pmt_ref}' created successfully!", "ref_no": pmt_ref})'''

new_pmt_code = '''                cur.execute("""
                    INSERT INTO it_asset_payments (
                        ref_no, payment_category, related_rental_id, related_service_id, vendor_name,
                        amount, due_date, payment_status, notes, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, 'Upcoming Due', ?, ?)
                """, (pmt_ref, cat, rental_id, service_id, vendor, amount, due, notes, now))
                pmt_id = cur.lastrowid
                conn.commit()
                self.send_json({"success": True, "message": f"Payment schedule '{pmt_ref}' created successfully!", "payment_id": pmt_id, "ref_no": pmt_ref})'''

assert old_pmt_code in code, "old_pmt_code not found"
code = code.replace(old_pmt_code, new_pmt_code, 1)

with open('school_website/server.py', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ Server routes successfully patched!")
