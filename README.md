# BigQuery Metadata viewer

> "Designed for superusers who value their time"

- quick search through available projects, dataset, tables
- view table metadata and schema
- open in browser

## Requirements

- python >= 3.6

- fzf - https://github.com/junegunn/fzf (required)

```bash
brew install fzf
```

## Installation

- Using [pypi](https://pypi.org/project/bq-meta/)

```bash
pip install bq-meta
```

- Initialize

```bash
bq-meta --init
```

## Examples

```bash
Usage: bq-meta [OPTIONS] [SQL]

  BiqQuery query.

Options:
  -f, --file FILENAME  File containing SQL
  -y, --yes            Automatic yes to prompt
  -h, --history        Search local history
  -d, --delete         Delete job from history (local & cloud)
  -i, --info           Show gcloud configuration
  --clear              Clear local history
  --sync               Sync history from cloud
  --init               Initialize bq-meta environment
  --version            Show the version and exit.
  --help               Show this message and exit.
```
