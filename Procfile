web: NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program gunicorn -k gevent  -w 1 app:server --preload  --log-file -
log: tail -f log/development.log
