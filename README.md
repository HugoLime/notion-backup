# notion-backup

Automate export of Notion workspace

## Deprecation

The login system does not work occasionally. It seems to be blocked by a browser integrity check

## Installation

```
pip install --upgrade notion-backup
```

## Usage
Command line:
```bash
backup_notion --output-dir='.'
```

From Python:
```python
from pathlib import Path

from notion_backup.backup_service import BackupService

space_id: str = "..."
block_id: str = "..."

serv = BackupService(Path.home())
payloads: dict[str, bytes] = serv.retrieve_block(space_id, block_id)
```

## How it works

The script obtains an API token by requesting a temporary password to be sent to your email address.

Login information are stored in `~/.notion_backup.conf`

The export zip is generated and downloaded to the specified directory, or unzipped in memory and returned.
