# Py-Effort

`py-effort` is a small script that queries jira cloud to distribute effort across the **Initiatives**, **Epics**, and **Stories** for a given user and time period.

## Prerequisites

> **Warning**
> This project was built using python 3.8.16. Use other versions at your own risk.

Install Dependencies

``` sh
pip install -r requirements.txt
```

Setup `.env`

``` sh
cp .env.example .env
```

Get a token to interact with the Jira api like this:  https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/

Update these variables

``` sh
JIRA_USER=
JIRA_TOKEN=
JIRA_SUBDOMAIN=
```

## Running

``` sh
python py-effort "Jeff Bezos" "2023-07-10" "2023-08-18" 0
```

See the required arguments

``` sh
python py-effort -h
usage: py-effort [-h] [-d] user start end pto

positional arguments:
  user           the user's name you running the report for
  start          the start date in YYYY-MM-DD format
  end            the end date in YYYY-MM-DD format
  pto            the pto days the user has taken between start and end

optional arguments:
  -h, --help     show this help message and exit
  -d, --details  show the details section
```
