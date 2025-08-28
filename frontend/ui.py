import streamlit as st

def display_patient_summary(patient_row, overall_impact):
    #patient basic information
    st.markdown("### Patient Details")
    st.markdown(f"Name: {patient_row.get('name','')}")
    st.markdown(f"Age: {patient_row.get('agefactor','')}")
    st.markdown(f"Disease: {patient_row.get('disease','')}")
    #risk assessment
    st.markdown("### Patient Risk Assessment")
    st.markdown(f"Risk Score: {patient_row['risk_score']:.2f}%")
    st.markdown(f"Risk Level: {patient_row['risk_level']}")
    st.markdown(f"Recommendation: {patient_row['recommendation']}")
    #patient level financial-impact
    st.markdown("### Individual Patient Impact")
    st.markdown(f"**Expected Money Saved:** ${patient_row['expected_saving']:,.2f}")
    #Hospital wide financial saving
    st.markdown("### Overall Hospital Impact")
    st.markdown(f"**Estimated Overall Savings:** ${overall_impact:,.2f}")
