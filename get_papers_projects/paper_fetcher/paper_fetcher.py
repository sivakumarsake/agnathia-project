import csv
from typing import List, Dict, Optional
import xml.etree.ElementTree as ET
from Bio import Entrez
import time
class paperfetcher:
    """Handles fetching and processing of PubMed papers, with optional patient data."""
    
    def __init__(self, query: str, email: str, patient_data: Optional[List[Dict[str, str]]] = None, debug: bool = False):
        self.query = query
        self.email = email
        self.patient_data = patient_data or []  # Store patient data if provided, default to empty list
        self.debug = debug
        self.base_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    def _log(self, message: str) -> None:
        """Log debug messages if debug is enabled."""
        if self.debug:
            print(f"DEBUG: {message}")

    def fetch_paper_ids(self) -> List[str]:
        """Fetch PubMed IDs based on the query."""
        try:
            self._log(f"Fetching IDs for query: {self.query}")
            Entrez.email = self.email
            handle = Entrez.esearch(db="pubmed", term=self.query, retmax=100)
            record = Entrez.read(handle)
            handle.close()
            return record["IdList"]
        except Exception as e:
            raise RuntimeError(f"Failed to fetch paper IDs: {str(e)}")

    def fetch_paper_details(self, ids: List[str]) -> List[Dict[str, str]]:
        """Fetch details for given PubMed IDs."""
        try:
            self._log(f"Fetching details for {len(ids)} papers")
            Entrez.email = self.email
            handle = Entrez.efetch(db="pubmed", id=",".join(ids), retmode="xml")
            xml_data = handle.read()
            handle.close()
            return self._parse_xml(xml_data)
        except Exception as e:
            raise RuntimeError(f"Failed to fetch paper details: {str(e)}")

    def _parse_xml(self, xml_data: bytes) -> List[Dict[str, str]]:
        """Parse XML data and extract required fields."""
        root = ET.fromstring(xml_data)
        results = []

        for article in root.findall(".//PubmedArticle"):
            paper: Dict[str, str] = {
                "PubmedID": "",
                "Title": "",
                "Publication Date": "",
                "Non-academic Author(s)": "",
                "Company Affiliation(s)": "",
                "Corresponding Author Email": "",
                "Related Patient IDs": ""  # New field to link patient data
            }

            # Extract PubMed ID
            pmid = article.find(".//PMID")
            paper["PubmedID"] = pmid.text if pmid is not None else ""

            # Extract Title
            title = article.find(".//ArticleTitle")
            paper["Title"] = title.text if title is not None else ""

            # Extract Publication Date
            date = article.find(".//PubDate/Year")
            paper["Publication Date"] = date.text if date is not None else ""

            # Extract Authors and Affiliations
            authors = article.findall(".//Author")
            non_academic_authors = []
            companies = []
            email = ""

            for author in authors:
                last_name = author.find("LastName")
                initials = author.find("Initials")
                affiliation = author.find(".//Affiliation")
                
                name = f"{last_name.text} {initials.text}" if last_name is not None and initials is not None else ""
                aff_text = affiliation.text if affiliation is not None else ""

                # Heuristic: Check for company-like affiliations
                if aff_text and any(keyword in aff_text.lower() for keyword in ["pharma", "bio", "inc", "ltd", "@"]):
                    non_academic_authors.append(name)
                    companies.append(aff_text.split(",")[0])

                # Check for email (assume last author is corresponding)
                if author == authors[-1] and "@" in aff_text:
                    email = aff_text.split()[-1] if "@" in aff_text.split()[-1] else ""

            paper["Non-academic Author(s)"] = "; ".join(non_academic_authors)
            paper["Company Affiliation(s)"] = "; ".join(companies)
            paper["Corresponding Author Email"] = email

            # Link patient data (example heuristic: match by query-related condition)
            if self.patient_data:
                related_patients = [p["Patient ID"] for p in self.patient_data if self.query.lower() in p.get("Condition", "").lower()]
                paper["Related Patient IDs"] = "; ".join(related_patients)

            if non_academic_authors:  # Only include papers with non-academic authors
                results.append(paper)

        self._log(f"Parsed {len(results)} papers with non-academic affiliations")
        return results

    def save_to_csv(self, papers: List[Dict[str, str]], filename: Optional[str] = None) -> None:
        """Save results to CSV or print to console, including patient data."""
        headers = ["PubmedID", "Title", "Publication Date", "Non-academic Author(s)", 
                   "Company Affiliation(s)", "Corresponding Author Email", "Related Patient IDs"]
        
        # If patient_data exists, append patient details to the output
        if self.patient_data and filename:
            patient_headers = ["Patient ID", "Name", "Condition"]  # Example patient fields
            all_headers = headers + [h for h in patient_headers if h not in headers]
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=all_headers)
                writer.writeheader()
                
                # Write paper data with linked patient info
                for paper in papers:
                    row = paper.copy()
                    if paper["Related Patient IDs"]:
                        patient_ids = paper["Related Patient IDs"].split("; ")
                        for pid in patient_ids:
                            patient = next((p for p in self.patient_data if p["Patient ID"] == pid), {})
                            row.update(patient)  # Add patient details to the row
                            writer.writerow(row)
                    else:
                        writer.writerow(row)
            self._log(f"Saved results with patient data to {filename}")
        elif filename:
            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
                writer.writerows(papers)
            self._log(f"Saved results to {filename}")
        else:
            print(",".join(headers))
            for paper in papers:
                print(",".join(f'"{paper[h]}"' for h in headers))
