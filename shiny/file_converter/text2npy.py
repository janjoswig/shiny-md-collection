"""Extract data from text-file into numpy-file

Reads a plain text file (e.g. .xvg for typical GROMACS output)
and writes the content to a binary numpy file (.npy).
The data is attempted to be extracted with ``:meth:numpy.loadtxt``
by default before we resort to manual parsing.
"""

import argparse
import pathlib

import numpy as np


DEFAULTS = {
    "dtype": "float",
    "comments": ['#', '@', '&', '%'],
    "usecols": [1],
}


def read_file(f, *, v=False, **kwargs):

    read_with = None

    try:
        # Read the file using numpy
        file_content = np.loadtxt(
            f,
            **kwargs
            )

        read_with = "numpy"

    except IndexError:
        # Fallback to read the file line by line if numpy read
        # fails (e.g. IndexError if file has different column
        # lengths)

        comments = tuple(kwargs.get("comments", DEFAULTS["comments"]))
        usecols = np.array(
            kwargs.get("usecols", DEFAULTS["usecols"]),
            ndmin=1,
            dtype=int
            )
        min_cols_per_line = np.max(usecols) + 1
        dtype = kwargs.get("dtype", DEFAULTS["dtype"])
        delimiter = kwargs.get("delimiter", None)

        file_content = []
        with open(f) as file_:
            for lineno, line in enumerate(file_):
                line = line.strip()

                if line.startswith(comments):
                    continue

                if line in {"", "\n", "\r"}:
                    continue

                line_content = np.asarray(line.split(delimiter), dtype=dtype)

                if len(line_content) == min_cols_per_line:
                    file_content.extend(
                        line_content[usecols]
                        )
                elif v:
                    print(
                        f"Skipping line {lineno} because "
                        f"of inconsistent column numbers."
                        )

        file_content = np.asarray(file_content, dtype=dtype)
        read_with = "custom"

    finally:
        if v:
            if read_with == "numpy":
                print(f"Read {f} using numpy.")
            elif read_with == "custom":
                print(f"Read {f} using custom parsing.")
            else:
                print(f"Failed to read {f}.")

    return file_content


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog="text2npy",
        description='Extract data from text-file into numpy-file',
        usage="%(prog)s -f input [-o output] [READING OPTIONS]",
        epilog="https://github.com/janjoswig/shiny-md-collection"
        )
    io_arguments = parser.add_argument_group('input/output arguments')
    io_arguments.add_argument(
        '-f', "--file",
        metavar="path",
        nargs='+',
        type=str,
        help=(
            "full input path and filename with extentsion (.xvg); "
            "multiple arguments possible."
            ),
        required=True
        )
    io_arguments.add_argument(
        '-o', '--output',
        metavar="path",
        nargs='+',
        type=str,
        help=(
            "full output path and filename;  if a list of input files is "
            "provided, a list of output filenames with the same number of "
            "entries should be specified;  the default (None) names the "
            "output following the input."
            ),
        default=None
        )
    reading_arguments = parser.add_argument_group('reading options')
    reading_arguments.add_argument(
        '--dtype',
        metavar="dtype",
        nargs='+',
        type=str,
        help="data-type (numpy) of the resulting array",
        default=DEFAULTS["dtype"]
        )
    reading_arguments.add_argument(
        '--comments',
        metavar="str",
        nargs='+',
        type=str,
        help="list of characters indicating comments",
        default=DEFAULTS["comments"]
        )
    reading_arguments.add_argument(
        '--delimiter',
        metavar="str",
        nargs='+',
        type=str,
        help='the string used to separate values',
        default=None
        )

    # TODO: converters flag

    reading_arguments.add_argument(
        '--skiprows',
        metavar="int",
        type=int,
        help="skip the first skiprows lines, including comments",
        default=0
        )
    reading_arguments.add_argument(
        '--usecols',
        metavar="int",
        nargs='+',
        type=int,
        help="which columns to read, with 0 being the first",
        default=DEFAULTS["usecols"]
        )
    reading_arguments.add_argument(
        '--ndmin',
        metavar="int",
        type=int,
        help="the returned array will have at least ndmin dimensions",
        default=0
        )
    reading_arguments.add_argument(
        '--encoding',
        metavar="encoding",
        type=str,
        help="encoding used to decode the inputfile",
        default='utf8'
        )
    reading_arguments.add_argument(
        '--max_rows',
        metavar="int",
        type=int,
        help="read max_rows lines of content after skiprows lines",
        default=None
        )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help="be chatty",
        default=False
        )
    args = parser.parse_args()

    if (args.output is not None) and (len(args.output) != len(args.file)):
        raise ValueError("Number of input and output files does not match")

    read_kwargs = {
        "dtype": args.dtype,
        "comments": args.comments,
        "delimiter": args.delimiter,
        "skiprows": args.skiprows,
        "usecols": args.usecols,
        "ndmin": args.ndmin,
        "encoding": args.encoding,
        "max_rows": args.max_rows
    }

    for count, fname in enumerate(args.file):
        f = pathlib.Path(fname)

        if not f.is_file():
            if args.verbose:
                print(f"File {f} does not exist.")
            continue

        file_content = read_file(f, v=args.verbose, **read_kwargs)

        if args.output is None:
            output = fname.rsplit('.', 1)[0]
        else:
            output = args.output[count]

        if args.verbose:
            print(f'Saving {output}.npy')

        np.save(output, file_content)
