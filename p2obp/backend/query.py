from typing import Optional, Dict, List
from pathlib import Path

import astropy.units as u
import pkg_resources
from astropy.table import Table
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier

from .options import options

TARGET_INFO_FILE = Path(pkg_resources.resource_filename("p2obp", "data/target_information.csv"))


# TODO: Add all these fields to the query as a standard (not all but some) xD
# TODO: Make option called resolution dict, that takes the resolution into account
# for all targets where it is known.
TARGET_INFO_MAPPING = {"name": "Target Name",
                       "RA": "RA [hms]",
                       "DEC": "DEC [dms]",
                       "propRA": "PMA [arcsec/yr]",
                       "propDEC": "PMD [arcsec/yr]",
                       "Lflux": "Flux L-band [Jy]",
                       "Nflux": "Flux N-band [Jy]",
                       "Hmag": "H mag",
                       "Kmag": "K mag",
                       "GSname": "GS Name",
                       "GSRA": "GS RA [hms]",
                       "GSDEC": "GS DEC [hms]",
                       "GSpropRA": "GS Off-axis Coude PMA [arcsec/yr]",
                       "GSpropDEC": "GS Off-axis Coude PMD [arcsec/yr]",
                       "GSmag": "GS mag",
                       "LResAT": "L-Resolution (AT)",
                       "LResUT": "L-Resolution (UT)"}

# TODO: Include file overwrite with online files and comments for
# Calibrator stars and better values. Such as where flux is missing and such
# Make functions for that that check if that is the case -> Maybe even after query?

# GSmag is key for guiding star magnitude

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



def name_yet_to_find():
    import pandas as pd
    print(pd.read_csv(GS_FILE).columns)


def get_best_match(target: Dict, catalog: str,
                   catalog_table: Table) -> Table:
    """Gets the best match from the catalog entries

    Parameters
    ----------
    target : dict
        The target's queried information.
    catalog : str
        The catalog's name.
    catalog_table : Table
        The table containing the queried catalog's results.

    Returns
    -------
    best_match : Table
        The best match from the queried catalog's table.
    """
    best_matches = {}
    if not catalog_table:
        return best_matches

    for query_key in options[f"catalogs.{catalog}.query"]:
        if query_key in catalog_table.columns:
            if len(catalog_table) == 1:
                value = catalog_table[query_key][0]
            else:
                # NOTE: Get lowest element in case magnitude is queried
                if "mag" in query_key:
                    value = catalog_table[query_key].min()
                else:
                    value = catalog_table[query_key].max()

            if query_key in target:
                if "mag" in query_key:
                    if target[query_key] > value:
                        best_matches[query_key] = value
                else:
                    if target[query_key] < value:
                        best_matches[query_key] = value
            else:
                best_matches[query_key] = value
    return best_matches


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
        The radius in which is queried.
        Default is 5.

    Returns
    -------
    catalog_table : Table
        The table containing the queried catalog's results.
    """
    if not isinstance(match_radius, u.Quantity):
        match_radius *= u.arcsec
    else:
        if match_radius.unit != u.arcsec:
            raise ValueError("The match radius has to be in"
                             " astropy.units.arcsecond.")

    if catalog == "simbad":
        query_site = Simbad()
        simbad_fields = options["catalogs.simbad.fields"]
        query_site.add_votable_fields(*simbad_fields)
        catalog_table = query_site.query_object(name)
    else:
        query_site = Vizier(catalog=options[f"catalogs.{catalog}.catalog"],
                            columns=options[f"catalogs.{catalog}.fields"])
        catalog_table = query_site.query_object(name, radius=match_radius)

        # NOTE: Only get table from TableList if not empty
        if catalog_table:
            catalog_table = catalog_table[0]
    return catalog_table


# TODO: Make a pretty print built in functionality for the dictionary.
def query(name: str,
          catalogs: Optional[List] = None,
          exclude_catalogs: Optional[List] = None,
          match_radius: Optional[float] = 5.) -> Dict:
    """Queries information for an astronomical target by its name from
    various catalogs.

    Parameters
    ----------
    name : str
        The target's name.
    catalogs : list of str, optional
        The catalogs to query. By default the catalogs "gaia",
        "tycho", "nomad", "2mass", "wise", "mdfc" and "simbad"
        are included.
    exclude_catalogs : list of str
        A list of catalog to be excluded.
    match_radius : float, optional
        The radius in which is queried.
        Default is 5.

    Returns
    -------
    target : dict
        The target's queried information.
    """
    target = {"name": name}
    if catalogs is None:
        catalogs = options["catalogs"]

    if exclude_catalogs is not None:
        catalogs = [catalog for catalog in catalogs
                    if catalog not in exclude_catalogs]

    for catalog in catalogs:
        catalog_table = get_catalog(name, catalog, match_radius)
        best_matches = get_best_match(target, catalog, catalog_table)
        target = {**target, **best_matches}
    return target


if __name__ == "__main__":
    from pprint import pprint
    q = query("HD169022")
    from .compose import format_fluxes
    pprint(q)
    print(format_fluxes(q))
