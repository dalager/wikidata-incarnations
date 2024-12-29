import sys
import pandas as pd

# use first argument as input filename and second argument as output filename
# if no arguments are provided, use default values

filename = sys.argv[1] if len(sys.argv) > 1 else "born_and_died_slim.ndjson"
output_filename = sys.argv[2] if len(sys.argv) > 2 else "born_and_died_slim.csv"


pd.read_json(filename, lines=True).to_csv(output_filename, index=False)
