from p2obp.backend.create import create_ob

create_ob("HD 142666", "sci", "uts",
          operational_mode="gr", output_dir="assets/")

create_ob("HD100920", "cal", "uts", sci_name="HD 142666", 
          operational_mode="gr", output_dir="assets/")
