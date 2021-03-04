from dronekit import Vehicle

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

