Pimoroni Presto adding timezone to World Clock example

I am happy I received the ordered Pimoroni Presto Kit (PIM ...)

PURPOSE:
To add timezone correction to the World Clock example:

See the folder ```Examples```

File modified:  ```world_clock.py```

File added: ```secrets.py```

The current setting of  in file ```secrets.py``` is set for the time zone of Europe/Lisbon
which is GMT +1.

```
TIMEZONE_OFFSET = "1" # One hour for Europe/Lisbon
```

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
