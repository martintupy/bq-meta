# BigQuery metadata viewer

> "Inspect BigQuery metadata faster"

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
Usage: bq_meta [OPTIONS] [TABLE]

  BiqQuery table metadata viewer

Options:
  -p, --project-id TEXT  Project name
  -d, --dataset-id TEXT  Dataset name
  -t, --table-id TEXT    Table name
  --init                 Initialize bq_meta
  --info                 Print info of currently logged account
  --fetch-projects       Fetch projects
  --version              Show the version and exit.
  --help                 Show this message and exit.
```
