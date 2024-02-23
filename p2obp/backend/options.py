import logging
from types import SimpleNamespace
from pathlib import Path

# NOTE: General settings for the logging
log = SimpleNamespace(
        path=Path.home() / "Documents" / "logs",
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

# NOTE: The settings for the `create_obs` and `create_ob`-scripts.
# NOTE: Sets the standard resolution.
resolution = SimpleNamespace(
        active="low",
        overwrite=False
        )

# NOTE: Set the photometry
photometry = SimpleNamespace(
        matisse=SimpleNamespace(
            ats=True, uts=True),
        gra4mat=SimpleNamespace(
            ats=True, uts=False)
        )

# NOTE: Set the central wavelengths
w0 = SimpleNamespace(
        matisse=SimpleNamespace(
            ats=SimpleNamespace(low=4.1, med=4.1, high=4.1),
            uts=SimpleNamespace(low=4.1, med=4.1, high=4.1)),
        gra4mat=SimpleNamespace(
            ats=SimpleNamespace(low=4.1, med=4.1, high=4.1),
            uts=SimpleNamespace(low=4.1, med=3.52, high=3.52))
        )

# NOTE: Set the integration times
dit = SimpleNamespace(
        matisse=SimpleNamespace(
            ats=SimpleNamespace(low=0.111, med=0.111, high=0.111),
            uts=SimpleNamespace(low=0.111, med=0.111, high=0.111)),
        gra4mat=SimpleNamespace(
            ats=SimpleNamespace(low=0.6, med=1.3, high=3.),
            uts=SimpleNamespace(low=0.6, med=0.6, high=0.6))
        )

# NOTE: Set the weather constraints.
constraints = SimpleNamespace(
        pwv=10,
        turbulence=30,
        transparency="clear"
        )

# NOTE: The settings for the `query`-script
# TODO: Implement the backup target source?
local = SimpleNamespace(
        active="standard",
        standard="Targets",
        ciao="CIAO Offaxis Targets"
        )

gaia = SimpleNamespace(
        catalog="I/345/gaia2",
        fields=["*"],
        query=["Gmag", "pmRA", "pmDE"]
        )

tycho = SimpleNamespace(
        catalog="I/350/tyc2tdsc",
        fields=["*", "e_BTmag", "e_VTmag"],
        query=["VTmag"]
        )

nomad = SimpleNamespace(
        catalog="I/297/out",
        fields=["*"],
        query=["Vmag"]
        )

two_mass = SimpleNamespace(
        catalog="II/246/out",
        fields=["*"],
        query=["Jmag", "Hmag", "Kmag"]
        )

wise = SimpleNamespace(
        catalog="II/311/wise",
        fields=["*"],
        query=["W1mag", "W3mag", "Hmag", "Kmag"]
        )

mdfc = SimpleNamespace(
        catalog="II/361/mdfc-v10",
        fields=["**"],
        query=["med-Lflux", "med-Nflux", "Hmag", "Kmag"]
        )

simbad = SimpleNamespace(
        catalog=None,
        fields=["mk", "sp", "sptype", "fe_h",
                "pm", "plx", "rv_value",
                "flux(U)", "flux_error(U)",
                "flux(B)", "flux_error(B)",
                "flux(V)", "flux_error(V)",
                "flux(R)", "flux_error(R)",
                "flux(I)", "flux_error(I)",
                "flux(J)", "flux_error(J)",
                "flux(H)", "flux_error(H)",
                "flux(K)", "flux_error(K)"],
        query=["SP_TYPE", "RA", "DEC", "PMRA",
               "PMDEC", "FLUX_V", "FLUX_H", "FLUX_K"]
        )

irsa = SimpleNamespace(
        catalog=None,
        fields=["A_over_E_B_V_SandF"],
        query=["UKIRT K", "2MASS J", "2MASS H"]
        )


catalogs = SimpleNamespace(
        available=["gaia", "tycho", "nomad", "two_mass", "wise", "mdfc", "simbad", "local"],
        local=local, gaia=gaia, tycho=tycho, nomad=nomad, two_mass=two_mass, wise=wise,
        mdfc=mdfc, simbad=simbad, irsa=irsa)


OPTIONS = SimpleNamespace(
        log=log, resolution=resolution, photometry=photometry,
        w0=w0, dit=dit, constraints=constraints, catalogs=catalogs)


OPTIONS.log.path.mkdir(parents=True, exist_ok=True)
with open(OPTIONS.log.path / "p2obp.log", "w+") as log_file:
    log_file.write("Start of log:")

logging.basicConfig(filename=OPTIONS.log.path / "p2obp.log",
                    filemode="w", level=OPTIONS.log.level,
                    format=OPTIONS.log.format)
