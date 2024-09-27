import logging
import os
import pandas as pd
from datetime import datetime, time, timedelta
from time import sleep
from climate_web_utilities import ClimateConfig
from light_utilities import flash_lights_thrice, send_to_arduino

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger(__name__)


def time_to_time_delta(
    time_value: datetime.time = time(hour=0, minute=0, second=0, microsecond=0)
) -> timedelta:
    """Returns the amount of time, a datetime.timedelta, between datetime.time(0, 0) and the time_value."""
    return timedelta(
        hours=time_value.hour,
        minutes=time_value.minute,
        seconds=time_value.second,
        microseconds=time_value.microsecond,
    )


def find_next_row(df: pd.DataFrame, elapsed_time: timedelta) -> int:
    """Find the next row of the Dataframe that elapsed_time > elapsed_time.

    Arguments:
        df (DataFrame): A dataframe where the first column are times that light intensities are to be set.
        elapsed_time (timedelta): The amount of time since the profile was started.
    Returns (int):
        Index of the next row in the dataframe where time <= the elapsed time.
    """
    time_column_name: str = df.columns[0]
    row_idx: int = 0
    # Note: Time values in the dataframe are type datetime.time's
    next_time = time_to_time_delta(df[time_column_name][0])
    while elapsed_time > next_time and row_idx + 1 < len(df):
        next_time = time_to_time_delta(df[time_column_name][row_idx + 1])
        row_idx += 1
    return row_idx


def control_lights(profile_path: str, start_time: datetime):
    global logger
    logger.info("Light controller starting as pid=%s", os.getpid())
    flash_lights_thrice()
    df = pd.read_excel(profile_path)
    time_column_name, intensity_column_name = df.columns

    # track which row we are at in the excel file
    row_count = 0

    # calc elapsed_time
    elapsed_time = datetime.now() - start_time  # This returns a datetime.timedelta
    elapsed_time = elapsed_time - timedelta(
        days=elapsed_time.days
    )  # Ensures the timedelta days = 0

    # go thru each of the rows
    while row_count < len(df):
        if row_count == 0:
            # Find the next row in the dataframe that is at or after the current elapsed time:
            # Note, this may not be the 1st row if a profile is "restarted".
            row_count = find_next_row(df, elapsed_time)
        # Extract the "next" row's time and intensity values:
        next_time = time_to_time_delta(df[time_column_name][row_count])
        intensity = df[intensity_column_name][row_count]

        # Set light intensity
        logger.info("Updating light intensity to %s.", intensity)
        send_to_arduino(intensity)

        while elapsed_time <= next_time:
            sleep(1)
            elapsed_time = datetime.now() - start_time
            elapsed_time = elapsed_time - timedelta(days=elapsed_time.days)
        row_count += 1


if __name__ == "__main__":
    # Normally the config has already been written and contains the path to the xlsx and when it stared.
    config = ClimateConfig()
    if config.profile_filename:
        control_lights(config._profile_filepath, config.started)
