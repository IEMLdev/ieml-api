from ieml.dictionary.script import Script
from typing import List, Dict

Translations=Dict[str, List[str]]
Commentary=Dict[str, List[str]]
Inhibitions=List[str]


class IEMLDBInterface:
    def create_morpheme_root_paradigm(self,
                                      script: Script,
                                      translations: Translations,
                                      author_name: str,
                                      author_mail: str,
                                      comments: Commentary=None,
                                      inhibitions: Inhibitions = ()):
        """
        Add a new root morpheme to the dictionary. All the singular sequences morphemes are also
        automatically created.

        :param script: The root morpheme
        :param translations: translations for this morpheme
        :param comments: Optional : commentaries for this morpheme or None
        :param inhibitions: List of relations inhibitions
        :return: None
        """
        raise NotImplementedError

    def add_morpheme_paradigm(self,
                              script: Script,
                              author_name: str,
                              author_mail: str,
                              translations: Translations = None,
                              comments: Commentary = None):
        """
        Add a paradigm to a root paradigm.
        :param script: The script of the morpheme paradigm
        :param translations: Optional : translations for this morpheme or None
        :param comments: Optional : commentaries for this morpheme or None
        :return: None
        """
        raise NotImplementedError

    def delete_morpheme_root_paradigm(self,
                                      script: Script,
                                      author_name: str,
                                      author_mail: str):
        """
        Delete an existing root paradigms and all its translations, commentaries, inhibitions, with all
        the other morphemes and paradigms that are contains in this root morpheme.

        :param script: The root morpheme
        :return: None
        """
        raise NotImplementedError

    def delete_morpheme_paradigm(self,
                                 script: Script,
                                 author_name: str,
                                 author_mail: str):
        """
        Delete an existing non-root morpheme paradigm.

        :param script: The morpheme paradigm
        :return: None
        """
        raise NotImplementedError

    def update_morpheme_translation(self,
                                    script: Script,
                                    translations: Translations,
                                    author_name: str,
                                    author_mail: str,
                                    inhibitions: Inhibitions=()):
        """
        Update translation for this morpheme

        :param script: The morpheme
        :param translation: The translation
        :return: None
        """
        raise NotImplementedError

    @classmethod
    def set_morpheme_comments(cls, db_folder: str, script: Script, comments: Commentary):
        """
        Update comments for this morpheme

        :param script: The morpheme
        :param comments: The comments
        :return: None
        """
        raise NotImplementedError

    def set_morpheme_root_paradigm_inhibitions(self,
                                               script: Script,
                                               inhibitions: Inhibitions):
        """
        Update inhibitions for this root morpheme

        :param script: The morpheme
        :param inhibitions: The inhibitions
        :return: None
        """
        raise NotImplementedError
