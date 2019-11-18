release: flask db upgrade
web: newrelic-admin run-program gunicorn home_budgeting_app.app:create_app\(\) -b 0.0.0.0:$PORT -w 3
