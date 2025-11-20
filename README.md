# Fireflies.ai → Obsidian Sync

Automatically sync meeting transcripts and summaries from Fireflies.ai to your Obsidian vault as beautifully formatted Markdown files.

## Features

- **Automatic daily sync**: Fetches only today's meetings from Fireflies.ai
- **Idempotent operation**: Safe to run multiple times - no duplicates created
- **Rich Markdown output**: Formatted notes with YAML frontmatter
- **Complete meeting data**:
  - Meeting metadata (date, duration, participants, organizer)
  - AI-generated summary with overview and keywords
  - Action items organized by assignee as checkable tasks
  - Full transcript with speaker names and timestamps
  - Direct link to view full meeting on Fireflies
- **Obsidian-optimized**: Clean formatting designed for Obsidian vaults
- **Free plan compatible**: Works with Fireflies free accounts

## Project Structure

```
fireflies_obsidian_sync/
├── sync_fireflies.py                      # Main sync script
├── test_api.py                           # API diagnostic tool
├── debug_meeting.py                      # Meeting data debug tool
├── com.fireflies.obsidian.sync.plist     # launchd configuration template
├── requirements.txt                       # Python dependencies
├── .env                                   # Your API keys (create from .env.example)
├── .env.example                          # Template for environment variables
├── .gitignore                            # Git ignore rules
└── README.md                             # This file

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
- Each time you run the script, it fetches the last 10 meetings and filters for today
- Perfect for automated daily syncing via cron jobs
- Meetings from previous days are not re-fetched

**Note:** If you have more than 10 meetings in a single day, increase the `limit` parameter in `sync_fireflies.py` (line 92).

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

### What Data is Included

**✅ Available with Free Fireflies Plan:**
- Meeting title, date, duration
- Organizer and participant emails
- Full transcript with speaker names and timestamps
- AI-generated summary and overview
- Keywords extracted from discussion
- Action items organized by assignee
- Link to view full meeting on Fireflies.ai

**❌ Requires Paid Fireflies Plan:**
- `audio_url` - Direct audio file download (requires Pro or higher)
- `video_url` - Direct video file download (requires Business or higher)
- Date filtering via API (requires Business or higher)

**Workaround:** The script fetches recent meetings and filters locally, so date filtering still works without a paid plan.

## Automation Options for macOS

Since the script only syncs today's meetings and is idempotent, you can safely schedule it to run multiple times per day to ensure timely syncing.

### Option 1: launchd (Recommended for macOS)

launchd is macOS's native scheduling system and is more reliable than cron. It automatically handles system restarts and provides better logging.

#### Step 1: Create the launchd plist file

**Option A: Copy the included template (easiest)**

```bash
# Create the directory if it doesn't exist
mkdir -p ~/Library/LaunchAgents

# Copy the plist file
cp com.fireflies.obsidian.sync.plist ~/Library/LaunchAgents/
```

**Option B: Create manually**

Create a file at `~/Library/LaunchAgents/com.fireflies.obsidian.sync.plist`:

```bash
nano ~/Library/LaunchAgents/com.fireflies.obsidian.sync.plist
```

Paste this configuration (update paths to match your setup):

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.fireflies.obsidian.sync</string>

    <key>ProgramArguments</key>
    <array>
        <string>/bin/bash</string>
        <string>-c</string>
        <string>cd /Users/ritwik/valeo-projects/fireflies_obsidian_sync && source venv/bin/activate && python3 sync_fireflies.py</string>
    </array>

    <key>StartCalendarInterval</key>
    <array>
        <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>12</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>13</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>14</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>17</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>19</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>12</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>13</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>14</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>17</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>19</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>12</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>13</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>14</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>17</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>19</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>12</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>13</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>14</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>17</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>19</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>10</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>11</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>12</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>13</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>14</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>15</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>16</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>17</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>18</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>19</integer><key>Minute</key><integer>0</integer></dict>
        <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>20</integer><key>Minute</key><integer>0</integer></dict>
    </array>

    <key>StandardOutPath</key>
    <string>/tmp/fireflies_sync.log</string>

    <key>StandardErrorPath</key>
    <string>/tmp/fireflies_sync_error.log</string>

    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
```

**Configuration notes:**
- `Weekday`: 1=Monday, 2=Tuesday, 3=Wednesday, 4=Thursday, 5=Friday
- Runs every hour from 10 AM to 8 PM (10:00-20:00)
- Logs to `/tmp/fireflies_sync.log` and `/tmp/fireflies_sync_error.log`
- Update the path in `ProgramArguments` to match your project location

#### Step 2: Load the launchd job

```bash
# Load the job
launchctl load ~/Library/LaunchAgents/com.fireflies.obsidian.sync.plist

# Start it immediately (optional)
launchctl start com.fireflies.obsidian.sync
```

#### Step 3: Verify it's running

```bash
# Check if loaded
launchctl list | grep fireflies

# View logs
tail -f /tmp/fireflies_sync.log
tail -f /tmp/fireflies_sync_error.log
```

#### Managing the launchd job

```bash
# Stop the job
launchctl stop com.fireflies.obsidian.sync

# Unload (disable) the job
launchctl unload ~/Library/LaunchAgents/com.fireflies.obsidian.sync.plist

# Reload after making changes
launchctl unload ~/Library/LaunchAgents/com.fireflies.obsidian.sync.plist
launchctl load ~/Library/LaunchAgents/com.fireflies.obsidian.sync.plist
```

#### Troubleshooting launchd

```bash
# Check for errors
cat /tmp/fireflies_sync_error.log

# Test the command manually
cd /Users/ritwik/valeo-projects/fireflies_obsidian_sync && source venv/bin/activate && python3 sync_fireflies.py

# Check launchd status
launchctl print gui/$(id -u)/com.fireflies.obsidian.sync
```

**Advantages of launchd over cron:**
- ✅ Automatically reruns if system was asleep
- ✅ Better logging and error handling
- ✅ Survives system reboots
- ✅ Native macOS integration
- ✅ More reliable scheduling

---

### Option 2: Cron (Alternative)

If you prefer cron, here's how to set it up:

#### Edit Your Crontab

```bash
crontab -e
```

#### Add the Cron Job

**Run hourly Mon-Fri from 10 AM to 8 PM:**

```cron
0 10-20 * * 1-5 cd /Users/ritwik/valeo-projects/fireflies_obsidian_sync && source venv/bin/activate && python3 sync_fireflies.py >> /tmp/fireflies_sync.log 2>&1
```

**Breakdown:**
- `0 10-20 * * 1-5`: Every hour at minute 0, from 10 AM to 8 PM, Monday through Friday
- `source venv/bin/activate`: Activates your virtual environment
- `>> /tmp/fireflies_sync.log 2>&1`: Logs all output to `/tmp/fireflies_sync.log`

**Important:** Update the path to match your actual project location.

#### Other Cron Scheduling Options

```cron
# Every 2 hours during work day (Mon-Fri)
0 10,12,14,16,18,20 * * 1-5 cd /path && source venv/bin/activate && python3 sync_fireflies.py >> /tmp/fireflies_sync.log 2>&1

# Twice daily at 10 AM and 6 PM (Mon-Fri)
0 10,18 * * 1-5 cd /path && source venv/bin/activate && python3 sync_fireflies.py >> /tmp/fireflies_sync.log 2>&1

# Once at end of work day at 6 PM (Mon-Fri)
0 18 * * 1-5 cd /path && source venv/bin/activate && python3 sync_fireflies.py >> /tmp/fireflies_sync.log 2>&1

# Every day including weekends at 9 AM
0 9 * * * cd /path && source venv/bin/activate && python3 sync_fireflies.py >> /tmp/fireflies_sync.log 2>&1
```

#### View Cron Logs

```bash
tail -f /tmp/fireflies_sync.log
```

**Note:** Since the script only fetches today's meetings, running it multiple times is safe and efficient.

## Output Format

Each meeting is saved as a Markdown file with:

### YAML Frontmatter

```yaml
---
date: 2025-11-20
datetime: "2025-11-20 16:30 IST"
title: Ritwik / Muhammed
duration: 15m
organizer: ritwik.gupta@feelvaleo.com
fireflies_id: 01KAGATHQKYBR4EQ9X8MCDC16Z
tags:
  - meeting
  - fireflies
type: meeting-note
participants:
  - hafil@feelvaleo.com
  - ritwik.gupta@feelvaleo.com
keywords:
  - Zoho integration
  - Shopify
  - Fulfillment sheet
---
```

### Meeting Details

- Date and time (in IST - Indian Standard Time)
- Duration (in minutes)
- Organizer email
- Participants (email addresses)
- Link to view full meeting on Fireflies.ai

### Summary Section

- AI-generated overview of the meeting
- Keywords extracted from discussion
- Action items organized by assignee (as Obsidian checkboxes)

**Example action items:**
```markdown
**Muhammed Hafil**
- [ ] Share the Fulfillment sheet with Ritwik

**Ritwik Gupta**
- [ ] Review the shared sheets and discuss with team
- [ ] Verify the monthly data extraction process
```

### Full Transcript

- Complete conversation with speaker names
- Timestamps for each statement
- Organized by speaker turns

**Example:**
```markdown
**Ritwik Gupta** `[03:02]`
I just want to understand the complete Zoho work.
Integration, how we have done that.

**Muhammed Hafil** `[03:39]`
So integration and all are done by job.
Basically shopify integration with Zoho.
```

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
- Today's meetings haven't been processed by Fireflies yet (there's typically a delay after the meeting ends)
- Your meetings were on different days

**Note:** The script fetches the last 10 meetings and filters for today's date. If you have more than 10 meetings per day, some may not sync.

### Time Zone

Meeting times are displayed in **IST** (Indian Standard Time, UTC+5:30):
- All times are automatically converted from UTC to IST
- **Example**: Meeting at `11:00 UTC` is displayed as `16:30 IST` (4:30 PM)
- Both YAML frontmatter and meeting details show IST time

**To change to a different timezone:**
- Edit the `IST_OFFSET` constant in `sync_fireflies.py` (line 23)
- For other timezones: `timedelta(hours=X, minutes=Y)`
- Examples:
  - EST (UTC-5): `timedelta(hours=-5)`
  - PST (UTC-8): `timedelta(hours=-8)`
  - JST (UTC+9): `timedelta(hours=9)`

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

### Version 1.3 (2025-11-20)
- **IST timezone support:** All times now displayed in IST (UTC+5:30)
- Meeting times converted from UTC to Indian Standard Time
- Both YAML frontmatter and meeting details show IST
- Configurable timezone offset for other regions
- Updated documentation with timezone examples

### Version 1.2 (2025-11-20)
- **Full data support:** Restored all available meeting data
- Added complete transcript with speaker names and timestamps
- Added action items organized by assignee
- Added comprehensive AI-generated summary with keywords
- Fixed duration parsing (now shows correct duration in minutes)
- Improved participant handling
- Added link to view full meeting on Fireflies
- Works with Fireflies free plan
- Updated cron examples for Mon-Fri 10 AM - 8 PM scheduling
- Added launchd configuration for macOS automation

### Version 1.1 (2025-11-20)
- **Breaking change:** Now fetches only today's meetings (not all meetings)
- Added idempotent operation - safe to run multiple times
- Improved error messages and debugging
- Local date filtering (fetches last 10 meetings, filters for today)
- Removed MAX_MEETINGS and DAYS_LOOKBACK configuration options
- Enhanced documentation with daily sync examples
- Added test_api.py and debug_meeting.py diagnostic tools

### Version 1.0 (2025-11-20)
- Initial release
- GraphQL API integration
- YAML frontmatter support
- Basic meeting metadata
- Duplicate prevention
