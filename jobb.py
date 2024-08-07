
import streamlit as st
import pandas as pd
import pickle

# Assuming userprofile_df and job_df are already defined DataFrames
# Replace this with your actual DataFrames or loading logic
userprofile_df = pd.read_csv('userprofile.csv')
job_df = pd.read_csv('job_data.csv')

# Save the DataFrames into a pickle file
data = {
    'userprofile_df': userprofile_df,
    'job_df': job_df
}

with open('recommended_jobs.pkl', 'wb') as file:
    pickle.dump(data, file)

# Function to load data from pickle file
@st.cache_data()
def load_data(pickle_file):
    try:
        with open(pickle_file, 'rb') as file:
            data = pickle.load(file)
            if isinstance(data, dict) and 'userprofile_df' in data and 'job_df' in data:
                return data['userprofile_df'], data['job_df']
            else:
                raise ValueError("Invalid pickle file format. Expected a dictionary with 'userprofile_df' and 'job_df'.")
    except FileNotFoundError:
        st.error(f"File {pickle_file} not found.")
    except Exception as e:
        st.error(f"Error loading data: {e}")
    return None, None

# Define recommend_jobs function
def recommend_jobs(applicantId_or_skill, userprofile_df, job_df, top_n=3):
    if isinstance(applicantId_or_skill, str):  # Applicant ID case
        user_row = userprofile_df[userprofile_df['applicantId'] == applicantId_or_skill]

        if user_row.empty:
            return None  # Return None if applicant ID not found

        user_skills = set(user_row['skills'].iloc[0].lower().split(','))

        recommended_jobs = []
        for idx, job_data in job_df.iterrows():
            job_skills = set(job_data['skills'].lower().split(','))

            if user_skills.intersection(job_skills):
                recommended_jobs.append({
                    'position': job_data['position'],
                    'location': job_data['location'],
                    'skills': job_data['skills'],
                    'vacancies': job_data['vacancies'],
                    'minExp': job_data['minExp']
                })
                if len(recommended_jobs) == top_n:
                    break

    elif isinstance(applicantId_or_skill, list):  # Skills case
        recommended_jobs = []
        for skill in applicantId_or_skill:
            skill = skill.strip().lower()
            for idx, job_data in job_df.iterrows():
                job_skills = set(job_data['skills'].lower().split(','))

                if skill in job_skills:
                    recommended_jobs.append({
                        'position': job_data['position'],
                        'location': job_data['location'],
                        'skills': job_data['skills'],
                        'vacancies': job_data['vacancies'],
                        'minExp': job_data['minExp']
                    })
                    if len(recommended_jobs) == top_n:
                        break

    return recommended_jobs

# Main Streamlit app
def main():
    # Set page config
    st.set_page_config(page_title="Job Recommendation Engine", page_icon=":briefcase:", layout="wide", initial_sidebar_state="expanded")

    # Title
    st.markdown(
        """
        <style>
        .title {
            font-size: 3em;
            color: white;  /* Change the title color to white */
            text-align: center;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #333333;  /* Dark background */
            border-radius: 10px;
        }
        .selectbox-label {
            color: white !important;
        }
        .section-header {
            color: white;
        }
        .job-card {
            background-color: #f0f0f0;
            padding: 10px;
            margin-bottom: 10px;
            border: 1px solid #333333;
            border-radius: 5px;
            color: black;
        }
        .apply-button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            text-decoration: none;
            border-radius: 5px;
            display: inline-block;
            text-align: center;
        }
        @media (max-width: 767px) {
            .job-card {
                font-size: 1em;  /* Adjust font size for mobile */
            }
            .apply-button {
                padding: 8px 16px;  /* Adjust padding for mobile */
            }
        }
        </style>
        """, unsafe_allow_html=True
    )

    st.markdown('<div class="title">Job Recommendation Engine</div>', unsafe_allow_html=True)

    # Customizing the app appearance with a background image
    background_image_url = "https://e0.pxfuel.com/wallpapers/561/410/desktop-wallpaper-job-posting-sites-for-your-next-hire-employment-background-investigations-inc.jpg"  # Replace with your image URL
    st.markdown(f"""
        <style>
        .stApp {{
            background: url({background_image_url});
            background-size: cover;
        }}
        </style>
        """, unsafe_allow_html=True)

    # Extract unique skills from job_df
    unique_skills = set()
    for skills_str in job_df['skills']:
        skills_list = [skill.strip().lower() for skill in skills_str.split(',')]
        unique_skills.update(skills_list)
    unique_skills = sorted(unique_skills)  # Sort skills alphabetically

    # Input fields
    st.markdown('<div class="selectbox-label">Select an option:</div>', unsafe_allow_html=True)
    option = st.selectbox("", ["Applicant ID", "Skills"], key='select-option')

    if option == "Applicant ID":
        st.markdown('<div class="selectbox-label">Select Applicant ID:</div>', unsafe_allow_html=True)
        applicant_id_options = list(userprofile_df['applicantId'])
        applicant_id = st.selectbox("", applicant_id_options, key='select-applicant-id')
        if st.button("Recommend Jobs"):
            if not applicant_id:
                st.warning("Please select an Applicant ID.")
            else:
                recommended_jobs = recommend_jobs(applicant_id, userprofile_df, job_df)
                if recommended_jobs:
                    st.markdown('<div class="section-header">Recommended Jobs for Applicant ID {}</div>'.format(applicant_id), unsafe_allow_html=True)
                    for job in recommended_jobs:
                        st.markdown(
                            f"""
                            <div class='job-card'>
                                <h3 style='color: green;'>{job['position']}</h3>
                                <p><strong>Location:</strong> {job['location']}</p>
                                <p><strong>Skills Required:</strong> {job['skills']}</p>
                                <p><strong>Vacancies:</strong> {job['vacancies']}</p>
                                <p><strong>Minimum Experience Required:</strong> {job['minExp']}</p>
                                <a href="https://us13.list-manage.com/contact-form?u=8ac5c4589b3005482b2dcef3b&form_id=ad7d834f290d50ab3c74ac5ed2eef1b7" target="_blank" class="apply-button">Apply</a>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.warning(f"No matching jobs found for Applicant ID {applicant_id}.")

    elif option == "Skills":
        st.markdown('<div class="selectbox-label">Select Skills:</div>', unsafe_allow_html=True)
        selected_skills = st.multiselect("", unique_skills, key='select-skills')
        if st.button("Recommend Jobs"):
            if not selected_skills:
                st.warning("Please select at least one skill.")
            else:
                recommended_jobs = recommend_jobs(selected_skills, userprofile_df, job_df)
                if recommended_jobs:
                    st.markdown('<div class="section-header">Recommended Jobs based on Skills</div>', unsafe_allow_html=True)
                    for job in recommended_jobs:
                        st.markdown(
                            f"""
                            <div class='job-card'>
                                <h3 style='color: green;'>{job['position']}</h3>
                                <p><strong>Location:</strong> {job['location']}</p>
                                <p><strong>Skills Required:</strong> {job['skills']}</p>
                                <p><strong>Vacancies:</strong> {job['vacancies']}</p>
                                <p><strong>Minimum Experience Required:</strong> {job['minExp']}</p>
                                <a href="https://us13.list-manage.com/contact-form?u=8ac5c4589b3005482b2dcef3b&form_id=ad7d834f290d50ab3c74ac5ed2eef1b7" target="_blank" class="apply-button">Apply</a>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                else:
                    st.warning(f"No matching jobs found based on selected skills.")

if __name__ == "__main__":
    main()
