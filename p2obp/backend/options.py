options = {}

# TODO: Think of implementation of uploading after parsing?

# NOTE: Sets the standard resolution
options["resolution"] = "low"
options["central_wl"] = 4.1

# NOTE: Set the integration times for the standalone
options["dit.matisse.ats.low"] = 0.111
options["dit.matisse.ats.med"] = 0.111
options["dit.matisse.ats.high"] = 0.111

options["dit.matisse.uts.low"] = 0.111
options["dit.matisse.uts.med"] = 0.111
options["dit.matisse.uts.high"] = 0.111

# NOTE: Set the integration times for the gra4mat
options["dit.gra4mat.ats.low"] = 0.6
options["dit.gra4mat.ats.med"] = 1.3
options["dit.gra4mat.ats.high"] = 3.

options["dit.gra4mat.uts.low"] = 0.6
options["dit.gra4mat.uts.med"] = 0.6
options["dit.gra4mat.uts.high"] = 0.6
