import numpy as np
import pandas as pd

# -------------------------
# Risk Calculation
# -------------------------
def calculate_risk(df, weights=None):
    """
    Calculate risk score for each patient in the dataframe.
    
    Parameters:
        df (pd.DataFrame): Patient dataset with necessary columns.
        weights (dict, optional): Weights for each feature. Defaults to predefined values.
        
    Returns:
        pd.DataFrame: Updated dataframe with 'risk_score' column.
    """
    if weights is None:
        weights = {
            'agefactor': 0.4,
            'WBC mean': 0.8,
            'heart rate': 0.3,
            'diabetes': 1.5,
            'hypertension': 1.0
        }
    
    # Ensure all necessary columns exist
    for col in weights.keys():
        if col not in df.columns:
            df[col] = 0

    df['risk_score'] = (
        weights['agefactor'] * (df['agefactor'] / 100) +
        weights['WBC mean'] * (df['WBC mean'] / 20000) +
        weights['heart rate'] * (df['heart rate'] / 200) +
        weights['diabetes'] * df['diabetes'] +
        weights['hypertension'] * df['hypertension']
    )
    
    # Sigmoid scaling to percentage
    df['risk_score'] = 1 / (1 + np.exp(-df['risk_score'])) * 100
    return df

# -------------------------
# Risk Level Assignment
# -------------------------
def assign_risk_level_vectorized(scores: pd.Series) -> pd.Series:
    """
    Assign categorical risk levels based on numeric risk scores.
    
    Parameters:
        scores (pd.Series): Risk scores (0-100)
        
    Returns:
        pd.Series: Categorical risk levels ('LOW', 'MEDIUM', 'HIGH')
    """
    return np.where(scores >= 75, "HIGH", np.where(scores >= 50, "MEDIUM", "LOW"))

# -------------------------
# Individual Patient Savings
# -------------------------
def individual_savings(risk_score, cost_per_patient=15000, prevention_success_rate=0.7):
    """
    Calculate expected savings per patient by preventing readmission.
    
    Parameters:
        risk_score (float): Patient risk score (0-100)
        cost_per_patient (float): Cost of readmission per patient
        prevention_success_rate (float): Probability intervention prevents readmission
        
    Returns:
        float: Expected savings
    """
    return cost_per_patient * (risk_score / 100) * prevention_success_rate

# -------------------------
# Hospital-wide Impact
# -------------------------
def hospital_impact(df: pd.DataFrame) -> float:
    """
    Calculate hospital-wide potential savings from interventions.
    
    Parameters:
        df (pd.DataFrame): Patient dataframe with 'risk_score' column
    
    Returns:
        float: Total expected savings (capped by maximum penalty reduction)
    """
    df['expected_saving'] = df['risk_score'].apply(individual_savings)
    total_saving = df['expected_saving'].sum()
    max_penalty_reduction = 26e9 * 0.15
    return min(total_saving, max_penalty_reduction)

# -------------------------
# Readmission Flag
# -------------------------
def assign_readmission_flag_vectorized(probs: pd.Series) -> pd.Series:
    """
    Assign readmission risk flags based on predicted probability.
    
    Parameters:
        probs (pd.Series): Predicted probability of readmission (0-1)
        
    Returns:
        pd.Series: Flags ('Low Risk', 'Moderate Risk', 'High Risk')
    """
    return np.where(probs >= 0.7, "High Risk",
                    np.where(probs >= 0.4, "Moderate Risk", "Low Risk"))
