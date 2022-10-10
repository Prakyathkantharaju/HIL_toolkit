import asyncio
from bleak import BleakScanner
import yaml


async def run():
    info = {}
    devices = await BleakScanner.discover()
    for d in devices:
        if 'H10' in d.name:
            print(d)
            info['address'] = d.address
            info['name'] = d.name
            # info['metadata'] = d.metadata
            with open('configs/polar.yml', 'w') as outfile:
                yaml.dump(info, outfile)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
