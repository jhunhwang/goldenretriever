## Below is an example for configuring and tuning Goldenretriever one section of data in Sample HR handbook.
### Installation and requirements
- python version: 3.6 - 3.7 (some tensorflow modules are uncompatible with python 3.8)
- updated requirements.txt file on module versions

### 1) Change configurations under:
```./app/api/config```

a. Change QA index
```python
#Example:
QA_INDEX = 'duke_hr'    # this will be the index name of the data you upload to elasticsearch
```
b. Change names for Minio
```python
# paths for nearest neighbor index
INDEX_BUCKET = 'pdpa-index'. # name of minio bucket to save index to
INDEX_PICKLE = 'pdpa-data.pkl'. # name of pickle file output by saving process
INDEX_FILE = 'pdpa.idx'. # name of .idx file output by saving process
INDEX_PREFIX = 'pdpa'. # prefix used when loading index. This should corresponse to 'prefix-data.pkl' and 'prefix.idx'
```

```python
#Example:
# paths for nearest neighbor index
INDEX_BUCKET = 'duke_hr-index'
INDEX_PICKLE = 'duke_hr-data.pkl'
INDEX_FILE = 'duke_hr.idx'
INDEX_PREFIX = 'duke_hr'
```
### 2) Change configurations under:

```./src/finetune/config```

a. Change Kb name
```python
#Example:
kb_names:["duke_hr"]    # you use the kb_names as index in elasticsearch to return the qa pair.
```
### 3) Before running docker compose up, we will need to increase the limit of mmap counts.
The default operating system limits on mmap count is likely to be too low for Elasticsearch.
Run the code below to increase virtual memory limit. Click the link below to learn more.
https://www.elastic.co/guide/en/elasticsearch/reference/current/vm-max-map-count.html
```bash
sysctl -w vm.max_map_count=262144
```

### 4) Docker Compose makes it easy to run the following Docker container applications to form a fully integrated application. Build and start the multi-container application by typing:

```
docker-compose -f docker-compose.yml build
docker-compose -f docker-compose.yml up
```

### 5) Input the csv data under data directory

### 6) Uploading training/evaluation data to elasticsearch
```python
# --url: elasticsearch url
# --csv_file : csv file with question and answer pairs
# --index_name : name of index to create (in elasticsearch, index name is like you table name)

python -m src.elasticsearch.create_doc_index --url localhost --csv_file data/pdpa.csv --index_name qa-pdpa
```
```python
#Example: [we do not need the --prefixes]

python -m src.elasticsearch.create_doc_index http://localhost:9200/ data/sample_duke_hr.csv duke_hr
```

### 7) Fine tune
Only after we have uploaded our data to elasticsearch we can use the command below to finetune
```python
python -m src.finetune.main
```
### 8) Encode and save index from elasticsearch

```python
# --index_name: name of index to export as csv
# --csv_prefix: prefix to add to -.csv of index
# --savedir: path to save csv file

python -m src.dvc_pipeline_scripts.index_extract --index_name pdpa --csv_prefix pdpa --savedir ./test
```
```python
#Example: [Here we need the --prefixes]

python -m src.dvc_pipeline_scripts.index_extract --index_name=duke_hr --csv_prefix=sample_duke_hr --savedir=./test_hr
```
```python
# --data: path to file with raw responses
# --output_folder: path to save index
# --index_prefix: prefix to add to -data.pkl of index
# --gr_model: name of gr model
# --savedir: path to fine-tuned encoder weights

#Example
python -m src.dvc_pipeline_scripts.index_encode --data=./data/sample_duke_hr.csv --output_folder=model_artefacts --index_prefix=duke_hr --gr_model=USEEncoder --savedir=./test_finetune/model_duke_hr/USE/best/0
```
