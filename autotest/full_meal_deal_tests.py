import os
import platform

ext = ''
bin_path = os.path.join("..","..","bin")
if "linux" in platform.platform().lower():
    bin_path = os.path.join(bin_path,"linux")
elif "darwin" in platform.platform().lower():
    bin_path = os.path.join(bin_path,"mac")
else:
    bin_path = os.path.join(bin_path,"win")
    ext = '.exe'
    

mf_exe_name = os.path.join(bin_path,"mfnwt")
pp_exe_name = os.path.join(bin_path, "pestpp-glm")
ies_exe_name = os.path.join(bin_path, "pestpp-ies")
swp_exe_name = os.path.join(bin_path, "pestpp-swp")

# for f in [mf_exe_name,pp_exe_name,ies_exe_name]:
#     if not os.path.exists(f):
#         raise Exception("{0} not found",f)

def freyberg_test():
    import shutil

    import numpy as np
    import pandas as pd
    try:
        import flopy
    except Exception as e:
        return
    import pyemu

    ext = ''
    bin_path = os.path.join("..", "..", "bin")
    if "linux" in platform.platform().lower():
        bin_path = os.path.join(bin_path, "linux")
    elif "darwin" in platform.platform().lower():
        bin_path = os.path.join(bin_path, "mac")
    else:
        bin_path = os.path.join(bin_path, "win")
        ext = '.exe'

    org_model_ws = os.path.join("..", "examples", "freyberg_sfr_update")
    nam_file = "freyberg.nam"
    m = flopy.modflow.Modflow.load(nam_file, model_ws=org_model_ws, check=False,forgive=False,
                                   exe_name=mf_exe_name)
    org_model_ws = "temp"

    m.change_model_ws(org_model_ws)
    m.write_input()
    print("{0} {1}".format(mf_exe_name,m.name+".nam"),org_model_ws)
    pyemu.os_utils.run("{0} {1}".format(mf_exe_name,m.name+".nam"),cwd=org_model_ws)
    hds_file = "freyberg.hds"
    list_file = "freyberg.list"
    for f in [hds_file, list_file]:
        assert os.path.exists(os.path.join(org_model_ws, f))

    new_model_ws = "template1"

    props = [["upw.hk",None],["upw.vka",None],["upw.ss",None],["rch.rech",None]]

    hds_kperk = [[kper,0] for kper in range(m.nper)]

    temp_bc_props = [["wel.flux",kper] for kper in range(m.nper)]
    spat_bc_props= [["wel.flux",2]]

    ph = pyemu.helpers.PstFromFlopyModel(nam_file,new_model_ws,org_model_ws,
                                         const_props=props,
                                         zone_props=props,
                                         kl_props=props,
                                         pp_props=props,
                                         grid_props=props,
                                         hds_kperk=hds_kperk,
                                         sfr_pars=True,sfr_obs=True,
                                         spatial_bc_props=spat_bc_props,
                                         temporal_bc_props=temp_bc_props,
                                         remove_existing=True,
                                         model_exe_name="mfnwt")
    tmp = mf_exe_name.split(os.sep)
    tmp = os.path.join(*tmp[1:])+ext
    assert os.path.exists(tmp),tmp
    shutil.copy2(tmp,os.path.join(new_model_ws,"mfnwt"+ext))
    ph.pst.control_data.noptmax = 0
    ph.pst.write(os.path.join(new_model_ws,"test.pst"))
    print("{0} {1}".format(pp_exe_name,"test.pst"), new_model_ws)
    pyemu.os_utils.run("{0} {1}".format(pp_exe_name,"test.pst"),cwd=new_model_ws)
    for ext in ["rec",'rei',"par"]:
        assert os.path.exists(os.path.join(new_model_ws,"test.{0}".format(ext))),ext
    ph.pst.parrep(os.path.join(new_model_ws,"test.par"))
    res = pyemu.pst_utils.read_resfile(os.path.join(new_model_ws,"test.rei"))
    ph.pst.observation_data.loc[res.name,"obsval"] = res.modelled
    ph.pst.write(os.path.join(new_model_ws,"test.pst"))
    print("{0} {1}".format(pp_exe_name, "test.pst"), new_model_ws)

    pyemu.os_utils.run("{0} {1}".format(pp_exe_name,"test.pst"),cwd=new_model_ws)
    for ext in ["rec",'rei',"par","iobj"]:
        assert os.path.exists(os.path.join(new_model_ws,"test.{0}".format(ext))),ext
    df = pd.read_csv(os.path.join(new_model_ws,"test.iobj"))
    assert df.total_phi.iloc[0] < 1.0e-10
    pe = ph.draw(10)
    pe.to_csv(os.path.join(new_model_ws,"par_en.csv"))
    ph.pst.pestpp_options["ies_par_en"] = "par_en.csv"
    ph.pst.control_data.noptmax = 1
    ph.pst.write(os.path.join(new_model_ws, "test.pst"))
    master_dir = "test_master"
    pyemu.os_utils.start_workers(new_model_ws,ies_exe_name,"test.pst",
                                num_workers=10,worker_root='.',
                                master_dir=master_dir,silent_master=False)

    df = pd.read_csv(os.path.join(master_dir,"test.phi.meas.csv"),index_col=0)
    init_phi = df.loc[0,"mean"]
    final_phi = df.loc[1,"mean"]
    assert final_phi < init_phi


def fake_run_test():
    import os
    import numpy as np
    import pyemu
    new_model_ws = "template1"
    if not os.path.exists(new_model_ws):
        freyberg_test()
    pst = pyemu.Pst(os.path.join(new_model_ws,"freyberg.pst"))
    pst.pestpp_options["ies_num_reals"] = 10
    pst.pestpp_options["ies_par_en"] = "par_en.csv"
    pst.control_data.noptmax = 0
    #pst = pyemu.helpers.setup_fake_forward_run(pst,"fake.pst",org_cwd=new_model_ws)
    #pyemu.os_utils.run("{0} {1}".format(pp_exe_name,"fake.pst"),cwd=new_model_ws)
    #pyemu.os_utils.run("{0} {1}".format(ies_exe_name, "fake.pst"), cwd=new_model_ws)

    new_cwd = "fake_test"
    pst = pyemu.helpers.setup_fake_forward_run(pst, "fake.pst", org_cwd=new_model_ws,new_cwd=new_cwd)
    s = pst.process_output_files(new_cwd)
    if s is not None:
        assert s.dropna().shape[0] == pst.nobs
        obs = pst.observation_data

        diff = (100 * (obs.obsval - s.obsval) / obs.obsval).apply(np.abs)

        print(diff)
        print(obs.loc[diff>0.0,"obsval"],s.loc[diff>0.0,"obsval"])
        assert diff.sum() < 1.0e-3,diff.sum()
    pyemu.os_utils.run("{0} {1}".format(ies_exe_name, "fake.pst"), cwd=new_cwd)



def freyberg_kl_pp_compare():
    import shutil
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    try:
        import flopy
    except Exception as e:
        return
    import pyemu

    ext = ''
    bin_path = os.path.join("..", "..", "bin")
    if "linux" in platform.platform().lower():
        bin_path = os.path.join(bin_path, "linux")
    elif "darwin" in platform.platform().lower():
        bin_path = os.path.join(bin_path, "mac")
    else:
        bin_path = os.path.join(bin_path, "win")
        ext = '.exe'

    org_model_ws_base = os.path.join("..", "examples", "freyberg_sfr_update")
    nam_file = "freyberg.nam"
    m = flopy.modflow.Modflow.load(nam_file, model_ws=org_model_ws_base, check=False, forgive=False,
                                   exe_name=mf_exe_name)
    org_model_ws = "temp"

    m.change_model_ws(org_model_ws)
    m.write_input()
    print("{0} {1}".format(mf_exe_name, m.name + ".nam"), org_model_ws)
    pyemu.os_utils.run("{0} {1}".format(mf_exe_name, m.name + ".nam"), cwd=org_model_ws)
    hds_file = "freyberg.hds"
    list_file = "freyberg.list"
    for f in [hds_file, list_file]:
        assert os.path.exists(os.path.join(org_model_ws, f))

    new_model_ws = "template1"

    props = [["upw.hk", None]]

    hds_kperk = [[kper, 0] for kper in range(m.nper)]

    temp_bc_props = [["wel.flux", kper] for kper in range(m.nper)]
    spat_bc_props = [["wel.flux", 2]]

    ph = pyemu.helpers.PstFromFlopyModel(nam_file, new_model_ws, org_model_ws,
                                         kl_props=props,
                                         kl_num_eig=66,
                                         pp_props=props,
                                         pp_space=3,
                                         hds_kperk=hds_kperk,
                                         sfr_obs=True,
                                         remove_existing=True,
                                         model_exe_name="mfnwt")

    obs = ph.pst.observation_data
    hds_obs = obs.loc[obs.obgnme=="hds",:].copy()
    hds_obs.loc[:, "i"] = hds_obs.obsnme.apply(lambda x: int(x.split('_')[2]))
    hds_obs.loc[:, "j"] = hds_obs.obsnme.apply(lambda x: int(x.split('_')[3]))
    hds_obs.loc[:,'ij'] = hds_obs.apply(lambda x: "{0:02d}{1:02d}".format(x.i,x.j),axis=1)
    hds_obs.loc[:, "kper"] = hds_obs.obsnme.apply(lambda x: int(x.split('_')[4]))
    hds_obs = hds_obs.loc[hds_obs.kper==hds_obs.kper.max(),:]
    obs.loc[:,"weight"] = 0.0
    obs_locs = pd.read_csv(os.path.join(org_model_ws_base,"obs_loc.csv"))
    obs_locs.loc[:,"ij"] = obs_locs.apply(lambda x: "{0:02d}{1:02d}".format(x.row-1,x.col-1),axis=1)
    print(obs_locs)
    print(hds_obs.i.max(),hds_obs.j.max())
    print(hds_obs.head())
    hds_nz_obs = hds_obs.loc[hds_obs.ij.apply(lambda x: x in obs_locs.ij.values),"obsnme"]
    print(hds_nz_obs)
    obs.loc[hds_nz_obs,"weight"] = 1.0
    obs.loc[hds_nz_obs,"obsval"] += np.random.normal(0.0,1.0,len(hds_nz_obs))
    ph.pst.control_data.noptmax = 6
    ph.pst.parameter_data.loc[ph.pst.parameter_data.pargp!="pp_hk0","partrans"] = "fixed"
    ph.pst.write(os.path.join(new_model_ws,"pest_pp.pst"))
    ph.pst.parameter_data.loc[:,"partrans"] = "log"
    ph.pst.parameter_data.loc[ph.pst.parameter_data.pargp == "pp_hk0", "partrans"] = "fixed"
    ph.pst.write(os.path.join(new_model_ws, "pest_kl.pst"))

    pyemu.os_utils.start_workers(new_model_ws,"pestpp-ies","pest_pp.pst", num_workers=10,worker_root='.',
                                master_dir="pest_pp")




if __name__ == "__main__":




    freyberg_test()
    #freyberg_kl_pp_compare()
    #import shapefile
    #run_sweep_test()
    fake_run_test()