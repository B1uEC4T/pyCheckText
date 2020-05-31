import shutil
import os
import itertools
import pytest
import sys
import gettext
from typing import List, Iterable, Union, Dict
sys.path.extend('../../')
from pychecktext.validator import get_translation_object, validate_translations  # noqa: E402

supported_languages = ['en', 'ar', 'ay']


@pytest.fixture
def english_fixture():
    language = 'en'
    os.makedirs("./tests/test_module/locale/{}/LC_MESSAGES".format(language), exist_ok=True)
    shutil.copy("./tests/test_artifacts/{}.mo".format(language), 
                "./tests/test_module/locale/{}/LC_MESSAGES".format(language))
    os.rename("./tests/test_module/locale/{0}/LC_MESSAGES/{0}.mo".format(language),
              "./tests/test_module/locale/{}/LC_MESSAGES/test.mo".format(language))
    output = get_translation_object("./tests/test_module/locale", "test", [language])
    yield output


def all_combinations(any_list: List[any]) -> Iterable[Union[str, List[str]]]:
    return itertools.chain.from_iterable(
        itertools.combinations(any_list, i + 1)
        for i in range(len(any_list)))


def copy_languages(languages: List[str]):
    for language in languages:
        os.makedirs("./tests/test_module/locale/{}/LC_MESSAGES".format(language), exist_ok=True)
        shutil.copy("./tests/test_artifacts/{}.mo".format(language), 
                    "./tests/test_module/locale/{}/LC_MESSAGES".format(language))
        os.rename("./tests/test_module/locale/{0}/LC_MESSAGES/{0}.mo".format(language),
                  "./tests/test_module/locale/{0}/LC_MESSAGES/test.mo".format(language))


@pytest.mark.parametrize('languages', all_combinations(supported_languages))
def test_get_translations(cleanup_fixture, languages: List[str]):
    copy_languages(languages)
    output = get_translation_object("./tests/test_module/locale",
                                    "test", languages)
    assert len(output) == len(languages)
    for lang, translator in output.items():
        assert isinstance(translator, gettext.GNUTranslations)
        info = translator.info()
        assert info['language'] == lang


def test_get_translations_missing(capsys, cleanup_fixture):
    copy_languages(['ar', 'ay'])
    output = get_translation_object("./tests/test_module/locale",
                                    "test", ['ar', 'ay', 'en'])
    stdout = capsys.readouterr().out
    assert len(output) == 2
    assert "Language file en is missing in domain 'test'" in stdout
    for lang, translator in output.items():
        assert isinstance(translator, gettext.GNUTranslations)
        info = translator.info()
        assert info['language'] == lang


test_calls = [
    {
        'function': 'gettext',
        'args': ['herring'],
        'expected': 'You must cut down the mightiest tree in the forest with... a herring!'
    },
    {
        "function": "ngettext",
        "args": ["swallow_singular", "swallow_plural"],
        "expected": "How do you know so much about a swallow?"
    },
    {
        "function": "ngettext",
        "args": ["swallow_singular", "swallow_plural"],
        "expected": "How do you know so much about swallows?"
    },
    {
        "function": "pgettext",
        "args": ["polite", "parrot"],
        "expected": "He has expired and gone to meet his maker."
    },
    {
        "function": "pgettext",
        "args": ["impolite", "parrot"],
        "expected": "He's run down the curtain and joined the bleeding choir invisible."
    },
    {
        "function": "npgettext",
        "args": ["male", "french_singular", "french_plural"],
        "expected": "He's run down the curtain and joined the bleeding choir invisible."
    },
    {
        "function": "npgettext",
        "args": ["male", "french_singular", "french_plural"],
        "expected": "He's run down the curtain and joined the bleeding choir invisible."
    },
    {
        "function": "npgettext",
        "args": ["female", "french_singular", "french_plural"],
        "expected": "He's run down the curtain and joined the bleeding choir invisible."
    },
    {
        "function": "npgettext",
        "args": ["female", "french_singular", "french_plural"],
        "expected": "He's run down the curtain and joined the bleeding choir invisible."
    }
]


@pytest.mark.parametrize("call", test_calls)
def test_valid_translations(english_fixture,
                            cleanup_fixture,
                            capsys,
                            call: Dict[str, Union[str, List[str]]]):
    translators = english_fixture
    validate_translations(translators, {'test.py': {'literal_calls': [call]}})
    outputs = capsys.readouterr()
    stdout = outputs.out.splitlines()
    stderr = outputs.err
    assert stderr == ''
    assert len(stdout) == 1


def test_missing_context(english_fixture,
                         cleanup_fixture,
                         capsys):
    call = {
        "function": "pgettext",
        "args": ["downright_rude", "parrot"]
    }
    translators = english_fixture
    validate_translations(translators, {'test.py': {'literal_calls': [call]}})
    outputs = capsys.readouterr()
    stdout = outputs.out.splitlines()
    stderr = outputs.err
    assert stderr == ''
    assert len(stdout) == 2
    assert all(test in stdout[1] for test in ['parrot', 'en'])


def test_missing_translation(english_fixture,
                             cleanup_fixture,
                             capsys):
    call = {
        "function": "gettext",
        "args": ["blank"]
    }
    translators = english_fixture
    validate_translations(translators, {'test.py': {'literal_calls': [call]}})
    outputs = capsys.readouterr()
    stdout = outputs.out.splitlines()
    stderr = outputs.err
    assert stderr == ''
    assert len(stdout) == 2
    assert all(test in stdout[1] for test in ['blank', 'en'])


def test_missing_msgid(english_fixture,
                       cleanup_fixture,
                       capsys):
    call = {
        "function": "gettext",
        "args": ["not_the_messiah"]
    }
    translators = english_fixture
    validate_translations(translators, {'test.py': {'literal_calls': [call]}})
    outputs = capsys.readouterr()
    stdout = outputs.out.splitlines()
    stderr = outputs.err
    assert stderr == ''
    assert len(stdout) == 2
    assert all(test in stdout[1] for test in ['not_the_messiah', 'en'])
