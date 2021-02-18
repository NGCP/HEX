import attr
# TODO:add import statements


@attr.s                                                       #Defines class as an attr type class
class Coms():
  '''Compartmentalizes coms functionality and scope'''
  configs = attr.ib()
  xbee_callback = attr.ib()

  def send_till_ack(self):
    # TODO: implement
    pass

  def acknowledge(self):
    # TODO: implement
    pass

  def new_msg_id(self):
    # TODO: implement
    pass

  def receive(self):
    # TODO: implement
    pass

  def send(self):
    # TODO: implement
    pass

  def bad_msg(self):
    # TODO: implement
    pass

  def comm_simulation(self):
    # TODO: implement
    pass
