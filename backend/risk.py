import numpy as np

def calculate_risk(df):
    #calculate a combined risk score based on patient health factors
    df['risk_score'] = (
        0.4 * (df['agefactor'] / 100) +
        0.8 * (df['WBC mean'] / 20000) +
        0.3 * (df['heart rate'] / 200) +
        1.5 * df['diabetes'] +
        1.0 * df['hypertension']
    )
    #convert the combined score into percentage.
    df['risk_score'] = 1 / (1 + np.exp(-df['risk_score'])) * 100
    return df

def assign_risk_level(score):
    #label the risk level as high,medium or low based on the percentage
    if score >= 75: return "HIGH"
    elif score >= 50: return "MEDIUM"
    else: return "LOW"

def individual_savings(risk_score, cost_per_patient=15000, prevention_success_rate=0.7):
    #estimates how much money can be saved by preventing complications in one patient based on their risk.
    return cost_per_patient * (risk_score/100) * prevention_success_rate

def hospital_impact(df):
    #calculate total expected savings for all patients and limit it to a maximum allowed amount.
    df['expected_saving'] = df['risk_score'].apply(individual_savings)
    total_saving = df['expected_saving'].sum()
    max_penalty_reduction = 26e9 * 0.15 # this is the highest total penalty reduction the hospital can get
    return min(total_saving, max_penalty_reduction)

def assign_readmission_flag(prob):
    #assign readmission risk flags based on probability thresholds
    if prob >= 0.7: return "High Risk"
    elif prob >= 0.4: return "Moderate Risk"
    else: return "Low Risk"
