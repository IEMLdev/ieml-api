rm -r data/dump/
tar xvf data/terms.tar.gz -C data/
mongorestore --drop data/dump
rm -r data/dump