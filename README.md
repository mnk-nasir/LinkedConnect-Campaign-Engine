# LinkedConnect-Campaign-Engine
# LinkedIn Interactions → Email Campaign (Python)

This project reproduces the logic of your n8n workflow:
- Fetches LinkedIn post commenters & likers (Phantombuster)
- Enriches contacts (Dropcontact)
- Checks and updates/creates records in Airtable
- Adds leads to Lemlist
- Upserts contacts to HubSpot

---

## 🧱 Project Structure

linkedin_campaign_sync.py # main automation script
config.py # loads env vars and handles mock/real mode
requirements.txt # dependencies
.env.example # environment variable template
README.md # this file

yaml
Copy code

---

## 🚀 Quick Start (Mock Mode – No API Keys Required)

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate       # Windows
Install dependencies:

bash
Copy code
pip install -r requirements.txt
Run the script (mock mode auto-enabled since no API keys are set):

bash
Copy code
python linkedin_campaign_sync.py --once
Expected output:
The script will simulate LinkedIn commenters and likers, enrich them with mock data, and log the results.

⚙️ Real Mode (Optional – with API Keys)
If you want to connect real services:

Copy .env.example to .env

bash
Copy code
cp .env.example .env
Fill in all the API keys for Phantombuster, Dropcontact, Airtable, Lemlist, and HubSpot.

Run the script again:

bash
Copy code
python linkedin_campaign_sync.py --once
If all required keys are present, the script will automatically switch to REAL mode.
(Currently, API call placeholders exist — you can extend them to use official REST APIs.)


linkedin_campaign_sync.py # main automation script config.py # loads env vars and handles mock/real mode requirements.txt # dependencies .env.example # environment variable template
