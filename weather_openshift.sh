#! /bin/bash
source "$VIRTUAL_ENV"/bin/activate
python "$OPENSHIFT_REPO_DIR"weather/weather.py >> "$OPENSHIFT_PYTHON_LOG_DIR"weather.log 2>&1
deactivate
