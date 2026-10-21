import sqlite3
import streamlit as st
import pandas as pd

# Set professional layout and page styling
st.set_page_config(page_title="EMS Portal", page_icon="💼", layout="wide")

# 1. Database Configuration
DB_FILE = "company_management.db"

def get_db_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

def init_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id TEXT PRIMARY KEY,
            name TEXT,
            contact TEXT,
            doj TEXT,
            dob TEXT,
            address TEXT,
            designation TEXT,
            salary TEXT
        )
        """)
        conn.commit()
        conn.close()
    except sqlite3.Error as err:
        st.error(f"Database error during initialization: {err}")

init_db()

# 2. Next Employee ID Generator
def get_next_employee_id():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM employees ORDER BY rowid DESC LIMIT 1")
        last_id_row = cursor.fetchone()
        conn.close()
        
        if last_id_row:
            last_id = last_id_row[0]
            try:
                last_number = int(last_id.replace("EID-", ""))
                next_number = last_number + 1
            except Exception:
                next_number = 1
        else:
            next_number = 1
            
        return f"EID-{next_number:03d}"
    except sqlite3.Error:
        return "EID-001"

# --- LOGIN SECURITY GATE ---
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    # Colorful Title Banner for Login Room
    st.markdown("""
        <div style="background-color:#6C5CE7;padding:20px;border-radius:10px;margin-bottom:25px;text-align:center;">
            <h1 style="color:white;font-family:'Segoe UI',Arial,sans-serif;margin:0;">🔒 SECURE EMS PORTAL</h1>
            <p style="color:#DFE6E9;margin:5px 0 0 0;">Please authorize your credentials to manage records</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Centered Login Card
    login_col, _ = st.columns([1, 2])
    with login_col:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter admin username")
            password = st.text_input("Password", type="password", placeholder="Enter admin password")
            submit_login = st.form_submit_button("Secure Login")
            
            if submit_login:
                # Set your secure administrative login details here
                if username == "admin" and password == "Missing@1":
                    st.session_state["authenticated"] = True
                    st.success("Access Granted! Loading system dashboard...")
                    st.rerun()
                else:
                    st.error("Invalid credentials! Please try again.")
    st.stop()  # Stop executing the rest of the application until logged in

# --- MAIN DASHBOARD INTERFACE (Shown Only After Login) ---
# Logout Button on Top Right Corner
top_col1, top_col2 = st.columns([9, 1])
with top_col2:
    if st.button("Log Out 🔓", type="secondary"):
        st.session_state["authenticated"] = False
        st.rerun()

# Vivid Modern Dashboard Header Banner
st.markdown("""
    <div style="background-image: linear-gradient(135deg, #00CEC9 0%, #6C5CE7 100%); padding:25px; border-radius:12px; margin-bottom:30px;">
        <h1 style="color:white; font-family:'Segoe UI',Arial,sans-serif; margin:0; font-size:32px;">💼 CORPORATE EMPLOYEE REGISTRY</h1>
        <p style="color:#F5F6FA; margin:6px 0 0 0; font-size:16px;">Advanced Real-time Cloud Management Terminal</p>
    </div>
""", unsafe_allow_html=True)

# Fetch IDs for select boxes
try:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM employees")
    all_ids = [row[0] for row in cursor.fetchall()]
    conn.close()
except sqlite3.Error:
    all_ids = []

# Dynamic Metrics Cards Row
col_m1, col_m2, col_m3 = st.columns(3)
with col_m1:
    st.metric(label="Total Registered Workforce", value=len(all_ids), delta="Active Employees")
with col_m2:
    st.metric(label="Database Status", value="ONLINE", delta="SQLite3 Cloud Layer", delta_color="normal")
with col_m3:
    st.metric(label="Security Level", value="ENHANCED", delta="Session Locked")

# Modern Colorful Operations Interface via Tabs
tab1, tab2, tab3 = st.tabs(["✨ Add Employee Profile", "⚙️ Modify Staff Record", "🗑️ Remove Employee Profile"])

# --- 1. CREATE OPERATION ---
with tab1:
    next_id = get_next_employee_id()
    st.markdown(f"#### Assigning Automated System Index: :b[<span style='color:#6C5CE7; font-size:24px;'>{next_id}</span>]", unsafe_allow_html=True)
    
    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", placeholder="e.g. John Doe", key="add_name")
            doj = st.text_input("Date of Joining", placeholder="DD-MM-YYYY", key="add_doj")
            address = st.text_area("Permanent Residential Address", placeholder="Street, City, State", height=90, key="add_address")
        with col2:
            contact = st.text_input("Mobile Contact Number", placeholder="e.g. +91 9876543210", key="add_contact")
            dob = st.text_input("Date of Birth", placeholder="DD-MM-YYYY", key="add_dob")
            designation = st.text_input("Corporate Designation", placeholder="e.g. Software Engineer", key="add_designation")
            salary = st.text_input("Allocated Salary (Monthly CTC)", placeholder="e.g. 75000", key="add_salary")
            
        if st.button("🚀 Commit Record to Server", type="primary", key="save_btn"):
            if not name or not contact:
                st.warning("Action Rejected: 'Full Name' and 'Mobile Contact Number' fields are mandatory!")
            else:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    query = "INSERT INTO employees VALUES (?, ?, ?, ?, ?, ?, ?, ?)"
                    cursor.execute(query, (next_id, name, contact, doj, dob, address, designation, salary))
                    conn.commit()
                    conn.close()
                    st.balloons()
                    st.success(f"Transaction successful! Added {name} under tracking reference: {next_id}")
                    st.rerun()
                except sqlite3.Error as err:
                    st.error(f"SQL Storage Layer Failure: {err}")

# --- 2. UPDATE OPERATION ---
with tab2:
    st.markdown("#### 📝 Edit Personnel Configurations")
    if all_ids:
        selected_id = st.selectbox("Choose System Target ID to Alter", all_ids, key="update_select")
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM employees WHERE id=?", (selected_id,))
            emp_data = cursor.fetchone()
            conn.close()
            
            if emp_data:
                with st.container(border=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        u_name = st.text_input("Modify Full Name", value=emp_data[1], key="u_name")
                        u_doj = st.text_input("Modify Date of Joining", value=emp_data[3], key="u_doj")
                        u_address = st.text_area("Modify Residential Address", value=emp_data[5], height=90, key="u_address")
                    with col2:
                        u_contact = st.text_input("Modify Contact Number", value=emp_data[2], key="u_contact")
                        u_dob = st.text_input("Modify Date of Birth", value=emp_data[4], key="u_dob")
                        u_designation = st.text_input("Modify Designation", value=emp_data[6], key="u_designation")
                        u_salary = st.text_input("Modify Salary", value=emp_data[7], key="u_salary")
                    
                    if st.button("💾 Apply Modifications", type="primary", key="update_btn"):
                        try:
                            conn = get_db_connection()
                            cursor = conn.cursor()
                            cursor.execute("""
                            UPDATE employees SET name=?, contact=?, doj=?, dob=?, address=?, designation=?, salary=? 
                            WHERE id=?
                            """, (u_name, u_contact, u_doj, u_dob, u_address, u_designation, u_salary, selected_id))
                            conn.commit()
                            conn.close()
                            st.success(f"System Matrix Updated! Profile reference index {selected_id} is now modified.")
                            st.rerun()
                        except sqlite3.Error as err:
                            st.error(f"Write Transaction Failed: {err}")
        except sqlite3.Error as err:
            st.error(f"Database Fetch Interrupted: {err}")
    else:
        st.info("System Notification: No data assets currently populated to enable modification rules.")

# --- 3. DELETE OPERATION ---
with tab3:
    st.markdown("#### 🚨 Dangerous Action Area")
    if all_ids:
        delete_id = st.selectbox("Choose System Target ID to Purge", all_ids, key="delete_select")
        
        st.markdown(f"<span style='color:#D63031; font-weight:bold;'>Warning:</span> This will permanently erase the database reference index for **{delete_id}**.", unsafe_allow_html=True)
        if st.button("🗑️ Purge Record Permanently", type="secondary", key="delete_btn"):
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM employees WHERE id=?", (delete_id,))
                conn.commit()
conn.close()
st.toast(f"Purged ID {delete_id} successfully!")
st.success(f"Data Purge complete. System reference index {delete_id} dropped from global catalog.")
st.rerun()
except sqlite3.Error as err:
st.error(f"Purge Execution Aborted: {err}")
else:
st.info("System Notification: Catalog is completely empty. Clear of any historical target files to execute purge.")

--- 4. VIEW LOG TRANSACTION LAYER (LIVE DATAFRAME VIEW) ---

st.markdown("

", unsafe_allow_html=True)
st.markdown("""

📋 CENTRAL INTELLIGENCE CATALOG (LIVE RECORD REGISTRY)

""", unsafe_allow_html=True)
try:
conn = get_db_connection()
df = pd.read_sql_query("SELECT * FROM employees ORDER BY rowid DESC", conn)
conn.close()
if not df.empty:
# Beautifully formatted responsive live dynamic data table wrapper
st.dataframe(df.style.set_properties(**{
'background-color': '#FFFFFF',
'border-color': '#DFE6E9',
'color': '#2D3436'
}), use_container_width=True)
else:
st.warning("Empty Matrix Notice: Global data warehouse holds zero values. Please execute staff entry steps above to initialize registry streams.")
except Exception as e:
st.error(f"Catalog Render Engine Failure: {e}")