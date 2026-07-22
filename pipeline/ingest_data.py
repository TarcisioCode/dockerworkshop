#!/usr/bin/env python
# coding: utf-8


import click
import pandas as pd
import tqdm as t
from sqlalchemy import create_engine

dtype = {
    "VendorID": "Int64",
    "passenger_count": "Int64",
    "trip_distance": "float64",
    "RatecodeID": "Int64",
    "store_and_fwd_flag": "string",
    "PULocationID": "Int64",
    "DOLocationID": "Int64",
    "payment_type": "Int64",
    "fare_amount": "float64",
    "extra": "float64",
    "mta_tax": "float64",
    "tip_amount": "float64",
    "tolls_amount": "float64",
    "improvement_surcharge": "float64",
    "total_amount": "float64",
    "congestion_surcharge": "float64"
}

parse_dates = [
    "tpep_pickup_datetime",
    "tpep_dropoff_datetime"
]


@click.command()
@click.option('--pg-user', default='root', help='PostgreSQL user.')
@click.option('--pg-pass', default='root', help='PostgreSQL password.')
@click.option('--pg-host', default='localhost', help='PostgreSQL host.')
@click.option('--pg-db', default='ny_taxi', help='PostgreSQL database name.')
@click.option('--port', default=5432, type=int, help='PostgreSQL port.')
@click.option('--year', default=2021, type=int, help='Year of the trip data.')
@click.option('--month', default=1, type=int, help='Month of the trip data.')
@click.option('--target-table', default='yellow_taxi_data', help='Destination table name.')
@click.option('--chunk-size', default=100000, type=int, help='Rows per insert chunk.')
def run(pg_user, pg_pass, pg_host, pg_db, port, year, month, target_table, chunk_size):
    prefix = 'https://github.com/DataTalksClub/nyc-tlc-data/releases/download/yellow/'
    file_name = f'yellow_tripdata_{year}-{month:02d}.csv.gz'

    df_iter = pd.read_csv(
        prefix + file_name,
        dtype=dtype,
        parse_dates=parse_dates,
        iterator=True,
        chunksize=chunk_size
    )
    engine = create_engine(f'postgresql+psycopg://{pg_user}:{pg_pass}@{pg_host}:{port}/{pg_db}')

    first = True
    
    for df_chunk in t.tqdm(df_iter):
        if first:
            df_chunk.head(n=0).to_sql(
                name=target_table,
                con=engine,
                if_exists='replace')
            
            first = False
        df_chunk.to_sql(
            name=target_table, 
            con=engine, 
            if_exists='append')

if __name__ == '__main__':
    run()