release: flask db upgrade
web: newrelic-admin run-program gunicorn w_app.app:create_app\(\) -b 0.0.0.0:$PORT -w 3
