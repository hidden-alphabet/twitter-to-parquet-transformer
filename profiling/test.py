import transformer
import sys

file = open(sys.argv[1])
html = file.read().decode('utf-8')
search = TwitterAdvancedSearchHTML(html)
parquet = TwitterAdvancedSearchHTML.to_parquet()
