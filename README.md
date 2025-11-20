# Fireflies.ai → Obsidian Sync

Automatically sync meeting transcripts and summaries from Fireflies.ai to your Obsidian vault as beautifully formatted Markdown files.

## Features

- **Automatic daily sync**: Fetches only today's meetings from Fireflies.ai
- **Idempotent operation**: Safe to run multiple times - no duplicates created
- **Rich Markdown output**: Formatted notes with YAML frontmatter
- **Complete meeting data**:
  - Meeting metadata (date, duration, participants, organizer)
  - AI-generated summary, keywords, and key points
  - Action items as checkable tasks
  - Full transcript with speaker names and timestamps
  - Links to audio/video recordings
- **Obsidian-optimized**: Clean formatting designed for Obsidian vaults

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
```

**Important:**
- Replace `your_actual_api_key_here` with your real Fireflies API key
- Update the `OBSIDIAN_VAULT_PATH` to point to your Obsidian vault location
- The script automatically fetches only today's meetings

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
2. Fetch meetings that occurred today
3. Create Markdown files for new meetings in your Obsidian vault
4. Skip any meetings that were already synced (no duplicates)
5. Show a summary of what was saved

### 5. Check Your Obsidian Vault

Open Obsidian and navigate to `Fireflies Meetings/` to see your synced meeting notes.

## How It Works

### Daily Sync Behavior

The script is designed to sync **only today's meetings**:
- Each time you run the script, it fetches meetings from the current day
- Perfect for automated daily syncing via cron jobs
- Meetings from previous days are not re-fetched

### Idempotent Operation

The sync is **completely idempotent**:
- Running the script multiple times is safe and will not create duplicates
- If a meeting note already exists, it will be skipped
- You can run the script as often as you like without worrying about data duplication
- Useful if you want to sync multiple times per day to catch meetings as they're processed

**Example:**
```bash
# Run the script at 10 AM - syncs morning meetings
python sync_fireflies.py

# Run again at 5 PM - syncs afternoon meetings
# Morning meetings are skipped (already synced)
python sync_fireflies.py
```

## Automation with Cron (macOS)

Since the script only syncs today's meetings and is idempotent, you can safely schedule it to run multiple times per day to ensure timely syncing.

### Step 1: Make the Script Executable

```bash
chmod +x /path/to/fireflies_obsidian_sync/sync_fireflies.py
```

### Step 2: Edit Your Crontab

```bash
crontab -e
```

### Step 3: Add a Cron Job

**Recommended: Sync every 2 hours during work hours**

```cron
0 9,11,13,15,17 * * * cd /Users/ritwik/valeo-projects/fireflies_obsidian_sync && /usr/bin/python3 sync_fireflies.py >> /tmp/fireflies_sync.log 2>&1
```

**Or sync once at end of day:**

```cron
0 18 * * * cd /Users/ritwik/valeo-projects/fireflies_obsidian_sync && /usr/bin/python3 sync_fireflies.py >> /tmp/fireflies_sync.log 2>&1
```

**Adjust the path** to match your actual project location and Python installation.

### Other Scheduling Options

- Every hour: `0 * * * *` (catches meetings quickly)
- Every 3 hours: `0 */3 * * *` (balanced approach)
- Twice daily (morning and evening): `0 9,17 * * *`
- Once at 6 PM: `0 18 * * *` (end of day sync)

**Note:** Since the script only fetches today's meetings, running it multiple times is safe and efficient.

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

### "No meetings found for today"

This is normal if:
- You have no meetings scheduled for today
- Today's meetings haven't been processed by Fireflies yet (there's typically a delay)
- Your meetings were on different days

**To sync meetings from a different day:**
- The script only syncs today's meetings by design
- Run the script on the day you want to sync meetings for
- Or modify the date range in the script if needed

### Permission denied when running script

Make the script executable:

```bash
chmod +x sync_fireflies.py
```

## Future Improvements

Here are some ideas to enhance this integration:

### ✅ 1. Daily Incremental Sync (Implemented)

**Status:** ✅ Complete
- Script now fetches only today's meetings using date filters
- Idempotent operation prevents duplicates
- Efficient and safe for multiple daily runs

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

### Version 1.1 (2025-11-20)
- **Breaking change:** Now fetches only today's meetings (not all meetings)
- Added idempotent operation - safe to run multiple times
- Improved error messages and debugging
- Added date filtering using fromDate/toDate API parameters
- Removed MAX_MEETINGS and DAYS_LOOKBACK configuration options
- Enhanced documentation with daily sync examples
- Added test_api.py diagnostic tool

### Version 1.0 (2025-11-20)
- Initial release
- GraphQL API integration
- YAML frontmatter support
- Action items as checkboxes
- Transcript with timestamps
- Duplicate prevention
