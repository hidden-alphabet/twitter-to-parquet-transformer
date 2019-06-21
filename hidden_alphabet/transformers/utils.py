import pyarrow as pa

def objects_to_pyarrow_table(
        objects,
        type_map={
            bool: pa.bool_,
            int: pa.int64,
            bytes: pa.binary,
            str: pa.string,
            dict: pa.struct,
            list: pa.list_
        }
    ):
    columns = list(objects[0].keys())
    values = [list(dict.values()) for dict in objects]
    rows = [pa.array(row) for row in zip(*values)]

    fields = [pa.field(column, type_map[type(values[0][i])]()) for i, column in enumerate(columns)]
    schema = pa.schema(fields)

    batch = pa.RecordBatch.from_arrays(rows, columns)
    table = pa.Table.from_batches([batch], schema)

    return table
