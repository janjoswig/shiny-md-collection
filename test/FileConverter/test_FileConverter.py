import subprocess
import shlex

import numpy as np
import pytest

from shiny.FileConverter import text2npy


class Test_text2npy:

    def test_try_read_missing_file(self):
        with pytest.raises(OSError):
            text2npy.read_file("notafile.dat")

    @pytest.mark.parametrize(
        "filename",
        ["typical_xvg_gromacs.xvg", "typical_xvg_gromacs_broken.xvg"]
        )
    def test_read_xvg(self, filename, datadir, num_regression):
        content = text2npy.read_file(
            datadir / filename,
            comments=['#', '@'],
            usecols=1
            )

        num_regression.check({"column": content})

    def test_CLI(self, datadir, num_regression):
        command = (
            f"python -m shiny.FileConverter.text2npy "
            f"-f {datadir / 'typical_xvg_gromacs.xvg'}"
            )

        process = subprocess.run(
            shlex.split(command)
        )

        assert process.returncode == 0

        content = np.load(datadir / 'typical_xvg_gromacs.npy')

        num_regression.check(
            {"column": content}
            )
