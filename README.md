# notion-backup

Automate export of Notion workspace

## Deprecation

The login system does not work anymore. Its seems to be blocked by a browser integrity check

## Installation

```
pip install --upgrade notion-backup
```

## Usage

```
backup_notion --output-dir='.'
```

## How it works

The script obtains an API token by requesting a temporary password to be sent to your email address.

Login information are stored in `~/.notion_backup.conf`

The export zip is generated and downloaded to the specified directory.
