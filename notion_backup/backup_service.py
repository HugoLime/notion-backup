from notion_backup.notion_client import NotionClient


class BackupService:
    def __init__(self):
        self.notion_client = NotionClient()

    def backup(self):
        print("Login to notion if necessary")
        print("Launching export task")
        print("Waiting for export task to complete")
        print("Downloading zip export")


if __name__ == "__main__":
    print('Backup Notion workspace')
    backup_service = BackupService()
    backup_service.backup()
