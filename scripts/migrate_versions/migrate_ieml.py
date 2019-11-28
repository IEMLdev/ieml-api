import pygit2

from ieml.ieml_database import GitInterface
from ieml.ieml_database.transactions.DBTransaction import DBTransactions
from ieml.usl import Word
from ieml.usl.lexeme import Lexeme


def migrate(u):
    if not isinstance(u, (Lexeme, Word)):
        return str(u)

    return str(u) + ' asdasd'


if __name__ == '__main__':

    gitdb = GitInterface(origin='ssh://git@github.com/ogrergo/ieml-language.git',
                         credentials=pygit2.Keypair('git', '/home/louis/.ssh/id_rsa.pub', '/home/louis/.ssh/id_rsa', ''),
                         folder='/tmp/gitdb')
    gitdb.pull()

    signature = pygit2.Signature("Louis van Beurden", "louis.vanbeurden@gmail.com")

    transaction = DBTransactions(gitdb, signature)

    transaction.update_all_ieml(migrate, "Test de migration")