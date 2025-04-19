import pandas as pd
from transformers import pipeline
from tqdm import tqdm

# Zero-shot classification for "Job Title" to "Position" column
df_j = pd.read_csv("./Dataset/Jobstreet/Jobstreet_combined_data2.csv")

# Jobstreet Data for Extract the more simple Position from Job Title by using NLP method
# Load zero-shot classification pipeline
classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-3")

candidate_labels = ["Data Scientist", "Data Analyst", "Data Engineer", "Data Operation", 
                    "Business Analyst", "Software Developer", "Machine Learning Engineer", 
                    "Business Intelligence Analyst", "AI Engineer", "Others"]

df_j2 = df_j.copy()

titles = df_j2['Job Title'].tolist()
positions = []
for title in tqdm(titles, desc="Classifying job titles"):
    try:
        result = classifier(title, candidate_labels)
        positions.append(result['labels'][0])  
    except Exception as e:
        print(f"Error processing title: {title} | {e}")
        positions.append("Others") 

df_j2['Position'] = positions
df_j2.to_csv("./Dataset/Jobstreet/Updated_Jobstreet_data.csv", index=False)
print("'Updated_Jobstreet_data.csv' save successfully!")