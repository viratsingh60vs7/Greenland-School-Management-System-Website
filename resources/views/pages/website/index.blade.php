<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ $system_name }} - Official School Portal & Website</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #1e3a8a;
            --primary-dark: #172554;
            --secondary: #d97706;
            --accent: #0284c7;
            --gray-50: #f8fafc;
            --gray-100: #f1f5f9;
            --gray-200: #e2e8f0;
            --gray-600: #475569;
            --gray-700: #334155;
            --gray-900: #0f172a;
            --white: #ffffff;
            --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
            --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1);
            --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1);
            --shadow-xl: 0 20px 25px -5px rgb(0 0 0 / 0.1);
            --radius-md: 10px;
            --radius-lg: 16px;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Plus Jakarta Sans', system-ui, sans-serif; }
        body { background-color: var(--gray-50); color: var(--gray-700); line-height: 1.6; }
        a { text-decoration: none; color: inherit; }

        .top-bar {
            background-color: var(--primary-dark);
            color: #94a3b8;
            font-size: 0.85rem;
            padding: 8px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .main-navbar {
            background-color: var(--white);
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: var(--shadow-sm);
            padding: 14px 32px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .brand-logo { display: flex; align-items: center; gap: 12px; }
        .crest-icon {
            width: 44px; height: 44px;
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white; border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 1.3rem; font-weight: 800;
        }
        .brand-text h1 { font-size: 1.25rem; font-weight: 800; color: var(--primary); }
        .brand-text p { font-size: 0.72rem; color: var(--gray-600); text-transform: uppercase; letter-spacing: 1px; font-weight: 600; }

        .nav-links { display: flex; list-style: none; gap: 24px; align-items: center; }
        .nav-links a { font-size: 0.95rem; font-weight: 600; color: var(--gray-700); }
        .nav-links a:hover { color: var(--primary); }

        .btn {
            display: inline-flex; align-items: center; justify-content: center; gap: 8px;
            padding: 10px 20px; font-size: 0.9rem; font-weight: 600;
            border-radius: 6px; border: none; cursor: pointer; transition: all 0.2s;
        }
        .btn-primary { background: linear-gradient(135deg, var(--primary), #3b82f6); color: white; }
        .btn-secondary { background: linear-gradient(135deg, var(--secondary), #f59e0b); color: white; }
        .btn-outline { background: transparent; border: 2px solid var(--primary); color: var(--primary); }

        .hero-section {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.88), rgba(30, 58, 138, 0.85)), 
                        url('https://images.unsplash.com/photo-1523050854058-8df90110c9f1?q=80&w=1600&auto=format&fit=crop') center/cover no-repeat;
            color: white; padding: 90px 32px; min-height: 540px; display: flex; align-items: center;
        }
        .hero-container { max-width: 1200px; margin: 0 auto; width: 100%; }
        .hero-title { font-size: 3.2rem; font-weight: 800; line-height: 1.15; margin-bottom: 20px; max-width: 800px; font-family: 'Outfit', sans-serif; }
        .hero-title span { color: #fbbf24; }
        .hero-subtitle { font-size: 1.15rem; color: #cbd5e1; max-width: 680px; margin-bottom: 36px; }

        .stats-ribbon {
            background: var(--white); box-shadow: var(--shadow-xl); border-radius: var(--radius-lg);
            max-width: 1100px; margin: -50px auto 40px auto; position: relative; z-index: 10;
            padding: 30px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px;
            border-bottom: 4px solid var(--secondary);
        }
        .stat-item { text-align: center; border-right: 1px solid var(--gray-200); }
        .stat-item:last-child { border-right: none; }
        .stat-number { font-size: 2.2rem; font-weight: 800; color: var(--primary); font-family: 'Outfit', sans-serif; }
        .stat-label { font-size: 0.85rem; font-weight: 600; color: var(--gray-600); text-transform: uppercase; }

        .section { padding: 70px 32px; }
        .section-container { max-width: 1200px; margin: 0 auto; }
        .section-header { text-align: center; margin-bottom: 50px; }
        .section-subtitle { font-size: 0.85rem; font-weight: 700; color: var(--secondary); text-transform: uppercase; letter-spacing: 1.5px; }
        .section-title { font-size: 2.2rem; font-weight: 800; color: var(--primary-dark); font-family: 'Outfit', sans-serif; }

        .program-cards { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 24px; }
        .program-card { background: white; border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-md); border-top: 4px solid var(--primary); }
        .program-img { height: 180px; width: 100%; object-fit: cover; }
        .program-body { padding: 24px; }

        .admissions-box {
            background: white; border-radius: var(--radius-lg); box-shadow: var(--shadow-xl);
            padding: 48px; display: grid; grid-template-columns: 1fr 1.2fr; gap: 48px; border: 1px solid var(--gray-200);
        }
        .form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
        .form-group { display: flex; flex-direction: column; gap: 6px; margin-bottom: 16px; }
        .form-control { padding: 10px 14px; border: 1px solid #cbd5e1; border-radius: 6px; font-size: 0.9rem; }

        .site-footer { background: var(--gray-900); color: #94a3b8; padding: 60px 32px 24px 32px; }
        .footer-grid { max-width: 1200px; margin: 0 auto; display: grid; grid-template-columns: 2fr 1fr 1fr 1.5fr; gap: 40px; }
    </style>
</head>
<body>

    <!-- Top Announcement Bar -->
    <div class="top-bar">
        <div>
            <span>📍 {{ $address }}</span> &nbsp;|&nbsp;
            <span>📞 {{ $phone }}</span> &nbsp;|&nbsp;
            <span>✉️ {{ $system_email }}</span>
        </div>
        <div>
            <a href="{{ route('login') }}" style="color:#fbbf24; font-weight:700;">★ Portal Login (LAV_SMS)</a>
        </div>
    </div>

    <!-- Main Navigation Header -->
    <header class="main-navbar">
        <div class="brand-logo">
            <div class="crest-icon">{{ $system_title ?: 'CJ' }}</div>
            <div class="brand-text">
                <h1>{{ $system_name }}</h1>
                <p>Excellence • Character • Leadership</p>
            </div>
        </div>

        <ul class="nav-links">
            <li><a href="#home">Home</a></li>
            <li><a href="#about">About Us</a></li>
            <li><a href="#academics">Academics</a></li>
            <li><a href="#admissions">Admissions</a></li>
            <li><a href="#contact">Contact</a></li>
        </ul>

        <div>
            <a href="{{ route('login') }}" class="btn btn-primary">
                🔐 Access SMS Portal
            </a>
        </div>
    </header>

    @if(session('flash_success'))
        <div style="background:#dcfce7; color:#166534; padding:16px 32px; border-bottom:2px solid #10b981; font-weight:600; text-align:center;">
            {{ session('flash_success') }}
        </div>
    @endif

    <!-- Hero Section -->
    <section id="home" class="hero-section">
        <div class="hero-container">
            <div style="display:inline-block; background:rgba(217, 119, 6, 0.25); border:1px solid #d97706; color:#fde68a; padding:6px 16px; border-radius:50px; font-size:0.82rem; font-weight:700; margin-bottom:20px;">
                ✨ Admissions Open for {{ $current_session }} Session
            </div>
            <h1 class="hero-title">
                Nurturing Intellect, Inspiring <span>Moral Leadership</span>
            </h1>
            <p class="hero-subtitle">
                Welcome to {{ $system_name }}. An institution where students develop critical reasoning, 
                technological literacy, and moral character to thrive in modern global society.
            </p>
            <div style="display:flex; gap:16px;">
                <a href="#admissions" class="btn btn-secondary">Apply for Admission</a>
                <a href="{{ route('login') }}" class="btn btn-primary" style="background:white; color:#1e3a8a; font-weight:700;">
                    🚀 Open Management Portal
                </a>
            </div>
        </div>
    </section>

    <!-- Key Statistics -->
    <div class="stats-ribbon">
        <div class="stat-item">
            <div class="stat-number">1,450+</div>
            <div class="stat-label">Enrolled Students</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">98.6%</div>
            <div class="stat-label">Graduation & Pass Rate</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">65+</div>
            <div class="stat-label">Certified Faculty</div>
        </div>
        <div class="stat-item">
            <div class="stat-number">100%</div>
            <div class="stat-label">University Placement</div>
        </div>
    </div>

    <!-- Academic Programs -->
    <section id="academics" class="section">
        <div class="section-container">
            <div class="section-header">
                <span class="section-subtitle">Academic Tiers</span>
                <h2 class="section-title">Academic Wings at {{ $system_title ?: 'CJIA' }}</h2>
            </div>

            <div class="program-cards">
                <div class="program-card">
                    <img src="https://images.unsplash.com/photo-1588072432836-e10032774350?q=80&w=600&auto=format&fit=crop" class="program-img" alt="Early Years">
                    <div class="program-body">
                        <h3 style="font-size:1.2rem; font-weight:700; margin-bottom:8px;">Early Years & Nursery</h3>
                        <p style="font-size:0.88rem; color:#64748b; margin-bottom:16px;">Play-based phonics, creative discovery, and early motor skills nurturing.</p>
                        <a href="#admissions" class="btn btn-outline" style="padding:6px 12px; font-size:0.8rem;">Enroll</a>
                    </div>
                </div>

                <div class="program-card">
                    <img src="https://images.unsplash.com/photo-1509062522246-3755977927d7?q=80&w=600&auto=format&fit=crop" class="program-img" alt="Primary School">
                    <div class="program-body">
                        <h3 style="font-size:1.2rem; font-weight:700; margin-bottom:8px;">Primary School (Grades 1-6)</h3>
                        <p style="font-size:0.88rem; color:#64748b; margin-bottom:16px;">Foundations in mathematics, literacy, general sciences, and ICT.</p>
                        <a href="#admissions" class="btn btn-outline" style="padding:6px 12px; font-size:0.8rem;">Enroll</a>
                    </div>
                </div>

                <div class="program-card">
                    <img src="https://images.unsplash.com/photo-1544717305-2782549b5136?q=80&w=600&auto=format&fit=crop" class="program-img" alt="Junior Secondary">
                    <div class="program-body">
                        <h3 style="font-size:1.2rem; font-weight:700; margin-bottom:8px;">Junior Secondary (JSS 1-3)</h3>
                        <p style="font-size:0.88rem; color:#64748b; margin-bottom:16px;">Analytical sciences, introductory technology, arts, and BECE preparation.</p>
                        <a href="#admissions" class="btn btn-outline" style="padding:6px 12px; font-size:0.8rem;">Enroll</a>
                    </div>
                </div>

                <div class="program-card">
                    <img src="https://images.unsplash.com/photo-1523240795612-9a054b0db644?q=80&w=600&auto=format&fit=crop" class="program-img" alt="Senior Secondary">
                    <div class="program-body">
                        <h3 style="font-size:1.2rem; font-weight:700; margin-bottom:8px;">Senior Secondary (SSS 1-3)</h3>
                        <p style="font-size:0.88rem; color:#64748b; margin-bottom:16px;">Science, commercial, and humanities tracks for WAEC, NECO, and university admission.</p>
                        <a href="#admissions" class="btn btn-outline" style="padding:6px 12px; font-size:0.8rem;">Enroll</a>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Admissions Form -->
    <section id="admissions" class="section" style="background:#f1f5f9;">
        <div class="section-container">
            <div class="admissions-box">
                <div>
                    <span class="section-subtitle">Enrollment</span>
                    <h3 style="font-size:1.8rem; font-weight:800; color:#172554; margin-bottom:16px;">
                        Online Admission Inquiry
                    </h3>
                    <p style="color:#64748b; margin-bottom:20px;">
                        Complete the inquiry form to start your child's enrollment. Our admissions coordinator 
                        will contact you with entrance assessment dates.
                    </p>
                    <ul style="list-style:none; display:flex; flex-direction:column; gap:12px; font-size:0.9rem;">
                        <li>✓ Diagnostic academic assessment</li>
                        <li>✓ Campus tour & faculty interaction</li>
                        <li>✓ Merit-based scholarship opportunities</li>
                    </ul>
                </div>

                <form method="POST" action="{{ route('website.inquiry') }}">
                    @csrf
                    <div class="form-grid">
                        <div class="form-group">
                            <label style="font-size:0.85rem; font-weight:600;">Student Full Name *</label>
                            <input type="text" name="name" class="form-control" required placeholder="Student Name">
                        </div>
                        <div class="form-group">
                            <label style="font-size:0.85rem; font-weight:600;">Parent Name *</label>
                            <input type="text" name="parent_name" class="form-control" required placeholder="Parent Name">
                        </div>
                    </div>
                    <div class="form-grid">
                        <div class="form-group">
                            <label style="font-size:0.85rem; font-weight:600;">Email Address *</label>
                            <input type="email" name="email" class="form-control" required placeholder="parent@mail.com">
                        </div>
                        <div class="form-group">
                            <label style="font-size:0.85rem; font-weight:600;">Phone Number *</label>
                            <input type="tel" name="phone" class="form-control" required placeholder="+234...">
                        </div>
                    </div>
                    <button type="submit" class="btn btn-primary" style="width:100%; padding:12px; margin-top:8px;">
                        Submit Admission Inquiry
                    </button>
                </form>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="site-footer">
        <div class="footer-grid">
            <div>
                <h3 style="color:white; margin-bottom:12px;">{{ $system_name }}</h3>
                <p style="font-size:0.85rem;">{{ $address }}</p>
                <p style="font-size:0.85rem;">Phone: {{ $phone }}</p>
                <p style="font-size:0.85rem;">Email: {{ $system_email }}</p>
            </div>
            <div>
                <h4 style="color:white; margin-bottom:12px;">Portals</h4>
                <p><a href="{{ route('login') }}">Portal Login</a></p>
            </div>
            <div>
                <h4 style="color:white; margin-bottom:12px;">Academic Session</h4>
                <p>{{ $current_session }}</p>
            </div>
            <div>
                <a href="{{ route('login') }}" class="btn btn-secondary">Enter Management System</a>
            </div>
        </div>
    </footer>
</body>
</html>
