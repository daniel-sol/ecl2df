import logging
import argparse
from pathlib import Path
import importlib
from inspect import signature, Parameter
from typing import List
from fmu.config.utilities import yaml_load
from ecl2df.constants import SUBMODULES

logger = logging.getLogger(__name__)


standard_options = {
    "initvectors": None,  # List[str]
    "keywords": None,  # List[str] x3
    "keyword": "VFPPROD",
    "vfpnumbers": "",
    "fipname": "FIPNUM",  # str
    "vectors": "*",  # List[str]
    "stackdates": False,  # bool x2
    "dropconstants": False,  # bool
    "arrow": False,  # bool x2
    "coords": False,  # bool
    "pillars": False,  # bool
    "region": "",  # str
    "rstdates": "",  # str
    "soilcutoff": 0.5,  # float
    "sgascutoff": 0.5,  # float
    "swatcutoff": 0.5,  # float
    "group": False,  # bool
    "wellname": None,  # str
    "date": None,  # str
    "time_index": "raw",  # str
    "column_keys": None,
    "start_date": "",  # str
    "startdate": None,
    "end_date": "",  # str
    "params": False,  # bool
    "paramfile": None,  # str
    "include_restart": False,  # bool
    "boundaryfilter": False,
    "onlyk": False,
    "onlyij": False,
    "nnc": False,
    "verbose": False,
    "zonemap": "tut",
    "use_wellconnstatus": False,
    "excl_well_startswith": None,
}


def fill_parser(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    """Set up sys.argv parsers.

    Arguments:
        parser (argparse.ArgumentParser or argparse.subparser): parser to
            fill with arguments
    """
    # parser.add_argument("DATAFILE", help="Name of Eclipse DATA file.")
    parser.add_argument("-v", "--verbose", action="store_true", help="Be verbose")
    return parser


def bulk_export(eclpath, config_path, include: List = None, options: dict = None):
    """Bulk uploads every module to sumo with metadata

    eclpath (str): path to eclipse datafile
    config_path (str): path to fmu config file
    include (List): list of submodules to include. Defaults to None which includes all
    """
    # Substituting the options passed in into standard options
    if options is not None:
        for key, value in options.items():
            if key in standard_options:
                standard_options[key] = value
    if include is None:
        include = SUBMODULES
    for submod_name in include:
        if submod_name in ["bulk"]:
            # vfp is different to all the others
            # bulk is this one
            continue
        if submod_name in include:
            func = importlib.import_module("ecl2df." + submod_name).export_w_metadata
            sig_items = signature(func).parameters.items()
            filtered_options = {
                name: standard_options[name]
                for name, param in sig_items
                if param.kind is not Parameter.empty
                and name not in {"eclpath", "config_path"}
            }
            func(eclpath, config_path, **filtered_options)
            logger.info("Export of %s data", submod_name)
            # break
        else:
            logger.warning("This is not included %s", submod_name)


def glob_for_datafiles(path="eclipse/model/"):
    """glob for data files in folder

    Args:
        path (str, optional): The folder for eclipse models.
                              Defaults to "eclipse/model/".

    Returns:
        generator: the generator made
    """
    return Path(path).glob("*.DATA")


def bulk_export_with_configfile(config_path):
    """Export eclipse results controlled by config file

    Args:
        config_path (str): path to config file
    """
    config = yaml_load(config_path)
    try:
        ecl_config = config["ecl2csv"]
        try:
            path = "eclipse/model/" + ecl_config["datafile"]
            logging.debug("Path to use for search %s", path)
            eclpaths = [path]
            includes = ecl_config.get("datatypes", None)
            logger.debug("User defined modules %s", includes)
            options = ecl_config.get("options", None)
            logger.debug("User defined options %s", options)
        except (KeyError, AttributeError, TypeError):
            eclpaths = glob_for_datafiles()
            includes = None
            options = None
        logger.info("Data files to use: %s", eclpaths)
        for eclpath in eclpaths:
            logger.info("Working with %s", eclpath)
            bulk_export(str(eclpath), config_path, includes, options)

    except KeyError:
        logger.warning("No eclipse export set up, you will not get anything exported")


def bulk_main(args):
    """Generate all datatypes

    Args:
        args (argparse.NameSpace): The input arguments
    """
    bulk_export_with_configfile(args.config_path)
