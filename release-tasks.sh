#!/usr/bin/env bash

if [ ! -d migrations ]; then
  flask db init
fi

flask db upgrade
