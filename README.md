# notion-backup

Automate export of Notion workspace

## Installation

```
pip install --upgrade notion-backup
```

## Configuration

Create a `notion_backup.conf` file from the template `notion_backup.conf.template`.
Get the token, file_token and space_id from the cookies of your browser.

## Usage

```
backup_notion --output-dir='.' --config-file='notion_backup.conf'
```
