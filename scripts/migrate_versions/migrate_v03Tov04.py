import argparse
from collections import defaultdict
import json

from ieml import IEMLDatabase


def migrate(database, author_name, author_email):
    folder = database.folder

    all_db = defaultdict(lambda : defaultdict(dict))

    for (ieml, lang, desc), (v) in database.descriptors():
        # print(ieml)
        all_db[ieml][lang][desc] = v.values[0]

    return {
        ieml: dict(dd) for ieml, dd in all_db.items()
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('author_name', type=str)
    parser.add_argument('author_email', type=str)

    parser.add_argument('--folder', type=str)

    args = parser.parse_args()

    folder = args.folder

    db = IEMLDatabase(db_folder=folder)

    r = migrate(db, args.author_name, args.author_email)
    print(json.dumps(r, indent=True))
