import json
import requests
import datetime
from typing import List, Tuple, Dict
from requests.auth import HTTPBasicAuth
from requests.models import Response
from models import Sprint, Epic, Issue


class JiraClient:
    def __init__(self, jira_user: str, jira_token: str, jira_subdomain: str):
        self.base_url = f"https://{jira_subdomain}.atlassian.net/rest/"
        self.auth = HTTPBasicAuth(jira_user, jira_token)
        self.headers = {"Accept": "application/json"}

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

    def get_sprints(
        self, start_date: datetime.datetime, end_date: datetime.datetime
    ) -> List[Sprint]:
        is_last = False
        sprints = []
        max_results = 50
        start_at = 0

        # We have to loop through results because the API doesn't allow filtering by dates.
        # https://jira.atlassian.com/browse/JRACLOUD-72007
        while not is_last:
            response = self._make_request(
                url="agile/1.0/board/485/sprint",
                params={"maxResults": max_results, "startAt": start_at},
            )
            sprints_response = json.loads(response.text)
            sprints.extend([Sprint(v) for v in sprints_response["values"]])
            is_last = sprints_response["isLast"]
            if not is_last:
                start_at = start_at + max_results

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

        response = self._make_request(
            url="api/3/search",
            params={
                "jql": f'assignee = "{assignee}" AND issueType = Story AND sprint in ({quoted_sprint_names})',
                "fields": "summary,key,status,assignee,updated,issuetype,parent,customfield_11200,customfield_12488,customfield_10004,customfield_10007",
                "maxResults": "50",
            },
        )
        stories_response = json.loads(response.text)
        stories = [Issue(s) for s in stories_response["issues"]]

        all_story_points = 0
        for s in stories:
            all_story_points += s.storyPoints

        return stories, all_story_points

    def get_epics(self, epic_keys: List[str], stories: List[Issue]) -> List[Epic]:
        """
        Gets a list of Epics from the Jira Cloud API.
        """

        response = self._make_request(
            url="api/3/search",
            params={
                "jql": f'key in ({",".join(epic_keys)})',
                "fields": "summary,key,status,assignee,updated,issuetype,parent,customfield_11200,customfield_12488,customfield_10004,customfield_10007",
                "maxResults": "50",
            },
        )
        epics_response = json.loads(response.text)
        return [Epic(e, stories) for e in epics_response["issues"]]
