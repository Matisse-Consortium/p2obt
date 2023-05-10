import logging
from pathlib import Path

options = {}

# NOTE: General settings for the `p2obp`.
options["logging.folder"] = "logs"
options["logging.path"] = Path(__file__).parent.parent / options["logging.folder"]
options["logging.level"] = logging.DEBUG
options["logging.format"] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

if not options["logging.path"].exists():
    options["logging.path"].mkdir(parents=True, exist_ok=True)

logging.basicConfig(filename=options["logging.path"] / "p2obp.log",
                    filemode="w", level=options["logging.level"],
                    format=options["logging.format"])

# NOTE: The settings for the `create_obs` and `create_ob`-scripts.
# NOTE: Sets the standard resolution.
options["resolution"] = "low"
options["resolution.overwrite"] = False

# NOTE: Set the photometry for standalone.
options["photometry.matisse.ats"] = True
options["photometry.matisse.uts"] = True

# NOTE: Set the photometry for gra4mat.
options["photometry.gra4mat.ats"] = True
options["photometry.gra4mat.uts"] = False

# NOTE: Set the central wavelengths for standalone.
options["w0.matisse.ats.low"] = 4.1
options["w0.matisse.ats.med"] = 4.1
options["w0.matisse.ats.high"] = 4.1

options["w0.matisse.uts.low"] = 4.1
options["w0.matisse.uts.med"] = 4.1
options["w0.matisse.uts.high"] = 4.1

# NOTE: Set the integration times for gra4mat.
options["w0.gra4mat.ats.low"] = 4.1
options["w0.gra4mat.ats.med"] = 4.1
options["w0.gra4mat.ats.high"] = 4.1

options["w0.gra4mat.uts.low"] = 4.1
options["w0.gra4mat.uts.med"] = 3.52
options["w0.gra4mat.uts.high"] = 3.52

# NOTE: Set the integration times for standalone.
options["dit.matisse.ats.low"] = 0.111
options["dit.matisse.ats.med"] = 0.111
options["dit.matisse.ats.high"] = 0.111

options["dit.matisse.uts.low"] = 0.111
options["dit.matisse.uts.med"] = 0.111
options["dit.matisse.uts.high"] = 0.111

# NOTE: Set the integration times for gra4mat.
options["dit.gra4mat.ats.low"] = 0.6
options["dit.gra4mat.ats.med"] = 1.3
options["dit.gra4mat.ats.high"] = 3.

options["dit.gra4mat.uts.low"] = 0.6
options["dit.gra4mat.uts.med"] = 0.6
options["dit.gra4mat.uts.high"] = 0.6

# NOTE: The settings for the `query`-script.
options["catalogs"] = ["gaia", "tycho", "nomad",
                       "2mass", "wise", "mdfc",
                       "simbad", "local"]

# TODO: Implement the backup target source?
# NOTE: The local catalogs/databases.
options["catalogs.local.standard"] = "Targets"
options["catalogs.local.ciao"] = "CIAO Offaxis Targets"
options["catalogs.local.active"] = "standard"

# NOTE: Set the catalogs accessed.
options["catalogs.gaia.catalog"] = "I/345/gaia2"
options["catalogs.tycho.catalog"] = "I/350/tyc2tdsc"
options["catalogs.nomad.catalog"] = "I/297/out"
options["catalogs.2mass.catalog"] = "II/246/out"
options["catalogs.wise.catalog"] = "II/311/wise"
options["catalogs.mdfc.catalog"] = "II/361/mdfc-v10"

# NOTE: Set the fields accessed in each catalog.
options["catalogs.gaia.fields"] = ["*"]
options["catalogs.tycho.fields"] = ["*", "e_BTmag", "e_VTmag"]
options["catalogs.nomad.fields"] = ["*"]
options["catalogs.2mass.fields"] = ["*"]
options["catalogs.wise.fields"] = ["*"]
options["catalogs.mdfc.fields"] = ["**"]
options["catalogs.simbad.fields"] = ["mk", "sp", "sptype", "fe_h",
                                     "pm", "plx", "rv_value",
                                     "flux(U)", "flux_error(U)",
                                     "flux(B)", "flux_error(B)",
                                     "flux(V)", "flux_error(V)",
                                     "flux(R)", "flux_error(R)",
                                     "flux(I)", "flux_error(I)",
                                     "flux(J)", "flux_error(J)",
                                     "flux(H)", "flux_error(H)",
                                     "flux(K)", "flux_error(K)"]

# NOTE: The queries from each catalog.
options["catalogs.gaia.query"] = ["Gmag", "pmRA", "pmDE"]
options["catalogs.tycho.query"] = ["VTmag"]
options["catalogs.2mass.query"] = ["Jmag", "Hmag", "Kmag"]
options["catalogs.nomad.query"] = ["Vmag"]
options["catalogs.wise.query"] = ["W1mag", "W3mag", "Hmag", "Kmag"]
options["catalogs.mdfc.query"] = ["med-Lflux", "med-Nflux", "Hmag", "Kmag"]
options["catalogs.simbad.query"] = ["RA", "DEC", "PMRA", "PMDEC",
                                    "FLUX_V", "FLUX_H", "FLUX_K"]
