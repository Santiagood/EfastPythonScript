import RPi.GPIO as GPIO
import time
import pymysql.cursors
from datetime import datetime
now = datetime.now()

GPIO.setmode(GPIO.BCM)

TRIG = 23
ECHO = 24
samp = 100
discard = int(samp * 0.2)

print("Distance Measurement In Progress")

GPIO.setup(TRIG,GPIO.OUT)
GPIO.setup(ECHO,GPIO.IN)
summedtimes = 0
pulse_start = 0
pulse_end = 0
avgdist = 0

#data that will be sent to the database
river_level  = None
river_status = None
river_year   = None
river_month  = None
river_day    = None
river_time   = None
river_date   = None
created_at   = None
updated_at   = None


timelist = []
try:
    for x in range(0, samp):
       GPIO.output(TRIG, False)
       time.sleep(0.010)
       
       GPIO.output(TRIG, True)
       time.sleep(0.000011)
       GPIO.output(TRIG, False)
       
       while GPIO.input(ECHO)==0:
           pulse_start = time.time()
           
       while GPIO.input(ECHO)==1:
           pulse_end = time.time()
        
       pulse_duration = pulse_end - pulse_start
       timelist.append(pulse_duration)
       print('Reading ' + str(x+1) + '/' + str(samp), str(pulse_duration))
       
    timelist.sort(key=None)

    for y in range(discard, (samp - discard)):
        summedtimes += timelist[y]
        
    sumdist = summedtimes * 34300 * 0.5
    avgdist = int((sumdist / (samp - discard * 2)))

    if avgdist >= 23 and avgdist <= 600:
        print('Distance: ', avgdist, ' cm')
        meterAvgdist = avgdist / 100;
        print('Distance: ', meterAvgdist, 'meters')
        #river_level assign
        river_level = meterAvgdist;
        
        #check the river status:
        #river_status assign
        if meterAvgdist <= 14.9:
            river_status = "Normal"
        elif meterAvgdist >= 15 and meterAvgdist < 16:
            river_status = "1st Alarm"
        elif meterAvgdist >= 16 and meterAvgdist < 17:
            river_status = "2nd Alarm"
        elif meterAvgdist >= 17 and meterAvgdist < 18:
            river_status = "3rd Alarm"
        elif meterAvgdist >= 18 and meterAvgdist < 19:
            river_status = "4th Alarm"
        else:
            river_status = "Beyond 4th Alarm"
            
        #date assign
        river_date=datetime.now().strftime('%Y-%m-%d')
        
        #time assign
        river_time=datetime.now().strftime('%I:%M %p')
        
        #year assign
        river_year=datetime.now().strftime('%Y')
        
        #month assign
        river_month=datetime.now().strftime('%B')
        
        #day assign
        river_day=datetime.now().strftime('%d')
        
        #created_at
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        #updated_at
        updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        connection=pymysql.connect(
            host='',
            port=,
            user='',
            password='',
            db='',
            charset='',
            cursorclass=pymysql.cursors.DictCursor)
        
        with connection.cursor() as cursor:
            #create a new record
            sql="INSERT INTO `river_levels` (`river_status`,`river_level`,`year`,`month`,`day`,`time`,`created_at`,`updated_at`,`date`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (river_status,river_level,river_year,river_month,river_day,river_time,created_at,updated_at,river_date))
        
        connection.commit()
        connection.close()
        
    else:
        print('Error reading ', avgdist, 'cm')
        meterAvgdist = avgdist / 100;
        print('Distance: ', meterAvgdist, 'meters')


    with open('/home/EfastKalumpang/EfastPythonScript/EfastLog.txt', 'a') as f:
        f.write('Last EFAST river level check is on: {} || river-level: {} meters || river-status: {} || date: {} || time: {} ||year: {} || month: {} || day: {} \n\n'.format(now, river_level, river_status, river_date, river_time, river_year, river_month, river_day))

    GPIO.cleanup()
    print("Done")
    

except KeyboardInterrupt: # If there is a KeyboardInterrupt (when you press ctrl+c), exit the program
    print("Cleaning up!")
    GPIO.cleanup()
