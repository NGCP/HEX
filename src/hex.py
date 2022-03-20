from dronekit import Vehicle
#functions of the MEA
#Step 1) we need to have a autopilot takeoff
#Step 2) we need a standby or loiter function, maintains the current altitude
#Step 3) we need a autopilot point a to b (when GCS say that MEA needs to go to home)
#Step 4) we need a autopilot landing on home, set altitude to 0
#Step 5) we need an override for the autopilot to manual
#step 6) Payload integration function (secondary issue)

class HEX(Vehicle):
  def __init__(self, *args):
    pass

  def setup(self):
    pass

  def coms_callback(self, command):
    pass

  def start_auto_mission(self):
    pass

  def takeoff(self):
    pass

  def go_to(self, point):
    pass

  def land(self):
    pass

  def set_altitude(self, alt):
    pass

  def change_status(self, new_status):
    pass

  def send_attitude_target(
      self,
      roll_angle=0.0,
      pitch_angle=0.0,
      yaw_angle=None,
      yaw_rate=0.0,
      use_yaw_rate=False,
      thrust=0.5
      ):
    pass

  def set_attitude(
      self,
      roll_angle=0.0,
      pitch_angle=0.0,
      yaw_angle=None,
      yaw_rate=0.0,
      use_yaw_rate=False,
      thrust=0.5
      ):
    pass

  def update_thread(self, address):
    pass

