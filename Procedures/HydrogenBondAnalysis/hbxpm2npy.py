"""Convert GROMACS "gmx hbond" output to numpy-files

Rreads a XPixMap matrix file (.xpm) created by GROMACS
"gmx hbond -hbm" (H-bond existence vs. timeframe) and writes the
content as a matrix to a binary numpy-file (.npy).  Also reads
an index file (.ndx) created by GROMACS "gmx hbond -hbn"
(hydrogen-bond identifiers as index-tuples), translates the content
into (human readable) names according to a mapping, and writes it
to a numpy-file.
"""

import argparse
import json

import numpy as np


def read_hbxpm(f, /):
    with open(args.hbm_input) as file_:
        hb_existence = [
            line.strip(('"\n,'))
            for line in file_
            if not line.startswith("/*")
            ][4:]

    hb_existence = (x.replace(' ', '0') for x in hb_existence)
    hb_existence = [x.replace('o', '1') for x in hb_existence]

    hb_existence = np.array(
        [np.array(x, dtype='uint8') for x in hb_existence]
        ).T

    return hb_existence


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog='hbxpm2npy',
        description=(
            'Convert GROMACS "gmx hbond" output '
            '(hbm.xpm and/or hbn.ndx) to numpy-files'
            ),
        usage=(
            "%(prog)s -hbm hbm.xpm [-ohbm hbm.npy] -hbn hbn.ndx "
            "[-ohbn hbn.npy] -d mapping.npy [-sel Protein]"
            ),
        epilog="https://github.com/janjoswig/shiny-md-collection"
        )
    parser.add_argument(
        '-hbm', '--hbm_xpm',
        metavar="filename",
        type=str,
        help=(
            'full input path and filename '
            'with extension (.xpm) of GROMACS hydrogen-bond existence '
            'information'
            ),
        dest="hbm_input",
        default=None
        )
    parser.add_argument(
        '-ohbm', '--output_hbm',
        metavar="filename",
        type=str,
        help=(
            'full output path and filename with extension (.npy) '
            'for hydrogen-bond existence matrix;  if not specified, '
            'uses input file name stem for the output'
            ),
        dest="hbm_output",
        default=None
        )
    parser.add_argument(
        '-hbn', '--hbond_ndx',
        metavar="filename",
        type=str,
        help=(
            'full input path and filename '
            'with extension (.ndx) of GROMACS hydrogen-bond '
            'index-identifiers; requires mapping (-d) for the conversion'
            ),
        dest="hbn_input",
        default=None
        )
    parser.add_argument(
        '-ohbn', '--output_hbn',
        metavar="filename",
        type=str,
        help=(
            'full output path and filename with extension (.npy) '
            'for hydrogen-bond identifiers;  if not specified, '
            'uses input file name stem for the output'
            ),
        dest="hbn_output",
        default=None
        )
    parser.add_argument(
        '-d', '--dictionary',
        metavar="filename",
        help=(
            'mapping used to map hydrogen-bond index identifiers '
            'to names'
            ),
        dest="mapping",
        default=None
        )
    parser.add_argument(
        '-sel', '--selection',
        metavar="string",
        type=str,
        help=(
            'name of the group that was used for the hbond analysis '
            '(default = "Protein")'
            ),
        dest="selection",
        default='Protein'
        )
    parser.add_argument(
        '-v', '--verboose',
        action='store_true',
        help="be chatty",
        default=False
        ),

    args = parser.parse_args()

    if args.hbn_input is not None and args.mapping is None:
        parser.error(
            'Input option -hbn (--HBONS_NDX) requieres -d (--DICTIONARY)'
            )

    if args.hbm_input is not None:
        if args.hbm_output is None:
            args.hbm_output = args.hbm_input.rsplit('.', 1)[0]

        hb_existence = read_hbxpm(args.hbm_input)

        if args.verboose:
            print(f'Saving {args.hbm_output}.npy')
        np.save(args.hbm_output, hb_existence)

    if args.hbn_input is not None:
        if args.hbn_output is None:
            args.hbn_output = args.hbn_input.rsplit('.', 1)[0]

        try:
            mapping = np.load(args.d, allow_pickle=True)
        except OSError:
            if args.verboose:
                print(f"Failed to interpret file {args.d} as a pickle")

            with open(args.d) as fp:
                mapping = json.load(fp)

        mapping = {
            atom: group
            for group, atoms in mapping.items()
            for atom in atoms
            }

        with open(args.hbn_input) as file_:
            line = next(file_)
            while not line.startswith(f'[ hbonds_{args.selection} ]'):
                line = next(file_)

            names = []
            for line in file_:
                donor, hydrogen, acceptor = line.split()
                names.append(f"{mapping[donor]}-{mapping[acceptor]}")

        if args.verboose:
            print(f'Saving {args.hbn_output}.npy')
        np.save(args.hbn_output, names[::-1])
        # Saving the hb identifiers in reversed order is necessary
        # because of the order in which GROMACS gives the indices
        # (first index tuple in hbn.ndx file corresponds to the last
        # line of the hbm.xpm file or the last column of hbm.npy matrix,
        # respectively)