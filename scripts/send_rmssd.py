from HIL.cost_processing.ECG.RMSSD import RMSSDFromStream
import yaml
import logging



logging.basicConfig(level=logging.DEBUG)

logger_blocklist = [
    "fiona",
    "rasterio",
    "matplotlib",
    "PIL",
]

for module in logger_blocklist:
    logging.getLogger(module).setLevel(logging.WARNING)
config_file = open("configs/RMSSD.yml", 'r')

rmssd_config = yaml.safe_load(config_file)

# cost function
rmssd = RMSSDFromStream(config=rmssd_config)

# start the cost function
rmssd.run()