import sys
import os

# Add devices module to path
sys.path.append(os.path.abspath("."))

from devices.device import Device
from devices.output import *


def main():
    device_name = "Faraday Probe"
    outputs = []

    outputs.append(eField(device_name=device_name, data_path="./example_data/C1--XX_SCOPE2--00081.csv"
        ))

    myFaradayProbe = Device(
        device_name=device_name,
        outputs=outputs
    )

    myFaradayProbe.get_outputs()
    myFaradayProbe.call_analysis()


if __name__ == "__main__":
    main()

