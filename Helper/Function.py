import pandas as pd
import re
import os
import numpy as np
import streamlit as st
import spacy
from spacy.matcher import PhraseMatcher
from rapidfuzz import fuzz
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

def combine_data(file_list, path_way, output_file="Coursera_combined_data.csv"):
    combine_df = pd.DataFrame()

    for file in file_list:
        file_path = os.path.join(path_way, file)
        try:
            df = pd.read_csv(file_path)
            combine_df = pd.concat([combine_df, df], ignore_index=True)
        except Exception as error:
            print(f"Error reading {file}: {error}")

    output_path = os.path.join(path_way, output_file)
    combine_df.to_csv(output_path, index=False)
    print(f"Combined CSV saved to: {output_path} successfully!")
    return combine_df

def update_salary(salary_str):
    if isinstance(salary_str, str):
        salary_str = salary_str.replace(',', '')
        # Use regex to extract numeric values, which also works with salary ranges
        salary_values = re.findall(r'\d+\.?\d*', salary_str)  # This will extract all numbers (integers or floats)
        if len(salary_values) == 2:
            try:
                lower_salary = float(salary_values[0])
                upper_salary = float(salary_values[1])
                return round((lower_salary + upper_salary) / 2 )
            except ValueError:
                return salary_str
        elif len(salary_values) == 1:
            try:
                return round(float(salary_values[0]) )
            except ValueError:
                return salary_str
    return salary_str

def classify_job_level(job_title):
    job_title = job_title.lower()
    if 'intern' in job_title:
        return 'Intern'
    elif 'junior' in job_title:
        return 'Junior'
    elif 'senior' in job_title:
        return 'Senior'
    elif 'manager' in job_title:
        return 'Manager'
    elif 'director' in job_title:
        return 'Director'
    elif 'vice president' in job_title:
        return 'Vice President'
    elif 'lead' in job_title:
        return 'Lead'
    elif 'head' in job_title:
        return 'Head'
    else:
        return 'Junior'    

# Load model
@st.cache_resource
def load_embedding_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

# Load job DataFrame from .pkl
@st.cache_data
def load_job_embeddings():
    df = pd.read_pickle("./Dataset/Jobstreet/Jobstreet_after_embeddings.pkl")
    df["Embeddings cleaned responsibilities"] = df["Embeddings cleaned responsibilities"].apply(np.array)
    return df

# Function to extract skills from the Job Responsibility column
def extract_skills_from_job_responsibility(job_responsibility_text):
    nlp = spacy.load("en_core_web_md")
    
    known_skills = [
        "python", "r", "sql", "java", "scala", "c++", "matlab", "julia", "mysql", 
    "postgresql", "mongodb", "cassandra", "oracle", "hadoop", "hbase", "etl", 
    "nosql", "redis", "elasticsearch", "tableau", "power bi", "qlikview", "apache superset", 
    "matplotlib", "seaborn", "plotly", "d3.js", "machine learning", "deep learning", 
    "tensorflow", "keras", "pytorch", "scikit-learn", "xgboost", "lightgbm", "nlp", 
    "computer vision", "ai", "apache spark", "apache kafka", "apache flink", "databricks", 
    "aws", "google cloud", "azure", "docker", "kubernetes", "google bigquery", "aws s3", 
    "aws lambda", "terraform", "apache airflow", "data pipeline", "apache nifi", 
    "kafka streams", "data integration", "data modeling", "data governance", "data quality", 
    "jenkins", "git", "ci/cd", "github", "ansible", "chef", "puppet", "microservices", 
    "devops", "cloud computing", "network security", "docker containers", "agile", 
    "scrum", "project management", "business intelligence", "data visualization", 
    "database administration", "machine learning algorithms", "data architecture", 
    "data engineering", "data science", "big data", "computer networks", "digital transformation", 
    "data wrangling", "business analysis", "digital marketing", "customer relations",
    "market research", "data analysis", "excel", "procurement", "supply chain management"
    ]
    
    doc = nlp(job_responsibility_text.lower())
    
    matcher = PhraseMatcher(nlp.vocab)
    patterns = [nlp.make_doc(skill) for skill in known_skills]
    matcher.add("SKILLS", patterns)
    
    matches = matcher(doc)
    matched_skills = [doc[start:end].text for _, start, end in matches]   
    lemmatized_tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]
    noun_chunks = [chunk.text for chunk in doc.noun_chunks]

    irrelevant_terms = [
        "ability", "skills", "team", "knowledge", "experience", "strong", "good", "excellent",
        "that", "a", "the", "and", "or", "in", "for", "management", "product managers", 
        "orders", "prothesis", "leadership", "communication", "efficient", "result", "september", "services"
    ]
    
    filtered_noun_chunks = [chunk for chunk in noun_chunks if all(term not in chunk for term in irrelevant_terms)]
    all_skills = set(matched_skills + filtered_noun_chunks)
    fuzzy_matches = [skill for skill in known_skills if any(fuzz.partial_ratio(skill, token) > 80 for token in lemmatized_tokens)]
    combined_skills = list(set(all_skills).union(fuzzy_matches))
    
    return combined_skills

# Function to extract skills from the Resume text
def extract_skills_from_resume(resume_text):
    nlp = spacy.load("en_core_web_md")
    
    known_skills = [
        "python", "r", "sql", "java", "scala", "c++", "matlab", "julia", "mysql", 
    "postgresql", "mongodb", "cassandra", "oracle", "hadoop", "hbase", "etl", 
    "nosql", "redis", "elasticsearch", "tableau", "power bi", "qlikview", "apache superset", 
    "matplotlib", "seaborn", "plotly", "d3.js", "machine learning", "deep learning", 
    "tensorflow", "keras", "pytorch", "scikit-learn", "xgboost", "lightgbm", "nlp", 
    "computer vision", "ai", "apache spark", "apache kafka", "apache flink", "databricks", 
    "aws", "google cloud", "azure", "docker", "kubernetes", "google bigquery", "aws s3", 
    "aws lambda", "terraform", "apache airflow", "data pipeline", "apache nifi", 
    "kafka streams", "data integration", "data modeling", "data governance", "data quality", 
    "jenkins", "git", "ci/cd", "github", "ansible", "chef", "puppet", "microservices", 
    "devops", "cloud computing", "network security", "docker containers", "agile", 
    "scrum", "project management", "business intelligence", "data visualization", 
    "database administration", "machine learning algorithms", "data architecture", 
    "data engineering", "data science", "big data", "computer networks", "digital transformation", 
    "data wrangling", "business analysis", "digital marketing", "customer relations",
    "market research", "data analysis", "excel", "procurement", "supply chain management"
    ]
    
    resume_text = resume_text.lower()    
    doc = nlp(resume_text)
    
    matcher = PhraseMatcher(nlp.vocab)
    patterns = [nlp.make_doc(skill) for skill in known_skills]
    matcher.add("SKILLS", patterns)
    
    matches = matcher(doc)
    matched_skills = [doc[start:end].text for _, start, end in matches]    
    lemmatized_tokens = [token.lemma_ for token in doc if not token.is_stop and not token.is_punct]    
    noun_chunks = [chunk.text for chunk in doc.noun_chunks]
    
    irrelevant_terms = [
        "ability", "skills", "team", "knowledge", "experience", "strong", "good", "excellent",
        "that", "a", "the", "and", "or", "in", "for", "management", "product managers", 
        "orders", "prothesis", "leadership", "communication", "efficient", "result", "september", "services"
    ]
    
    filtered_noun_chunks = [chunk for chunk in noun_chunks if all(term not in chunk for term in irrelevant_terms)]
    all_skills = set(matched_skills + filtered_noun_chunks)
    fuzzy_matches = [skill for skill in known_skills if any(fuzz.partial_ratio(skill, token) > 80 for token in lemmatized_tokens)]
    combined_skills = list(set(all_skills).union(fuzzy_matches))
    
    return combined_skills

def get_top_matches(base_list, compare_list, top_n):
    vectorizer = TfidfVectorizer().fit(base_list + compare_list) 
    base_vecs = vectorizer.transform(base_list)
    compare_vecs = vectorizer.transform(compare_list)

    similarity = cosine_similarity(base_vecs, compare_vecs)
    matches = []

    for i, row in enumerate(similarity):
        top_indices = row.argsort()[::-1]  # Sort similarities in descending order
        for idx in top_indices:
            if compare_list[idx] not in matches:
                matches.append(compare_list[idx])
                break
        if len(matches) >= top_n:  
            break

    return matches[:top_n]
