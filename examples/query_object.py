"""This script is meant to give an example on how to use the
the "query" feature of p2obp to get information on a target.
"""
from pprint import pprint

from p2obp import options, query

# NOTE: Queries the target 'HD 142666', and by default the following
# catalogs: 'simbad', 'nomad', 'mdfc', 'gaia', 'tycho', '2mass' and 'wise'.
# The catalogs can be either set manually with the 'catalogs' keyword
# or specific ones excluded with the 'exclude_catalogs' (both take
# a list as input). Further can the 'match_radius' be determined (in arcsec).
target = query("HD 142666")
pprint(target)

# NOTE: The accessed fields can be modified with the options dictionary (this
# also applies for the 'catalog' and the 'fields')
# options["catalogs.tycho.catalog"] = "..."
options["catalogs.tycho.fields"] = ["**"]
# options["catalogs.tycho.query"] = ["...", "..."]


# NOTE: Catalogs can also be excluded via (this can results in errors if all or 
# too many are excluded)
target = query("HD 142666", exclude_catalogs=["tycho"])
pprint(target)
