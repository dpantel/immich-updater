# Immich Updater

Simple and dumb Immich server updater.

Compares the current server version with the version of the latest release on Github. If there has been a major version update **OR** the release notes say "breaking change" (case-insensitive) anywhere, then it aborts. Otherwise, if there has been a version change, will do `docker pull`, `docker compose up -d`.

## Limitations

This script is **DUMB**!

It's literally looking for a string in the release notes.

Also, this script only looks at the notes of the LATEST release. That means that it needs to be run often (daily? weekly?) to make sure that it does not miss a "breaking change" release between runs.

## Installation & Running

1. Copy the script to a location of your choice. I recommend `/etc/cron.daily/` or `/etc/cron.weekly/` so that it runs on a schedule (see Limitations).
1. Edit the `IMMICH_DIR` variable at the top of the script to point to the correct location.
1. Make it executable.

If there is nothing to do, there is no output. Anything else prints messages to STDOUT.

## Requirements
- Python v3.8+
- Python [sh](https://github.com/amoffat/sh) module v2+
- Docker compose
