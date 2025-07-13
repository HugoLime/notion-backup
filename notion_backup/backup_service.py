from datetime import datetime
from operator import itemgetter
from pathlib import Path
from time import sleep

import click
import requests
from prompt_toolkit import prompt
from tqdm import tqdm

from notion_backup.configuration_service import ConfigurationService
from notion_backup.notion_client import NotionClient

STATUS_WAIT_TIME = 10
block_size = 1024  # 1 Kibibyte


class BackupService:
    def __init__(self, output_dir_path, config_file):
        self.output_dir_path = output_dir_path
        if not self.output_dir_path.exists():
            raise Exception(
                f"Output directory {self.output_dir_path.resolve()} does not exit"
            )
        self.configuration_service = ConfigurationService(config_file)
        self.notion_client = NotionClient(self.configuration_service)

    def _download_file(self, url, export_file, file_token):
        with requests.get(
            url, stream=True, allow_redirects=True, cookies={"file_token": file_token}
        ) as response:
            total_size = int(response.headers.get("Content-Length", 0))
            tqdm_bar = tqdm(total=total_size, unit="iB", unit_scale=True)
            with export_file.open("wb") as export_file_handle:
                for data in response.iter_content(block_size):
                    tqdm_bar.update(len(data))
                    export_file_handle.write(data)
            tqdm_bar.close()

    def get_backup_tasks(self):
        user_tasks = self.notion_client.get_user_tasks()
        backup_tasks = [
            task for task in user_tasks if task["eventName"] == "partitionedExportSpace"
        ]
        return backup_tasks

    def backup(self):
        try:
            self.notion_client.get_user_content()
        except requests.exceptions.HTTPError as err:
            raise Exception("Token is not valid")

        user_content = self.notion_client.get_user_content()

        user_id = list(user_content["notion_user"].keys())[0]
        print(f"User id: {user_id}")

        available_spaces_ids = [
            space_view_pointer["spaceId"]
            for space_view_pointer in user_content["user_root"][user_id]["value"][
                "space_view_pointers"
            ]
        ]
        print(f"Available spaces ids: {available_spaces_ids}")

        selected_space_id = self.configuration_service.get_string_key("space_id")
        print(f"Selected space id: {selected_space_id}")
        if selected_space_id not in available_spaces_ids:
            raise Exception("Selected space id not in list of available spaces")

        print("Checking if export task is already running")
        backup_tasks = self.get_backup_tasks()
        if len(backup_tasks) > 0:
            task_id = backup_tasks[0]["id"]
            print(f"Export task {task_id} is already running")
        else:
            print("Launching export task")
            self.notion_client.launch_export_task(selected_space_id)
            print(f"Export task has been launched")
            print(f"Searching for export task id")
            backup_tasks = self.get_backup_tasks()
            if len(backup_tasks) == 0:
                raise Exception("Export task not found")
            task_id = backup_tasks[0]["id"]
            print(f"Export task {task_id} found")

        while True:
            try:
                task_status = self.notion_client.get_task_status(task_id)
            except requests.exceptions.HTTPError as err:
                if err.response.status_code == 429:
                    print(f"Too many requests when polling task status")
                raise err
            if "status" in task_status:
                status_type = task_status["status"].get("type")
                if status_type == "complete":
                    break
                pages_exported = task_status["status"].get("pagesExported")
                print(
                    f"...Export still in progress, {pages_exported} pages exported, waiting for {STATUS_WAIT_TIME} seconds"
                )
            else:
                print(
                    f"...Export still in progress, waiting for {STATUS_WAIT_TIME} seconds"
                )
            sleep(STATUS_WAIT_TIME)
        print("Export task is finished")

        export_link = task_status["status"]["exportURL"]
        print(f"Downloading zip export from {export_link}")

        export_file_name = (
            f'export_{selected_space_id}_{datetime.now().strftime("%Y%m%d")}.zip'
        )

        file_token = self.configuration_service.get_string_key("file_token")
        self._download_file(
            export_link, self.output_dir_path / export_file_name, file_token
        )


@click.command()
@click.option("--output-dir", default=".", help="Where the zip export will be saved")
@click.option("--config-file", help="Path to the configuration file")
def main(output_dir, config_file):
    output_dir_path = Path(output_dir)
    print(f"Backup Notion workspace into directory {output_dir_path.resolve()}")
    backup_service = BackupService(output_dir_path, config_file)
    backup_service.backup()


if __name__ == "__main__":
    main()
