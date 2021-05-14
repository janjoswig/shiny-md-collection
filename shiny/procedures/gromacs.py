import shlex
import subprocess

from tqdm import tqdm


class Runner:

    def __init__(self, binary="gmx"):
        self.binary = binary
        self.last_process = None

    def run(
            self,
            tool,
            subprocess_kwargs=None,
            dry=False,
            **kwargs):
        options = (f"-{flag} {value}" for flag, value in kwargs.items())
        shell_command = (
            f"{self.binary} "
            f"{tool} "
            f"{' '.join(options)}"
        )

        if dry:
            tqdm.write(shell_command)
            return

        default_subprocess_kwargs = {
            "encoding": "utf-8",
            "stderr": subprocess.PIPE,
            "stdout": subprocess.PIPE,
        }

        if subprocess_kwargs is not None:
            default_subprocess_kwargs.update(subprocess_kwargs)

        self.last_process = subprocess.run(
            shlex.split(shell_command),
            **default_subprocess_kwargs
            )

    def run_from_list(self, command_list, v=True, dry=False):

        for command in tqdm(command_list):
            run_id = command.get("run_id")
            if run_id is None:
                run_id = ""

            if v:
                tqdm.write(f"Run {run_id}")
                tqdm.write("=" * 80)

            self.run(
                tool=command.get("tool"),
                subprocess_kwargs=command.get("subprocess_kwargs"),
                dry=dry,
                **command.get("options", {})
            )

            if not dry:
                if self.last_process.returncode != 0:
                    tqdm.write("failed")

                    if v:
                        tqdm.write(self.last_process.stderr)
                        tqdm.write(self.last_process.stdout)

                    break

            tqdm.write("done\n")
