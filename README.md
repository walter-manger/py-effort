# Py-Effort

`py-effort` is a small script that queries jira cloud to distribute effort across the **Initiatives**, **Epics**, and **Stories**.

## Prerequisites

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
