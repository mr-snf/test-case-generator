"""
Fetch ticket details from Jira including descriptions and attachments.
Uses configuration from configs/config.py
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

from configs.config import JIRA_API_TOKEN, JIRA_TICKET_ID, JIRA_URL, JIRA_USERNAME
from src.jira import JiraAPI


class TicketDetailsFetcher:
    """Class to fetch and process ticket details from Jira"""

    def __init__(self):
        """Initialize the fetcher with Jira configuration"""
        try:
            self.jira_client = JiraAPI(
                base_url=JIRA_URL, username=JIRA_USERNAME, api_token=JIRA_API_TOKEN
            )
            print(f"✅ Initialized Jira client for: {JIRA_URL}")
        except ValueError as e:
            print(f"❌ Configuration error: {e}")
            print("\nPlease check your environment variables or .env file:")
            print("  - JIRA_URL")
            print("  - JIRA_USERNAME")
            print("  - JIRA_API_TOKEN")
            sys.exit(1)
        except Exception as e:
            print(f"❌ Failed to initialize Jira client: {e}")
            sys.exit(1)

    def test_connection(self) -> bool:
        """Test the connection to Jira"""
        print("Testing connection to Jira...")
        try:
            if self.jira_client.test_connection():
                print("✅ Successfully connected to Jira!")
                return True
            else:
                print("❌ Failed to connect to Jira")
                return False
        except Exception:
            print("❌ Connection test failed!!")
            sys.exit(1)

    def get_ticket_details(self, ticket_id: str) -> Dict:
        """
        Get comprehensive ticket details

        Args:
            ticket_id: The Jira ticket ID (e.g., 'PROJ-123')

        Returns:
            Dictionary containing ticket details
        """
        print(f"\n📋 Fetching details for ticket: {ticket_id}")

        try:
            # Get full issue details
            issue = self.jira_client.get_issue(ticket_id)
            if not issue:
                print(f"❌ Ticket {ticket_id} not found or error occurred")
                return {}

            # Extract key information
            fields = issue.get("fields", {})
            ticket_details = {
                "ticket_id": ticket_id,
                "key": issue.get("key", ticket_id),
                "summary": fields.get("summary", ""),
                "description": self.jira_client.get_issue_description(ticket_id),
                "attachments": self._get_attachments(fields.get("attachment", [])),
            }

            print(f"✅ Successfully fetched details for {ticket_id}")
            return ticket_details

        except Exception as e:
            print(f"❌ Error fetching ticket details: {e}")
            raise

    def _get_attachments(self, attachments: List[Dict]) -> List[Dict]:
        """
        Process attachment information

        Args:
            attachments: List of attachment objects from Jira

        Returns:
            List of processed attachment details
        """
        processed_attachments = []

        for attachment in attachments:
            processed_attachment = {
                "filename": attachment.get("filename", ""),
                "size": attachment.get("size", 0),
                "mime_type": attachment.get("mimeType", ""),
                "created": attachment.get("created", ""),
                "author": attachment.get("author", {}).get("displayName", ""),
                "url": attachment.get("content", ""),
                "thumbnail": attachment.get("thumbnail", ""),
            }
            processed_attachments.append(processed_attachment)

        return processed_attachments

    def save_to_json(
        self, ticket_details: Dict, output_file: Optional[str] = None
    ) -> str:
        """
        Save ticket details to JSON file

        Args:
            ticket_details: Ticket details dictionary
            output_file: Output file path (optional)

        Returns:
            Path to the saved file
        """
        if not output_file:
            ticket_id = ticket_details.get("ticket_id", "unknown")
            output_file = f"ticket_details_{ticket_id}.json"

        try:
            # Create directory if it doesn't exist
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(ticket_details, f, indent=2, ensure_ascii=False)

            print(f"✅ Ticket details saved to: {output_file}")
            return output_file

        except OSError as e:
            print(f"❌ Error saving to file: {e}")
            return ""

    def print_summary(self, ticket_details: Dict):
        """
        Print a summary of ticket details

        Args:
            ticket_details: Ticket details dictionary
        """
        if not ticket_details:
            print("❌ No ticket details to display")
            return

        print(f"\n📊 Ticket ID: {ticket_details.get('ticket_id', 'Unknown')}")
        print("=" * 60)
        print(f"Summary: {ticket_details.get('summary', 'N/A')}")

        # Description preview
        description = ticket_details.get("description", "")
        if description:
            preview = (
                description[:200] + "..." if len(description) > 200 else description
            )
            print(f"\nDescription Preview:\n{preview}")

        # Attachments
        attachments = ticket_details.get("attachments", [])
        if attachments:
            print(f"\n📎 Attachments ({len(attachments)}):")
            for i, attachment in enumerate(attachments, 1):
                print(
                    f"  {i}. {attachment.get('filename', 'Unknown')} ({attachment.get('size', 0)} bytes)"
                )

    def download_attachments(
        self, ticket_details: Dict, download_dir: str = "attachments"
    ) -> List[str]:
        """
        Download attachments from the ticket

        Args:
            ticket_details: Ticket details dictionary
            download_dir: Directory to save attachments

        Returns:
            List of downloaded file paths
        """
        attachments = ticket_details.get("attachments", [])
        if not attachments:
            print("📎 No attachments to download")
            return []

        # Create download directory
        Path(download_dir).mkdir(exist_ok=True)

        downloaded_files = []
        print(f"\n📥 Downloading {len(attachments)} attachments to '{download_dir}'...")

        for i, attachment in enumerate(attachments, 1):
            filename = attachment.get("filename", f"attachment_{i}")
            url = attachment.get("url", "")

            if not url:
                print(f"  ⚠️  Skipping {filename}: No download URL")
                continue

            try:
                # Download the file
                response = self.jira_client.session.get(url, auth=self.jira_client.auth)
                if response.status_code == 200:
                    file_path = os.path.join(download_dir, filename)
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    downloaded_files.append(file_path)
                    print(f"  ✅ Downloaded: {filename}")
                else:
                    print(
                        f"  ❌ Failed to download {filename}: HTTP {response.status_code}"
                    )

            except OSError as e:
                print(f"  ❌ Error downloading {filename}: {e}")

        print(f"📥 Downloaded {len(downloaded_files)} files successfully")
        return downloaded_files


def main():
    """Main function"""

    # Initialize fetcher
    fetcher = TicketDetailsFetcher()

    # Test connection
    if not fetcher.test_connection():
        sys.exit(1)

    # Get ticket details
    ticket_details = fetcher.get_ticket_details(JIRA_TICKET_ID)
    if not ticket_details:
        print(f"❌ Failed to fetch details for ticket {JIRA_TICKET_ID}")
        sys.exit(1)

    # Print summary (unless disabled)
    fetcher.print_summary(ticket_details)

    # Save to JSON (if requested)
    output_dir = "feature"
    fetcher.save_to_json(
        ticket_details, f"{output_dir}/ticket_details_{JIRA_TICKET_ID}.json"
    )

    # Download attachments (if requested)
    fetcher.download_attachments(ticket_details, output_dir)

    print(f"\n✅ Successfully processed ticket {JIRA_TICKET_ID}")


if __name__ == "__main__":
    main()
