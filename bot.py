import slack
import os
import requests

from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, jsonify
from slackeventsapi import SlackEventAdapter
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)
slack_event_adapter = SlackEventAdapter(os.environ['SIGNING_SECRET'],'/slack/events', app)

bot_client = slack.WebClient(token=os.environ['BOT_SLACK_TOKEN'])
BOT_ID = bot_client.api_call("auth.test")['user_id']
azure_client = DocumentAnalysisClient(endpoint=os.environ['AZURE_ENDPOINT'], credential=AzureKeyCredential(os.environ['AZURE_TOKEN']))

@app.route("/")
def index():
    return jsonify({"status": "ok"})


@slack_event_adapter.on('message')
def message(payload):
    response = jsonify({'status': 'ok'})
    event = payload.get('event', {})
    user_id = event.get('user')

    if BOT_ID == user_id:
        return

    files = event.get("files", [])
    if not files:
        return

    file_info = files[0]
    priv_img_url = file_info.get("url_private")

    response = requests.get(url=priv_img_url, headers={'Authorization': f'Bearer {os.environ['BOT_SLACK_TOKEN']}'})

    analyze = azure_client.begin_analyze_document(model_id='prebuilt-businessCard', document=response.content)

    result = analyze.result()
  
    print(result.documents[0].fields[0].value)

    return jsonify({"status": "ok"}), 200

PORT = int(os.environ.get("PORT", 8080))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)