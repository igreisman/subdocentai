# Backups

## What needs backing up

The code is in GitHub. What is not in GitHub is everything a curator changes
through the admin screens, which lives on the Render persistent disk (`/data`):

- `videos.jsonl`, the FAQ corpus and categories, the glossary, the operations
  guide, incidents, Eternal Patrol, Medal of Honor, museums and museum pages
- uploaded images (`faq_uploads/`, `museum_uploads/`)
- unpublished pages under `/data/web/`
- visitor feedback (`feedback.jsonl`)

A redeploy keeps all of this. A lost or corrupted disk does not. Render's own
disk snapshots are not something we control, so we keep our own copies.

## How it works

`GET /admin/backup` (admin login required) returns a tar.gz of the whole
persistent disk, minus the TTS audio cache, which is large and regenerates
itself. `?include_cache=1` adds it.

`scripts/backup_site.py` downloads that archive to a dated file under
`~/Backups/submarinedocent/`, verifies it opens, unpacks the newest one into
`latest/` so single files are easy to grab, and deletes archives older than
60 days. A typical archive is about 2 MB, so a year of nightly copies is under
a gigabyte.

## One-time setup on your Mac

1. Create the credentials file. It is the only place the password lives.

       mkdir -p ~/.config/submarinedocent
       cat > ~/.config/submarinedocent/backup.env <<'EOF'
       SITE=https://submarinedocent.org
       ADMIN_USERNAME=your-admin-username
       ADMIN_PASSWORD=your-admin-password
       EOF
       chmod 600 ~/.config/submarinedocent/backup.env

2. Run it once by hand to confirm it works.

       mkdir -p ~/Backups/submarinedocent
       python3 ~/Documents/submarinedocent/scripts/backup_site.py

   You should see `saved ... unpacked to ...`.

3. Install the nightly job (3:30 a.m.; runs on wake if the Mac was asleep).

       cp ~/Documents/submarinedocent/scripts/org.submarinedocent.backup.plist ~/Library/LaunchAgents/
       launchctl load ~/Library/LaunchAgents/org.submarinedocent.backup.plist

   To run it immediately as a test:

       launchctl start org.submarinedocent.backup
       tail ~/Backups/submarinedocent/backup.log

   To stop it: `launchctl unload ~/Library/LaunchAgents/org.submarinedocent.backup.plist`

## Checking that it is working

`ls -l ~/Backups/submarinedocent/` should show a new file each morning. If the
Mac was off overnight the job runs at the next wake. `backup.log` records every
run, and any failure (wrong password, site down, bad archive) exits non-zero
with a plain-English reason.

## Restoring

To restore one file (say, `videos.jsonl` after a bad edit):

1. Take it from `~/Backups/submarinedocent/latest/data/` or unpack an older
   archive with `tar -xzf submarinedocent-DATE.tar.gz`.
2. For videos, `scripts/import_videos.py` can push records back through the
   admin API (`--update-existing` to overwrite fields).
3. For anything else, or to restore everything, use Render's shell for the
   service (Dashboard, the service, "Shell") and copy the files into `/data/`.
   Render also supports `render ssh` from the CLI, which lets you `scp` a whole
   directory.

Because the archive keeps the original directory layout under `data/`, a full
restore is `tar -xzf` into `/data` and a service restart.

## Off-site copy

`~/Backups/submarinedocent/` is on one Mac. If that Mac is backed up by Time
Machine or iCloud Drive, the archives go with it. If not, consider pointing
`BACKUP_DIR` in `backup.env` at a folder that is (for example
`~/Library/Mobile Documents/com~apple~CloudDocs/Backups/submarinedocent`).
