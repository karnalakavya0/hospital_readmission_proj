import sqlite3
import pandas as pd
import streamlit as st
#keep data ready so we don't load it again and again
@st.cache_data
def load_patients_from_db(db_path):
    #to open the database file
    conn = sqlite3.connect(db_path)
    try:
        #gets all the patient info from the admissions table
        df = pd.read_sql("SELECT * FROM admissions_scored", conn)
    finally:
        #ends the connection to the database when done
        conn.close()
    #returns the patient data to use in the app
    return df
