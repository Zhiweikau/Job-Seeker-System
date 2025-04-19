import sys
sys.path.append('.')
import pandas as pd
from Helper.Function import combine_data

# Data preprocessing for Coursera Data by gathering all of the data
file_list_coursera = ["coursera_AI_Engineer.csv", "coursera_Business_Intelligence_Analyst.csv", "coursera_Machine_Learning_Engineer.csv",
             "coursera_Software_Developer.csv", "coursera_Business_Analyst.csv", "coursera_Data_Engineer.csv",
             "coursera_Data_Analyst.csv", "coursera_Data_Scientist.csv"]
path_way_coursera = "./Dataset/Coursera"
df_combined_coursera_data = combine_data(file_list_coursera, path_way_coursera, output_file="Coursera_combined_data.csv")


# Data preprocessing for Jobstreet Data by gathering all of the data
file_list_jobstreet = ["AI_Engineer_sample.csv", "Business_Intelligence_Analyst_sample.csv", "Machine_Learning_Engineer_sample.csv",
             "Software_Developer_sample.csv", "Business_Analyst_sample.csv", "Data_Engineer_sample.csv",
             "Data_Analyst_sample.csv", "Data_Scientist_sample.csv", "Data_Operation_sample.csv"]
path_way_jobstreet = "./Dataset/Jobstreet"
df_combined_jobstreet_data = combine_data(file_list_jobstreet, path_way_jobstreet, output_file="Jobstreet_combined_data.csv")
df = pd.read_csv("./Dataset/Jobstreet/Jobstreet_combined_data.csv")
df.to_csv("./Dataset/Jobstreet/Jobstreet_combined_data.csv", index=False, encoding='utf-8-sig')