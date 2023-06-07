#!/usr/bin/env python3

import ujson
import typer
import fsspec
import typing
import kerchunk.hdf
from tqdm import tqdm
from pathlib import Path
from kerchunk.netCDF3 import NetCDF3ToZarr
from kerchunk.hdf import SingleHdf5ToZarr

def main(indir: Path = typer.Argument(..., help='directory of input files to process'), 
         outdir: Path = typer.Argument(Path("/tmp"), help="directory to save output")):
       
    kerchunk_directory_of_files(indir, outdir)


def kerchunk_directory_of_files(indir:  Path = Path('.'),
                                outdir: Path = Path('/tmp')) -> None:
    
    refs = {}
    fs = fsspec.filesystem('')
    flist = fs.glob(f'{indir}/*')
    with tqdm(total=len(flist)) as pbar:
        for f in flist:
            fname = Path(f).name
            refs[fname] = NetCDF3ToZarr(f).translate()
            pbar.update(1)
        pbar.close()

    for name, ref_json in refs.items():
        outname = '.'.join(name.split('.')[0:-1]) + '.json'
        with open(outdir/outname, 'w') as outf:
            ujson.dump(ref_json, outf)

if __name__ == "__main__":
    typer.run(main)
