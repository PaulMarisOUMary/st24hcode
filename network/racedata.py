#
# Notes:
# - To reduce the data stream for the BLE connection, we use float(4) instead
#   of double(8), signed char(1) and signed short(2) instead of int(4).
#   The total byte size for car dynamic data is: 12 Bytes
#        status(char1) + position(char1) + orientation(short2) + x(float4) + y(float4)
#   So total for 16 cars + meta data = 205 Bytes
#        status(char1) + counter(uint4) + timestamp(ulonglong 8) + 16 x car data(12)
# - Below classes may be implemented with "dataclasses" but it is not available
#   on Python older version.
#
# TODO add debug traces under a flag
#

import json
import struct
import time

PACK_ENDIANNESS = "<" # little endian (Intel, Arm, Android...)

class Car:
    PACK_STR_NO_ENDIANNESS = "bbhff" # Only for dynamic car data
    PACK_STR = PACK_ENDIANNESS + PACK_STR_NO_ENDIANNESS

    CAR_STATUS_IN_RACE     = 96
    CAR_STATUS_RUNWAY_EXIT = 97
    CAR_STATUS_PIT_STOP    = 98
    CAR_STATUS_OUT_OF_RACE = 99
    CAR_STATUS_LAST = CAR_STATUS_OUT_OF_RACE # Do no forget to update this one when adding more status
    CAR_STATUS_LEGEND_STR = "Car status: OOR = Out Of Race, PS = Pit Stop, RE = Runway Exit, IR = In Race"

    def __init__(self, team_name: str, pilot_names: str, car_number: int):
        self.team: str = team_name
        self.pilots: str = pilot_names
        self.car_number: int = car_number
        self.set_dynamic_data()

    def set_dynamic_data(self, status: int = CAR_STATUS_OUT_OF_RACE, position: int = 0, orientation: int = 0, x: float = 0.0, y: float = 0.0):
        self.status: int = status
        self.position: int = position
        self.orientation: int = orientation
        self.x: float = x
        self.y: float = y

    def get_dynamic_data(self):
        # important: return order need to be the same as set_dynamic_data due to
        # pack/unpack usage later... TODO not so nice, should be improved...
        return self.status, self.position, self.orientation, self.x, self.y

    def get_status_str(self) -> str:
        return get_car_status_str(self.status)


class RaceData:
    MAX_CARS = 16
    
    RACEDATA_STATUS_STOPPED = 0
    RACEDATA_STATUS_STARTED = 1
    RACEDATA_STATUS_SLOW    = 2
    RACEDATA_STATUS_LEGEND_STR = "Race status: STOPPED, STARTED, RACING SLOWLY"


    PACK_STR = PACK_ENDIANNESS + "bIQ" # status(char1) + counter(uint4) + timestamp(ulonglong 8)

    def __init__(self, max_cars: int = MAX_CARS, json_filename: str = ""):
        if max_cars > self.MAX_CARS:
            print("ERROR __init__(): too many cars")
            assert False

        self.cars = []

        self.max_cars: int = max_cars
        self.last_id: int = 0
        self.status: int = RaceData.RACEDATA_STATUS_STOPPED # byte in the data stream
        self.counter: int = 0 # unsigned short in the data stream
        self.timestamp: int = 0 # unsigned long long in the data stream
        self.pack_str: str = self.PACK_STR

        # Load data from the json file if requested
        if json_filename != "":
            #print("INFO RaceData: Loading car data from \"{}\"".format(json_filename))
            with open(json_filename, "r") as f:
                json_data = json.load(f)
            #print(json_data, type(json_data), len(json_data))
            self.max_cars = len(json_data)
            for car in json_data:
                l = list(car.values())
                #print("add_car", *l[0:3], "set_car_data", *l[3:])
                id = self.add_car(*l[0:3])
                self.set_car_data(id, *l[3:])

    def add_car(self, team_name: str, pilot_names:str, car_number: int) -> int:
        id = self.last_id
        if id < self.max_cars:
            self.cars.append(Car(team_name, pilot_names, car_number))
            self.pack_str += Car.PACK_STR_NO_ENDIANNESS
            #print(self.pack_str)
            #print(self.cars[id])
            self.last_id += 1
        else:
            print("ERROR add_car(): not enough space in the structure!")
            assert False
        return id

    def __check_id(self, id: int):
        # check if no item or bad id
        if (self.last_id == 0) or (id >= self.last_id) or (id < 0):
            print("ERROR __check_id(): bad car id")
            assert False

    def get_car_full_data(self, id: int):
        self.__check_id(id)
        return vars(self.cars[id])

    def get_car_data(self, id: int):
        self.__check_id(id)
        return self.cars[id].get_dynamic_data()

    # Often called but only by the server for updating car data
    def set_car_data(self, id: int, status: int, position: int, orientation: int, x: float, y: float):
        self.__check_id(id)
        self.cars[id].set_dynamic_data(status, position, orientation, x, y)

    # Often called but only by the server for packing data to broadcast
    def pack_race_data(self) -> bytes:
        # prepare data before packing
        # TODO not so nice, to be improve in the future, anyway, done only by the server
        data = []
        for car in self.cars:
            data.extend(car.get_dynamic_data())
        #print(data)
        self.counter += 1
        self.timestamp = time.time_ns()
        byte_stream = struct.pack(self.pack_str, self.status, self.counter, self.timestamp, *data)
        #print(byte_stream)
        return byte_stream

    # Only called by the viewing client (HUD)
    def unpack_and_update_race_data(self, byte_stream: bytes):
        # TODO not so nice, to be improve in the future, anyway, done only by the server
        self.status, self.counter, self.timestamp, *d = struct.unpack(self.pack_str, byte_stream)
        print(self.status, self.counter, self.timestamp, *d)
        for car in self.cars:
            car.set_dynamic_data(*d[0:5])
            del d[0:5]

    def get_race_data(self, ordered: bool = False) -> dict:
        output = []
        for car in self.cars:
            output.append(vars(car))

        if ordered:
            # TODO this function should be in the car class
            def get_position(elem):
                return elem.get('position')
            output.sort(key=get_position)

        return output

    def __repr__(self) -> str:
        s: str = "{:>6} {:>2} {:>3} {:<15}{:<80}\n".format("Status", "P.", "N.", "Teams", "Pilots")
        for car in self.cars:
            s += " {:>3}  {:>2} {:>3}  {:<15}{:<80}\n".format(car.get_status_str(), car.position, car.car_number, car.team, car.pilots)
        s += Car.CAR_STATUS_LEGEND_STR + "\n"
        s += "Race status: {}".format(self.get_status_str())
        return s

    def json_save_to_file(self, filename: str):
        cars = self.get_race_data(ordered=True)
        json_data = json.dumps(cars, indent=4)
        with open(filename, "w") as f:
            f.write(json_data)

    def get_status_str(self) -> str:
        return get_race_status_str(self.status)


### Helpers for "simple" client (ie. without using the RaceData class)

# Rarely called, only by clients
def get_car_data_unpack_offset(car_id: int) -> int:
    # IMPORTANT there is no check on car_id
    # Important: endianness (< or >) MUST be used when using struct.calcsize() else results may be not correct
    # print(struct.calcsize(self.pack_str), struct.calcsize(self.PACK_STR), struct.calcsize(Car.PACK_STR), struct.calcsize(Car.PACK_STR_NO_ENDIANNESS))
    return struct.calcsize(RaceData.PACK_STR) + (car_id * struct.calcsize(Car.PACK_STR))

# Often called, only by clients (no need to have any data in this class)
def unpack_car_data_and_meta(byte_stream: bytes, car_data_unpack_offset: int):
    race_status, counter, ts = struct.unpack_from(RaceData.PACK_STR, byte_stream, 0)
    #ts, = ts # from tuple to simple variable
    car_status, position, orientation, x, y = struct.unpack_from(Car.PACK_STR, byte_stream, offset=car_data_unpack_offset)
    return car_status, position, orientation, x, y, race_status, counter, ts

# Sometimes called, mostly by HUD clients
def unpack_meta(byte_stream: bytes):
    race_status, counter, ts = struct.unpack_from(RaceData.PACK_STR, byte_stream, 0)
    return race_status, counter, ts

# May be useful for clients
def get_number_of_cars_in_a_byte_stream(byte_stream: bytes) -> int:
    nb_cars = (len(byte_stream) - struct.calcsize(RaceData.PACK_STR)) // struct.calcsize(Car.PACK_STR)
    return nb_cars

# May be useful for clients
def get_car_status_str(status) -> str:
    if status == Car.CAR_STATUS_OUT_OF_RACE:
        status_str = "OOR"
    elif status == Car.CAR_STATUS_PIT_STOP:
        status_str = " PS"
    elif status == Car.CAR_STATUS_RUNWAY_EXIT:
        status_str = " RE"
    elif status == Car.CAR_STATUS_IN_RACE:
        status_str = " IR"
    else:
        status_str = "---"
    return status_str

# May be useful for clients
def get_race_status_str(status) -> str:
    if status == RaceData.RACEDATA_STATUS_STOPPED:
        status_str = "STOPPED"
    elif status == RaceData.RACEDATA_STATUS_STARTED:
        status_str = "STARTED"
    elif status == RaceData.RACEDATA_STATUS_SLOW:
        status_str = "RACING SLOWLY"
    else:
        status_str = "------"
    return status_str
