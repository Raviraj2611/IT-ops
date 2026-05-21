import json
import os
from pathlib import Path

from dotenv import load_dotenv
import requests
import azure.functions as func

load_dotenv(dotenv_path=Path(__file__).parent.parent / '.env', encoding='utf-8-sig')


def main(req: func.HttpRequest) -> func.HttpResponse:
    instance_url = (req.params.get('url') or os.getenv('SERVICENOW_URL', '')).strip()
    username = (req.params.get('username') or os.getenv('SERVICENOW_USER', '')).strip()
    password = (req.params.get('password') or os.getenv('SERVICENOW_PASS', '')).strip()

    if not instance_url or not username or not password:
        return func.HttpResponse(
            json.dumps({
                'error': 'Missing ServiceNow URL, username, or password.',
                'help': 'Provide url, username, and password in .env or as query parameters.'
            }),
            status_code=400,
            mimetype='application/json'
        )

    url = instance_url.rstrip('/') + '/api/now/table/incident?sysparm_limit=10000'

    try:
        response = requests.get(
            url,
            auth=(username, password),
            headers={'Accept': 'application/json'},
            timeout=30
        )
        body = response.json()

        if response.status_code >= 400:
            return func.HttpResponse(
                json.dumps({
                    'error': 'ServiceNow request failed',
                    'details': body
                }),
                status_code=response.status_code,
                mimetype='application/json'
            )

        return func.HttpResponse(
            json.dumps(body.get('result', body)),
            status_code=200,
            mimetype='application/json'
        )
    except Exception as error:
        return func.HttpResponse(
            json.dumps({
                'error': 'Unable to fetch incidents from ServiceNow.',
                'details': str(error)
            }),
            status_code=500,
            mimetype='application/json'
        )
