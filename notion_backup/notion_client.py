import requests

from notion_backup.configuration_service import ConfigurationService

NOTION_API_ROOT = "https://www.notion.so/api/v3"


class NotionClient:
    def __init__(self, configuration_service: ConfigurationService):
        self.configuration_service = configuration_service

    def _send_post_request(self, path, body):
        token = self.configuration_service.get_string_key("token")
        response = requests.request(
            "POST",
            f"{NOTION_API_ROOT}/{path}",
            json=body,
            cookies={"token_v2": token},
        )
        response.raise_for_status()
        return response.json()

    def get_user_content(self):
        return self._send_post_request("loadUserContent", {})["recordMap"]

    def launch_export_task(self, space_id):
        self._send_post_request(
            "enqueueTask",
            {
                "task": {
                    "eventName": "exportSpace",
                    "request": {
                        "spaceId": space_id,
                        "exportOptions": {
                            "exportType": "markdown",
                            "timeZone": "Europe/Paris",
                            "locale": "en",
                            "collectionViewExportType": "currentView",
                        },
                        "shouldExportComments": False,
                    },
                }
            },
        )

    def get_task_status(self, task_id):
        task_statuses = self._send_post_request("getTasks", {"taskIds": [task_id]})[
            "results"
        ]

        return list(
            filter(lambda task_status: task_status["id"] == task_id, task_statuses)
        )[0]

    def get_user_tasks(self):
        task_ids = self._send_post_request(
            "getUserTasks",
            {"spaceId": self.configuration_service.get_string_key("space_id")},
        )["taskIds"]
        return self._send_post_request("getTasks", {"taskIds": task_ids})["results"]
