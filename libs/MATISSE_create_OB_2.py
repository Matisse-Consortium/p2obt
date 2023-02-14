#######################################################################
# This tool produces MATISSE OBs
# Output: ESO VLTI/MATISSE OBs in obx format
# Baseline configurations:
# AT small:  'A0-B2-C1-D0'
# AT medium: 'D0-G2-J3-K0'
# AT large:  'A0-G1-J2-J3'
# UTs:       'UT1-UT2-UT3-UT4'
# Caveats:
#   - STTimeIntervals not implemented
#   - no finding charts are produced
# Jozsef Varga, 2019-2020
# varga@strw.leidenuniv.nl

# main function to create OBs: mat_gen_ob(...)
# Parameters:
# - target_name: target name
# - baseline_config: UTs, small, large, medium 
# - object_type: 'CAL' or 'SCI'
#
# Further parameters are optional:
# - outdir: folder where the output obx file is saved
# - obs_tpls: list of observation templates (either user-specified or built-in), default: [obs_tpl]
#       Each template is a dictionary, with a set of predifined parameter values. 
#       Built in template dictionaries: 
#           obs_tpl: standard MATISSE standalone template (MATISSE_hyb_obs) - LM-LR+N_HR, DIT=0.111s, wl0=4.1um
#           obs_ft_coh_tpl: GRA4MAT corr. flux template (MATISSE_hyb_obs_ft_coh) - LM-MR+N_HR, DIT = 3s, wl0=3.95um
#           obs_ft_vis_tpl: GRA4MAT visibility template (MATISSE_hyb_obs_ft_vis) - LM-LR+N_HR, DIT=0.111s, wl0=4.1um
# - acq_tpl: acquisition template, default: [acq_tpl]
#       The template is a dictionary, with a set of predifined parameter values.
#       Built in template dictionaries: 
#           acq_tpl: acquisition template for MATISSE standalone
#           acq_ft_tpl: acquisition template for GRA4MAT
# - header_dic: dictionary for the OB header, default: [header_dic]
#
# First, the program loads the acquisition and observation templates from the template dictionaries.
# The following options can be used to modify the values in the already loaded templates.
# - spectral_setups: list of spectral setups (one for each observation template), default: ['']
#       examples: 'L-LR_N-LR','L-LR_N-HR','L-MR_N-LR','L-MR_N-HR','L-HR_N-LR','L-LR_N-LR'
#       if empty string, the spectral setup is taken from the previously loaded template
# - central_wls: list of central wavelengths  (one for each observation template), default: [np.nan]
#       if nan, the central wavelength in the previously loaded template will be used
# - DITs: list of DITs  (one for each observation template), default: [np.nan]
#       if nan, the DIT in the previously loaded template will be used
# - ncycles: list of the number of cycles (one for each observation template), default: [np.nan]
#       if nan, the ncycles in the previously loaded template will be used
# - photo_sts: list of the photometry status flags (one for each observation template), default: ['']
#       'T': true, or 'F': false
#       if empty string, the photo_sts in the previously loaded templates will be used
#       in case of GRA4MAT OBs, this will not have any effect, as these do not contain photo_st flags
# - user_comments: user comments, default: ''
#       if empty string, the user comments in the previously loaded template will be used
# - obname: OB name, default: ''
#       if empty string, the OB name will be automatically generated.
# - obs_type: observation type, default: ''
#       possible options: 'snapshot', 'imaging', 'time-series'
#       if empty string, the obs_type in the previously loaded template will be used
# - simbad_data_dic: dictionary containing information on the object (coordinates, fluxes, etc.), default: {}
#       If empty dictionary, SIMBAD and Vizier will be queried for the object coordinates and fluxes
# 
# Miscellenaous parameters:
# - sci_name: the name of the science target corresponding to the calibrator can be given. default = ''   
#       if provided, sci_name will be appended to the obname
# - tag: optional tag, could be used to indicate whether a calibrator is for L or N band. default = '' 
#       if provided, tag will be appended to the obname
# By using sci_name and tag, you can have an obname like this: CAL_HD27482_RYTau_LN (object_type,target_name,sci_name,tag)
# - print_info (True/False, default: True): whether to print target info to the terminal
#
# Example usages:
# Simplest (good for MATISSE standalone):
# import MATISSE_create_OB_2 as ob
# ob.mat_gen_ob('RY Tau','UTs','SCI')
#
# For several targets:
# import MATISSE_create_OB_2 as ob
# print('    source            coordinates                     L       N      K     V         SpT  diam')
# print('                      RA (J2000)     dec (J2000)   [Jy]     [Jy] [mag] [mag]             [mas]')
# sci_lst = ['RY Tau','AB Aur','HD 36112', 'FU Ori','IQ Tau','IP Tau','DL Tau','bet Pic']
# outdir = '/some/dir'
# for obj in sci_lst:
#     ob.mat_gen_ob(obj,'UTs','SCI',outdir)
#
# How to make a GRA4MAT OB:
# import MATISSE_create_OB_2 as ob
# outdir = '/some/dir'
# ob.mat_gen_ob('R Mon','large','SCI',outdir=outdir,
#     obs_tpls=[ob.obs_ft_coh_tpl,ob.obs_ft_vis_tpl],acq_tpl=ob.acq_ft_tpl)
#
# How to make a calibrator OB:
# import MATISSE_create_OB_2 as ob
# outdir = '/some/dir'
# ob.mat_gen_ob('HD27482','UTs','CAL',outdir=outdir,sci_name='RY Tau',tag='LN')
#
#######################################################################

import numpy as np
import math
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier
from astropy import units as u 
from astropy.coordinates import SkyCoord
import warnings
import time
warnings.filterwarnings('ignore')

# Simbad.list_votable_fields()
customSimbad = Simbad()
customSimbad.add_votable_fields('mk','fe_h','pm','plx','rv_value','fluxdata(V)','fluxdata(H)','fluxdata(K)','fluxdata(R)')

viz = Vizier(catalog="I/297/out")
viz2 = Vizier(catalog="II/311/wise")
# viz_jsdc = Vizier(catalog="II/346/jsdc_v2")
viz_mdfc = Vizier(catalog="II/361/mdfc-v10",columns=["**"])

#default template dictionaries
acq_tpl ={
    'ACQUISITION.TEMPLATE.NAME': "MATISSE_img_acq",
    'SEQ.TARG.FLUX.L': 3000.0,
    'SEQ.TARG.FLUX.N': 300.0,
    'SEQ.TARG.MAG.K': 0.0,
    'TEL.TARG.ADDVELALPHA': 0.0,
    'TEL.TARG.ADDVELDELTA': 0.0,
    'COU.AG.ALPHA': "00:00:00.000",
    'COU.AG.DELTA': "00:00:00.000",
    'COU.AG.EPOCH': 2000.0,
    'COU.AG.EQUINOX': 2000.0,
    'COU.AG.GSSOURCE': "SCIENCE",
    'COU.AG.PMA': 0.0,
    'COU.AG.PMD': 0.0,
    'COU.AG.TYPE': "ADAPT_OPT",
    'COU.GS.MAG': 30.0,
    'ISS.BASELINE': "large",
    'ISS.VLTITYPE': "snapshot"
}

acq_ft_tpl ={
    'ACQUISITION.TEMPLATE.NAME': "MATISSE_img_acq_ft",
    'SEQ.TARG.FLUX.L': 3000.0,
    'SEQ.TARG.FLUX.N': 300.0,
    'SEQ.TARG.MAG.H': 0.0,
    'SEQ.TARG.MAG.K': 0.0,
    'TEL.TARG.ADDVELALPHA': 0.0,
    'TEL.TARG.ADDVELDELTA': 0.0,
    'COU.AG.ALPHA': "00:00:00.000",
    'COU.AG.DELTA': "00:00:00.000",
    'COU.AG.EPOCH': 2000.0,
    'COU.AG.EQUINOX': 2000.0,
    'COU.AG.GSSOURCE': "SCIENCE",
    'COU.AG.PMA': 0.0,
    'COU.AG.PMD': 0.0,
    'COU.AG.TYPE': "ADAPT_OPT",
    'COU.GS.MAG': 0.0,
    'ISS.BASELINE': "large",
    'ISS.VLTITYPE': "snapshot"
}

obs_tpl = {
    "TEMPLATE.NAME": "MATISSE_hyb_obs",
    "DET1.DIT": 0.111,
    "DET1.READ.CURNAME": "SCI-SLOW-SPEED",
    "SEQ.DIL.USER.WL0": 0.0,
    "SEQ.DIL.WL0": 4.1,
    "SEQ.FRINGES.NCYCLES": 1, #set number of exposure cycles
    "SEQ.PHOTO.ST": "T",
    "SEQ.SKY.OFFS.ALPHA": 1.0,
    "SEQ.SKY.OFFS.DELTA": 15.0,
    "SEQ.TRACK.BAND": "L",
    "INS.DIL.NAME": "LOW",
    "INS.DIN.NAME": "HIGH",
    "DPR.CATG": "SCIENCE"
}

obs_ft_tpl = {
    "TEMPLATE.NAME": "MATISSE_hyb_obs_ft",
    "DET1.DIT": 1.3,
    "DET1.READ.CURNAME": "SCI-SLOW-SPEED",
    "SEQ.DIL.USER.WL0": 0.0,
    "SEQ.DIL.WL0": 4.1,
    "SEQ.FRINGES.NCYCLES": 1,
    "SEQ.OFFSET.ALPHA": 0.0,
    "SEQ.OFFSET.DELTA": 0.0,
    "SEQ.PHOTO.ST": "T",
    "SEQ.SKY.OFFS.ALPHA": 1.0,
    "SEQ.SKY.OFFS.DELTA": 15.0,
    "SEQ.TRACK.BAND": "L",
    "INS.DIL.NAME": "MED",
    "INS.DIN.NAME": "LOW",
    "DPR.CATG": "SCIENCE",
}

obs_ft_coh_tpl = {
    "TEMPLATE.NAME": "MATISSE_hyb_obs_ft_coh",
    "DET1.DIT": 3.0,
    "DET1.READ.CURNAME": "SCI-SLOW-SPEED",
    "SEQ.DIL.USER.WL0": 0.0,
    "SEQ.DIL.WL0": 3.95,
    "SEQ.FRINGES.NCYCLES": 1,
    "SEQ.SKY.OFFS.ALPHA": 1.0,
    "SEQ.SKY.OFFS.DELTA": 15.0,
    "SEQ.TRACK.BAND": "L",
    "INS.DIL.NAME": "MED",
    "INS.DIN.NAME": "HIGH",
    "DPR.CATG": "SCIENCE"    
}

obs_ft_vis_tpl = {
    "TEMPLATE.NAME": "MATISSE_hyb_obs_ft_vis",
    "DET1.DIT": 0.111,
    "DET1.READ.CURNAME": "SCI-SLOW-SPEED",
    "SEQ.DIL.USER.WL0": 0.0,
    "SEQ.DIL.WL0": 4.1,
    "SEQ.FRINGES.NCYCLES": 1,
    "SEQ.SKY.OFFS.ALPHA": 1.0,
    "SEQ.SKY.OFFS.DELTA": 15.0,
    "SEQ.TRACK.BAND": "L",
    "INS.DIL.NAME": "LOW",
    "INS.DIN.NAME": "HIGH",
    "DPR.CATG": "SCIENCE"    
}

header_dic = {
    "name":'',
    "userComments":'',
    "InstrumentComments":'',
    "userPriority":1,
    "type":"O",
    "TARGET.NAME":'',
    "propRA":0.0,
    "propDec":0.0,
    "diffRA":0.0,
    "diffDec":0.0,
    "equinox":2000,
    "epoch":2000.0,
    "ra":"00:00:00.000",
    "dec":"00:00:00.000",
    "CONSTRAINT.SET.NAME":"No Name",
    "seeing":2.0,
    "sky_transparency":"Clear",
    "air_mass":2.0,
    "fractional_lunar_illumination":1.0,
    "moon_angular_distance":20,
    "strehlratio":0.0,
    "twilight":0,
    "watervapour":30.0,
    "atm":"70%  (Seeing < 1.15 arcsec, t0 > 2.2 ms)",
    "contrast":0.0,
    "description":'',
    "OBSERVATION.DESCRIPTION.NAME":'',
    "instrument":'MATISSE'   
}

def query_SIMBAD(name):
    dic = {}
    time.sleep(0.1)
    result_simbad = customSimbad.query_object(name)
    result_nomad = viz.query_object(name,catalog=["NOMAD"],radius=5.0*u.arcsec)
    time.sleep(0.1)
    result_mdfc = viz_mdfc.query_object(name,catalog=["II/361/mdfc-v10"],radius=5.0*u.arcsec)

    try:
        dic['ra_hms' ]= result_simbad['RA'][0]
        dic['dec_dms'] = result_simbad['DEC'][0]
        dic['sptype'] = result_simbad['MK_Spectral_type'][0].decode('unicode_escape')
        # dic['Teff'] = result_table['Fe_H_Teff'][0]
        # dic['logg'] = result_table['Fe_H_log_g'][0]
        # dic['Fe_H'] = result_table['Fe_H_Fe_H'][0]
        dic['pmra'] = result_simbad['PMRA'][0]/1000.0 #arcsec/yr
        dic['pmdec'] = result_simbad['PMDEC'][0]/1000.0 #arcsec/yr
        dic['parallax'] = result_simbad['PLX_VALUE'][0] #mas
        dic['radvel'] = result_simbad['RV_VALUE'][0] #km/s
        dic['Vmag'] = result_simbad['FLUX_V'][0]      
        dic['Hmag'] = result_simbad['FLUX_H'][0]  
        dic['Kmag'] = result_simbad['FLUX_K'][0]
        # print('%16s'%name,'%24s'%sptype,'%4d'%Teff,logg,Fe_H)
        if math.isnan(dic['parallax']):
            dic['parallax'] = 0.0
        if math.isnan(dic['radvel']):
            dic['radvel'] = 0.0 
        c = SkyCoord(dic['ra_hms']+' '+dic['dec_dms'], unit=(u.hourangle, u.deg))
        dic['ra_hms'] = '%02d:%02d:%06.3f' % c.ra.hms
        dic['dec_dms'] = '%02d:%02d:%06.3f' % (c.dec.dms[0],abs(c.dec.dms[1]),abs(c.dec.dms[2]))
    except TypeError as e:
        # print('Object not found in SIMBAD: '+name)
        pass
    except IndexError as e:
        # print('Object not found in SIMBAD: '+name)
        pass

    try:
        dic['Rmag'] = result_nomad[0]['Rmag'][0]
    except TypeError as e:
        # print('Object not found in NOMAD catalog: '+name)
        dic['Rmag'] = np.nan
    except IndexError as e:
        dic['Rmag'] = np.nan
    try:
        dic['Lflux'] = result_mdfc[0]['med-Lflux'][0]
        dic['Nflux'] = result_mdfc[0]['med-Nflux'][0]
    except TypeError as e:
        result_wise = viz2.query_object(name,catalog=["II/311/wise"],radius=5.0*u.arcsec)
        dic['W1mag'] = result_wise[0]['W1mag'][0]
        dic['W3mag'] = result_wise[0]['W3mag'][0]
        dic['Lflux'] = 309.54 * 10.0**(-dic['W1mag']/2.5) #Jy
        dic['Nflux'] = 31.674 * 10.0**(-dic['W3mag']/2.5) #Jy
    except IndexError as e:
        result_wise = viz2.query_object(name,catalog=["II/311/wise"],radius=5.0*u.arcsec)
        dic['W1mag'] = result_wise[0]['W1mag'][0]
        dic['W3mag'] = result_wise[0]['W3mag'][0]
        dic['Lflux'] = 309.54 * 10.0**(-dic['W1mag']/2.5) #Jy
        dic['Nflux'] = 31.674 * 10.0**(-dic['W3mag']/2.5) #Jy

    dic['Lmag'] = -2.5*np.log10(dic['Lflux']/281.4)
    dic['Nmag'] = -2.5*np.log10(dic['Nflux']/38.6)

    try:
        dic['LDD'] = result_mdfc[0]['LDD-est'][0]
    except TypeError as e:
        # print('Object not found in JSDC: '+name)
        dic['LDD'] = np.nan
    except IndexError as e:
        # print('Object not found in JSDC: '+name)
        dic['LDD'] = np.nan

    return dic

# available acquisition templates
#       'MATISSE_acq'
#       'MATISSE_acq_ft'
def add_acq_template(tdic):
    template_str = ''
    template_str+=('%-32s\"%s\"\n'%("ACQUISITION.TEMPLATE.NAME",tdic['ACQUISITION.TEMPLATE.NAME']))
    template_str+=('%-32s\"%.2f\"\n'%("SEQ.TARG.FLUX.L",tdic['SEQ.TARG.FLUX.L']))
    template_str+=('%-32s\"%.2f\"\n'%("SEQ.TARG.FLUX.N",tdic['SEQ.TARG.FLUX.N']))
    if 'SEQ.TARG.MAG.H' in tdic:
        template_str+=('%-32s\"%.2f\"\n'%("SEQ.TARG.MAG.H",tdic['SEQ.TARG.MAG.H']))
    template_str+=('%-32s\"%.2f\"\n'%("SEQ.TARG.MAG.K",tdic['SEQ.TARG.MAG.K']))
    template_str+=('%-32s\"%.1f\"\n'%("TEL.TARG.ADDVELALPHA",tdic['TEL.TARG.ADDVELALPHA']))
    template_str+=('%-32s\"%.1f\"\n'%("TEL.TARG.ADDVELDELTA",tdic['TEL.TARG.ADDVELDELTA']))
    template_str+=('%-32s\"%s\"\n'%("COU.AG.ALPHA",tdic['COU.AG.ALPHA']))
    template_str+=('%-32s\"%s\"\n'%("COU.AG.DELTA",tdic['COU.AG.DELTA']))
    template_str+=('%-32s\"%.1f\"\n'%("COU.AG.EPOCH",tdic['COU.AG.EPOCH']))
    template_str+=('%-32s\"%.1f\"\n'%("COU.AG.EQUINOX",tdic['COU.AG.EQUINOX']))
    template_str+=('%-32s\"%s\"\n'%("COU.AG.GSSOURCE",tdic['COU.AG.GSSOURCE']))
    template_str+=('%-32s\"%f\"\n'%("COU.AG.PMA",tdic['COU.AG.PMA']))
    template_str+=('%-32s\"%f\"\n'%("COU.AG.PMD",tdic['COU.AG.PMD']))
    template_str+=('%-32s\"%s\"\n'%("COU.AG.TYPE",tdic['COU.AG.TYPE']))
    template_str+=('%-32s\"%.2f\"\n'%("COU.GS.MAG",tdic['COU.GS.MAG']))
    template_str+=('%-32s\"%s\"\n'%("ISS.BASELINE",tdic['ISS.BASELINE']))
    template_str+=('%-32s\"%s\"\n'%("ISS.VLTITYPE",tdic['ISS.VLTITYPE']))
    template_str+=('\n')
    template_str+=('\n')
    return template_str

wl0s = np.array([3.5,4.1,3.03,3.05,3.17,3.3,3.4,3.52,3.77,3.88,3.95,4.0,4.05,4.65,4.78])
wl0s_str = ['3.5','4.1','3.03','3.05','3.17','3.3','3.4','3.52','3.77','3.88','3.95','4.0','4.05','4.65','4.78']

dits = np.array([0.020,0.075,0.111,1.0,1.3,3.0,10.0])
dits_str = ['0.020','0.075','0.111','1.0','1.3','3.0','10.0']

# available observation templates
#       'MATISSE_hyb_obs': standard MATISSE standalone template
#       'MATISSE_hyb_obs_ft_coh': GRA4MAT template
#       'MATISSE_hyb_obs_ft_vis': GRA4MAT template
def add_obs_template(tdic):
    template_str = ''
    template_str+='%-32s\"%s\"\n'%("TEMPLATE.NAME",tdic['TEMPLATE.NAME'])
    idx = find_nearest_idx(dits,tdic['DET1.DIT'])
    template_str+='%-32s\"%s\"\n'%("DET1.DIT",dits_str[idx])
    template_str+='%-32s\"%s\"\n'%("DET1.READ.CURNAME",tdic['DET1.READ.CURNAME'])
    template_str+='%-32s\"%.2f\"\n'%("SEQ.DIL.USER.WL0",tdic['SEQ.DIL.USER.WL0'])
    idx = find_nearest_idx(wl0s,tdic['SEQ.DIL.WL0'])
    template_str+='%-32s\"%s\"\n'%("SEQ.DIL.WL0",wl0s_str[idx])
    template_str+='%-32s\"%d\"\n'%("SEQ.FRINGES.NCYCLES",tdic['SEQ.FRINGES.NCYCLES'])
    if 'SEQ.PHOTO.ST' in tdic:
        template_str+='%-32s\"%s\"\n'%("SEQ.PHOTO.ST",tdic['SEQ.PHOTO.ST'])
    template_str+='%-32s\"%.1f\"\n'%("SEQ.SKY.OFFS.ALPHA",tdic['SEQ.SKY.OFFS.ALPHA'])
    template_str+='%-32s\"%.1f\"\n'%("SEQ.SKY.OFFS.DELTA",tdic['SEQ.SKY.OFFS.DELTA'])
    template_str+='%-32s\"%s\"\n'%("SEQ.TRACK.BAND",tdic['SEQ.TRACK.BAND'])
    template_str+='%-32s\"%s\"\n'%("INS.DIL.NAME",tdic['INS.DIL.NAME'])
    template_str+='%-32s\"%s\"\n'%("INS.DIN.NAME",tdic['INS.DIN.NAME'])
    template_str+='%-32s\"%s\"\n'%("DPR.CATG",tdic['DPR.CATG'])
    template_str+='\n'
    template_str+='\n'
    return template_str

def add_header(tdic):
    template_str = ''
    template_str+='%-32s\"%s\"\n'%("name",tdic['name'])
    template_str+='%-32s\"%s\"\n'%("userComments",tdic['userComments'])
    template_str+='%-32s\"%s\"\n'%("InstrumentComments",tdic['InstrumentComments'])
    template_str+='%-32s\"%d\"\n'%("userPriority",tdic['userPriority'])
    template_str+='%-32s\"%s\"\n'%("type",tdic['type'])
    template_str+='\n'
    template_str+='\n'
    template_str+='%-32s\"%s\"\n'%("TARGET.NAME",tdic['TARGET.NAME'])
    template_str+='%-32s\"%f\"\n'%("propRA",tdic['propRA'])
    template_str+='%-32s\"%f\"\n'%("propDec",tdic['propDec'])
    template_str+='%-32s\"%f\"\n'%("diffRA",tdic['diffRA'])
    template_str+='%-32s\"%f\"\n'%("diffDec",tdic['diffDec'])
    template_str+='%-32s\"%d\"\n'%("equinox",tdic['equinox'])
    template_str+='%-32s\"%.1f\"\n'%("epoch",tdic['epoch'])
    template_str+='%-32s\"%s\"\n'%("ra",tdic['ra'])
    template_str+='%-32s\"%s\"\n'%("dec",tdic['dec'])
    template_str+='\n'
    template_str+='\n'
    template_str+='%-32s\"%s\"\n'%("CONSTRAINT.SET.NAME",tdic['CONSTRAINT.SET.NAME'])
    template_str+='%-32s\"%.1f\"\n'%("seeing",tdic['seeing'])
    template_str+='%-32s\"%s\"\n'%("sky_transparency",tdic['sky_transparency'])
    template_str+='%-32s\"%.1f\"\n'%("air_mass",tdic['air_mass'])
    template_str+='%-32s\"%.1f\"\n'%("fractional_lunar_illumination",tdic['fractional_lunar_illumination'])
    template_str+='%-32s\"%d\"\n'%("moon_angular_distance",tdic['moon_angular_distance'])
    template_str+='%-32s\"%.1f\"\n'%("strehlratio",tdic['strehlratio'])
    template_str+='%-32s\"%d\"\n'%("twilight",tdic['twilight'])
    template_str+='%-32s\"%.1f\"\n'%("watervapour",tdic['watervapour'])
    template_str+='%-32s\"%s\"\n'%("atm",tdic['atm'])
    template_str+='%-32s\"%.1f\"\n'%("contrast",tdic['contrast'])
    template_str+='%-32s\"%s\"\n'%("description",tdic['description'])
    template_str+='\n'
    template_str+='\n'
    template_str+='%-32s\"%s\"\n'%("OBSERVATION.DESCRIPTION.NAME",tdic['OBSERVATION.DESCRIPTION.NAME'])
    template_str+='%-32s\"%s\"\n'%("instrument",tdic['instrument'])
    template_str+='\n'
    template_str+='\n'

    # finding_chart_list = "" #"p2fc_ob2366601_1.jpg = p2fc_ob2366601_2.jpg" #<---
    # template_str+='%-32s\"%s\"\n'%("finding_chart_list",tdic['finding_chart_list'])
    # template_str+='\n'
    # template_str+='\n'

    #sidereal time intervals not implemented !!!!!!!!!!!!!!!!!!!!!!!!!!
    # STTimeIntervals = '{}'
    # if baseline_config == 'A0-B2-C1-D0':
    #     STTimeIntervals = dfs['STTimeIntervals_ATsmall'][i]
    # if baseline_config == 'D0-G2-J3-K0':
    #     STTimeIntervals = dfs['STTimeIntervals_ATmed'][i]
    # if baseline_config == 'A0-G1-J2-J3':
    #     STTimeIntervals = dfs['STTimeIntervals_ATlarge'][i]
    # if baseline_config == 'UT1-UT2-UT3-UT4':
    #     STTimeIntervals = dfs['STTimeIntervals_UT'][i]
    #template_str+='%-32s\"%s\"\n'%("STTimeIntervals",tdic['STTimeIntervals'])
    #template_str+='\n'
    #template_str+='\n')

    return template_str

def decdeg2dms(dd):
    is_positive = dd >= 0
    dd = abs(dd)
    minutes,seconds = divmod(dd*3600,60)
    degrees,minutes = divmod(minutes,60)
    degrees = degrees if is_positive else -degrees
    return [degrees,minutes,seconds]

def find_nearest_idx(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return idx

def mat_gen_ob(target_name,baseline_config,object_type,outdir='.',
    obs_tpls=[obs_tpl],acq_tpl=acq_tpl,header_dic=header_dic,spectral_setups=[''],
    central_wls=[np.nan],DITs=[np.nan],ncycles=[np.nan],photo_sts=[''],
    user_comments='',obname='',obs_type='',simbad_data_dic = {},sci_name='',tag='',
    print_info=True):

    #print(object_type+' '+target_name+' '+baseline_config+' ',end='')

    # update header
    if obname == '':
        if sci_name == '':
            obname = object_type + '_' + target_name.replace(' ', '_')
        else: 
            obname = object_type + '_' + target_name.replace(' ', '_') + '_' + sci_name.replace(' ', '_')
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
        sdic = query_SIMBAD(target_name)
    
    header_dic['TARGET.NAME'] = target_name.replace(' ','_')
    if not math.isnan(sdic['pmra']):
        header_dic['propRA'] = sdic['pmra']  #arcsec/yr
    else:
        header_dic['propRA'] = 0.0
    if not math.isnan(sdic['pmdec']):
        header_dic['propDec'] = sdic['pmdec'] #arcsec/yr
    else:
        header_dic['propDec'] = 0.0
    header_dic['ra'] = sdic['ra_hms']
    header_dic['dec'] = sdic['dec_dms']

    header_dic['OBSERVATION.DESCRIPTION.NAME'] = obname
 
    #update acquisition template
    acq_tpl['SEQ.TARG.FLUX.L'] = sdic['Lflux']
    acq_tpl['SEQ.TARG.FLUX.N'] = sdic['Nflux']
    if 'SEQ.TARG.MAG.H' in acq_tpl:
        acq_tpl['SEQ.TARG.MAG.H'] = sdic['Hmag']
    acq_tpl['SEQ.TARG.MAG.K'] = sdic['Kmag']

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

    #update observation templates
    for i in range(len(obs_tpls)):
        #update the spectral resolutions if needed
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
        print("%-3s %-17s %12s  %13s %5.1f  %7.1f  %4.1f  %4.1f "%
          (object_type,target_name,sdic['ra_hms'],sdic['dec_dms'],
           sdic['Lflux'],sdic['Nflux'],sdic['Kmag'],sdic['Vmag']),end='')
        if object_type == 'CAL':
            print('%11s '%(sdic['sptype']),end='')
        else:
            print('%11s '%(''),end='')

        if object_type == 'CAL' and not math.isnan(sdic['LDD']):
            print('%5.1f'%(sdic['LDD']))
        else:
            print('')

    #write obx file
    outfile = outdir+'/'+obname + '.obx'
    #print(outfile)
    obfile = open(outfile,"w")
    obfile.write(add_header(header_dic))
    obfile.write(add_acq_template(acq_tpl))
    for i in range(len(obs_tpls)):
        obfile.write(add_obs_template(obs_tpls[i]))
    obfile.close()

