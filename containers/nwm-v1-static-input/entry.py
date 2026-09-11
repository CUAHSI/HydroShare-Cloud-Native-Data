#!/usr/bin/env python3

import sys
import uuid
import typer
import subprocess
from pathlib import Path
from enum import Enum

app = typer.Typer()


class NWMVersion(str, Enum):
    v1_2_4 = "1.2.4"
    v2_0 = "2.0.0"
    v3_0_11 = "3.0.11"


@app.command(context_settings={"ignore_unknown_options": True})
def main(
    ymin: float = typer.Argument(..., help="Lower y boundary"),
    xmin: float = typer.Argument(..., help="Lower x boundary"),
    ymax: float = typer.Argument(..., help="Upper y boundary"),
    xmax: float = typer.Argument(..., help="Upper x boundary"),
    nwmv1_data: str = typer.Argument(
        "/srv/domain",
        help="Directory where NWM V1.2.4 data is located/mounted "
        "within the container",
    ),
    output_dir: str = typer.Argument("/srv/output", help="Directory to save output"),
    cell_buffer: int = typer.Argument(4, help="Buffer around the subset domain"),
    nwm_version: NWMVersion = typer.Argument("1.2.4", help="NWM version to use"),
):
    print(f"{xmin} {xmax} {ymin} {ymax} {nwmv1_data} {output_dir} {cell_buffer}")

    # generate unique identifier for the job
    uid = uuid.uuid4().hex

    # run the subsetting operation
    subset(
        uid, xmin, xmax, ymin, ymax, nwmv1_data, output_dir, cell_buffer, nwm_version
    )


def subset(
    uid,
    xmin,
    xmax,
    ymin,
    ymax,
    nwmv1_data,
    output_dir="/tmp",
    cell_buffer=4,
    nwm_version=NWMVersion.v1_2_4,
):

    # set the subset script based on the NWM version
    script_dir = "v1"  # set the default to v1
    if nwm_version == NWMVersion.v2_0:
        script_dir = "v2"
    elif nwm_version == NWMVersion.v3_0_11:
        # hard coded to the domain dir for now. This should be changed in the
        # future to be more flexible by adding a domain argument to the function.
        # This will enable subsetting of Alaska, Hawaii, and Puerto Rico domains.
        nwmv1_data = nwmv1_data + "/domain"
        script_dir = "v3"
    working_dir = Path("/srv/scripts") / script_dir

    subset_script = "subset_domain.R"

    cmd = [
        "Rscript",
        subset_script,
        uid,
        str(ymin),
        str(ymax),
        str(xmin),
        str(xmax),
        nwmv1_data,
        output_dir,
        str(cell_buffer),
    ]
    print(" ".join(cmd))
    p = subprocess.Popen(
        cmd, cwd=working_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
    )
    for c in iter(lambda: p.stdout.read(1), b""):
        sys.stdout.buffer.write(c)
    p.stdout.close()
    p.wait()


#    # run watershed shapefile creation
#    if len(hucs) != 0:
#        logger.debug('Submitting create_shapefile')
#        outpath = os.path.join(outdir, 'watershed.shp')
#        watershed.create_shapefile(uid, hucs, outpath)
#    else:
#        msg = 'skipping create_shapefile b/c no hucs were provided'
#        logger.debug(msg)
#
#    # write metadata file
#    meta = {'date_processed': str(datetime.now(tz=timezone.utc)),
#            'guid': uid,
#            'model': 'WRF-Hydro configured as NWM',
#            'version': '1.2.4',
#            'hucs': hucs}
#
#    with open(os.path.join(outdir, 'metadata.json'), 'w') as jsonfile:
#        json.dump(meta, jsonfile)

if __name__ == "__main__":
    app()
