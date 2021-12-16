"""contains a few functions that are used across other functions"""
import json

def time_convert(hours_minutes="00:00"):
    """converts hours:minutes into seconds"""
    hours = ' '
    minutes = ' '
    seconds = 1
    if hours_minutes is not None:
        hours = int(hours_minutes.split(':')[0])
        minutes = int(hours_minutes.split(':')[1])
        minutes = minutes+(hours*60)
        seconds = minutes*60
    return seconds


def get_config_data():
    """loads and returns the users config data"""
    config = open("config.json","r")
    config_data = json.load(config)
    return config_data
