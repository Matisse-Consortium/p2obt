"""
jsdc = Vizier(catalog="II/346/jsdc_v2")

Returned fields:
SIMBAD: "MAIN_ID", "RA", "DEC", "RA_PREC", "DEC_PREC", "COO_ERR_MAJA",
"COO_ERR_MINA", "COO_ERR_ANGLE", "COO_QUAL", "COO_WAVELENGTH", "COO_BIBCODE",
"MK_ds", "MK_mss", "MK_Spectral_type", "MK_bibcode", "SP_TYPE", "SP_TYPE_2",
"SP_QUAL", "SP_BIBCODE", "Fe_H_Teff", "Fe_H_log_g", "Fe_H_Fe_H", "Fe_H_flag",
"Fe_H_CompStar", "Fe_H_CatNo", "Fe_H_bibcode", "PMRA", "PMDEC", "PM_ERR_MAJA",
"PM_ERR_MINA", "PM_ERR_ANGLE", "PLX_VALUE", "RV_VALUE", "FLUX_U", "FLUX_ERROR_U",
"FLUX_B", "FLUX_ERROR_B", "FLUX_V", "FLUX_ERROR_V", "FLUX_R", "FLUX_ERROR_R",
"FLUX_I", "FLUX_ERROR_I", "FLUX_J", "FLUX_ERROR_J", "FLUX_H", "FLUX_ERROR_H",
"FLUX_K", "FLUX_ERROR_K"

GAIA: "RA_ICRS", "e_RA_ICRS", "DE_ICRS", "e_DE_ICRS", "Source", "Plx", "e_Plx",
  "pmRA", "e_pmRA", "pmDE", "e_pmDE", "Dup", "FG", "e_FG", "Gmag", "e_Gmag",
  "FBP", "e_FBP", "BPmag", "e_BPmag", "FRP", "e_FRP", "RPmag", "e_RPmag", "BP-RP",
   "RV", "e_RV", "Teff", "AG", "E_BP-RP_", "Rad", "Lum"

TYCHO: "e_BTmag", "e_VTmag", "IDTyc2", "RAT", "DET", "pmRA", "pmDE", "EpRA1990",
  "EpDE1990", "CCDM", "BTmag", "VTmag", "TDSC", "WDS", "PA", "Sep", "_RA.icrs", "_DE.icrs"

NOMAD: "NOMAD1", "YM", "RAJ2000", "DEJ2000", "r", "pmRA", "e_pmRA", "pmDE", "e_pmDE",
  "Bmag", "r_Bmag", "Vmag", "r_Vmag", "Rmag", "r_Rmag", "Jmag", "Hmag", "Kmag", "R"

2MASS: "RAJ2000", "DEJ2000", "_2MASS", "Jmag", "e_Jmag", "Hmag", "e_Hmag", "Kmag", "e_Kmag",
  "Qflg", "Rflg", "Bflg", "Cflg", "Xflg", "Aflg"

WISE: "RAJ2000","DEJ2000","eeMaj","eeMin","Im","W1mag","e_W1mag","W2mag","e_W2mag",
  "W3mag","e_W3mag","W4mag","e_W4mag","Jmag","Hmag","Kmag","ccf","ex","var","d2M","_2M"

MDFC: "_r", "Name", "SpType", "RAJ2000", "DEJ2000", "Dist", "Teff-MIDI", "Teff-GAIA",
  "Comp", "Mean-sep", "mag1", "mag2", "Diam-MIDI", "e_Diam-MIDI", "Diam-Cohen",
  "e_Diam-Cohen", "Diam-GAIA", "LDD-meas", "e_LDD-meas", "UDD-meas", "Band-meas",
  "LDD-est", "e_LDD-est", "UDDL-est", "UDDM-est", "UDDN-est", "Jmag", "Hmag", "Kmag",
  "W4mag", "CalFlag", "IRflag", "nb-Lflux", "med-Lflux", "disp-Lflux", "nb-Mflux",
  "med-Mflux", "disp-Mflux", "nb-Nflux", "med-Nflux", "disp-Nflux", "Lcorflux30",
  "Lcorflux100", "Lcorflux130", "Mcorflux30", "Mcorflux100", "Mcorflux130", "Ncorflux30",
  "Ncorflux100", "Ncorflux130", "Simbad"
"""
import time
from typing import Optional, List

import astropy.units as u
from astropy.table import Table
from astropy.coordinates import SkyCoord
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier


# NOTE: Simbad.list_votable_fields()
SIMBAD_FIELDS = ["mk", "sp", "sptype", "fe_h",
                 "pm", "plx", "rv_value",
                 "flux(U)", "flux_error(U)",
                 "flux(B)", "flux_error(B)",
                 "flux(V)", "flux_error(V)",
                 "flux(R)", "flux_error(R)",
                 "flux(I)", "flux_error(I)",
                 "flux(J)", "flux_error(J)",
                 "flux(H)", "flux_error(H)",
                 "flux(K)", "flux_error(K)"]

CATALOGS = {"gaia": {"catalog": "I/345/gaia2"},
            "tycho": {"catalog": "I/350/tyc2tdsc",
                      "columns": ["*", "e_BTmag", "e_VTmag"]},
            "nomad": {"catalog": "I/297/out"},
            "2mass": {"catalog": "II/246/out"},
            "wise": {"catalog": "II/311/wise"},
            "mdfc": {"catalog": "II/361/mdfc-v10", "columns": ["**"]}}

QUERIES = {"gaia": "Gmag", "tycho": "VTmag",
           "nomad": "Vmag", "2mass": "Jmag",
           "wise": "W1mag", "mdfc": "med-Lflux", "simbad": "FLUX_V"}


def get_best_match(catalog: Table,
                   dic, multi_sel_key,
                   multi_sel_sign,
                   keys=None, table=None):
    """Gets the best match from the catalog entries

    Parameters
    ----------

    Returns
    -------
    """
    return_val = 0
    if catalog:
        if table is None:
            if len(catalog[0]) == 1:
                # NOTE: Exactly one match
                bi = 0  # best index
            # NOTE: Select the brightest match
            else:
                if multi_sel_sign > 0:
                    bi = catalog[0][multi_sel_key].argmax()
                else:
                    bi = catalog[0][multi_sel_key].argmin()
                return_val = 1
            tab = catalog[0][bi]
        else:
            tab = table
        if keys is None:
            keys = catalog[0].keys()
        for i in range(len(keys)):
            dic[keys[i]] = tab[keys[i]]
    else:
        # NOTE: Empty catalog
        return_val = 2
    return return_val

def get_catalog(name: str, catalog: str,
                match_radius: u.arcsec = 5.):
    """Queries the specified catalog.

    Parameters
    ----------
    name : str
        The target's name.
    catalog : str
        The catalog's name.
    match_radius : astropy.units.arcsec
        Default is 5.

    Returns
    -------
    catalog_result :
    """
    if not isinstance(match_radius, u.Quantity):
        match_radius *= u.arcsec
    else:
        if match_radius.unit != u.arcsec:
            raise ValueError("The match radius has to be in"
                             " astropy.units.arcsecond.")

    if catalog == "simbad":
        query_site = Simbad().add_votable_fields(*SIMBAD_FIELDS)
    else:
        query_site = Vizier(**CATALOGS[catalog])
    return query_site.query_object(name, radius=match_radius)


def query(name: str,
          catalogs: Optional[List] = None,
          match_radius: Optional[float] = 5.,
          sleep_time: float = 0.1):
    """Queries an astronomical target by its name from 

    Parameters
    ----------
    name : str
        The target's name.
    catalogs : list, optional
        The catalog's name.
    match_radius : float, optional
        Default is 5.

    Returns
    -------
    """
    target = {}
    if catalogs is None:
        catalogs = [*CATALOGS.keys()]

    for catalog in catalogs:
        get_catalog(name, catalog, match_radius)
        time.sleep(sleep_time)
        

        # c = SkyCoord(target["RA"]+" "+target["DEC"], unit=(u.hourangle, u.deg))
        # target["ra_hms"] = "%02d:%02d:%06.3f" % c.ra.hms
        # target["dec_dms"] = "%02d:%02d:%06.3f" % (
        #     c.dec.dms[0], abs(c.dec.dms[1]), abs(c.dec.dms[2]))
        # target["ra_deg"] = c.ra.deg
        # target["dec_deg"] = c.dec.deg
    return target


if __name__ == "__main__":
    query("HD142666")
    # get_catalog("HD142666", "tycho")
