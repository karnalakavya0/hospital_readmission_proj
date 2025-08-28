# ehr_main_app.py
import streamlit as st
import os
import pickle
from backend.data import load_patients_from_db
from backend.risk import calculate_risk, assign_risk_level_vectorized, assign_readmission_flag_vectorized, hospital_impact
from backend.report import generate_structured_report, create_patient_pdf_bytes
from frontend.ui import display_patient_summary
from backend.ml_visuals import plot_shap_contributions

# -------------------------
# Load ML model safely
# -------------------------
MODEL_PATH = "xgb_readmission_model.pkl"
ml_model = None
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        ml_model = pickle.load(f)
    st.sidebar.success("✅ ML model loaded successfully.")
else:
    st.sidebar.warning("⚠ ML model not found. ML predictions and SHAP will be unavailable.")

# -------------------------
# Load patients from DB
# -------------------------
DB_PATH = "ehr_large.db"
patients_df = load_patients_from_db(DB_PATH)

# -------------------------
# Calculate risk scores and levels
# -------------------------
patients_df = calculate_risk(patients_df)
patients_df['risk_level'] = assign_risk_level_vectorized(patients_df['risk_score'])
patients_df['expected_saving'] = patients_df['risk_score'].apply(lambda x: 15000*(x/100)*0.7)
overall_impact = hospital_impact(patients_df)

# -------------------------
# ML readmission probability
# -------------------------
if ml_model:
    feature_cols = ['agefactor','WBC mean','heart rate','diabetes','hypertension']
    X = patients_df[feature_cols].values
    try:
        preds = ml_model.predict_proba(X)[:,1]
        patients_df['readmit_prob'] = preds
    except:
        patients_df['readmit_prob'] = patients_df['risk_score']/100
else:
    patients_df['readmit_prob'] = patients_df['risk_score']/100

# Assign readmission flags
patients_df['readmit_flag'] = assign_readmission_flag_vectorized(patients_df['readmit_prob'])

# -------------------------
# Streamlit UI
# -------------------------
st.set_page_config(layout="wide")
st.title("🏥 Hospital EHR Patient Analysis")

# Patient selection
patient_options = patients_df[['patient_id','name']].values.tolist()
patient_dict = dict(patient_options)
selected_patient_id = st.selectbox(
    "Select patient",
    list(patient_dict.keys()),
    format_func=lambda x: patient_dict[x]
)
patient_row = patients_df[patients_df["patient_id"]==selected_patient_id].iloc[0]

# Display patient summary
display_patient_summary(patient_row, overall_impact)

# Predictive readmission alert
st.markdown("### Predictive Readmission Alert")
if patient_row['readmit_flag'] == "High Risk":
    st.markdown(f"<span style='color:red;font-weight:bold'>⚠ High-Risk ({patient_row['readmit_prob']*100:.1f}%)</span>", unsafe_allow_html=True)
elif patient_row['readmit_flag'] == "Moderate Risk":
    st.markdown(f"<span style='color:orange;font-weight:bold'>⚠ Medium-Risk ({patient_row['readmit_prob']*100:.1f}%)</span>", unsafe_allow_html=True)
else:
    st.markdown(f"<span style='color:green;font-weight:bold'>Low Risk ({patient_row['readmit_prob']*100:.1f}%)</span>", unsafe_allow_html=True)

# -------------------------
# PDF generation
# -------------------------
if st.button("Generate PDF"):
    report = generate_structured_report(patient_row)
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

    pdf_bytes = create_patient_pdf_bytes(patient_row, summary_text)
    st.download_button(
        label="Download Patient Summary PDF",
        data=pdf_bytes,
        file_name=f"{patient_row.get('name','unknown')}_summary.pdf",
        mime="application/pdf"
    )

# -------------------------
# SHAP feature contributions
# -------------------------
if ml_model:
    plot_shap_contributions(ml_model, patient_row, patients_df)
