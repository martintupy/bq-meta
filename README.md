# BigQuery metadata

> "Inspect BigQuery metadata faster"

- Interactive CLI
- Quick search through available projects, datasets, tables
- View up to date table's metadata and it's schema
- Local history of searched tables

## Requirements

- python >= 3.6

- fzf - https://github.com/junegunn/fzf (required)

```bash
brew install fzf
```

search through list of values (i.e. project, dataset, tables) is done using `fzf`

## Installation

1. Install as python package using [pypi](https://pypi.org/project/bq-meta/), this will create executable in `/usr/local/bin/bq-meta`

    ```bash
    pip install bq-meta
    ```

2. Initialize `bq-meta`

    ```bash
    bq-meta --init
    ```

3. Follow on screen prompts

    - create configuration
    - login to the google account using browser (Account is separated from `gcloud` cli)

## Run

To open interactive CLI, simply run

```bash
bq-meta
```

![cli](https://github.com/martintupy/bq-meta/raw/main/docs/cli.png)

### Table metadata

To view table metadata, press `o` key and select through project, dataset, table.

![metadata](https://github.com/martintupy/bq-meta/raw/main/docs/metadata.png)

Table metadata can be refreshed, press `r` to fetch fresh metadata

It's also possible to run `bq-meta` directly with `FULL_TABLE_ID`

```bash
bq-meta bigquery-public-data:github_repos.commits
```

### Table schema

Once table metadata is opened, press `s` key to view it's schema

![schema](https://github.com/martintupy/bq-meta/raw/main/docs/schema.png)

### Open in console

You can open table in console.cloud.google.com by pressing `c` key

![browser](https://raw.githubusercontent.com/martintupy/bq-meta/main/docs/browser.png)

### Search history

Every viewed table is saved to the history. To search through history, press `h` key

![history](https://github.com/martintupy/bq-meta/raw/main/docs/history.png)

### Other

```bash
Usage: python -m bq_meta [OPTIONS] [FULL_TABLE_ID]

  BiqQuery metadata

Options:
  --raw             View raw response from the BigQuery for specific 'FULL_TABLE_ID'
  --init            Initialize 'bq-meta' configuration
  --info            Print info of currently used account
  --fetch-projects  Fetch availabe google projects
  --version         Show the version and exit.
  --help            Show this message and exit.
```
