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
print("Query with standard settings:")
print("f{'':-^50}")
pprint(target)
print("f{'':-^50}")

# NOTE: The accessed fields can be modified with the options dictionary (this
# also applies for the 'catalog' and the 'fields')
# options["catalogs.tycho.catalog"] = "..."
options["catalogs.tycho.fields"] = ["**"]
# options["catalogs.tycho.query"] = ["...", "..."]

# NOTE: Catalogs can also be excluded via (this can results in errors if all or
# too many are excluded)
target = query("HD 142666", exclude_catalogs=["tycho"])
print("Query with 'tycho' catalog excluded:")
print("f{'':-^50}")
pprint(target)
print("f{'':-^50}")

# NOTE: There are also two local catalogs present. The active one is by default
# the 'standard'-local catalog as there might be a target overlap for different
# purposes
target = query("M8E-IR")
print("Query of target present in local 'standard' catalog:")
print("f{'':-^50}")
pprint(target)
print("f{'':-^50}")


# NOTE: The local catalog for the 'ciao offaxis'-observations can be activated
# with the options
options["catalogs.local.active"] = "ciao"
target = query("YLW 16A")
print("Query of target present in local 'ciao' catalog:")
print("f{'':-^50}")
pprint(target)
print("f{'':-^50}")
