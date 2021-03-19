# notion-backup

Automate export of Notion workspace

## Installation

```bash
pip install --upgrade notion-backup
```

## Usage

```bash
backup_notion --output-dir='.'
```

## Usage with docker-compose

```bash
docker-compose build
docker-compose run notion_backup
```

## How it works

The script obtains an API token by requesting a temporary password to be sent to your email address.

Login information are stored in `~/.notion_backup.conf`

The export zip is generated and downloaded to the specified directory.

## Environment Variable Options

* `OUTPUT_DIR=/exports` override output directory. overrides `--output-dir`
* `CONFIG_FILE=/config/notion_backup.conf` override config file path
* `RUN_MODE=noninteractive` don't ask for SPACE_ID, read from config file or ENV
* `SPACE_ID=asdf-aasdf-asdf` override space_id from config file
