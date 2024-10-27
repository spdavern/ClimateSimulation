import json
import logging
import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import os
import pandas as pd
from abc import ABC
from datetime import datetime, date, time, timedelta
from glob import glob
from multiprocessing import Process
from typing import Optional

CONFIG_NAME: str = "climate_config.json"
LIVE_FOLDER_PATH: str = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "static/live"
)
DEFAULT_PROFILE: str = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "default_profiles/base.xlsx"
)

matplotlib.use("Agg")

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO").upper())
logger = logging.getLogger(__name__)


class ClimateConfig(ABC):
    """A class to contain the current configuration of the Climate Simulation.

    Attributes:
        run_continuously (bool): Is the climate controller running continously or just for 24 hrs?
        last_updated (datetime): The last date and time the instance has been updated
        rpi_time_script_finished: The date and time the profile script finished.
        _profile_filepath: The path to the running or completed profile.
        _started (datetime): The date and time the config was instantiated.

    Methods:
        profile_filename (str): Returns the filename portion of _profile_filepath.
        started (datetime): Returns _started.
        update: Saves a copy of an instances's state to {LIVE_FOLDER_PATH}/{CONFIG_NAME} (a .json)
        retrieve_config: Repopulates an instance with what's in {LIVE_FOLDER_PATH}/{CONFIG_NAME}
        __del__: Upon deletion of an instance any saved state file is deleted.
    """

    def __init__(self, profile_path: str = None, run_continuously: bool = True):
        """Initializes the ClimateConfig class."""
        self._profile_filepath: Optional[str] = None
        # If a saved config json exists recover it. (e.g. power outage may have happened)
        live_config = glob(os.path.join(LIVE_FOLDER_PATH, CONFIG_NAME))
        if live_config:
            logger.info("An existing config was found - instantiating from it!")
            self.retrieve_config()
        else:
            self._started: datetime = datetime.now()
            self.run_continuously: bool = run_continuously
            self.rpi_time_script_finished: Optional[datetime] = None

            if profile_path:
                if os.path.exists(profile_path):
                    self._profile_filepath = profile_path
                    logger.info(
                        "Config instantiated with profile: %s", self.profile_filename
                    )
                else:
                    logger.warning(
                        "The provided profile path did not exist: %s", profile_path
                    )
                    # If a profile currently exists
                    xlsx_files: list = glob(os.path.join(LIVE_FOLDER_PATH, "*.xlsx"))
                    if xlsx_files:
                        logger.info(
                            "An existing profile xlsx was found, using it: %s",
                            xlsx_files[0],
                        )
                        self._profile_filepath = xlsx_files[0]
        # Note: Due to when python garbage collection happens, if you reinstantiate a instance of this class
        # the __del__ may occur AFTER the save() that happens in the update() below leaving no .json.
        # A new json will be created the next save() but if this becomes a problem it will have to be dealt
        # with. This should normally never be a problem with one, prolonged instance of the class.

    @property
    def started(self) -> datetime:
        """Returns the date and time of when the config was [originally] instantiated."""
        return self._started

    @property
    def profile_filename(self) -> str:
        """Returns the filename of the provided profile."""
        return (
            os.path.basename(self._profile_filepath) if self._profile_filepath else ""
        )

    def update(self) -> None:
        """Updates the live plot and 'remembered' state."""
        # Should perhaps update live_plot.png here. If so, probably should be deleted in __del__.
        self.last_updated = datetime.now()
        plot_excel(self._profile_filepath, self)
        self.save()

    def save(self) -> None:
        """Saves the state of the config to live/{CONFIG_NAME}."""
        with open(
            os.path.join(LIVE_FOLDER_PATH, CONFIG_NAME), "w", encoding="utf-8"
        ) as outfile:
            json.dump(self.__dict__, outfile, indent=4, sort_keys=True, default=str)

    def retrieve_config(self) -> None:
        """Retrieves climate configuration from static/live/{CONFIG_NAME}."""
        config_path = os.path.join(LIVE_FOLDER_PATH, CONFIG_NAME)
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as infile:
                data = json.load(infile)
        else:
            logger.warning("No config file was found!")
            return
        # Repopulate the config instance from available data.
        # Note datetimes are saved as strings in jsons because they're not natively serializable.
        self._started = (
            datetime.fromisoformat(data["_started"])
            if "_started" in data
            else datetime.now()
        )
        self.last_updated = (
            datetime.fromisoformat(data["last_updated"])
            if "last_updated" in data
            else datetime.now()
        )
        self.run_continuously = (
            data["run_continuously"]
            if "run_continuously" in data and isinstance(data["run_continuously"], bool)
            else False
        )
        self.rpi_time_script_finished = (
            datetime.fromisoformat(data["rpi_time_script_finished"])
            if "rpi_time_script_finished" in data
            and isinstance(data["rpi_time_script_finished"], str)
            else None
        )
        self._profile_filepath = (
            data["_profile_filepath"]
            if "_profile_filepath" in data
            and isinstance(data["_profile_filepath"], str)
            and os.path.exists(data["_profile_filepath"])
            else None
        )
        if not self._profile_filepath:
            logger.warning(
                "No valid profile file found in config! Populated with 'None'."
            )
        if not all([key in data for key in self.__dict__.keys()]):
            missing = [key for key in self.__dict__.keys() if key not in data]
            logger.warning("Data for %s keys missing in the config found: ", missing)

    def __del__(self) -> None:
        """Function called when a ClimateConfig instance is deleted."""
        # Note: This could add the start and finish times to the name and move to a history folder.
        # Instead it now just cleans up after itself.
        if os.path.exists(os.path.join(LIVE_FOLDER_PATH, CONFIG_NAME)):
            os.remove(os.path.join(LIVE_FOLDER_PATH, CONFIG_NAME))
        if os.path.exists(self._profile_filepath):
            os.remove(self._profile_filepath)
        if os.path.exists(os.path.join(LIVE_FOLDER_PATH, "live_plot.png")):
            os.remove(os.path.join(LIVE_FOLDER_PATH, "live_plot.png"))


def expand_profile_points(df: pd.DataFrame) -> pd.DataFrame:
    """Pads a dataframe of duration, intensity values to capture step nature of profiles.

    Arguments:
        df(DataFrame): Dataframe with first column of timedeltas (time since start) and
        second column of light intensity values.

    Returns (DataFrame):
        Dataframe with extra rows facilitating the plotting of light intensity setting
        steps where the source dataframe specifies only the time and intensity values
        at the steps.
    """
    df2 = pd.DataFrame(columns=df.columns)
    idx2 = 0
    zero = pd.Timedelta(seconds=0)
    time_col = df.columns[0]
    intensity_col = df.columns[1]
    for idx, row in df.iterrows():
        duration = row[time_col]
        if idx == 0:
            # If the first row isn't duration = zero create one.
            if duration == zero:
                row.name = 0
                df2 = df2._append(row)
                last_row = row
            else:
                # Otherwise use the initial row.
                first_row = row.copy()
                first_row.name = 0
                first_row[time_col] = zero
                first_row[intensity_col] = 0
                df2 = df2._append(first_row)
                last_row = first_row
            idx2 += 1
        if duration == zero or row[intensity_col] == last_row[intensity_col]:
            # Skip any duplicate duration = zero rows or duplicate intensities in profile
            if idx < len(df) - 1:  # Keep the last row of the profile.
                continue
        # Add a row that has new timedelta and intensity from the last row.
        new_row = last_row.copy()
        new_row[time_col] = row[time_col]
        new_row.name = idx2
        df2 = df2._append(new_row)
        idx2 += 1
        # Finally append the next row
        row.name = idx2
        df2 = df2._append(row)
        last_row = row.copy()
        idx2 += 1
    return df2


def plot_excel(filepath: str = "", config: Optional[ClimateConfig] = None):
    # Read excel file and transform input data time column to timedeltas from start
    df = pd.read_excel(filepath)
    if df.dtypes[df.columns[0]] == "O" and isinstance(df.iloc[0, 0], time):
        # Pandas column datatype is 'Object', specifically a python datetime.time, in Excel it is a time
        time_deltas = [
            datetime.combine(date.min, x) - datetime.min for x in df.iloc[:, 0].tolist()
        ]
    elif df.dtypes[df.columns[0]] == "<M8[ns]":
        # Pandas column datatype is a pandas Timestamp, in Excel it is a date
        time_deltas = [(x - df.iloc[0, 0]).to_pytimedelta() for x in df.iloc[:, 0]]
    df[df.columns[0]] = time_deltas
    # Add data points that facilitate plotting step changes
    df = expand_profile_points(df)
    # Determine the profile cycle length and last cycle start time.
    cycle_dur = min(max(time_deltas), timedelta(days=1))
    now = datetime.now()
    if config:
        total_elapsed_time = now - config.started
        cycle_num = total_elapsed_time // cycle_dur
        if config.run_continuously:
            cycle_start = config.started + cycle_num * cycle_dur
        else:
            cycle_start = config.started
    else:
        # Facilitates Light Profile View
        cycle_start = datetime(
            year=now.year, month=now.month, day=now.day, hour=0, second=0
        )
        cycle_num = 0
    # Calculate plot x values for the current (or first) cycle.
    times = [cycle_start + x for x in df.iloc[:, 0]]
    values = df.iloc[:, 1]

    # Build plot
    plt.figure(figsize=(10, 6))

    # plot cols
    plt.plot(times, values, marker=".")
    plt.grid("both")
    plt.xlabel("Duration from Start of Profile")
    plt.ylabel("Light Intensity Value")
    plt.title(str(os.path.basename(filepath)))
    plt.tight_layout()

    if config:
        # For life profile label plots with start and current time/duration.
        dur = now - cycle_start
        if dur > cycle_dur and not config.run_continuously:
            now = cycle_start + cycle_dur
            dur = cycle_dur
        time_fmt = "%H:%M:%S" if cycle_dur < timedelta(minutes=10) else "%H:%M"
        dur_str = now.strftime(time_fmt)
        plt.axvline(x=now, linestyle="--", color="r")
        plt.annotate(dur_str, [now, 84], rotation=90, ha="right")
        # TODO: To plot value we need to determine what it is. This should be done by
        #       the same function that does it for control_lights.py.
        # plt.annotate(0, [now, 0], ha="left")
        plt.annotate("Last Update", [now, 80.5], rotation=90, ha="left")
        if config.run_continuously and cycle_num:
            plt.axvline(x=cycle_start, linestyle="--", color="r")
            plt.annotate(
                cycle_start.strftime("%m/%d %H:%M:%S"),
                [cycle_start, 41],
                rotation=90,
                ha="right",
            )
            plt.annotate(
                f"Cycle {cycle_num + 1:,} Start Time",
                [cycle_start, 39],
                rotation=90,
                ha="left",
            )
        plt.xlabel("Rasberry Pi Time of Day")
        plt.title(
            f"Controlling Profile: {config.profile_filename}{' (looping)' if config.run_continuously else ''}"
            f"\n Started: {config._started.strftime('%m/%d %H:%M:%S')}"
        )
        plt.tight_layout()

    plt.gcf().autofmt_xdate(rotation=90, ha="center")
    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter(time_fmt))

    # save plot to 'static' folder
    plot_path = (
        os.path.join(LIVE_FOLDER_PATH, "live_plot.png")
        if config
        else os.path.join(os.path.dirname(filepath), "plot.png")
    )
    plt.savefig(plot_path)
    plt.close()


def check_profile_validity(filepath):

    # 1. check if excel file or csv file
    if filepath.endswith(".xlsx"):
        df = pd.read_excel(filepath)

    elif filepath.endswith(".csv"):
        df = pd.read_csv(filepath)

    else:
        return False

    # 2. check if file has 2 columns
    if len(df.columns) != 2:
        return False

    # 3. check if first column is time
    try:
        # convert first col to pd time
        df.iloc[:, 0] = pd.to_datetime(df.iloc[:, 0], format="%H:%M:%S").dt.time
    except:
        return False

    # if passed all the tests, return True!
    return True
