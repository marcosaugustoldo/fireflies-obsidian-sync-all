#!/usr/bin/env python3
"""
Fireflies.ai to Obsidian Sync Script
Fetches meeting transcripts from Fireflies.ai and saves them as Markdown files in Obsidian.
"""

import os
import sys
import json
from datetime import datetime, time, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv


class FirefliesObsidianSync:
    """Synchronize Fireflies meetings to Obsidian vault."""

    FIREFLIES_API_URL = "https://api.fireflies.ai/graphql"

    # IST timezone offset: UTC+5:30
    IST_OFFSET = timedelta(hours=5, minutes=30)

    def __init__(self):
        """Initialize the sync service with environment variables."""
        load_dotenv()

        self.api_key = os.getenv("FF_API_KEY")
        self.vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
        self.subfolder = os.getenv("FIREFLIES_SUBFOLDER", "Fireflies Meetings")

        self._validate_config()

        # Create full path to notes folder
        self.notes_path = Path(self.vault_path) / self.subfolder
        self.notes_path.mkdir(parents=True, exist_ok=True)

    def _validate_config(self):
        """Validate required configuration."""
        if not self.api_key:
            raise ValueError("FF_API_KEY not set in .env file")
        if not self.vault_path:
            raise ValueError("OBSIDIAN_VAULT_PATH not set in .env file")
        if not Path(self.vault_path).exists():
            raise ValueError(f"Obsidian vault path does not exist: {self.vault_path}")

    def fetch_meetings(self) -> List[Dict]:
        """Fetch recent meetings from Fireflies API using GraphQL.

        Fetches recent meetings and filters for today's meetings locally.
        Note: Date filtering (fromDate/toDate) requires a Business plan.
        """
        # Calculate today's date range for local filtering
        now = datetime.now(timezone.utc)
        today_start = datetime.combine(now.date(), time.min, tzinfo=timezone.utc)
        today_end = datetime.combine(now.date(), time.max, tzinfo=timezone.utc)

        # GraphQL query to fetch recent transcripts (no date filtering)
        # Fetch last 10 meetings and filter for today locally
        # Note: audio_url and video_url require paid plans
        query = """
        query Transcripts($limit: Int) {
          transcripts(limit: $limit) {
            id
            title
            date
            dateString
            duration
            organizer_email
            participants
            meeting_attendees {
              displayName
              email
            }
            summary {
              overview
              keywords
              action_items
              outline
              gist
            }
            sentences {
              text
              speaker_name
              start_time
              end_time
            }
            transcript_url
          }
        }
        """

        variables = {
            "limit": 10  # Fetch last 10 meetings
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "query": query,
            "variables": variables
        }

        try:
            print(f"Fetching recent meetings from Fireflies API...")
            print(f"  → Looking for meetings from: {today_start.strftime('%Y-%m-%d')} (UTC)")
            print(f"  → Note: Fetching last 10 meetings and filtering locally")

            response = requests.post(
                self.FIREFLIES_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )

            # Check if we got a response
            if response.status_code != 200:
                print(f"\nAPI returned status code {response.status_code}")
                print(f"Response body: {response.text[:500]}")

                # Try to parse error details from response
                try:
                    error_data = response.json()
                    if "errors" in error_data:
                        errors = error_data["errors"]
                        for err in errors:
                            error_code = err.get("code", "")
                            error_msg = err.get("message", "")

                            # Check for authentication errors
                            if error_code == "auth_failed" or "authenticat" in error_msg.lower():
                                raise Exception(
                                    f"Authentication failed: {error_msg}\n"
                                    f"  → Your FF_API_KEY is invalid or expired\n"
                                    f"  → Get a new key at: https://app.fireflies.ai/integrations/custom/fireflies\n"
                                    f"  → Update the FF_API_KEY in your .env file"
                                )
                except:
                    pass

                response.raise_for_status()

            data = response.json()

            # Check for GraphQL errors
            if "errors" in data:
                error_msgs = [err.get("message", str(err)) for err in data["errors"]]
                raise Exception(f"GraphQL errors: {', '.join(error_msgs)}")

            # Check if data exists
            if "data" not in data:
                raise Exception(f"No 'data' field in response: {data}")

            all_transcripts = data.get("data", {}).get("transcripts", [])

            if all_transcripts is None:
                print(f"\nWarning: transcripts field is None. Full response: {data}")
                all_transcripts = []

            print(f"Fetched {len(all_transcripts)} recent meetings")

            # Filter for today's meetings only
            today_transcripts = []
            for transcript in all_transcripts:
                try:
                    # Parse the meeting date (can be Unix timestamp or ISO string)
                    date_value = transcript['date']

                    if isinstance(date_value, (int, float)):
                        # Unix timestamp (milliseconds)
                        meeting_date = datetime.fromtimestamp(date_value / 1000, tz=timezone.utc)
                    else:
                        # ISO string format
                        meeting_date = datetime.fromisoformat(date_value.replace('Z', '+00:00'))

                    # Check if meeting is from today
                    if today_start <= meeting_date <= today_end:
                        today_transcripts.append(transcript)
                        print(f"  > Found today's meeting: {transcript.get('title', 'Unknown')}")
                except Exception as e:
                    print(f"  > Warning: Could not parse date for meeting {transcript.get('title', 'Unknown')}: {e}")
                    continue

            print(f"Found {len(today_transcripts)} meeting(s) from today")
            return today_transcripts

        except requests.exceptions.HTTPError as e:
            # Provide more detailed error information
            error_msg = f"HTTP {e.response.status_code} error from Fireflies API"
            if e.response.status_code == 401:
                error_msg += "\n  → Check that your FF_API_KEY is correct"
            elif e.response.status_code == 500:
                error_msg += "\n  → Server error. The API may be temporarily unavailable or the query may be invalid"
                error_msg += f"\n  → Try running 'python test_api.py' to diagnose the issue"
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch meetings from Fireflies API: {e}")

    def _format_duration(self, duration_value) -> str:
        """Convert duration to human-readable format.

        Args:
            duration_value: Can be seconds (int) or minutes (float)
        """
        if not duration_value:
            return "Unknown"

        # If it's a float, it's likely in minutes (based on API response)
        if isinstance(duration_value, float):
            minutes = int(duration_value)
            if minutes >= 60:
                hours = minutes // 60
                mins = minutes % 60
                return f"{hours}h {mins}m"
            return f"{minutes}m"

        # If it's an int, treat as seconds
        hours = duration_value // 3600
        minutes = (duration_value % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to MM:SS timestamp."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def _sanitize_filename(self, title: str, date) -> str:
        """Create a safe filename from meeting title and date."""
        # Parse the date (can be Unix timestamp or ISO string) and convert to IST
        try:
            if isinstance(date, (int, float)):
                dt_utc = datetime.fromtimestamp(date / 1000, tz=timezone.utc)
            else:
                dt_utc = datetime.fromisoformat(date.replace('Z', '+00:00'))

            # Convert to IST for the filename date
            dt_ist = dt_utc + self.IST_OFFSET
            date_str = dt_ist.strftime("%Y-%m-%d")
        except:
            date_str = "unknown-date"

        # Sanitize title
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title[:50]  # Limit length

        if not safe_title:
            safe_title = "Meeting"

        return f"{date_str} - {safe_title}.md"

    def _generate_markdown(self, meeting: Dict) -> str:
        """Generate Markdown content with YAML frontmatter for a meeting."""
        # Parse date (can be Unix timestamp or ISO string) and convert to IST
        try:
            date_value = meeting['date']
            if isinstance(date_value, (int, float)):
                dt_utc = datetime.fromtimestamp(date_value / 1000, tz=timezone.utc)
            else:
                dt_utc = datetime.fromisoformat(date_value.replace('Z', '+00:00'))

            # Convert UTC to IST
            dt_ist = dt_utc + self.IST_OFFSET

            # Format: "20 November 2025"
            date_formatted = dt_ist.strftime("%d %B %Y")
            # Format: "16:30 IST" (time only)
            time_formatted = dt_ist.strftime("%H:%M IST")
            # Full datetime for Meeting Details section
            datetime_formatted = dt_ist.strftime("%d %B %Y %H:%M IST")
        except:
            date_formatted = "Unknown"
            time_formatted = "Unknown"
            datetime_formatted = "Unknown"

        # Extract participants
        participants = []
        if meeting.get('meeting_attendees'):
            for attendee in meeting['meeting_attendees']:
                name = attendee.get('displayName') or attendee.get('email') or 'Unknown'
                if name and name != 'Unknown':
                    participants.append(name)
        elif meeting.get('participants'):
            # Fallback to participants list (emails)
            for participant in meeting['participants']:
                if participant:
                    participants.append(participant)

        # Build YAML frontmatter
        frontmatter = {
            'date': date_formatted,
            'Start Time': time_formatted,
            'title': meeting.get('title', 'Untitled Meeting'),
            'duration': self._format_duration(meeting.get('duration', 0)),
            'organizer': meeting.get('organizer_email', 'Unknown'),
            'fireflies_id': meeting['id'],
            'tags': ['meeting', 'fireflies'],
            'type': 'meeting-note'
        }

        # Add optional fields
        if participants:
            frontmatter['participants'] = participants

        summary = meeting.get('summary', {})
        if summary and summary.get('keywords'):
            frontmatter['keywords'] = summary['keywords']

        # Start building markdown
        md_lines = ["---"]

        # Write frontmatter
        for key, value in frontmatter.items():
            if isinstance(value, list):
                md_lines.append(f"{key}:")
                for item in value:
                    md_lines.append(f"  - {item}")
            else:
                # Escape quotes in strings
                if isinstance(value, str) and ('"' in value or ':' in value):
                    value = f'"{value}"'
                md_lines.append(f"{key}: {value}")

        md_lines.append("---")
        md_lines.append("")

        # Add title
        md_lines.append(f"# {meeting.get('title', 'Untitled Meeting')}")
        md_lines.append("")

        # Add metadata section
        md_lines.append("## Meeting Details")
        md_lines.append("")
        md_lines.append(f"- **Date:** {datetime_formatted}")
        md_lines.append(f"- **Duration:** {self._format_duration(meeting.get('duration', 0))}")
        md_lines.append(f"- **Organizer:** {meeting.get('organizer_email', 'Unknown')}")

        if participants:
            md_lines.append(f"- **Participants:** {', '.join(participants)}")

        # Add transcript link if available
        if meeting.get('transcript_url'):
            md_lines.append(f"- **Transcript:** [View on Fireflies]({meeting['transcript_url']})")

        md_lines.append("")

        # Add summary section
        if summary:
            md_lines.append("## Summary")
            md_lines.append("")

            if summary.get('overview'):
                md_lines.append(summary['overview'])
                md_lines.append("")

            if summary.get('keywords'):
                md_lines.append("**Keywords:** " + ", ".join(summary['keywords']))
                md_lines.append("")

            if summary.get('action_items'):
                md_lines.append("### Action Items")
                md_lines.append("")
                # Action items is a string with newlines, parse it
                action_items_text = summary['action_items']
                if isinstance(action_items_text, str):
                    # Split by double newlines to get sections
                    lines = action_items_text.strip().split('\n')
                    for line in lines:
                        line = line.strip()
                        if line and not line.startswith('**'):
                            # Skip header lines with **Name**
                            if line and line[0].isalpha():
                                md_lines.append(f"- [ ] {line}")
                        elif line.startswith('**'):
                            # Add name headers as bold text
                            md_lines.append(f"\n{line}")
                else:
                    # If it's a list (old format)
                    for item in action_items_text:
                        md_lines.append(f"- [ ] {item}")
                md_lines.append("")

            if summary.get('outline'):
                md_lines.append("### Key Points")
                md_lines.append("")
                for point in summary['outline']:
                    md_lines.append(f"- {point}")
                md_lines.append("")

        # Add transcript section
        if meeting.get('sentences'):
            md_lines.append("## Transcript")
            md_lines.append("")

            current_speaker = None
            speaker_sentences = []
            first_timestamp = None

            for sentence in meeting['sentences']:
                speaker = sentence.get('speaker_name', 'Unknown')
                text = sentence.get('text', '').strip()
                timestamp = self._format_timestamp(sentence.get('start_time', 0))

                # If speaker changes, output previous speaker's text
                if speaker != current_speaker:
                    # Output accumulated sentences from previous speaker
                    if current_speaker is not None and speaker_sentences:
                        md_lines.append(f"**{current_speaker}** `[{first_timestamp}]`")
                        md_lines.append("")
                        md_lines.append(" ".join(speaker_sentences))
                        md_lines.append("")  # Blank line between speakers
                        speaker_sentences = []

                    current_speaker = speaker
                    first_timestamp = timestamp

                # Accumulate sentences for current speaker
                if text:
                    speaker_sentences.append(text)

            # Don't forget to output the last speaker's sentences
            if current_speaker is not None and speaker_sentences:
                md_lines.append(f"**{current_speaker}** `[{first_timestamp}]`")
                md_lines.append("")
                md_lines.append(" ".join(speaker_sentences))

        md_lines.append("")
        md_lines.append("---")
        md_lines.append("*Synced from Fireflies.ai*")

        return "\n".join(md_lines)

    def save_meeting(self, meeting: Dict) -> bool:
        """Save a meeting as a Markdown file. Returns True if saved, False if skipped.

        This method is idempotent - it will not overwrite existing meeting files.
        If a file with the same name already exists, it will be skipped.
        """
        filename = self._sanitize_filename(
            meeting.get('title', 'Untitled'),
            meeting.get('date', '')
        )
        filepath = self.notes_path / filename

        # Skip if file already exists (idempotent behavior)
        if filepath.exists():
            print(f"  [SKIP] Already synced: {filename}")
            return False

        # Generate and save markdown
        markdown_content = self._generate_markdown(meeting)

        try:
            filepath.write_text(markdown_content, encoding='utf-8')
            print(f"  [SAVED] {filename}")
            return True
        except Exception as e:
            print(f"  [ERROR] Failed to save {filename}: {e}")
            return False

    def sync(self):
        """Main sync process.

        Fetches today's meetings from Fireflies and syncs them to Obsidian.
        This operation is idempotent - running multiple times will not create duplicates.
        """
        today = datetime.now().strftime("%Y-%m-%d")

        print("=" * 60)
        print("Fireflies.ai -> Obsidian Sync")
        print("=" * 60)
        print(f"Syncing meetings for: {today}")
        print()

        try:
            # Fetch meetings
            meetings = self.fetch_meetings()

            if not meetings:
                print("No meetings found for today.")
                print()
                print("This is normal if:")
                print("  - You have no meetings scheduled today")
                print("  - Your meetings haven't been processed by Fireflies yet")
                return

            print()
            print(f"Processing {len(meetings)} meeting(s)...")
            print()

            # Save each meeting
            saved_count = 0
            skipped_count = 0

            for meeting in meetings:
                if self.save_meeting(meeting):
                    saved_count += 1
                else:
                    skipped_count += 1

            # Summary
            print()
            print("=" * 60)
            print(f"Sync complete!")
            print(f"  - New meetings: {saved_count}")
            print(f"  - Already synced: {skipped_count}")
            print(f"  - Location: {self.notes_path}")
            print("=" * 60)

        except Exception as e:
            print(f"\nError during sync: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main entry point."""
    try:
        sync_service = FirefliesObsidianSync()
        sync_service.sync()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
