import os
import traceback
from datetime import datetime

import requests

SLACK_WEBHOOK_URL = os.environ["SLACK_WEBHOOK_URL"]

def send_slack_message(message: dict):
    response = requests.post(SLACK_WEBHOOK_URL, json=message)
    response.raise_for_status()

def notify_success(pipeline_name: str, records_processed: int = None, duration_sec: float = None):
    message = {
        "text": "ETL Pipeline Succeeded",
        "attachments": [{
            "color": "#36a64f",
            "fields": [
                {"title": "Pipeline", "value": pipeline_name, "short": True},
                {"title": "Time", "value": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "short": True},
                {"title": "Records Processed", "value": str(records_processed or "N/A"), "short": True},
                {"title": "Duration", "value": f"{duration_sec:.1f}s" if duration_sec else "N/A", "short": True},
            ]
        }]
    }
    send_slack_message(message)

def notify_failure(pipeline_name: str, error: Exception, stage: str = None):
    message = {
        "text": "ETL Pipeline Failed",
        "attachments": [{
            "color": "#ff0000",
            "fields": [
                {"title": "Pipeline", "value": pipeline_name, "short": True},
                {"title": "Failed Stage", "value": stage or "Unknown", "short": True},
                {"title": "Error", "value": str(error), "short": False},
                {"title": "Traceback", "value": f"```{traceback.format_exc()[-500:]}```", "short": False},
            ]
        }]
    }
    send_slack_message(message)

def notify_retry(pipeline_name: str, attempt: int, max_attempts: int, error: Exception):
    message = {
        "text": "ETL Pipeline Retrying",
        "attachments": [{
            "color": "#ffaa00",
            "fields": [
                {"title": "Pipeline", "value": pipeline_name, "short": True},
                {"title": "Attempt", "value": f"{attempt} of {max_attempts}", "short": True},
                {"title": "Reason", "value": str(error), "short": False},
            ]
        }]
    }
    send_slack_message(message)