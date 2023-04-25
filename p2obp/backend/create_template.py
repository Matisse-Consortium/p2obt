import math
import warnings
from pathlib import Path
from typing import Optional, Dict, Tuple

import numpy as np


def format_ra_and_dec(target: Dict):
    """Correclty formats the right ascension and declination."""
    coordinates = SkyCoord(f"{target['RA']} {target['DEC']}",
                           unit=(u.hourangle, u.deg))
    declination = '%02d:%02d:%06.3f' % (c.dec.dms[0],
                                        abs(c.dec.dms[1]),
                                        abs(c.dec.dms[2]))
    right_ascencion = ...

    target['ra_deg'] = c.ra.deg
    target['dec_deg'] = c.dec.deg


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


def create_template(target_name: str, baseline_configuration: str,
                    observation_type: str, sci_name: Optional[str] = None,
                    output_dir: Path):
    ob_name = f"{observation_type}_{target_name.replace(' ', '_')}"


def mat_gen_ob(target_name, baseline_config, object_type, outdir='.',
               obs_tpls=[OBS_TPL], acq_tpl=ACQ_TPL, header_dic=HEADER_DIC,
               spectral_setups=[''], central_wls=[np.nan], DITs=[np.nan],
               ncycles=[np.nan], photo_sts=[''], user_comments='', obname='',
               obs_type='', simbad_data_dic={}, sci_name='', tag='',
               print_info=True):
    # NOTE: Update header
    if obname == '':
        if sci_name == '':
            obname = object_type + '_' + target_name.replace(' ', '_')
        else:
            obname = object_type + '_' + \
                target_name.replace(' ', '_') + '_' + \
                sci_name.replace(' ', '_')
    if tag != '':
        obname = obname + '_' + tag
    header_dic['name'] = obname
    if user_comments != '':
        header_dic['userComments'] = user_comments

    # get target information
    if simbad_data_dic:
        sdic = simbad_data_dic
    else:
        # query SIMBAD
        sdic = qc.query_CDS(target_name)

    header_dic['TARGET.NAME'] = target_name.replace(' ', '_')
    if not math.isnan(sdic['PMRA']):
        header_dic['propRA'] = sdic['PMRA']/1000.0  # arcsec/yr
    else:
        header_dic['propRA'] = 0.0
    if not math.isnan(sdic['PMDEC']):
        header_dic['propDec'] = sdic['PMDEC']/1000.0  # arcsec/yr
    else:
        header_dic['propDec'] = 0.0
    header_dic['ra'] = sdic['ra_hms']
    header_dic['dec'] = sdic['dec_dms']

    header_dic['OBSERVATION.DESCRIPTION.NAME'] = obname

    if ('UT' in baseline_config) or ('ut' in baseline_config):
        header_dic["moon_angular_distance"] = 10

    try:
        Lflux = sdic['med-Lflux']
        Nflux = sdic['med-Nflux']
    except (TypeError, IndexError, KeyError) as e:
        try:
            Lflux = 309.54 * 10.0**(-sdic['W1mag']/2.5)  # Jy
            Nflux = 31.674 * 10.0**(-sdic['W3mag']/2.5)  # Jy
        except (KeyError) as e:
            Lflux = np.nan
            Nflux = np.nan
    sdic['Lmag'] = -2.5*np.log10(Lflux/281.4)
    sdic['Nmag'] = -2.5*np.log10(Nflux/38.6)

    if math.isnan(sdic['Hmag']):
        sdic['Hmag'] = sdic['FLUX_H']
    if math.isnan(sdic['Kmag']):
        sdic['Kmag'] = sdic['FLUX_K']

    # update acquisition templatelflux
    acq_tpl['SEQ.TARG.FLUX.L'] = Lflux
    acq_tpl['SEQ.TARG.FLUX.N'] = Nflux
    if 'SEQ.TARG.MAG.H' in acq_tpl:
        acq_tpl['SEQ.TARG.MAG.H'] = sdic['Hmag']
    acq_tpl['SEQ.TARG.MAG.K'] = sdic['Kmag']

    sdic['Vmag'] = sdic['FLUX_V']
    if sdic['Vmag'] > 0.0:
        acq_tpl['COU.GS.MAG'] = sdic['Vmag']
    else:
        acq_tpl['COU.GS.MAG'] = 0.0
    acq_tpl['ISS.BASELINE'] = baseline_config
    if obs_type != '':
        acq_tpl['ISS.VLTITYPE'] = obs_type
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

    # update observation templates
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

        if object_type == 'SCI':
            obs_tpls[i]['DPR.CATG'] = "SCIENCE"
        if object_type == 'CAL':
            obs_tpls[i]['DPR.CATG'] = "CALIB"

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

    # write obx file
    outfile = outdir+'/'+obname + '.obx'
    # print(outfile)
    obfile = open(outfile, "w")
    obfile.write(add_header(header_dic))
    obfile.write(add_acq_template(acq_tpl))
    for i in range(len(obs_tpls)):
        obfile.write(add_obs_template(obs_tpls[i]))
    obfile.close()
