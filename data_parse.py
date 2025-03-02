import pandas as pd
import re

data = pd.read_csv('linkedin_jobs_filtered.csv')
data.rename(columns={'date': 'posting_date'}, inplace=True)  

def extract_salary(description):
    """
    Extracts the salary range from the description and classifies as per hour or per year.
    """
    if pd.isna(description):
        return 'NA'
    
    hourly_pattern = r'(\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?(?:\s*[-–]\s*\$?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)?)(?:\s*(?:\/|per)\s*hour|\s*hourly)'
    hourly_match = re.search(hourly_pattern, description, re.IGNORECASE)
    
    if hourly_match:
        return f"{hourly_match.group(1)} per hour"
    
    annual_pattern = r'(\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?(?:\s*[-–]\s*\$?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)?)(?:\s*(?:\/|per)\s*(?:year|annum|annually))'
    annual_match = re.search(annual_pattern, description, re.IGNORECASE)
    
    if annual_match:
        return f"{annual_match.group(1)} per year"
    
    general_pattern = r'(\$\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?(?:\s*[-–]\s*\$?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?)?)'
    general_match = re.search(general_pattern, description, re.IGNORECASE)
    
    if general_match:
        salary_text = general_match.group(1)
        first_number_match = re.search(r'\$(\d{1,3}(?:,\d{3})*)', salary_text)
        if first_number_match:
            first_number = float(first_number_match.group(1).replace(',', ''))
            if first_number < 100:  
                return f"{salary_text} per hour"
            elif first_number < 50000:  
                return f"{salary_text} (unspecified rate)"
            else: 
                return f"{salary_text} per year"
        return f"{salary_text} (unspecified rate)"
    
    return 'NA'

data['salary_range'] = data['job_description'].apply(extract_salary)

filtered_data = data[['title', 'company', 'location', 'posting_date', 'salary_range', 'job_description']]

print(filtered_data.head())

filtered_data.to_csv('filtered_linkedin_jobs.csv', index=False)