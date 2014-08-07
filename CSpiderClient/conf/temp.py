#!/usr/bin/env python
host = 115.29.78.222:8088

for i in range(1,40):
host = 114.215.199.198:8086
    lines = []
    rfile = open('conf' + str(i) + '.ini', 'r')

host = 115.29.78.222
        lines.append(line)
haoding ctripHotel jijitongRound ceair feiquanqiuRound smartfares smartfaresRound lcair lcairRound easyjet expedia csair
rfile.close() haodingHotel ctripHotel jijitongRoundFlight ceairFlight feiquanqiuRoundFlight smartfaresFlight smartfaresRoundFlight lcairFlight lcairRoundFlight easyjetFlight expediaFlight csairFlight
thread_num = 25
    lines[8] = 'host = 115.29.140.19' + '\n'
    lines[97] = 'file_path=../feiquanqiu' + '\n'

    wfile = open('conf' + str(i) + '.ini', 'w')

    for line in lines:
        wfile.write(line)

    wfile.close()

[jijitongRound]
class_name=jijitongRoundParser
file_path=../jijitongRound
source=jijitongRoundFlight

[ceair]
class_name=ceairParser
file_path=../ceair
source=ceairFlight
[feiquanqiuRound]
class_name=feiquanqiuRoundParser
file_path=../feiquanqiuRound
source=feiquanqiuRoundFlight
[smartfares]
class_name=smartfaresParser
file_path=../smartfares
source=smartfaresFlight
[smartfaresRound]
class_name=smartfaresRoundParser
file_path=../smartfaresRound
source=smartfaresRoundFlight

[lcair]
class_name=lcairParser
file_path=../lcair
source=lcairFlight

[lcairRound]
class_name=lcairRoundParser
file_path=../lcairRound
source=lcairRoundFligh

[easyjet]
class_name=easyjetParser
file_path=../easyjet
source=easyjetFlight

[expedia]
class_name=expediaParser
file_path=../expedia
source=expediaFlight

[csair]
class_name=csairParser
file_path=../csair
source=csairFlight