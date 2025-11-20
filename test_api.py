#!/usr/bin/env python3
"""
Test script to diagnose Fireflies API connection issues.
"""

import os
import sys
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FF_API_KEY")
API_URL = "https://api.fireflies.ai/graphql"

if not API_KEY:
    print("❌ FF_API_KEY not set in .env file")
    sys.exit(1)

print("Testing Fireflies API connection...")
print(f"API Key: {API_KEY[:10]}...{API_KEY[-4:]}")
print()

# Test 1: Minimal query (just id and title)
print("=" * 60)
print("Test 1: Minimal query (id and title only)")
print("=" * 60)

query1 = """
query Transcripts {
  transcripts(limit: 1) {
    id
    title
  }
}
"""

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

payload1 = {
    "query": query1,
    "variables": {}
}

try:
    response = requests.post(API_URL, headers=headers, json=payload1, timeout=30)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            print(f"❌ GraphQL Errors: {data['errors']}")
        elif "data" in data and data["data"].get("transcripts"):
            transcripts = data["data"]["transcripts"]
            print(f"✅ Success! Found {len(transcripts)} transcript(s)")
            if transcripts:
                print(f"   First transcript: {transcripts[0].get('title', 'No title')}")
        else:
            print(f"⚠️  Empty or unexpected response: {data}")
    else:
        print(f"❌ Failed with status {response.status_code}")
        print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"❌ Exception: {e}")

print()

# Test 2: Add more fields incrementally
print("=" * 60)
print("Test 2: Adding date, duration, and organizer_email")
print("=" * 60)

query2 = """
query Transcripts {
  transcripts(limit: 1) {
    id
    title
    date
    duration
    organizer_email
  }
}
"""

payload2 = {
    "query": query2,
    "variables": {}
}

try:
    response = requests.post(API_URL, headers=headers, json=payload2, timeout=30)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            print(f"❌ GraphQL Errors: {data['errors']}")
        elif "data" in data:
            print(f"✅ Success!")
        else:
            print(f"⚠️  Unexpected response: {data}")
    else:
        print(f"❌ Failed with status {response.status_code}")
        print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"❌ Exception: {e}")

print()

# Test 3: Try adding summary fields
print("=" * 60)
print("Test 3: Adding summary fields")
print("=" * 60)

query3 = """
query Transcripts {
  transcripts(limit: 1) {
    id
    title
    date
    summary {
      overview
      keywords
    }
  }
}
"""

payload3 = {
    "query": query3,
    "variables": {}
}

try:
    response = requests.post(API_URL, headers=headers, json=payload3, timeout=30)
    print(f"Status Code: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        if "errors" in data:
            print(f"❌ GraphQL Errors: {data['errors']}")
        elif "data" in data:
            print(f"✅ Success!")
            transcripts = data.get("data", {}).get("transcripts", [])
            if transcripts and transcripts[0].get("summary"):
                print(f"   Has summary: Yes")
        else:
            print(f"⚠️  Unexpected response: {data}")
    else:
        print(f"❌ Failed with status {response.status_code}")
        print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"❌ Exception: {e}")

print()
print("=" * 60)
print("Diagnostic complete!")
print("=" * 60)
