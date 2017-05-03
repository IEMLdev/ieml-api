#!/bin/bash

cd data/ && mongodump --db=ieml_db --collection=terms && tar cvf terms.tar.gz dump/ieml_db/
rm -r dump
