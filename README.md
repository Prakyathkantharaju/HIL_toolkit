# HIL_toolkit_temp
Temporary toolkit for human in the loop optimization

## Requirements for the toolkit

### General requirements
- Python 3.10 or higher.
- Labstreaminglayer - install here. 

### Metabolic cost.
- Cosmed or other metabolic cart device.
- Setup metabolic cost acquisition code.

### ECG
- Polar H10
- Bluetooth capible laptop for ECG.

### Foot pressure.
- Pressure SDK.


## Installation
Complete python HIL toolkit install
```bash
pip install -e .
```

## Testing the installtion.
This will test the all the files are setup for simple installtion. **Does not test the ECG, or metabolic cost acquisition**
```bash
pytest .
```

## Device setups
### ECG device setup
For setting up the new polar H10 ( ECG sensor )
- Please turn on the computer bluetooth connection.
- Run the following script to find all the available POLAR sensor scripts `python scripts/search_polar.py`. This script will search for polar sensors in the bluetooth range and save the BLE information in the `config/polar.yml` file. And return success or failure.
- Run the script to collect data from the polar and send it. `python scripts/collect_polar.py`

