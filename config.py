"""
Configuration loader.
Loads API keys and settings from environment variables.
If no API keys are found, the script runs in MOCK mode.
"""

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load variables from a .env file if present
load_dotenv()


@dataclass
class Config:
    # API keys (optional)
    PHANTOMBUSTER_API_KEY: str
    DROPCONTACT_API_KEY: str
    AIRTABLE_API_KEY: str
    AIRTABLE_BASE_ID: str
    AIRTABLE_TABLE: str
    LEMLIST_API_KEY: str
    HUBSPOT_API_KEY: str

    # Behavior
    mock: bool

    @staticmethod
    def load_from_env() -> "Config":
        """Load configuration from environment variables."""
        ph = os.getenv("PHANTOMBUSTER_API_KEY", "")
        dc = os.getenv("DROPCONTACT_API_KEY", "")
        at = os.getenv("AIRTABLE_API_KEY", "")
        at_base = os.getenv("AIRTABLE_BASE_ID", "")
        at_table = os.getenv("AIRTABLE_TABLE", "Contacts")
        le = os.getenv("LEMLIST_API_KEY", "")
        hs = os.getenv("HUBSPOT_API_KEY", "")

        # Mock mode if any major key is missing
        mock = not (ph and dc and at and at_base and le and hs)

        return Config(
            PHANTOMBUSTER_API_KEY=ph,
            DROPCONTACT_API_KEY=dc,
            AIRTABLE_API_KEY=at,
            AIRTABLE_BASE_ID=at_base,
            AIRTABLE_TABLE=at_table,
            LEMLIST_API_KEY=le,
            HUBSPOT_API_KEY=hs,
            mock=mock,
        )
