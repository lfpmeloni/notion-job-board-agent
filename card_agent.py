import os
import datetime
import openai
import json  # Importing JSON module for safe parsing
from notion_client import Client
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve API keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
NOTION_API_KEY = os.getenv("NOTION_API_KEY")

# Configure OpenAI API key
openai.api_key = OPENAI_API_KEY

# Initialize the Notion Client
notion = Client(auth=NOTION_API_KEY)

# Notion API key and database ID (Kanban board ID)
PAGE_ID = "10de7e0f4b84809f8162c744000d9790"
#DATABASE_ID = "10de7e0f4b8480e799d2d697012fc903" #Test page
DATABASE_ID = "112e7e0f4b848136ad0dfd17eee073a3"  #Official page

# Function to extract job information using GPT-3.5
def extract_job_info_from_gpt(job_description):
    prompt = f"""
    You are an AI agent designed to extract key details from job descriptions. Based on the following job description, provide the information in JSON format with these fields:
    - "Company Name": string
    - "Job Name": string - Bring the complete name including field, if provided
    - "Language": string (e.g., "English, German") - If multiple languages, separate by comma
    - "Working Model": string (e.g., "Remote, Hybrid, Office") - If mentioned that hybrid or remote is possible, bring this possibility
    - "Location": string (e.g., city name where office is based, "Remote" is not applicable)
    - "Role": string (e.g., "Software Engineer", "Project Manager", "Developer")
    - "Short Job Description": string (1-2 sentences summary)
    - "Salary Expectation": number - without "" (salary expectation in euros per year, if unavailable make a guess based on seniority)

    Job Description:
    {job_description}

    Respond in JSON format only.
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "system", "content": prompt}],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract the completion
        completion = response['choices'][0]['message']['content']
        return completion.strip()
    except Exception as e:
        print(f"Error extracting job info from GPT: {e}")
        return None

# Function to read a notion page and retrieve the job description
def read_notion_page_content(page_id):
    try:
        blocks = notion.blocks.children.list(block_id=page_id).get('results', [])
        content = ""

        for block in blocks:
            block_type = block.get('type')
            block_data = block.get(block_type, {})

            if block_type in ['paragraph', 'heading_1', 'heading_2', 'heading_3']:
                text_elements = block_data.get('rich_text', [])
                text = "".join([part['plain_text'] for part in text_elements])
                content += text + " "
        
        return content.strip()
    except Exception as e:
        print(f"Error fetching Notion page {page_id}: {str(e)}")
        return ""

# Function to create a new card in the specified Notion board
def create_notion_card_on_page(database_id, company_name, status, job_name, job_description, language, model, location, role, salary_expectation):
    today_date = datetime.datetime.now().strftime("%Y-%m-%d")
    
    try:
        new_page = notion.pages.create(
            parent={"database_id": database_id},
            properties={
                "Company Name": {
                    "title": [
                        {
                            "text": {
                                "content": company_name
                            }
                        }
                    ]
                },
                "Status": {
                    "status": {
                        "name": status
                    }
                },
                "Date": {
                    "date": {
                        "start": today_date
                    }
                },
                "Job Name": {
                    "rich_text": [
                        {
                            "text": {
                                "content": job_name
                            }
                        }
                    ]
                },
                "Job Description": {
                    "rich_text": [
                        {
                            "text": {
                                "content": job_description
                            }
                        }
                    ]
                },
                "Language": {
                    "rich_text": [
                        {
                            "text": {
                                "content": language
                            }
                        }
                    ]
                },
                "Model": {
                    "rich_text": [
                        {
                            "text": {
                                "content": model
                            }
                        }
                    ]
                },
                "Location": {
                    "rich_text": [
                        {
                            "text": {
                                "content": location
                            }
                        }
                    ]
                },
                "Role": {
                    "rich_text": [
                        {
                            "text": {
                                "content": role
                            }
                        }
                    ]
                },
                "Salary Expectation": {
                    "number": salary_expectation
                }
            }
        )
        print("Card created successfully:", new_page)
    except Exception as e:
        print(f"Error creating card: {e}")

# Main function to handle the process
def main():
    # Step 1: Read the job description from Notion
    job_description = read_notion_page_content(PAGE_ID)
    
    if not job_description:
        print("Failed to retrieve job description.")
        return

    print("Job Description retrieved:", job_description)

    # Step 2: Extract job details using GPT
    job_info_json = extract_job_info_from_gpt(job_description)
    
    if not job_info_json:
        print("Failed to retrieve job information from GPT.")
        return

    print("Job Information retrieved from GPT:", job_info_json)

    # Step 3: Parse the JSON output from GPT
    try:
        job_info = json.loads(job_info_json)  # Safely parse the JSON response

        # Retrieve the necessary fields
        company_name = job_info.get("Company Name", "Unknown Company")
        job_name = job_info.get("Job Name", "Unknown Job")
        language = job_info.get("Language", "N/A")
        model = job_info.get("Working Model", "N/A")
        location = job_info.get("Location", "N/A")
        role = job_info.get("Role", "N/A")
        short_description = job_info.get("Short Job Description", "")
        salary_expectation = job_info.get("Salary Expectation", 0)

        # Step 4: Create a card on the Notion board
        create_notion_card_on_page(
            database_id=DATABASE_ID,
            company_name=company_name,
            status="Not applied",  # Default status for new cards
            job_name=job_name,
            job_description=short_description,
            language=language,
            model=model,
            location=location,
            role=role,
            salary_expectation=salary_expectation
        )

    except Exception as e:
        print(f"Error parsing job info JSON: {e}")

# Run the main function
if __name__ == "__main__":
    main()
