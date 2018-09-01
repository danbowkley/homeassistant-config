#!/bin/bash
service home-assistant@homeassistant stop
mysqldump -u hassuser -p=Ep8nLKd9RJ3z6lRM --create-options --routines --triggers hass > ./db.dmp
mysqlcheck -u hassuser -p=Ep8nLKd9RJ3z6lRM --check --databases hass
mysqlcheck -u hassuser -p=Ep8nLKd9RJ3z6lRM --optimize --databases hass
service home-assistant@homeassistant start
