#
# Minimalist example of an udp multicast client receiving data for a given car
#
# Note: Please refer to "udp_multicast_client.py" for more details about
#       car data (timestamp decoding, counter for qos...)
#

import mcastsocket      # Used to manage network socket in udp multicast
import racedata         # Contains direct helpers and the class RaceData

### Network part
client = mcastsocket.MCastClient()

### Data part
car_id = 1              # <----- PUT HERE YOUR CAR ID
ofs = racedata.get_car_data_unpack_offset(car_id)

while True:
    # Get data from the udp multicast socket and unpack them
    byte_stream = client.recv()
    if byte_stream is None:
        continue

    # Unpack your car data
    car_status, position, orientation, x, y, race_status, counter, timestamp_ns = racedata.unpack_car_data_and_meta(byte_stream, ofs)

    # Do whatever you want with your car data...
    print("car status {:2}, position {:2}, orientation {:3}°, x {: 6.1f}, y {: 6.1f}, race status {:2}, counter {:6}, {:}".
        format(car_status, position, orientation, x, y, race_status, counter, timestamp_ns))
