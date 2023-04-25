import math
import warnings
from pathlib import Path
from typing import Optional, Dict, Tuple

import astropy.units as u
import numpy as np
from astropy.coordinates import SkyCoord


def print_content():
    if print_info:
        print("%-3s %-17s %12s  %13s %5.1f  %7.1f  %4.1f  %4.1f " %
              (object_type, target_name, sdic['ra_hms'], sdic['dec_dms'],
               Lflux, Nflux, sdic['Kmag'], sdic['Vmag']), end='')
        if object_type == 'CAL':
            print('%11s ' % (sdic['SP_TYPE']), end='')  # .decode("utf-8"))
        else:
            print('%11s ' % (''), end='')

        try:
            sdic['LDD'] = sdic['LDD-est']
        except (TypeError, KeyError) as e:
            # print('Object not found in JSDC: '+name)
            sdic['LDD'] = np.nan
        if object_type == 'CAL' and not math.isnan(sdic['LDD']):
            print('%5.1f' % (sdic['LDD']))
        else:
            print('')


def set_resolution():
    """"""
    for i in range(len(obs_tpls)):
        # update the spectral resolutions if needed
        try:
            spectral_setup = spectral_setups[i]
        except IndexError as e:
            spectral_setup = ''
        if spectral_setup != '':
            spectral_setup_L = spectral_setup.split('_')[0]
            spectral_setup_N = spectral_setup.split('_')[1]
            if spectral_setup_L == 'L-LR':
                obs_tpls[i]['INS.DIL.NAME'] = 'LOW'
            if spectral_setup_L == 'L-MR':
                obs_tpls[i]['INS.DIL.NAME'] = 'MED'
            if spectral_setup_L == 'L-HR':
                obs_tpls[i]['INS.DIL.NAME'] = 'HIGH'
            if spectral_setup_N == 'N-LR':
                obs_tpls[i]['INS.DIN.NAME'] = 'LOW'
            if spectral_setup_N == 'N-HR':
                obs_tpls[i]['INS.DIN.NAME'] = 'HIGH'

        try:
            if not math.isnan(central_wls[i]):
                obs_tpls[i]['SEQ.DIL.WL0'] = central_wls[i]
        except IndexError as e:
            pass

        try:
            if not math.isnan(DITs[i]):
                obs_tpls[i]['DET1.DIT'] = DITs[i]
        except IndexError as e:
            pass

        try:
            if not math.isnan(ncycles[i]):
                obs_tpls[i]['SEQ.FRINGES.NCYCLES'] = ncycles[i]
        except IndexError as e:
            pass

        try:
            if photo_sts[i] != '':
                if 'SEQ.PHOTO.ST' in obs_tpls[i]:
                    obs_tpls[i]['SEQ.PHOTO.ST'] = photo_sts[i]
        except IndexError as e:
            pass



def set_ob_name(target_name: str,
                observation_type: str,
                sci_name: Optional[str] = None,
                tag: Optional[str] = None) -> str:
    """"""
    ob_name = f"{observation_type}"\
              f"_{target_name.replace(' ', '_')}"
    if sci_name is not None:
        ob_name += f"_{sci_name.replace(' ', '_')}"
    return ob_name if tag is None else f"{ob_name}_{tag}"


def format_ra_and_dec(target: Dict):
    """Correclty formats the right ascension and declination."""
    coordinates = SkyCoord(f"{target['RA']} {target['DEC']}",
                           unit=(u.hourangle, u.deg))
    declination = '%02d:%02d:%06.3f' % (coordinates.dec.dms[0],
                                        abs(coordinates.dec.dms[1]),
                                        abs(coordinates.dec.dms[2]))
    right_ascension = ...

    target['ra_deg'] = coordinates.ra.deg
    target['dec_deg'] = coordinates.dec.deg


def calculate_fluxes(target: Dict) -> Tuple[float, float]:
    """Calculates the fluxes from the queried data.

    Parameters
    ----------
    target : Dict

    Returns
    -------
    flux_lband : float
    flux_nband : float
    """
    flux_lband, flux_nband = np.nan, np.nan
    lband_keys, nband_keys = ["med-Lflux", "W1mag"], ["med-Nflux", "W3mag"]

    for lband_key, nband_key in zip(lband_keys, nband_keys):
        if lband_key in target and flux_lband == np.nan:
            flux_lband = target[lband_key]
            if "mag" in lband_key:
                flux_lband = 309.54 * 10.0**(-flux_lband/2.5) 

        if nband_key in target and flux_nband == np.nan:
            flux_nband = target[nband_key]
            if "mag" in nband_key:
                flux_nband = 31.674 * 10.0**(-flux_nband/2.5)
    return flux_lband, flux_nband


# TODO: Think of a way to efficiently create the three different types of templates
def create_template(target_name: str, baseline_configuration: str,
                    observation_type: str, sci_name: Optional[str] = None,
                    comment: Optional[str] = None,
                    output_dir: Optional[Path] = None):
    """"""
    ob_name = set_ob_name(target_name, observation_type, sci_name, tag)
    # header_dic['name'] = obname
    # NOTE: Update header
    # if user_comments != '':
        # header_dic['userComments'] = user_comments
    # header_dic['TARGET.NAME'] = target_name.replace(' ', '_')
    # if not math.isnan(sdic['PMRA']):
    #     header_dic['propRA'] = sdic['PMRA']/1000.0  # arcsec/yr
    # else:
    #     header_dic['propRA'] = 0.0
    # if not math.isnan(sdic['PMDEC']):
    #     header_dic['propDec'] = sdic['PMDEC']/1000.0  # arcsec/yr
    # else:
    #     header_dic['propDec'] = 0.0
    # header_dic['ra'] = sdic['ra_hms']
    # header_dic['dec'] = sdic['dec_dms']
    #
    # header_dic['OBSERVATION.DESCRIPTION.NAME'] = obname
    # if ('UT' in baseline_config) or ('ut' in baseline_config):
    #     header_dic["moon_angular_distance"] = 10
    #
    # sdic['Lmag'] = -2.5*np.log10(Lflux/281.4)
    # sdic['Nmag'] = -2.5*np.log10(Nflux/38.6)

    # sdic['Vmag'] = sdic['FLUX_V']
    # if sdic['Vmag'] > 0.0:
    #     acq_tpl['COU.GS.MAG'] = sdic['Vmag']
    # else:
    #     acq_tpl['COU.GS.MAG'] = 0.0
    # acq_tpl['ISS.BASELINE'] = baseline_config
    # if obs_type != '':
        # acq_tpl['ISS.VLTITYPE'] = obs_type
    # update acquisition templatelflux
    # acq_tpl['SEQ.TARG.FLUX.L'] = Lflux
    # acq_tpl['SEQ.TARG.FLUX.N'] = Nflux
    # update observation templates
        # if object_type == 'SCI':
        #     obs_tpls[i]['DPR.CATG'] = "SCIENCE"
        # if object_type == 'CAL':
        #     obs_tpls[i]['DPR.CATG'] = "CALIB"

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
def create_ob():
    # write obx file
    outfile = outdir+'/'+obname + '.obx'
    # print(outfile)
    obfile = open(outfile, "w")
    obfile.write(add_header(header_dic))
    obfile.write(add_acq_template(acq_tpl))
    for i in range(len(obs_tpls)):
        obfile.write(add_obs_template(obs_tpls[i]))
    obfile.close()
