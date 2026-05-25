import logging
import json
import requests

import azure.functions as func

from requests.auth import HTTPBasicAuth

from azure.ai.agents import AgentsClient
from azure.identity import AzureCliCredential
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

app = func.FunctionApp()

# =========================
# ServiceNow Config
# =========================

SNOW_URL = os.getenv("SNOW_URL")
SNOW_USER = os.getenv("SNOW_USER")
SNOW_PASSWORD = os.getenv("SNOW_PASSWORD")

# =========================
# Azure Foundry Config
# =========================

PROJECT_ENDPOINT = os.getenv("PROJECT_ENDPOINT")
AGENT_ID = os.getenv("AGENT_ID")

# =========================
# Azure Agent Client
# =========================

credential = AzureCliCredential()

client = AgentsClient(
    endpoint=PROJECT_ENDPOINT,
    credential=credential
)

# =========================
# HTTP Trigger Function
# =========================

@app.route(route="incidents")
def incidents(req: func.HttpRequest) -> func.HttpResponse:

    logging.info("Fetching incidents from ServiceNow")

    response = requests.get(
        SNOW_URL,
        auth=HTTPBasicAuth(SNOW_USER, SNOW_PASSWORD),
        headers={
            "Accept": "application/json"
        },
        params={
            "sysparm_limit": "5"
        }
    )

    data = response.json()

    incidents = data["result"]

    final_output = []

    for incident in incidents:

        # Create thread
        thread = client.threads.create()

        # Send incident to agent
        client.messages.create(
            thread_id=thread.id,
            role="user",
            content=str(incident)
        )

        # Run agent
        run = client.runs.create_and_process(
            thread_id=thread.id,
            agent_id=AGENT_ID
        )

        # Get response
        messages = client.messages.list(thread_id=thread.id)

        for msg in messages:
            if msg.role == "assistant":

                try:
                    response_json = json.loads(
                        msg.content[0].text.value
                    )

                    final_output.append(response_json)

                except Exception:
                    final_output.append({
                        "raw_response": msg.content[0].text.value
                    })

    return func.HttpResponse(
        json.dumps(final_output, indent=2),
        mimetype="application/json",
        status_code=200
    )