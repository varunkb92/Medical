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
            tumor_size TEXT,
            lymph_nodes_positive TEXT,
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
            avg_risk = df_stats['avg_risk'].iloc[0]
            if avg_risk is not None:
                st.metric("Avg Risk Score", f"{avg_risk:.1f}")
            
            # Risk distribution
            risk_dist = pd.read_sql_query("""
                SELECT risk_category, COUNT(*) as count 
                FROM patients 
                WHERE risk_category IS NOT NULL
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
        
        # Patient Assessment Form (Updated with new specifications)
        st.markdown("### 📋 Patient Information & Risk Assessment")
        
        # Section 1: Patient Characteristics
        st.markdown("#### 👤 Section 1: Patient Characteristics")
        col1, col2 = st.columns(2)
        
        with col1:
            uhid = st.text_input("🆔 Patient UHID", placeholder="Enter UHID")
            patient_name = st.text_input("👤 Patient Name", placeholder="Enter full name")
        
        with col2:
            age = st.number_input("🎂 Age", min_value=1, max_value=120, value=50)
            
            # Age validation
            if age < 18:
                st.warning("⚠️ Age should be 18 or above for breast cancer assessment")
            elif age > 100:
                st.warning("⚠️ Please verify age - unusually high value")
            
            menopausal_status = st.selectbox("🔄 Menopausal Status", 
                ["Premenopausal", "Postmenopausal"])
        
        st.markdown("---")
        
        # Section 2: Anatomic Risk
        st.markdown("#### 🔬 Section 2: Anatomic Risk")
        col1, col2 = st.columns(2)
        
        with col1:
            tumor_size = st.selectbox("📏 Tumour Size", 
                ["T1 (<2 cm)", "T2 (2-5 cm)", "T3 (>5 cm)"])
        
        with col2:
            nodal_status = st.selectbox("🔗 Nodal Status", 
                ["N0 (0 nodes)", "N1 (1-3 nodes)", "N2+ (>=4 nodes)"])
        
        st.markdown("---")
        
        # Section 3: Tumor Biology/Genomic
        st.markdown("#### 🧬 Section 3: Tumor Biology/Genomic")
        col1, col2 = st.columns(2)
        
        with col1:
            tumor_grade = st.selectbox("⭐ Grading", 
                ["Grade 1", "Grade 2", "Grade 3"])
            
            ki67 = st.number_input("📊 Ki-67 (%)", 
                                 min_value=0.0, max_value=100.0, value=15.0, step=0.1)
            
            # Ki67 validation
            if ki67 > 100:
                st.error("❌ Ki-67 percentage cannot exceed 100%")
            elif ki67 < 0:
                st.error("❌ Ki-67 percentage cannot be negative")
        
        with col2:
            st.markdown("**Genomic Test:**")
            genomic_test_name = st.text_input("Name of test", placeholder="e.g., Oncotype DX, MammaPrint")
            genomic_test_report = st.text_area("Report of test", 
                                             placeholder="Enter test results/report details",
                                             height=100)
        
        # Calculate button
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            calculate_button = st.button("🔬 Submit & Calculate Risk", 
                                       type="primary", 
                                       use_container_width=True)
        
        # Risk calculation and display
        if calculate_button:
            if uhid and patient_name and age >= 18 and 0 <= ki67 <= 100:
                
                # Risk calculation logic as specified
                def calculate_risk_category(nodal_status, tumor_size, tumor_grade, ki67):
                    """Calculate risk category based on exact specified logic"""
                    
                    # If Nodal Status = N2+ then output = "High Risk"
                    if "N2+" in nodal_status:
                        return "High Risk"
                    
                    # If Nodal Status = N1 then output = "High Risk"
                    elif "N1" in nodal_status:
                        return "High Risk"
                    
                    # If Nodal Status = N0
                    elif "N0" in nodal_status:
                        
                        # If Nodal Status = N0 and Tumor Size = T3 then output = "High Risk"
                        if "T3" in tumor_size:
                            return "High Risk"
                        
                        # If Nodal Status = N0 and Tumor Size = T1 then output = "Low Risk"
                        elif "T1" in tumor_size:
                            return "Low Risk"
                        
                        # If Nodal Status = N0 and Tumor Size = T2
                        elif "T2" in tumor_size:
                            
                            # If Nodal Status = N0 and Tumor Size = T2 and Grade = Grade 3 then output = "High Risk"
                            if tumor_grade == "Grade 3":
                                return "High Risk"
                            
                            # If Nodal Status = N0 and Tumor Size = T2 and Grade = Grade 1 then output = "Low Risk"
                            elif tumor_grade == "Grade 1":
                                return "Low Risk"
                            
                            # If Nodal Status = N0 and Tumor Size = T2 and Grade = Grade 2
                            elif tumor_grade == "Grade 2":
                                
                                # If Nodal Status = N0 and Tumor Size = T2 and Grade = Grade 2 and Ki-67 >= 20% then output = "High Risk"
                                if ki67 >= 20:
                                    return "High Risk"
                                
                                # If Nodal Status = N0 and Tumor Size = T2 and Grade = Grade 2 and Ki-67 < 20% then output = "Low Risk"
                                else:
                                    return "Low Risk"
                    
                    # This should not be reached with valid inputs
                    return "Unable to determine risk"
                
                # Calculate risk
                risk_category = calculate_risk_category(nodal_status, tumor_size, tumor_grade, ki67)
                
                # Display results
                st.markdown("---")
                st.markdown("## 🎯 Risk Assessment Results")
                
                # Risk category display
                if risk_category == "High Risk":
                    risk_color = "#D32F2F"  # Red
                elif risk_category == "Low Risk":
                    risk_color = "#4CAF50"  # Green
                else:
                    risk_color = "#FF9800"  # Orange
                
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    st.markdown(f"""
                    <div style="background: {risk_color}; 
                                padding: 2rem; 
                                border-radius: 15px; 
                                text-align: center;
                                box-shadow: 0 8px 25px rgba(0,0,0,0.15);">
                        <h1 style="color: white; margin: 0; font-size: 3rem;">🎯</h1>
                        <h2 style="color: white; margin: 1rem 0;">Risk Assessment Result</h2>
                        <h1 style="color: white; margin: 0; font-size: 2.5rem;">{risk_category}</h1>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Patient summary
                st.markdown("### 📋 Patient Summary")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Patient Information:**")
                    st.text(f"UHID: {uhid}")
                    st.text(f"Name: {patient_name}")
                    st.text(f"Age: {age} years")
                    st.text(f"Menopausal Status: {menopausal_status}")
                
                with col2:
                    st.markdown("**Assessment Parameters:**")
                    st.text(f"Tumour Size: {tumor_size}")
                    st.text(f"Nodal Status: {nodal_status}")
                    st.text(f"Grade: {tumor_grade}")
                    st.text(f"Ki-67: {ki67}%")
                
                # Genomic test results (if provided)
                if genomic_test_name or genomic_test_report:
                    st.markdown("### 🧬 Genomic Test Information")
                    if genomic_test_name:
                        st.text(f"Test Name: {genomic_test_name}")
                    if genomic_test_report:
                        st.text_area("Test Report:", value=genomic_test_report, height=100, disabled=True)
                
                # Save to database
                cursor = conn.cursor()
                
                # Save patient data (simplified fields)
                cursor.execute('''
                    INSERT OR REPLACE INTO patients 
                    (uhid, patient_name, age, menopausal_status, tumor_size, lymph_nodes_positive,
                     tumor_grade, ki67_percentage, assessment_date, risk_score, risk_category, 
                     treatment_recommendation, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (uhid, patient_name, age, menopausal_status, tumor_size, 
                      nodal_status, tumor_grade, ki67, datetime.now(), 
                      0,  # No numeric score in new logic
                      risk_category, 
                      f"Genomic Test: {genomic_test_name}" if genomic_test_name else "",
                      genomic_test_report if genomic_test_report else ""))
                
                conn.commit()
                
                st.success("✅ Patient assessment completed and saved successfully!")
                
            else:
                # Validation errors
                error_messages = []
                if not uhid:
                    error_messages.append("Patient UHID is required")
                if not patient_name:
                    error_messages.append("Patient Name is required")
                if age < 18:
                    error_messages.append("Age must be 18 or above")
                if not (0 <= ki67 <= 100):
                    error_messages.append("Ki-67 percentage must be between 0 and 100")
                
                for error in error_messages:
                    st.error(f"❌ {error}")
    
    elif page == "📊 Patient Database":
        st.markdown("### 📊 Patient Database & Records")
        
        # Get all patients
        df = pd.read_sql_query("""
            SELECT uhid, patient_name, age, tumor_size, lymph_nodes_positive, 
                   risk_score, risk_category, assessment_date
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
                    ["All", "Low Risk", "High Risk"])
            
            with col3:
                sort_by = st.selectbox("📋 Sort by", 
                    ["Assessment Date", "Patient Name", "Age"])
            
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
                st.dataframe(filtered_df, use_container_width=True, height=400)
                
                # Quick statistics
                st.markdown("### 📈 Database Statistics")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Total Patients", len(df))
                
                with col2:
                    high_risk_count = len(df[df['risk_category'] == 'High Risk'])
                    st.metric("High Risk Patients", high_risk_count)
                
                with col3:
                    avg_age = df['age'].mean()
                    st.metric("Average Age", f"{avg_age:.1f} years")
            
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
                        'Low Risk': '#4CAF50',
                        'High Risk': '#D32F2F'
                    }
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            
            with col2:
                st.markdown("#### Age Distribution")
                fig_hist = px.histogram(
                    df, x='age', 
                    nbins=10,
                    title="Age Distribution",
                    labels={'age': 'Age (years)', 'count': 'Number of Patients'}
                )
                fig_hist.update_traces(marker_color='#667eea')
                st.plotly_chart(fig_hist, use_container_width=True)
            
        else:
            st.info("📊 Need at least 3 patients for meaningful analytics. Add more assessments to see insights.")
    
    elif page == "💾 Export Data":
        st.markdown("### 💾 Export Patient Data")
        
        df = pd.read_sql_query("SELECT * FROM patients ORDER BY assessment_date DESC", conn)
        
        if not df.empty:
            st.markdown("#### 📄 Export Options")
            
            # Export as CSV
            csv_data = df.to_csv(index=False)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ebc_patients_{st.session_state.doctor_id}_{timestamp}.csv"
            
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                use_container_width=True
            )
            
            st.dataframe(df, use_container_width=True)
        
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
        
        # App information
        st.markdown("---")
        st.markdown("#### ℹ️ Application Information")
        
        st.markdown("""
        **EBC Risk Assessment Tool v2.0**
        
        - Evidence-based risk calculation algorithms
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
