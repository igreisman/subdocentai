# Pampanito Deployment Checklist

This checklist is for deploying SubmarineDocent for live use on USS Pampanito or in the museum environment.

## Scope

- [ ] Confirm the target deployment mode:
- [ ] `On-prem/local network` for the live Pampanito tour and museum devices.
- [ ] `Render/cloud` only for the public website if that is still needed in parallel.
- [ ] Confirm the production entry URL that visitors should use.
- [ ] Confirm whether the deployment is `tour only` or `tour + FAQ + Eternal Patrol + feedback/contact features`.

## Content Freeze

- [ ] Freeze the web content to be deployed from [web](../web).
- [ ] Freeze the corpora to be deployed from [corpora](../corpora).
- [ ] Verify the Pampanito tour stops and labels in [web/pampanito.html](../web/pampanito.html).
- [ ] Verify the tour media manifest in [web/pampanito-tour-cues.js](../web/pampanito-tour-cues.js).
- [ ] Verify all required video files are present under [web/videos](../web/videos).
- [ ] Verify required images are present under [web/images](../web/images).
- [ ] Verify FAQ corpus and category files are final if the FAQ site is part of the deployment.
- [ ] Verify Eternal Patrol data is final if that page is part of the deployment.

## Hardware And OS

- [ ] Identify the production machine that will host the app.
- [ ] Confirm the host OS and version.
- [ ] Confirm the machine has stable power, automatic restart behavior, and enough disk space for media.
- [ ] Confirm Python 3.9+ is installed.
- [ ] Confirm the repo has been copied to the target machine.
- [ ] Confirm the Python virtual environment is created and dependencies install cleanly from [requirements.txt](../requirements.txt).

## Network

- [ ] Assign a stable local IP address or DHCP reservation to the host machine.
- [ ] Record the final visitor URL.
- [ ] Do not assume a single Wi‑Fi signal will propagate reliably through the submarine.
- [ ] Treat full-vessel BYOD coverage as a hard launch requirement.
- [ ] Perform a compartment-by-compartment connectivity survey on the real vessel.
- [ ] Identify dead zones, weak-signal areas, and spaces where visitor devices fail to stay connected.
- [ ] Decide whether the final network model is:
- [ ] `Single access point` only if live testing proves it is reliable across the full visitor path.
- [ ] `Multiple access points with wired backhaul` if compartments need separate coverage to satisfy full-vessel BYOD.
- [ ] Confirm museum Wi‑Fi or local LAN coverage reaches every area that must support the experience.
- [ ] Confirm that failure to achieve full-vessel BYOD coverage is a `no-go` for launch.
- [ ] Confirm the device firewall allows the chosen ports.
- [ ] If certain hostnames should land on the tour page, set `TOUR_HOST_PREFIXES` explicitly and verify the configured prefixes are intentional.

## TLS And Browser Trust

- [ ] Decide whether visitors will use HTTP or HTTPS.
- [ ] If using HTTPS on-site, generate or install the production certificate and key in [certs](../certs).
- [ ] Verify the certificate subject matches the actual URL visitors will open.
- [ ] Trust the certificate on museum-managed iPhones/iPads if self-signed certs are used.
- [ ] Test microphone access on the real visitor devices, because speech features are sensitive to browser security context and certificate trust.

## Secrets And Environment Variables

- [ ] Create a local `.env.local` file on the deployment machine if using the HTTPS startup flow.
- [ ] Set `GROQ_API_KEY` if server-side transcription is required.
- [ ] Decide whether `SMTP_USER` and `SMTP_PASS` should be set to enable contact/feedback email sending.
- [ ] Confirm SMTP credentials are app-specific credentials, not a personal primary password.
- [ ] Decide whether `OPENAI_API_KEY` is needed for this deployment. The current repo primarily uses Groq for transcription and an internal stub for answer synthesis, so this may not be required for on-prem launch.
- [ ] Decide whether `USE_LLM` should remain off or be enabled.
- [ ] Set `ADMIN_USERNAME` and `ADMIN_PASSWORD` before exposing curator pages or `/admin/*` routes.
- [ ] Decide whether `PREVIEW_USERNAME` and `PREVIEW_PASSWORD` should protect the tour preview.

## Runtime Choice

- [ ] Choose the startup path:
- [ ] `Local HTTPS launch` via [start_https.sh](../start_https.sh) on port `8443`.
- [ ] `Plain uvicorn HTTP launch` via `uvicorn api.main:app --host 0.0.0.0 --port 8000`.
- [ ] Prefer the HTTPS path if visitor devices will use speech recognition or microphone-driven features.
- [ ] Confirm startup commands are wrapped in `launchd`, `systemd`, or another auto-restart mechanism for production.

## App Behavior Review

- [ ] Confirm the root-route behavior is correct for the production host.
- [ ] Confirm whether the welcome page should be shown on first visit.
- [ ] Confirm whether the `visited=1` cookie skip behavior is acceptable for shared visitor devices.
- [ ] Confirm whether preview protection should rely on `PREVIEW_USERNAME` and `PREVIEW_PASSWORD`.
- [ ] Set `LOCAL_HTTPS_HOST` and related startup variables if the deployment machine should advertise a non-default host or port.
- [ ] Review any links in [web/welcome.html](../web/welcome.html) that point to external services or analytics.

## Data Persistence And Backups

- [ ] Decide which files must be writable in production.
- [ ] Confirm how visitor feedback will be retained.
- [ ] Confirm how contact submissions will be retained if SMTP is unavailable.
- [ ] Back up the corpora before launch.
- [ ] Back up [web/pampanito-tour-cues.js](../web/pampanito-tour-cues.js) and all media assets before launch.
- [ ] Define a rollback plan to the last known-good repo snapshot.

## Pre-Launch Smoke Tests

- [ ] Verify the server starts without errors.
- [ ] Verify the tour page loads at the final URL.
- [ ] Verify the FAQ page loads if it is part of the deployment.
- [ ] Verify the Eternal Patrol page loads if it is part of the deployment.
- [ ] Verify [api/main.py](../api/main.py) `GET /health` returns successfully.
- [ ] Verify `POST /ask` works from the Pampanito page.
- [ ] Verify `POST /transcribe` works if `GROQ_API_KEY` is configured.
- [ ] Verify `POST /feedback` succeeds.
- [ ] Verify `POST /contact` succeeds or logs safely if SMTP is intentionally disabled.

## Tour-Specific Tests

- [ ] Test every Pampanito stop in the selector.
- [ ] Verify each stop plays the correct primary media.
- [ ] Verify `After Deck` video plays.
- [ ] Verify `After Torpedo` video plays from the configured file mapping.
- [ ] Verify compartments without videos behave as expected.
- [ ] Verify `Audio Tour` hides visual media as intended.
- [ ] Verify `Video Tour` shows the first frame when available.
- [ ] Verify the play/pause button works on iPhone and desktop.
- [ ] Verify seeking on the progress bar works.
- [ ] Verify switching between audio and video preserves position well enough for live use.

## Device Tests

- [ ] Test on at least one iPhone on the real museum network.
- [ ] Test on at least one Android device if Android visitors are expected.
- [ ] Test on one staff desktop or laptop if staff will demo from a non-phone device.
- [ ] Walk the full visitor route with real phones and confirm they remain connected end to end.
- [ ] Test microphone permissions and question asking on real devices.
- [ ] Test page reload behavior and caching after a content update.
- [ ] Confirm no stale cached copy of [web/pampanito-tour-cues.js](../web/pampanito-tour-cues.js) is being used.

## Operations And Monitoring

- [ ] Decide who owns day-of-launch support.
- [ ] Document how to restart the service.
- [ ] Document where logs are written.
- [ ] Document how to verify that the server is listening on the expected port.
- [ ] Document how to replace a tour video or cue manifest without breaking the deployment.
- [ ] Document who updates corpora, tour cues, and static media after launch.

## Museum Handoff

- [ ] Prepare a one-page operator runbook.
- [ ] Provide the final visitor URL to museum staff.
- [ ] Provide the restart command to museum staff.
- [ ] Provide the location of media and cue files to the content owner.
- [ ] Provide the rollback procedure to the technical owner.
- [ ] Record all final IPs, hostnames, ports, and credentials storage locations in a private ops document.

## Final Go/No-Go

- [ ] All required pages load at the production URL.
- [ ] All required tour stops play correctly.
- [ ] Speech, feedback, and contact behavior match the intended museum experience.
- [ ] Staff have restart instructions.
- [ ] Backups exist.
- [ ] Rollback path is tested.
- [ ] Launch approved.
