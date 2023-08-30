from typing import List
from models import Vapp


def print_header(
    story_length: int,
    total_story_points: int,
    total_days: int,
    pto_days: int,
    sprint_names: List[str],
    args,
):
    d = {
        "Total Stories:": story_length,
        "Total Story Points:": total_story_points,
        "Total Working Days:": total_days,
    }

    if pto_days:
        d["PTO Days:"] = pto_days

    max_key_length = 0
    for k in d.keys():
        if len(k) > max_key_length:
            max_key_length = len(k)

    print("\nEffort Report for %s" % args.user)
    print("{:{fill}<{width}}".format("", fill="-", width=max_key_length + 10))
    for k in d.keys():
        key, val = (
            "{:{fill}<{width}}".format(k, width=max_key_length + 3, fill="."),
            d[k],
        )
        print("{} {}".format(key, val))

    print("")
    print(f"Found {len(sprint_names)} sprints between {args.start} and {args.end}")
    for n in sprint_names:
        print(f"🗓️  {n}")

    print("")


def print_vapps(vapps: List[Vapp]):
    print("Details")
    print("{:{fill}<{width}}".format("", fill="-", width=50))
    for vapp in vapps:
        print("📦 {} {}".format(vapp, vapp.storyPoints))
        for epic in vapp.epics:
            print(" 📁 {} {}".format(epic, epic.storyPoints))
            for story in epic.stories:
                print(" ↳ {} {}".format(story, story.storyPoints))
        print("")


def print_summary(
    vapps: List[Vapp],
    total_story_points: int,
    total_percent: int,
    pto_days: int,
    total_days: int,
):
    max_key_length = 0
    for v in vapps:
        if len(str(v)) > max_key_length:
            max_key_length = len(str(v))

    print("Summary")
    print("{:{fill}<{width}}".format("", fill="-", width=max_key_length + 15))

    for vapp in vapps:
        print(
            "📦 %s %d (%s)"
            % (
                "{:{fill}<{width}}".format(
                    str(vapp),
                    width=max_key_length + 3,
                    fill=".",
                ),
                vapp.storyPoints,
                "{:.0f}%".format(vapp.storyPoints / total_story_points * total_percent),
            )
        )

    if pto_days:
        print(
            "🌴 %s %d (%s)"
            % (
                "{:{fill}<{width}}".format(
                    "PTO Days", width=max_key_length + 3, fill="."
                ),
                pto_days,
                "{:.0f}%".format(pto_days / total_days * 100),
            )
        )

    print("")
