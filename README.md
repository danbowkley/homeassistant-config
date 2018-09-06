# homeassistant-config
My Home Assistant configuration files

This is a pretty straightforward and somewhat old-school Hass config. I'm not using Custom UI or Lovelace, at least so far.

Interesting tidbits include SNMP monitoring of a color laser printer, an Appdaemon app that controls my thermostat, and some creative tracking of my ISP average download speed.

To-do: 
  Get HTML5 notifications working.
    This is core to Home Automation Made Evil: I need actionable notifications to turn the sprinklers on when Karl comes over.
  Get Google Hangouts messages working. This is gonna be REALLY fun.
    Automation: if the trash hasn't gone out, send a Hangouts nag-o-gram to whoever is home.
    Stephen (to group chat): It's really hot in the house today. Hass: Well yeah, dumbass, I didn't know you were home!
  Get the humidity sensor in my CT-101(Iris) thermostat reporting properly
  Figure out why the HP-iLo component takes so bloody long to update and fix it
  Figure out why my bathroom fan automation only works sometimes (it triggers when it's supposed to, but it often doesn't actually turn the fan on or off) and fix it
  Get motion detection through the UniFi cameras working again (it worked back around 0.45 or so)
  Clean up recorder so it isn't recording stupid crap and intermediate sensor values (such as the printer toner capacity and raw level, just store the calculated % level)
  Build an integration for Mojio (T-Mobile SyncUp Drive) device tracking
  Build an integration for APRS (amateur radio GPS position tracking and remote telemetry) device tracking
