import sqlite3
import streamlit as st
import pandas as pd

# 1. डेटाबेस फ़ाइल का नाम (यह सीधे ऑनलाइन सर्वर पर ही बनेगी)
DB_FILE = "company_management.db"

# 2. डेटाबेस कनेक्शन फंक्शन (SQLite)
def get_db_connection():
    return sqlite3.connect(DB_FILE, check_same_thread=False)

# 3. टेबल बनाने का फंक्शन (अगर पहले से नहीं बनी है)
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
        st.error(f"Database error during init: {err}")

# ऐप खुलते ही सबसे पहले डेटाबेस टेबल तैयार करें
init_db()

# 4. अगला ऑटोमैटिक ID नंबर (EID-001 फॉर्मेट) ढूंढने का फंक्शन
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

# --- मुख्य लाइव वेब इंटरफ़ेस (Streamlit UI) ---
st.title("💼 Employee Management System (Online Live)")

# लाइव ऑटो-आईडी जनरेट करना
next_id = get_next_employee_id()
st.subheader(f"Assigned Employee ID: :blue[{next_id}]")

# इनपुट फॉर्म लेआउट (2 कॉलम्स में)
col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Name")
    doj = st.text_input("DOJ (DD-MM-YYYY)")
    address = st.text_area("Address", height=100)

with col2:
    contact = st.text_input("Contact")
    dob = st.text_input("DOB (DD-MM-YYYY)")
    designation = st.text_input("Designation")
    salary = st.text_input("Salary")

# बटन क्लिक होने पर डेटा सेव करना (CREATE)
if st.button("➕ Save Employee", type="primary"):
    if not name or not contact:
        st.warning("कृपया कम से कम Name और Contact जरूर भरें!")
    else:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # SQLite में %s की जगह ? का उपयोग किया गया है
            query = """INSERT INTO employees (id, name, contact, doj, dob, address, designation, salary) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
            cursor.execute(query, (next_id, name, contact, doj, dob, address, designation, salary))
            
            conn.commit()
            conn.close()
            st.success(f"कर्मचारी {name} सफलतापूर्वक जुड़ गया! (ID: {next_id})")
            st.rerun() # स्क्रीन को रिफ्रेश करने के लिए ताकि आईडी बदल सके
        except sqlite3.Error as err:
            st.error(f"डेटा सेव करने में एरर आया: {err}")

# --- डेटा दिखाने के लिए टेबल (READ) सेक्शन ---
st.markdown("---")
st.markdown("### 📋 Saved Employee Records")

try:
    conn = get_db_connection()
    # Pandas की मदद से सीधे डेटा को टेबल फॉर्मेट में लोड करना
    df = pd.read_sql_query("SELECT * FROM employees ORDER BY rowid DESC", conn)
    conn.close()
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("अभी डेटाबेस में कोई रिकॉर्ड मौजूद नहीं है।")
except Exception as e:
    st.error(f"डेटा लोड करने में समस्या आई: {e}")
