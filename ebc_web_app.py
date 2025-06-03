# Enhanced EBC Streamlit Web App with Doctor Authentication
# This version adds multi-doctor support with individual databases
# Save as: ebc_web_app.py

import streamlit as st
import sqlite3
import pandas as pd
import hashlib
import os
from pathlib import Path
from datetime import datetime
import json

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
    
    # Create tables
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
            notes TEXT
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
    st.markdown("""
    <div style="text-align: center; padding: 2rem;">
        <h1>🏥 EBC Risk Assessment Tool</h1>
        <h3>Early Breast Cancer Risk Evaluation System</h3>
        <p>Professional medical assessment tool for oncologists</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["👨‍⚕️ Login", "📝 New Doctor Registration"])
        
        with tab1:
            st.subheader("Doctor Login")
            login_name = st.text_input("Doctor Name", placeholder="Dr. John Smith")
            login_hospital = st.text_input("Hospital ID", placeholder="HOSP123")
            login_password = st.text_input("Password", type="password")
            
            if st.button("Login", type="primary"):
                if login_name and login_hospital and login_password:
                    doctor_id = verify_doctor_login(login_name, login_hospital, login_password)
                    if doctor_id:
                        st.session_state.doctor_id = doctor_id
                        st.session_state.doctor_name = login_name
                        st.session_state.hospital_id = login_hospital
                        st.success("Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("Invalid credentials or doctor not found")
                else:
                    st.warning("Please fill in all fields")
        
        with tab2:
            st.subheader("New Doctor Registration")
            reg_name = st.text_input("Full Name", placeholder="Dr. Jane Smith")
            reg_hospital = st.text_input("Hospital/Institution ID", placeholder="AIIMS2024")
            reg_department = st.selectbox("Department", [
                "Oncology", "Surgery", "Radiology", "Pathology", 
                "Internal Medicine", "General Practice", "Other"
            ])
            reg_password = st.text_input("Create Password", type="password")
            reg_confirm = st.text_input("Confirm Password", type="password")
            
            if st.button("Create Account", type="primary"):
                if all([reg_name, reg_hospital, reg_department, reg_password, reg_confirm]):
                    if reg_password == reg_confirm:
                        if len(reg_password) >= 6:
                            doctor_id = create_doctor_profile(
                                reg_name, reg_hospital, reg_department, reg_password
                            )
                            st.success(f"Account created successfully! Doctor ID: {doctor_id}")
                            st.info("Please use the Login tab to access your account")
                        else:
                            st.error("Password must be at least 6 characters")
                    else:
                        st.error("Passwords don't match")
                else:
                    st.warning("Please fill in all fields")

def calculate_risk_score(tumor_size, nodes_positive, grade, er_status, age, ki67):
    """Enhanced risk calculation algorithm"""
    
    # Base risk score
    risk_score = 0
    
    # Tumor size factor
    if tumor_size <= 1:
        risk_score += 1
    elif tumor_size <= 2:
        risk_score += 2
    elif tumor_size <= 5:
        risk_score += 3
    else:
        risk_score += 4
    
    # Nodal involvement
    if nodes_positive == 0:
        risk_score += 0
    elif nodes_positive <= 3:
        risk_score += 3
    elif nodes_positive <= 9:
        risk_score += 5
    else:
        risk_score += 7
    
    # Tumor grade
    grade_scores = {"Grade 1": 1, "Grade 2": 2, "Grade 3": 3}
    risk_score += grade_scores.get(grade, 2)
    
    # ER status
    if er_status == "Negative":
        risk_score += 2
    
    # Age factor
    if age < 35:
        risk_score += 2
    elif age > 70:
        risk_score += 1
    
    # Ki67 factor
    if ki67 > 20:
        risk_score += 2
    elif ki67 > 14:
        risk_score += 1
    
    # Normalize to 0-100 scale
    normalized_score = min(100, (risk_score / 20) * 100)
    
    return normalized_score

def get_risk_category(score):
    """Categorize risk based on score"""
    if score < 20:
        return "Low Risk"
    elif score < 50:
        return "Intermediate Risk"
    elif score < 70:
        return "High Risk"
    else:
        return "Very High Risk"

def get_treatment_recommendation(score, er_status, her2_status):
    """Generate treatment recommendations"""
    recommendations = []
    
    if score < 20:
        recommendations.append("Consider hormone therapy if ER/PR positive")
        recommendations.append("Regular surveillance")
    elif score < 50:
        recommendations.append("Adjuvant chemotherapy consideration")
        recommendations.append("Hormone therapy if ER/PR positive")
    elif score < 70:
        recommendations.append("Adjuvant chemotherapy recommended")
        recommendations.append("Hormone therapy if ER/PR positive")
        if her2_status == "Positive":
            recommendations.append("Anti-HER2 therapy (Trastuzumab)")
    else:
        recommendations.append("Aggressive adjuvant chemotherapy")
        recommendations.append("Consider neoadjuvant therapy")
        if her2_status == "Positive":
            recommendations.append("Anti-HER2 therapy (Trastuzumab + Pertuzumab)")
    
    return "; ".join(recommendations)

def main_app():
    """Main application interface"""
    
    # Header
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #1e3a8a, #3b82f6); padding: 1rem; border-radius: 10px; margin-bottom: 2rem;">
        <h1 style="color: white; margin: 0;">🏥 EBC Risk Assessment Tool</h1>
        <p style="color: white; margin: 0;">Welcome Dr. {st.session_state.doctor_name} | {st.session_state.hospital_id}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("Navigation")
        page = st.selectbox("Select Function", [
            "New Patient Assessment",
            "View Patient Database", 
            "Analytics Dashboard",
            "Export Data",
            "Account Settings"
        ])
        
        st.markdown("---")
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Get doctor's database connection
    conn = get_doctor_database(st.session_state.doctor_id)
    
    if page == "New Patient Assessment":
        st.header("📋 New Patient Risk Assessment")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Patient Information")
            uhid = st.text_input("UHID", placeholder="Unique Hospital ID")
            patient_name = st.text_input("Patient Name")
            age = st.number_input("Age", min_value=18, max_value=100, value=50)
            menopausal_status = st.selectbox("Menopausal Status", 
                ["Pre-menopausal", "Post-menopausal", "Peri-menopausal"])
        
        with col2:
            st.subheader("Tumor Characteristics")
            tumor_size = st.number_input("Tumor Size (cm)", min_value=0.1, max_value=20.0, value=2.0, step=0.1)
            lymph_nodes = st.number_input("Positive Lymph Nodes", min_value=0, max_value=50, value=0)
            tumor_grade = st.selectbox("Tumor Grade", ["Grade 1", "Grade 2", "Grade 3"])
            histological_type = st.selectbox("Histological Type", [
                "Invasive Ductal Carcinoma", "Invasive Lobular Carcinoma", 
                "Mixed Ductal and Lobular", "Other"
            ])
        
        col3, col4 = st.columns(2)
        
        with col3:
            st.subheader("Biomarkers")
            er_status = st.selectbox("ER Status", ["Positive", "Negative"])
            pr_status = st.selectbox("PR Status", ["Positive", "Negative"])
        
        with col4:
            st.subheader("Additional Markers")
            her2_status = st.selectbox("HER2 Status", ["Positive", "Negative", "Equivocal"])
            ki67 = st.number_input("Ki67 Percentage", min_value=0.0, max_value=100.0, value=15.0, step=0.1)
        
        notes = st.text_area("Clinical Notes", placeholder="Additional observations, comorbidities, etc.")
        
        if st.button("Calculate Risk Assessment", type="primary"):
            if uhid and patient_name:
                # Calculate risk
                risk_score = calculate_risk_score(tumor_size, lymph_nodes, tumor_grade, er_status, age, ki67)
                risk_category = get_risk_category(risk_score)
                treatment_rec = get_treatment_recommendation(risk_score, er_status, her2_status)
                
                # Display results
                st.markdown("---")
                st.header("🎯 Risk Assessment Results")
                
                col_r1, col_r2, col_r3 = st.columns(3)
                
                with col_r1:
                    st.metric("Risk Score", f"{risk_score:.1f}/100")
                
                with col_r2:
                    color = {"Low Risk": "green", "Intermediate Risk": "orange", 
                            "High Risk": "red", "Very High Risk": "darkred"}[risk_category]
                    st.markdown(f"**Risk Category:** <span style='color: {color}'>{risk_category}</span>", 
                              unsafe_allow_html=True)
                
                with col_r3:
                    st.markdown(f"**Assessment Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                
                st.subheader("Treatment Recommendations")
                st.info(treatment_rec)
                
                # Save to database
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO patients 
                    (uhid, patient_name, age, menopausal_status, tumor_size, lymph_nodes_positive,
                     tumor_grade, er_status, pr_status, her2_status, ki67_percentage, 
                     histological_type, assessment_date, risk_score, risk_category, 
                     treatment_recommendation, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (uhid, patient_name, age, menopausal_status, tumor_size, lymph_nodes,
                      tumor_grade, er_status, pr_status, her2_status, ki67,
                      histological_type, datetime.now(), risk_score, risk_category,
                      treatment_rec, notes))
                
                conn.commit()
                st.success("✅ Patient assessment saved successfully!")
            
            else:
                st.error("Please provide UHID and Patient Name")
    
    elif page == "View Patient Database":
        st.header("📊 Patient Database")
        
        # Get all patients
        df = pd.read_sql_query("SELECT * FROM patients ORDER BY assessment_date DESC", conn)
        
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            st.subheader("Quick Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Patients", len(df))
            with col2:
                st.metric("High Risk Patients", len(df[df['risk_category'].isin(['High Risk', 'Very High Risk'])]))
            with col3:
                avg_age = df['age'].mean()
                st.metric("Average Age", f"{avg_age:.1f}")
            with col4:
                avg_risk = df['risk_score'].mean()
                st.metric("Average Risk Score", f"{avg_risk:.1f}")
        else:
            st.info("No patients assessed yet. Start with 'New Patient Assessment'.")
    
    elif page == "Export Data":
        st.header("📤 Export Patient Data")
        
        df = pd.read_sql_query("SELECT * FROM patients ORDER BY assessment_date DESC", conn)
        
        if not df.empty:
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"ebc_patients_{st.session_state.doctor_id}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
            
            st.subheader("Data Preview")
            st.dataframe(df.head(), use_container_width=True)
        else:
            st.info("No data to export")
    
    conn.close()

# Main application logic
def main():
    """Main application entry point"""
    
    # Initialize session state
    if 'doctor_id' not in st.session_state:
        st.session_state.doctor_id = None
    
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
# sqlite3 (built-in)
# hashlib (built-in)
# pathlib (built-in)
# =============================================================================