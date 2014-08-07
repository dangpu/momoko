#!/usr/bin/env python

'''
    
'''

import sys
import db

def InsertFlight(args):
    #sql = "INSERT INTO flight" + table_name_date + " (flight_no,plane_no,airline,dept_id,dest_id,dept_day,dept_time," + \
            #"dest_time,dur,price,tax,surcharge,currency,seat_type,source,return_rule," + \
            #"stop) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    sql = "INSERT INTO flight (flight_no,plane_no,airline,dept_id,dest_id,dept_day,dept_time," + \
            "dest_time,dur,price,tax,surcharge,currency,seat_type,source,return_rule," + \
            "stop) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    return db.ExecuteSQLs(sql,args)

def InsertRoundFlight(args):
    sql = 'INSERT INTO flight_round (dept_id, dest_id, dept_day, dest_day, price, tax, surcharge, currency, source, return_rule,' + \
            'flight_no_A, airline_A, plane_no_A, dept_time_A, dest_time_A, dur_A, seat_type_A, stop_A, flight_no_B, airline_B, plane_no_B,' + \
            'dept_time_B, dest_time_B, dur_B, seat_type_B, stop_B) VALUES ( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, ' + \
            '%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'

    return db.ExecuteSQLs(sql,args)

def InsertHotel(args):
    sql = 'INSERT INTO hotel (hotel_name,hotel_name_en,source,source_id,brand_name,map_info,address,city,' + \
            'country,postal_code,star,grade,has_wifi,is_wifi_free,has_parking,is_parking_free,service,' + \
            'img_items, description) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

    return db.ExecuteSQLs(sql,args)

def InsertHotel_room(args):
    sql = 'INSERT INTO room (hotel_name, city, source, source_hotelid,source_roomid,real_source,room_type,' + \
            'occupancy, bed_type, size, floor, check_in, check_out, price, tax, currency, is_extrabed, is_extrabed_free,has_breakfast,' + \
            'is_breakfast_free,is_cancel_free, room_desc) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

    return db.ExecuteSQLs(sql,args)

def InsertHotel_comment(args):
    sql = 'INSERT INTO hotel_comment (hotel_name, city, source, source_hotelid, title, comment, comment_user)' + \
            ' VALUES( %s,%s,%s,%s,%s,%s,%s)'

    return db.ExecuteSQLs(sql,args)

def InsertTask(args):
    sql = "INSERT INTO workload (task,source,task_type,priority,crawl_day,crawl_hour,update_times,success_times,batch_id)" + \
            "VALUES (%s, %s, %s ,%s, %s, %s, %s, %s, %s)"

    return db.ExecuteSQLs(sql,args)


