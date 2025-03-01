import json
import requests

DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1345391739933818950/MnK0mzcM8cj4L80yJmsc6KPGlNeKXggqzKdFDUibJutk_zAEuprYu8b9-mkj6y84I4iz"

def send_discord_notification(username, email):
    data = {
        "content": f"🎉 New user signed up!\n👤 **Username:** {username}\n📧 **Email:** {email}",
        "username": "Protobase"
    }

    headers = {"Content-Type": "application/json"}
    response = requests.post(DISCORD_WEBHOOK_URL, data=json.dumps(data), headers=headers)

    if response.status_code == 204:
        print("✅ Discord notification sent successfully.")
    else:
        print(f"❌ Failed to send Discord notification: {response.status_code}, {response.text}")

send_discord_notification("Akash", "mail.com")