import os
import platform

if not os.path.exists("temp"):
    os.mkdir("temp")


def from_io_with_inschek_test():
    import os
    from pyemu import Pst, pst_utils
    # creation functionality
    dir = os.path.join("..", "verification", "10par_xsec", "template_mac")
    pst = Pst(os.path.join(dir, "pest.pst"))

    tpl_files = [os.path.join(dir, f) for f in pst.template_files]
    out_files = [os.path.join(dir, f) for f in pst.output_files]
    ins_files = [os.path.join(dir, f) for f in pst.instruction_files]
    in_files = [os.path.join(dir, f) for f in pst.input_files]

    new_pst = Pst.from_io_files(tpl_files, in_files,
                                ins_files, out_files,
                                pst_filename=os.path.join("temp", "test.pst"))
    print(new_pst.observation_data)
    return


def tpl_ins_test():
    import os
    from pyemu import Pst, pst_utils, helpers
    # creation functionality
    dir = os.path.join("..", "verification", "henry", "misc")
    files = os.listdir(dir)
    tpl_files, ins_files = [], []
    for f in files:
        if f.lower().endswith(".tpl") and "coarse" not in f:
            tpl_files.append(os.path.join(dir, f))
        if f.lower().endswith(".ins"):
            ins_files.append(os.path.join(dir, f))

    out_files = [f.replace(".ins", ".junk") for f in ins_files]
    in_files = [f.replace(".tpl", ".junk") for f in tpl_files]

    helpers.pst_from_io_files(tpl_files, in_files,
                                ins_files, out_files,
                                pst_filename=os.path.join("temp", "test.pst"))
    return


def res_test():
    import os
    import numpy as np
    from pyemu import Pst, pst_utils
    # residual functionality testing
    pst_dir = os.path.join("pst")

    p = Pst(os.path.join(pst_dir, "pest.pst"))
    phi_comp = p.phi_components
    assert "regul_p" in phi_comp
    assert "regul_m" in phi_comp

    p.adjust_weights_discrepancy(original_ceiling=False)
    d = np.abs(p.phi - p.nnz_obs)
    assert d < 1.0E-5

    p = Pst(os.path.join(pst_dir, "pest.pst"))
    p.adjust_weights_discrepancy(original_ceiling=False,bygroups=True)

    d = np.abs(p.phi - p.nnz_obs)
    assert d < 1.0E-5
    p.adjust_weights(obsgrp_dict={"head": 50})
    assert np.abs(p.phi_components["head"] - 50) < 1.0e-6

    # get()
    new_p = p.get()
    new_p.prior_information = p.prior_information
    new_file = os.path.join("temp", "new.pst")
    new_p.write(new_file)

    p_load = Pst(new_file, resfile=p.resfile)
    for gname in p.phi_components:
        d = np.abs(p.phi_components[gname] - p_load.phi_components[gname])
        assert d < 1.0e-5


def pst_manip_test():
    import os
    from pyemu import Pst
    pst_dir = os.path.join("pst")
    org_path = os.path.join(pst_dir, "pest.pst")
    new_path = os.path.join("temp", "pest1.pst")
    pst = Pst(org_path)
    pst.control_data.pestmode = "regularisation"
    pst.write(new_path)
    pst = Pst(new_path)
    pst.svd_data.maxsing = 1
    pst.write(new_path, update_regul=True)


def load_test():
    import os
    from pyemu import Pst, pst_utils
    pst_dir = os.path.join("pst")
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    # just testing all sorts of different pst files
    pst_files = os.listdir(pst_dir)
    exceptions = []
    load_fails = []
    for pst_file in pst_files:
        if pst_file.endswith(".pst") and not "comments" in pst_file and \
                not "missing" in pst_file:
            print(pst_file)
            try:
                p = Pst(os.path.join(pst_dir, pst_file))
            except Exception as e:
                exceptions.append(pst_file + " read fail: " + str(e))
                load_fails.append(pst_file)
                continue
            out_name = os.path.join(temp_dir, pst_file)
            print(out_name)
            # p.write(out_name,update_regul=True)
            try:
                p.write(out_name, update_regul=True)
            except Exception as e:
                exceptions.append(pst_file + " write fail: " + str(e))
                continue
            print(pst_file)
            try:
                p = Pst(out_name)
            except Exception as e:
                exceptions.append(pst_file + " reload fail: " + str(e))
                continue

    # with open("load_fails.txt",'w') as f:
    #    [f.write(pst_file+'\n') for pst_file in load_fails]
    if len(exceptions) > 0:
        raise Exception('\n'.join(exceptions))

def comments_test():
    import os
    import pyemu

    pst = pyemu.Pst(os.path.join("pst", "comments.pst"))
    pst.with_comments = True
    pst.write(os.path.join("temp", "comments.pst"))
    pst1 = pyemu.Pst(os.path.join("temp", "comments.pst"))
    assert pst1.parameter_data.extra.dropna().shape[0] == pst.parameter_data.extra.dropna().shape[0]
    pst1.with_comments = False
    pst1.write(os.path.join("temp", "comments.pst"))
    pst2 = pyemu.Pst(os.path.join("temp", "comments.pst"))
    assert pst2.parameter_data.dropna().shape[0] == 0




def tied_test():
    import os
    import pyemu
    pst_dir = os.path.join("pst")
    pst = pyemu.Pst(os.path.join(pst_dir, "br_opt_no_zero_weighted.pst"))
    print(pst.tied)
    pst.write(os.path.join("temp", "pest_tied_tester_1.pst"))


    par = pst.parameter_data
    par.loc[pst.par_names[::3], "partrans"] = "tied"
    try:
        pst.write(os.path.join("temp", "pest_tied_tester_1.pst"))
    except:
        pass
    else:
        raise Exception()
    par.loc[pst.par_names[::3], "partied"] = pst.par_names[0]

    pst = pyemu.Pst(os.path.join("pst", "pest.pst"))
    print(pst.tied)
    par = pst.parameter_data
    par.loc[pst.par_names[2], "partrans"] = "tied"
    print(pst.tied)
    par.loc[pst.par_names[2], "partied"] = "junk1"
    pst.write(os.path.join("temp", "test.pst"))
    pst = pyemu.Pst(os.path.join("temp", "test.pst"))

    pst = pyemu.Pst(os.path.join("pst", "pest.pst"))
    print(pst.tied)
    par = pst.parameter_data
    par.loc[pst.par_names[2], "partrans"] = "tied"
    par.loc[pst.par_names[2], "partied"] = "junk"
    pst.write(os.path.join("temp", "test.pst"))
    pst = pyemu.Pst(os.path.join("temp", "test.pst"))


def derivative_increment_tests():
    import os
    import pyemu

    pst = pyemu.Pst(os.path.join("pst", "inctest.pst"))
    pst.calculate_pertubations()


def pestpp_args_test():
    import os
    import pyemu
    pst_dir = os.path.join("pst")
    pst = pyemu.Pst(os.path.join(pst_dir, "br_opt_no_zero_weighted.pst"))
    pst.pestpp_options["lambdas"] = "0.1,0.2,0.3"
    pst.write(os.path.join("temp", "temp.pst"))
    pst = pyemu.Pst(os.path.join("temp", "temp.pst"))
    print(pst.pestpp_options)


def reweight_test():
    import os
    import numpy as np
    from pyemu import Pst, pst_utils
    pst_dir = os.path.join("pst")
    p = Pst(os.path.join(pst_dir, "pest.pst"))
    obsgrp_dict = {"pred": 1.0, "head": 1.0, "conc": 1.0}
    p.adjust_weights(obsgrp_dict=obsgrp_dict)
    assert np.abs(p.phi - 3.0) < 1.0e-5, p.phi

    obs = p.observation_data
    obs.loc[obs.obgnme == "pred", "weight"] = 0.0
    assert np.abs(p.phi - 2.0) < 1.0e-5, p.phi

    obs_dict = {"pd_one": 1.0, "pd_ten": 1.0}
    p.adjust_weights(obs_dict=obs_dict)
    assert np.abs(p.phi - 4.0) < 1.0e-5, p.phi


def reweight_res_test():
    import os
    import numpy as np
    import pyemu
    pst = pyemu.Pst(os.path.join("pst", "pest.pst"))
    print(pst.res.loc[pst.nnz_obs_names, :])
    print(pst.phi, pst.nnz_obs)
    pst.adjust_weights_discrepancy(bygroups=True)
    print(pst.phi, pst.nnz_obs)
    assert np.abs(pst.phi - pst.nnz_obs) < 1.0e-6


def regul_rectify_test():
    import os
    import pyemu
    pst = pyemu.Pst(os.path.join("pst", "inctest.pst"))
    pyemu.helpers.zero_order_tikhonov(pst)
    assert pst.prior_information.shape[0] == pst.npar_adj
    pst._update_control_section()
    assert pst.control_data.nprior == pst.prior_information.shape[0]
    fix_names = pst.adj_par_names[::2]
    pst.parameter_data.loc[fix_names, "partrans"] = "fixed"
    pst.rectify_pi()
    assert pst.prior_information.shape[0] == pst.npar_adj
    pst._update_control_section()
    assert pst.control_data.nprior == pst.prior_information.shape[0]


def nnz_groups_test():
    import os
    import pyemu
    pst_dir = os.path.join("pst")
    pst = pyemu.Pst(os.path.join(pst_dir, "br_opt_no_zero_weighted.pst"))
    org_og = pst.obs_groups
    org_nnz_og = pst.nnz_obs_groups
    obs = pst.observation_data
    obs.loc[obs.obgnme == org_og[0], "weight"] = 0.0
    new_og = pst.obs_groups
    new_nnz_og = pst.nnz_obs_groups
    assert org_og[0] not in new_nnz_og


def adj_group_test():
    import os
    import pyemu
    pst_dir = os.path.join("pst")
    pst = pyemu.Pst(os.path.join(pst_dir, "pest.pst"))
    par = pst.parameter_data
    par.loc[par.pargp.apply(lambda x: x in pst.par_groups[1:]),"partrans"] = "fixed"
    assert pst.adj_par_groups == [pst.par_groups[0]]

def regdata_test():
    import os
    import pyemu

    pst = pyemu.Pst(os.path.join("pst", "pest.pst"))
    phimlim = 10.0
    pst.reg_data.phimlim = phimlim
    pst.control_data.pestmode = "regularization"
    pst.write(os.path.join("temp", "pest_regultest.pst"))
    pst_new = pyemu.Pst(os.path.join("temp", "pest_regultest.pst"))
    assert pst_new.reg_data.phimlim == phimlim









def add_pi_test():
    import os
    import pyemu
    pst = pyemu.Pst(os.path.join("pst", "pest.pst"))
    pst.prior_information = pst.null_prior
    par_names = pst.parameter_data.parnme[:10]
    pst.add_pi_equation(par_names, coef_dict={par_names[1]: -1.0})
    pst.write(os.path.join("temp", "test.pst"))

    pst = pyemu.Pst(os.path.join("temp", "test.pst"))
    print(pst.prior_information)


def setattr_test():
    import os
    import pyemu
    pst = pyemu.Pst(os.path.join("pst", "pest.pst"))
    pst.model_command = 'test'
    assert isinstance(pst.model_command, list)
    pst.model_command = ["test", "test1"]
    assert isinstance(pst.model_command, list)
    pst.write(os.path.join("temp", "test.pst"))
    pst = pyemu.Pst(os.path.join("temp", "test.pst"))
    assert isinstance(pst.model_command, list)


def add_pars_test():
    import os
    import pyemu
    pst = pyemu.Pst(os.path.join("pst", "pest.pst"))
    npar = pst.npar
    tpl_file = os.path.join("temp", "crap.in.tpl")
    with open(tpl_file, 'w') as f:
        f.write("ptf ~\n")
        f.write("  ~junk1   ~\n")
        f.write("  ~ {0}  ~\n".format(pst.parameter_data.parnme[0]))
    pst.add_parameters(tpl_file, "crap.in", pst_path="temp")
    assert npar + 1 == pst.npar
    assert "junk1" in pst.parameter_data.parnme
    assert os.path.join("temp", "crap.in") in pst.input_files
    assert os.path.join("temp", "crap.in.tpl") in pst.template_files


def add_obs_test():
    import os
    import pyemu
    pst = pyemu.Pst(os.path.join("pst", "pest.pst"))
    nobs = pst.nobs
    ins_file = os.path.join("temp", "crap.out.ins")
    out_file = os.path.join("temp", "crap.out")
    oval = 1234.56
    with open(ins_file, 'w') as f:
        f.write("pif ~\n")
        # f.write("  ~junk1   ~\n")
        # f.write("  ~ {0}  ~\n".format(pst.parameter_data.parnme[0]))
        f.write("l1 w  !{0}!\n".format("crap1"))
    with open(out_file, "w") as f:
        f.write("junk1  {0:8.2f} \n".format(oval))
    pst.add_observations(ins_file, out_file, pst_path="temp")
    assert nobs + 1 == pst.nobs
    assert "crap1" in pst.observation_data.obsnme
    assert os.path.join("temp", "crap.out") in pst.output_files, str(pst.output_files)
    assert os.path.join("temp", "crap.out.ins") in pst.instruction_files
    print(pst.observation_data.loc["crap1", "obsval"], oval)


def test_write_input_files():
    import os
    import shutil
    import numpy as np
    import pyemu
    from pyemu import Pst, pst_utils
    # creation functionality
    dir = os.path.join("..", "verification", "10par_xsec", "template_mac")
    if os.path.exists("temp_dir"):
        shutil.rmtree("temp_dir")
    shutil.copytree(dir, "temp_dir")
    os.chdir("temp_dir")
    pst = Pst(os.path.join("pest.pst"))
    pst.write_input_files()
    arr1 = np.loadtxt(pst.input_files[0])
    print(pst.parameter_data.parval1)
    pst.parameter_data.loc[:, "parval1"] *= 10.0
    pst.write_input_files()
    arr2 = np.loadtxt(pst.input_files[0])
    assert (arr1 * 10).sum() == arr2.sum()
    os.chdir("..")


def res_stats_test():
    import os
    import pyemu

    import os
    import numpy as np
    from pyemu import Pst, pst_utils
    # residual functionality testing
    pst_dir = os.path.join("pst")

    p = pyemu.pst_utils.generic_pst(["p1"], ["o1"])
    try:
        p.get_res_stats()
    except:
        pass
    else:
        raise Exception()

    p = Pst(os.path.join(pst_dir, "pest.pst"))
    phi_comp = p.phi_components
    # print(phi_comp)
    df = p.get_res_stats()
    assert np.abs(df.loc["rss", "all"] - p.phi) < 1.0e-6, "{0},{1}".format(df.loc["rss", "all"], p.phi)
    for pc in phi_comp.keys():
        assert phi_comp[pc] == p.phi_components[pc]


def write_tables_test():
    import os
    import pyemu

    pst = pyemu.Pst(os.path.join("pst", "freyberg_gr.pst"))
    group_names = {"w0": "wells t"}
    pst.write_par_summary_table(group_names=group_names)
    pst.write_obs_summary_table(group_names={"calhead": "calibration heads"})

def test_e_clean():
    import os
    import pyemu

    pst_name = os.path.join("pst", "test_missing_e.pst")
    try:
        pst = pyemu.Pst(pst_name)
    except:
        pass
    else:
        raise Exception()

    clean_name = os.path.join("temp", "clean.pst")
    pyemu.pst_utils.clean_missing_exponent(pst_name, clean_name)
    pst = pyemu.Pst(clean_name)


def run_test():
    import os
    import pyemu

    pst = pyemu.Pst(os.path.join("pst", "pest.pst"))
    # pst.run("pestchek")
    pst.write(os.path.join("temp", "test.pst"))


    try:
        pst.run("pestchek")
    except:
        print("error calling pestchek")


def rectify_pgroup_test():
    import os
    import pyemu
    pst = pyemu.Pst(os.path.join("pst", "pest.pst"))
    npar = pst.npar
    tpl_file = os.path.join("temp", "crap.in.tpl")
    with open(tpl_file, 'w') as f:
        f.write("ptf ~\n")
        f.write("  ~junk1   ~\n")
        f.write("  ~ {0}  ~\n".format(pst.parameter_data.parnme[0]))
    # print(pst.parameter_groups)

    pst.add_parameters(tpl_file, "crap.in", pst_path="temp")

    # print(pst.parameter_groups)
    pst.rectify_pgroups()
    # print(pst.parameter_groups)

    pst.parameter_groups.loc["pargp", "inctyp"] = "absolute"
    print(pst.parameter_groups)
    pst.write(os.path.join('temp', "test.pst"))
    print(pst.parameter_groups)


def try_process_ins_test():
    import os
    import numpy as np
    import pandas as pd
    import pyemu

    ins_file = os.path.join("utils", "BH.mt3d.processed.ins")
    i = pyemu.pst_utils.InstructionFile(ins_file)
    df2 = i.read_output_file(ins_file.replace(".ins",""))



    # df1 = pyemu.pst_utils._try_run_inschek(ins_file,ins_file.replace(".ins",""))
    df1 = pd.read_csv(ins_file.replace(".ins", ".obf"), delim_whitespace=True, names=["obsnme", "obsval"], index_col=0)
    # df1.index = df1.obsnme
    df1.loc[:, "obsnme"] = df1.index
    df1.index = df1.obsnme
    # df1 = df1.loc[df.obsnme,:]
    diff = df2.obsval - df1.obsval
    print(diff.max(), diff.min())
    print(diff.sum())
    assert diff.sum() < 1.0e+10



def sanity_check_test():
    import os
    import pyemu
    pst = pyemu.Pst(os.path.join("pst", "pest.pst"))
    pst.parameter_data.loc[:, "parnme"] = "crap"
    pst.observation_data.loc[:, "obsnme"] = "crap"

    pst.write(os.path.join("temp", "test.pst"))



def csv_to_ins_test():
    import os
    import numpy as np
    import pandas as pd
    import pyemu

    cnames = ["col{0}".format(i) for i in range(10)]
    rnames = ["row{0}".format(i) for i in range(10)]
    df = pd.DataFrame(index=rnames,columns=cnames)
    df.loc[:,:] = np.random.random(df.shape)
    df.to_csv(os.path.join("temp", "temp.csv"))
    names = pyemu.pst_utils.csv_to_ins_file(df, ins_filename=os.path.join("temp", "temp.csv.ins"),
                                            only_cols=cnames[0],prefix="test")
    assert len(names) == df.shape[0], names
    for name in names.obsnme:
        assert name.startswith("test"),name

    names = pyemu.pst_utils.csv_to_ins_file(df, ins_filename=os.path.join("temp", "temp.csv.ins"),
                                            only_cols=cnames[0:2])
    assert len(names) == df.shape[0]*2, names

    names = pyemu.pst_utils.csv_to_ins_file(df, ins_filename=os.path.join("temp", "temp.csv.ins"),
                                            only_rows=rnames[0])
    assert len(names) == df.shape[1], names

    names = pyemu.pst_utils.csv_to_ins_file(df, ins_filename=os.path.join("temp", "temp.csv.ins"),
                                            only_rows=rnames[0:2])
    assert len(names) == df.shape[1] * 2, names

    names = pyemu.pst_utils.csv_to_ins_file(df,ins_filename=os.path.join("temp","temp.csv.ins"))
    assert len(names) == df.shape[0] * df.shape[1]

    df.columns = ["col" for i in range(df.shape[1])]
    names = pyemu.pst_utils.csv_to_ins_file(df, ins_filename=os.path.join("temp", "temp.csv.ins"))
    assert len(names) == df.shape[0] * df.shape[1]

    names = pyemu.pst_utils.csv_to_ins_file(df, ins_filename=os.path.join("temp", "temp.csv.ins"),
                                            only_cols="col")
    assert len(names) == df.shape[0] * df.shape[1]

    df.index = ["row" for i in range(df.shape[0])]
    names = pyemu.pst_utils.csv_to_ins_file(df, ins_filename=os.path.join("temp", "temp.csv.ins"))
    assert len(names) == df.shape[0] * df.shape[1]

    names = pyemu.pst_utils.csv_to_ins_file(df, ins_filename=os.path.join("temp", "temp.csv.ins"),
                                            only_cols="col",only_rows="row")
    assert len(names) == df.shape[0] * df.shape[1]



def lt_gt_constraint_names_test():
    import os
    import pyemu
    import os
    import pyemu
    pst = pyemu.Pst(os.path.join("pst", "pest.pst"))
    obs = pst.observation_data
    obs.loc[:,"weight"] = 1.0
    pst.observation_data.loc[pst.obs_names[:4],"obgnme"] = "lessjunk"
    pst.observation_data.loc[pst.obs_names[4:8], "obgnme"] = "l_junk"
    pst.observation_data.loc[pst.obs_names[8:12], "obgnme"] = "greaterjunk"
    pst.observation_data.loc[pst.obs_names[12:16], "obgnme"] = "g_junk"
    assert pst.less_than_obs_constraints.shape[0] == 8
    assert pst.greater_than_obs_constraints.shape[0] == 8

    obs.loc[:, "weight"] = 0.0
    assert pst.less_than_obs_constraints.shape[0] == 0
    assert pst.greater_than_obs_constraints.shape[0] == 0

    pi = pst.prior_information
    pi.loc[pst.prior_names[:4],"obgnme"] = "lessjunk"
    pi.loc[pst.prior_names[4:8], "obgnme"] = "l_junk"
    pi.loc[pst.prior_names[8:12], "obgnme"] = "greaterjunk"
    pi.loc[pst.prior_names[12:16], "obgnme"] = "g_junk"
    assert pst.less_than_pi_constraints.shape[0] == 8
    assert pst.greater_than_pi_constraints.shape[0] == 8

    pi.loc[:, "weight"] = 0.0
    assert pst.less_than_pi_constraints.shape[0] == 0
    assert pst.greater_than_pi_constraints.shape[0] == 0


def new_format_test():
    import numpy as np
    import pyemu
    pst_files = [f for f in os.listdir("pst") if f.endswith(".pst")]
    for pst_file in pst_files:
        try:
            pst = pyemu.Pst(os.path.join("pst", pst_file))
        except:
            print("error loading",pst_file)
            continue
        print(pst_file)
        npar,nobs,npr = pst.npar,pst.nobs,pst.nprior
        ppo = pst.pestpp_options
        pst.write("test.pst",version=2)



        pst_new = pyemu.Pst("test.pst")
        npar1, nobs1, npr1 = pst_new.npar, pst_new.nobs, pst_new.nprior
        ppo1 = pst_new.pestpp_options
        assert len(ppo) == len(ppo1)
        assert npar == npar1
        assert nobs == nobs1
        assert npr == npr1,"{0}: {1},{2}".format(pst_file,npr,npr1)


        pst_new.write("test.pst",version=1)
        pst_new = pyemu.Pst("test.pst")
        npar1, nobs1, npr1 = pst_new.npar, pst_new.nobs, pst_new.nprior
        ppo1 = pst_new.pestpp_options
        assert len(ppo) == len(ppo1)
        assert npar == npar1
        assert nobs == nobs1
        assert npr == npr1, "{0}: {1},{2}".format(pst_file, npr, npr1)
        pst_new.write("test.pst",version=2)
        pst_new = pyemu.Pst("test.pst")
        npar1, nobs1, npr1 = pst_new.npar, pst_new.nobs, pst_new.nprior
        ppo1 = pst_new.pestpp_options
        assert len(ppo) == len(ppo1)
        assert npar == npar1
        assert nobs == nobs1
        assert npr == npr1, "{0}: {1},{2}".format(pst_file, npr, npr1)


    pst_new.parameter_groups.loc[:,:] = np.NaN
    pst_new.parameter_groups.dropna(inplace=True)
    pst_new.write("test.pst",version=2)
    pst_new = pyemu.Pst("test.pst")


    pst_new.parameter_data.loc[:,"counter"] = 1
    pst_new.observation_data.loc[:,"x"] = 999.0
    pst_new.observation_data.loc[:,'y'] = 888.0
    pst_new.write("test.pst",version=2)
    pst_new = pyemu.Pst("test.pst")
    assert "counter" in pst_new.parameter_data.columns
    assert "x" in pst_new.observation_data.columns
    assert "y" in pst_new.observation_data.columns

    # lines = open("test.pst").readlines()
    # for i,line in enumerate(lines):
    #     lines[i] = line.replace("header=True","header=False")
    # with open("test.pst",'w') as f:
    #     [f.write(line) for line in lines]
    # try:
    #     pst_new = pyemu.Pst("test.pst")
    # except:
    #     pass
    # else:
    #     raise Exception()


def change_limit_test():
    import numpy as np
    import pyemu
    pst = pyemu.Pst(os.path.join("pst","pest.pst"))
    #print(pst.parameter_data)
    cols = ["parval1", "rel_upper", "rel_lower", "fac_upper", "fac_lower","chg_upper","chg_lower"]
    pst.control_data.relparmax = 3
    pst.control_data.facparmax = 3
    par = pst.parameter_data

    par.loc[:,"parval1"] = 1.0
    df = pst.get_par_change_limits()
    assert df.rel_upper.mean() == 4.0
    assert df.rel_lower.mean() == -2.0
    assert df.fac_upper.mean() == 3.0
    assert np.abs(df.fac_lower.mean() -  0.33333) < 1.0e-3

    pst.control_data.facorig = 2.0
    par.loc[:,"partrans"] = "none"
    df = pst.get_par_change_limits()
    assert df.rel_upper.mean() == 8.0
    assert df.rel_lower.mean() == -4.0
    assert df.fac_upper.mean() == 6.0
    assert np.abs(df.fac_lower.mean() - 0.66666) < 1.0e-3

    pst.control_data.facorig = 0.001
    par.loc[:, "partrans"] = "none"
    par.loc[:, "parval1"] = -1.0
    df = pst.get_par_change_limits()
    #print(df.loc[:, cols])
    assert df.rel_upper.mean() == 2.0
    assert df.rel_lower.mean() == -4.0
    assert df.fac_lower.mean() == -3.0
    assert np.abs(df.fac_upper.mean() + 0.33333) < 1.0e-3

    print(df.loc[:,["eff_upper","eff_lower"]])
    print(df.loc[:,cols])


def process_output_files_test():

    import os
    import numpy as np
    from pyemu import Pst, pst_utils

    # ins_file = os.path.join("utils","hauraki_transient.mt3d.processed.ins")
    # out_file = ins_file.replace(".ins","")
    #
    # i = pst_utils.InstructionFile(ins_file)
    # print(i.read_output_file(out_file))
    # return

    ins_dir = "ins"
    ins_files = [os.path.join(ins_dir,f) for f in os.listdir(ins_dir) if f.endswith(".ins")]
    ins_files.sort()
    out_files = [f.replace(".ins","") for f in ins_files]
    print(ins_files)

    i4 = pst_utils.InstructionFile(ins_files[3])
    s4 = i4.read_output_file(out_files[3])
    print(s4)
    assert s4.loc["h01_02","obsval"] == 1.024
    assert s4.loc["h01_10","obsval"] == 4.498
    i3 = pst_utils.InstructionFile(ins_files[2])
    s3 = i3.read_output_file(out_files[2])
    #print(s3)
    assert s3.loc["test","obsval"] == 1.23456
    assert s3.loc["h01_02","obsval"] == 1.024

    i1 = pst_utils.InstructionFile(ins_files[0])
    s1 = i1.read_output_file(out_files[0])
    a1 = np.loadtxt(out_files[0]).flatten()
    assert np.abs(s1.obsval.values - a1).sum() == 0.0

    i2 = pst_utils.InstructionFile(ins_files[1])
    s2 = i2.read_output_file(out_files[1])
    assert s2.loc["h01_02","obsval"] == 1.024


if __name__ == "__main__":
    # process_output_files_test()
    #change_limit_test()
    #new_format_test()
    #lt_gt_constraint_names_test()
    #csv_to_ins_test()
    #pst_from_flopy_geo_draw_test()
    #pst_from_flopy_specsim_draw_test()
    #try_process_ins_test()
    # write_tables_test()
    #res_stats_test()
    test_write_input_files()
    # add_obs_test()
    # add_pars_test()
    # setattr_test()
    # run_array_pars()
    #from_flopy_zone_pars()
    #from_flopy_pp_test()
    # from_flopy()
    # add_obs_test()
    #from_flopy_kl_test()
    #from_flopy_reachinput()
    # add_pi_test()
    # regdata_test()
    # nnz_groups_test()
    # adj_group_test()
    # regul_rectify_test()
    # derivative_increment_tests()
    # tied_test()
    # smp_test()
    # smp_dateparser_test()
    # pst_manip_test()
    # tpl_ins_test()
    # comments_test()
    # test_e_clean()
    # load_test()
    #res_test()
    # smp_test()
    #from_io_with_inschek_test()
    #pestpp_args_test()
    # reweight_test()
    # reweight_res_test()
    # run_test()
    # rectify_pgroup_test()
    # sanity_check_test()
