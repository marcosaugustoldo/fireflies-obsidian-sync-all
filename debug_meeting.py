#!/usr/bin/env python3
"""
Debug script to see all available meeting data
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FF_API_KEY")
API_URL = "https://api.fireflies.ai/graphql"

# Query to get full meeting data (without paid fields)
query = """
query Transcripts {
  transcripts(limit: 1) {
    id
    title
    date
    dateString
    duration
    organizer_email
    participants
    fireflies_users
    host_email
    transcript_url
    summary {
      overview
      keywords
      action_items
      outline
      shorthand_bullet
      gist
    }
    sentences {
      text
      speaker_name
      start_time
      end_time
    }
    meeting_attendees {
      displayName
      email
    }
  }
}
"""

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

payload = {
    "query": query,
    "variables": {}
}

print("Fetching meeting data...")
response = requests.post(API_URL, headers=headers, json=payload, timeout=30)

if response.status_code == 200:
    data = response.json()
    if "errors" in data:
        print("Errors:", json.dumps(data["errors"], indent=2))
    else:
        transcripts = data.get("data", {}).get("transcripts", [])
        if transcripts:
            print("\nFull meeting data:")
            print(json.dumps(transcripts[0], indent=2))
        else:
            print("No meetings found")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
