import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import hashlib
import os

# Page configuration
st.set_page_config(
    page_title="BMI Calculator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database setup
def init_db():
    """Initialize the SQLite database with users and patients tables"""
    conn = sqlite3.connect('bmi_records.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            email TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Modified patients table with user_id
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            gender TEXT NOT NULL,
            age INTEGER NOT NULL,
            height REAL NOT NULL,
            weight REAL NOT NULL,
            bmi REAL NOT NULL,
            bmi_category TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, email=None):
    """Create a new user"""
    conn = sqlite3.connect('bmi_records.db')
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, email)
            VALUES (?, ?, ?)
        ''', (username, hash_password(password), email))
        conn.commit()
        conn.close()
        return True, "User created successfully!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Username already exists!"
    except Exception as e:
        conn.close()
        return False, f"Error: {str(e)}"

def verify_user(username, password):
    """Verify user credentials"""
    conn = sqlite3.connect('bmi_records.db')
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, password_hash FROM users WHERE username = ?
    ''', (username,))
    result = cursor.fetchone()
    conn.close()
    
    if result and result[1] == hash_password(password):
        return True, result[0]  # Return True and user_id
    return False, None

def calculate_bmi(weight, height):
    """Calculate BMI and return BMI value and category"""
    bmi = weight / (height ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
        color = "blue"
    elif 18.5 <= bmi < 25:
        category = "Normal weight"
        color = "green"
    elif 25 <= bmi < 30:
        category = "Overweight"
        color = "orange"
    else:
        category = "Obese"
        color = "red"
    
    return round(bmi, 2), category, color

def save_to_database(user_id, name, gender, age, height, weight, bmi, category):
    """Save patient data to database with user association"""
    conn = sqlite3.connect('bmi_records.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO patients (user_id, name, gender, age, height, weight, bmi, bmi_category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, name, gender, age, height, weight, bmi, category))
    conn.commit()
    conn.close()

def get_user_records(user_id):
    """Retrieve records for a specific user"""
    conn = sqlite3.connect('bmi_records.db')
    df = pd.read_sql_query('''
        SELECT id, name, gender, age, height, weight, bmi, bmi_category, created_at
        FROM patients 
        WHERE user_id = ?
        ORDER BY created_at DESC
    ''', conn, params=(user_id,))
    conn.close()
    return df

def login_page():
    """Display login/registration page"""
    st.title("🏥 BMI Calculator - Login")
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔐 Login")
        login_username = st.text_input("Username", key="login_username")
        login_password = st.text_input("Password", type="password", key="login_password")
        
        if st.button("Login", type="primary", use_container_width=True):
            if login_username and login_password:
                success, user_id = verify_user(login_username, login_password)
                if success:
                    st.session_state.logged_in = True
                    st.session_state.username = login_username
                    st.session_state.user_id = user_id
                    st.success("✅ Login successful!")
                    st.rerun()
                else:
                    st.error("❌ Invalid username or password")
            else:
                st.error("❌ Please enter both username and password")
    
    with col2:
        st.subheader("📝 Register New User")
        reg_username = st.text_input("Choose Username", key="reg_username")
        reg_email = st.text_input("Email (optional)", key="reg_email")
        reg_password = st.text_input("Choose Password", type="password", key="reg_password")
        reg_password_confirm = st.text_input("Confirm Password", type="password", key="reg_password_confirm")
        
        if st.button("Register", type="secondary", use_container_width=True):
            if not reg_username or not reg_password:
                st.error("❌ Username and password are required")
            elif reg_password != reg_password_confirm:
                st.error("❌ Passwords do not match")
            elif len(reg_password) < 6:
                st.error("❌ Password must be at least 6 characters long")
            else:
                success, message = create_user(reg_username, reg_password, reg_email)
                if success:
                    st.success(f"✅ {message} Please login with your credentials.")
                else:
                    st.error(f"❌ {message}")

def main():
    # Initialize database
    init_db()
    
    # Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    # Check if user is logged in
    if not st.session_state.logged_in:
        login_page()
    else:
        # Sidebar for navigation and user info
        st.sidebar.title("🏥 BMI Calculator")
        st.sidebar.success(f"👤 Logged in as: {st.session_state.username}")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_id = None
            st.rerun()
        
        st.sidebar.markdown("---")
        page = st.sidebar.selectbox("Choose a page:", ["Calculate BMI", "My Records", "BMI Information"])
        
        if page == "Calculate BMI":
            calculate_page()
        elif page == "My Records":
            records_page()
        else:
            info_page()

def calculate_page():
    st.title("⚖️ BMI Calculator")
    st.markdown(f"Welcome, **{st.session_state.username}**! 👋")
    st.markdown("---")
    
    # Create two columns for better layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Patient Information")
        
        # Input fields
        name = st.text_input("Patient Name", placeholder="Enter patient's full name")
        
        gender = st.selectbox("Gender", ["Select Gender", "Male", "Female", "Other"])
        
        col_age, col_height = st.columns(2)
        with col_age:
            age = st.number_input("Age (years)", min_value=1, max_value=150, value=25)
        
        with col_height:
            height = st.number_input("Height (meters)", min_value=0.5, max_value=3.0, value=1.70, step=0.01, format="%.2f")
        
        weight = st.number_input("Weight (kg)", min_value=1.0, max_value=500.0, value=70.0, step=0.1, format="%.1f")
        
        st.markdown("---")
        
        # Action buttons
        st.subheader("Choose Action")
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            calculate_only = st.button("🧮 Calculate BMI Only", type="secondary", use_container_width=True)
        
        with col_btn2:
            calculate_and_save = st.button("💾 Calculate BMI & Save to My Records", type="primary", use_container_width=True)
    
    with col2:
        st.subheader("BMI Categories")
        st.markdown("""
        <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px;">
        <p><span style="color: blue;">🔵 Underweight:</span> BMI < 18.5</p>
        <p><span style="color: green;">🟢 Normal weight:</span> BMI 18.5-24.9</p>
        <p><span style="color: orange;">🟠 Overweight:</span> BMI 25-29.9</p>
        <p><span style="color: red;">🔴 Obese:</span> BMI ≥ 30</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Process calculations
    if calculate_only or calculate_and_save:
        # Validation
        if not name or name.strip() == "":
            st.error("❌ Please enter the patient's name")
            return
        
        if gender == "Select Gender":
            st.error("❌ Please select a gender")
            return
        
        if height <= 0 or weight <= 0:
            st.error("❌ Please enter valid positive values for height and weight")
            return
        
        # Calculate BMI
        bmi, category, color = calculate_bmi(weight, height)
        
        # Display results
        st.markdown("---")
        st.subheader("📊 BMI Results")
        
        # Create result display
        result_col1, result_col2, result_col3 = st.columns(3)
        
        with result_col1:
            st.metric("BMI Value", f"{bmi}", help="Body Mass Index")
        
        with result_col2:
            st.metric("Category", category)
        
        with result_col3:
            if color == "green":
                st.success(f"✅ {category}")
            elif color == "blue":
                st.info(f"ℹ️ {category}")
            elif color == "orange":
                st.warning(f"⚠️ {category}")
            else:
                st.error(f"⚠️ {category}")
        
        # Patient summary
        st.subheader("👤 Patient Summary")
        summary_data = {
            "Attribute": ["Name", "Gender", "Age", "Height", "Weight", "BMI", "Category"],
            "Value": [name, gender, f"{age} years", f"{height} m", f"{weight} kg", f"{bmi}", category]
        }
        summary_df = pd.DataFrame(summary_data)
        st.table(summary_df)
        
        # Save to database if requested
        if calculate_and_save:
            try:
                save_to_database(st.session_state.user_id, name, gender, age, height, weight, bmi, category)
                st.success("✅ BMI calculated and data saved to your records successfully!")
                st.balloons()
            except Exception as e:
                st.error(f"❌ Error saving to database: {str(e)}")
        else:
            st.info("ℹ️ BMI calculated successfully! (Data not saved to your records)")

def records_page():
    st.title("📋 My BMI Records")
    st.markdown(f"Records for: **{st.session_state.username}**")
    st.markdown("---")
    
    try:
        df = get_user_records(st.session_state.user_id)
        
        if df.empty:
            st.info("📝 You have no BMI records yet.")
            st.markdown("Add some records using the BMI Calculator!")
        else:
            # Display statistics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Records", len(df))
            
            with col2:
                avg_bmi = df['bmi'].mean()
                st.metric("Average BMI", f"{avg_bmi:.1f}")
            
            with col3:
                normal_count = len(df[df['bmi_category'] == 'Normal weight'])
                st.metric("Normal Weight", normal_count)
            
            with col4:
                latest_date = df['created_at'].iloc[0].split()[0] if not df.empty else "N/A"
                st.metric("Latest Record", latest_date)
            
            st.markdown("---")
            
            # Search and filter options
            st.subheader("🔍 Search & Filter")
            col_search, col_filter = st.columns(2)
            
            with col_search:
                search_name = st.text_input("Search by name", placeholder="Enter patient name...")
            
            with col_filter:
                filter_category = st.selectbox("Filter by BMI category", 
                                             ["All Categories"] + list(df['bmi_category'].unique()))
            
            # Apply filters
            filtered_df = df.copy()
            
            if search_name:
                filtered_df = filtered_df[filtered_df['name'].str.contains(search_name, case=False, na=False)]
            
            if filter_category != "All Categories":
                filtered_df = filtered_df[filtered_df['bmi_category'] == filter_category]
            
            # Display filtered results
            st.subheader(f"📊 Your Records ({len(filtered_df)} of {len(df)})")
            
            if not filtered_df.empty:
                # Rename columns for better display
                display_df = filtered_df.copy()
                display_df.columns = ['ID', 'Name', 'Gender', 'Age', 'Height (m)', 'Weight (kg)', 'BMI', 'Category', 'Date Added']
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "BMI": st.column_config.NumberColumn(
                            "BMI",
                            format="%.1f"
                        ),
                        "Category": st.column_config.TextColumn(
                            "Category",
                        )
                    }
                )
                
                # Download option
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📥 Download My Records as CSV",
                    data=csv,
                    file_name=f"my_bmi_records_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.warning("No records match your search criteria.")
    
    except Exception as e:
        st.error(f"❌ Error loading records: {str(e)}")

def info_page():
    st.title("📚 BMI Information")
    st.markdown("---")
    
    # BMI explanation
    st.subheader("What is BMI?")
    st.markdown("""
    **Body Mass Index (BMI)** is a measure of body fat based on height and weight. 
    It's calculated using the formula:
    """)
    
    st.latex(r"BMI = \frac{Weight (kg)}{Height (m)^2}")
    
    # BMI categories
    st.subheader("BMI Categories")
    
    categories_data = {
        "Category": ["Underweight", "Normal weight", "Overweight", "Obese"],
        "BMI Range": ["< 18.5", "18.5 - 24.9", "25.0 - 29.9", "≥ 30.0"],
        "Health Risk": ["Malnutrition risk", "Low risk", "Moderate risk", "High risk"],
        "Color Code": ["🔵 Blue", "🟢 Green", "🟠 Orange", "🔴 Red"]
    }
    
    categories_df = pd.DataFrame(categories_data)
    st.table(categories_df)
    
    # Important notes
    st.subheader("⚠️ Important Notes")
    st.markdown("""
    - BMI is a screening tool, not a diagnostic tool
    - It doesn't directly measure body fat percentage
    - May not be accurate for athletes with high muscle mass
    - Age, sex, and ethnicity can affect BMI interpretation
    - Always consult healthcare professionals for health assessments
    """)
    
    # Health tips
    st.subheader("💡 Health Tips")
    st.markdown("""
    **For maintaining a healthy BMI:**
    - Eat a balanced diet with plenty of fruits and vegetables
    - Exercise regularly (at least 150 minutes of moderate activity per week)
    - Stay hydrated
    - Get adequate sleep (7-9 hours per night)
    - Manage stress levels
    - Regular health check-ups
    """)

if __name__ == "__main__":
    main()
