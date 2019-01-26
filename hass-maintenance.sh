#!/bin/bash
echo "Stopping Home Assistant..."
sudo service home-assistant@homeassistant stop
echo "Deleting joe backup files"
sudo find -name '*~' -exec rm '{}' \;
echo "Setting file permissions"
sudo chown -R homeassistant:homeassistant * .*
sudo find . -type d -exec setfacl -m 'u:danb:rwx' '{}' \;
sudo find . -type f -exec setfacl -m 'u:danb:rw' '{}' \;
sudo find -name '*.sh' -exec setfacl -m 'u:danb:rwx' '{}' \;
echo "Backing up database..."
if mysqldump --login-path=hass --create-options --routines --triggers --verbose hass > /mnt/backups/Dan/hass-backup/db.dmp ; then
   echo "Database successfully backed up"
else
   echo "Database backup failed, exiting"
   exit 1
fi
echo "Checking database..."
if mysqlcheck --login-path=hass --check --databases hass ; then
   echo "Database checks OK"
else
   echo "Database checks failed, attempting to repair"
   if mysqlcheck --login-path=hass --repair --databases hass ; then
      echo "Database successfully repaired"
   else
      echo "You\'re hosed, bro..."
   fi
fi
echo "Optimizing database..."
mysqlcheck --login-path=hass --optimize --databases hass
echo "Copying all files to backup directory..."
sudo cp -R /home/homeassistant/.homeassistant/* /mnt/backups/Dan/hass-backup/
echo "Starting Home Assistant..."
sudo service home-assistant@homeassistant start
echo "Done!"
