# EBC Risk Assessment Web App - Matching Portable App Interface
# Enhanced with multi-doctor authentication while preserving original interface
# Save as: ebc_web_app.py

import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import os
from pathlib import Path
from datetime import datetime
import json
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="EBC Risk Assessment Tool",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database directory
DB_DIR = Path("doctor_databases")
DB_DIR.mkdir(exist_ok=True)

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_doctor_profile(doctor_name, hospital_id, department, password):
    """Create a new doctor profile"""
    doctor_id = f"{doctor_name.replace(' ', '_').lower()}_{hospital_id.lower()}"
    doctor_db = DB_DIR / f"{doctor_id}.db"
    
    # Create doctor's database
    conn = sqlite3.connect(doctor_db)
    cursor = conn.cursor()
    
    # Create tables matching original app structure
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctor_info (
            doctor_id TEXT PRIMARY KEY,
            name TEXT,
            hospital_id TEXT,
            department TEXT,
            password_hash TEXT,
            created_at TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            uhid TEXT UNIQUE,
            patient_name TEXT,
            age INTEGER,
            menopausal_status TEXT,
            tumor_size REAL,
            lymph_nodes_positive INTEGER,
            tumor_grade TEXT,
            er_status TEXT,
            pr_status TEXT,
            her2_status TEXT,
            ki67_percentage REAL,
            histological_type TEXT,
            assessment_date TIMESTAMP,
            risk_score REAL,
            risk_category TEXT,
            treatment_recommendation TEXT,
            notes TEXT,
            
            -- Additional fields matching original app
            chemotherapy_recommendation TEXT,
            hormonal_therapy_recommendation TEXT,
            radiation_therapy_recommendation TEXT,
            follow_up_plan TEXT,
            prognosis TEXT
        )
    ''')
    
    # Insert doctor info
    cursor.execute('''
        INSERT OR REPLACE INTO doctor_info 
        (doctor_id, name, hospital_id, department, password_hash, created_at, last_login)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (doctor_id, doctor_name, hospital_id, department, 
          hash_password(password), datetime.now(), datetime.now()))
    
    conn.commit()
    conn.close()
    
    return doctor_id

def verify_doctor_login(doctor_name, hospital_id, password):
    """Verify doctor login credentials"""
    doctor_id = f"{doctor_name.replace(' ', '_').lower()}_{hospital_id.lower()}"
    doctor_db = DB_DIR / f"{doctor_id}.db"
    
    if not doctor_db.exists():
        return None
    
    conn = sqlite3.connect(doctor_db)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT password_hash FROM doctor_info WHERE doctor_id = ?
    ''', (doctor_id,))
    
    result = cursor.fetchone()
    if result and result[0] == hash_password(password):
        # Update last login
        cursor.execute('''
            UPDATE doctor_info SET last_login = ? WHERE doctor_id = ?
        ''', (datetime.now(), doctor_id))
        conn.commit()
        conn.close()
        return doctor_id
    
    conn.close()
    return None

def get_doctor_database(doctor_id):
    """Get connection to doctor's database"""
    doctor_db = DB_DIR / f"{doctor_id}.db"
    return sqlite3.connect(doctor_db)

def login_page():
    """Display login/registration page"""
    
    # Header matching original design
    st.markdown("""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; 
                border-radius: 15px; 
                margin-bottom: 2rem;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);">
        <h1 style="color: white; text-align: center; font-size: 2.5rem; margin: 0;">
            🏥 Early Breast Cancer Risk Assessment Tool
        </h1>
        <h3 style="color: #f0f2f6; text-align: center; margin: 1rem 0 0 0;">
            Evidence-Based Clinical Decision Support System
        </h3>
        <p style="color: #e1e5f0; text-align: center; margin: 0.5rem 0 0 0;">
            Professional Medical Assessment Platform | Version 2.0
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Info section matching original
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border-left: 5px solid #4CAF50;">
            <h4 style="color: #2c3e50; margin-top: 0;">🎯 Clinical Application</h4>
            <p style="color: #34495e; margin-bottom: 0;">
                This tool provides evidence-based risk stratification for early breast cancer patients 
                using validated prognostic factors and treatment guidelines.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Login/Registration tabs
        tab1, tab2 = st.tabs(["👨‍⚕️ Doctor Login", "📝 New Registration"])
        
        with tab1:
            st.markdown("### 🔐 Access Your Database")
            
            login_name = st.text_input("👤 Doctor Name", placeholder="Dr. John Smith", key="login_name")
            login_hospital = st.text_input("🏥 Hospital/Institution ID", placeholder="AIIMS2024", key="login_hospital")
            login_password = st.text_input("🔑 Password", type="password", key="login_password")
            
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                if st.button("🚀 Login to EBC Tool", type="primary", use_container_width=True):
                    if login_name and login_hospital and login_password:
                        doctor_id = verify_doctor_login(login_name, login_hospital, login_password)
                        if doctor_id:
                            st.session_state.doctor_id = doctor_id
                            st.session_state.doctor_name = login_name
                            st.session_state.hospital_id = login_hospital
                            st.success("✅ Authentication successful! Loading your workspace...")
                            st.rerun()
                        else:
                            st.error("❌ Invalid credentials. Please check your details.")
                    else:
                        st.warning("⚠️ Please fill in all required fields")
        
        with tab2:
            st.markdown("### 📋 Create New Account")
            
            reg_name = st.text_input("👤 Full Name", placeholder="Dr. Jane Smith", key="reg_name")
            reg_hospital = st.text_input("🏥 Hospital/Institution ID", placeholder="AIIMS2024", key="reg_hospital")
            reg_department = st.selectbox("🏢 Department", [
                "Oncology", "Surgical Oncology", "Radiation Oncology", "Hematology-Oncology",
                "Breast Surgery", "General Surgery", "Internal Medicine", "Pathology", "Other"
            ], key="reg_department")
            reg_password = st.text_input("🔑 Create Password", type="password", key="reg_password")
            reg_confirm = st.text_input("🔑 Confirm Password", type="password", key="reg_confirm")
            
            col_a, col_b, col_c = st.columns([1, 2, 1])
            with col_b:
                if st.button("📝 Create Medical Account", type="primary", use_container_width=True):
                    if all([reg_name, reg_hospital, reg_department, reg_password, reg_confirm]):
                        if reg_password == reg_confirm:
                            if len(reg_password) >= 6:
                                doctor_id = create_doctor_profile(
                                    reg_name, reg_hospital, reg_department, reg_password
                                )
                                st.success(f"✅ Account created successfully!")
                                st.info(f"🆔 Your Doctor ID: {doctor_id}")
                                st.info("👈 Please use the 'Doctor Login' tab to access your workspace")
                            else:
                                st.error("❌ Password must be at least 6 characters")
                        else:
                            st.error("❌ Passwords don't match")
                    else:
                        st.warning("⚠️ Please fill in all required fields")

# Original risk calculation functions (unchanged)
def calculate_nottingham_prognostic_index(tumor_size, lymph_nodes, grade):
    """Calculate Nottingham Prognostic Index"""
    # Tumor size score
    if tumor_size <= 2:
        size_score = 1
    elif tumor_size <= 5:
        size_score = 2
    else:
        size_score = 3
    
    # Lymph node score  
    if lymph_nodes == 0:
        node_score = 1
    elif lymph_nodes <= 3:
        node_score = 2
    else:
        node_score = 3
    
    # Grade score
    grade_scores = {"Grade 1": 1, "Grade 2": 2, "Grade 3": 3}
    grade_score = grade_scores.get(grade, 2)
    
    # NPI calculation: (0.2 × size) + node_score + grade_score
    npi = (0.2 * tumor_size) + node_score + grade_score
    
    return npi, size_score, node_score, grade_score

def calculate_comprehensive_risk_score(tumor_size, nodes_positive, grade, er_status, pr_status, 
                                     her2_status, age, ki67, histological_type):
    """Enhanced comprehensive risk calculation"""
    
    risk_score = 0
    risk_factors = []
    
    # Nottingham Prognostic Index
    npi, size_score, node_score, grade_score = calculate_nottingham_prognostic_index(
        tumor_size, nodes_positive, grade)
    
    # Base NPI contribution (30% of total score)
    npi_contribution = (npi / 6.8) * 30  # Normalize NPI to 30-point scale
    risk_score += npi_contribution
    
    # Molecular subtype scoring (25% of total score)
    if er_status == "Positive" and pr_status == "Positive" and her2_status == "Negative":
        molecular_score = 5  # Luminal A-like (good prognosis)
        subtype = "Luminal A-like"
    elif er_status == "Positive" and her2_status == "Negative":
        molecular_score = 10  # Luminal B-like
        subtype = "Luminal B-like"
    elif her2_status == "Positive":
        molecular_score = 20  # HER2-positive
        subtype = "HER2-positive"
    else:
        molecular_score = 25  # Triple-negative (poor prognosis)
        subtype = "Triple-negative"
    
    risk_score += molecular_score
    risk_factors.append(f"Molecular subtype: {subtype}")
    
    # Ki67 proliferation index (15% of total score)
    if ki67 < 14:
        ki67_score = 2
        risk_factors.append("Low proliferation (Ki67 < 14%)")
    elif ki67 < 30:
        ki67_score = 8
        risk_factors.append("Moderate proliferation (Ki67 14-30%)")
    else:
        ki67_score = 15
        risk_factors.append("High proliferation (Ki67 > 30%)")
    
    risk_score += ki67_score
    
    # Age factor (10% of total score)
    if age < 35:
        age_score = 10
        risk_factors.append("Young age (< 35 years)")
    elif age < 50:
        age_score = 5
        risk_factors.append("Premenopausal age")
    elif age > 70:
        age_score = 3
        risk_factors.append("Elderly (> 70 years)")
    else:
        age_score = 0
    
    risk_score += age_score
    
    # Histological type (5% of total score)
    histology_scores = {
        "Invasive Ductal Carcinoma": 2,
        "Invasive Lobular Carcinoma": 1,
        "Mixed Ductal and Lobular": 3,
        "Inflammatory Breast Cancer": 5,
        "Other": 2
    }
    hist_score = histology_scores.get(histological_type, 2)
    risk_score += hist_score
    
    # Additional risk factors (15% of total score)
    additional_score = 0
    
    if tumor_size > 5:
        additional_score += 5
        risk_factors.append("Large tumor (> 5 cm)")
    
    if nodes_positive > 10:
        additional_score += 5
        risk_factors.append("Extensive nodal involvement (> 10 nodes)")
    
    if grade == "Grade 3":
        additional_score += 3
        risk_factors.append("High-grade tumor")
    
    risk_score += additional_score
    
    # Normalize to 100-point scale
    final_score = min(100, max(0, risk_score))
    
    return final_score, npi, risk_factors, subtype

def get_risk_category_detailed(score):
    """Detailed risk categorization"""
    if score < 15:
        return "Very Low Risk", "#4CAF50", "Excellent prognosis"
    elif score < 30:
        return "Low Risk", "#8BC34A", "Good prognosis"
    elif score < 50:
        return "Intermediate Risk", "#FF9800", "Moderate prognosis"
    elif score < 70:
        return "High Risk", "#FF5722", "Poor prognosis"
    else:
        return "Very High Risk", "#D32F2F", "Very poor prognosis"

def generate_treatment_recommendations(score, er_status, pr_status, her2_status, age, tumor_size, nodes_positive):
    """Generate comprehensive treatment recommendations"""
    
    recommendations = {
        "chemotherapy": [],
        "hormonal": [],
        "targeted": [],
        "radiation": [],
        "surgery": [],
        "follow_up": []
    }
    
    # Chemotherapy recommendations
    if score >= 30 or nodes_positive > 0 or tumor_size > 2:
        if age < 70:
            if score >= 50:
                recommendations["chemotherapy"].append("Anthracycline + Taxane based regimen")
                recommendations["chemotherapy"].append("Consider dose-dense protocols")
            else:
                recommendations["chemotherapy"].append("Standard adjuvant chemotherapy")
                recommendations["chemotherapy"].append("TC or AC-T regimen")
        else:
            recommendations["chemotherapy"].append("Consider single-agent chemotherapy")
            recommendations["chemotherapy"].append("Assess comorbidities and performance status")
    
    # Hormonal therapy
    if er_status == "Positive" or pr_status == "Positive":
        if age < 50:  # Premenopausal
            recommendations["hormonal"].append("Tamoxifen 20mg daily for 5-10 years")
            recommendations["hormonal"].append("Consider ovarian suppression (GnRH agonist)")
            if score >= 50:
                recommendations["hormonal"].append("Consider extended therapy")
        else:  # Postmenopausal
            recommendations["hormonal"].append("Aromatase inhibitor (preferred) or Tamoxifen")
            recommendations["hormonal"].append("Duration: 5-10 years")
            if score >= 40:
                recommendations["hormonal"].append("Consider extended AI therapy")
    
    # Targeted therapy
    if her2_status == "Positive":
        recommendations["targeted"].append("Trastuzumab 1 year (every 3 weeks)")
        if score >= 50:
            recommendations["targeted"].append("Consider dual HER2 blockade (Trastuzumab + Pertuzumab)")
        recommendations["targeted"].append("Monitor cardiac function (ECHO/MUGA)")
    
    # Radiation therapy
    if tumor_size > 4 or nodes_positive >= 4:
        recommendations["radiation"].append("Post-mastectomy radiation therapy indicated")
    
    recommendations["radiation"].append("Breast conserving surgery: whole breast radiation")
    recommendations["radiation"].append("Consider hypofractionated regimens")
    
    if nodes_positive > 0:
        recommendations["radiation"].append("Include regional lymph nodes")
    
    # Surgical recommendations
    if tumor_size <= 3 and nodes_positive <= 2:
        recommendations["surgery"].append("Breast conserving surgery option")
        recommendations["surgery"].append("Sentinel lymph node biopsy")
    else:
        recommendations["surgery"].append("Consider mastectomy")
        recommendations["surgery"].append("Axillary lymph node dissection may be needed")
    
    # Follow-up
    recommendations["follow_up"].append("Clinical examination every 3-6 months for 3 years")
    recommendations["follow_up"].append("Annual mammography")
    recommendations["follow_up"].append("Monitor for treatment-related side effects")
    
    if score >= 50:
        recommendations["follow_up"].append("More frequent monitoring in first 2 years")
        recommendations["follow_up"].append("Consider additional imaging (MRI/CT)")
    
    return recommendations

def main_app():
    """Main application interface matching original design"""
    
    # Header matching original style
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                padding: 1.5rem; 
                border-radius: 15px; 
                margin-bottom: 2rem;
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <h1 style="color: white; margin: 0; font-size: 2rem;">🏥 EBC Risk Assessment Tool</h1>
                <p style="color: #f0f2f6; margin: 0.5rem 0 0 0;">Dr. {st.session_state.doctor_name} | {st.session_state.hospital_id}</p>
            </div>
            <div style="text-align: right;">
                <p style="color: #e1e5f0; margin: 0; font-size: 0.9rem;">Version 2.0</p>
                <p style="color: #e1e5f0; margin: 0; font-size: 0.8rem;">Evidence-Based Assessment</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar matching original design
    with st.sidebar:
        st.markdown("### 🎯 Navigation")
        
        # Main functions
        page = st.selectbox("📋 Select Function", [
            "🆕 New Patient Assessment",
            "📊 Patient Database", 
            "📈 Analytics Dashboard",
            "💾 Export Data",
            "⚙️ Settings"
        ])
        
        st.markdown("---")
        
        # Quick stats
        conn = get_doctor_database(st.session_state.doctor_id)
        df_stats = pd.read_sql_query("SELECT COUNT(*) as total, AVG(risk_score) as avg_risk FROM patients", conn)
        
        if df_stats['total'].iloc[0] > 0:
            st.markdown("### 📊 Quick Stats")
            st.metric("Total Patients", int(df_stats['total'].iloc[0]))
            st.metric("Avg Risk Score", f"{df_stats['avg_risk'].iloc[0]:.1f}")
            
            # Risk distribution
            risk_dist = pd.read_sql_query("""
                SELECT risk_category, COUNT(*) as count 
                FROM patients 
                GROUP BY risk_category
            """, conn)
            
            if len(risk_dist) > 0:
                st.markdown("**Risk Distribution:**")
                for _, row in risk_dist.iterrows():
                    st.text(f"• {row['risk_category']}: {row['count']}")
        
        conn.close()
        
        st.markdown("---")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content area
    conn = get_doctor_database(st.session_state.doctor_id)
    
    if page == "🆕 New Patient Assessment":
        
        # Patient Assessment Form (matching original layout)
        st.markdown("### 📋 Patient Information & Risk Assessment")
        
        # Patient demographics
        st.markdown("#### 👤 Patient Demographics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            uhid = st.text_input("🆔 UHID/MRN", placeholder="Hospital ID", help="Unique Hospital Identification")
            patient_name = st.text_input("👤 Patient Name", placeholder="Full name")
        
        with col2:
            age = st.number_input("🎂 Age (years)", min_value=18, max_value=100, value=50)
            menopausal_status = st.selectbox("🔄 Menopausal Status", 
                ["Pre-menopausal", "Post-menopausal", "Peri-menopausal"])
        
        with col3:
            assessment_date = st.date_input("📅 Assessment Date", value=datetime.now().date())
        
        st.markdown("---")
        
        # Tumor characteristics
        st.markdown("#### 🔬 Tumor Characteristics")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tumor_size = st.number_input("📏 Tumor Size (cm)", 
                                       min_value=0.1, max_value=20.0, value=2.0, step=0.1,
                                       help="Largest diameter of invasive component")
            lymph_nodes = st.number_input("🔗 Positive Lymph Nodes", 
                                        min_value=0, max_value=50, value=0,
                                        help="Number of positive lymph nodes")
        
        with col2:
            tumor_grade = st.selectbox("⭐ Tumor Grade", 
                                     ["Grade 1", "Grade 2", "Grade 3"],
                                     help="Nottingham histologic grade")
            histological_type = st.selectbox("🧪 Histological Type", [
                "Invasive Ductal Carcinoma", 
                "Invasive Lobular Carcinoma", 
                "Mixed Ductal and Lobular", 
                "Inflammatory Breast Cancer",
                "Other"
            ])
        
        with col3:
            ki67 = st.number_input("📊 Ki67 Index (%)", 
                                 min_value=0.0, max_value=100.0, value=15.0, step=0.1,
                                 help="Proliferation marker percentage")
        
        st.markdown("---")
        
        # Biomarkers
        st.markdown("#### 🧬 Biomarker Status")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            er_status = st.selectbox("🟢 ER Status", ["Positive", "Negative"],
                                   help="Estrogen Receptor status")
            pr_status = st.selectbox("🔵 PR Status", ["Positive", "Negative"],
                                   help="Progesterone Receptor status")
        
        with col2:
            her2_status = st.selectbox("🟡 HER2 Status", ["Positive", "Negative", "Equivocal"],
                                     help="HER2/neu status")
        
        with col3:
            st.markdown("**Molecular Subtype (Auto-calculated)**")
            if er_status == "Positive" and her2_status == "Negative":
                if ki67 < 14:
                    subtype_preview = "Luminal A-like"
                else:
                    subtype_preview = "Luminal B-like"
            elif her2_status == "Positive":
                subtype_preview = "HER2-positive"
            else:
                subtype_preview = "Triple-negative"
            
            st.info(f"Predicted: {subtype_preview}")
        
        # Clinical notes
        st.markdown("#### 📝 Clinical Notes")
        notes = st.text_area("Additional Information", 
                           placeholder="Comorbidities, family history, previous treatments, etc.",
                           height=100)
        
        # Calculate button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            calculate_button = st.button("🔬 Calculate Risk Assessment", 
                                       type="primary", 
                                       use_container_width=True,
                                       help="Perform comprehensive risk analysis")
        
        # Risk calculation and display
        if calculate_button:
            if uhid and patient_name:
                # Perform calculations
                risk_score, npi, risk_factors, molecular_subtype = calculate_comprehensive_risk_score(
                    tumor_size, lymph_nodes, tumor_grade, er_status, pr_status, 
                    her2_status, age, ki67, histological_type
                )
                
                risk_category, risk_color, prognosis = get_risk_category_detailed(risk_score)
                treatment_recs = generate_treatment_recommendations(
                    risk_score, er_status, pr_status, her2_status, age, tumor_size, lymph_nodes
                )
                
                # Display results in original style
                st.markdown("---")
                st.markdown("## 🎯 Risk Assessment Results")
                
                # Main metrics
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.markdown(f"""
                    <div style="background: linear-gradient(45deg, #FF6B6B, #FF8E8E); 
                                padding: 1rem; border-radius: 10px; text-align: center;">
                        <h3 style="color: white; margin: 0;">Risk Score</h3>
                        <h1 style="color: white; margin: 0;">{risk_score:.1f}</h1>
                        <p style="color: white; margin: 0;">/ 100</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown(f"""
                    <div style="background: {risk_color}; 
                                padding: 1rem; border-radius: 10px; text-align: center;">
                        <h3 style="color: white; margin: 0;">Risk Category</h3>
                        <h2 style="color: white; margin: 0;">{risk_category}</h2>
                        <p style="color: white; margin: 0;">{prognosis}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col3:
                    st.markdown(f"""
                    <div style="background: linear-gradient(45deg, #4ECDC4, #44A08D); 
                                padding: 1rem; border-radius: 10px; text-align: center;">
                        <h3 style="color: white; margin: 0;">NPI Score</h3>
                        <h1 style="color: white; margin: 0;">{npi:.1f}</h1>
                        <p style="color: white; margin: 0;">Nottingham Index</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col4:
                    st.markdown(f"""
                    <div style="background: linear-gradient(45deg, #A8EDEA, #FED6E3); 
                                padding: 1rem; border-radius: 10px; text-align: center;">
                        <h3 style="color: #2c3e50; margin: 0;">Molecular Type</h3>
                        <h2 style="color: #2c3e50; margin: 0;">{molecular_subtype}</h2>
                        <p style="color: #2c3e50; margin: 0;">Subtype</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Risk factors
                st.markdown("### 🚨 Risk Factors Identified")
                if risk_factors:
                    for factor in risk_factors:
                        st.markdown(f"• {factor}")
                else:
                    st.info("No significant risk factors identified")
                
                # Treatment recommendations
                st.markdown("### 💊 Treatment Recommendations")
                
                tab1, tab2, tab3, tab4 = st.tabs(["🧪 Systemic Therapy", "⚡ Radiation", "🔪 Surgery", "📅 Follow-up"])
                
                with tab1:
                    if treatment_recs["chemotherapy"]:
                        st.markdown("**Chemotherapy:**")
                        for rec in treatment_recs["chemotherapy"]:
                            st.markdown(f"• {rec}")
                    
                    if treatment_recs["hormonal"]:
                        st.markdown("**Hormonal Therapy:**")
                        for rec in treatment_recs["hormonal"]:
                            st.markdown(f"• {rec}")
                    
                    if treatment_recs["targeted"]:
                        st.markdown("**Targeted Therapy:**")
                        for rec in treatment_recs["targeted"]:
                            st.markdown(f"• {rec}")
                
                with tab2:
                    for rec in treatment_recs["radiation"]:
                        st.markdown(f"• {rec}")
                
                with tab3:
                    for rec in treatment_recs["surgery"]:
                        st.markdown(f"• {rec}")
                
                with tab4:
                    for rec in treatment_recs["follow_up"]:
                        st.markdown(f"• {rec}")
                
                # Risk visualization
                st.markdown("### 📊 Risk Visualization")
                
                # Create risk gauge chart
                fig_gauge = go.Figure(go.Indicator(
                    mode = "gauge+number+delta",
                    value = risk_score,
                    domain = {'x': [0, 1], 'y': [0, 1]},
                    title = {'text': "Risk Score"},
                    delta = {'reference': 50},
                    gauge = {
                        'axis': {'range': [None, 100]},
                        'bar': {'color': risk_color},
                        'steps': [
                            {'range': [0, 15], 'color': "#E8F5E8"},
                            {'range': [15, 30], 'color': "#C8E6C9"},
                            {'range': [30, 50], 'color': "#FFE0B2"},
                            {'range': [50, 70], 'color': "#FFCDD2"},
                            {'range': [70, 100], 'color': "#FFCDD2"}
                        ],
                        'threshold': {
                            'line': {'color': "red", 'width': 4},
                            'thickness': 0.75,
                            'value': 90
                        }
                    }
                ))
                
                fig_gauge.update_layout(height=300)
                st.plotly_chart(fig_gauge, use_container_width=True)
                
                # Save to database
                cursor = conn.cursor()
                
                # Prepare treatment recommendations as text
                all_recs = []
                for category, recs in treatment_recs.items():
                    if recs:
                        all_recs.extend([f"{category.title()}: {rec}" for rec in recs])
                
                treatment_text = "; ".join(all_recs)
                
                cursor.execute('''
                    INSERT OR REPLACE INTO patients 
                    (uhid, patient_name, age, menopausal_status, tumor_size, lymph_nodes_positive,
                     tumor_grade, er_status, pr_status, her2_status, ki67_percentage, 
                     histological_type, assessment_date, risk_score, risk_category, 
                     treatment_recommendation, notes, chemotherapy_recommendation, 
                     hormonal_therapy_recommendation, radiation_therapy_recommendation, 
                     follow_up_plan, prognosis)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (uhid, patient_name, age, menopausal_status, tumor_size, lymph_nodes,
                      tumor_grade, er_status, pr_status, her2_status, ki67,
                      histological_type, assessment_date, risk_score, risk_category,
                      treatment_text, notes, 
                      "; ".join(treatment_recs["chemotherapy"]),
                      "; ".join(treatment_recs["hormonal"]),
                      "; ".join(treatment_recs["radiation"]),
                      "; ".join(treatment_recs["follow_up"]),
                      prognosis))
                
                conn.commit()
                
                st.success("✅ Patient assessment completed and saved successfully!")
                
                # Option to print/export
                col1, col2, col3 = st.columns(3)
                with col2:
                    if st.button("📄 Generate Report", use_container_width=True):
                        st.info("Report generation feature - would export detailed PDF report")
            
            else:
                st.error("❌ Please provide UHID and Patient Name")
    
    elif page == "📊 Patient Database":
        st.markdown("### 📊 Patient Database & Records")
        
        # Get all patients
        df = pd.read_sql_query("""
            SELECT uhid, patient_name, age, tumor_size, lymph_nodes_positive, 
                   risk_score, risk_category, assessment_date, er_status, her2_status
            FROM patients 
            ORDER BY assessment_date DESC
        """, conn)
        
        if not df.empty:
            # Search and filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_term = st.text_input("🔍 Search Patients", placeholder="Name or UHID")
            
            with col2:
                risk_filter = st.selectbox("📈 Filter by Risk", 
                    ["All", "Very Low Risk", "Low Risk", "Intermediate Risk", "High Risk", "Very High Risk"])
            
            with col3:
                sort_by = st.selectbox("📋 Sort by", 
                    ["Assessment Date", "Risk Score", "Patient Name", "Age"])
            
            # Apply filters
            filtered_df = df.copy()
            
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['patient_name'].str.contains(search_term, case=False, na=False) |
                    filtered_df['uhid'].str.contains(search_term, case=False, na=False)
                ]
            
            if risk_filter != "All":
                filtered_df = filtered_df[filtered_df['risk_category'] == risk_filter]
            
            # Display results
            st.markdown(f"**Showing {len(filtered_df)} of {len(df)} patients**")
            
            if len(filtered_df) > 0:
                # Color code the dataframe
                def color_risk_score(val):
                    if val < 30:
                        color = '#4CAF50'  # Green
                    elif val < 50:
                        color = '#FF9800'  # Orange
                    else:
                        color = '#F44336'  # Red
                    return f'background-color: {color}; color: white'
                
                styled_df = filtered_df.style.applymap(color_risk_score, subset=['risk_score'])
                st.dataframe(styled_df, use_container_width=True, height=400)
                
                # Quick statistics
                st.markdown("### 📈 Database Statistics")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Total Patients", len(df))
                
                with col2:
                    high_risk_count = len(df[df['risk_category'].isin(['High Risk', 'Very High Risk'])])
                    st.metric("High Risk Patients", high_risk_count)
                
                with col3:
                    avg_age = df['age'].mean()
                    st.metric("Average Age", f"{avg_age:.1f} years")
                
                with col4:
                    avg_risk = df['risk_score'].mean()
                    st.metric("Average Risk Score", f"{avg_risk:.1f}")
                
                # Patient detail view
                st.markdown("### 👤 Patient Details")
                selected_uhid = st.selectbox("Select Patient for Details:", 
                                           filtered_df['uhid'].tolist() if len(filtered_df) > 0 else [])
                
                if selected_uhid:
                    patient_detail = pd.read_sql_query(
                        "SELECT * FROM patients WHERE uhid = ?", 
                        conn, params=[selected_uhid]
                    )
                    
                    if len(patient_detail) > 0:
                        patient = patient_detail.iloc[0]
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Patient Information:**")
                            st.text(f"Name: {patient['patient_name']}")
                            st.text(f"UHID: {patient['uhid']}")
                            st.text(f"Age: {patient['age']} years")
                            st.text(f"Menopausal Status: {patient['menopausal_status']}")
                            
                            st.markdown("**Tumor Characteristics:**")
                            st.text(f"Size: {patient['tumor_size']} cm")
                            st.text(f"Grade: {patient['tumor_grade']}")
                            st.text(f"Positive Nodes: {patient['lymph_nodes_positive']}")
                            st.text(f"Histology: {patient['histological_type']}")
                        
                        with col2:
                            st.markdown("**Biomarkers:**")
                            st.text(f"ER Status: {patient['er_status']}")
                            st.text(f"PR Status: {patient['pr_status']}")
                            st.text(f"HER2 Status: {patient['her2_status']}")
                            st.text(f"Ki67: {patient['ki67_percentage']}%")
                            
                            st.markdown("**Risk Assessment:**")
                            st.text(f"Risk Score: {patient['risk_score']:.1f}")
                            st.text(f"Risk Category: {patient['risk_category']}")
                            st.text(f"Assessment Date: {patient['assessment_date']}")
                        
                        if patient['notes']:
                            st.markdown("**Clinical Notes:**")
                            st.text_area("", value=patient['notes'], height=100, disabled=True)
                        
                        if patient['treatment_recommendation']:
                            st.markdown("**Treatment Recommendations:**")
                            st.text_area("", value=patient['treatment_recommendation'], height=150, disabled=True)
            
            else:
                st.info("No patients match the current filters")
        
        else:
            st.info("📝 No patients in database yet. Start with 'New Patient Assessment'")
    
    elif page == "📈 Analytics Dashboard":
        st.markdown("### 📈 Analytics & Insights Dashboard")
        
        df = pd.read_sql_query("SELECT * FROM patients ORDER BY assessment_date DESC", conn)
        
        if not df.empty and len(df) >= 3:
            # Risk distribution pie chart
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### Risk Category Distribution")
                risk_counts = df['risk_category'].value_counts()
                
                fig_pie = px.pie(
                    values=risk_counts.values, 
                    names=risk_counts.index,
                    title="Patient Risk Distribution",
                    color_discrete_map={
                        'Very Low Risk': '#4CAF50',
                        'Low Risk': '#8BC34A',
                        'Intermediate Risk': '#FF9800',
                        'High Risk': '#FF5722',
                        'Very High Risk': '#D32F2F'
                    }
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.markdown("#### Risk Score Distribution")
                fig_hist = px.histogram(
                    df, x='risk_score', 
                    nbins=20,
                    title="Risk Score Histogram",
                    labels={'risk_score': 'Risk Score', 'count': 'Number of Patients'}
                )
                fig_hist.update_traces(marker_color='#667eea')
                st.plotly_chart(fig_hist, use_container_width=True)
            
            # Age vs Risk scatter
            st.markdown("#### Age vs Risk Score Analysis")
            fig_scatter = px.scatter(
                df, x='age', y='risk_score',
                color='risk_category',
                size='tumor_size',
                title="Age vs Risk Score (bubble size = tumor size)",
                labels={'age': 'Age (years)', 'risk_score': 'Risk Score'}
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Biomarker analysis
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### ER/PR Status Distribution")
                hormone_status = df.groupby(['er_status', 'pr_status']).size().reset_index(name='count')
                hormone_status['combined'] = hormone_status['er_status'] + '/' + hormone_status['pr_status']
                
                fig_bar = px.bar(
                    hormone_status, x='combined', y='count',
                    title="ER/PR Status Distribution",
                    labels={'combined': 'ER/PR Status', 'count': 'Number of Patients'}
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                st.markdown("#### Risk Score by Molecular Subtype")
                # Create molecular subtype column
                def get_molecular_subtype(row):
                    if row['er_status'] == 'Positive' and row['her2_status'] == 'Negative':
                        return 'Luminal (ER+/HER2-)'
                    elif row['her2_status'] == 'Positive':
                        return 'HER2-positive'
                    else:
                        return 'Triple-negative'
                
                df['molecular_subtype'] = df.apply(get_molecular_subtype, axis=1)
                
                fig_box = px.box(
                    df, x='molecular_subtype', y='risk_score',
                    title="Risk Score by Molecular Subtype"
                )
                st.plotly_chart(fig_box, use_container_width=True)
            
            # Treatment recommendations analysis
            st.markdown("#### Treatment Pattern Analysis")
            
            # Count different treatment types
            chemo_count = df['chemotherapy_recommendation'].notna().sum()
            hormone_count = df['hormonal_therapy_recommendation'].notna().sum()
            
            treatment_data = pd.DataFrame({
                'Treatment Type': ['Chemotherapy Recommended', 'Hormonal Therapy Recommended'],
                'Count': [chemo_count, hormone_count]
            })
            
            fig_treatment = px.bar(
                treatment_data, x='Treatment Type', y='Count',
                title="Treatment Recommendations Overview"
            )
            st.plotly_chart(fig_treatment, use_container_width=True)
            
        else:
            st.info("📊 Need at least 3 patients for meaningful analytics. Add more assessments to see insights.")
    
    elif page == "💾 Export Data":
        st.markdown("### 💾 Export Patient Data")
        
        df = pd.read_sql_query("SELECT * FROM patients ORDER BY assessment_date DESC", conn)
        
        if not df.empty:
            # Export options
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📄 Export Options")
                
                export_format = st.selectbox("Export Format", ["CSV", "Excel"])
                date_range = st.selectbox("Date Range", [
                    "All Records", "Last 30 Days", "Last 90 Days", "This Year"
                ])
                
                include_columns = st.multiselect("Include Columns", 
                    df.columns.tolist(), 
                    default=['uhid', 'patient_name', 'age', 'risk_score', 'risk_category', 'assessment_date'])
            
            with col2:
                st.markdown("#### 📊 Export Preview")
                
                # Apply date filter
                filtered_df = df.copy()
                if date_range != "All Records":
                    from datetime import timedelta
                    today = datetime.now().date()
                    
                    if date_range == "Last 30 Days":
                        cutoff_date = today - timedelta(days=30)
                    elif date_range == "Last 90 Days":
                        cutoff_date = today - timedelta(days=90)
                    else:  # This Year
                        cutoff_date = datetime(today.year, 1, 1).date()
                    
                    filtered_df['assessment_date'] = pd.to_datetime(filtered_df['assessment_date']).dt.date
                    filtered_df = filtered_df[filtered_df['assessment_date'] >= cutoff_date]
                
                # Select columns
                if include_columns:
                    export_df = filtered_df[include_columns]
                else:
                    export_df = filtered_df
                
                st.dataframe(export_df.head(), use_container_width=True)
                st.text(f"Total records to export: {len(export_df)}")
            
            # Generate export file
            if len(export_df) > 0:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                if export_format == "CSV":
                    csv_data = export_df.to_csv(index=False)
                    filename = f"ebc_patients_{st.session_state.doctor_id}_{timestamp}.csv"
                    
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv",
                        use_container_width=True
                    )
                
                else:  # Excel
                    from io import BytesIO
                    buffer = BytesIO()
                    
                    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                        export_df.to_excel(writer, sheet_name='EBC_Patients', index=False)
                        
                        # Add summary sheet
                        summary_data = {
                            'Metric': ['Total Patients', 'High Risk Count', 'Average Age', 'Average Risk Score'],
                            'Value': [
                                len(export_df),
                                len(export_df[export_df['risk_category'].isin(['High Risk', 'Very High Risk'])]),
                                export_df['age'].mean(),
                                export_df['risk_score'].mean()
                            ]
                        }
                        pd.DataFrame(summary_data).to_excel(writer, sheet_name='Summary', index=False)
                    
                    filename = f"ebc_patients_{st.session_state.doctor_id}_{timestamp}.xlsx"
                    
                    st.download_button(
                        label="📥 Download Excel",
                        data=buffer.getvalue(),
                        file_name=filename,
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True
                    )
            
            # Backup options
            st.markdown("---")
            st.markdown("#### 💾 Database Backup")
            
            if st.button("📦 Create Complete Backup", use_container_width=True):
                # Create a backup of the entire database
                backup_data = {
                    'doctor_info': pd.read_sql_query("SELECT * FROM doctor_info", conn).to_dict('records'),
                    'patients': df.to_dict('records'),
                    'backup_date': datetime.now().isoformat()
                }
                
                backup_json = json.dumps(backup_data, indent=2, default=str)
                backup_filename = f"ebc_backup_{st.session_state.doctor_id}_{timestamp}.json"
                
                st.download_button(
                    label="📥 Download Database Backup",
                    data=backup_json,
                    file_name=backup_filename,
                    mime="application/json"
                )
        
        else:
            st.info("📝 No data to export. Add patient assessments first.")
    
    elif page == "⚙️ Settings":
        st.markdown("### ⚙️ Account Settings")
        
        # Doctor information
        doctor_info = pd.read_sql_query("SELECT * FROM doctor_info WHERE doctor_id = ?", 
                                      conn, params=[st.session_state.doctor_id])
        
        if len(doctor_info) > 0:
            doctor = doctor_info.iloc[0]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 👤 Account Information")
                st.text(f"Doctor ID: {doctor['doctor_id']}")
                st.text(f"Name: {doctor['name']}")
                st.text(f"Hospital: {doctor['hospital_id']}")
                st.text(f"Department: {doctor['department']}")
                st.text(f"Account Created: {doctor['created_at']}")
                st.text(f"Last Login: {doctor['last_login']}")
            
            with col2:
                st.markdown("#### 📊 Usage Statistics")
                
                patient_count = pd.read_sql_query("SELECT COUNT(*) as count FROM patients", conn)['count'].iloc[0]
                
                recent_assessments = pd.read_sql_query("""
                    SELECT COUNT(*) as count FROM patients 
                    WHERE assessment_date >= date('now', '-30 days')
                """, conn)['count'].iloc[0]
                
                st.metric("Total Patients Assessed", patient_count)
                st.metric("Assessments (Last 30 Days)", recent_assessments)
                
                if patient_count > 0:
                    avg_risk = pd.read_sql_query("SELECT AVG(risk_score) as avg FROM patients", conn)['avg'].iloc[0]
                    st.metric("Average Risk Score", f"{avg_risk:.1f}")
        
        # Database management
        st.markdown("---")
        st.markdown("#### 🗃️ Database Management")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🔄 Refresh Database", use_container_width=True):
                st.success("Database refreshed successfully!")
                st.rerun()
        
        with col2:
            if st.button("📊 Rebuild Indexes", use_container_width=True):
                cursor = conn.cursor()
                cursor.execute("REINDEX")
                conn.commit()
                st.success("Database indexes rebuilt!")
        
        with col3:
            if st.button("🧹 Clean Old Data", use_container_width=True):
                # Option to clean data older than X years
                st.info("Data cleaning options would go here")
        
        # App information
        st.markdown("---")
        st.markdown("#### ℹ️ Application Information")
        
        st.markdown("""
        **EBC Risk Assessment Tool v2.0**
        
        - Evidence-based risk calculation algorithms
        - Nottingham Prognostic Index integration
        - Molecular subtype classification
        - Comprehensive treatment recommendations
        - Individual doctor databases for privacy
        - Cross-platform web accessibility
        
        **Support:** For technical issues or feature requests, contact your system administrator.
        """)
    
    conn.close()

# Main application logic
def main():
    """Main application entry point"""
    
    # Initialize session state
    if 'doctor_id' not in st.session_state:
        st.session_state.doctor_id = None
    
    # Custom CSS for original app styling
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding: 0px 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
        color: #262730;
        font-weight: 500;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
    
    .reportview-container .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Show login or main app
    if st.session_state.doctor_id is None:
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()

# =============================================================================
# DEPLOYMENT REQUIREMENTS
# =============================================================================
# Create requirements.txt with:
# streamlit>=1.28.0
# pandas>=2.0.0
# plotly>=5.0.0
# openpyxl>=3.0.0
# sqlite3 (built-in)
# hashlib (built-in)
# pathlib (built-in)
# =============================================================================