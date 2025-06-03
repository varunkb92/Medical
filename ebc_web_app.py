<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EBC Risk Assessment Tool</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 15px;
            margin-bottom: 2rem;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            color: white;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }

        .header h3 {
            color: #f0f2f6;
            font-weight: 300;
        }

        .login-container {
            max-width: 500px;
            margin: 0 auto;
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }

        .tabs {
            display: flex;
            margin-bottom: 2rem;
            border-radius: 10px;
            overflow: hidden;
            background: #f0f2f6;
        }

        .tab {
            flex: 1;
            padding: 1rem;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s ease;
            font-weight: 500;
        }

        .tab.active {
            background: #667eea;
            color: white;
        }

        .tab-content {
            display: none;
        }

        .tab-content.active {
            display: block;
        }

        .form-group {
            margin-bottom: 1.5rem;
        }

        .form-group label {
            display: block;
            margin-bottom: 0.5rem;
            font-weight: 500;
            color: #555;
        }

        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 0.75rem;
            border: 2px solid #e1e5e9;
            border-radius: 8px;
            font-size: 1rem;
            transition: border-color 0.3s ease;
        }

        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #667eea;
        }

        .btn {
            background: #667eea;
            color: white;
            padding: 0.75rem 2rem;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
            display: inline-block;
            text-decoration: none;
            text-align: center;
        }

        .btn:hover {
            background: #5a6fd8;
            transform: translateY(-2px);
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
        }

        .btn-full {
            width: 100%;
        }

        .info-box {
            background: #f8f9fa;
            padding: 1.5rem;
            border-radius: 10px;
            border-left: 5px solid #4CAF50;
            margin-bottom: 2rem;
        }

        .main-app {
            display: none;
        }

        .main-app.active {
            display: block;
        }

        .sidebar {
            position: fixed;
            left: -300px;
            top: 0;
            width: 300px;
            height: 100vh;
            background: white;
            box-shadow: 2px 0 10px rgba(0,0,0,0.1);
            transition: left 0.3s ease;
            z-index: 1000;
            overflow-y: auto;
            padding: 2rem;
        }

        .sidebar.open {
            left: 0;
        }

        .sidebar-toggle {
            position: fixed;
            top: 20px;
            left: 20px;
            background: #667eea;
            color: white;
            border: none;
            padding: 10px;
            border-radius: 5px;
            cursor: pointer;
            z-index: 1001;
        }

        .main-content {
            margin-left: 0;
            padding: 2rem;
            transition: margin-left 0.3s ease;
        }

        .main-content.sidebar-open {
            margin-left: 300px;
        }

        .assessment-form {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            margin-bottom: 2rem;
        }

        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .section-header {
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 8px;
            margin: 2rem 0 1rem 0;
            border-left: 4px solid #667eea;
        }

        .risk-result {
            text-align: center;
            padding: 2rem;
            border-radius: 15px;
            margin: 2rem 0;
            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        }

        .risk-high {
            background: #D32F2F;
            color: white;
        }

        .risk-low {
            background: #4CAF50;
            color: white;
        }

        .patient-summary {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 2rem;
            margin: 2rem 0;
        }

        .summary-card {
            background: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        .alert {
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
        }

        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }

        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .alert-warning {
            background: #fff3cd;
            color: #856404;
            border: 1px solid #ffeaa7;
        }

        .hidden {
            display: none;
        }

        @media (max-width: 768px) {
            .form-row {
                grid-template-columns: 1fr;
            }

            .patient-summary {
                grid-template-columns: 1fr;
            }

            .header h1 {
                font-size: 1.8rem;
            }

            .main-content.sidebar-open {
                margin-left: 0;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Login/Registration Page -->
        <div id="loginPage">
            <div class="header">
                <h1>🏥 Early Breast Cancer Risk Assessment Tool</h1>
                <h3>Evidence-Based Clinical Decision Support System</h3>
                <p>Professional Medical Assessment Platform | Version 2.0</p>
            </div>

            <div class="login-container">
                <div class="info-box">
                    <h4 style="color: #2c3e50; margin-bottom: 1rem;">🎯 Clinical Application</h4>
                    <p style="color: #34495e;">
                        This tool provides evidence-based risk stratification for early breast cancer patients 
                        using validated prognostic factors and treatment guidelines.
                    </p>
                </div>

                <div class="tabs">
                    <div class="tab active" onclick="switchTab('login')">👨‍⚕️ Doctor Login</div>
                    <div class="tab" onclick="switchTab('register')">📝 New Registration</div>
                </div>

                <!-- Login Tab -->
                <div id="loginTab" class="tab-content active">
                    <h3 style="margin-bottom: 1.5rem;">🔐 Access Your Database</h3>
                    <form id="loginForm">
                        <div class="form-group">
                            <label for="loginName">👤 Doctor Name</label>
                            <input type="text" id="loginName" placeholder="Dr. John Smith" required>
                        </div>
                        <div class="form-group">
                            <label for="loginHospital">🏥 Hospital/Institution ID</label>
                            <input type="text" id="loginHospital" placeholder="AIIMS2024" required>
                        </div>
                        <div class="form-group">
                            <label for="loginPassword">🔑 Password</label>
                            <input type="password" id="loginPassword" required>
                        </div>
                        <button type="submit" class="btn btn-full">🚀 Login to EBC Tool</button>
                    </form>
                </div>

                <!-- Registration Tab -->
                <div id="registerTab" class="tab-content">
                    <h3 style="margin-bottom: 1.5rem;">📋 Create New Account</h3>
                    <form id="registerForm">
                        <div class="form-group">
                            <label for="regName">👤 Full Name</label>
                            <input type="text" id="regName" placeholder="Dr. Jane Smith" required>
                        </div>
                        <div class="form-group">
                            <label for="regHospital">🏥 Hospital/Institution ID</label>
                            <input type="text" id="regHospital" placeholder="AIIMS2024" required>
                        </div>
                        <div class="form-group">
                            <label for="regDepartment">🏢 Department</label>
                            <select id="regDepartment" required>
                                <option value="">Select Department</option>
                                <option value="Oncology">Oncology</option>
                                <option value="Surgical Oncology">Surgical Oncology</option>
                                <option value="Radiation Oncology">Radiation Oncology</option>
                                <option value="Hematology-Oncology">Hematology-Oncology</option>
                                <option value="Breast Surgery">Breast Surgery</option>
                                <option value="General Surgery">General Surgery</option>
                                <option value="Internal Medicine">Internal Medicine</option>
                                <option value="Pathology">Pathology</option>
                                <option value="Other">Other</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="regPassword">🔑 Create Password</label>
                            <input type="password" id="regPassword" required>
                        </div>
                        <div class="form-group">
                            <label for="regConfirm">🔑 Confirm Password</label>
                            <input type="password" id="regConfirm" required>
                        </div>
                        <button type="submit" class="btn btn-full">📝 Create Medical Account</button>
                    </form>
                </div>
            </div>
        </div>

        <!-- Main Application -->
        <div id="mainApp" class="main-app">
            <button class="sidebar-toggle" onclick="toggleSidebar()">☰</button>
            
            <div class="sidebar" id="sidebar">
                <h3 style="margin-bottom: 2rem; color: #667eea;">🎯 Navigation</h3>
                
                <div style="margin-bottom: 2rem;">
                    <button class="btn btn-full" onclick="switchPage('assessment')" style="margin-bottom: 0.5rem;">🆕 New Patient Assessment</button>
                    <button class="btn btn-full" onclick="switchPage('database')" style="margin-bottom: 0.5rem;">📊 Patient Database</button>
                    <button class="btn btn-full" onclick="switchPage('analytics')" style="margin-bottom: 0.5rem;">📈 Analytics Dashboard</button>
                    <button class="btn btn-full" onclick="switchPage('export')" style="margin-bottom: 0.5rem;">💾 Export Data</button>
                    <button class="btn btn-full" onclick="switchPage('settings')" style="margin-bottom: 0.5rem;">⚙️ Settings</button>
                </div>

                <hr style="margin: 2rem 0;">

                <div id="quickStats">
                    <h4 style="margin-bottom: 1rem;">📊 Quick Stats</h4>
                    <div style="background: #f8f9fa; padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
                        <div>Total Patients: <span id="totalPatients">0</span></div>
                        <div>High Risk: <span id="highRiskPatients">0</span></div>
                        <div>Avg Risk Score: <span id="avgRiskScore">0</span></div>
                    </div>
                </div>

                <button class="btn btn-full" onclick="logout()" style="background: #dc3545;">🚪 Logout</button>
            </div>

            <div class="main-content" id="mainContent">
                <div class="header">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <h1>🏥 EBC Risk Assessment Tool</h1>
                            <p id="doctorInfo">Dr. [Name] | [Hospital]</p>
                        </div>
                        <div style="text-align: right;">
                            <p style="margin: 0; font-size: 0.9rem;">Version 2.0</p>
                            <p style="margin: 0; font-size: 0.8rem;">Evidence-Based Assessment</p>
                        </div>
                    </div>
                </div>

                <!-- Patient Assessment Page -->
                <div id="assessmentPage" class="page-content">
                    <div class="assessment-form">
                        <h2>📋 Patient Information & Risk Assessment</h2>
                        
                        <div class="section-header">
                            <h3>👤 Section 1: Patient Characteristics</h3>
                        </div>
                        
                        <form id="assessmentForm">
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="uhid">🆔 Patient UHID</label>
                                    <input type="text" id="uhid" placeholder="Enter UHID" required>
                                </div>
                                <div class="form-group">
                                    <label for="patientName">👤 Patient Name</label>
                                    <input type="text" id="patientName" placeholder="Enter full name" required>
                                </div>
                            </div>
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="age">🎂 Age</label>
                                    <input type="number" id="age" min="18" max="120" value="50" required>
                                </div>
                                <div class="form-group">
                                    <label for="menopausalStatus">🔄 Menopausal Status</label>
                                    <select id="menopausalStatus" required>
                                        <option value="Premenopausal">Premenopausal</option>
                                        <option value="Postmenopausal">Postmenopausal</option>
                                    </select>
                                </div>
                            </div>

                            <div class="section-header">
                                <h3>🔬 Section 2: Anatomic Risk</h3>
                            </div>
                            
                            <div class="form-row">
                                <div class="form-group">
                                    <label for="tumorSize">📏 Tumour Size</label>
                                    <select id="tumorSize" required>
                                        <option value="">Select size</option>
                                        <option value="T1 (<2 cm)">T1 (<2 cm)</option>
                                        <option value="T2 (2-5 cm)">T2 (2-5 cm)</option>
                                        <option value="T3 (>5 cm)">T3 (>5 cm)</option>
                                    </select>
                                </div>
                                <div class="form-group">
                                    <label for="nodalStatus">🔗 Nodal Status</label>
                                    <select id="nodalStatus" required>
                                        <option value="">Select status</option>
                                        <option value="N0 (0 nodes)">N0 (0 nodes)</option>
                                        <option value="N1 (1-3 nodes)">N1 (1-3 nodes)</option>
                                        <option value="N2+ (>=4 nodes)">N2+ (>=4 nodes)</option>
                                    </select>
                                </div>
                            </div>

                            <div class="section-header">
                                <h3>🧬 Section 3: Tumor Biology/Genomic</h3>
                            </div>
                            
                            <div class="form-row">
                                <div>
                                    <div class="form-group">
                                        <label for="tumorGrade">⭐ Grading</label>
                                        <select id="tumorGrade" required>
                                            <option value="">Select grade</option>
                                            <option value="Grade 1">Grade 1</option>
                                            <option value="Grade 2">Grade 2</option>
                                            <option value="Grade 3">Grade 3</option>
                                        </select>
                                    </div>
                                    <div class="form-group">
                                        <label for="ki67">📊 Ki-67 (%)</label>
                                        <input type="number" id="ki67" min="0" max="100" step="0.1" value="15" required>
                                    </div>
                                </div>
                                <div>
                                    <div class="form-group">
                                        <label for="genomicTestName">Genomic Test Name</label>
                                        <input type="text" id="genomicTestName" placeholder="e.g., Oncotype DX, MammaPrint">
                                    </div>
                                    <div class="form-group">
                                        <label for="genomicTestReport">Test Report</label>
                                        <textarea id="genomicTestReport" rows="3" placeholder="Enter test results/report details"></textarea>
                                    </div>
                                </div>
                            </div>
                            
                            <div style="text-align: center; margin: 2rem 0;">
                                <button type="submit" class="btn" style="padding: 1rem 3rem; font-size: 1.1rem;">
                                    🔬 Submit & Calculate Risk
                                </button>
                            </div>
                        </form>
                        
                        <div id="assessmentResult" class="hidden">
                            <!-- Results will be displayed here -->
                        </div>
                    </div>
                </div>

                <!-- Other pages -->
                <div id="databasePage" class="page-content hidden">
                    <h2>📊 Patient Database & Records</h2>
                    <div class="assessment-form">
                        <p>Patient database functionality would be implemented here.</p>
                    </div>
                </div>

                <div id="analyticsPage" class="page-content hidden">
                    <h2>📈 Analytics & Insights Dashboard</h2>
                    <div class="assessment-form">
                        <p>Analytics dashboard would be implemented here.</p>
                    </div>
                </div>

                <div id="exportPage" class="page-content hidden">
                    <h2>💾 Export Patient Data</h2>
                    <div class="assessment-form">
                        <p>Data export functionality would be implemented here.</p>
                    </div>
                </div>

                <div id="settingsPage" class="page-content hidden">
                    <h2>⚙️ Account Settings</h2>
                    <div class="assessment-form">
                        <p>Settings functionality would be implemented here.</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Application state
        let currentUser = null;
        let patients = [];
        let sidebarOpen = false;

        // Tab switching for login/register
        function switchTab(tab) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
            
            if (tab === 'login') {
                document.querySelector('.tab:first-child').classList.add('active');
                document.getElementById('loginTab').classList.add('active');
            } else {
                document.querySelector('.tab:last-child').classList.add('active');
                document.getElementById('registerTab').classList.add('active');
            }
        }

        // Login form handler
        document.getElementById('loginForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const name = document.getElementById('loginName').value;
            const hospital = document.getElementById('loginHospital').value;
            const password = document.getElementById('loginPassword').value;
            
            if (name && hospital && password) {
                // Simulate login (in real app, this would authenticate against backend)
                currentUser = {
                    name: name,
                    hospital: hospital,
                    id: name.toLowerCase().replace(/\s+/g, '_') + '_' + hospital.toLowerCase()
                };
                
                // Load stored data
                loadUserData();
                
                // Switch to main app
                document.getElementById('loginPage').style.display = 'none';
                document.getElementById('mainApp').classList.add('active');
                
                // Update header
                document.getElementById('doctorInfo').textContent = `Dr. ${name} | ${hospital}`;
                
                showAlert('✅ Authentication successful! Loading your workspace...', 'success');
            } else {
                showAlert('⚠️ Please fill in all required fields', 'warning');
            }
        });

        // Registration form handler
        document.getElementById('registerForm').addEventListener('submit', function(e) {
            e.preventDefault();
            
            const name = document.getElementById('regName').value;
            const hospital = document.getElementById('regHospital').value;
            const department = document.getElementById('regDepartment').value;
            const password = document.getElementById('regPassword').value;
            const confirm = document.getElementById('regConfirm').value;
            
            if (name && hospital && department && password && confirm) {
                if (password === confirm) {
                    if (password.length >= 6) {
                        const doctorId = name.toLowerCase().replace(/\s+/g, '_') + '_' + hospital.toLowerCase();
                        
                        // Store registration (in real app, this would be sent to backend)
                        const userData = {
                            name: name,
                            hospital: hospital,
                            department: department,
                            id: doctorId,
                            created: new Date().toISOString()
                        };
                        
                        localStorage.setItem('user_' + doctorId, JSON.stringify(userData));
                        
                        showAlert('✅ Account created successfully!', 'success');
                        showAlert(`🆔 Your Doctor ID: ${doctorId}`, 'success');
                        showAlert('👈 Please use the "Doctor Login" tab to access your workspace', 'success');
                        
                        // Switch to login tab
                        switchTab('login');
                        
                        // Clear form
                        document.getElementById('registerForm').reset();
                    } else {
                        showAlert
