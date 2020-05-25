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

        print("Launching export task")
        print("Waiting for export task to complete")
        print("Downloading zip export")


if __name__ == "__main__":
    print("Backup Notion workspace")
    backup_service = BackupService()
    backup_service.backup()
