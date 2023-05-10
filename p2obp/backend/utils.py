import datetime
import re
from collections import namedtuple
from typing import Union, Optional, Tuple, List

import astropy.units as u
import ephem
import pytz
from astropy.time import Time
from astropy.coordinates import EarthLocation


def add_space(input_str: str):
    """Adds a space to the "HD xxxxxx" targets,
    between the HD and the rest. """
    if re.match(r'^HD\s*\d+', input_str, flags=re.IGNORECASE):
        return re.sub(r'^HD', 'HD ', input_str, flags=re.IGNORECASE)
    return input_str


def remove_parenthesis(input_str: str):
    """Removes parenthesis from a string.

    This if for the ob's name so it is elegible for upload
    (either manually after (.obx)-file creation or automatically.
    """
    return re.sub(r'[\[\](){}]', '', input_str)


def prompt_user(message: str, selections: List[str]) -> str:
    """Prompts the user for a numerical input and returns
    the associated value from the selection list.

    Parameters
    ----------
    message : str
    selections : list of str

    Returns
    -------
    user_input : str
    """
    print(f"Run's {message} could not be automatically detected!")
    choice = ', '.join([f'{index}: {selection}'
                        for index, selection in
                        enumerate(selections, start=1)])
    notice = f"Please input run's {message} ({choice}): "
    return selections[int(input(notice))-1]


def contains_element(list_to_search: List, element_to_search: str) -> bool:
    """Checks if an element is in the list searched and returns 'True' or 'False'

    Parameters
    ----------
    list_to_search: List
        The list to be searched in
    element_to_search: str
        The element being searched for

    Returns
    -------
    element_in_list: bool
        'True' if element is found, 'False' otherwise
    """
    return any(element_to_search in element for element in list_to_search)


def convert_proper_motions(*proper_motions: u.mas,
                           rfloat: Optional[bool] = True) -> Tuple:
    """Converts the proper motions from [mas/yr] to [arcsec/yr].

    Input is assumed to be in [mas], if given as float.
    """
    if all(not isinstance(x, u.Quantity) for x in proper_motions):
        proper_motions = map(lambda x: x*u.mas, proper_motions)
    else:
        raise IOError("Please input proper motions as float or"
                      " astropy.units.mas.")
    proper_motions = u.Quantity([x.to(u.arcsec) for x in proper_motions])
    return proper_motions.value if rfloat else proper_motions


def calculate_twilight(date: Union[str, datetime],
                       site: Optional[str] = "paranal",
                       latitude: Optional[float] = None,
                       longitude: Optional[float] = None,
                       twilight_kind: Optional[str] = "astronomical"
                       ) -> Tuple[namedtuple, namedtuple]:
    """Calculates the sunset and sunrise for the input type of twilight.

    Parameters
    ----------
    date : str or datetime.date or datetime.datetime
        Can either be a string of the form "yyyy-mm-dd" or
        a `datetime.date`/`datetime.datetime`.
    site : str, optional
        The site at which the sunset and sunrise are to be
        determined.
    latitude : float, optional
        The latitude at which the sunset and sunrise are to be
        determined [deg].
    longitude : float, optional
        The longitude at which the sunset and sunrise are to be
        determined [deg].
    twilight_kind : str, optional
        The type of twilight. Can be "civil" for -6 degrees, "nautical"
        for -12 degrees and astronomical for -18 degrees.

    Returns
    -------
    sunset : namedtuple of str
        The sunset at the twilight specified. This is a named tuple
        containing string entries for "utc", "lst" and "cet".
    sunrise : namedtuple of str
        The sunrise at the twilight specified. This is a named tuple
        containing string entries for "utc", "lst" and "cet".
    """
    TimesTuple = namedtuple("TimesTuple", ["utc", "lst", "cet"])
    if isinstance(date, (datetime.date, datetime.datetime)):
        date = date.strftime('%Y-%m-%d')

    if latitude is not None:
        location = EarthLocation(lat=latitude*u.deg, lon=longitude*u.deg)
    else:
        location = EarthLocation.of_site(site)
    observer = ephem.Observer()
    observer.date = date
    observer.lat = str(location.lat.value)
    observer.lon = str(location.lon.value)

    if twilight_kind == "civil":
        observer.horizon = "-6"
    elif twilight_kind == "nautical":
        observer.horizon = "-12"
    elif twilight_kind == "astronomical":
        observer.horizon = "-18"

    sunset = observer.next_setting(ephem.Sun(), use_center=True)
    sunrise = observer.next_rising(ephem.Sun(), use_center=True)

    sunset, sunrise = map(lambda x: Time(x.datetime()), [sunset, sunrise])
    sunset_utc, sunrise_utc = map(lambda x: x.utc, [sunset, sunrise])
    sunrise_utc += datetime.timedelta(days=1)

    utc_timezone = pytz.timezone("UTC")
    sunset_aware_utc = utc_timezone.localize(sunset_utc.to_datetime())
    sunrise_aware_utc = utc_timezone.localize(sunrise_utc.to_datetime())

    sunset_lst = sunset.sidereal_time("mean", longitude=location.lon)
    sunrise_lst = sunrise.sidereal_time("mean", longitude=location.lon)

    cet_timezone = pytz.timezone("CET")
    sunset_cet = sunset_aware_utc.astimezone(cet_timezone)
    sunrise_cet = sunrise_aware_utc.astimezone(cet_timezone)

    sunset = TimesTuple(str(sunset_utc),
                        str(sunset_lst),
                        f"{sunset_cet.date()} {sunset_cet.time()}")
    sunrise = TimesTuple(str(sunrise_utc),
                         str(sunrise_lst),
                         f"{sunrise_cet.date()} {sunrise_cet.time()}")
    return sunset, sunrise


# TODO: Reimplement this as classes to take into account all three types utc, lst and
# so at once
def calculate_night_lengths(date: Union[str, datetime],
                            observation_slot: str,
                            site: Optional[str] = "paranal",
                            latitude: Optional[float] = None,
                            longitude: Optional[float] = None,
                            twilight_kind: Optional[str] = "astronomical"
                            ) -> namedtuple:
    """Calculates the length of the total night as well as the 

    Parameters
    ----------
    date : str or datetime.date or datetime.datetime
        Can either be a string of the form "yyyy-mm-dd" or
        a `datetime.date`/`datetime.datetime`.
    observation_slot : str
        This is the time that is alloted for the observations
        on the night in question. Can be any combination of the
        following "0.6h1", "1.2h2" or "1.0n". The floats can be
        any number and the string specifies the start "h1" for
        the beginning of the night, "h2" for the second half of 
        the night and "n" for the full night.
    site : str, optional
        The site at which the sunset and sunrise are to be
        determined.
    latitude : float, optional
        The latitude at which the sunset and sunrise are to be
        determined [deg].
    longitude : float, optional
        The longitude at which the sunset and sunrise are to be
        determined [deg].
    twilight_kind : str, optional
        The type of twilight. Can be "civil" for -6 degrees, "nautical"
        for -12 degrees and astronomical for -18 degrees.

    Returns
    -------
    night_duration : namedtuple
    """
    NightDuration = namedtuple("NightDuration", ["duration", "start", "end",
                                                 "observation"])
    Observation = namedtuple("Observation", ["type", "start", "end",
                                             "duration", "minutes"])
    sunset, sunrise = calculate_twilight(date, site, latitude,
                                         longitude, twilight_kind)
    sunset_utc = datetime.datetime.strptime(sunset.utc, "%Y-%m-%d %H:%M:%S.%f")
    sunrise_utc = datetime.datetime.strptime(sunrise.utc, "%Y-%m-%d %H:%M:%S.%f")
    total_duration = sunrise_utc - sunset_utc

    pattern = r"(\d+\.\d+|\d+\.\d*|\d+)([a-z]+)(\d*)"
    match = re.match(pattern, observation_slot)
    multiplicative_factor = float(match.group(1))
    part_identifier = match.group(2)
    half_night_identifier = int(match.group(3)) if match.group(3) else None

    if part_identifier == "n":
        observation_duration = total_duration
        observation_start = sunrise
    elif part_identifier == "h":
        observation_duration = (total_duration / 2) * multiplicative_factor
        observation_minutes = observation_duration.seconds // 60
        if half_night_identifier == 1:
            observation_start = sunset
            observation_end = sunset_utc + observation_duration
        elif half_night_identifier == 2:
            observation_start = sunrise_utc - observation_duration
            observation_end = sunrise_utc
    observation = Observation(observation_slot, str(observation_start),
                              str(observation_end), str(observation_duration),
                              observation_minutes)
    return NightDuration(str(total_duration), sunset.lst, sunrise.lst, observation)


if __name__ == "__main__":
    date = datetime.date(2023, 5, 4)
    sunset, sunrise = calculate_twilight(date)
    breakpoint()
