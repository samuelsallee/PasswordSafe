# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/getEnv.ipynb (unless otherwise specified).

__all__ = ['BUCKETNAME', 'TABLENAME', 'SIMPLETABLENAME']

# Cell
# pull out data from environemnt variable
import os
BUCKETNAME = os.environ.get('BUCKETNAME')
TABLENAME = os.environ.get('TABLENAME')
SIMPLETABLENAME = os.environ.get('SIMPLETABLENAME')