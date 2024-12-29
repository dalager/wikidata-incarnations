# Wikidata Incarnations

This is silly idea.

Let us build a personal reincarnation lineage report based on ~2 million people from wikidata with precise birth and death dates.

## The data

The data is in a gzipped csv file: [born_and_died_slim.csv.gz](born_and_died_slim.csv.gz) (~127mb zipped/ ~475mb unzipped).

It contains 2.953.301 persons with 6 fields:

```csv
id,P569,P570,P27,label,sitelinks
```

- **id** is the wikidata id of the person, can be used to get more data from wikidata site, Q1868 would point to [https://www.wikidata.org/wiki/Q1868](https://www.wikidata.org/wiki/Q1868)
- **P569** is the birth date
- **P570** is the death date
- **P27** is country of citizenship (Q31 for Belgium)
- **label** is the name of the person (Paul Otlet)
- **sitelinks** is a json object with links to wikipedia pages in different languages

## How I got the data

If you want to rebuild the dataset from scratch and add some dimensions to it or something, here is how I did it:

### 1. Get the wikipedia dump

Its big, ~130 gb zipped. Academic torrents has it. <https://academictorrents.com/browse.php?search=wikidata.org>

### 2. Filter the dump for humans with birth and death dates

Get wikibase-dump-filter from <https://github.com/maxlath/wikibase-dump-filter>

Read the documentation and you might end up with a command like this:

```bash
nice -n+19 pigz -d < wikidata-20240101-all.json.gz | grep '"Q5"' | nice -n+19 load-balance-lines wikibase-dump-filter --simplify -q --claim 'P31:Q5&P569&P570' > born_and_died.ndjson
```

It says that you should get all instances of humans (Q5) with birth and death dates (P569 and P570) and put it in a file called born_and_died.ndjson.

The result is 3.6 gb with 2.953.301 persons, one json object per line.

### 3. Trim the data by selecting born, died, country and sitelinks

Something like this:

```bash
cat .\born_and_died.ndjson | jq -c '{id:.id,P569:.claims.P569[0],P570:.claims.P570[0],P27:(.claims.P27[0] // null),label:(.labels.en // (.labels | to_entries | .[0].value)),sitelinks:.sitelinks}' > born_and_died_slim.ndjson
```

result is 650 mb

### 4. Convert ndjson to csv

I made a short python script to convert the ndjson to csv:

```bash
python convert_ndjson_to_csv.py
```

result is 450 mb, 2.953.301 rows.

## Working with the data

1. Load and clean with [01_load_and_clean.ipynb](01_load_and_clean.ipynb)
2. Create reincarnation report with [02_single_person_lineage.ipynb](03_single_person_lineage.ipynb)
