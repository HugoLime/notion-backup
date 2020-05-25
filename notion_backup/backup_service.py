from operator import itemgetter

from prompt_toolkit import prompt

from notion_backup.configuration_service import ConfigurationService
from notion_backup.notion_client import NotionClient


class BackupService:
    def __init__(self):
        self.configuration_service = ConfigurationService()
        self.notion_client = NotionClient(self.configuration_service)

    def login(self):
        email = self.configuration_service.get_key("email")
        if email:
            email = prompt("Email address: ", default=email)
        else:
            email = prompt("Email address: ")
        self.configuration_service.write_key("email", email)

        csrf_values = self.notion_client.ask_otp()
        print(f"A one temporary password has been sent to your email address {email}")
        otp = prompt("Temporary password: ")

        token = self.notion_client.get_token(csrf_values, otp)
        self.configuration_service.write_key("token", token)
        print("Congratulations, you have been successfully authenticated")

    def backup(self):
        print("Login to notion if necessary")
        token = self.configuration_service.get_key("token")
        if not token:
            self.login()

        user_content = self.notion_client.get_user_content()

        user_id = list(user_content["notion_user"].keys())[0]
        print(f"User id: {user_id}")

        spaces = [
            (space_id, space_details["value"]["name"])
            for (space_id, space_details) in user_content["space"].items()
        ]
        print("Available spaces:")
        for (space_id, space_name) in spaces:
            print(f'\t- {space_name}: {space_id}')
        space_id = self.configuration_service.get_key('space_id')
        space_id = prompt("Select space id: ", default=(space_id or spaces[0][0]))

        if space_id not in map(itemgetter(0), spaces):
            raise Exception('Selected space id not in list')

        self.configuration_service.write_key('space_id', space_id)
        print("Launching export task")



        print("Waiting for export task to complete")
        print("Downloading zip export")


if __name__ == "__main__":
    print("Backup Notion workspace")
    backup_service = BackupService()
    backup_service.backup()
