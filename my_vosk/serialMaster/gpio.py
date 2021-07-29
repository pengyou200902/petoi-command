import RPi.GPIO as GPIO  # import RPi.GPIO module  
# from time import sleep  # lets us have a delay

GPIO.setmode(GPIO.BCM)  # choose BCM or BOARD

gpio_number = 4
GPIO.setup(gpio_number, GPIO.OUT)  # set GPIOgpio_number as an output

GPIO.output(gpio_number, 1)

# try:
#     while True:
#         GPIO.output(gpio_number, 1)  # set GPIOgpio_number to 1/GPIO.HIGH/True
#         sleep(0.5)  # wait half a second
#         GPIO.output(gpio_number, 0)  # set GPIOgpio_number to 0/GPIO.LOW/False
#         sleep(0.5)  # wait half a second