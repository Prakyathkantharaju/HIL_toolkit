"""This code script is for optimization of the metabolic cost estimation and optimization using the HIL toolbox.
"""

import yaml 

# HIL toolbox import

from HIL.optimization.HIL import HIL


def run():
    
        args = yaml.safe_load(open('configs/Met_config.yml','r'))
        hil = HIL(args)
        hil.start()

run()
