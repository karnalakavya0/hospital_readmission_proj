from fpdf import FPDF

def generate_structured_report(row):
    report = {}
    #calculate the readmission probability as a percentage
    readmit_prob_pct = row.get('readmit_prob',0)*100
    #get the readmission risk label
    readmit_flag = row.get('readmit_flag','Low Risk')
    #patient summary
    report['Patient Summary'] = (
        f"{row.get('name','Unknown')}, Age {row.get('agefactor',0)}, "
        f"Risk Score: {row.get('risk_score',0):.2f}% ({row.get('risk_level','LOW')}), "
        f"ML Readmission Probability: {readmit_prob_pct:.1f}% ({readmit_flag})"
    )
    #key risk factors based on age and medical conditions
    factors=[]
    if row.get('agefactor',0)>65: factors.append("Advanced age")
    for c in ['diabetes','hypertension','ckd','copd','cad','stroke','cancer']:
        if row.get(c,0)==1: factors.append(c.capitalize())
    if row.get('WBC mean',0)>11000: factors.append(f"High WBC ({row.get('WBC mean',0):,.0f})")
    if row.get('heart rate',0)>100: factors.append(f"High HR ({row.get('heart rate',0):.0f} bpm)")
    if row.get('BP-mean',0)>140 or row.get('BP-mean',0)<90: factors.append(f"Abnormal BP ({row.get('BP-mean',0):.0f} mmHg)")
    factors.append(f"Readmission Risk: {readmit_flag}")
    report['Risk Factors'] = factors if factors else ["None notable"]
    #collect current medications and suggestions based on conditions
    meds=[]
    suggestions=[]
    for m,s in [('antibiotics',"Consider antibiotics if infection suspected"),
                ('antihypertensives',"Ensure BP control with antihypertensives"),
                ('insulin',"Manage glucose with insulin or oral agents"),
                ('statins',"Continue statins for cardiac risk"),
                ('anticoagulants',"Evaluate need for anticoagulation")]:
        if row.get(m,0): meds.append(m.capitalize())
        elif m=='antibiotics' and row.get('WBC mean',0)>11000:
            suggestions.append("Consider antibiotics for elevated WBC")
    #store medications and clinical suggestions
    report['Medications & Suggestions'] = {
        'Current Medications': meds if meds else ["None"],
        'Suggestions': suggestions if suggestions else ["No additional suggestions"]
    }
    #recommended follow-up or intervention
    report['Recommended Interventions'] = row.get('recommendation','Standard follow-up')
    #extra notes for clinicians to monitor
    notes=[]
    if row.get('temperature mean',0)>100.4: notes.append("Monitor for fever")
    if row.get('haemoglobin',0)<12: notes.append("Check for anemia")
    report['Notes for Clinicians'] = notes if notes else ["No immediate concerns"]
    return report

def create_patient_pdf_bytes(patient_row, summary_text):
    pdf = FPDF()
    pdf.add_page() #start a new page
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Patient Risk Summary", ln=True, align="C") #centered title 
    pdf.set_font("Arial", "", 12) #normal font for content
    pdf.ln(10) #add some vertical space
    #print patient details line by line
    pdf.multi_cell(0,8,f"Patient Name: {patient_row.get('name','Unknown')}")
    pdf.multi_cell(0,8,f"Age: {patient_row.get('agefactor',0)}")
    pdf.multi_cell(0,8,f"Disease: {patient_row.get('disease','Unknown')}")
    pdf.multi_cell(0,8,f"Risk Score: {patient_row.get('risk_score',0):.2f}% ({patient_row.get('risk_level','LOW')})")
    pdf.multi_cell(0,8,f"Recommendation: {patient_row.get('recommendation','Standard follow-up')}")
    pdf.ln(5) #small gap before AI summary
    pdf.multi_cell(0,8,"AI-Generated Summary:")
    pdf.multi_cell(0,8,summary_text) #add the multi-line summary text
    #return pdf as a byte string for saving or downloading
    return pdf.output(dest='S').encode('latin1')
