#!/usr/bin/env python3

import os
import argparse
import datetime
import numpy as np
from dotenv import load_dotenv
from models import Vapp, wrangle_no_epic_stories
from output import print_header, print_summary, print_vapps
from api_requests import JiraClient

load_dotenv()
for v in ["JIRA_USER", "JIRA_TOKEN", "JIRA_SUBDOMAIN"]:
    if not os.getenv(v):
        raise Exception(f"{v} must be in .env")


parser = argparse.ArgumentParser()
parser.add_argument("user", help="the user's name you running the report for")
parser.add_argument(
    "start",
    help="the start date in YYYY-MM-DD format",
    type=datetime.date.fromisoformat,
)
parser.add_argument(
    "end", help="the end date in YYYY-MM-DD format", type=datetime.date.fromisoformat
)
parser.add_argument(
    "pto",
    help="the pto days the user has taken between start and end",
    type=int,
    default=0,
)
parser.add_argument("--details", default=False, action="store_true")
args = parser.parse_args()


if __name__ == "__main__":
    total_days = int(np.busday_count(args.start, args.end))
    total_percent = 100 - (args.pto / total_days * 100)

    # Setup the JiraClient
    client = JiraClient(
        os.getenv("JIRA_USER"), os.getenv("JIRA_TOKEN"), os.getenv("JIRA_SUBDOMAIN")
    )

    # Get all sprints, then filter between start_date and end_date
    sprints = client.get_sprints(args.start, args.end)
    sprint_names = [s.name for s in sprints]

    # Get all stories filtered by user and sprints
    stories, total_story_points = client.get_stories(args.user, sprint_names)

    # Get all epics that match the story epic keys
    epic_keys = list(set([k.parent.key for k in stories]))
    epics = client.get_epics([k for k in epic_keys if k != ""], stories)

    # Create vapps from the epics to build out the full tree
    vapp_keys = list(set([k.parent.key for k in epics]))
    vapps = [Vapp(k, epics) for k in vapp_keys]

    # Add in the stories that don't have a parent
    vapps = wrangle_no_epic_stories(vapps, stories)

    # Output
    print_header(
        len(stories), total_story_points, total_days, args.pto, sprint_names, args
    )
    print_summary(vapps, total_story_points, total_percent, args.pto, total_days)
    if args.details:
        print_vapps(vapps)
