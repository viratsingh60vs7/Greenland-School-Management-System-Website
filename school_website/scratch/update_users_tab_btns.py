with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

old_btns = """                                            <div style="display:flex; gap:6px;">
                                                <button class="btn btn-primary btn-sm" style="font-size:0.73rem; padding:3px 8px;" onclick="openEditCredentialsModal(${u.id})">
                                                    ✏️ Edit ID/Pass
                                                </button>
                                                <button class="btn btn-secondary btn-sm" style="font-size:0.73rem; padding:3px 8px; background:#475569; color:white;" onclick="openAssignUserRoleModal(${u.id})">
                                                    🎭 Assign Role
                                                </button>
                                            </div>"""

new_btns = """                                            <div style="display:flex; gap:6px;">
                                                <button class="btn btn-secondary btn-sm" style="font-size:0.73rem; padding:3px 8px; background:#475569; color:white;" onclick="openAssignUserRoleModal(${u.id})">
                                                    🎭 Assign Role
                                                </button>
                                                <button class="btn btn-outline btn-sm" style="font-size:0.73rem; padding:3px 8px; color:#2563eb; border-color:#93c5fd;" onclick="showTab('credentials')">
                                                    🔐 IT & Owner Credential Desk
                                                </button>
                                            </div>"""

text_norm = text.replace('\r\n', '\n')
old_btns_norm = old_btns.replace('\r\n', '\n')
new_btns_norm = new_btns.replace('\r\n', '\n')

if old_btns_norm in text_norm:
    text_norm = text_norm.replace(old_btns_norm, new_btns_norm)
    with open('school_website/js/app.js', 'w', encoding='utf-8') as f:
        f.write(text_norm)
    print("Updated action buttons in renderUsersTab")
else:
    print("WARNING: action buttons not found")
