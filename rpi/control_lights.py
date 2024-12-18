import json
import logging
import os
import pandas as pd
from datetime import datetime, date, time, timedelta
from time import sleep
from typing import Optional
from climate_web_utilities import (
    CONFIG_NAME,
    LIVE_FOLDER_PATH,
    RETRIEVE_CONFIG,
    times_to_timedeltas,
)
from light_utilities import flash_lights_thrice, send_to_arduino

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger(__name__)
CONFIG_PATH = os.path.join(LIVE_FOLDER_PATH, CONFIG_NAME)


def find_next_row(df: pd.DataFrame, elapsed_time: timedelta) -> int:
    """Find the next row of the Dataframe that elapsed_time > elapsed_time.

    Arguments:
        df (DataFrame): A dataframe where the first column are timedeltas that light intensities are to be set.
        elapsed_time (timedelta): The amount of time since the profile was started.
    Returns (int):
        Index of the next row in the dataframe where time <= the elapsed time.
    """
    time_column_name: str = df.columns[0]
    row_idx: int = 0
    # Note: Time values in the dataframe are type datetime.timedelta's
    next_time = df[time_column_name][row_idx]
    while elapsed_time > next_time and row_idx + 1 < len(df):
        next_time = df[time_column_name][row_idx + 1]
        row_idx += 1
    return row_idx


def save_config(config: dict) -> None:
    """Save climate_config.json."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as outfile:
        json.dump(config, outfile, indent=4, sort_keys=True, default=str)
    return


def control_lights():
    """Controls light intensity and updates climate_config.json."""
    # Get and save pid immediately before taking the time to flash the lights.
    pid = os.getpid()
    logger.info("Light controller starting as pid=%s", pid)
    config = RETRIEVE_CONFIG()
    config["pid"] = pid
    start_time = config["_started"]
    save_config(config)
    # Confirm new light controller by flashing lights:
    flash_lights_thrice()
    # Read profile excel file
    df = pd.read_excel(config["_profile_filepath"])
    time_column_name, intensity_column_name = df.columns[:2]
    # Transform input data time column to timedeltas
    df = times_to_timedeltas(df)

    def update_and_report(time_point: datetime, update_intensity: float):
        send_to_arduino(update_intensity)
        config["last_updated"] = time_point
        config["last_intensity"] = update_intensity
        save_config(config)

    # Determine the profile cycle length and where the current time is relative to when it was started.
    cycle_dur = max(df[time_column_name])
    now = datetime.now()
    now = now - timedelta(microseconds=now.microsecond)
    total_elapsed_time = now - start_time
    cycle_num = total_elapsed_time // cycle_dur
    cycle_start = start_time + cycle_num * cycle_dur
    dur_into_cycle = now - cycle_start
    if dur_into_cycle > cycle_dur and not config["run_continuously"]:
        logger.info(
            "Duration since start already > profile cycle length. Light controller done."
        )
        controlling = False
        row_count = len(df) - 1
    else:
        # Find the next row in the dataframe that is at or after the current elapsed time:
        # Note, this may not be the 1st row if a profile is "restarted".
        row_count = max(0, find_next_row(df, dur_into_cycle) - 1)
    next_time = df[time_column_name][row_count + 1]
    intensity = df[intensity_column_name][row_count]
    logger.info(
        "%s: Initializing light intensity to %s by pid %s."
        % (now.strftime("%m/%d %H:%M:%S"), intensity, config['pid'])
    )
    update_and_report(now, intensity)
    last_intensity = intensity

    controlling = True
    while controlling:
        # go thru each of the rows
        while row_count < len(df)-1:
            if intensity != last_intensity:
                # Set light intensity
                logger.info(
                    "%s: Updating light intensity to %s by pid %s."
                    % (now.strftime("%m/%d %H:%M:%S"), intensity, config['pid'])
                )
                update_and_report(now, intensity)
                last_intensity = intensity

            while dur_into_cycle <= next_time:
                sleep(0.5)
                now = datetime.now()
                now = now - timedelta(microseconds=now.microsecond)
                dur_into_cycle = now - cycle_start
            row_count += 1
            # Extract the "next" row's time and the new intensity:
            next_time = df[time_column_name][row_count + 1] if row_count < len(df)-1 else df[time_column_name][1]
            intensity = df[intensity_column_name][row_count]
        row_count = 0
        cycle_num += 1
        now = datetime.now()
        now = now - timedelta(microseconds=now.microsecond)
        cycle_start = start_time + cycle_num * cycle_dur
        dur_into_cycle = now - cycle_start
        controlling = config["run_continuously"]
        intensity = df[intensity_column_name].iloc[0] if config["run_continuously"] else df[intensity_column_name].iloc[-1]
    if intensity != last_intensity:
        logger.info(
            "%s, Final light intensity to %s by pid %s."
            % (now.strftime("%m/%d %H:%M:%S"), intensity, config['pid'])
        )
        update_and_report(now, intensity)
    config["rpi_time_script_finished"] = datetime.now()
    config["pid"] = None
    save_config(config)
