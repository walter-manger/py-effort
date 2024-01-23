from typing import List, Dict
import datetime

BLANK_VAPP_KEY = "<V>"


class Parent:
    def __init__(self, issue: Dict):
        parentKey = ""
        parentSummary = ""
        if "parent" in issue["fields"]:
            if "key" in issue["fields"]["parent"]:
                parentKey = issue["fields"]["parent"]["key"]
            if "fields" in issue["fields"]["parent"]:
                parentSummary = issue["fields"]["parent"]["fields"]["summary"]

        self.key = parentKey
        self.summary = parentSummary


class IssueBase:
    def __init__(self, issue: Dict):
        self.key = issue["key"]
        self.summary = issue["fields"]["summary"]
        self.parent = Parent(issue)

    def __str__(self) -> str:
        return "{} {}".format(self.key, self.summary.strip())


class Issue(IssueBase):
    def __init__(self, issue: Dict):
        super().__init__(issue)
        self.status = (issue["fields"]["status"]["name"],)
        self.storyPoints = (
            issue["fields"]["customfield_10004"]
            if "customfield_10004" in issue["fields"]
            else 0
        )

    def __str__(self) -> str:
        return super().__str__()


class Epic(IssueBase):
    def __init__(self, epic: Dict, stories: List[Issue]):
        super().__init__(epic)
        epic_stories = [s for s in stories if s.parent.key == self.key]
        self.stories = epic_stories

        epicStoryPoints = 0
        for s in epic_stories:
            if s.storyPoints:
                epicStoryPoints += s.storyPoints
            else:
                print("found a story {} without a storyPoint value".format(s.key))
        self.storyPoints = epicStoryPoints

    def __str__(self) -> str:
        return super().__str__()


class Vapp(IssueBase):
    def __init__(self, key: str, epics: List[Epic]):
        vapp_epics = [e for e in epics if e.parent.key == key]
        parent_summary = vapp_epics[0].parent.summary or "BLANK VAPP"
        super().__init__(
            {"key": key or BLANK_VAPP_KEY, "fields": {"summary": parent_summary}}
        )
        self.epics = vapp_epics
        self.storyPoints = 0

        for e in self.epics:
            self.storyPoints += e.storyPoints

    def add_epic(self, epic):
        self.epics.append(epic)
        self.storyPoints += epic.storyPoints

    def __str__(self) -> str:
        return super().__str__()


class Sprint:
    def __init__(self, value):
        #              2021-08-23T17:00:31.245Z
        date_format = "%Y-%m-%dT%H:%M:%S.%fZ"

        self.id = value["id"]
        self.name = value["name"]

        # sometimes there are no startDate and endDate values
        # In this case, let's just make those values unmeaningful
        if 'startDate' in value and 'endDate' in value:
            self.start_date = datetime.datetime.strptime(
                value["startDate"], date_format
            ).date()
            self.end_date = datetime.datetime.strptime(value["endDate"], date_format).date()
        else:
            self.start_date = datetime.date.today()
            self.end_date = datetime.date.today()



def wrangle_no_epic_stories(vapps: List[Vapp], stories: List[Issue]):
    """
    Add any stories that have empty parent keys and put then in the blank vapp.
    """
    vapp_list = vapps
    # wrangle any last stories that were not in epics
    no_epic_stories = [s for s in stories if s.parent.key == ""]
    if no_epic_stories:
        for v in vapp_list:
            if v.key == BLANK_VAPP_KEY:
                v.add_epic(
                    Epic({"key": "", "fields": {"summary": "NO EPIC"}}, no_epic_stories)
                )
                break

    return vapp_list
