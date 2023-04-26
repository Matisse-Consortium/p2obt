"""

"""
from pathlib import Path
from typing import Optional, Dict, Tuple

import astropy.units as u
import pkg_resources
import toml
from astropy.coordinates import SkyCoord

from .query import query
from .utils import convert_proper_motions

# TODO: Include file overwrite with online files and comments for
# Calibrator stars and better values. Such as where flux is missing and such
# Make functions for that that check if that is the case -> Maybe even after query?


TEMPLATE_FILE = Path(pkg_resources.resource_filename("p2obp", "data/templates.toml"))


# def print_content():
#     if print_info:
#         print("%-3s %-17s %12s  %13s %5.1f  %7.1f  %4.1f  %4.1f " %
#               (object_type, target_name, sdic['ra_hms'], sdic['dec_dms'],
#                Lflux, Nflux, sdic['Kmag'], sdic['Vmag']), end='')
#         if object_type == 'CAL':
#             print('%11s ' % (sdic['SP_TYPE']), end='')  # .decode("utf-8"))
#         else:
#             print('%11s ' % (''), end='')
#
#         try:
#             sdic['LDD'] = sdic['LDD-est']
#         except (TypeError, KeyError) as e:
#             # print('Object not found in JSDC: '+name)
#             sdic['LDD'] = np.nan
#         if object_type == 'CAL' and not math.isnan(sdic['LDD']):
#             print('%5.1f' % (sdic['LDD']))
#         else:
#             print('')
#
#
def load_template(file: Path,
                  header: str,
                  operational_mode: Optional[str] = None) -> Dict:
    """Loads a template from a (.toml)-file.

    Parameters
    ----------
    file : path
        A (.toml)-file containing templates.
    header : str
        The name of the specific tempalte.
    operational_mode : str, optional
        The mode in which MATISSE is operated, either
        "gra4mat" or "matisse".

    Returns
    -------
    template : dict
        A dictionary that is the template.
    """
    with open(file, "r+", encoding="utf-8") as toml_file:
        if operational_mode is not None:
            return toml.load(toml_file)[operational_mode][header]
        return toml.load(toml_file)[header]


def set_ob_name(target: str,
                observation_type: str,
                sci_name: Optional[str] = None,
                tag: Optional[str] = None) -> str:
    """Sets the OB's name.

    Parameters
    ----------
    target_name : str
    observation_type : str
    sci_name : str, optional
    tag : str, Optional

    Returns
    -------
    ob_name : str

    Examples
    --------
    """
    ob_name = f"{observation_type.upper()}"\
              f"_{target['name'].replace(' ', '_').upper()}"
    if sci_name is not None:
        ob_name += f"_{sci_name.replace(' ', '_')}"
    return ob_name if tag is None else f"{ob_name}_{tag}"


def set_resolution_and_dit(resolution: str,
                           operational_mode: str,
                           array_configuration: str) -> Tuple[str, float]:
    """

    Parameters
    ----------
    resolution : str
    operational_mode : str
    array_configuration : str

    Returns
    -------
    resolution : str
    dit : float
    """
    if "ut" in array_configuration:
        if operational_mode == "matisse":
            dit = 0.111
        else:
            resolution, dit = "LOW", 0.6
    else:
        if resolution == "low":
            dit = 0.6
        elif resolution == "med":
            dit = 1.3
        else:
            dit = 3.
    return resolution.upper(), dit


def format_proper_motions(target: Dict) -> Tuple[float, float]:
    """Correctly formats the right ascension's and declination's
    proper motions."""
    # TODO: Implement check if key is missing or np.nan?
    return convert_proper_motions(target["PMRA"], target["PMDEC"])


def format_ra_and_dec(target: Dict) -> Tuple[str, str]:
    """Correclty formats the right ascension and declination."""
    coordinates = SkyCoord(f"{target['RA']} {target['DEC']}",
                           unit=(u.hourangle, u.deg))
    ra_hms = coordinates.ra.to_string(unit=u.hourangle, sep=":",
                                      pad=True, precision=3)
    dec_dms = coordinates.dec.to_string(sep=":", pad=True,
                                        precision=3)
    return ra_hms, dec_dms


# CHECK: Implement some way to show that flux has been not set?
def format_fluxes(target: Dict) -> Tuple[float, float]:
    """Correctly gets and formats the fluxes from the queried data."""
    flux_lband, flux_nband = None, None
    lband_keys, nband_keys = ["med-Lflux", "W1mag"], ["med-Nflux", "W3mag"]

    for lband_key, nband_key in zip(lband_keys, nband_keys):
        if lband_key in target and flux_lband is None:
            flux_lband = target[lband_key]
            if "mag" in lband_key:
                flux_lband = 309.54 * 10.0**(-flux_lband/2.5)

        if nband_key in target and flux_nband is None:
            flux_nband = target[nband_key]
            if "mag" in nband_key:
                flux_nband = 31.674 * 10.0**(-flux_nband/2.5)
    return round(flux_lband, 2), round(flux_nband, 2)


def fill_header(target: Dict,
                observation_type: str,
                array_configuration: str,
                sci_name: Optional[str] = None,
                tag: Optional[str] = None,
                comment: Optional[str] = None) -> Dict:
    """Fills in the header dictionary with the information from the query.

    Parameters
    ----------
    target : dict
    observation_type : str
    array_configuration : str
    sci_name : str, optional
    tag : str, optional
    comment : str, optional

    Returns
    -------
    header : dict
    """
    header = load_template(TEMPLATE_FILE, "header")
    ob_name = set_ob_name(target, observation_type, sci_name, tag)
    ra_hms, dec_dms = format_ra_and_dec(target)
    prop_ra, prop_dec = format_proper_motions(target)

    header["name"] = ob_name
    header["OBSERVATION.DESCRIPTION.NAME"] = ob_name
    header["TARGET.NAME"] = target["name"].replace(' ', '_')
    header["ra"], header["dec"] = ra_hms, dec_dms
    header["propRA"], header["propDec"] = prop_ra, prop_dec

    if comment is not None:
        header["userComments"] = comment

    if "ut" in array_configuration:
        header["moon_angular_distance"] = 10
    return header


def fill_acquisition(target: Dict,
                     operational_mode: str,
                     array_configuration: str) -> Dict:
    """Gets the for the operational mode correct acquisition template
    and then fills it in with the information from the query.

    Parameters
    ----------
    target : dict
    operational_mode : str
    array_configuration : str

    Returns
    -------
    acquisition : dict
    """
    acquisition = load_template(TEMPLATE_FILE, "acquisition", operational_mode)
    flux_lband, flux_nband = format_fluxes(target)

    if "Vmag" in target:
        acquisition["COU.GS.MAG"] = target["Vmag"]
    elif "FLUX_V" in target:
        acquisition['COU.GS.MAG'] = target["FLUX_V"]

    if "ut" in array_configuration:
        array_configuration = "UTs"

    acquisition["ISS.BASELINE"] = array_configuration
    acquisition['SEQ.TARG.FLUX.L'] = flux_lband
    acquisition['SEQ.TARG.FLUX.N'] = flux_nband
    acquisition["SEQ.TARG.MAG.K"] = round(target["Kmag"], 2)

    if operational_mode == "gra4mat":
        acquisition["SEQ.TARG.MAG.H"] = round(target["Hmag"], 2)
    return acquisition


def fill_observation(resolution: str,
                     observation_type: str,
                     operational_mode: str,
                     array_configuration: str) -> Dict:
    """Gets the for the operational mode correct acquisition template
    and then fills it in with the information from the query.

    Parameters
    ----------
    resolution : str
    observation_type : str
    operational_mode : str
    array_configuration : str

    Returns
    -------
    acquisition : dict
    """
    observation = load_template(TEMPLATE_FILE, "observation", operational_mode)
    resolution, dit = set_resolution_and_dit(resolution, operational_mode,
                                             array_configuration)
    observation_type = "SCIENCE" if observation_type == "sci" else "CALIB"
    observation["DPR.CATG"] = observation_type
    observation["INS.DIL.NAME"] = resolution
    observation["DET1.DIT"] = dit
    return observation


# TODO: Think of a way to efficiently create the three different types of templates
# TODO: Rename this
def create_ob(target_name: str,
              observation_type: str,
              array_configuration: str,
              operational_mode: Optional[str] = "st",
              sci_name: Optional[str] = None,
              comment: Optional[str] = None,
              resolution: Optional[str] = "low",
              output_dir: Optional[Path] = None):
    """

    Parameters
    ----------
    target_name : str
    array_configuration : str
        Determines the array configuration. Possible values are "UTs",
        "small", "medium", "large", "extended".
    observation_type : str
    operational_mode : str, optional
        The mode of operation for MATISSE. Can be either "st"/"standalone"
        for the MATISSE-standalone mode or "gr"/"gra4mat" for GRA4MAT.
        Default is standalone.
    sci_name : str, optional
    comment : str, optional
    resolution : str, optional
    output_dir : path, optional
    """
    array_configuration = array_configuration.lower()
    if array_configuration not in ["uts", "small", "medium", "large", "extended"]:
        raise IOError("Unknown array configuration provided!"
                      " Choose from 'UTs', 'small', 'medium',"
                      " 'large' or 'extended'.")

    observation_type = observation_type.lower()
    if observation_type not in ["sci", "cal"]:
        raise IOError("Unknown observation type provided!"
                      " Choose from 'SCI' or 'CAL', for "
                      "a science target or a calibrator.")

    operational_mode = operational_mode.lower()
    if operational_mode in ["st", "standalone"]:
        operational_mode = "matisse"
    elif operational_mode in ["gr", "gra4mat"]:
        operational_mode = "gra4mat"
    else:
        raise IOError("Unknown operational mode provided!"
                      " Choose from 'st'/'standalone' or"
                      " 'gr'/'gra4mat'.")

    resolution = resolution.lower()
    if resolution not in ["low", "med", "high"]:
        raise IOError("Unknown resolution provided!"
                      " Choose from 'low', 'med' or 'high'.")

    target = query(target_name)
    header = fill_header(target, array_configuration,
                         observation_type, sci_name, comment)
    acquisition = fill_acquisition(target,
                                   operational_mode,
                                   array_configuration)

    observation = fill_observation(resolution, observation_type,
                                   operational_mode, array_configuration)

    print(observation)

    # TODO: Implement this via the sheets written
    # Off-axis Coude guide star not implemented
    # else:
    #     COU_AG_ALPHA = dd2dms(['guide_star_RA'][i]/15.0) #<---
    #     COU_AG_DELTA = dd2dms(['guide_star_dec'][i]) #<---
    #     COU_AG_EPOCH = 2000.0
    #     COU_AG_EQUINOX = 2000.0
    #     COU_AG_GSSOURCE = "SETUPFILE"
    #     COU_AG_PMA = dfs['GS_pm_RA'][i]/1000.0 #<---
    #     COU_AG_PMD = dfs['GS_pm_dec'][i]/1000.0 #<---
    #     COU_AG_TYPE = "DEFAULT"
    #     COU_GS_MAG = dfs['GS_V_mag'][i] #V mag of guide star from input table
    # if math.isnan(sdic['Hmag']):
    #     sdic['Hmag'] = sdic['FLUX_H']
    # if math.isnan(sdic['Kmag']):
    #     sdic['Kmag'] = sdic['FLUX_K']
    #
    # if 'SEQ.TARG.MAG.H' in acq_tpl:
    #     acq_tpl['SEQ.TARG.MAG.H'] = sdic['Hmag']
    # acq_tpl['SEQ.TARG.MAG.K'] = sdic['Kmag']


# TODO: Make this properly and move to different file
# def create_ob():
#     # write obx file
#     outfile = outdir+'/'+obname + '.obx'
#     # print(outfile)
#     obfile = open(outfile, "w")
#     obfile.write(add_header(header_dic))
#     obfile.write(add_acq_template(acq_tpl))
#     for i in range(len(obs_tpls)):
#         obfile.write(add_obs_template(obs_tpls[i]))
#     obfile.close()


if __name__ == "__main__":
    create_ob("hd142666", "sci", "uts", operational_mode="st")
