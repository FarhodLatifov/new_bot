# Telegram Bot with Google Sheets Integration

This Telegram bot integrates with Google Sheets to manage client and partner requests.

## Deployment to Render.com

To deploy this bot securely to Render.com without exposing secrets:

1. Make sure `service_account.json` is in `.gitignore` (already configured)
2. Set the following environment variables in your Render.com dashboard:
   - `BOT_TOKEN` - Your Telegram bot token
   - `ADMIN_IDS` - Comma-separated list of admin user IDs
   - `GOOGLE_SPREADSHEET_ID` - Your Google Spreadsheet ID
   - `GOOGLE_SERVICE_ACCOUNT_JSON` - Full content of your service account JSON file

The bot is configured to read the Google service account credentials from the `GOOGLE_SERVICE_ACCOUNT_JSON` environment variable when deployed, falling back to the file-based approach for local development.

## Local Development

For local development, copy `env.example` to `.env` and fill in your values:
```bash
cp env.example .env
```

Also copy `service_account.json.example` to `service_account.json` and fill in your service account details:
```bash
cp service_account.json.example service_account.json
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Run the bot:
```bash
python main.py
```
