# CHANGED EXAMPLES FOR THE PIMORONI PRESTO:

I am happy I received the ordered Pimoroni Presto Kit (PIM765)

PURPOSE OF THE CHANGED EXAMPLES IN THIS REPO:
1) adding timezone to "Word Clock" example;
2) adding timezone and other changes to the "Analog Clock".


See the folder ```Examples```

Files modified:  ```word_clock_w_tz.py``` and ```vector_clock_full_v2.py```

File added: ```secrets.py```

The current setting of  in file ```secrets.py``` is set for the time zone of Europe/Lisbon
which is GMT +1.

```
TIMEZONE_OFFSET = "1" # One hour for Europe/Lisbon
```

Images. See the folder ```images```.

Shell (serial) output text files: seel folder ```docs```.

# EXAMPLE WORD CLOCK

In any micropython script, in the global variables section, one can add:
```
from secrets import TIMEZONE_OFFSET # get the timezone offset (a string type)

tz_offset = int(TIMEZONE_OFFSET)  # convert string to an integer value

time_string = None  # used in function update()

```

then in a function like: update() the following code:

```
# A function to update the RTC with a datetime from an NTP server
# with taking into account a possible timezone difference from GMT
# Assuming a WiFi connection is established.
def update():
    global time_string
    # grab the current time from the ntp server and update the Pico RTC
    try:
        sec = ntptime.time()
        timezone_sec = tz_offset * 3600
        sec = int(sec + timezone_sec)
        (year, month, day, hours, minutes, seconds, weekday, yearday) = time.localtime(sec)
        rtc.datetime((year, month, day, 0, hours, minutes, seconds, 0))

        # The code lines above instead of the following line of code:
        # ntptime.settime()  # original code by Pimoroni
    except OSError:
        print("Unable to contact NTP server")

    current_t = rtc.datetime()
    time_string = approx_time(current_t[4] - 12 if current_t[4] > 12 else current_t[4], current_t[5])

    # Splits the string into an array of words for displaying later
    time_string = time_string.split()

    print(time_string)

    # more code here...

```

# EXAMPLE ANALOG CLOCK PAULSKPT

In this example the following changes have been made:

1) to get ntp datetimestamp at start and next at set interval. See NTP_UPDATE_INTERVAL at line 19.
3) in the main loop added time calculations to control the ntp refresh interval;
2) circular change of the clock face aspect colours. At hours between 22pm and 7am the brightest clock face will not be shown.
   During these night hours also reversed colours will be used;
3) optional wait for 0 seconds at startup (boolean flag "do_startwait" at line 59);
4) wdDict (weekday dictionary). Print day of the week (serial output only);
5) print day of the year (serial output only);
5) print timezone. See function pr_dt() (serial output only).

# UPDATES

2025-05-01: 
Added font file "Roboto-Medium.af"
Added touch functionality to the 2nd example. 
For the touch functionality I devided the screen into 4 quadrants: 
```
        |
   NW   |   NE       Touching the NW quadrant changes the index for the clock aspect. 
--------+--------    Touching the NE quadrant toggles the show_date flag. Default this flag is set to True.
   SW   |   SE       Touching the SW quadrant switches on the ambient LEDs and changes the colour index.
        |            Touching the SE quadrant switches off the ambient LEDs. Default the LEDs are off.


```

# FINAL NOTES
I received a suggestion to create a PR for (at least the first example) however I am not that good in creating PR's. It takes also quite some time before a PR is handled.
For these reasons I prefer to create my own repo's and announce their existance in the various forums.
