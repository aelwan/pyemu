"""Various PEST(++) control file peripheral operations"""
from __future__ import print_function, division
import os
import warnings
import multiprocessing as mp
import numpy as np
import pandas as pd
pd.options.display.max_colwidth = 100

import pyemu
from ..pyemu_warnings import PyemuWarning
#formatters
#SFMT = lambda x: "{0:>20s}".format(str(x.decode()))
def SFMT(item):
    try:
        s = "{0:<20s} ".format(item.decode())
    except:
        s = "{0:<20s} ".format(str(item))
    return s

SFMT_LONG = lambda x: "{0:<50s} ".format(str(x))
IFMT = lambda x: "{0:<10d} ".format(int(x))
FFMT = lambda x: "{0:<20.10E} ".format(float(x))

def str_con(item):
    if len(item) == 0:
        return np.NaN
    return item.lower().strip()

pst_config = {}

# parameter stuff
pst_config["tied_dtype"] = np.dtype([("parnme", "U20"), ("partied","U20")])
pst_config["tied_fieldnames"] = ["parnme","partied"]
pst_config["tied_format"] = {"parnme":SFMT,"partied":SFMT}
pst_config["tied_converters"] = {"parnme":str_con,"partied":str_con}
pst_config["tied_defaults"] = {"parnme":"dum","partied":"dum"}

pst_config["par_dtype"] = np.dtype([("parnme", "U20"), ("partrans","U20"),
                                   ("parchglim","U20"),("parval1", np.float64),
                                   ("parlbnd",np.float64),("parubnd",np.float64),
                                   ("pargp","U20"),("scale", np.float64),
                                   ("offset", np.float64),("dercom",np.int)])
pst_config["par_fieldnames"] = "PARNME PARTRANS PARCHGLIM PARVAL1 PARLBND PARUBND " +\
                              "PARGP SCALE OFFSET DERCOM"
pst_config["par_fieldnames"] = pst_config["par_fieldnames"].lower().strip().split()
pst_config["par_format"] = {"parnme": SFMT, "partrans": SFMT,
                           "parchglim": SFMT, "parval1": FFMT,
                           "parlbnd": FFMT, "parubnd": FFMT,
                           "pargp": SFMT, "scale": FFMT,
                           "offset": FFMT, "dercom": IFMT}
pst_config["par_converters"] = {"parnme": str_con, "pargp": str_con,
                                "parval1":np.float,"parubnd":np.float,
                                "parlbnd":np.float,"scale":np.float,
                                "offset":np.float}
pst_config["par_defaults"] = {"parnme":"dum","partrans":"log","parchglim":"factor",
                             "parval1":1.0,"parlbnd":1.1e-10,"parubnd":1.1e+10,
                             "pargp":"pargp","scale":1.0,"offset":0.0,"dercom":1}


# parameter group stuff
pst_config["pargp_dtype"] = np.dtype([("pargpnme", "U20"), ("inctyp","U20"),
                                   ("derinc", np.float64),
                                   ("derinclb",np.float64),("forcen","U20"),
                                   ("derincmul",np.float64),("dermthd", "U20"),
                                   ("splitthresh", np.float64),("splitreldiff",np.float64),
                                      ("splitaction","U20")])
pst_config["pargp_fieldnames"] = "PARGPNME INCTYP DERINC DERINCLB FORCEN DERINCMUL " +\
                        "DERMTHD SPLITTHRESH SPLITRELDIFF SPLITACTION"
pst_config["pargp_fieldnames"] = pst_config["pargp_fieldnames"].lower().strip().split()

pst_config["pargp_format"] = {"pargpnme":SFMT,"inctyp":SFMT,"derinc":FFMT,"forcen":SFMT,
                      "derincmul":FFMT,"dermthd":SFMT,"splitthresh":FFMT,
                      "splitreldiff":FFMT,"splitaction":SFMT}

pst_config["pargp_converters"] = {"pargpnme":str_con,"inctyp":str_con,
                         "dermethd":str_con,"derinc":np.float,"derinclb":np.float,
                         "splitaction":str_con,"forcen":str_con,"derincmul":np.float}
pst_config["pargp_defaults"] = {"pargpnme":"pargp","inctyp":"relative","derinc":0.01,
                       "derinclb":0.0,"forcen":"switch","derincmul":2.0,
                     "dermthd":"parabolic","splitthresh":1.0e-5,
                       "splitreldiff":0.5,"splitaction":"smaller"}


# observation stuff
pst_config["obs_fieldnames"] = "OBSNME OBSVAL WEIGHT OBGNME".lower().split()
pst_config["obs_dtype"] = np.dtype([("obsnme","U20"),("obsval",np.float64),
                           ("weight",np.float64),("obgnme","U20")])
pst_config["obs_format"] = {"obsnme": SFMT, "obsval": FFMT,
                   "weight": FFMT, "obgnme": SFMT}
pst_config["obs_converters"] = {"obsnme": str_con, "obgnme": str_con,
                                "weight":np.float,"obsval":np.float}
pst_config["obs_defaults"] = {"obsnme":"dum","obsval":1.0e+10,
                     "weight":1.0,"obgnme":"obgnme"}


# prior info stuff
pst_config["null_prior"] = pd.DataFrame({"pilbl": None,
                                    "obgnme": None}, index=[])
pst_config["prior_format"] = {"pilbl": SFMT, "equation": SFMT_LONG,
                     "weight": FFMT, "obgnme": SFMT}
pst_config["prior_fieldnames"] = ["pilbl","equation", "weight", "obgnme"]


# other containers
pst_config["model_command"] = []
pst_config["template_files"] = []
pst_config["input_files"] = []
pst_config["instruction_files"] = []
pst_config["output_files"] = []
pst_config["other_lines"] = []
pst_config["tied_lines"] = []
pst_config["regul_lines"] = []
pst_config["pestpp_options"] = {}


def read_resfile(resfile):
    """load a PEST-style residual file into a pandas.DataFrame

   Args:
        resfile (`str`): path and name of an existing residual file

    Returns:
        `pandas.DataFrame`: a dataframe of info from the residuals file.
        Column names are the names from the residuals file: "name", "group",
        "measured", "modelled" (with two "L"s), "residual", "weight".

    Example::

        df = pyemu.pst_utils.read_resfile("my.res")
        df.residual.plot(kind="hist")

    """
    assert os.path.exists(resfile),"read_resfile() error: resfile " +\
                                   "{0} not found".format(resfile)
    converters = {"name": str_con, "group": str_con}
    f = open(resfile, 'r')
    while True:
        line = f.readline()
        if line == '':
            raise Exception("Pst.get_residuals: EOF before finding "+
                            "header in resfile: " + resfile)
        if "name" in line.lower():
            header = line.lower().strip().split()
            break
    res_df = pd.read_csv(f, header=None, names=header, sep="\s+",
                             converters=converters)
    res_df.index = res_df.name
    f.close()
    return res_df

def res_from_en(pst,enfile):
    """load ensemble results from PESTPP-IES into a PEST-style
    residuals `pandas.DataFrame`

    Args:
        enfile (`str`): CSV-format ensemble file name

    Returns:
        `pandas.DataFrame`: a dataframe with the same columns as a
        residual dataframe (a la `pst_utils.read_resfile()`)

    Note:
        If a "base" realization is found in the ensemble, it is used
        as the "modelled" column in the residuals dataframe.  Otherwise,
        the mean of the ensemble is used as "modelled"

    Example::

        df = pyemu.pst_utils.res_from_en("my.0.obs.csv")
        df.residual.plot(kind="hist")

    """
    converters = {"name": str_con, "group": str_con}
    obs=pst.observation_data
    if isinstance(enfile,str):
        df=pd.read_csv(enfile,converters=converters)
        df.columns=df.columns.str.lower()
        df = df.set_index('real_name').T.rename_axis('name').rename_axis(None, 1)
    else:
        df = enfile.T
    if 'base' in df.columns:
        modelled = df['base']
        std = df.std(axis=1)
    else:
        modelled = df.mean(axis=1)
        std = df.std(axis=1)
    #probably a more pandastic way to do this
    res_df = pd.DataFrame({"modelled":modelled,"std":std},index=obs.obsnme.values)
    res_df['group']=obs['obgnme'].copy()
    res_df['measured']=obs['obsval'].copy()
    res_df['weight']=obs['weight'].copy()
    res_df['residual']=res_df['measured']-res_df['modelled']
    return res_df

def read_parfile(parfile):
    """load a PEST-style parameter value file into a pandas.DataFrame

    Args:
        parfile (`str`): path and name of existing parameter file

    Returns:
        `pandas.DataFrame`: a dataframe with columns of "parnme", "parval1",
        "scale" and "offset"

    Example::

        df = pyemu.pst_utils.read_parfile("my.par1")

    """
    if not os.path.exists(parfile):
        raise Exception("pst_utils.read_parfile: parfile not found: {0}".\
                        format(parfile))
    f = open(parfile, 'r')
    header = f.readline()
    par_df = pd.read_csv(f, header=None,
                             names=["parnme", "parval1", "scale", "offset"],
                             sep="\s+")
    par_df.index = par_df.parnme
    return par_df

def write_parfile(df,parfile):
    """ write a PEST-style parameter file from a dataframe

    Args:
        df (`pandas.DataFrame`): a dataframe with column names
            that correspond to the entries in the parameter data
            section of the pest control file
        parfile (`str`): name of the parameter file to write

    Example::

        pyemu.pst_utils.write_parfile(pst.parameter_data,"my.par")

    """
    columns = ["parnme","parval1","scale","offset"]
    formatters = {"parnme":lambda x:"{0:20s}".format(x),
                  "parval1":lambda x:"{0:20.7E}".format(x),
                  "scale":lambda x:"{0:20.7E}".format(x),
                  "offset":lambda x:"{0:20.7E}".format(x)}

    for col in columns:
        assert col in df.columns,"write_parfile() error: " +\
                                 "{0} not found in df".format(col)
    with open(parfile,'w') as f:
        f.write("single point\n")
        f.write(df.to_string(col_space=0,
                      columns=columns,
                      formatters=formatters,
                      justify="right",
                      header=False,
                      index=False,
                      index_names=False) + '\n')


def parse_tpl_file(tpl_file):
    """ parse a PEST-style template file to get the parameter names

    Args:
    tpl_file (`str`): path and name of a template file

    Returns:
        [`str`] : list of parameter names found in `tpl_file`

    Example::

        par_names = pyemu.pst_utils.parse_tpl_file("my.tpl")

    """
    par_names = set()
    with open(tpl_file,'r') as f:
        try:
            header = f.readline().strip().split()
            assert header[0].lower() in ["ptf","jtf"],\
                "template file error: must start with [ptf,jtf], not:" +\
                str(header[0])
            assert len(header) == 2,\
                "template file error: header line must have two entries: " +\
                str(header)

            marker = header[1]
            assert len(marker) == 1,\
                "template file error: marker must be a single character, not:" +\
                str(marker)
            for line in f:
                par_line = set(line.lower().strip().split(marker)[1::2])
                par_names.update(par_line)
                #par_names.extend(par_line)
                #for p in par_line:
                #    if p not in par_names:
                #        par_names.append(p)
        except Exception as e:
            raise Exception("error processing template file " +\
                            tpl_file+" :\n" + str(e))
    #par_names = [pn.strip().lower() for pn in par_names]
    #seen = set()
    #seen_add = seen.add
    #return [x for x in par_names if not (x in seen or seen_add(x))]
    return [p.strip() for p in list(par_names)]


def write_input_files(pst,pst_path='.'):
    """write parameter values to model input files

    Args:
        pst (`pyemu.Pst`): a Pst instance
        pst_path (`str`): the path to where the control file and template
            files reside.  Default is '.'.

    Note:

        This function uses template files with the current parameter \
        values (stored in `pst.parameter_data.parval1`).

        This function uses multiprocessing - one process per template file

        This is a simple implementation of what PEST does.  It does not
        handle all the special cases, just a basic function...user beware

    """
    par = pst.parameter_data
    par.loc[:, "parval1_trans"] = (par.parval1 * par.scale) + par.offset
    pairs = np.array(list(zip(pst.template_files, pst.input_files)))
    num_tpl = len(pairs)
    chunk_len = 50
    num_chunk_floor = num_tpl // chunk_len
    main_chunks = pairs[:num_chunk_floor * chunk_len].reshape(
        [-1, chunk_len, 2]).tolist()  # the list of files broken down into chunks
    remainder = pairs[num_chunk_floor * chunk_len:].tolist()  # remaining files
    chunks = main_chunks + [remainder]
    procs = []
    for chunk in chunks:
        #write_to_template(pst.parameter_data.parval1_trans,os.path.join(pst_path,tpl_file),
        #                  os.path.join(pst_path,in_file))
        p = mp.Process(target=_write_chunk_to_template,
                       args=[chunk, pst.parameter_data.parval1_trans,
                             pst_path])
        p.start()
        procs.append(p)
    for p in procs:
        p.join()


def _write_chunk_to_template(chunk, parvals, pst_path):
    for tpl_file, in_file in chunk:
        tpl_file = os.path.join(pst_path, tpl_file)
        in_file = os.path.join(pst_path, in_file)
        write_to_template(parvals, tpl_file, in_file)


def write_to_template(parvals,tpl_file,in_file):
    """ write parameter values to a model input file using
    the corresponding template file

    Args:
        parvals (`dict`): a container of parameter names and values.  Can
            also be a `pandas.Series`
        tpl_file (`str`): path and name of a template file
        in_file (`str`): path and name of model input file to write

    Examples::

        pyemu.pst_utils.write_to_template(par.parameter_data.parval1,
                                          "my.tpl","my.input")

    """
    f_in = open(in_file,'w')
    f_tpl = open(tpl_file,'r')
    header = f_tpl.readline().strip().split()
    if header[0].lower() not in ["ptf", "jtf"]:
        raise Exception("template file error: must start with [ptf,jtf], not:" + \
        str(header[0]))
    if len(header) != 2:
        raise Exception("template file error: header line must have two entries: " + \
        str(header))

    marker = header[1]
    if len(marker) != 1:
        raise Exception("template file error: marker must be a single character, not:" + \
        str(marker))
    for line in f_tpl:
        if marker not in line:
            f_in.write(line)
        else:
            line = line.rstrip()
            par_names = line.lower().split(marker)[1::2]
            par_names = [name.strip() for name in par_names]
            start,end = _get_marker_indices(marker, line)
            if len(par_names) != len(start):
                raise Exception("par_names != start")
            new_line = line[:start[0]]
            between = [line[e:s] for s,e in zip(start[1:],end[:-1])]
            for i,name in enumerate(par_names):
                s,e = start[i],end[i]
                w = e - s
                if w > 15:
                    d = 6
                else:
                    d = 3
                fmt = "{0:" + str(w)+"."+str(d)+"E}"
                val_str = fmt.format(parvals[name])
                new_line += val_str
                if i != len(par_names) - 1:
                    new_line += between[i]
            new_line += line[end[-1]:]
            f_in.write(new_line+'\n')
    f_tpl.close()
    f_in.close()


def _get_marker_indices(marker, line):
    """ method to find the start and end parameter markers
    on a template file line.  Used by write_to_template()

    """
    indices = [i for i, ltr in enumerate(line) if ltr == marker]
    start = indices[0:-1:2]
    end = [i+1 for i in indices[1::2]]
    assert len(start) == len(end)
    return start,end


def parse_ins_file(ins_file):
    """parse a PEST-style instruction file to get observation names

    Args:
        ins_file (`str`): path and name of an existing instruction file

    Returns:
        [`str`]: a list of observation names found in `ins_file`

    Note:
        This is a basic function for parsing instruction files to
        look for observation names.

    Example::

        obs_names = pyemu.pst_utils.parse_ins_file("my.ins")

    """

    obs_names = []
    with open(ins_file,'r') as f:
        header = f.readline().strip().split()
        assert header[0].lower() in ["pif","jif"],\
            "instruction file error: must start with [pif,jif], not:" +\
            str(header[0])
        marker = header[1]
        assert len(marker) == 1,\
            "instruction file error: marker must be a single character, not:" +\
            str(marker)
        for line in f:
            line = line.lower()
            if marker in line:
                raw = line.lower().strip().split(marker)
                for item in raw[::2]:
                    obs_names.extend(_parse_ins_string(item))
            else:
                obs_names.extend(_parse_ins_string(line.strip()))
    #obs_names = [on.strip().lower() for on in obs_names]
    return obs_names


def _parse_ins_string(string):
    """ split up an instruction file line to get the observation names
    """
    istart_markers = ["[","(","!"]
    iend_markers = ["]",")","!"]

    obs_names = []

    idx = 0
    while True:
        if idx >= len(string) - 1:
            break
        char = string[idx]
        if char in istart_markers:
            em = iend_markers[istart_markers.index(char)]
            # print("\n",idx)
            # print(string)
            # print(string[idx+1:])
            # print(string[idx+1:].index(em))
            # print(string[idx+1:].index(em)+idx+1)
            eidx = min(len(string),string[idx+1:].index(em)+idx+1)
            obs_name = string[idx+1:eidx]
            if obs_name.lower() != "dum":
                obs_names.append(obs_name)
            idx = eidx + 1
        else:
            idx += 1
    return obs_names


def _populate_dataframe(index, columns, default_dict, dtype):
    """ helper function to populate a generic Pst dataframe attribute.

    Note:
        This function is called as part of constructing a generic Pst instance

    """
    new_df = pd.DataFrame(index=index,columns=columns)
    for fieldname,dt in zip(columns,dtype.descr):
        default = default_dict[fieldname]
        new_df.loc[:,fieldname] = default
        new_df.loc[:,fieldname] = new_df.loc[:,fieldname].astype(dt[1])
    return new_df


def generic_pst(par_names=["par1"],obs_names=["obs1"],addreg=False):
    """generate a generic pst instance.

    Args:
        par_names ([`str`], optional): parameter names to include in the new
            `pyemu.Pst`.  Default is ["par2"].
        obs_names ([`str`], optional): observation names to include in the new
            `pyemu.Pst`.  Default is ["obs1"].
        addreg (`bool`): flag to add zero-order Tikhonov prior information
            equations to the new control file

    Returns:
        `pyemu.Pst`: a new control file instance. This instance does not have
        all the info needed to run, but is a placeholder that can then be
        filled in later.

    Example::

        par_names = ["par1","par2"]
        obs_names = ["obs1","obs2"]
        pst = pyemu.pst_utils.generic_pst(par_names,obs_names]

    """
    if not isinstance(par_names,list):
        par_names = list(par_names)
    if not isinstance(obs_names,list):
        obs_names = list(obs_names)
    new_pst = pyemu.Pst("pest.pst",load=False)
    pargp_data = _populate_dataframe(["pargp"], new_pst.pargp_fieldnames,
                                     new_pst.pargp_defaults, new_pst.pargp_dtype)
    new_pst.parameter_groups = pargp_data

    par_data = _populate_dataframe(par_names, new_pst.par_fieldnames,
                                   new_pst.par_defaults, new_pst.par_dtype)
    par_data.loc[:,"parnme"] = par_names
    par_data.index = par_names
    par_data.sort_index(inplace=True)
    new_pst.parameter_data = par_data
    obs_data = _populate_dataframe(obs_names, new_pst.obs_fieldnames,
                                   new_pst.obs_defaults, new_pst.obs_dtype)
    obs_data.loc[:,"obsnme"] = obs_names
    obs_data.index = obs_names
    obs_data.sort_index(inplace=True)
    new_pst.observation_data = obs_data

    new_pst.template_files = ["file.tpl"]
    new_pst.input_files = ["file.in"]
    new_pst.instruction_files = ["file.ins"]
    new_pst.output_files = ["file.out"]
    new_pst.model_command = ["model.bat"]

    new_pst.prior_information = new_pst.null_prior

    #new_pst.other_lines = ["* singular value decomposition\n","1\n",
    #                       "{0:d} {1:15.6E}\n".format(new_pst.npar_adj,1.0E-6),
    #                       "1 1 1\n"]
    if addreg:
        new_pst.zero_order_tikhonov()

    return new_pst


def try_process_output_file(ins_file,output_file=None):
    """attempt to process a model output file using a PEST-style instruction file

    Args:
        ins_file (`str`): path and name of an instruction file
        output_file (`str`,optional): path and name of existing model
            output file to process.  If `None`, `ins_file.replace(".ins","")`
            is used.  Default is None.

    Returns:
        `pandas.DataFrame`: a dataframe of observation name and simulated outputs
        extracted from `output_file`.

    Note:
        If an exception is raised when processing the output file, the exception
        is echoed to the screen and `None` is returned.

    Example::

        df = pyemu.pst_utils.try_process_output_file("my.ins","my.output")

    """
    if output_file is None:
        output_file = ins_file.replace(".ins","")
    df = None
    try:
        i = InstructionFile(ins_file)
        df = i.read_output_file(output_file)
    except Exception as e:
        print("error processing instruction/output file pair: {0}".format(str(e)))
    return df


def try_process_output_pst(pst):
    """ attempt to process each instruction file, model output
    file pair in a `pyemu.Pst`.

    Args:
        pst (`pyemu.Pst`): a control file instance

    Returns:
        `pandas.DataFrame`: a dataframe of observation names and simulated outputs
        extracted from model output files.

    Note:
        This function first tries to process the output files using the
        InstructionFile class,  If that failes, then it tries to run
        INSCHEK. If an instructionfile is processed successfully,
        the extract simulated values are used to populate the
        `pst.observation_data.obsval` attribute.


    """
    for ins_file,out_file in zip(pst.instruction_files,pst.output_files):
        df = None
        try:
            i = InstructionFile(ins_file,pst=pst)
            df = i.read_output_file(out_file)
        except Exception as e:
            warnings.warn("error processing instruction file {0}, trying inschek: {1}".format(ins_file,str(e)))
            df = _try_run_inschek(ins_file,out_file)
        if df is not None:
            pst.observation_data.loc[df.index, "obsval"] = df.obsval


def _try_run_inschek(ins_file,out_file,cwd='.'):
    """try to run inschek and load the resulting obf file
    """
    try:
        pyemu.os_utils.run("inschek {0} {1}".format(ins_file, out_file),cwd=cwd)
        obf_file = os.path.join(cwd,ins_file.replace(".ins", ".obf"))
        df = pd.read_csv(obf_file, delim_whitespace=True,
                         skiprows=0, index_col=0, names=["obsval"])
        df.index = df.index.map(str.lower)
        return df
    except Exception as e:
        print("error using inschek for instruction file {0}:{1}".
              format(ins_file, str(e)))
        print("observations in this instruction file will have" +
              "generic values.")
        return None


def get_phi_comps_from_recfile(recfile):
    """read the phi components from a record file by iteration

    Args:
        recfile (`str`): pest record file name

    Returns:
        `dict`:  nested dictionary of iteration number, {group,contribution}

    Note:
        It is really poor form to use the record file in this way.  Please only
        use this as a last resort!

    """
    iiter = 1
    iters = {}
    f = open(recfile,'r')
    while True:
        line = f.readline()
        if line == '':
            break
        if "starting phi for this iteration" in line.lower() or \
            "final phi" in line.lower():
            contributions = {}
            while True:
                line = f.readline()
                if line == '':
                    break
                if "contribution to phi" not in line.lower():
                    iters[iiter] = contributions
                    iiter += 1
                    break
                raw = line.strip().split()
                val = float(raw[-1])
                group = raw[-3].lower().replace('\"', '')
                contributions[group] = val
    return iters


def res_from_obseravtion_data(observation_data):
    """create a PEST-style residual dataframe filled with np.NaN for
    missing information

    Args:
        observation_data (`pandas.DataFrame`): the "* observation data"
            `pandas.DataFrame` from `pyemu.Pst.observation_data`

    Returns:
        `pandas.DataFrame`: a dataframe with the same columns as the
        residual dataframe ("name","group","measured","modelled",
        "residual","weight").



    """
    res_df = observation_data.copy()
    res_df.loc[:, "name"] = res_df.pop("obsnme")
    res_df.loc[:, "measured"] = res_df.pop("obsval")
    res_df.loc[:, "group"] = res_df.pop("obgnme")
    res_df.loc[:, "modelled"] = np.NaN
    res_df.loc[:, "residual"] = np.NaN
    return res_df

def clean_missing_exponent(pst_filename,clean_filename="clean.pst"):
    """fixes the issue where some terrible fortran program may have
    written a floating point format without the 'e' - like 1.0-3, really?!

    Args:
        pst_filename (`str`): the pest control file
        clean_filename (`str`, optional):  the new pest control file to write.
            Default is "clean.pst"

    """
    lines = []
    with open(pst_filename,'r') as f:
        for line in f:
            line = line.lower().strip()
            if '+' in line:
                raw = line.split('+')
                for i,r in enumerate(raw[:-1]):
                    if r[-1] != 'e':
                        r = r + 'e'
                    raw[i] = r
                lines.append('+'.join(raw))
            else:
                lines.append(line)
    with open(clean_filename,'w') as f:
        for line in lines:
            f.write(line+'\n')

def csv_to_ins_file(csv_filename,ins_filename=None,only_cols=None,only_rows=None,
                    marker='~',includes_header=True,includes_index=True,prefix=''):
    """write a PEST-style instruction file from an existing CSV file

    Args:
        csv_filename (`str`): path and name of existing CSV file
        ins_filename (`str`, optional): path and name of the instruction
            file to create.  If `None`, then `csv_filename`+".ins" is used.
            Default is `None`.
        only_cols ([`str`]): list of columns to add observations for in the
            resulting instruction file. If `None`, all columns are used.
        only_rows ([`str`]): list of rows to add observations for in the
            resulting instruction file. If `None`, all rows are used.
        marker (`str`): the PEST instruction marker to use.  Default is "~"
        includes_header (`bool`): flag to indicate `csv_filename` includes a
            header row as the first row.  Default is True.
        includes_index (`bool`): lag to indicate `csv_filename` includes a
            index column as the first column.  Default is True.
        prefix (`str`, optional): a prefix to prepend to observation names.
            Default is ""

    Returns:
        `pandas.DataFrame`: a dataframe of observation names and values found in
        `csv_filename`

    Note:
        resulting observation names in `ins_filename` are a combiation of index and
        header values.


    """
    # process the csv_filename in case it is a dataframe
    if isinstance(csv_filename,str):
        df = pd.read_csv(csv_filename,index_col=0)
        df.columns = df.columns.map(str.lower)
        df.index = df.index.map(lambda x: str(x).lower())
    else:
        df = csv_filename

    # process only_cols
    if only_cols is None:
        only_cols = set(df.columns.map(str.lower))
    else:
        if isinstance(only_cols,str): # incase it is a single name
            only_cols = [only_cols]
        only_cols = set(only_cols)

    if only_rows is None:
        only_rows = set(df.index.map(str.lower))
    else:
        if isinstance(only_rows,str): # incase it is a single name
            only_rows = [only_rows]
        only_rows = set(only_rows)

    # process the row labels, handling duplicates
    rlabels = []
    row_visit = {}
    only_rlabels = []
    for rname in df.index:
        rname = str(rname).strip().lower()

        if rname in row_visit:
            rsuffix = str(int(row_visit[rname] + 1))
            row_visit[rname] += 1
        else:
            row_visit[rname] = 1
            rsuffix = ''
        rlabel = rname + rsuffix
        rlabels.append(rlabel)
        if rname in only_rows:
            only_rlabels.append(rlabel)
    only_rlabels = set(only_rlabels)

    #process the col labels, handling duplicates
    clabels = []
    col_visit = {}
    only_clabels = []
    for cname in df.columns:
        cname = str(cname).strip().lower()
        if cname in col_visit:
            csuffix = str(int(col_visit[cname]+1))
            col_visit[cname] += 1
        else:
            col_visit[cname] = 1
            csuffix = ''
        clabel = cname + csuffix
        clabels.append(clabel)
        if cname in only_cols:
            only_clabels.append(clabel)

    if ins_filename is None:
        if not isinstance(csv_filename,str):
            raise Exception("ins_filename is None but csv_filename is not string")
        ins_filename = csv_filename + ".ins"
    row_visit, col_visit = {},{}
    onames = []
    ovals = []
    with open(ins_filename,'w') as f:
        f.write("pif ~\nl1\n")
        for i,rlabel in enumerate(rlabels):
            if includes_header:
                f.write("l1 ") #skip the row (index) label
            for j,clabel in enumerate(clabels):
                if rlabel in only_rlabels and clabel in only_clabels:
                    oname = prefix+rlabel+"_"+clabel
                    onames.append(oname)
                    ovals.append(df.iloc[i,j])
                else:
                    oname = "dum"
                if j == 0:
                    if includes_index:
                        f.write(" {0},{0} ".format(marker))
                else:
                    f.write(" {0},{0} ".format(marker))
                f.write(" !{0}! ".format(oname))
            f.write('\n')
    odf = pd.DataFrame({"obsnme":onames,"obsval":ovals},index=onames)
    return odf




class InstructionFile(object):
    """class for handling instruction files.

    Args:
        ins_filename (`str`): path and name of an existing instruction file
        pst (`pyemu.Pst`, optional): Pst instance - used for checking that instruction file is
            compatible with the control file (e.g. no duplicates)

    Example::

        i = InstructionFile("my.ins")
        df = i.read_output_file("my.output")

    """
    def __init__(self,ins_filename,pst=None):
        self._ins_linecount = 0
        self._out_linecount = 0
        self._ins_filename = ins_filename
        #self._pst = pst
        self._marker = None
        self._ins_filehandle = None
        self._out_filehandle = None
        self._last_line = ''
        self._full_oname_set = None
        if pst is not None:
            self._full_oname_set = set(pst.obs_names)
        self._found_oname_set = set()

        self._instruction_lines = []
        self._instruction_lcount = []

        self.read_ins_file()

    def read_ins_file(self):
        """read the instruction and do some minimal error checking.

        Note:

            This is called by the constructor

        """
        self._instruction_lines = []
        self._instruction_lcount = []
        first_line = self._readline_ins()
        if len(first_line) < 2:
            raise Exception("first line of ins file must have atleast two entries, not '{0}'".format(','.join(first_line)))
        if first_line[0] != "pif":
            raise Exception("first line of ins file '{0}' must start with 'pif', not '{1}'". \
                            format(self._ins_filename, first_line[0]))
        self._marker = first_line[1]
        while True:
            line = self._readline_ins()

            if line is None:
                break
            elif len(line) == 0:
                self.throw_ins_warning("empty line, breaking")
                break
            elif line[0].startswith('l'):
                pass
            elif line[0].startswith(self._marker):
                pass
            elif line[0].startswith('&'):
                self.throw_ins_error("line continuation not supported")
            else:
                self.throw_ins_error("first token must be line advance ('l'), primary marker, or continuation ('&'),"+
                                     "not: {0}".format(line[0]))

            for token in line[1:]:
                if token.startswith("t"):
                    self.throw_ins_error("tab instruction not supported")
                elif token.startswith(self._marker):
                    if not token.endswith(self._marker):
                        self.throw_ins_error("unbalanced secondary marker in token '{0}'".format(token))


                for somarker,eomarker in zip(['!','[','('],['!',']',')']):
                    #
                    if token[0] == somarker:
                        ofound = True
                        if eomarker not in token[1:]:
                            self.throw_ins_error("unmatched observation marker '{0}', looking for '{1}' in token '{2}'".\
                                                 format(somarker,eomarker,token))
                        raw = token[1:].split(eomarker)[0].replace(somarker,'')
                        if raw == 'dum':
                            pass
                        else:
                            if self._full_oname_set is not None and raw not in self._full_oname_set:
                                self.throw_ins_error("obs name '{0}' not in pst".format(raw))
                            elif raw in self._found_oname_set:
                                self.throw_ins_error("obs name '{0}' is listed more than once".format(raw))
                            self._found_oname_set.add(raw)
                        break
                        #print(raw)

            self._instruction_lines.append(line)
            self._instruction_lcount.append(self._ins_linecount)


    def throw_ins_warning(self,message,lcount=None):
        """throw a verbose PyemuWarning

        Args:
            message (`str`): the warning message
            lcount (`int`, optional): warning line number.  If None, self._ins_linecount is used

        """
        if lcount is None:
            lcount = self._ins_linecount
        warnings.warn("InstructionFile error processing instruction file {0} on line number {1}: {2}".\
                        format(self._ins_filename,lcount,message),PyemuWarning)

    def throw_ins_error(self,message,lcount=None):
        """throw a verbose instruction file error

        Args:
            message (`str`): the error message
            lcount (`int`, optional): error line number.  If None, self._ins_linecount is used
        """
        if lcount is None:
            lcount = self._ins_linecount
        raise Exception("InstructionFile error processing instruction file on line number {0}: {1}".\
                        format(lcount,message))

    def throw_out_error(self,message,lcount=None):
        """throw a verbose output file error

        Args:
            message (`str`): the error message
            lcount (`int`, optional): error line number.  If None, self._ins_linecount is used

        """
        if lcount is None:
            lcount = self._out_linecount
        raise Exception("InstructionFile error processing output file on line number {0}: {1}".\
                        format(lcount,message))

    def read_output_file(self,output_file):
        """process a model output file using  `InstructionFile.instruction_set`

        Args:
            output_file (`str`): path and name of existing output file

        Returns:

            `pd.DataFrame`: a dataframe with observation names and simulated values
            extracted from `output_file`


        """
        self._out_filename = output_file
        val_dict = {}
        for ins_line,ins_lcount in zip(self._instruction_lines,self._instruction_lcount):
            #try:
            val_dict.update(self._execute_ins_line(ins_line,ins_lcount))
            #except Exception as e:
            #    raise Exception(str(e))
        s = pd.Series(val_dict)
        s.sort_index(inplace=True)

        return pd.DataFrame({"obsval":s},index=s.index)

    def _execute_ins_line(self,ins_line,ins_lcount):
        """private method to process output file lines with an instruction line

        """
        cursor_pos = 0
        val_dict = {}
        for ii,ins in enumerate(ins_line):

            #primary marker
            if ii == 0 and ins.startswith(self._marker):
                mstr = ins.replace(self._marker,'')
                while True:
                    line = self._readline_output()
                    if line is None:
                        self.throw_out_error(
                            "EOF when trying to find primary marker '{0}' from instruction file line {1}".format(mstr,ins_lcount))
                    if mstr in line:
                        break
                cursor_pos = line.index(mstr) + len(mstr)

            # line advance
            elif ins.startswith('l'):
                try:
                    nlines = int(ins[1:])
                except Exception as e:
                    self.throw_ins_error("casting line advance to int for instruction '{0}'". \
                                         format(ins), ins_lcount)
                for i in range(nlines):
                    line = self._readline_output()
                    if line is None:
                        self.throw_out_error("EOF when trying to read {0} lines for line advance instruction '{1}', from instruction file line number {2}". \
                                             format(nlines, ins, ins_lcount))
            elif ins == 'w':
                raw = line[cursor_pos:].split()
                if line[cursor_pos] == ' ':
                    raw.insert(0,'')
                if len(raw) == 1:
                    self.throw_out_error("no whitespaces found on output line {0} past {1}".format(line,cursor_pos))
                cursor_pos = cursor_pos + line[cursor_pos:].index(" "+raw[1]) + 1


            elif ins.startswith('!'):
                oname = ins.replace('!','')
                # look a head for a sec marker
                if ii < len(ins_line) - 1 and ins_line[ii+1].startswith(self._marker):
                    m = ins_line[ii+1].replace(self._marker,'')
                    if m not in line[cursor_pos:]:
                        self.throw_out_error("secondary marker '{0}' not found from cursor_pos {2}".format(m,cursor_pos))
                    val_str = line[cursor_pos:].split(m)[0]
                else:
                    val_str = line[cursor_pos:].split()[0]
                try:
                    val = float(val_str)
                except Exception as e:
                    self.throw_out_error("casting string '{0}' to float for instruction '{1}'".format(val_str,ins))

                if oname != "dum":
                    val_dict[oname] = val
                #ipos = line[cursor_pos:].index(val_str)
                #val_len = len(val_str)
                cursor_pos = cursor_pos + line[cursor_pos:].index(val_str) + len(val_str)

                #print(val,cursor_pos)

                #print(line[cursor_pos:])
                #print('')

            elif ins.startswith(self._marker):
                m = ins.replace(self._marker,'')
                if m not in line[cursor_pos:]:
                    self.throw_out_error("secondary marker '{0}' not found from cursor_pos {2}".format(m,cursor_pos))
                cursor_pos = cursor_pos + line[cursor_pos:].index(m) + len(m)

            else:
                self.throw_out_error("unrecognized instruction '{0}' on ins file line {1}".format(ins,ins_lcount))

        return val_dict

    def _readline_ins(self):
        """consolidate private method to read the next instruction file line.  Casts to lower and splits
        on whitespace
        """
        if self._ins_filehandle is None:
            if not os.path.exists(self._ins_filename):
                raise Exception("instruction file '{0}' not found".format(self._ins_filename))
            self._ins_filehandle = open(self._ins_filename,'r')
        line = self._ins_filehandle.readline()
        self._ins_linecount += 1
        if line == '':
            return None
        self._last_line = line
        return line.lower().strip().split()


    def _readline_output(self):
        """consolidate private method to read the next output file line.  Casts to lower

        """
        if self._out_filehandle is None:
            if not os.path.exists(self._out_filename):
                raise Exception("output file '{0}' not found".format(self._out_filename))
            self._out_filehandle = open(self._out_filename,'r')
        line = self._out_filehandle.readline()
        self._out_linecount += 1
        if line == '':
            return None
        self._last_line = line
        return line.lower()





def process_output_files(pst,pst_path='.'):
    """helper function to process output files using the
     InstructionFile class

   Args:
        pst (`pyemu.Pst`): control file instance

        pst_path (`str`): path to instruction and output files to append to the front
            of the names in the Pst instance

    Returns:
        `pd.DataFrame`: dataframe of observation names and simulated values
        extracted from the model output files listed in `pst`

    Example::

        pst = pyemu.Pst("my.pst")
        df = pyemu.pst_utils.process_output_files(pst)


    """
    if not isinstance(pst,pyemu.Pst):
        raise Exception("process_output_files error: 'pst' arg must be pyemu.Pst instance")
    series = []
    for ins,out in zip(pst.instruction_files,pst.output_files):
        ins = os.path.join(pst_path,ins)
        out = os.path.join(pst_path,out)
        if not os.path.exists(out):
            warnings.warn("out file '{0}' not found".format(out),PyemuWarning)
        f = os.path.join(pst_path,ins)
        i = InstructionFile(ins,pst=pst)
        try:
            s = i.read_output_file(out)
            series.append(s)
        except Exception as e:
            warnings.warn("error processing output file '{0}': {1}".format(out,str(e)))
    if len(series) == 0:
        return None
    series = pd.concat(series)
    #print(series)
    return series

