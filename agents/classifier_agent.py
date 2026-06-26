"""
classifier_agent.py

Purpose:
    Handles communication with the Azure AI Foundry
    Classification Agent.

Responsibilities:
    - Creates a conversation thread.
    - Sends incident data to the Classification Agent.
    - Executes the agent run.
    - Retrieves and parses the agent response.
    - Returns structured JSON output for downstream processing.

Author: Md Kaif Ansari
Created: June 2026
"""

import os
import json
import logging

from azure.ai.agents import AgentsClient
from azure.identity import AzureCliCredential


class ClassifierAgent:
    """
    Wrapper class for interacting with the Azure AI Foundry
    Classification Agent.

    This class manages:
        - Client initialization
        - Thread creation
        - Message submission
        - Agent execution
        - Response retrieval
    """

    def __init__(self):
        """
        Initialize the Azure AI Foundry client and
        load agent configuration from environment variables.
        """

        self.client = AgentsClient(
            endpoint=os.getenv("PROJECT_ENDPOINT"),
            credential=AzureCliCredential()
        )

        self.agent_id = os.getenv("AGENT_ID")

    def classify(self, incident_data):
        """
        Send incident data to the Classification Agent
        and return the processed response.

        Args:
            incident_data (dict):
                Normalized incident payload.

        Returns:
            dict:
                Parsed JSON response from the agent.

            OR

            dict:
                Error details if execution fails.
        """

        try:

            logging.info("Creating agent thread")

            # Create a new conversation thread
            thread = self.client.threads.create()

            logging.info(
                f"Thread created successfully: {thread.id}"
            )

            # Send incident payload to agent
            self.client.messages.create(
                thread_id=thread.id,
                role="user",
                content=json.dumps(incident_data)
            )

            logging.info(
                "Incident payload sent to classifier agent"
            )

            # Execute the agent and wait for completion
            run = self.client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=self.agent_id
            )

            logging.info(
                f"Agent execution completed. Status: {run.status}"
            )

            # Retrieve messages from thread
            messages = self.client.messages.list(
                thread_id=thread.id
            )

            # Extract assistant response
            for message in messages:

                if message.role == "assistant":

                    response_text = (
                        message.content[0].text.value
                    )

                    try:
                        # Return structured JSON if valid
                        return json.loads(response_text)

                    except json.JSONDecodeError:

                        logging.warning(
                            "Agent response is not valid JSON"
                        )

                        return {
                            "raw_response": response_text
                        }

            return {
                "error":
                "No response received from classifier agent"
            }

        except Exception as ex:

            logging.exception(
                "Classifier Agent execution failed"
            )

            return {
                "error": str(ex)
            }