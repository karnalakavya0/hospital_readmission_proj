# ml_visuals.py
import shap
import pandas as pd
import streamlit as st

def plot_shap_contributions(ml_model, patient_row, patients_df):
    """
    Generate and display a SHAP feature contribution bar chart for a single patient.

    Parameters:
        ml_model: Trained ML model (e.g., XGBoost)
        patient_row: pd.Series of the selected patient
        patients_df: pd.DataFrame containing all patients (needed for feature alignment)
    """
    if ml_model is None:
        st.warning("ML model not loaded. SHAP plot unavailable.")
        return

    # Get feature names from model
    try:
        feature_cols = ml_model.get_booster().feature_names
    except:
        st.warning("Unable to retrieve model feature names from ML model.")
        return

    # Ensure all features exist in patients_df
    for col in feature_cols:
        if col not in patients_df.columns:
            patients_df[col] = 0

    # Prepare features for the selected patient
    X_patient = patients_df.loc[patients_df['patient_id'] == patient_row['patient_id'], feature_cols]

    # Compute SHAP values
    explainer = shap.TreeExplainer(ml_model)
    shap_values = explainer.shap_values(X_patient)

    # Convert to DataFrame for plotting
    shap_df = pd.DataFrame({
        'Feature': feature_cols,
        'Contribution': shap_values[0]  # first (and only) row
    }).sort_values(by='Contribution', key=abs, ascending=False)

    # Display bar chart in Streamlit
    st.markdown("### Feature Contribution to Readmission Risk (SHAP)")
    st.bar_chart(shap_df.set_index('Feature')['Contribution'])
