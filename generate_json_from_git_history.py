import os
import json

import git

from generate_json_notams import pib_to_json, write_json

# Try running this under the python jit/compiler? How do you speed up pygit?

repo = git.Repo()
path = "data/PIB.xml"

commits = list(repo.iter_commits(paths=path))
commits.reverse()
total = len(commits)
count = 0

# Swap seen to be a dict of notams that contains unpublished date (if it exists) and the filepath to it, and if we've seen it this run
# Seen is now a bad name, maybe existing?
# Before running in single run mode, load all notams from disk into this struct
# When running in history replay mode, start with nothing
# When we see a notam in the PIB, mark it as seen in this run
# When we hit a notam that is a replacement, open the previous notam and mark it as replaced, and give it the new notam ID/date
# # We may not HAVE the previous notam, so handle that, maybe flag it?
# When we finish a single run, find all existing notams with an unpublished date that we didn't just see, and update their unpublished date to now
# When we finish a commit in the history replay and we didn't see them, use the date of the commit they vanished in

existing = {}
unpublished = set()

#   for root, dirs, files in os.walk("json"):
#       for file in files:
#           if file.endswith('.json'):
#               _, nid, series = file.split("_")
#               series, _ = series.split(".")
#               notam_id = f"{nid}/{series}"
#               existing[notam_id] = os.path.join(root, file)

for commit in commits:
    count += 1
    print(f"{count}/{total}: Processing {commit} from {commit.authored_datetime}")

    seen_in_version = set()

    pib_body = (commit.tree / path).data_stream.read()
    for json_notam in pib_to_json(pib_body, existing_notams=existing):
        json_path = write_json(json_notam)
        existing[json_notam["id"]] = json_path
        seen_in_version.add(json_notam["id"])

        if json_notam["replaces"]:
            print(f"{json_notam['id']} replaces {json_notam['replaces']['id']}")
            replaced_notam_path = existing.get(json_notam["replaces"]["id"])
            if replaced_notam_path:
                with open(replaced_notam_path, "r") as f:
                    data = json.load(f)
                    data["replaced_by"] = json_notam["id_fields"]
                    data["replaced_by"]["id"] = json_notam["id"]

                with open(replaced_notam_path, "w") as f:
                    json.dump(data, f, indent=4, separators=(",", ": "))


    inactive_notams = set(existing.keys()) - unpublished - seen_in_version
    for notam_id in inactive_notams:
        unpublished.add(notam_id)

        print(f"{notam_id} unpublished on {commit.authored_datetime}")
        with open(existing[notam_id], "r") as f:
            data = json.load(f)
            data["date"]["unpublished"] = commit.authored_datetime.replace(tzinfo=None).isoformat()

        with open(existing[notam_id], "w") as f:
            json.dump(data, f, indent=4, separators=(",", ": "))
