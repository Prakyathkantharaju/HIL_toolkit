import os
import asyncio
import yaml



from HIL.cost_acquisition.polar.polar import Polar



def start_polar(address):
    """
    Start the Polar data collection.
    """
    polar_inst=Polar(address)
    # start the Polar data collection
    # polar(polar_address)
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(polar_inst.main())


if __name__ == "__main__":
    file = open('configs/polar.yml', 'r')
    polar_information = yaml.safe_load(file)
    address = polar_information['address']
    print(address)
    start_polar(address)