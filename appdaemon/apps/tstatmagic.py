import appdaemon.plugins.hass.hassapi as hass

###############################################################################
# Dan's super de duper automagic thermostat setting app                       #
# Dan Bowkley <danbowkley@gmail.com>                                          #
#                                                                             #
# Ver. 1.3                                                                    #
# Using proximity to set temperature rather than just presence                #
#                                                                             #
# WARNING: Author doesn't know squat about Python; if it doesn't have line    #
# numbers he becomes agitated and may attempt to bite his own ear off.  This  #
# app may run better on a TRS-80, as that is the last platform for which he   #
# managed to write a program that actually ran without releasing magic smoke. #
#                                                                             #
#   * In all seriousness, this app is free and you got what you paid for. *   #
#                                                                             #
# CLOAD SAUCER, baby...                                                       #
###############################################################################
#
# sample appdaemon.cfg section:
# [Thermostatic Magic]
# module = tstatmagic
# class = tstatmagic
# heat_tstat = climate.2gig_technologies_ct101_thermostat_iris_heating_1_2_1
# cool_tstat = climate.2gig_technologies_ct101_thermostat_iris_cooling_1_2_2
# proximity_home = proximity.home
# sensor_doorsopen = sensor.doorsopen
# constrain_input_boolean = input_boolean.hvac_automation
# outside_temp = sensor.dark_sky_temperature
#
class tstatmagic(hass.Hass):
# Set our initial values. These will be tweaked as we go.
# These four target values will be used unless the outside temp goes above "bloody_hot" or below "bloody_cold" or nobody is home, as explained further below.
  day_cool_target = 75
  day_heat_target = 72
  night_cool_target = 72
  night_heat_target = 69
# If the outside temperature is really extreme, keep the temp between these values no matter what
  occupied_max_temp = 78
  occupied_min_temp = 55
# If nobody is home, we shouldn't bother keeping the place terribly comfy. Just keep my chocolate from melting and my pipes from freezing.
  unoccupied_max_temp = 84
  unoccupied_min_temp = 40
# Adjust the setpoint by miles/divisor up to the unoccupied max/min
  unoccupied_divisor = 2.5 
# The thermostat gets adjusted when above bloody_hot or below bloody_cold degrees outside. It's adjusted by 1/bloody_divisor degree for each degree above or below the bloody values.
# For example, if it's 100F outside, cool_target=75, bloody_hot=90F, and bloody_divisor=2, then the cooling setpoint would be 75+((100-90)/2) or 80F.
  bloody_hot = 88
  bloody_cold = 35
  bloody_divisor = 2.5
# 
# There be dragons here. Proceed with caution!
#
#
  def initialize(self):
    self.log("Starting Thermostatic Magic...")
    self.listen_state(self.change_temp, self.args["proximity_home"])           #Listen for proximity to change
    self.listen_state(self.change_openings, self.args["sensor_doorsopen"])     #Listen for openings to change. If an opening is open, it shuts off the system.
    self.listen_state(self.change_temp, self.args["outside_temp"])             #Listen for outside temperature to change
    
  def change_temp(self, entity, attribute, old, new, kwargs):                  #The brains live here; this is the routine that actually sets the thermostat setpoints.
    self.log("Change temp routine called.")
    self.distance = int(float(self.get_state(self.args["proximity_home"])))    #get the distance to the nearest resident, returns zero if home
    self.outside_temp = int(float(self.get_state(self.args["outside_temp"])))  #get the outside temperature
    self.log("Outside Temp: {0}".format(self.outside_temp))
    self.distance_offset = int(self.distance / self.unoccupied_divisor)        #set the temperature offset for distance. 
    self.log("Distance: {0}  Distance offset: {1}".format(self.distance,self.distance_offset))
    if self.sun_up():                                                          #set the base setpoints for daytime
        self.base_cool_target = self.day_cool_target
        self.base_heat_target = self.day_heat_target
    else:                                                                      #set the base setpoints for nighttime
        self.base_cool_target = self.night_cool_target
        self.base_heat_target = self.night_heat_target
    self.log("Base cool target: {0}  Base heat target: {1}".format(self.base_cool_target,self.base_heat_target))
    self.log("Occupied max: {0}  Occupied min: {1}".format(self.occupied_max_temp,self.occupied_min_temp))
    self.log("Unoccupied max: {0}  Unoccupied min: {1}".format(self.unoccupied_max_temp,self.unoccupied_min_temp))
    if self.outside_temp < self.bloody_cold:                                   #set the heat offset for bloody cold weather
        self.bloody_cool_offset = 0
        self.bloody_heat_offset = (self.bloody_cold-self.outside_temp)/self.bloody_divisor
    elif self.outside_temp > self.bloody_hot:                                  #set the AC offset for bloody hot weather
        self.bloody_cool_offset = (self.outside_temp-self.bloody_hot)/self.bloody_divisor
        self.bloody_heat_offset = 0
    else:                                                                      #set no "bloody" offsets for mild weather
        self.bloody_cool_offset = 0
        self.bloody_heat_offset = 0
    self.log("Bloody cool offset: {0}  Bloody heat offset: {1}".format(self.bloody_cool_offset,self.bloody_heat_offset))
    self.heat_target = max((max(self.base_heat_target-self.bloody_heat_offset,self.occupied_min_temp)-self.distance_offset),self.unoccupied_min_temp) #calculate the actual heating setpoint
    self.cool_target = min((min(self.base_cool_target+self.bloody_cool_offset,self.occupied_max_temp)+self.distance_offset),self.unoccupied_max_temp) #calculate the actual cooling setpoint
    self.log("Heat target: {0}  Cool target: {1}".format(self.heat_target,self.cool_target))
    self.adjust_heat_temp(self.heat_target)                                    #call function to set the heating thermostat
    self.adjust_cool_temp(self.cool_target)                                    #call function to set the cooling thermostat
    
  def change_openings(self,entity,attribute,old,new,kwargs):                   #Turn the heating and air conditioning on or off if the doors are closed or open, respectively
    self.log("change_openings called, self.get_state_sensor_doorsopen returns {0}".format(self.get_state(self.args["sensor_doorsopen"])))
    if self.get_state(self.args["sensor_doorsopen"]) == "on":                  #turn the system off if doors are open
      self.log("Door or window left open, setting thermostats to Off.")
      self.set_off()
    else:                                                                      #turn the system on if all doors are closed
      self.log("Doors and windows closed or unknown, setting thermostats to Auto.")
      self.set_auto()
    
  def set_auto(self):                                                          #sets thermostats to auto mode
# change the operation mode to match your system if you have two separate thermostats (both to 'on' should work)
# setting both heat and cool to auto is probably redundant, but it can't hurt either. I think.
    self.call_service("climate/set_operation_mode", entity_id = self.args["heat_tstat"], operation_mode = "Auto")
    self.call_service("climate/set_operation_mode", entity_id = self.args["cool_tstat"], operation_mode = "Auto")
    self.log("set_auto called, setting {0} and {1} to Auto.".format(self.args["heat_tstat"],self.args["cool_tstat"]))
    
  def set_off(self):                                                           #sets thermostats to off
# Again, changing both of these on a single thermostat system is probably redundant, but it can't hurt.
    self.call_service("climate/set_operation_mode", entity_id = self.args["heat_tstat"], operation_mode = "Off") 
    self.call_service("climate/set_operation_mode", entity_id = self.args["cool_tstat"], operation_mode = "Off") 
    self.log("set_off called, setting {0} and {1} to Off.".format(self.args["heat_tstat"],self.args["cool_tstat"]))

  def adjust_heat_temp(self,temp):                                             #set the heating thermostat
    self.call_service("climate/set_temperature", entity_id = self.args["heat_tstat"], temperature = temp)
    self.log("adjust_heat_temp called, setting {0} to {1}".format(self.args["heat_tstat"],temp))

  def adjust_cool_temp(self,temp):                                             #set the AC thermostat
    self.call_service("climate/set_temperature", entity_id = self.args["cool_tstat"], temperature = temp)
    self.log("adjust_cool_temp called, setting {0} to {1}".format(self.args["cool_tstat"],temp))
