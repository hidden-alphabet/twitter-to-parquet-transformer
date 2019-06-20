from hidden_alphabet.transformers import twitter
import sys

print('Opening file.')
file = open(sys.argv[1])

print('Reading file.')
html = file.read()

print('Parsing objects')
objects = twitter.html_to_objects(html)

print('Parsing pyarrow table')
table = twitter.objects_to_pyarrow_table(objects)

print('Done!')
