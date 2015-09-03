import RPi.GPIO as GPIO, sys, threading, time

GPIO.setwarnings(False)

#use physical pin numbering
GPIO.setmode(GPIO.BOARD)

#set up digital line detectors as inputs
GPIO.setup(12, GPIO.IN)
GPIO.setup(13, GPIO.IN)

#use pwm on inputs so motors don't go too fast
GPIO.setup(19, GPIO.OUT)
p=GPIO.PWM(19, 20)
p.start(0)
GPIO.setup(21, GPIO.OUT)
q=GPIO.PWM(21, 20)
q.start(0)
GPIO.setup(24, GPIO.OUT)
a=GPIO.PWM(24,20)
a.start(0)
GPIO.setup(26, GPIO.OUT)
b=GPIO.PWM(26,20)
b.start(0)


#make a global variable to communicate between sonar function and main loop
globalstop=0
finished = False
fast = 40
slow = 20



#servo

GPIO.setmode(GPIO.BOARD)
pin= 22
GPIO.setup(pin,GPIO.OUT)
freq =50
pwm1= GPIO.PWM(pin, freq)
posList1 = [2.25]
posList2 = [.75]

msPerCycle= 1000/freq

#line following speed
linespeed = 20

grabbedbox = 0 # Haven't grabbed box


def stopall():
  p.ChangeDutyCycle(0)
  q.ChangeDutyCycle(0)
  a.ChangeDutyCycle(0)
  b.ChangeDutyCycle(0)     

# Arm movements     
def openx():
     dc1 = 2.25 * 100/msPerCycle
     pwm1.start(dc1)
     time.sleep(0.5)
     pwm1.ChangeDutyCycle(0)


def closex():
     dc1 = 0.75 * 100/msPerCycle
     pwm1.start(dc1)
     time.sleep(0.5)
     pwm1.ChangeDutyCycle(0)
     
def turnright():
  p.ChangeDutyCycle(0)
  q.ChangeDutyCycle(80)
  a.ChangeDutyCycle(80)
  b.ChangeDutyCycle(0)
  print 'turning right'

def turnrightslow():
  p.ChangeDutyCycle(0)
  q.ChangeDutyCycle(10)
  a.ChangeDutyCycle(10)
  b.ChangeDutyCycle(0)
  print 'slow right'

def turnsharpright():
  p.ChangeDutyCycle(0)
  q.ChangeDutyCycle(80)
  a.ChangeDutyCycle(90)
  b.ChangeDutyCycle(0)

def sonar():
    dist_list=[]
    for i in range(5): 
           GPIO_TRIGGER=8
           GPIO_ECHO=8
           GPIO.setup(8,GPIO.OUT)
           # Send 10us pulse to trigger
           GPIO.output(GPIO_TRIGGER, True)
           time.sleep(0.00001)
           GPIO.output(GPIO_TRIGGER, False)
           start = time.time()
           count=time.time()
           GPIO.setup(8,GPIO.IN)
           while GPIO.input(GPIO_ECHO)==0 and time.time()-count<0.1:
                   start = time.time()
           stop=time.time()
           while GPIO.input(GPIO_ECHO)==1:
                   stop = time.time()
           # Calculate pulse length
           elapsed = stop-start
           # Distance pulse travelled in that time is time
           # multiplied by the speed of sound (cm/s)
           distance = elapsed * 34000
           # That was the distance there and back so halve the value
           distance = distance / 2
           dist_list=dist_list+[distance]
           time.sleep(.01)
    sorted_list= sorted(dist_list)
       
    return sorted_list[2] 



try:
     openx()
     finish =1
     foundline=1
     while True:
          dist = sonar()
          print dist
          if dist < 7.5 and grabbedbox == 0:
                    #where you grab box
                    stopall()
                    print('stop')
                    closex()
                    grabbedbox = 1
                    foundline=0
                    #turn around w/ box
                    print 'grabbed box, turning right'
                    turnright()
                    time.sleep(.2)
                    stopall()
                    while GPIO.input(12) or GPIO.input(13):
                      print 'left', GPIO.input(12), 'right', GPIO.input(13)
                    while GPIO.input(12)==0 and GPIO.input(13)==0:
                      turnrightslow()
                      foundline=1
                       
                    print 'grabbed box, finished turning right'
                    #sense line again w/ box & sense line
                              
          elif foundline:
               if GPIO.input(12)==1 and GPIO.input(13)==1 and grabbedbox == 1:
                    a.ChangeDutyCycle(0)
                    b.ChangeDutyCycle(0)
                    p.ChangeDutyCycle(0)
                    q.ChangeDutyCycle(0)
                    print('stop')
                    openx()
                    grabbedbox = 0
                    time.sleep(.2)
                    turnsharpright()
                    time.sleep(.3)
                    while GPIO.input(12)==0 and GPIO.input(13)==0:
                      turnrightslow()
               elif GPIO.input(12)==1 and GPIO.input(13)==1:
                    a.ChangeDutyCycle(0)
                    b.ChangeDutyCycle(0)
                    p.ChangeDutyCycle(0)
                    q.ChangeDutyCycle(0)
                    print('stop')
               elif GPIO.input(12)==0 and GPIO.input(13)==0:
                    p.ChangeDutyCycle(linespeed)
                    q.ChangeDutyCycle(0)
                    a.ChangeDutyCycle(linespeed)
                    b.ChangeDutyCycle(0)
                    print('straight')
               elif GPIO.input(12)==1:
                    p.ChangeDutyCycle(0)
                    q.ChangeDutyCycle(linespeed)
                    a.ChangeDutyCycle(linespeed)
                    b.ChangeDutyCycle(0)
                    print('right')
               elif GPIO.input(13)==1:
                    p.ChangeDutyCycle(linespeed)
                    q.ChangeDutyCycle(0)
                    a.ChangeDutyCycle(0)
                    b.ChangeDutyCycle(linespeed)
                    print('left')
          else: 
               stopall()
               print 'Complete stop'
             
except KeyboardInterrupt:
       finished = True  # stop other loops
       GPIO.cleanup()
       sys.exit()
