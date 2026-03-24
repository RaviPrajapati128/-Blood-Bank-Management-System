import pandas as pd
import streamlit as st
import random
import datetime
from datetime import timedelta
import sqlite3

# ---------- DATABASE SETUP ----------
conn = sqlite3.connect("blood_bank_management_system.db", check_same_thread=False)
c = conn.cursor()

def init_db():
    """Initializes all required tables with correct schemas."""
    # 1. Users
    c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT, password TEXT)")
    
    # 2. Donors
    c.execute("""CREATE TABLE IF NOT EXISTS donors (
                DonorID INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, Age INTEGER, 
                Gender TEXT, BloodGroup TEXT, Contact TEXT, 
                DonatedDate DATE, City TEXT)""")
    
    # 3. Recipients
    c.execute("""CREATE TABLE IF NOT EXISTS recipients (
                ID INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, Age INTEGER, 
                Gender TEXT, BloodGroup TEXT, Contact TEXT, 
                RequestDate DATE, City TEXT)""")
    
    # 4. Hospitals
    c.execute("""CREATE TABLE IF NOT EXISTS hospitals (
                HospitalID INTEGER PRIMARY KEY AUTOINCREMENT, Name TEXT, 
                Location TEXT, Contact TEXT)""")
    
    # 5. Inventory
    c.execute("""CREATE TABLE IF NOT EXISTS inventory (
                UnitID INTEGER PRIMARY KEY AUTOINCREMENT, BloodGroup TEXT, 
                Quantity INTEGER, CollectionDate DATE, 
                ExpiryDate DATE, QualityStatus TEXT)""")
    
    # 6. Transactions
    c.execute("""CREATE TABLE IF NOT EXISTS transactions (
                TransactionID INTEGER PRIMARY KEY AUTOINCREMENT, RecipientID INTEGER, 
                DonorID INTEGER, BloodGroup TEXT, 
                Quantity INTEGER, Date DATE)""")
    conn.commit()

init_db()

# ---------- HELPER FUNCTIONS ----------
def add_user(u, p):
    c.execute("INSERT INTO users VALUES (?,?)", (u, p))
    conn.commit()

def login_user(u, p):
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p))
    return c.fetchone()

# ---------- UI CONFIG ----------
st.set_page_config(page_title="Vital Flow", layout="wide", page_icon="🩸")

st.markdown("""
<style>
    .stApp { background-color: #fdfdfd; }
    .stTabs [role="tablist"] { justify-content: space-evenly; }
    .stTabs [role="tab"] { flex: 1; text-align: center; font-weight: bold; font-size: 18px; }
    .main-title { text-align: center; color: #b22222; font-family: 'Trebuchet MS'; }
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "login" not in st.session_state:
    st.session_state.login = False

# ---------- LOGIN/SIGNUP PAGE ----------
if not st.session_state.login:
    st.markdown("<h1 class='main-title'>🏥 VitalFlow: Smart Blood Bank</h1>", unsafe_allow_html=True)
    tab_login, tab_signup = st.tabs(["Login", "Signup"])

    with tab_login:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            if login_user(u, p):
                st.session_state.login = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab_signup:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        if st.button("Create Account", use_container_width=True):
            if new_u and new_p:
                add_user(new_u, new_p)
                st.success("Account created! Please switch to Login tab.")
            else:
                st.warning("Please fill in both fields.")

# ---------- MAIN APP ----------
else:
    st.sidebar.success(f"👋 Logged in as: {st.session_state.user}")
    admin_mode = st.sidebar.toggle("🧑‍⚕️ Admin Dashboard")

    if st.sidebar.button("Logout", use_container_width=True):
        st.session_state.login = False
        st.rerun()

    st.markdown("<h1 class='main-title'>🩸 VitalFlow Management System</h1>", unsafe_allow_html=True)

    if admin_mode:
        t1, t2, t3, t4, t5, t6 = st.tabs(["Home", "Donors", "Requests", "Hospitals", "Inventory", "Transactions"])

        # TAB 1: HOME
        with t1:
            st.subheader("📊 Dashboard Statistics")
            c1, c2, c3 = st.columns(3)
            donors_n = pd.read_sql("SELECT COUNT(*) FROM donors", conn).iloc[0,0]
            req_n = pd.read_sql("SELECT COUNT(*) FROM recipients", conn).iloc[0,0]
            inv_n = pd.read_sql("SELECT SUM(Quantity) FROM inventory", conn).iloc[0,0] or 0
            
            c1.metric("Registered Donors", donors_n)
            c2.metric("Pending Requests", req_n)
            c3.metric("Total Stock (ml)", f"{inv_n}ml")

        # TAB 2: DONORS
        with t2:
            st.subheader("🩸 Donor Database")
            df_d = pd.read_sql("SELECT * FROM donors", conn)
            st.dataframe(df_d, use_container_width=True)
            
            with st.expander("➕ Register New Donor"):
                with st.form("donor_form"):
                    col_a, col_b = st.columns(2)
                    d_name = col_a.text_input("Full Name")
                    d_age = col_a.number_input("Age", 18, 65)
                    d_bg = col_b.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                    d_city = col_b.text_input("City")
                    d_contact = col_a.text_input("Contact Number")
                    d_gender = col_b.radio("Gender", ["Male", "Female", "Other"], horizontal=True)
                    if st.form_submit_button("Add Donor"):
                        c.execute("INSERT INTO donors (Name, Age, Gender, BloodGroup, Contact, DonatedDate, City) VALUES (?,?,?,?,?,?,?)",
                                  (d_name, d_age, d_gender, d_bg, d_contact, datetime.date.today(), d_city))
                        conn.commit()
                        st.success("Donor added successfully!")
                        st.rerun()

        # TAB 3: REQUESTS (UPDATED)
        with t3:
            st.subheader("📩 Patient Blood Requests")
            # Fetch and display the list of requests
            df_r = pd.read_sql("SELECT * FROM recipients", conn)
            if not df_r.empty:
                st.dataframe(df_r, use_container_width=True)
            else:
                st.info("No active blood requests found.")
            
            with st.expander("➕ Add New Request"):
                with st.form("req_form"):
                    r_name = st.text_input("Patient Name")
                    r_bg = st.selectbox("Required Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                    r_city = st.text_input("Hospital City")
                    if st.form_submit_button("Submit Request"):
                        c.execute("INSERT INTO recipients (Name, BloodGroup, RequestDate, City) VALUES (?,?,?,?)",
                                  (r_name, r_bg, datetime.date.today(), r_city))
                        conn.commit()
                        st.success("Request logged!")
                        st.rerun()

        # TAB 4: HOSPITALS
        with t4:
            st.subheader("🏥 Partnered Hospitals")
            df_h = pd.read_sql("SELECT * FROM hospitals", conn)
            st.dataframe(df_h, use_container_width=True)
            
            with st.expander("➕ Register Hospital"):
                with st.form("hosp_form"):
                    h_name = st.text_input("Hospital Name")
                    h_loc = st.text_input("Location/Address")
                    h_con = st.text_input("Emergency Contact")
                    if st.form_submit_button("Register Hospital"):
                        c.execute("INSERT INTO hospitals (Name, Location, Contact) VALUES (?,?,?)", (h_name, h_loc, h_con))
                        conn.commit()
                        st.rerun()

        # TAB 5: INVENTORY
        with t5:
            st.subheader("📦 Inventory Management")
            df_i = pd.read_sql("SELECT * FROM inventory", conn)
            st.dataframe(df_i, use_container_width=True)
            
            with st.expander("➕ Add Stock"):
                with st.form("stock_form"):
                    s_bg = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                    s_qty = st.number_input("Quantity (ml)", 250, 1000, step=50)
                    if st.form_submit_button("Update Inventory"):
                        exp = datetime.date.today() + timedelta(days=35)
                        c.execute("INSERT INTO inventory (BloodGroup, Quantity, CollectionDate, ExpiryDate, QualityStatus) VALUES (?,?,?,?,?)",
                                  (s_bg, s_qty, datetime.date.today(), exp, "Excellent"))
                        conn.commit()
                        st.rerun()

        # TAB 6: TRANSACTIONS
        with t6:
            st.subheader("💳 Dispatch & Transactions")
            df_t = pd.read_sql("SELECT * FROM transactions", conn)
            st.dataframe(df_t, use_container_width=True)
            
            with st.expander("📝 Record Dispatch"):
                with st.form("trans_form"):
                    t_rid = st.number_input("Recipient ID", min_value=1)
                    t_did = st.number_input("Donor ID (Optional)", min_value=0)
                    t_bg = st.selectbox("Group Dispatched", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                    t_qty = st.number_input("Amount (ml)", 100)
                    if st.form_submit_button("Log Transaction"):
                        c.execute("INSERT INTO transactions (RecipientID, DonorID, BloodGroup, Quantity, Date) VALUES (?,?,?,?,?)",
                                  (t_rid, t_did, t_bg, t_qty, datetime.date.today()))
                        conn.commit()
                        st.success("Transaction Recorded.")
                        st.rerun()

    else:
        # ---------- PUBLIC SEARCH VIEW ----------
        st.subheader("🔍 Search for Available Donors")
        c1, c2 = st.columns(2)
        s_bg = c1.selectbox("Blood Group Needed", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        s_city = c2.selectbox("Select City", ["Ahmedabad", "Gandhinagar", "Surat", "Rajkot", "Mumbai"])
        
        # Search Donors
        res_d = pd.read_sql("SELECT Name, Contact, BloodGroup, City FROM donors WHERE BloodGroup=? AND City=?", conn, params=(s_bg, s_city))
        
        # Search Inventory
        res_i = pd.read_sql("SELECT BloodGroup, Quantity, ExpiryDate FROM inventory WHERE BloodGroup=? AND QualityStatus != 'Expired'", conn, params=(s_bg,))

        col_left, col_right = st.columns(2)
        with col_left:
            st.write("### 🩸 Available Donors")
            if not res_d.empty:
                st.table(res_d)
            else:
                st.info("No individual donors found in this city.")
        
        with col_right:
            st.write("### 📦 In-House Stock")
            if not res_i.empty:
                st.table(res_i)
            else:
                st.warning("Out of stock for this blood group.")