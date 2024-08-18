#!/usr/bin/python3

"""Simple and dumb Immich server updater.

Compares the current server version with the version of the latest release on
Github. If there has been a major version update -OR- the release notes say
"breaking change" (case-insensitive) anywhere, then it aborts. Otherwise, if
there has been a version change, will do `docker pull`, `docker compose up -d`.

Limitations:
This script is DUMB. It's literally looking for a string in the release notes.
Also, this script only looks at the notes of the LATEST release. That means
that it needs to be run often (daily? weekly?) to make sure that it does not
miss a "breaking change" release between runs.
"""

import re
import sys
import requests
import sh


# Where do the Immich docker-compose.yml and .env files live?
IMMICH_DIR = '/opt/immich'


# Retrieve currently-install version from the API.
# JSON dictionary object with 'major', 'minor', and 'patch' keys.
r = requests.get('http://localhost:2283/api/server-info/version', timeout=30)
curr_vers = r.json()
curr_vers_str = (f'v{curr_vers["major"]}.{curr_vers["minor"]}'
                 f'.{curr_vers["patch"]}')

# Retrieve the latest release info from github.
r = requests.get(
    "https://api.github.com/repos/immich-app/immich/releases/latest",
    allow_redirects=True, timeout=30)
release_data = r.json()

# Extract release version from 'tag_name' or 'name'.
# It will be a string in the form of 'v<major>.<minor>.<patch>'.
latest_version_str = release_data['tag_name']
latest_version = latest_version_str.lstrip('v').split('.')

# If major version has changed, assume there will be breaking changes.
if int(latest_version[0]) != int(curr_vers['major']):
    print('Immich-Updater: Detected a major version change.'
          ' Will not proceed with the update. Currently-installed version:'
          f' {curr_vers_str} / latest release: {latest_version_str}.')
    sys.exit(0)

# If no other changes, then can be done.
if (int(latest_version[1]) == int(curr_vers['minor'])
        and int(latest_version[2]) == int(curr_vers['patch'])):
    sys.exit(0)

# If there has been a minor version change, then need to check the release
# notes for a breaking changes.
# Do not do this for a patch update only, because the "breaking..." warning is
# repeated in patch updates if there was one in the minor update.
if int(latest_version[1]) != int(curr_vers['minor']):
    for line in release_data['body'].splitlines():
        # Dumb regex search for literaly "breaking change".
        # This has been a consistent pattern in the release notes for a while.
        if re.search('breaking change', line, re.IGNORECASE) is not None:
            # Line found
            print('Immich-Updater: A breaking change has been detected when'
                  ' comparing the currently-installed version'
                  f' ({curr_vers_str}) to the latest release'
                  f' ({release_data["tag_name"]}). Will not proceed with the'
                  ' update.')
            sys.exit(0)

# If we made it this far, then there has been an update and no breaking
# changes have been detected. Ok to proceed with update.

# Build a docker SH command
docker = sh.Command('docker')
docker = docker.bake(_err_to_out=True, _cwd=IMMICH_DIR)

# pull
print('Immich-Updater: Updating to the latest version.')
print(docker('compose', 'pull'))

# reload
print('Immich-Updater: Reloading server.')
print(docker('compose', 'up', '-d'))

sys.exit(0)
