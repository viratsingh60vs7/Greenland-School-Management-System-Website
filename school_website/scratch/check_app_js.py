with open('school_website/js/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- ROLE_ALLOWED_TABS (118-130) ---")
for i in range(117, 130):
    print(lines[i], end='')

print("\n--- formatRoleName (665-680) ---")
for i in range(665, 680):
    print(lines[i], end='')

print("\n--- showTab switch (710-745) ---")
for i in range(710, 745):
    print(lines[i], end='')

print("\n--- renderDashboardTab (788-806) ---")
for i in range(788, 807):
    print(lines[i], end='')
