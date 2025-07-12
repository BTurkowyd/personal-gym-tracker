import pyarrow.parquet as pq


def print_parquet_schema(filename):
    table = pq.read_table(filename)
    print(f"Schema for {filename}:")
    print(table.schema)
    print("-" * 40)


for fname in ["e59aef22-aec5-430a-b26e-e01a58ced34c.parquet"]:
    print_parquet_schema(fname)
