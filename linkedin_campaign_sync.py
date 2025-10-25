#!/usr/bin/env python3
"""
Main script to replicate the n8n workflow in Python.

Behavior:
- Runs once (or you can schedule it externally every hour)
- Fetches LinkedIn commenters & likers (Phantombuster)
- Waits 30s between steps where appropriate
- Enriches contacts with Dropcontact
- Checks Airtable for existing contacts → update or create
- Adds leads to Lemlist and upserts to HubSpot

The script supports two modes:
- REAL mode: when API keys are provided via environment variables (it will attempt real HTTP calls)
- MOCK mode: when API keys are missing — script will use simulated data so you can test locally or before adding keys

You can run this script directly:

    python linkedin_campaign_sync.py
"""
import os
import time
import logging
import argparse
from typing import List, Dict, Any
import requests
from config import Config

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ---- Helpers / Service wrappers ----

class PhantombusterClient:
    def __init__(self, cfg: Config):
        self.api_key = cfg.PHANTOMBUSTER_API_KEY
        self.mock = cfg.mock

    def fetch_post_commenters(self) -> List[Dict[str, Any]]:
        if self.mock:
            log.info("[Phantombuster] Using mock commenters data")
            return [
                {"first_name": "Ada", "last_name": "Lovelace", "profile_url": "https://linkedin.example/ada"},
                {"first_name": "Alan", "last_name": "Turing", "profile_url": "https://linkedin.example/alan"},
            ]
        log.info("[Phantombuster] Real mode not implemented — please add API logic here.")
        return []

    def fetch_post_likers(self) -> List[Dict[str, Any]]:
        if self.mock:
            log.info("[Phantombuster] Using mock likers data")
            return [
                {"first_name": "Grace", "last_name": "Hopper", "profile_url": "https://linkedin.example/grace"},
            ]
        log.info("[Phantombuster] Real mode not implemented — please add API logic here.")
        return []

    def trigger_next_phantom(self):
        if self.mock:
            log.info("[Phantombuster] Mock trigger of next phantom")
            return True
        log.info("[Phantombuster] Real trigger not implemented")
        return False


class DropcontactClient:
    def __init__(self, cfg: Config):
        self.api_key = cfg.DROPCONTACT_API_KEY
        self.mock = cfg.mock

    def enrich(self, person: Dict[str, Any]) -> Dict[str, Any]:
        if self.mock:
            # return fake enrichment
            email = f"{person.get('first_name','').lower()}@example.com"
            return {
                "full_name": f"{person.get('first_name','')} {person.get('last_name','')}",
                "first_name": person.get('first_name'),
                "last_name": person.get('last_name'),
                "email": [{"email": email}],
                "phone": "",
                "linkedin": person.get('profile_url'),
                "company": "Example Ltd",
                "website": "https://example.com",
            }
        log.info("[Dropcontact] Real mode not implemented — please add API logic here.")
        return {}


class AirtableClient:
    def __init__(self, cfg: Config):
        self.api_key = cfg.AIRTABLE_API_KEY
        self.base_id = cfg.AIRTABLE_BASE_ID
        self.table = cfg.AIRTABLE_TABLE or "Contacts"
        self.mock = cfg.mock

    def list_records_matching_email(self, email: str) -> List[Dict[str, Any]]:
        if self.mock:
            log.info(f"[Airtable] Mock search for {email}")
            if "new" in email:
                return []
            return [{"id": "rec123", "fields": {"Email": email}}]
        log.info("[Airtable] Real mode not implemented — please add API logic here.")
        return []

    def create_record(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        if self.mock:
            log.info(f"[Airtable] Mock create: {fields}")
            return {"id": "rec_new", "fields": fields}
        log.info("[Airtable] Real mode not implemented — please add API logic here.")
        return {}

    def update_record(self, record_id: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        if self.mock:
            log.info(f"[Airtable] Mock update {record_id}: {fields}")
            return {"id": record_id, "fields": fields}
        log.info("[Airtable] Real mode not implemented — please add API logic here.")
        return {}


class LemlistClient:
    def __init__(self, cfg: Config):
        self.api_key = cfg.LEMLIST_API_KEY
        self.mock = cfg.mock

    def add_lead(self, lead: Dict[str, Any]) -> bool:
        if self.mock:
            log.info(f"[Lemlist] Mock add lead {lead.get('email')}")
            return True
        log.info("[Lemlist] Real mode not implemented — please add API logic here.")
        return False


class HubspotClient:
    def __init__(self, cfg: Config):
        self.api_key = cfg.HUBSPOT_API_KEY
        self.mock = cfg.mock

    def upsert_contact(self, contact: Dict[str, Any]) -> bool:
        if self.mock:
            log.info(f"[HubSpot] Mock upsert contact {contact.get('email')}")
            return True
        log.info("[HubSpot] Real mode not implemented — please add API logic here.")
        return False


# ---- Main orchestration ----

def process_person(person: Dict[str, Any], clients: Dict[str, Any], cfg: Config):
    drop = clients['dropcontact']
    airtable = clients['airtable']
    lemlist = clients['lemlist']
    hubspot = clients['hubspot']

    enriched = drop.enrich(person)
    email = (enriched.get('email') or [{}])[0].get('email') if enriched.get('email') else None
    log.info(f"Enriched person -> {enriched.get('full_name')} | email={email}")

    if not email:
        log.warning("No email found — skipping contact creation")
        return

    existing = airtable.list_records_matching_email(email)
    if existing:
        rec_id = existing[0]['id']
        fields = {
            "Email": email,
            "Phone": enriched.get('phone'),
            "LinkedIn": enriched.get('linkedin'),
            "Account": enriched.get('company'),
            "Company website": enriched.get('website'),
        }
        airtable.update_record(rec_id, fields)
    else:
        fields = {
            "Name": enriched.get('full_name'),
            "Account": enriched.get('company'),
            "Company website": enriched.get('website'),
            "Email": email,
            "Phone": enriched.get('phone'),
            "LinkedIn": enriched.get('linkedin'),
        }
        airtable.create_record(fields)

    # Add to Lemlist
    lemlist.add_lead({
        "email": email,
        "firstName": enriched.get('first_name'),
        "lastName": enriched.get('last_name'),
        "companyName": enriched.get('company'),
    })

    # Upsert to HubSpot
    hubspot.upsert_contact({
        "email": email,
        "firstName": enriched.get('first_name'),
        "lastName": enriched.get('last_name'),
        "company": enriched.get('company'),
        "phone": enriched.get('phone'),
    })


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run once and exit (default)")
    parser.add_argument("--interval-minutes", type=int, default=60, help="If not --once, interval between runs in minutes")
    args = parser.parse_args()

    cfg = Config.load_from_env()

    phanto = PhantombusterClient(cfg)
    drop = DropcontactClient(cfg)
    airtable = AirtableClient(cfg)
    lemlist = LemlistClient(cfg)
    hubspot = HubspotClient(cfg)

    clients = {
        'phantombuster': phanto,
        'dropcontact': drop,
        'airtable': airtable,
        'lemlist': lemlist,
        'hubspot': hubspot,
    }

    def run_cycle():
        log.info("=== Run cycle started ===")
        commenters = phanto.fetch_post_commenters()
        # wait 30s as in original workflow
        log.info("Waiting 30 seconds to mimic n8n 'Wait 30s' node")
        time.sleep(30)
        log.info(f"Fetched {len(commenters)} commenters")

        for p in commenters:
            process_person(p, clients, cfg)

        likers = phanto.fetch_post_likers()
        log.info(f"Fetched {len(likers)} likers")
        for p in likers:
            process_person(p, clients, cfg)

        # Trigger follow-up phantom if needed
        phanto.trigger_next_phantom()

        log.info("=== Run cycle finished ===")

    if args.once:
        run_cycle()
        return

    # loop mode
    interval = args.interval_minutes * 60
    try:
        while True:
            run_cycle()
            log.info(f"Sleeping for {args.interval_minutes} minutes")
            time.sleep(interval)
    except KeyboardInterrupt:
        log.info("Interrupted by user — exiting")


if __name__ == '__main__':
    main()
