import os
import httpx
from .. import schemas

# Get the webhook URL from our environment variables
TEAMS_WEBHOOK_URL = os.getenv("TEAMS_WEBHOOK_URL")

async def send_threat_to_teams(threat: schemas.Threat):
    """
    Formats a threat notification and sends it to a Microsoft Teams channel
    using an Incoming Webhook.
    """
    if not TEAMS_WEBHOOK_URL:
        print("Warning: TEAMS_WEBHOOK_URL is not set. Skipping notification.")
        return

    # We will use an "Adaptive Card" for a rich, well-formatted message.
    # This is a standard JSON format that Teams understands.
    card_payload = {
        "type": "message",
        "attachments": [
            {
                "contentType": "application/vnd.microsoft.card.adaptive",
                "contentUrl": None,
                "content": {
                    "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
                    "type": "AdaptiveCard",
                    "version": "1.5",
                    "msteams": {"width": "Full"},
                    "body": [
                        {
                            "type": "TextBlock",
                            "text": "🚨 New Maritime Threat Detected!",
                            "weight": "Bolder",
                            "size": "Large",
                            "color": "Attention"
                        },
                        {
                            "type": "TextBlock",
                            "text": threat.title,
                            "weight": "Bolder",
                            "size": "Medium",
                            "wrap": True
                        },
                        {
                            "type": "FactSet",
                            "facts": [
                                {"title": "Region:", "value": threat.region},
                                {"title": "Category:", "value": threat.category},
                                {"title": "Published:", "value": f"{threat.date_mentioned}" if threat.date_mentioned else "Not specified"},
                                {"title": "Impact:", "value": threat.potential_impact or "Not specified"},
                                {"title": "Reported:", "value": f"{threat.created_at.strftime('%Y-%m-%d %H:%M')} UTC"}  
                            ]
                        },
                        {
                            "type": "TextBlock",
                            "text": threat.description,
                            "wrap": True,
                            "separator": True
                        },
                        *(
                            [
                                {
                                    "type": "TextBlock",
                                    "text": f"[{url.split('/')[-2].replace('-', ' ').title()}]({url.strip()})", # Extracts and formats the domain/path for display
                                    "wrap": True,
                                    "separator": True,
                                    "spacing": "Small"
                                }
                                for url in threat.source_urls
                            ]
                            if threat.source_urls
                            else [
                                {
                                    "type": "TextBlock",
                                    "text": "No source URLs provided.",
                                    "wrap": True,
                                    "separator": True
                                }
                            ]
                        )
                    ]
                }
            }
        ]
    }

    # Send the POST request to the Teams webhook URL
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(TEAMS_WEBHOOK_URL, json=card_payload)
            response.raise_for_status()  # Raises an exception for 4xx/5xx responses
            print(f"Successfully sent notification to Teams for threat ID: {threat.id}")
        except httpx.HTTPStatusError as e:
            print(f"Error sending notification to Teams: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            print(f"An unexpected error occurred while sending Teams notification: {e}")