from HIL.cost_processing.ECG.RMSSD import RMSSD
import yaml

config_file = open("../configs/RMSSD.yml", 'r')

rmssd_config = yaml.safe_load(config_file)

# cost function
rmssd = RMSSD(config=rmssd_config)

# start the cost function
rmssd.run()