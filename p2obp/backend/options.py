import logging
from pathlib import Path

OPTIONS = {}

# NOTE: General settings for the `p2obp`.
OPTIONS["logging.folder"] = "logs"
OPTIONS["logging.path"] = Path(__file__).parent.parent / OPTIONS["logging.folder"]
OPTIONS["logging.level"] = logging.DEBUG
OPTIONS["logging.format"] = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

if not OPTIONS["logging.path"].exists():
    OPTIONS["logging.path"].mkdir(parents=True, exist_ok=True)

logging.basicConfig(filename=OPTIONS["logging.path"] / "p2obp.log",
                    filemode="w", level=OPTIONS["logging.level"],
                    format=OPTIONS["logging.format"])

# NOTE: The settings for the `create_obs` and `create_ob`-scripts.
# NOTE: Sets the standard resolution.
OPTIONS["resolution"] = "low"
OPTIONS["resolution.overwrite"] = False

# NOTE: Set the photometry for standalone.
OPTIONS["photometry.matisse.ats"] = True
OPTIONS["photometry.matisse.uts"] = True

# NOTE: Set the photometry for gra4mat.
OPTIONS["photometry.gra4mat.ats"] = True
OPTIONS["photometry.gra4mat.uts"] = False

# NOTE: Set the central wavelengths for standalone.
OPTIONS["w0.matisse.ats.low"] = 4.1
OPTIONS["w0.matisse.ats.med"] = 4.1
OPTIONS["w0.matisse.ats.high"] = 4.1

OPTIONS["w0.matisse.uts.low"] = 4.1
OPTIONS["w0.matisse.uts.med"] = 4.1
OPTIONS["w0.matisse.uts.high"] = 4.1

# NOTE: Set the integration times for gra4mat.
OPTIONS["w0.gra4mat.ats.low"] = 4.1
OPTIONS["w0.gra4mat.ats.med"] = 4.1
OPTIONS["w0.gra4mat.ats.high"] = 4.1

OPTIONS["w0.gra4mat.uts.low"] = 4.1
OPTIONS["w0.gra4mat.uts.med"] = 3.52
OPTIONS["w0.gra4mat.uts.high"] = 3.52

# NOTE: Set the integration times for standalone.
OPTIONS["dit.matisse.ats.low"] = 0.111
OPTIONS["dit.matisse.ats.med"] = 0.111
OPTIONS["dit.matisse.ats.high"] = 0.111

OPTIONS["dit.matisse.uts.low"] = 0.111
OPTIONS["dit.matisse.uts.med"] = 0.111
OPTIONS["dit.matisse.uts.high"] = 0.111

# NOTE: Set the integration times for gra4mat.
OPTIONS["dit.gra4mat.ats.low"] = 0.6
OPTIONS["dit.gra4mat.ats.med"] = 1.3
OPTIONS["dit.gra4mat.ats.high"] = 3.

OPTIONS["dit.gra4mat.uts.low"] = 0.6
OPTIONS["dit.gra4mat.uts.med"] = 0.6
OPTIONS["dit.gra4mat.uts.high"] = 0.6

# NOTE: Set the weather constraints.
OPTIONS["constraints.pwv"] = 10
OPTIONS["constraints.turbulence"] = 30
OPTIONS["constraints.transparency"] = "clear"

# NOTE: The settings for the `query`-script.
OPTIONS["catalogs"] = ["gaia", "tycho", "nomad",
                       "2mass", "wise", "mdfc",
                       "simbad", "local"]

# TODO: Implement the backup target source?
# NOTE: The local catalogs/databases.
OPTIONS["catalogs.local.standard"] = "Targets"
OPTIONS["catalogs.local.ciao"] = "CIAO Offaxis Targets"
OPTIONS["catalogs.local.active"] = "standard"

# NOTE: Set the catalogs accessed.
OPTIONS["catalogs.gaia.catalog"] = "I/345/gaia2"
OPTIONS["catalogs.tycho.catalog"] = "I/350/tyc2tdsc"
OPTIONS["catalogs.nomad.catalog"] = "I/297/out"
OPTIONS["catalogs.2mass.catalog"] = "II/246/out"
OPTIONS["catalogs.wise.catalog"] = "II/311/wise"
OPTIONS["catalogs.mdfc.catalog"] = "II/361/mdfc-v10"

# NOTE: Set the fields accessed in each catalog.
OPTIONS["catalogs.gaia.fields"] = ["*"]
OPTIONS["catalogs.tycho.fields"] = ["*", "e_BTmag", "e_VTmag"]
OPTIONS["catalogs.nomad.fields"] = ["*"]
OPTIONS["catalogs.2mass.fields"] = ["*"]
OPTIONS["catalogs.wise.fields"] = ["*"]
OPTIONS["catalogs.mdfc.fields"] = ["**"]
OPTIONS["catalogs.simbad.fields"] = ["mk", "sp", "sptype", "fe_h",
                                     "pm", "plx", "rv_value",
                                     "flux(U)", "flux_error(U)",
                                     "flux(B)", "flux_error(B)",
                                     "flux(V)", "flux_error(V)",
                                     "flux(R)", "flux_error(R)",
                                     "flux(I)", "flux_error(I)",
                                     "flux(J)", "flux_error(J)",
                                     "flux(H)", "flux_error(H)",
                                     "flux(K)", "flux_error(K)"]
OPTIONS["catalogs.irsa.fields"] = ["A_over_E_B_V_SandF"]

# NOTE: The queries from each catalog.
OPTIONS["catalogs.gaia.query"] = ["Gmag", "pmRA", "pmDE"]
OPTIONS["catalogs.tycho.query"] = ["VTmag"]
OPTIONS["catalogs.2mass.query"] = ["Jmag", "Hmag", "Kmag"]
OPTIONS["catalogs.nomad.query"] = ["Vmag"]
OPTIONS["catalogs.wise.query"] = ["W1mag", "W3mag", "Hmag", "Kmag"]
OPTIONS["catalogs.mdfc.query"] = ["med-Lflux", "med-Nflux", "Hmag", "Kmag"]
OPTIONS["catalogs.simbad.query"] = ["SP_TYPE", "RA", "DEC", "PMRA", "PMDEC",
                                    "FLUX_V", "FLUX_H", "FLUX_K"]
OPTIONS["catalogs.irsa.query"] = ["UKIRT K", "2MASS J", "2MASS H"]
