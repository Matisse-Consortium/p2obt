from astroquery.simbad import Simbad
from astroquery.vizier import Vizier
from astropy import units as u
from astropy.coordinates import SkyCoord
import time
import math
import numpy as np
import re

# Simbad.list_votable_fields()
customSimbad = Simbad()
customSimbad.add_votable_fields('mk','sp','sptype','fe_h','pm','plx','rv_value',
'flux(U)','flux_error(U)',
'flux(B)','flux_error(B)',
'flux(V)','flux_error(V)',
'flux(R)','flux_error(R)',
'flux(I)','flux_error(I)',
'flux(J)','flux_error(J)',
'flux(H)','flux_error(H)',
'flux(K)','flux_error(K)')
gaia = Vizier(catalog="I/345/gaia2")
tycho = Vizier(catalog="I/350/tyc2tdsc",columns = ["*","e_BTmag","e_VTmag"])
nomad = Vizier(catalog="I/297/out")
twomass = Vizier(catalog="II/246/out")
wise = Vizier(catalog="II/311/wise")
mdfc = Vizier(catalog="II/361/mdfc-v10",columns=["**"])
# jsdc = Vizier(catalog="II/346/jsdc_v2")

# Returned fields:
# SIMBAD: 'MAIN_ID', 'RA', 'DEC', 'RA_PREC', 'DEC_PREC', 'COO_ERR_MAJA',
# 'COO_ERR_MINA', 'COO_ERR_ANGLE', 'COO_QUAL', 'COO_WAVELENGTH', 'COO_BIBCODE',
# 'MK_ds', 'MK_mss', 'MK_Spectral_type', 'MK_bibcode', 'SP_TYPE', 'SP_TYPE_2',
# 'SP_QUAL', 'SP_BIBCODE', 'Fe_H_Teff', 'Fe_H_log_g', 'Fe_H_Fe_H', 'Fe_H_flag',
# 'Fe_H_CompStar', 'Fe_H_CatNo', 'Fe_H_bibcode', 'PMRA', 'PMDEC', 'PM_ERR_MAJA',
# 'PM_ERR_MINA', 'PM_ERR_ANGLE', 'PLX_VALUE', 'RV_VALUE', 'FLUX_U', 'FLUX_ERROR_U',
# 'FLUX_B', 'FLUX_ERROR_B', 'FLUX_V', 'FLUX_ERROR_V', 'FLUX_R', 'FLUX_ERROR_R',
# 'FLUX_I', 'FLUX_ERROR_I', 'FLUX_J', 'FLUX_ERROR_J', 'FLUX_H', 'FLUX_ERROR_H',
# 'FLUX_K', 'FLUX_ERROR_K'

# Gaia: 'RA_ICRS', 'e_RA_ICRS', 'DE_ICRS', 'e_DE_ICRS', 'Source', 'Plx', 'e_Plx',
#   'pmRA', 'e_pmRA', 'pmDE', 'e_pmDE', 'Dup', 'FG', 'e_FG', 'Gmag', 'e_Gmag',
#   'FBP', 'e_FBP', 'BPmag', 'e_BPmag', 'FRP', 'e_FRP', 'RPmag', 'e_RPmag', 'BP-RP',
#    'RV', 'e_RV', 'Teff', 'AG', 'E_BP-RP_', 'Rad', 'Lum'

# Tycho: 'e_BTmag', 'e_VTmag', 'IDTyc2', 'RAT', 'DET', 'pmRA', 'pmDE', 'EpRA1990',
#   'EpDE1990', 'CCDM', 'BTmag', 'VTmag', 'TDSC', 'WDS', 'PA', 'Sep', '_RA.icrs', '_DE.icrs'

# NOMAD: 'NOMAD1', 'YM', 'RAJ2000', 'DEJ2000', 'r', 'pmRA', 'e_pmRA', 'pmDE', 'e_pmDE',
#   'Bmag', 'r_Bmag', 'Vmag', 'r_Vmag', 'Rmag', 'r_Rmag', 'Jmag', 'Hmag', 'Kmag', 'R'

# 2MASS: 'RAJ2000', 'DEJ2000', '_2MASS', 'Jmag', 'e_Jmag', 'Hmag', 'e_Hmag', 'Kmag', 'e_Kmag',
#   'Qflg', 'Rflg', 'Bflg', 'Cflg', 'Xflg', 'Aflg'

# WISE: 'RAJ2000','DEJ2000','eeMaj','eeMin','Im','W1mag','e_W1mag','W2mag','e_W2mag',
#   'W3mag','e_W3mag','W4mag','e_W4mag','Jmag','Hmag','Kmag','ccf','ex','var','d2M','_2M'

# MDFC: '_r', 'Name', 'SpType', 'RAJ2000', 'DEJ2000', 'Dist', 'Teff-MIDI', 'Teff-GAIA',
#   'Comp', 'Mean-sep', 'mag1', 'mag2', 'Diam-MIDI', 'e_Diam-MIDI', 'Diam-Cohen',
#   'e_Diam-Cohen', 'Diam-GAIA', 'LDD-meas', 'e_LDD-meas', 'UDD-meas', 'Band-meas',
#   'LDD-est', 'e_LDD-est', 'UDDL-est', 'UDDM-est', 'UDDN-est', 'Jmag', 'Hmag', 'Kmag',
#   'W4mag', 'CalFlag', 'IRflag', 'nb-Lflux', 'med-Lflux', 'disp-Lflux', 'nb-Mflux',
#   'med-Mflux', 'disp-Mflux', 'nb-Nflux', 'med-Nflux', 'disp-Nflux', 'Lcorflux30',
#   'Lcorflux100', 'Lcorflux130', 'Mcorflux30', 'Mcorflux100', 'Mcorflux130', 'Ncorflux30',
#   'Ncorflux100', 'Ncorflux130', 'Simbad'

def add_vizier_match_cat_to_dic(result_cat,dic,multi_sel_key,multi_sel_sign,keys=None,table=None):
    return_val = 0
    if result_cat:
        if table is None:
            if len(result_cat[0]) == 1:
                #exactly one match
                bi = 0 #best index
            else: #select the brightest match
                if multi_sel_sign > 0:
                    bi = result_cat[0][multi_sel_key].argmax()
                else:
                    bi = result_cat[0][multi_sel_key].argmin()
                return_val = 1
            tab = result_cat[0][bi]
        else:
            tab = table
        if keys is None:
            keys = result_cat[0].keys()
        for i in range(len(keys)):
            dic[keys[i]] = tab[keys[i]]
    else:
        #empty catalog
        return_val = 2
    return return_val

def print_msg(name,text,ret):
    if ret == 1:
        print(name+': More than 1 matching objects found in '+text)
    elif ret == 2:
        print(name+': No matching object found in '+text)

#query_CDS(name,catalogs=['simbad','gaia','tycho','2mass','wise'])

def query_CDS(name,catalogs=['simbad','nomad','wise','mdfc'],match_radius=5.0,verbose=False):
    catalogs = [i.lower() for i in catalogs]
    dic = {}

    if 'nomad' in catalogs:
        result_nomad = nomad.query_object(name,catalog=["I/297/out"],radius=match_radius*u.arcsec)
        time.sleep(0.1)
        ret = add_vizier_match_cat_to_dic(result_nomad,dic,'Vmag',-1)
        if verbose == True:
            print_msg('NOMAD',ret)


    if 'gaia' in catalogs:
        result_gaia = gaia.query_object(name,catalog=["I/345/gaia2"],radius=match_radius*u.arcsec)
        time.sleep(0.1)
        ret = add_vizier_match_cat_to_dic(result_gaia,dic,'Gmag',-1)
        if verbose == True:
            print_msg(name,'Gaia',ret)

        #     dic['teff_gaia'] = tab['Teff']
        #     #dic['diam_gaia']
        #     dic['parallax'] = tab['Plx'] #(mas)
        #     dic['parallax_error'] = tab['e_Plx']
        #     dic['pmra'] = tab['pmRA'] #(mas/yr)
        #     dic['pmdec'] = tab['pmDE'] #(mas/yr)
        #     dic['radial_velocity'] = tab['RV'] #(km/s)
        #     dic['Gmag'] = tab['Gmag']
        #     dic['e_Gmag'] = tab['e_Gmag']
        #     dic['BPmag'] = tab['BPmag']
        #     dic['e_BPmag'] = tab['e_BPmag']
        #     dic['RPmag'] = tab['RPmag']
        #     dic['e_RPmag'] = tab['e_RPmag']
        #     dic['AG'] = tab['AG']
        # else:
        #     print(name+': No matching object found in Gaia.')
        #     dic['teff_gaia'] = np.nan
        #     #dic['diam_gaia']
        #     dic['parallax'] = np.nan
        #     dic['parallax_error'] = np.nan
        #     dic['pmra'] = np.nan
        #     dic['pmdec'] = np.nan
        #     dic['radial_velocity'] = np.nan
        #     dic['Gmag'] = np.nan
        #     dic['e_Gmag'] = np.nan
        #     dic['BPmag'] = np.nan
        #     dic['e_BPmag'] = np.nan
        #     dic['RPmag'] = np.nan
        #     dic['e_RPmag'] = np.nan
        #     dic['AG'] = np.nan

    if 'tycho' in catalogs:
        result_tycho = tycho.query_object(name,catalog=["I/350/tyc2tdsc"],radius=match_radius*u.arcsec)
        time.sleep(0.1)
        ret = add_vizier_match_cat_to_dic(result_tycho,dic,'VTmag',-1)
        if verbose == True:
            print_msg(name,'Tycho',ret)

        # if result_tycho != []
        #     if len(result_tycho[0]) == 1:
        #         #exactly one match
        #         bi = 0 #best index
        #     else:
        #         print(name+': More than 1 matching objects found in TYCHO.')
        #         bi = result_tycho[0]['Jmag'].argmin() #select the brightest match
        #     tab = result_tycho[0][bi]
        #     keys = result_tycho[0].keys()
        #     for i in range(len(keys)):
        #         dic[keys[i]] = tab[keys[i]]
            # dic['BTmag'] = tab['BTmag']
            # dic['e_BTmag'] = tab['e_BTmag']
            # dic['VTmag'] = tab['VTmag']
            # dic['e_VTmag'] = tab['e_VTmag']
        # else:
        #     print(name+': No matching object found in TYCHO.')
            # dic['BTmag'] = np.nan
            # dic['e_BTmag'] = np.nan
            # dic['VTmag'] = np.nan
            # dic['e_VTmag'] = np.nan


        # if result_twomass != []
        #     if len(result_twomass[0]) == 1:
        #         #exactly one match
        #         bi = 0 #best index
        #     else:
        #         print(name+': More than 1 matching objects found in 2MASS.')
        #         bi = result_twomass[0]['Jmag'].argmin() #select the brightest match
        #     tab = result_twomass[0][bi]
        #     keys = result_twomass[0].keys()
        #     for i in range(len(keys)):
        #         dic[keys[i]] = tab[keys[i]]
            # dic['Jmag'] = tab['Jmag']
            # dic['e_Jmag'] = tab['e_Jmag']
            # dic['Hmag'] = tab['Hmag']
            # dic['e_Hmag'] = tab['e_Hmag']
            # dic['Kmag'] = tab['Kmag']
            # dic['e_Kmag'] = tab['e_Kmag']
        # else:
        #     print(name+': No matching object found in 2MASS.')
            # dic['Jmag'] = np.nan
            # dic['e_Jmag'] = np.nan
            # dic['Hmag'] = np.nan
            # dic['e_Hmag'] = np.nan
            # dic['Kmag'] = np.nan
            # dic['e_Kmag'] = np.nan

    if 'mdfc' in catalogs:
        result_mdfc = mdfc.query_object(name,catalog=["II/361/mdfc-v10"],radius=match_radius*u.arcsec)
        time.sleep(0.1)
        ret = add_vizier_match_cat_to_dic(result_mdfc,dic,'med-Lflux',+1)
        if verbose == True:
            print_msg(name,'MDFC',ret)

    if 'wise' in catalogs:
        result_wise = wise.query_object(name,catalog=["II/311/wise"],radius=match_radius*u.arcsec)
        time.sleep(0.1)
        ret = add_vizier_match_cat_to_dic(result_wise,dic,'W1mag',-1)
        if verbose == True:
            print_msg(name,'WISE',ret)

    if '2mass' in catalogs:
        result_twomass = twomass.query_object(name,catalog=["II/246/out"],radius=match_radius*u.arcsec)
        time.sleep(0.1)
        ret = add_vizier_match_cat_to_dic(result_twomass,dic,'Jmag',-1)
        if verbose == True:
            print_msg(name,'2MASS',ret)

    if 'simbad' in catalogs:
        result_simbad = customSimbad.query_object(name)
        time.sleep(0.1)
        ret = add_vizier_match_cat_to_dic(result_simbad,dic,'FLUX_V',-1,keys=result_simbad.keys(),table=result_simbad[0])
        if verbose == True:
            print_msg(name,'SIMBAD',ret)
        c = SkyCoord(dic['RA']+' '+dic['DEC'], unit=(u.hourangle, u.deg))
        dic['ra_hms'] = '%02d:%02d:%06.3f' % c.ra.hms
        dic['dec_dms'] = '%02d:%02d:%06.3f' % (c.dec.dms[0],abs(c.dec.dms[1]),abs(c.dec.dms[2]))
        dic['ra_deg'] = c.ra.deg
        dic['dec_deg'] = c.dec.deg

    # result_simbad = customSimbad.query_object(name)
    # try:
    #     dic['ra_hms' ]= result_simbad['RA'][0]
    #     dic['dec_dms'] = result_simbad['DEC'][0]
    #     dic['sptype'] = result_simbad['MK_Spectral_type'][0].decode('unicode_escape')
    #     # dic['Teff'] = result_table['Fe_H_Teff'][0]
    #     # dic['logg'] = result_table['Fe_H_log_g'][0]
    #     # dic['Fe_H'] = result_table['Fe_H_Fe_H'][0]
    #     dic['pmra'] = result_simbad['PMRA'][0]/1000.0 #arcsec/yr
    #     dic['pmdec'] = result_simbad['PMDEC'][0]/1000.0 #arcsec/yr
    #     dic['parallax'] = result_simbad['PLX_VALUE'][0] #mas
    #     dic['radvel'] = result_simbad['RV_VALUE'][0] #km/s
    #     dic['Vmag'] = result_simbad['FLUX_V'][0]
    #     dic['Hmag'] = result_simbad['FLUX_H'][0]
    #     dic['Kmag'] = result_simbad['FLUX_K'][0]
    #     # print('%16s'%name,'%24s'%sptype,'%4d'%Teff,logg,Fe_H)
    #     if math.isnan(dic['parallax']):
    #         dic['parallax'] = 0.0
    #     if math.isnan(dic['radvel']):
    #         dic['radvel'] = 0.0

    # except TypeError as e:
    #     # print('Object not found in SIMBAD: '+name)
    #     pass
    # except IndexError as e:
    #     # print('Object not found in SIMBAD: '+name)
    #     pass

    # try:
    #     dic['Rmag'] = result_nomad[0]['Rmag'][0]
    # except TypeError as e:
    #     # print('Object not found in NOMAD catalog: '+name)
    #     dic['Rmag'] = np.nan
    # except IndexError as e:
    #     dic['Rmag'] = np.nan

    return dic

def listify_dic(dic):
    newdic = {}
    keys = list(dic.keys())
    for key in keys:
        newdic[key] = []
    return newdic

def append_dic_list(dic,extra_dic):
    newdic = {}
    keys = list(dic.keys())
    for key in keys:
        if key in extra_dic:
            newdic[key] = dic[key] + [extra_dic[key]]
        else:
            newdic[key] = dic[key] + [None]
    return newdic

#l=['F0Iab' ,'K4III', 'M0', 'M2Iabep+B:', 'K5III','A1V+DA','F9VFe-1.4CH-0.7','M0',
#'~','K1II/III','hA3VakA0mA0(eb)_lB','F:I:']

sp_pattern1 = '(O0|O1|O2|O3|O4|O5|O6|O7|O8|O9|B0|B1|B2|B3|B4|B5|B6|B7|B8|B9|A0|A1|A2|A3|A4|A5|A6|A7|A8|A9|F0|F1|F2|F3|F4|F5|F6|F7|F8|F9|G0|G1|G2|G3|G4|G5|G6|G7|G8|G9|K0|K1|K2|K3|K4|K5|K6|K7|K8|K9|M0|M1|M2|M3|M4|M5|M6|M7|M8|M9)'
sp_pattern2 = '(O|B|A|F|G|K|M)'
lc_pattern1 = '(Ia|Ib)'
lc_pattern2 = '(III)'
lc_pattern3 = '(II)'
lc_pattern4 = '(VI)'
lc_pattern5 = '(IV)'
lc_pattern6 = '(V)'
lc_pattern7 = '(I)'

def parse_sptype(sptype_lst):
    spclass = []
    lumclass = []
    for sptype in sptype_lst:
        sptype = sptype.split('+')[0]
        sptype = sptype.replace('v','')
        sptype = sptype.replace('[e]','')
        sptype = sptype.replace('e','')
        sptype = sptype.replace('sh','')
        sptype = sptype.replace('p','')
        sptype = sptype.replace('s','')
        sptype = sptype.replace('nn','')
        sptype = sptype.replace('n','')
        sptype = sptype.replace('CN','')
        sptype = sptype.replace('w','')
        sptype = sptype.replace('m','')

        sptype = sptype.replace('h','')

        p = re.compile(sp_pattern1)
        m = p.search(sptype)
        if m:
            spclass.append(m.group())
        else:
            p = re.compile(sp_pattern2)
            m = p.search(sptype)
            if m:
                spclass.append(m.group())
            else:
                spclass.append('')

        p = re.compile(lc_pattern1)
        m = p.search(sptype)
        if m:
            lumclass.append('I')
        else:
            p = re.compile(lc_pattern2)
            m = p.search(sptype)
            if m:
                lumclass.append(m.group())
            else:
                p = re.compile(lc_pattern3)
                m = p.search(sptype)
                if m:
                    lumclass.append(m.group())
                else:
                    p = re.compile(lc_pattern4)
                    m = p.search(sptype)
                    if m:
                        lumclass.append(m.group())
                    else:
                        p = re.compile(lc_pattern5)
                        m = p.search(sptype)
                        if m:
                            lumclass.append(m.group())
                        else:
                            p = re.compile(lc_pattern6)
                            m = p.search(sptype)
                            if m:
                                lumclass.append(m.group())
                            else:
                                p = re.compile(lc_pattern7)
                                m = p.search(sptype)
                                if m:
                                    lumclass.append(m.group())
                                else:
                                    lumclass.append('')
    return spclass,lumclass

#print(parse_sptype(l))

def fix_list(lst,old,new):
    if old is None:
        for i in range(len(lst)):
            if lst[i] is None:
                lst[i] = new
    else:
        for i in range(len(lst)):
            if lst[i] == old:
                lst[i] = new
    #print(lst)
    return lst


if __name__ == "__main__":
    print(query_CDS("AB Aur"))

