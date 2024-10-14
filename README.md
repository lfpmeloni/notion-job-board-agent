# notion-job-board-agent

An agent that reads job descriptions from a Notion page, interprets key details using ChatGPT, and automatically creates a new card with the extracted information on a job application board in Notion.

<https://youtu.be/ehR9-pIjtW0>

## Features

- Retrieves job descriptions from a specified Notion page.
- Uses GPT-3.5 to extract details like job title, company name, language requirements, and salary expectations.
- Automatically creates a job card on a specified Notion board.

## Setup Instructions

1. Clone the repository:
   git clone <https://github.com/YOUR_GITHUB_USERNAME/notion-job-board-agent.git>

2. Install the required Python packages:
    pip install -r requirements.txt

3. Create a .env file and add your API keys:
    OPENAI_API_KEY=your_openai_api_key
    NOTION_API_KEY=your_notion_api_key

4. Run the script:
    python card_agent.py

## Contribution

Contributions are welcome! Please create a pull request.
