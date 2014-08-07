#!/usr/bin/env python
#coding=UTF8
'''

'''

import sys

reload(sys)

class Flight():
    def __init__(self):
        self.flight_no = 'NULL'
        self.plane_no = 'NULL'
        self.airline = 'NULL'
        self.dept_id = 'NULL'
        self.dest_id = 'NULL'
    	self.dept_day = 'NULL'
        self.dept_time = 'NULL'
        self.dest_time = 'NULL'
        self.dur = -1
        self.price = -1.0
        self.tax = -1.0
        self.surcharge = -1.0
        self.currency = 'NULL'
        self.seat_type = 'NULL'
        self.source = 'NULL'
        self.return_rule = 'NULL'
        #self.book_url = 'NULL'
        self.stop = -1

    def items(self):
        results = []
        for k,v in self.__dict__.items():
            results.append((k, str(v).decode("UTF-8")))
        return results


class RoundFlight():
    def __init__(self):
        self.dept_id = 'NULL'
        self.dest_id = 'NULL'
        self.dept_day = 'NULL'
        self.dest_day = 'NULL'
        self.price = -1.0
        self.tax = -1.0
        self.surcharge = -1.0
        self.currency = 'NULL'
        self.source = 'NULL'
        self.return_rule = 'NULL'
        self.flight_no_A = 'NULL'
        self.airline_A = 'NULL'
        self.plane_no_A = 'NULL'
        self.dept_time_A = 'NULL'
        self.dest_time_A = 'NULL'
        self.dur_A = -1
        self.seat_type_A = 'NULL'
        self.stop_A = -1
        self.flight_no_B = 'NULL'
        self.airline_B = 'NULL'
        self.plane_no_B = 'NULL'
        self.dept_time_B = 'NULL'
        self.dest_time_B = 'NULL'
        self.dur_B = -1
        self.seat_type_B = 'NULL'
        self.stop_B = -1

    def items(self):
        results = []
        for k,v in self.__dict__.items():
            results.append((k, str(v).decode('UTF-8')))
        return results

class EachFlight():
    def __init__(self):
        self.flight_key = 'NULL'
        self.flight_no = 'NULL'
        self.airline = 'NULL'
        self.plane_no = 'NULL'
        self.dept_id = 'NULL'
        self.dest_id = 'NULL'
        self.dept_time = 'NULL'
        self.dest_time = 'NULL'
        self.dur = -1
        
    def items(self):
        results = []
        for k,v in self.__dict__.items():
            results.append((k, str(v).decode('UTF-8')))
    
        return results

class Hotel():
    def __init__(self):
        self.hotel_name = 'NULL'
        self.hotel_name_en = 'NULL'
        self.source = 'NULL'
        self.source_id = 'NULL'
        self.brand_name = 'NULL'
        self.map_info = 'NULL'
        self.address = 'NULL'
        self.city = 'NULL'
        self.country = 'NULL'
        self.postal_code = 'NULL'
        self.star = -1.0
        self.grade = 'NULL'
        self.has_wifi = 'No'
        self.is_wifi_free = 'No'
        self.has_parking = 'No'
        self.is_parking_free ='No'
        self.service = 'NULL'
        self.img_items = 'NULL'
        self.description = 'NULL'
    
    def items(self):
        results = []
        for k,v in self.__dict__.items():
            results.append((k, str(v).decode("UTF-8")))
        return results


class Room():
    def __init__(self):
        self.hotel_name = 'NULL'
        self.city = 'NULL'
        self.source = 'NULL'
        self.source_hotelid = 'NULL'
        self.source_roomid = 'NULL'
        self.room_type = 'NULL'
        self.real_source = 'NULL'
        self.occupancy = -1
        self.bed_type = 'NULL'
        self.size = -1.0
        self.floor = -1
        self.check_in = 'NULL'
        self.check_out = 'NULL'
        self.price = -1.0
        self.tax = -1.0
        self.currency = 'NULL'
        self.is_extrabed = 'No'
        self.is_extrabed_free = 'No'
        self.has_breakfast = 'No'
        self.is_breakfast_free = 'No'
        self.is_cancel_free = 'No'
        self.room_desc = 'NULL'

    def items(self):
        results = []
        for k,v in self.__dict__.items():
            results.append((k, str(v).decode("UTF-8")))
        return results


class Comment():
    def __init__(self):
        self.hotel_name = 'NULL'
        self.city = 'NULL'
        self.source_hotelid = 'NULL'
        self.comment = 'NULL'
        self.comment_user = 'NULL'
        self.source = 'NULL'
        self.title = 'NULL'

    def items(self):
        results = []
        for k,v in self.__dict__.items():
            results.append((k, str(v).decode("UTF-8")))
        return results


class Car():
    def __init__(self):
        self.source = 'NULL'
        self.company = 'NULL'
        self.car_type = 'NULL'
        self.car_desc = 'NULL'
        self.price = -1.0
        self.list_price = -1.0
        self.store_name = 'NULL'
        self.store_addr = 'NULL'
        self.return_store_name = 'NULL'
        self.return_store_addr = 'NULL'
        self.take_time = 'NULL'
        self.return_time = 'NULL'
        self.is_automatic = 'NULL'
        self.baggages = -1
        self.passenagers = -1

    def items(self):
        results = []
        for k,v in self.__dict__.items():
            results.append((k, str(v).decode("UTF-8")))
        return results


class Attraction():
    def __init__(self):
        self.name = 'NULL'
        self.name_en = 'NULL'
        self.grade = 'NULL'
        self.city_id = 'NULL'
        self.map_info = 'NULL'
        self.address = 'NULL'
        self.phone = 'NULL'
        self.website = 'NULL'
        self.open = 'NULL'
        self.close = 'NULL'
        self.ticket = 'NULL'
        self.description = 'NULL'
        self.image = 'NULL'
        self.rcmd_visit_time = 'NULL'
    
    def items(self):
        results = []
        for k,v in self.__dict__.items():
            results.append((k, str(v).decode('utf-8')))
        return results
