#!/usr/bin/env python
#coding='utf-8'

import sys

day = int(sys.argv[1])

days = int(sys.argv[2])

for i in range(days):

    file = open('inter_routes','r')

    file2 = open('ctripFlightcontent_'+str(day+i) +'.txt','w')

    for line in file:
        airports = line.strip().split('\t')
    
        orig = airports[0].strip()

        for airport in airports[1:]:
            file2.write(orig + '&' + airport.strip() + '&' + str(day+i) + '\n')
    
    file.close()

    file2.close()
