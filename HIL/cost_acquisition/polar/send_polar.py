import os
import asyncio
import argparse



from HIL.cost_acquisition.polar.polar import Polar

def run():
    parser = argparse.ArgumentParser(description='Run the polar to stream the data.')
    parser.add_argument('--polar-address', type=str, help='Polar address, run python polar/utils/bleak_search.py to find the address.', default='E1:26:4D:8F:18:3B')
    args = parser.parse_args()
    start_polar(args.polar_address)



def start_polar(polar_address):
    """
    Start the Polar data collection.
    """
    # start the Polar data collection
    polar_inst = Polar(polar_address)
    os.environ["PYTHONASYNCIODEBUG"] = str(1)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(polar_inst.main())




if __name__ == "__main__":
    run()