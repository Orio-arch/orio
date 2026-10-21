import streamlit as st
import mysql.connector
import time

# Page configuration - Website layout setup
st.set_page_config(page_title="Company Management Portal", layout="wide")

# ========================================================
# 1. YAHAN APNA MYSQL PASSWORD DALEIN
# ========================================================
db_config = {
    "host": "172.20.10.3",       # iPad se connect karne ke liye yahan apne PC ka local IP (e.g., 192.168.1.15) dalein
    "user": "root",        
    "password": "Missing@1"  # <--- Apna sahi password yahan likhein
}
# ========================================================

# Database helper functions
def get_db_connection():
    return mysql.connector.connect(
        host=db_config["host"],
        user=db_config["user"],
        password=db_config["password"],
        database="company_management"
    )

def init_db():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS company_management")
        cursor.execute("USE company_management")
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS records (
                customer_id VARCHAR(50) PRIMARY KEY,
                customer_name VARCHAR(100) NOT NULL,
                contact_number VARCHAR(20),
                address TEXT,
                designation VARCHAR(100),
                salary DECIMAL(10, 2)
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        st.error(f"Database connection failed: {err}")

def generate_next_id():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT customer_id FROM records")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        max_num = 0
        for row in rows:
            id_str = str(row[0])
            if id_str.startswith("C") and id_str[1:].isdigit():
                num = int(id_str[1:])
                if num > max_num:
                    max_num = num
        return f"C{max_num + 1:03d}"
    except:
        return "C001"

# Database initialization trigger
init_db()

# --- Session State for Secure Login ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

# ---- LOGIN SCREEN ----
if not st.session_state['logged_in']:
    st.markdown("<h2 style='text-align: center;'>🔒 Secure Login Portal</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("Login Form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Sign In")
            
            if login_btn:
                if username == "admin" and password == "12345":
                    st.session_state['logged_in'] = True
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("Invalid Credentials!")

# ---- MAIN APPLICATION WEB INTERFACE ----
else:
    # Sidebar navigation logout setup
    st.sidebar.title("Navigation")
    if st.sidebar.button("Logout 🚪"):
        st.session_state['logged_in'] = False
        st.rerun()

    st.title("💼 Company Record Management Web System")
    
    # Dynamic tabs integration
    tab1, tab2 = st.tabs(["📝 Add New Record", "🔍 Manage Records (View/Update/Delete)"])
    
    # ---- TAB 1: ADD DATA ----
    with tab1:
        st.subheader("Customer/Employee Registration Form")
        next_id = generate_next_id()
        st.info(f"Generated Next Customer ID: **{next_id}**")
        
        with st.form("Entry Form", clear_on_submit=True):
            name = st.text_input("Customer Name")
            contact = st.text_input("Contact Number")
            address = st.text_area("Address")
            designation = st.text_input("Designation")
            salary = st.text_input("Salary")
            
            submit_btn = st.form_submit_button("Save Record")
            
            if submit_btn:
                if not (name and contact and address and designation and salary):
                    st.warning("All fields are required!")
                else:
                    try:
                        salary_val = float(salary)
                        conn = get_db_connection()
                        cursor = conn.cursor()
                        query = "INSERT INTO records VALUES (%s, %s, %s, %s, %s, %s)"
                        cursor.execute(query, (next_id, name, contact, address, designation, salary_val))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        st.success(f"Record successfully saved with ID: {next_id}")
                        time.sleep(1)
                        st.rerun()
                    except ValueError:
                        st.error("Salary must be a valid number!")
                    except mysql.connector.Error as err:
                        st.error(f"MySQL Error: {err}")

    # ---- TAB 2: MANAGE DATA (READ, UPDATE, DELETE, SEARCH) ----
    with tab2:
        st.subheader("Live Database Manager Grid")
        
        # Real-time search processing filter
        search_query = st.text_input("Search entries by Name or ID:")
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            if search_query:
                query = "SELECT * FROM records WHERE customer_id LIKE %s OR customer_name LIKE %s"
                cursor.execute(query, (f"%{search_query}%", f"%{search_query}%"))
            else:
                cursor.execute("SELECT * FROM records")
            
            records = cursor.fetchall()
            cursor.close()
            conn.close()
            
            if records:
                # Displays interactive dynamic web tables overview
                st.dataframe(records, use_container_width=True)
                
                st.markdown("---")
                st.subheader("Modify Record Operations")
                
                # Selection structure mapping
                record_ids = [r['customer_id'] for r in records]
                selected_id = st.selectbox("Select Customer ID to Update or Delete:", ["-- Select --"] + record_ids)
                
                if selected_id != "-- Select --":
                    # Fetching properties details for the selected object data matrix
                    selected_record = next(r for r in records if r['customer_id'] == selected_id)
                    
                    with st.form("Update Form"):
                        st.text(f"Modifying ID: {selected_id}")
                        u_name = st.text_input("Customer Name", value=selected_record['customer_name'])
                        u_contact = st.text_input("Contact Number", value=selected_record['contact_number'])
                        u_address = st.text_area("Address", value=selected_record['address'])
                        u_designation = st.text_input("Designation", value=selected_record['designation'])
                        u_salary = st.text_input("Salary", value=str(selected_record['salary']))
                        
                        col_up, col_del = st.columns(2)
                        with col_up:
                            up_btn = st.form_submit_button("Update Data ✏️")
                        with col_del:
                            del_btn = st.form_submit_button("Delete Record 🗑️")
                            
                        if up_btn:
                            try:
                                salary_val = float(u_salary)
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                query = """UPDATE records SET customer_name=%s, contact_number=%s, 
                                           address=%s, designation=%s, salary=%s WHERE customer_id=%s"""
                                cursor.execute(query, (u_name, u_contact, u_address, u_designation, salary_val, selected_id))
                                conn.commit()
                                cursor.close()
                                conn.close()
                                st.success("Record updated successfully!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Update failed: {e}")
                                
                        if del_btn:
                            try:
                                conn = get_db_connection()
                                cursor = conn.cursor()
                                cursor.execute("DELETE FROM records WHERE customer_id=%s", (selected_id,))
                                conn.commit()
                                cursor.close()
                                conn.close()
                                st.success("Record deleted successfully!")
                                time.sleep(1)
                                st.rerun()
                            except Exception as e:
                                st.error(f"Deletion failed: {e}")
            else:
                st.info("No records found in database matrix data grids.")
        except Exception as e:
            st.error(f"Error connecting grid layout components: {e}")
