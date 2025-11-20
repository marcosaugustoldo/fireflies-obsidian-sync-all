#!/usr/bin/env python3
"""
Fireflies.ai to Obsidian Sync Script
Fetches meeting transcripts from Fireflies.ai and saves them as Markdown files in Obsidian.
"""

import os
import sys
import json
from datetime import datetime, time, timezone
from pathlib import Path
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv


class FirefliesObsidianSync:
    """Synchronize Fireflies meetings to Obsidian vault."""

    FIREFLIES_API_URL = "https://api.fireflies.ai/graphql"

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
        """Fetch meetings from Fireflies API using GraphQL.

        Fetches only meetings that occurred today (based on local timezone).
        """
        # Calculate today's date range in ISO 8601 format
        # Get start of today (00:00:00) in UTC
        now = datetime.now(timezone.utc)
        today_start = datetime.combine(now.date(), time.min, tzinfo=timezone.utc)
        today_end = datetime.combine(now.date(), time.max, tzinfo=timezone.utc)

        # Format as ISO 8601 strings
        from_date = today_start.isoformat()
        to_date = today_end.isoformat()

        # GraphQL query to fetch transcripts with date filtering
        query = """
        query Transcripts($fromDate: String, $toDate: String) {
          transcripts(fromDate: $fromDate, toDate: $toDate) {
            id
            title
            date
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
            }
            sentences {
              text
              speaker_name
              start_time
            }
            audio_url
            video_url
          }
        }
        """

        variables = {
            "fromDate": from_date,
            "toDate": to_date
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
            print(f"Fetching today's meetings from Fireflies API...")
            print(f"  → Date range: {today_start.strftime('%Y-%m-%d')} (UTC)")

            response = requests.post(
                self.FIREFLIES_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )

            # Check if we got a response
            if response.status_code != 200:
                print(f"\n❌ API returned status code {response.status_code}")
                print(f"Response body: {response.text[:500]}")
                response.raise_for_status()

            data = response.json()

            # Check for GraphQL errors
            if "errors" in data:
                error_msgs = [err.get("message", str(err)) for err in data["errors"]]
                raise Exception(f"GraphQL errors: {', '.join(error_msgs)}")

            # Check if data exists
            if "data" not in data:
                raise Exception(f"No 'data' field in response: {data}")

            transcripts = data.get("data", {}).get("transcripts", [])

            if transcripts is None:
                print(f"\n⚠️  Warning: transcripts field is None. Full response: {data}")
                transcripts = []

            print(f"Successfully fetched {len(transcripts)} meetings")
            return transcripts

        except requests.exceptions.HTTPError as e:
            # Provide more detailed error information
            error_msg = f"HTTP {e.response.status_code} error from Fireflies API"
            if e.response.status_code == 401:
                error_msg += "\n  → Check that your FF_API_KEY is correct"
            elif e.response.status_code == 500:
                error_msg += "\n  → Server error. The API may be temporarily unavailable or the query may be invalid"
                error_msg += f"\n  → The script only fetches today's meetings. Check if you have meetings scheduled for today."
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to fetch meetings from Fireflies API: {e}")

    def _format_duration(self, seconds: int) -> str:
        """Convert duration in seconds to human-readable format."""
        if not seconds:
            return "Unknown"

        hours = seconds // 3600
        minutes = (seconds % 3600) // 60

        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"

    def _format_timestamp(self, seconds: float) -> str:
        """Convert seconds to MM:SS timestamp."""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def _sanitize_filename(self, title: str, date: str) -> str:
        """Create a safe filename from meeting title and date."""
        # Parse the date
        try:
            dt = datetime.fromisoformat(date.replace('Z', '+00:00'))
            date_str = dt.strftime("%Y-%m-%d")
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
        # Parse date
        try:
            dt = datetime.fromisoformat(meeting['date'].replace('Z', '+00:00'))
            date_formatted = dt.strftime("%Y-%m-%d")
            datetime_formatted = dt.strftime("%Y-%m-%d %H:%M")
        except:
            date_formatted = "Unknown"
            datetime_formatted = "Unknown"

        # Extract participants
        participants = []
        if meeting.get('meeting_attendees'):
            for attendee in meeting['meeting_attendees']:
                name = attendee.get('displayName', attendee.get('email', 'Unknown'))
                participants.append(name)

        # Build YAML frontmatter
        frontmatter = {
            'date': date_formatted,
            'datetime': datetime_formatted,
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

        # Add audio/video links if available
        if meeting.get('audio_url'):
            md_lines.append(f"- **Audio Recording:** [Listen]({meeting['audio_url']})")
        if meeting.get('video_url'):
            md_lines.append(f"- **Video Recording:** [Watch]({meeting['video_url']})")

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
                for item in summary['action_items']:
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
            for sentence in meeting['sentences']:
                speaker = sentence.get('speaker_name', 'Unknown')
                text = sentence.get('text', '')
                timestamp = self._format_timestamp(sentence.get('start_time', 0))

                # Add speaker header if speaker changes
                if speaker != current_speaker:
                    if current_speaker is not None:
                        md_lines.append("")  # Add spacing between speakers
                    md_lines.append(f"**{speaker}** `[{timestamp}]`")
                    current_speaker = speaker

                md_lines.append(text)

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
            print(f"  ⏭️  Already synced: {filename}")
            return False

        # Generate and save markdown
        markdown_content = self._generate_markdown(meeting)

        try:
            filepath.write_text(markdown_content, encoding='utf-8')
            print(f"  ✅ Saved: {filename}")
            return True
        except Exception as e:
            print(f"  ❌ Failed to save {filename}: {e}")
            return False

    def sync(self):
        """Main sync process.

        Fetches today's meetings from Fireflies and syncs them to Obsidian.
        This operation is idempotent - running multiple times will not create duplicates.
        """
        today = datetime.now().strftime("%Y-%m-%d")

        print("=" * 60)
        print("Fireflies.ai → Obsidian Sync")
        print("=" * 60)
        print(f"📅 Syncing meetings for: {today}")
        print()

        try:
            # Fetch meetings
            meetings = self.fetch_meetings()

            if not meetings:
                print("✓ No meetings found for today.")
                print()
                print("This is normal if:")
                print("  • You have no meetings scheduled today")
                print("  • Your meetings haven't been processed by Fireflies yet")
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
            print(f"✓ Sync complete!")
            print(f"  • New meetings: {saved_count}")
            print(f"  • Already synced: {skipped_count}")
            print(f"  • Location: {self.notes_path}")
            print("=" * 60)

        except Exception as e:
            print(f"\n❌ Error during sync: {e}", file=sys.stderr)
            sys.exit(1)


def main():
    """Main entry point."""
    try:
        sync_service = FirefliesObsidianSync()
        sync_service.sync()
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
