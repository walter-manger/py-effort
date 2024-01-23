import json
import requests
import datetime
from typing import List, Tuple, Dict
from requests.auth import HTTPBasicAuth
from requests.models import Response
from models import Sprint, Epic, Issue

class JiraClient:
    def __init__(self, jira_user: str, jira_token: str, jira_subdomain: str, board_id: int):
        self.base_url = f"https://{jira_subdomain}.atlassian.net/rest/"
        self.auth = HTTPBasicAuth(jira_user, jira_token)
        self.headers = {"Accept": "application/json"}
        self.board_id = board_id

    def _make_request(
        self, method: str = "GET", url: str = "", params: Dict = {"maxResults": 50}
    ) -> Response:
        return requests.request(
            method,
            self.base_url + url,
            headers=self.headers,
            params=params,
            auth=self.auth,
        )

    def _get_all_pages(
        self,
        url: str = "",
        params: Dict = {"maxResults": 50, "startAt": 0},
        collection_key="issues",
    ) -> List[Dict]:
        is_last = False
        collection = []
        max_results = "maxResults" in params and params["maxResults"] or 50
        start_at = "startAt" in params and params["startAt"] or 0

        while not is_last:
            response = self._make_request(
                url=url,
                params=params,
            )
            r = json.loads(response.text)
            collection.extend(r[collection_key])

            is_last = ("isLast" in r and r["isLast"]) or (
                "total" in r and r["total"] < start_at + max_results
            )
            if not is_last:
                start_at = max_results + start_at
                params["startAt"] = start_at
                print(f"url: {url}, start_at: {start_at}")

        return collection

    def get_sprints(
        self, start_date: datetime.datetime, end_date: datetime.datetime
    ) -> List[Sprint]:
        # We have to loop through results because the API doesn't allow filtering by dates.
        # https://jira.atlassian.com/browse/JRACLOUD-72007
        collection = self._get_all_pages(
            url=f"agile/1.0/board/{self.board_id}/sprint", collection_key="values"
        )

        sprints = [Sprint(v) for v in collection]
        filtered_sprints = [
            s for s in sprints if s.start_date >= start_date and s.end_date <= end_date
        ]

        return filtered_sprints

    def get_stories(
        self,
        assignee,
        sprint_names,
    ) -> Tuple[List[Issue], int]:
        """
        Gets a list of Stories from the Jira Cloud API.
        """
        quoted_sprint_names = ",".join([f'"{s}"' for s in sprint_names])

        collection = self._get_all_pages(
            url="api/3/search",
            params={
                "jql": f'assignee = "{assignee}" AND issueType = Story AND sprint in ({quoted_sprint_names})',
                "fields": "summary,key,status,assignee,updated,issuetype,parent,customfield_11200,customfield_12488,customfield_10004,customfield_10007",
            },
            collection_key="issues",
        )

        stories = [Issue(s) for s in collection]

        all_story_points = 0
        for s in stories:
            if s.storyPoints:
                all_story_points += s.storyPoints
            else:
                print("found a story {} without a storyPoint value".format(s.key))

        return stories, all_story_points

    def get_epics(self, epic_keys: List[str], stories: List[Issue]) -> List[Epic]:
        """
        Gets a list of Epics from the Jira Cloud API.
        """

        collection = self._get_all_pages(
            url="api/3/search",
            params={
                "jql": f'key in ({",".join(epic_keys)})',
                "fields": "summary,key,status,assignee,updated,issuetype,parent,customfield_11200,customfield_12488,customfield_10004,customfield_10007",
            },
            collection_key="issues",
        )

        return [Epic(e, stories) for e in collection]
