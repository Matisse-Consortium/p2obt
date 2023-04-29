import time
from typing import Optional, Dict, List

import astropy.units as u
from astropy.table import Table
from astroquery.simbad import Simbad
from astroquery.vizier import Vizier

from .options import options


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
