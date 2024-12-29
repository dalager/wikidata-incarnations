# Reincarnator

## Getting the data

1. Get the wikipedia dump

Its big. academic torrents has it. I have it on my external drive.

2. filter the dump for humans with birth and death dates

install the tools

```bash
npm install
```

```bash
nice -n+19 pigz -d < /mnt/c/temp/wikidata/wikidata-20240101-all.json.gz | grep '"Q5"' | nice -n+19 load-balance-lines wikibase-dump-filter --simplify -q --claim 'P31:Q5&P569&P570' > /mnt/f/wikidata/born_and_died.ndjson
```

Result is 3.6 gb with 2.953.301 persons

3. trim the data by selecting born, died, country and sitelinks

```powershell
gc .\born_and_died.ndjson | jq -c '{id:.id,P569:.claims.P569[0],P570:.claims.P570[0],P27:(.claims.P27[0] // null),label:(.labels.en // (.labels | to_entries | .[0].value)),sitelinks:.sitelinks}' > born_and_died_slim_rebuild.ndjson
```

result is 650 mb

4. convert ndjson to csv

```powershell
python convert_ndjson_to_csv.py
```

result is 450 mb, 2.953.301 rows.

## Working with the data

1. Load and clean with [01_load_and_clean.ipynb](01_load_and_clean.ipynb)
2. Create reincarnation report with [02_single_person_lineage.ipynb](03_single_person_lineage.ipynb)

# Old stuff

This is a collection of wikidata sparql queries that I have found useful.

Run the queries with python and the wikidata integrator library.

## Main requirements

## wikibase-dump-filter

## without simplify

```bash


cat wikidata-20240101-all.json.gz | gzip -d | grep '"Q5"' | wikibase-dump-filter -p --claim 'P31:Q5&P569&P570' | jq -c '{id:.id, P569: .claims.P569[0].mainsnak.datavalue.value.time, P570: .claims.P570[0].mainsnak.datavalue.value.time, P27: .claims.P27[0].mainsnak.datavalue.value.id,label: (.labels.en.value // (.labels | to_entries | .[0].value.value))}' > narrow_output.ndjson
```

## with simplify

```bash

cat wikidata-20240101-all.json.gz | gzip -d | grep '"Q5"' | wikibase-dump-filter -p --claim 'P31:Q5&P569&P570' --simplify | gojq -c '{id:.id,P569:.claims.P569[0],P570:.claims.P570[0],P27:(.claims.P27[0] // null),label:(.labels.en // (.labels | to_entries | .[0].value))}' > narrow_output.ndjson

```

### parallel

#### just take the first 100000 lines from the dump

```bash
nice -n+19 pigz -d < wikidata-20240101-all.json.gz | grep '"Q5"' |head -n 1000| nice -n+19 load-balance-lines wikibase-dump-filter --claim 'P31:Q5&P569&P570' --languages en,fr,de,da,it,sp | jq -c 'try { {id:.id, P569: .claims.P569[0].mainsnak.datavalue.value.time, P570: .claims.P570[0].mainsnak.datavalue.value.time, P27: .claims.P27[0].mainsnak.datavalue.value.id,label: (.labels.en.value // (.labels | to_entries | .[0].value.value))} } catch $e { "error:$e" }' > parallelout.ndjson
```

#### final version

```bash
nice -n+19 pigz -d < wikidata-20240101-all.json.gz | grep '"Q5"' | nice -n+19 load-balance-lines wikibase-dump-filter --simplify --languages en,de,fr,it,sp --claim 'P31:Q5&P569&P570' | jq -c '{id:.id, P569: .claims.P569[0].mainsnak.datavalue.value.time, P570: .claims.P570[0].mainsnak.datavalue.value.time, P27: .claims.P27[0].mainsnak.datavalue.value.id,label: (.labels.en.value // (.labels | to_entries | .[0].value.value))}' > parallelout.ndjson
```

```bash
# raw
nice -n+19 pigz -d < wikidata-20240101-all.json.gz | grep '"Q5"' | nice -n+19 load-balance-lines wikibase-dump-filter --simplify --languages en,de,fr,it,sp --claim 'P31:Q5&P569&P570' | jq -c '{id:.id, P569: .claims.P569[0].mainsnak.datavalue.value.time, P570: .claims.P570[0].mainsnak.datavalue.value.time, P27: .claims.P27[0].mainsnak.datavalue.value.id,label: (.labels.en.value // (.labels | to_entries | .[0].value.value))}' > /mnt/f/wikidata/born_and_died.ndjson



nice -n+19 pigz -d < wikidata-20240101-all.json.gz | grep '"Q5"' | head -n 10000000 | nice -n+19 load-balance-lines wikibase-dump-filter --simplify --claim 'P31:Q5&P569&P570' | jq -c '{id:.id,P569:.claims.P569[0],P570:.claims.P570[0],P27:(.claims.P27[0] // null),label:(.labels.en // (.labels | to_entries | .[0].value))}' > parallelout.ndjson

## breaking on numeric jq issue

```

nice -n+19 pigz -d < wikidata-20240101-all.json.gz | grep '"Q5"' | head -n 10000000 | nice -n+19 load-balance-lines wikibase-dump-filter --simplify --claim 'P31:Q5&P569&P570' | jq -c '{id:.id,P569:.claims.P569[0],P570:.claims.P570[0],P27:(.claims.P27[0] // null),label:(.labels.en // (.labels | to_entries | .[0].value))}' > parallelout.ndjson

````

## skrællet

nice -n+19 pigz -d < wikidata-20240101-all.json.gz | grep '"Q5"' | head -n 10000000 | nice -n+19 load-balance-lines wikibase-dump-filter --simplify --claim 'P31:Q5&P569&P570' | jq -c --stream-errors '{id:.id}' > parallelout.ndjson

## with parallel

nice -n +19 pigz -dc wikidata-20240101-all.json.gz | \
grep '"Q5"' | \
nice -n +19 parallel --pipe --block 10M -j$(nproc) "
load-balance-lines wikibase-dump-filter --simplify --claim 'P31:Q5&P569&P570' | \
 jq -c '{id:.id,P569:.claims.P569[0],P570:.claims.P570[0],P27:(.claims.P27[0] // null),label:(.labels.en // (.labels | to_entries | .[0].value))}'
" > parallelout.ndjson

jq -c --stream 'select(.[1].claims.P31[0].mainsnak.datavalue.value.id == "Q5") | {id: .[1].id, P569: .[1].claims.P569[0].ainsnak.datavalue.value.time, P570: .[1].claims.P570[0].mainsnak.datavalue.value.time, P27: .[1].claims.P27[0].mainsnak.atavalue.value.id, label: (.[1].labels.en.value // (.[1].labels | to_entries | .[0].value.value))}'

Det her virker ikke. jq giver en parse fejl

```bash
nice -n+19 pigz -d < wikidata-20240101-all.json.gz | nice -n+19 load-balance-lines wikibase-dump-filter --claim 'P31:Q5&P569&P570' | jq '{id:.id}'> humans.ndjson
````

cat wikidata-20240101-all.json.gz | nice -n+19 pigz -d | nice -n+19 load-balance-lines wikibase-dump-filter --claim 'P31:Q5&P569&P570' | jq '{id:.id}'> humans.ndjson

jq '{id:.id, P569: .claims.P569[0].mainsnak.datavalue.value.time, P570: .claims.P570[0].mainsnak.datavalue.value.time, P27: .claims.P27[0].mainsnak.datavalue.value.id,label: (.labels.en.value // (.labels | to_entries | .[0].value.value))}'

### Requirements

json dump
wikibase-dump-filter

### Steps

Select only humans:

In WSL

    ```bash

cat wikidata.gz | gzip -d | wikibase-dump-filter --claim P31:Q5 > humans.ndjson

```

```

birthdate: https://www.wikidata.org/wiki/Property:P569
deathdate: https://www.wikidata.org/wiki/Property:P570

## Tom

3. maj 1961
