# Fireflies.ai → Obsidian Sync

Automatically sync meeting transcripts and summaries from Fireflies.ai to your Obsidian vault as beautifully formatted Markdown files.

## Features

- Fetches meetings from Fireflies.ai using the GraphQL API
- Generates Markdown files with rich YAML frontmatter
- Includes meeting metadata: date, duration, participants, organizer
- Extracts summary, keywords, action items, and key points
- Full transcript with speaker names and timestamps
- Links to audio/video recordings
- Skips meetings that already exist (no duplicates)
- Clean, Obsidian-friendly formatting

## Project Structure

```
fireflies_obsidian_sync/
├── sync_fireflies.py      # Main sync script
├── test_api.py           # API diagnostic tool
├── requirements.txt       # Python dependencies
├── .env                   # Your API keys (create from .env.example)
├── .env.example          # Template for environment variables
├── .gitignore            # Git ignore rules
└── README.md             # This file

Obsidian Vault/
└── Valeo Health/
    └── Fireflies Meetings/  # Meeting notes saved here
```

## Prerequisites

- Python 3.8 or higher
- A Fireflies.ai account with API access
- An Obsidian vault

## Setup Instructions

### 1. Get Your Fireflies API Key

1. Log in to [Fireflies.ai](https://app.fireflies.ai/)
2. Navigate to **Integrations** → **Custom Integrations** → **Fireflies API**
3. Click **Generate API Key**
4. Copy your API key (you'll need it in step 3)

### 2. Install Python Dependencies

Open a terminal and navigate to the project directory:

```bash
cd /path/to/fireflies-obsidian-sync
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

Or using pip3:

```bash
pip3 install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Edit the `.env` file with your actual values:

```env
# Fireflies.ai API Configuration
FF_API_KEY=your_actual_api_key_here

# Obsidian Vault Configuration
OBSIDIAN_VAULT_PATH=/Users/ritwik/Documents/Obsidian Vault/Valeo Health
FIREFLIES_SUBFOLDER=Fireflies Meetings

# Optional: Limit the number of meetings to fetch (leave empty for all)
# MAX_MEETINGS=50

# Optional: Only fetch meetings from the last N days (leave empty for all)
# DAYS_LOOKBACK=30
```

**Important:** Replace `your_actual_api_key_here` with your real Fireflies API key.

### 4. Run the Sync Script

Run the script manually:

```bash
python sync_fireflies.py
```

Or using python3:

```bash
python3 sync_fireflies.py
```

The script will:
1. Connect to the Fireflies API
2. Fetch your meetings
3. Create Markdown files in your Obsidian vault
4. Show a summary of what was saved

### 5. Check Your Obsidian Vault

Open Obsidian and navigate to `Fireflies Meetings/` to see your synced meeting notes.

## Automation with Cron (macOS)

To automatically sync meetings every day, you can set up a cron job.

### Step 1: Make the Script Executable

```bash
chmod +x /path/to/fireflies_obsidian_sync/sync_fireflies.py
```

### Step 2: Edit Your Crontab

```bash
crontab -e
```

### Step 3: Add a Cron Job

Add this line to run the sync every day at 9 AM:

```cron
0 9 * * * cd /Users/ritwik/valeo-projects/fireflies_obsidian_sync && /usr/bin/python3 sync_fireflies.py >> /tmp/fireflies_sync.log 2>&1
```

**Adjust the path** to match your actual project location and Python installation.

### Common Cron Schedules

- Every hour: `0 * * * *`
- Every 6 hours: `0 */6 * * *`
- Twice daily (9 AM and 6 PM): `0 9,18 * * *`
- Every Monday at 8 AM: `0 8 * * 1`

### View Cron Logs

Check the sync log:

```bash
tail -f /tmp/fireflies_sync.log
```

## Output Format

Each meeting is saved as a Markdown file with:

### YAML Frontmatter

```yaml
---
date: 2025-01-15
datetime: 2025-01-15 14:30
title: Product Strategy Planning
duration: 45m
organizer: john@company.com
fireflies_id: abc123def456
tags:
  - meeting
  - fireflies
type: meeting-note
participants:
  - John Smith
  - Jane Doe
  - Bob Johnson
keywords:
  - product roadmap
  - Q1 goals
  - feature prioritization
---
```

### Meeting Details

- Date and time
- Duration
- Organizer
- Participants
- Links to audio/video recordings

### Summary Section

- Overview
- Keywords
- Action items (as Obsidian checkboxes)
- Key points

### Full Transcript

- Speaker names
- Timestamps
- Complete conversation

## Troubleshooting

### "FF_API_KEY not set in .env file"

Make sure you've created a `.env` file (not `.env.example`) and added your API key.

### "Obsidian vault path does not exist"

Check that the path in your `.env` file is correct and the folder exists.

### "Failed to fetch meetings from Fireflies API"

- Verify your API key is correct
- Check your internet connection
- Ensure your Fireflies account has API access enabled

### No meetings found

- Log in to Fireflies.ai and verify you have recorded meetings
- Check if you've set `MAX_MEETINGS` or `DAYS_LOOKBACK` too restrictively

### Permission denied when running script

Make the script executable:

```bash
chmod +x sync_fireflies.py
```

## Future Improvements

Here are some ideas to enhance this integration:

### 1. Incremental Sync

**Current:** Fetches all meetings every time
**Enhancement:** Track the last sync timestamp and only fetch new meetings

```python
# Store last sync time in a .last_sync file
# Use date filters in GraphQL query
```

### 2. Separate Summary and Transcript Files

**Current:** Everything in one file
**Enhancement:** Create two linked notes:
- `2025-01-15 - Meeting Summary.md` (overview, action items)
- `2025-01-15 - Meeting Transcript.md` (full transcript)

### 3. Smart Tagging

**Current:** Generic tags (`#meeting`, `#fireflies`)
**Enhancement:** Auto-tag based on:
- Participants (e.g., `#with/john-smith`)
- Keywords (e.g., `#product`, `#engineering`)
- Meeting patterns (e.g., `#standup`, `#one-on-one`)

### 4. Project/Client Backlinks

**Enhancement:** Automatically detect and link to relevant project notes:

```markdown
Related to: [[Project Alpha]], [[Client XYZ]]
```

### 5. Custom Templates

**Enhancement:** Support for user-defined Markdown templates:

```yaml
# template.yaml
sections:
  - summary
  - action_items
  - decisions
  - transcript
```

### 6. Real-time Webhook Sync

**Current:** Manual or cron-based sync
**Enhancement:** Receive webhook notifications from Fireflies when new meetings are processed

### 7. Meeting Analytics

**Enhancement:** Generate daily/weekly reports:
- Total meeting time
- Most active participants
- Common topics
- Action item tracking

### 8. Selective Sync

**Enhancement:** Configure which meetings to sync:

```yaml
sync_filters:
  include_participants: ["john@company.com"]
  exclude_titles: ["Test Meeting"]
  min_duration: 300  # Only meetings > 5 minutes
```

### 9. Bi-directional Sync

**Enhancement:** Update action items in Fireflies when checked off in Obsidian

### 10. Integration with Obsidian Daily Notes

**Enhancement:** Automatically link meetings to your daily note:

```markdown
# 2025-01-15

## Meetings
- [[2025-01-15 - Product Strategy Planning]]
- [[2025-01-15 - Team Standup]]
```

## Contributing

Feel free to fork and enhance this script! Some areas for contribution:

- Add error recovery and retry logic
- Implement the future improvements above
- Add support for custom Markdown templates
- Create a GUI for easier configuration
- Add unit tests

## License

MIT License - feel free to use and modify as needed.

## Support

For issues with:
- **This script:** Check the troubleshooting section above
- **Fireflies API:** Visit [Fireflies API Documentation](https://docs.fireflies.ai/)
- **Obsidian:** Visit [Obsidian Help](https://help.obsidian.md/)

## Changelog

### Version 1.0 (2025-11-20)
- Initial release
- GraphQL API integration
- YAML frontmatter support
- Action items as checkboxes
- Transcript with timestamps
- Duplicate prevention
