import subprocess
import shlex

import numpy as np
import pytest

from shiny.Procedures.HydrogenBondAnalysis import hbxpm2npy


class Test_hbxpm2npy:

    def test_try_read_missing_hbxpm_file(self):
        with pytest.raises(OSError):
            hbxpm2npy.read_hbxpm("notafile.xpm")

    def test_read_hbxpm(self, datadir, num_regression):
        content = hbxpm2npy.read_hbxpm(
            datadir / "hbm.xpm"
            )

        num_regression.check(
            {index: existence for index, existence in enumerate(content.T)}
            )

    def test_CLI_hbm(self, datadir, num_regression):
        command = (
            f"python -m shiny.Procedures.HydrogenBondAnalysis.hbxpm2npy "
            f"-hbm {datadir / 'hbm.xpm'}"
            )

        process = subprocess.run(
            shlex.split(command)
        )

        assert process.returncode == 0

        content = np.load(datadir / 'hbm.npy')

        num_regression.check(
            {index: existence for index, existence in enumerate(content.T)}
            )

    def test_CLI_hbn(self, datadir, num_regression):
        command = (
            f"python -m shiny.Procedures.HydrogenBondAnalysis.hbxpm2npy "
            f"-hbn {datadir / 'hbn.ndx'} "
            f"-d {datadir / 'groups.json'}"
            )

        process = subprocess.run(
            shlex.split(command)
        )

        assert process.returncode == 0

        content = np.load(datadir / 'hbn.npy')

        num_regression.check(
            {"names": content}
            )
