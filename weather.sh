#! /bin/bash
cd /srv/www && source .virtualenvs/p27temp/bin/activate && temp/weather.py >> temp/cron.log 2>&1
deactivate