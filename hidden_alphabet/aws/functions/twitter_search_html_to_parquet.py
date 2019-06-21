from hidden_alphabet.transformers import twitter
from hidden_alphabet.transformers import utils
from multiprocessing.dummy import Pool
from s3fs import S3FileSystem
import multiprocessing as mp
import pyarrow.parquet as pq
import pyarrow as pa
import os

ACCESS_KEY = os.environ['AWS_S3_ACCESS_KEY']
SECRET_KEY = os.environ['AWS_S3_SECRET_ACCESS_KEY']
FS = S3FileSystem(key=ACCESS_KEY, secret=SECRET_KEY)

def extract_transform_load(path):
    print('Reading {} from S3'.format(path))
    html = FS.open(path, 'r').read()

    print('Parsing HTML')
    objects = twitter.html_to_objects(html)

    print('Parsing twitter artifacts into pyarrow')
    table = utils.objects_to_pyarrow_table(objects)
    
    out = path.replace('.html', '.parquet').replace('raw', 'processed') 

    print('Writing to {}'.format(out))
    pq.write_to_dataset(
        table=table,
        root_path=out,
        use_dictionary=True,
        compression='snappy',
        filesystem=FS,
    )

    return True

def handler(event, context):
    status = 'error'

    if event is not None and len(event.get('Records', [])) > 0:
        objects = [(record['s3']['bucket']['name'], record['s3']['object']['key']) for record in event['Records']]
        files = ["s3://{}/{}".format(bucket, key) for bucket, key in objects] 

        pool = Pool(min(mp.cpu_count(), len(files)))

        pool.map(extract_transform_load, files)

        pool.close() 
        pool.join() 

        status = 'ok'

    return { 'status': status } 
