import csv
import progressbar
from handlers.dictionary.scripts import drupal_relations_dump


with open("../data/relations.csv", 'w') as fp:
    fieldnames = ['commentary', 'relation_name', 'relation_type', 'term_dest', 'term_src']
    writer = csv.DictWriter(fp, fieldnames=fieldnames)
    writer.writeheader()
    for r in progressbar.ProgressBar()(drupal_relations_dump(all=True)):
        writer.writerow(r)

