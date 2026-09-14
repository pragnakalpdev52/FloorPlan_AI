#!/usr/bin/env bash
# Launch Label Studio, configured to serve images straight out of this repo's
# data/real_tests/ folder (no need to re-upload them into Label Studio's own
# media store).
set -euo pipefail
cd "$(dirname "$0")/.."

export LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
export LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT="$(pwd)/data"

# Project "floorplans" was already created (label_studio/label_config.xml,
# login annotator@local.floorplan / FloorplanAnnotate123, local files storage
# already synced from data/real_tests). Just re-launch it:
exec .venv-labelstudio/bin/label-studio start floorplans -p 8080 --no-browser
