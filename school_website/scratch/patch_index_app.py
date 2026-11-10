with open('school_website/index.html', 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Add Campus App button in public navbar
target_nav = """            <div class="nav-actions">
                <a href="#admissions" class="btn btn-secondary btn-sm">Apply Online</a>
                <button class="btn btn-primary btn-sm" onclick="openPortalLogin()">
                    🔐 SMS Portal Login
                </button>
            </div>"""

replacement_nav = """            <div class="nav-actions">
                <a href="#admissions" class="btn btn-secondary btn-sm">Apply Online</a>
                <button class="btn btn-sm" onclick="openCampusApp()" style="background:#0284c7; color:white; font-weight:700; border:none; border-radius:6px; padding:6px 14px; display:inline-flex; align-items:center; gap:6px; cursor:pointer;">
                    📱 Student, Parent & Teacher App
                </button>
                <button class="btn btn-primary btn-sm" onclick="openPortalLogin()">
                    🔐 SMS Portal Login
                </button>
            </div>"""

assert target_nav in code, "target_nav not found in index.html"
code = code.replace(target_nav, replacement_nav, 1)

# 2. Add Campus App button in role-switcher-banner
target_banner_logout = """<button class="btn btn-secondary btn-sm" onclick="handlePortalLogout()" style="font-size:0.8rem; padding:6px 14px; background:#dc2626; border-color:#b91c1c; font-weight:700;">
                    🚪 Sign Out
                </button>"""

replacement_banner_logout = """<button type="button" class="btn btn-sm" onclick="openCampusApp()" style="background:#0284c7; color:white; font-size:0.8rem; font-weight:700; padding:6px 12px; border-radius:6px; border:none; display:inline-flex; align-items:center; gap:5px; cursor:pointer;" title="Open Campus Mobile & Web App">
                    📱 Open Campus App
                </button>
                <button class="btn btn-secondary btn-sm" onclick="handlePortalLogout()" style="font-size:0.8rem; padding:6px 14px; background:#dc2626; border-color:#b91c1c; font-weight:700;">
                    🚪 Sign Out
                </button>"""

assert target_banner_logout in code, "target_banner_logout not found in index.html"
code = code.replace(target_banner_logout, replacement_banner_logout, 1)

# 3. Add campus-app-view container between portal-login-view and portal-container
target_views_split = """    <!-- ================================================================= -->
    <!-- 3. INTEGRATED SCHOOL MANAGEMENT SYSTEM (SMS) PORTAL               -->
    <!-- ================================================================= -->
    <div id="portal-container">"""

campus_app_html = """    <!-- ================================================================= -->
    <!-- 2B. CAMPUS MOBILE & WEB APP (STUDENT • PARENT • TEACHER)          -->
    <!-- Dual Access Login: Phone Number as User ID OR Standard User ID   -->
    <!-- ================================================================= -->
    <div id="campus-app-view" style="display:none; min-height:100vh; background:linear-gradient(135deg, #0b1329 0%, #1e1b4b 50%, #0b1329 100%); padding:20px; color:#f8fafc; font-family:'Inter', sans-serif;">
        <!-- Top App Navigation & Simulator Bar -->
        <div style="max-width:960px; margin:0 auto 16px auto; display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:12px; background:rgba(255,255,255,0.06); backdrop-filter:blur(10px); padding:10px 18px; border-radius:12px; border:1px solid rgba(255,255,255,0.12);">
            <div style="display:flex; align-items:center; gap:12px;">
                <div style="width:36px; height:36px; border-radius:8px; background:#1e3a8a; display:flex; align-items:center; justify-content:center; overflow:hidden;">
                    <img src="assets/Logo_Greenland_School.png" style="width:100%; height:100%; object-fit:contain;" alt="GS">
                </div>
                <div>
                    <strong style="font-size:0.95rem; color:#ffffff; letter-spacing:0.4px;">Greenland Campus App</strong>
                    <div style="font-size:0.73rem; color:#94a3b8;">Mobile & Web Portal for Students, Parents & Teachers</div>
                </div>
            </div>
            <div style="display:flex; align-items:center; gap:8px;">
                <button type="button" class="btn btn-sm btn-outline" id="app-frame-toggle-btn" style="color:#e2e8f0; border-color:#475569; font-size:0.75rem; padding:5px 12px; background:rgba(255,255,255,0.05);" onclick="toggleAppDeviceFrame()">
                    📱 Phone Mockup Mode
                </button>
                <button type="button" class="btn btn-sm" style="background:#2563eb; color:white; font-size:0.75rem; padding:5px 14px; font-weight:700; border:none; border-radius:6px;" onclick="exitCampusApp()">
                    🔙 Back to Portal / Web
                </button>
            </div>
        </div>

        <!-- Phone Mockup Device Wrapper -->
        <div id="app-device-wrapper" style="max-width:440px; margin:0 auto; transition:all 0.3s ease;">
            <div id="app-mobile-chassis" style="background:#f8fafc; color:#0f172a; border-radius:36px; box-shadow:0 25px 60px -15px rgba(0,0,0,0.8), 0 0 0 10px #1e293b, 0 0 0 12px #334155; overflow:hidden; min-height:760px; display:flex; flex-direction:column; position:relative;">
                
                <!-- Phone Status Bar Mockup -->
                <div style="background:#0f172a; color:#cbd5e1; font-size:0.7rem; font-weight:700; padding:8px 20px 6px 20px; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.06); letter-spacing:0.3px;">
                    <span id="app-status-clock">09:41</span>
                    <div style="width:80px; height:14px; background:#000; border-radius:12px; margin:0 auto;"></div>
                    <span><i class="fas fa-signal"></i> 5G &nbsp; <i class="fas fa-battery-full"></i></span>
                </div>

                <!-- Dynamic Content Area of App -->
                <div id="app-screen-body" style="flex:1; overflow-y:auto; display:flex; flex-direction:column;">
                    <!-- Rendered dynamically by renderCampusApp() -->
                </div>

                <!-- Bottom Navigation Bar (Rendered dynamically when logged in) -->
                <div id="app-bottom-nav" style="display:none; background:#ffffff; border-top:1px solid #e2e8f0; padding:8px 6px; box-shadow:0 -4px 12px rgba(0,0,0,0.05);">
                    <!-- Dynamic navigation buttons -->
                </div>

            </div>
        </div>
    </div>

    <!-- ================================================================= -->
    <!-- 3. INTEGRATED SCHOOL MANAGEMENT SYSTEM (SMS) PORTAL               -->
    <!-- ================================================================= -->
    <div id="portal-container">"""

assert target_views_split in code, "target_views_split not found in index.html"
code = code.replace(target_views_split, campus_app_html, 1)

with open('school_website/index.html', 'w', encoding='utf-8') as f:
    f.write(code)

print("✓ index.html successfully updated with Campus App markup and buttons!")
