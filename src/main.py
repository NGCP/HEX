from digi.xbee.devices import DigiMeshDevice
#from pymavlink import mavutil
from xbee import TransmitThread, ToMAC, ToGCS, Orientation, LatLng, ManualControl, Geofence, read_lock
#import mavlink_msg_MAC

from enum import IntEnum
import threading
import queue
import struct
import time

class StatesMEA(IntEnum):
    LOITER = 0          # Loiter at the current altitude in a circle
    TAKEOFF = 1         # Switch to manual controls and takeoff
    DRIVE_EZ = 7    # Radio search for the hiker
    TRANSFER_HIKER = 8        # Payload drop
    LANDING = 9         # Switch to manual controls and land


class XBeeReceiver:
    def __init__(self, num_items : int, device : DigiMeshDevice):
        self.device = device                                # the managed xbee, used to receive data as a string of bytes (a.k.a. packet)
        self.num_items = num_items                          # the size of the data and decode queues
        self.packet_counter = 0                             # counter used anticipate the number of packets to be received
        self.packet_buffer = []                             # temporary buffer used to combine multiple packets into one; necessary for when data
                                    # from the managed xbee exceeds the maximum packet size
        self.data_queue = queue.Queue(num_items)            # queue used to hold the data to be deserialized
        self.decode_queue = queue.Queue(num_items)          # the queue that holds decoded packets for the main script
        self.transmit_thread = None                         # will be set to the managed transmit thread by the start_decode_thread() method

        # Set received packets to be placed in the packet buffer as soon as our xbee device receives them
        self.device.add_data_received_callback(self.receive_packets)
    
    def receive_packets(self, packet):
        '''Used to preprocess packets received from GCS and put them into a queue to await deserialization.
           Since one message from GCS may exceed the maximum packet length, multiple packets may be used to
           send over one message. The preprocessing done by this function collects all those packets up into
           one byte array, where it is then saved in data_queue as one complete message.'''

        if self.packet_counter == 0:
            # Upon having received all packets, prepare the packet buffer to be stored in data_queue
            self.packet_counter = struct.unpack("d", packet.data[:8])[0] -1 
            data = packet.data[8:]
            self.packet_buffer = b''
        else:
            # The entire series of packets containing the message has yet to be fully preprocessed,
            # so put this packet's data into the buffer and go to the next packet
            self.packet_counter -= 1
            data = packet.data
        
        self.packet_buffer += data

        # Upon having received all packets and the buffer has been prepared, store the data in the queue to
        # await deserialization
        if self.packet_counter == 0:
            with read_lock:
                self.data_queue.put(self.packet_buffer)
                self.packet_buffer = []

    def decode_packet(self):
        '''Decodes the next packet in the data queue if there is one.  Is passed to a TransmitThread object,
           which will run it in a loop for the lifetime of that object, by the start_decode_thread() method.'''
        try:
            data = self.data_queue.get_nowait()
            self.decode_queue.put(ToMAC.deserialize(data))
        except queue.Empty:
            # If the packet buffer is empty, do nothing
            # The TransmitThread object will call this function in the next iteration of its loop,
            # so nothing is done here to simply let the thread check again
            pass

    def start_decode_thread(self):
        '''Creates the thread which constantly checks the encode queue for data to serialize and transmit.'''
        self.transmit_thread = TransmitThread(self.decode_packet)
        self.transmit_thread.start()

    def __del__(self):
        # Removes the function that places packets in the packet buffer from the list of functions called when the 
        # managed xbee device receives data
        self.device.del_data_received_callback(self.receive_packets)

class XBeeSender:
    def __init__(self, num_items : int, device : DigiMeshDevice):
        self.device = device                                # the managed xbee, used to send data as a string of bytes (a.k.a. packet)
        self.num_items = num_items                          # the size of the encode queue
        self.encode_queue = queue.Queue(num_items)          # the queue that holds packets to be encoded and transmitted from the main script
                                                            # all items on the queue should be a tuple (id_of_recipient_xbee, data)
        self.transmit_thread = None                         # will be set to the managed transmit thread by the start_encode_thread() method
        
    def encode_packet(self):
        '''Serializes and transmits the next either ToMAC, ToGCS, ToERU, or ToMEA class found on the encode queue.
           Sends the data to the xbee specified by the id packaged with the data on the encode queue. Is passed to a 
           TransmitThread object, which will run it in a loop for the lifetime of that object, by the 
           start_decode_thread() method.'''
        try:
            data = self.encode_queue.get_nowait()
            data[1].serialize().transmit(self.device, data[0])
        except queue.Empty:
            # If the encode queue is empty, do nothing
            # The TransmitThread object will call this function in the next iteration of its loop,
            # so nothing is done here to simply let the thread check again
            pass
    
    def start_encode_thread(self):
        '''Creates the thread which constantly checks the encode queue for data to serialize and transmit.'''
        self.transmit_thread = TransmitThread(self.encode_packet)
        self.transmit_thread.start()

def get_devices(device):
    print("Getting devices")

    network = device.get_network()
    network.start_discovery_process()

    while network.is_discovery_running():
        time.sleep(.01)
    
    devices = {dev.get_node_id():dev._64bit_addr for dev in network.get_devices()}
    devices[device.get_node_id()] = device._64bit_addr

    print("This device's name: ", device.get_node_id())
    print("Discovered ", devices)

    return devices

def main():
    # Set up communication devices
    comm_port = "COM4"
    baud_rate = "9600"

    device = DigiMeshDevice(port=comm_port, baud_rate=baud_rate)
    device.open()

    devices = get_devices(device)

    num_items = 9
    #decoded_packets = queue.Queue(num_items)  # buffer of classes holding decoded packet data FIFO
    #encoded_packets = queue.Queue(num_items)  # buffer of data to encode to gcs FIFO
    
    # initialize constantly-run threads
    xbee_receiver = XBeeReceiver(num_items, device)
    xbee_sender = XBeeSender(num_items, device)

    # start constantly-run threads
    xbee_receiver.start_decode_thread()
    xbee_sender.start_encode_thread()
    #xbee_decode_thread = TransmitThread(xbee_receiver.decode_packet)
    #xbee_decode_thread.start()

    while True:
        # Check if data has been decoded and sent back to main script queue
        try:
            gcs_cmd = xbee_receiver.decode_queue.get_nowait()
            
            # series of conditionals for event-based functions
            if gcs_cmd.perform_state == StatesMEA.LOITER:
                print("Loiter at the current altitude in a circle")
            elif gcs_cmd.perform_state == StatesMEA.TAKEOFF:
                print("Switch to manual controls and takeoff")
            elif gcs_cmd.perform_state == StatesMEA.DRIVE_EZ:
                print("Radio search for the hiker")
            elif gcs_cmd.perform_state == StatesMEA.TRANSFER_HIKER:
                print("Payload drop")
            elif gcs_cmd.perform_state == StatesMEA.LANDING:
                print("Switch to manual controls and land")
            else:
                print("not a recognized state")
            
        except queue.Empty:
            pass
        finally:
            pass
        # check on constantly run functions
        # check if data needs to be encoded and place in queue
        cmd = input("Press y to send packet to GCS\n")
        if cmd == "y":
            recipient = devices['gcs']
            data = ToGCS(20.0, 50.0, Orientation(50.0, 120.0, 270.0), LatLng(33.933729, -117.6318437), 90, True, 3, False, LatLng(21.4, 8.0), 4, True, True)
            xbee_sender.encode_queue.put((recipient, data))

    # Close all communication
    device.close()

if __name__ == "__main__":
    main()


