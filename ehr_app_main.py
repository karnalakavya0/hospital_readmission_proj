import streamlit as st
from backend.data import load_patients_from_db
from backend.risk import calculate_risk, assign_risk_level, assign_readmission_flag, hospital_impact
from backend.report import generate_structured_report, create_patient_pdf_bytes
from frontend.ui import display_patient_summary
#load data and calculate risk scores
DB_PATH = "ehr_large.db"
patients_df = load_patients_from_db(DB_PATH)#get patient info from database
patients_df = calculate_risk(patients_df) #calculate health risk scores
#determine risk level based on risk score
patients_df['risk_level'] = patients_df['risk_score'].apply(assign_risk_level) #categorize risk level
patients_df['expected_saving'] = patients_df['risk_score'].apply(lambda x: 15000*(x/100)*0.7)
#calculate total possible savings for hospital
overall_impact = hospital_impact(patients_df)
#user interface: app title and selection box
st.title("🏥 Hospital EHR Patient Analysis")

patient_options = patients_df[['patient_id','name']].values.tolist()
patient_dict = dict(patient_options)
#let user pick a patient to view
selected_patient_id = st.selectbox("Select patient", list(patient_dict.keys()), format_func=lambda x: patient_dict[x])
patient_row = patients_df[patients_df["patient_id"]==selected_patient_id].iloc[0]
#shows selected patient's summary on screen
display_patient_summary(patient_row, overall_impact)
#generate and download PDF report when button clicked 
if st.button("Generate PDF"):
    report = generate_structured_report(patient_row)
    #convert report dictionary into readable summary text
    summary_text = ""
    for section, content in report.items():
        summary_text += f"{section}:\n"
        if isinstance(content, dict):
            for k,v in content.items():
                summary_text += f"  {k}: {', '.join(v)}\n"
        elif isinstance(content,list):
            for item in content:
                summary_text += f"  - {item}\n"
        else:
            summary_text += f"  {content}\n"
        summary_text += "\n"
    #create and offer PDF download
    pdf_bytes = create_patient_pdf_bytes(patient_row, summary_text)
    st.download_button(
        label="Download Patient Summary PDF",
        data=pdf_bytes,
        file_name=f"{patient_row.get('name','unknown')}_summary.pdf",
        mime="application/pdf"
    )
