import mysql.connector
import pandas as pd
from sqlalchemy import create_engine
import streamlit as st
import random
import datetime
from datetime import timedelta
import re
import sqlite3

# ---------- DATABASE ----------
conn = sqlite3.connect("bloodbank.db", check_same_thread=False)
c = conn.cursor()
# User accounts
c.execute("CREATE TABLE IF NOT EXISTS users(username TEXT,password TEXT)")

# Blood inventory
# ---------- FUNCTIONS ----------
def add_user(u,p):
    c.execute("INSERT INTO users VALUES (?,?)",(u,p))
    conn.commit()

def login_user(u,p):
    c.execute("SELECT * FROM users WHERE username=? AND password=?",(u,p))
    return c.fetchone()

# ---------- PAGE ----------
st.set_page_config(page_title="Vital Flow", layout="wide")

# ---------- UI ----------
st.markdown("""
<style>
.main {
    background: linear-gradient(135deg,#800000,#b22222,#dc143c);
    color:white;
}
.card {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(15px);
    padding:20px;
    border-radius:20px;
    margin-bottom:20px;
}
.title {
    font-size:40px;
    text-align:center;
    font-weight:bold;
    background: linear-gradient(90deg,#ff512f,#dd2476);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION ----------
if "login" not in st.session_state:
    st.session_state.login=False

# ---------- LOGIN ----------
if not st.session_state.login:

    st.markdown(
            """
            <h1 style='text-align: center; color: #b22222; font-family: "Trebuchet MS", sans-serif;'>
                🏥 VitalFlow: Smart Blood Bank Manager
            </h1>
            <h6 style='text-align: center; color: #444444; font-family: "Trebuchet MS", sans-serif;'>
                A streamlined system for donor and inventory management
            </h6>
            """,
            unsafe_allow_html=True
        )
    tab1,tab2 = st.tabs(["Login","Signup"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if login_user(u,p):
                st.session_state.login=True
                st.session_state.user=u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        u = st.text_input("New Username")
        p = st.text_input("New Password", type="password")

        if st.button("Create"):
            add_user(u,p)
            st.success("Account created")
            
else:
    st.sidebar.success(f"👋 {st.session_state.user}")
    admin_mode = st.sidebar.toggle("🧑‍⚕️ Admin Dashboard")

    if st.sidebar.button("Logout",use_container_width=True):
        st.session_state.login=False
        st.rerun()

    # Admin dashboard: manage inventory
    if admin_mode:
        
        st.markdown(
            """
            <h1 style='text-align: center; color: #b22222; font-family: "Trebuchet MS", sans-serif;'>
                🏥 VitalFlow: Smart Blood Bank Manager
            </h1>
            <h6 style='text-align: center; color: #444444; font-family: "Trebuchet MS", sans-serif;'>
                A streamlined system for donor and inventory management
            </h6>
            """,
            unsafe_allow_html=True
        )
        
        conn = mysql.connector.connect(
            host="localhost",
            user="root",   
            password="kr$na128",
            database="blood_bank_management_system"
        )
        cur =conn.cursor()
        engine = create_engine("mysql+mysqlconnector://root:kr$na128@localhost/blood_bank_management_system")
        
        st.markdown(
            """
            <style>
            /* Target the tab container */
            .stTabs [role="tablist"] {
                justify-content: space-evenly;
            }
            /* Make each tab take equal width */
            .stTabs [role="tab"] {
                flex: 1;
                text-align: center;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        
        tab1,tab2,tab3,tab4,tab5,tab6 = st.tabs(["Home","Donors","Requests","Hospitals","Inventory","Transactions"])   
        
        with tab2:
        
            st.subheader("🩸 Donors info")
            
            query = "SELECT * FROM donors order by DonatedDate"
            df = pd.read_sql(query, engine)
            st.dataframe(df)
            
            with st.expander("Add Donor"):
                with st.form("add_donor_form"):
                    ID = random.randint(100, 999)
                    Name = st.text_input("Enter Name:")
                    Age = st.number_input("Enter age:", min_value=18, max_value=50)
                    Gender = st.selectbox("Sex:", ["Male", "Female", "Others"])
                    blood_group = st.selectbox("Select Blood Group:", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                    Contact = st.text_input("Enter Contact no:")   
                    City = st.text_input("Enter City:")
                    DonatedDate = st.date_input("Collection Date:", datetime.date.today())  
                    
                    submit = st.form_submit_button("Add Donor", use_container_width=True)
             
                    if submit:
                        data = [(ID, Name, Age, Gender, blood_group, Contact,DonatedDate,City)]
                        df_new = pd.DataFrame(data,columns=['DonorID', 'Name', 'Age', 'Gender','BloodGroup','Contact','DonatedDate','City'])
                        st.write("New donor added:")
                        st.dataframe(df_new)
            
                        df_new.to_sql("donors", engine, if_exists="append", index=False)
                        st.success("Donor successfully added!")

            col1 , col2, col3 = st.columns(3)
            with col1:
                if st.button("Clear Donors",use_container_width=True):
                    cur.execute("Truncate table Donors")
                            
        with tab3:
        
            st.subheader("📩 Requests")
            
            query = "SELECT * FROM recipents ORDER BY RequestDate"
            df = pd.read_sql(query, engine)
            st.dataframe(df)
        
        
            with st.expander("Add Request"):
                with st.form("add_recipient_form"):
                    ID = random.randint(100, 999)
                    Name = st.text_input("Enter Name:")
                    Age = st.number_input("Enter age:", min_value=1, max_value=100)
                    Gender = st.selectbox("Sex:", ["Male", "Female", "Others"])
                    BloodGroup = st.selectbox("Select Blood Group:", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                    Contact = st.text_input("Enter Contact no:")
                    City = st.text_input("Enter City:")
                    CollectedDate = st.date_input("Collection Date:", datetime.date.today())  
            
                    submit = st.form_submit_button("Add Recipient", use_container_width=True)
            
                    if submit:
                        data = [(ID,Name, Age, Gender, BloodGroup, Contact, CollectedDate, City)]
                        df_new = pd.DataFrame(data,columns=['ID','Name', 'Age', 'Gender', 'BloodGroup', 'Contact', 'RequestDate', 'City'])
            
                        st.write("New recipient added:")
                        st.dataframe(df_new)
            
                        df_new.to_sql("recipents", engine, if_exists="append", index=False)
                        st.success("Recipient successfully added!")
                        
            col1 , col2, col3 = st.columns(3)
            with col1:
                if st.button("Clear Requests",use_container_width=True):
                    cur.execute("Truncate table recipents")
                
        with tab1:
            st.subheader("🏠 Home")
            
            st.write("Requests")
            query = "SELECT * FROM recipents ORDER BY RequestDate LIMIT 5"
            df = pd.read_sql(query, engine)
            st.dataframe(df)
        
            st.divider()
            
            st.subheader("🔍 Search")
            B = st.selectbox("Select Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
            c = st.selectbox("Select City",["Ahmedabad", "Gandhinagar", "Surat", "Rajkot"])
            q = "Select * From donors order by DonatedDate"
            d = pd.read_sql(q,engine)
        
            st.write("Donors")
            st.dataframe(d[(d["BloodGroup"]==B) & (d["City"]==c)])
        
            q2 = "SELECT * FROM inventory ORDER BY CollectionDate DESC"
            d2 = pd.read_sql(q2, engine)
        
            st.write("Available in Inventory")
            st.dataframe(d2[d2["Blood Group"]==B])
        
        with tab4:
            st.subheader("🏥 Hospitals")
        
            query = "SELECT * FROM hospitals ORDER BY HospitalID"
            df = pd.read_sql(query, engine)
            st.dataframe(df)
        
            with st.expander("Add Hospital"):
                with st.form("add_hospital_form"):
                    HospitalID = random.randint(100, 999)  
                    Name = st.text_input("Enter Hospital Name:")
                    Location = st.text_input("Enter Location:")
                    Contact = st.text_input("Enter Contact No:")
            
                    submit = st.form_submit_button("Add Hospital", use_container_width=True)
            
                    if submit:
                        data = [(HospitalID, Name, Location, Contact)]
                        df_new = pd.DataFrame(
                            data,
                            columns=['HospitalID', 'Name', 'Location', 'Contact']
                        )
            
                        st.write("New hospital added:")
                        st.dataframe(df_new)
            
                        df_new.to_sql("hospitals", engine, if_exists="append", index=False)
                        st.success("Hospital successfully added!")

            col1 , col2, col3 = st.columns(3)
            with col1:
                if st.button("Remove Hospitals",use_container_width=True):
                    cur.execute("Truncate table hospital")
                    
        with tab5:
            st.subheader("📦 Inventory")
        
            query = "SELECT * FROM inventory ORDER BY CollectionDate DESC"
            df = pd.read_sql(query, engine)
            st.dataframe(df)
            
            with st.expander("Add Inventory Record"):
                with st.form("add_inventory_form"):
                    UnitID = random.randint(1000, 9999)  # PK
                    BloodGroup = st.selectbox("Select Blood Group:", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                    Quantity = st.number_input("Enter Quantity (ml):", min_value=1)
                    CollectionDate = st.date_input("Collection Date:", datetime.date.today())
                    ExpiryDate = CollectionDate + timedelta(30)
                    days_remaining = (ExpiryDate - datetime.date.today()).days
        
                    if days_remaining > 20:
                        QualityStatus = "Good"
                    elif 10 < days_remaining <= 20:
                        QualityStatus = "Average"
                    elif 0 < days_remaining <= 10:
                        QualityStatus = "Poor"
                    else:
                        QualityStatus = "Expired"
                        
                    submit = st.form_submit_button("Add Record", use_container_width=True)
            
                    if submit:
                        data = [(UnitID, BloodGroup, Quantity, CollectionDate, ExpiryDate, QualityStatus)]
                        df_new = pd.DataFrame(
                            data,
                            columns=['UnitID', 'Blood Group', 'Quantity', 'CollectionDate', 'ExpiryDate', 'QualityStatus'])
            
                        st.write("New inventory record added:")
                        st.dataframe(df_new)
            
                        df_new.to_sql("inventory", engine, if_exists="append", index=False)
               
                        st.success("Inventory record successfully added!")
                        
            col1 , col2, col3 = st.columns(3)
            with col1:
                if st.button("Clear  Inventory",use_container_width=True):
                    cur.execute("Truncate table inventory")
            
                
        with tab6:
            
            st.subheader("💳 Transactions")
            
            query = "SELECT * FROM transactions"
            df = pd.read_sql(query, engine)
            st.dataframe(df)
            
            with st.expander("Add Transaction Record"):
                with st.form("add_transaction_form"):
                    TransactionID = random.randint(100, 999)
                    RecipientID = st.number_input("Enter Recipient ID:", min_value=1)
                    DonorID = st.number_input("Enter Donor ID:", min_value=1)
                    BloodGroup = st.selectbox("Select Blood Group:", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
                    Quantity = st.number_input("Enter Quantity (ml):", min_value=1)
                    Date = st.date_input("Date:", datetime.date.today())
            
                    submit = st.form_submit_button("Add Record", use_container_width=True)
            
                    if submit:
                        data = [(TransactionID,RecipientID, DonorID, BloodGroup,Quantity, Date)]
                        df_new = pd.DataFrame(
                            data,
                            columns=['TransactionID','RecipeintID', 'DonorID', 'BloodGroup', 'Quantity','Date']
                        )
            
                        st.write("New transaction record added:")
                        st.dataframe(df_new)
            
                        df_new.to_sql("transactions", engine, if_exists="append", index=False)
                        st.success("Transaction record successfully added!")

            col1 , col2, col3 = st.columns(3)
            with col1:
                if st.button("Clear Transaction",use_container_width=True):
                    cur.execute("Truncate table transactions")
    else:
        st.markdown(
                """
                <h1 style='text-align: center; color: #b22222; font-family: "Trebuchet MS", sans-serif;'>
                    🏥 VitalFlow: Smart Blood Bank Manager
                </h1>
                <h6 style='text-align: center; color: #444444; font-family: "Trebuchet MS", sans-serif;'>
                    A streamlined system for donor and inventory management
                </h6>
                """,
                unsafe_allow_html=True
            )        

        engine = create_engine("mysql+mysqlconnector://root:kr$na128@localhost/blood_bank_management_system")
        st.divider()
        st.subheader("🏠 Home")
            
        st.write("Requests")
        query = "SELECT * FROM recipents ORDER BY RequestDate LIMIT 5"
        df = pd.read_sql(query, engine)
        st.dataframe(df)
        
        st.divider()
            
        st.subheader("🔍 Search")
        B = st.selectbox("Select Blood Group", ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"])
        c = st.selectbox("Select City",["Ahmedabad", "Gandhinagar", "Surat", "Rajkot"])
        q = "Select * From donors order by DonatedDate"
        d = pd.read_sql(q,engine)
        
        st.write("Donors")
        st.dataframe(d[(d["BloodGroup"]==B) & (d["City"]==c)])
        
        q2 = "SELECT * FROM inventory ORDER BY CollectionDate DESC"
        d2 = pd.read_sql(q2, engine)
        
        st.write("Available in Inventory")
        st.dataframe(d2[d2["Blood Group"]==B])
        