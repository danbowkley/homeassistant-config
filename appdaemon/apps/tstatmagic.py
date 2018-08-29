import appdaemon.plugins.hass.hassapi as hass

###############################################################################
# Dan's super de duper automagic thermostat setting app                       #
# Dan Bowkley <danbowkley@gmail.com>                                          #
#                                                                             #
# Ver. 1.0                                                                    #
# First release, amazingly enough it doesn't crash (yet)                      #
# WARNING: Author doesn't know squat about Python, if it doesn't have line    #
# numbers he becomes agitated and may attempt to bite his own ear off.  This  #
# app may run better on a TRS-80, as that is the last platform for which he   #
# managed to write a program that actually ran without releasing magic smoke. #
###############################################################################
#
# Note: add logic to make sure it doesn't exceed unoccupied_targets when people are home. They should be max and min values.
#
# sample appdaemon.cfg section:
#[Thermostatic Magic]
#module = tstatmagic
#class = tstatmagic
#heat_tstat = climate.2gig_technologies_ct101_thermostat_iris_heating_1_2_1
#cool_tstat = climate.2gig_technologies_ct101_thermostat_iris_cooling_1_2_2
#device_tracker = group.people
#group_doorswindows = group.doorsandwindows
#constrain_input_boolean = input_boolean.hvac_automation
#outside_temp = sensor.pws_feelslike_f
#
class tstatmagic(hass.Hass):
# Set our initial values. These will be tweaked as we go.
# These four target values will be used unless the outside temp goes above "bloody_hot" or below "bloody_cold" as explained further below.
  day_cool_target = 75
  day_heat_target = 65
  night_cool_target = 69
  night_heat_target = 60
# If the outside temperature is really extreme, keep the temp between these values no matter what
  occupied_max_temp = 80
  occupied_min_temp = 55
# If nobody is home, we shouldn't bother keeping the place terribly comfy. Just keep my chocolate from melting and my pipes from freezing.
  unoccupied_cool_target = 84
  unoccupied_heat_target = 40
# The thermostat gets adjusted when above bloody_hot or below bloody_cold degrees outside. It's adjusted by 1/bloody_divisor degree for each degree above or below the bloody values.
# For example, if it's 100F outside, cool_target=75, bloody_hot=90F, and bloody_divisor=2, then the cooling setpoint would be 75+((100-90)/2) or 80F.
  bloody_hot = 90
  bloody_cold = 35
  bloody_divisor = 2.5

  def initialize(self):
    self.log("Starting Thermostatic Magic...")
    self.listen_state(self.change_temp, self.args["device_tracker"])         #This should be a group of people to track, not just every device in the home. I don't care if my smart TV gets hot.
    self.listen_state(self.change_openings, self.args["group_doorswindows"]) #One group that includes all your outside-opening doors and windows. If an opening is open, it shuts off the system.
    self.listen_state(self.change_temp, self.args["outside_temp"])           #A sensor for the outside temperature. I use a Weather Underground value, if you have an outside thermometer use that instead.

  def change_temp(self, entity, attribute, old, new, kwargs):
    self.outside_temp = int(float(self.get_state(self.args["outside_temp"])))
    if self.anyone_home():                                                                  #occupied
      if self.bloody_cold <= self.outside_temp <= self.bloody_hot:                          #happy temp
        if self.sun_up():                                                                   #day
          self.log("Happy temp daytime occupied, outside temp {0}, setting heat target to {1} and cool target to {2}.".format(self.outside_temp,self.day_heat_target,self.day_cool_target))
          self.adjust_heat_temp(self.day_heat_target)
          self.adjust_cool_temp(self.day_cool_target)
        else:                                                                                #night
          self.log("Happy temp nighttime occupied, outside temp {0}, setting heat target to {1} and cool target to {2}.".format(self.outside_temp,self.night_heat_target,self.night_cool_target))
          self.adjust_heat_temp(self.night_heat_target)
          self.adjust_cool_temp(self.night_cool_target)
      elif self.bloody_cold > self.outside_temp:                                            #bloody cold
        if self.sun_up():                                                                   #bloody cold day (wait, seriously? in Florida?! Better raise an error. This ain't right.)
          self.log("Bloody cold daytime occupied, outside temp {0}, setting heat target to {1} and cool target to {2}.".format(self.outside_temp,max(self.day_heat_target-((self.bloody_cold-self.outside_temp)/self.bloody_divisor),self.occupied_min_temp),self.day_cool_target))
          self.adjust_heat_temp(max(self.day_heat_target-((self.bloody_cold-self.outside_temp)/self.bloody_divisor),self.occupied_min_temp))
          self.adjust_cool_temp(self.day_cool_target)
        else:                                                                               #bloody cold night
          self.log("Bloody cold nighttime occupied, outside temp {0}, setting heat target to {1} and cool target to {2}.".format(self.outside_temp,max(self.night_heat_target-((self.bloody_cold-self.outside_temp)/self.bloody_divisor),self.occupied_min_temp),self.night_cool_target))
          self.adjust_heat_temp(max(self.night_heat_target-((self.bloody_cold-self.outside_temp)/self.bloody_divisor),self.occupied_min_temp))
          self.adjust_cool_temp(self.night_cool_target)
      else:                                                                                 #Must be bloody hot then. Duh, it's Florida! Should raise an error if this isn't met, actually.
        if self.sun_up():                                                                   #bloody hot day, as usual
          self.log("Bloody hot daytime occupied, outside temp {0}, setting heat target to {1} and cool target to {2}.".format(self.outside_temp,self.day_heat_target,min(self.day_cool_target+((self.outside_temp-self.bloody_hot)/self.bloody_divisor),self.occupied_max_temp)))
          self.adjust_cool_temp(min(self.day_cool_target+((self.outside_temp-self.bloody_hot)/self.bloody_divisor),self.occupied_max_temp))
          self.adjust_heat_temp(self.day_heat_target)
        else:                                                                               #bloody hot night
          self.log("Bloody hot nighttime occupied, outside temp {0}, setting heat target to {1} and cool target to {2}.".format(outside_temp,self.night_heat_target,min(self.night_cool_target+((self.outside_temp-self.bloody_hot)/self.bloody_divisor),self.occupied_max_temp)))
          self.adjust_cool_temp(min(self.night_cool_target+((self.outside_temp-self.bloody_hot)/self.bloody_divisor),self.occupied_max_temp))
          self.adjust_cool_temp(self.night_cool_target)            
    else:                                                                                   #unoccupied, back the temps off.
      self.log("Unoccupied mode, outside temp {0}, setting heat target to {1} and cool target to {2}.".format(self.outside_temp,self.unoccupied_heat_target,self.unoccupied_cool_target))
      self.adjust_heat_temp(self.unoccupied_heat_target)
      self.adjust_cool_temp(self.unoccupied_cool_target)
   
  def change_openings(self,entity,attribute,old,new,kwargs):
#    self.log("change_openings called, self.get_state_group_doorswindows returns {0}".format(self.get_state(self.args["group_doorswindows"])))
    if self.get_state(self.args["group_doorswindows"]) == "open":
      self.log("Door or window open, setting thermostats to Off.")
      self.set_off()
    else:
      self.log("Doors and windows closed or unknown, setting thermostats to Auto.")
      self.set_auto()
    
  def set_auto(self):
# change the operation mode to match your system if you have two separate thermostats (both to 'on' should work)
# setting both heat and cool to auto is probably redundant, but it can't hurt either. I think.
    self.call_service("climate/set_operation_mode", entity_id = self.args["heat_tstat"], operation_mode = "Auto")
    self.call_service("climate/set_operation_mode", entity_id = self.args["cool_tstat"], operation_mode = "Auto")
    self.log("set_auto called, setting {0} and {1} to Auto.".format(self.args["heat_tstat"],self.args["cool_tstat"]))
    
  def set_off(self):
# Again, changing both of these on a single thermostat system is probably redundant, but it can't hurt.
    self.call_service("climate/set_operation_mode", entity_id = self.args["heat_tstat"], operation_mode = "Off") 
    self.call_service("climate/set_operation_mode", entity_id = self.args["cool_tstat"], operation_mode = "Off") 
    self.log("set_off called, setting {0} and {1} to Off.".format(self.args["heat_tstat"],self.args["cool_tstat"]))

  def adjust_heat_temp(self,temp):
    self.call_service("climate/set_temperature", entity_id = self.args["heat_tstat"], temperature = temp)
    self.log("adjust_heat_temp called, setting {0} to {1}".format(self.args["heat_tstat"],temp))

  def adjust_cool_temp(self,temp):
    self.call_service("climate/set_temperature", entity_id = self.args["cool_tstat"], temperature = temp)
    self.log("adjust_cool_temp called, setting {0} to {1}".format(self.args["cool_tstat"],temp))
