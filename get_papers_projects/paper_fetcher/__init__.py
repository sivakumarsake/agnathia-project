import paperfetcher
# Sample patient data
patients = [
    {"Patient ID": "P001", "Name": "John Doe", "Condition": "Cancer"},
    {"Patient ID": "P002", "Name": "Jane Smith", "Condition": "Diabetes"}
]

# Create fetcher with patient data
fetcher = paperfetcher(query="cancer therapy", email="sivakumarshiv1191@gmail.com", patient_data=patients, debug=True)

# Fetch and save data
ids = fetcher.fetch_paper_ids()
details = fetcher.fetch_paper_details(ids)
fetcher.save_to_csv(details, "papers_with_patients.csv")