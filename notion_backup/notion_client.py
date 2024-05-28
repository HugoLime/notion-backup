import requests

from notion_backup.configuration_service import ConfigurationService

NOTION_API_ROOT = "https://www.notion.so/api/v3"


class NotionClient:
    def __init__(self, configuration_service: ConfigurationService = ConfigurationService()):
        self.configuration_service = configuration_service

    def ask_otp(self):
        response = requests.request(
            "POST",
            f"{NOTION_API_ROOT}/sendTemporaryPassword",
            json={
                "email": self.configuration_service.get_string_key("email"),
                "disableLoginLink": False,
                "native": False,
                "isSignup": False,
            },
        )
        response.raise_for_status()
        json_response = response.json()
        return {
            "csrf_state": json_response["csrfState"],
            "csrf_cookie": response.cookies["csrf"],
        }

    def get_token(self, csrf_values, otp):
        response = requests.request(
            "POST",
            f"{NOTION_API_ROOT}/loginWithEmail",
            json={"state": csrf_values["csrf_state"], "password": otp},
            cookies={"csrf": csrf_values["csrf_cookie"]},
        )
        response.raise_for_status()
        return response.cookies["token_v2"]

    def _send_post_request(self, path, body):
        token = self.configuration_service.get_string_key("token")
        if not token:
            raise Exception("Token is not set")
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

    def launch_space_export_task(self, space_id):
        return self._send_post_request(
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
                        },
                    },
                }
            },
        )["taskId"]

    def launch_block_export_task(
        self, space_id, block_id, recursive=False, export_comments=False, export_type="html",
        include_contents="no_files",
    ):
        return self._send_post_request(
            "enqueueTask",
            {
                "task": {
                    "eventName": "exportBlock",
                    "request": {
                        "block": {
                            "id": block_id,
                            "spaceId": space_id
                        },
                        "exportOptions": {
                            "collectionViewExportType": "currentView",
                            "exportType": export_type,
                            "includeContents": include_contents,
                            "locale": "en",
                            "timeZone": "Asia/Jerusalem"
                        },
                        "recursive": recursive,
                        "shouldExportComments": export_comments,
                    },
                }
            },
        )["taskId"]

    def get_user_task_status(self, task_id):
        task_statuses = self._send_post_request("getTasks", {"taskIds": [task_id]})[
            "results"
        ]

        return list(
            filter(lambda task_status: task_status["id"] == task_id, task_statuses)
        )[0]
