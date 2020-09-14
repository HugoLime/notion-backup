from datetime import datetime
from operator import itemgetter
from pathlib import Path
from time import sleep
import os

import click
import requests
from prompt_toolkit import prompt
from tqdm import tqdm

from notion_backup.configuration_service import ConfigurationService
from notion_backup.notion_client import NotionClient

STATUS_WAIT_TIME = 5
block_size = 1024  # 1 Kibibyte


class BackupService:
    def __init__(self, output_dir_path):
        self.output_dir_path = output_dir_path
        if not self.output_dir_path.exists():
            raise Exception(f'Output directory {self.output_dir_path.resolve()} does not exit')
        self.configuration_service = ConfigurationService()
        self.notion_client = NotionClient(self.configuration_service)

    def _login(self):
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

    def _download_file(self, url, export_file):
        with requests.get(url, stream=True, allow_redirects=True) as response:
            total_size = int(response.headers.get("content-length", 0))
            tqdm_bar = tqdm(total=total_size, unit="iB", unit_scale=True)
            with export_file.open("wb") as export_file_handle:
                for data in response.iter_content(block_size):
                    tqdm_bar.update(len(data))
                    export_file_handle.write(data)
            tqdm_bar.close()

    def backup(self):
        print("Login to notion if necessary")
        token = self.configuration_service.get_key("token")
        if not token:
            self._login()

        user_content = self.notion_client.get_user_content()

        user_id = list(user_content["notion_user"].keys())[0]
        print(f"User id: {user_id}")

        spaces = [
            (space_id, space_details["value"]["name"])
            for (space_id, space_details) in user_content["space"].items()
        ]
        print("Available spaces:")
        for (space_id, space_name) in spaces:
            print(f"\t- {space_name}: {space_id}")
        if 'SPACE_ID' in os.environ:
            space_id = os.environ.get('SPACE_ID')
        else:
            space_id = self.configuration_service.get_key("space_id")
        if space_id and os.environ.get('RUN_MODE', False) != 'noninteractive':
            space_id = prompt("Select space id: ", default=(space_id or spaces[0][0]))

        if space_id not in map(itemgetter(0), spaces):
            raise Exception("Selected space id not in list")

        self.configuration_service.write_key("space_id", space_id)

        print("Launching export task")
        task_id = self.notion_client.launch_export_task(space_id)
        print(f"Export task {task_id} has been launched")

        while True:
            task_status = self.notion_client.get_user_task_status(task_id)
            try:
                if task_status["status"]["type"] == "complete":
                    break
                current_status = task_status["status"]["type"]
                print(
                    f"...Export still in status '{current_status}', waiting for {STATUS_WAIT_TIME} seconds"
                )
                sleep(STATUS_WAIT_TIME)
            except KeyError:
                print(
                    f"...Export status not available, waiting for {STATUS_WAIT_TIME} seconds"
                )
        print("Export task is finished")

        export_link = task_status["status"]["exportURL"]
        print(f"Downloading zip export from {export_link}")

        export_file_name = f'export_{space_id}_{datetime.now().strftime("%Y%m%d")}.zip'

        self._download_file(export_link, self.output_dir_path / export_file_name)


@click.command()
@click.option("--output-dir", default=".", help="Where the zip export will be saved")
def main(output_dir):
    output_dir = os.environ.get('OUTPUT_DIR', output_dir)
    output_dir_path = Path(output_dir)
    print(f"Backup Notion workspace into directory {output_dir_path.resolve()}")
    backup_service = BackupService(output_dir_path)
    backup_service.backup()


if __name__ == '__main__':
    main()
