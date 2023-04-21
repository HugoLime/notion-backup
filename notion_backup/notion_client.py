import requests

from notion_backup.configuration_service import ConfigurationService

NOTION_API_ROOT = "https://www.notion.so/api/v3"


class NotionClient:
    def __init__(self, configuration_service: ConfigurationService):
        self.configuration_service = configuration_service

    def ask_otp(self):
        response = requests.request(
            "POST",
            f"{NOTION_API_ROOT}/sendTemporaryPassword",
            json={
                "email": self.configuration_service.get_key("email"),
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

    def get_file_token(self):
        response = requests.request(
            "GET",
            f"https://www.notion.so/f/refresh",
            cookies={"token_v2": self.configuration_service.get_key("token")},
        )
        response.raise_for_status()
        return response.cookies["file_token"]

    def _send_post_request(self, path, body):
        response = requests.request(
            "POST",
            f"{NOTION_API_ROOT}/{path}",
            json=body,
            cookies={"token_v2": self.configuration_service.get_key("token")},
        )
        response.raise_for_status()
        return response.json()

    def get_user_content(self):
        return self._send_post_request("loadUserContent", {})["recordMap"]

    def launch_export_task(self, space_id):
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

    def get_user_task_status(self, task_id):
        task_statuses = self._send_post_request("getTasks", {"taskIds": [task_id]})["results"]

        return list(filter(lambda task_status: task_status["id"] == task_id, task_statuses))[0]
