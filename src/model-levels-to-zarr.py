# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Convert Model level Era 5 Data to an unprocessed Zarr dataset.

Examples:
    Check if there's any missing data:
    ```
    python src/model-levels-to-zarr.py gs://anthromet-external-era5/model-level-reanalysis.zarr gs://$BUCKET/ml-cache/ \
     --start 1979-01-01 \
     --end 2021-07-01 \
     --setup_file ./setup.py \
     --find-missing
    ```

    Perform the conversion for the moisture dataset...
    ```
    python src/model-levels-to-zarr.py gs://anthromet-external-era5/model-level-moisture.zarr gs://$BUCKET/ml-moist-cache/ \
     --start 1979-01-01 \
     --end 2021-07-01 \
     --chunks o3q qrqs \
     --runner DataflowRunner \
     --project $PROJECT \
     --region $REGION \
     --temp_location "gs://$BUCKET/tmp/" \
     --setup_file ./setup.py \
     --experiment=use_runner_v2 \
     --disk_size_gb 3600 \
     --machine_type m1-ultramem-40 \
     --sdk_container_image=gcr.io/ai-for-weather/ecmwf-beam-worker:latest \
     --job_name model-level-moisture-to-zarr

    ```
    Perform the conversion for the wind dataset...
    ```
    python src/model-levels-to-zarr.py gs://anthromet-external-era5/model-level-wind.zarr gs://$BUCKET/ml-wind-cache1/ \
     --start 1979-01-01 \
     --end 2021-07-01 \
     --chunks dve tw \
     --runner DataflowRunner \
     --project $PROJECT \
     --region $REGION \
     --temp_location "gs://$BUCKET/tmp/" \
     --setup_file ./setup.py \
     --experiment=use_runner_v2 \
     --disk_size_gb 3600 \
     --machine_type m1-ultramem-40 \
     --sdk_container_image=gcr.io/ai-for-weather/ecmwf-beam-worker:latest \
     --job_name model-level-wind-to-zarr
    ```
"""
import datetime
import logging

import pandas as pd

from pangeo import run, parse_args

if __name__ == "__main__":
    logging.getLogger('pangeo_forge_recipes').setLevel(logging.DEBUG)
    logging.getLogger().setLevel(logging.INFO)

    def make_path(time: datetime.datetime, chunk: str) -> str:
        """Make path to Era5 data from timestamp and variable."""

        # Handle chunks that have been manually split into one-variable files.
        if '_' in chunk:
            chunk_, level, var = chunk.split('_')
            return (
                f"gs://external-data-ai-for-weather/ERA5GRIB/HRES/Daily/"
                f"{time.year:04d}/{time.year:04d}{time.month:02d}{time.day:02d}_hres_{chunk_}.grb2_{level}_{var}.grib"
            )

        return (
            f"gs://external-data-ai-for-weather/ERA5GRIB/HRES/Daily/"
            f"{time.year:04d}/{time.year:04d}{time.month:02d}{time.day:02d}_hres_{chunk}.grb2"
        )

    default_chunks = ['dve', 'tw']

    parsed_args, unknown_args = parse_args('Convert Era 5 Model Level data to Zarr', default_chunks)

    date_range = [
        ts.to_pydatetime()
        for ts in pd.date_range(start=parsed_args.start,
                                end=parsed_args.end,
                                freq="D").to_list()
    ]

    run(make_path, date_range, parsed_args, unknown_args)