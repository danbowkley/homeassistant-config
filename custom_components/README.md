goals:
    Device tracking via APRS. It will listen for transmissions by the specified callsign and translate them into device_tracker positions.
        Eventually, add proper telemetry message parsing to allow battery tracking, temperature monitoring, and so on.
        
    Notifications via APRS. Receive notifications from your house on your APRS TNC. Extra handy if you're out and about with your APRS-enabled HT.
    
    Telemetry updates via APRS. You could set up a beacon to tell the world what the humidity is in your bathroom. Don't know why you'd want to do that, but you could.






config params:
    aprs_callsign:      MANDATORY   this will be your base amateur radio callsign, as issued by your government authority (FCC in the US)
    aprs_is_key:        MANDATORY   This is the key required to access the APRS-IS servers. It is required to transmit, not to receive.
    aprs_taccall:       OPTIONAL    tactical callsign to use. For the device_tracker component, this is the tactical call for the device you're tracking (my truck is -14, for example).
                                    For the notification component, this is the target device. Odds are, this will be the same as the device_tracker taccall. This is ONLY the -xx at the end.
    aprs_from_taccall:  OPTIONAL    Tactical call to show as the tx station, when used for notifications

example
