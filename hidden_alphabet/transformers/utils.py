import pyarrow as pa
import collections

# Fixes: https://issues.apache.org/jira/browse/ARROW-3080?src=confmacro
def order_by_key(obj):
    return dict(collections.OrderedDict(sorted(obj.items())))

def pytype_to_pyarrow_type(
        obj,
        type_map={
            int: pa.int64,
            str: pa.string,
            bool: pa.bool_,
            bytes: pa.binary,
            float: pa.float64
        }
    ):
    t = type(obj)

    if t is list:
        if len(obj) > 0:
            return pa.list_(pytype_to_pyarrow_type(obj[0]))
        else:
            raise Exception('pyarrow.list_ does not support empty lists.')
    if t is dict:
	# PyArrow, currently, does not correctly handle the management of
	# complexly typed parquet structures. In particular, if the line
	# below this comment is removed, line 70 of this file fails in the
	# manner illustrated below:
	#
	# >>> utils.list_of_dicts_to_pyarrow_table([{ 'foo': { 'bar': {}, 'bac': {}, 'foo': 1 } }])
	# 	Traceback (most recent call last):
	# 	File "utils.py", line 47, in list_of_dicts_to_pyarrow_table
	#	File "pyarrow/table.pxi", line 1251, in pyarrow.lib.Table.from_batches
	# 	File "pyarrow/error.pxi", line 81, in pyarrow.lib.check_status
	# 	pyarrow.lib.ArrowInvalid: Schema at index 0 was different:
	# 	foo: struct<bar: struct<>, bac: struct<>, foo: int64>
	#	vs
        #	foo: struct<bac: struct<>, bar: struct<>, foo: int64>
	#
	# But, as shown be the following two examples, the above error only arises due to the
	# ordering of the keys to the nested dictionaries:
	#
	# >>> utils.list_of_dicts_to_pyarrow_table([{ 'foo': { 'bac': {}, 'bar': {}, 'foo': 1 } }])
	# >>> utils.list_of_dicts_to_pyarrow_table([{ 'foo': { 'bar': {}, 'bac': {} } }])
	#
	# The solution is thus to order those dictionaries, bykey, which is done
	# below:
        obj = order_by_key(obj)

        types = [pytype_to_pyarrow_type(v) for v in obj.values()]
        fields = [(k, v) for k, v in zip(obj.keys(), types)]
        return pa.struct(fields)
    else:
        return type_map[t]()

def list_of_dicts_to_pyarrow_table(objects):
    if len(objects) <= 0:
        return pa.Table.from_arrays([], [])

    objects = [order_by_key(obj) for obj in objects]

    columns = list(objects[0].keys())
    values = [list(dict.values()) for dict in objects]
    rows = [pa.array(row) for row in zip(*values)]

    fields = [pa.field(column, pytype_to_pyarrow_type(values[0][i])) for i, column in enumerate(columns)]
    schema = pa.schema(fields)

    batch = pa.RecordBatch.from_arrays(rows, columns)
    table = pa.Table.from_batches([batch], schema)

    return table
