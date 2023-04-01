#
# Example of an udp multicast client receiving data for a given car,
#       including all racedata, qos and timestamp examples
#
# Note: Please refer to "udp_multicast_client_minimalist_version.py"
#       for a shorter/simplier example.
#

import mcastsocket
import racedata
import time

### Network part
client = mcastsocket.MCastClient()

### Data part
# Receive a byte stream and get related number of cars
byte_stream = client.recv()
nb_cars = racedata.get_number_of_cars_in_a_byte_stream(byte_stream)

car_id = 1              # <----- PUT HERE YOUR CAR ID
ofs = racedata.get_car_data_unpack_offset(car_id)

### Log part (qos, performance...)
DEFAULT_FPS = 30.0 # Note: only here for logging as fps depends on the server data!
LOG_COUNTER_DEFAULT = int(DEFAULT_FPS * 4)
log_counter = LOG_COUNTER_DEFAULT
log_time = time.time()
received_frames = 0
not_received_frames = 0
previous_counter = 0

print("### Running (CTRL+C to close)...")
while True:
    # Get data from the udp multicast socket
    byte_stream = client.recv()
    if byte_stream is None:
        continue

    # Example of unpacking only one car data
    car_status, position, orientation, x, y, race_status, counter, timestamp_ns = racedata.unpack_car_data_and_meta(byte_stream, ofs)

    # Example of timestamp conversion
    timestamp_sec = timestamp_ns // 1000000000
    ms = (timestamp_ns - (timestamp_sec * 1000000000)) // 1000000
    readable_timestamp = time.strftime("%d %b %Y, %H:%M:%S", time.localtime(timestamp_sec))
    readable_timestamp = "{},{}".format(readable_timestamp, ms)
    #print(readable_timestamp)

    # Check if any missing frame (qos)
    if (counter != previous_counter + 1) and (previous_counter != 0):
        not_received_frames += 1
        print("warning: data frame \"{}\" not received, total not_received_frames {}".
              format(previous_counter + 1, not_received_frames))
    previous_counter = counter

    received_frames += 1

    # Log part (Example of displaying all race data)
    log_counter -= 1
    if log_counter == 0:
        print("Race information: status \"{}\", counter {}, ts {}".
              format(racedata.get_race_status_str(race_status), counter, readable_timestamp))
        print("Cars information: car_id, status, position, orientation, x, y")
        for i in range(nb_cars):
            offset = racedata.get_car_data_unpack_offset(i)
            car_status, position, orientation, x, y, _, _, _ = racedata.unpack_car_data_and_meta(byte_stream, offset)
            print("{:2}, {:2}, {:2}, {:3}°, {: 4.1f}, {: 4.1f}".
                  format(i, racedata.get_car_status_str(car_status), position, orientation, x, y))
        print(racedata.Car.CAR_STATUS_LEGEND_STR)

        log_counter = LOG_COUNTER_DEFAULT
        tt = time.time()
        speed = float(LOG_COUNTER_DEFAULT) / (tt - log_time)
        log_time = tt
        qos = 100.0 * (1.0 - (not_received_frames / (not_received_frames + received_frames)))
        print("Log: frames received {} / not received {} / qos {:.1f}%, {:.0f} frames/s\n".
              format(received_frames, not_received_frames, qos, speed))
