from HIL.cost_processing.ECG.RMSSD import RMSSDFromStream
import yaml

config_file = open("../configs/RMSSD.yml", 'r')

rmssd_config = yaml.safe_load(config_file)

# cost function
rmssd = RMSSDFromStream(config=rmssd_config)

# start the cost function
rmssd.run()