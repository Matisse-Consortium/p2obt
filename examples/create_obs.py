from p2obp.backend.automate import ob_creation


# path = "night_plan.yaml"
outdir = Path("assets/")

sci_lst = ["Beta Leo", "HD 100453"]
cal_lst = ["HD100920", "HD102964"]
tag_lst = []

# TODO: Make explanation/docs of the order_lst
order_lst = []

manual_lst = [sci_lst, cal_lst, tag_lst, order_lst]

res_dict = {}

ob_creation(outdir, sub_folder=None, manual_lst=manual_lst,
            res_dict=res_dict, operational_mode="both",
            standard_res="low", clean_previous=False)
