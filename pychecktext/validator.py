from typing import List, Dict, Union
from pychecktext import teamcity, get_timestamp, teamcity_messages
import gettext
import os


class ReportFallback(gettext.NullTranslations):
    @staticmethod
    def dgettext(domain: str, message: str) -> str:
        return (message, "**MISSING_TRANSLATION**")

    @staticmethod
    def ldgettext(domain: str, message: str) -> str:
        return (message, "**MISSING_TRANSLATION**")

    @staticmethod
    def dngettext(domain: str, singular: str, plural: str, n: int) -> str:
        return (singular, "**MISSING_TRANSLATION**")

    @staticmethod
    def ldngettext(domain: str, singular: str, plural: str, n: int) -> str:
        return (singular, "**MISSING_TRANSLATION**")

    @staticmethod
    def gettext(message: str) -> str:
        return (message, "**MISSING_TRANSLATION**")

    @staticmethod
    def lgettext(message: str) -> str:
        return (message, "**MISSING_TRANSLATION**")

    @staticmethod
    def ngettext(singular: str, plural: str, n: int) -> str:
        return (singular, "**MISSING_TRANSLATION**")

    @staticmethod
    def lngettext(singular: str, plural: str, n: int) -> str:
        return (singular, "**MISSING_TRANSLATION**")

    @staticmethod
    def pgettext(context: str, message: str) -> str:
        return (message, "**MISSING_TRANSLATION**")

    @staticmethod
    def dpgettext(domain: str, context: str, message: str) -> str:
        return (message, "**MISSING_TRANSLATION**")

    @staticmethod
    def npgettext(context: str, singular: str, plural: str, n: int) -> str:
        return (singular, "**MISSING_TRANSLATION**")

    @staticmethod
    def dnpgettext(domain: str, context: str, singular: str, plural: str, n: int) -> str:
        return (singular, "**MISSING_TRANSLATION**")


class CheckTextTranslation(gettext.GNUTranslations, object):
    def __init__(self, *args, **kwargs):
        super(CheckTextTranslation, self).__init__(*args, **kwargs)
        self.add_fallback(ReportFallback())


def get_translation_object(file_path: str, domain: str, languages: List[str]):
    translations = {}
    for lang in languages:
        if teamcity:
            teamcity_messages.testStarted('checkLanguageExistence.{}.{}'.format(domain, lang),
                captureStandardOutput=False)
        else:
            print("Checking existence of language {} in domain '{}'".format(lang, domain))
        try:
            translations[lang] = gettext.translation(domain, file_path, [lang], class_=CheckTextTranslation)
            if teamcity:
                teamcity_messages.testFinished('checkLanguageExistence.{}.{}'.format(domain, lang))
            else:
                print("Language {} in domain '{}' found.".format(lang, domain))
        except FileNotFoundError:
            if teamcity:
                teamcity_messages.testFailed('checkLanguageExistence.{}.{}'.format(domain, lang), 
                    message="Language file {0}.mo for language {1} is missing.".format(domain, lang))
            else:
                print("Language file {} is missing in domain '{}'".format(lang, domain))
    return translations


def validate_translations(translators: Dict[str, gettext.translation],
                          calls: Dict[str, Dict[str, List[Dict[str, Union[str, List[str]]]]]]):
    for lang, translator in translators.items():
        plural_options = predict_plurals(translator)
        for file_name, call_objs in calls.items():
            literal_calls = call_objs['literal_calls']
            has_failed = False
            if teamcity:
                teamcity_messages.testStarted('checkTokenExistence({}, {})'.format(os.path.basename(file_name), lang), 
                    captureStandardOutput=False)
            else:
                print("Verifying tokens for language {} in file '{}'".format(lang, os.path.basename(file_name)))
            for call in literal_calls:
                if call['function'] in ['gettext', 'dgettext', 'pgettext', 'dpgettext', 'lgettext', 'ldgettext']:
                    translation = getattr(translator, call['function'])(*call['args'])
                    if isinstance(translation, tuple):
                        has_failed = True
                        if teamcity:
                            teamcity_messages.customMessage('msgid {} is missing a translation'.format(translation[0]), 
                                status='FAILURE')
                        else:
                            print("msgid '{}' is missing a translation in language '{}'".format(translation[0], lang))
                else:
                    for plural_form in plural_options:
                        translation = getattr(translator, call['function'])(*call['args'], plural_form)
                        if isinstance(translation, tuple):
                            has_failed = True
                            if teamcity:
                                teamcity_messages.customMessage('msgid {0} is missing a translation '
                                                                'for plural id {1}'.format(translation[0], 
                                                                plural_options[plural_form]), status='FAILURE')                                      
                            else:
                                print("msgid '{}' is missing a translation in language '{}' for plural id {}".format(
                                    translation[0], lang, plural_options[plural_form]
                                ))
            timestamp = get_timestamp()
            if teamcity:
                if has_failed:
                    teamcity_messages.testFailed('checkTokenExistence({}, {})'.format(os.path.basename(file_name), 
                                                                                      lang), "Missing tokens found")
                else:
                    teamcity_messages.testFinished('checkTokenExistence({}, {})'.format(os.path.basename(file_name), 
                                                                                      lang))


def predict_plurals(translator: gettext.translation) -> Dict[int, int]:
    # A survey of the reported plural for examples from
    # 'http://docs.translatehouse.org/projects/localization-guide/en/latest/l10n/pluralforms.html'
    # Suggests that the number of required test ints is quite small
    # TODO: Verify coverage of these example
    test_ints = [*range(0, 30), 100, 101, 117, 200, 201, 1000, 1001]
    options = {}
    result_indexes = set()
    for test_int in test_ints:
        result_index = translator.plural(test_int)
        if result_index not in result_indexes:
            result_indexes.add(result_index)
            options[test_int] = result_index
    return options
