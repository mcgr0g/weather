#! /bin/bash
cd /srv/www && source .virtualenvs/p27temp/bin/activate && weather/weather.py >> weather/cron.log 2>&1
deactivate