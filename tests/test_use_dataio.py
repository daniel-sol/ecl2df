"""tests of function write_dframe_and_meta_to_file"""
import os
from argparse import Namespace
from pathlib import Path
from shutil import rmtree
import pandas as pd
from fmu.config.utilities import yaml_load
import ecl2df
from ecl2df.common import write_dframe_and_meta_to_file

TESTDIR = Path(__file__).absolute().parent
REEK_R_0 = TESTDIR / "data/reek/"
REEK_DATA_FILE = str(REEK_R_0 / "eclipse/model/2_R001_REEK-0.DATA")
CONFIG_PATH = REEK_R_0 / "fmuconfig/output/global_variables.yml"
CONFIG_PATH_W_PATH = REEK_R_0 / "fmuconfig/output/global_variables_w_eclpath.yml"


def _assert_string(string_to_assert, answer):
    """assert that string is equal to another string

    Args:
        string_to_assert (str): the string to check
        answer (str): the correct string
    """
    ass_string = f"{string_to_assert} should have been {answer}"
    assert string_to_assert == answer, ass_string


def _assert_metadata_are_produced_and_are_correct(
    tagname, correct_len=2, path="share/"
):
    """Assert that two files are produced, and that metadata are correct"""
    share_folder = Path(path)
    files = list(share_folder.glob("results/tables/*.*"))
    print(files)
    nr_files = len(files)
    len_str = f"Nr of files should be {correct_len}, but is {nr_files}"
    assert len(files) == correct_len, len_str
    for file_path in files:
        if file_path.name.startswith("."):
            meta = yaml_load(file_path)
            print(meta["data"])
            _assert_string(meta["data"]["name"], "2_R001_REEK")
            if tagname != "bulk":
                _assert_string(meta["data"]["tagname"], tagname)
            print(meta["data"]["spec"]["columns"])
            # _assert_string(meta["data"]["table_index"], ["DATE"])
        else:
            print(pd.read_csv(file_path).head())

    rmtree(share_folder)


def test_write_dframe_and_meta_to_file():
    """Test function write_dframe_and_meta_to_file"""
    test = pd.DataFrame({"DATE": [1, 2, 3], "FOPT": [0, 1, 2]})
    args = {
        "DATAFILE": REEK_DATA_FILE,
        "config_path": CONFIG_PATH,
        "output": "summary.csv",
        "subcommand": "summary",
    }

    write_dframe_and_meta_to_file(test, args)
    _assert_metadata_are_produced_and_are_correct("summary")


def test_write_through_summary_main(tmp_path):
    """Test summary main entry point"""
    os.chdir(tmp_path)
    ecl2df.summary.export_w_metadata(REEK_DATA_FILE, CONFIG_PATH)
    _assert_metadata_are_produced_and_are_correct("summary")


def test_write_through_satfunc_main(tmp_path):
    """Test summary main entry point"""
    os.chdir(tmp_path)
    ecl2df.satfunc.export_w_metadata(REEK_DATA_FILE, CONFIG_PATH)
    _assert_metadata_are_produced_and_are_correct("satfunc")


def test_write_through_rft_main(tmp_path):
    """Test summary main entry point"""
    os.chdir(tmp_path)
    ecl2df.rft.export_w_metadata(REEK_DATA_FILE, CONFIG_PATH)
    _assert_metadata_are_produced_and_are_correct("rft")


def test_write_through_pvt_main(tmp_path):
    """Test summary main entry point"""
    os.chdir(tmp_path)
    ecl2df.pvt.export_w_metadata(REEK_DATA_FILE, CONFIG_PATH)
    _assert_metadata_are_produced_and_are_correct("pvt")


def test_write_through_pillar_main(tmp_path):
    """Test summary main entry point"""
    os.chdir(tmp_path)
    ecl2df.pillars.export_w_metadata(REEK_DATA_FILE, CONFIG_PATH)
    _assert_metadata_are_produced_and_are_correct("pillars")


def test_write_through_nnc_main(tmp_path):
    """Test summary main entry point"""
    os.chdir(tmp_path)
    ecl2df.nnc.export_w_metadata(REEK_DATA_FILE, CONFIG_PATH)
    _assert_metadata_are_produced_and_are_correct("nnc")


def test_write_through_grid_main(tmp_path):
    """Test summary main entry point"""
    os.chdir(tmp_path)
    ecl2df.grid.export_w_metadata(REEK_DATA_FILE, CONFIG_PATH)
    _assert_metadata_are_produced_and_are_correct("grid")


def test_write_through_fipreports_main(tmp_path):
    """Test summary main entry point"""
    os.chdir(tmp_path)
    ecl2df.fipreports.export_w_metadata(REEK_DATA_FILE, CONFIG_PATH)
    _assert_metadata_are_produced_and_are_correct("fipreports")


def test_write_through_faults_main(tmp_path):
    """Test summary main entry point"""
    os.chdir(tmp_path)
    ecl2df.faults.export_w_metadata(REEK_DATA_FILE, CONFIG_PATH)
    _assert_metadata_are_produced_and_are_correct("faults")


def test_write_through_equil_main(tmp_path):
    """Test summary main entry point"""
    os.chdir(tmp_path)
    ecl2df.equil.export_w_metadata(REEK_DATA_FILE, CONFIG_PATH)
    _assert_metadata_are_produced_and_are_correct("equil")


def test_write_through_compdat_main(tmp_path):
    """Test summary main entry point"""
    os.chdir(tmp_path)
    ecl2df.compdat.export_w_metadata(REEK_DATA_FILE, CONFIG_PATH)
    _assert_metadata_are_produced_and_are_correct("compdat")


def test_bulk_upload(tmp_path):
    """Test bulk upload"""
    os.chdir(tmp_path)
    ecl2df.bulk.bulk_upload(REEK_DATA_FILE, CONFIG_PATH)
    _assert_metadata_are_produced_and_are_correct("bulk", 22)


def test_limiting_bulk_upload(tmp_path):
    """Test bulk upload with only one submodule"""
    os.chdir(tmp_path)
    ecl2df.bulk.bulk_upload(REEK_DATA_FILE, CONFIG_PATH, ["rft"])
    _assert_metadata_are_produced_and_are_correct("rft")


def test_bulk_upload_from_config():
    """Test bulk upload with config only"""
    os.chdir(REEK_R_0)
    ecl2df.bulk.bulk_upload_with_configfile(CONFIG_PATH)
    _assert_metadata_are_produced_and_are_correct("bulk", 22, path=REEK_R_0 / "share")


def test_bulk_upload_from_command_line(mocker):
    """Test bulk upload upload option from command line

    Args:
        mocker (func): mocking function for mimicing command line
    """
    os.chdir(REEK_R_0)
    mocker.patch(
        "sys.argv", ["ecl2csv", "--config_path", str(CONFIG_PATH_W_PATH), "bulk"]
    )
    ecl2df.ecl2csv.main()
    _assert_metadata_are_produced_and_are_correct("bulk", 22, path=REEK_R_0 / "share")


if __name__ == "__main__":
    test_bulk_upload_from_config()
