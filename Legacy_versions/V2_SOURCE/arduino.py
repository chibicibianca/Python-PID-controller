import math
import re
import pandas as pd
import serial

coordinateColumns = ['Gx', 'Gy', 'Gz', 'Ax', 'Ay', 'Az',
                     'Mx', 'My', 'Mz', 'H', 'T', 'Bv', 'Fa', 'Fb', 'Fc', 'Fd']


def read_line(arduino):
    data = arduino.readline()

    currentData = re.split('/', str(data))
    seriesData = dict()

    for row in currentData:
        params = re.split(':', row)

        if (len(params) is not 2):
            # End of list
            continue

        # Get key value pair
        key = params[0]
        try:
            value = float(params[1])
        except ValueError:
            # Not setting invalid not-float coordinates
            continue

        if (value is "" or math.isnan(float(value))):
            # Beggining of list
            continue

        if key in ['Mx', 'My', 'Mz', 'T', 'Bv']:
            seriesData[key] = round(float(value), 1)
        else:
            seriesData[key] = round(float(value), 2)

    return seriesData



