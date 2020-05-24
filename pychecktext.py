import ast
import _ast
import argparse
from typing import Union, List, Dict, Set
import os
import gettext

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

class CheckTextVisitor(ast.NodeVisitor):
    def __init__(self, aliases: Dict[str, str] = {}):
        self.literal_calls = []
        self.expression_calls = []
        self.aliases = aliases
        self.function_signatures = {
            "dgettext": [0, 1],
            "dngettext": [0, 1, 2],
            "dnpgettext": [0, 1, 2, 3],
            "dpgettext": [0, 1, 2],
            "gettext": [0],
            "ldgettext": [0, 1],
            "ldngettext": [0, 1, 2],
            "lgettext": [0],
            "lngettext": [0, 1],
            "ngettext": [0, 1],
            "npgettext": [0, 1, 2],
            "pgettext": [0, 1]}
        for alias, source in aliases.items():
            self.function_signatures[alias] = self.function_signatures[source]
    
    def visit_Call(self, node: _ast.Call):
        func_object = node.func
        if hasattr(node, 'args'):
            for arg in node.args:
                if isinstance(arg, _ast.Call):
                    self.visit_Call(arg)
        if hasattr(func_object, 'id') and func_object.id in self.function_signatures:
            # Get the calling function name, resolve aliases here
            if func_object.id in self.aliases:
                calling_name = self.aliases[func_object.id]
            else:
                calling_name = func_object.id
            # A call to gettext or one of its aliases, check if we have a literal
            called_args = []
            message_args = [node.args[index] for index in self.function_signatures[func_object.id]]
            if not isinstance(message_args, list):
                message_args = [message_args]
            has_complex_arg = False
            for arg in message_args:
                if isinstance(arg, _ast.Constant):
                    called_args.append(arg.value)
                else:
                    has_complex_arg = True
                    called_args.append(arg)
            call_struct = {
                "function": calling_name,
                "args": called_args
            }
            if has_complex_arg:
                self.expression_calls.append(call_struct)
            else:
                self.literal_calls.append(call_struct)
    
    def process_calls(self, source: str):
        for call in self.expression_calls:
            for index, call_arg in enumerate(call['args']):
                if not isinstance(call_arg, _ast.Constant):
                    source_call = ast.get_source_segment(source, call_arg)
                    call['args'][index] = source_call

def parse_folder(folder_path: str, alias: Dict[str, Union[str, None]]):
    folder_calls = {}
    for subdir, dirs, files in os.walk(folder_path):
        for filename in files:
            file_path = subdir + os.sep + filename
            if not filename.startswith('.') and file_path.endswith('.py'):
                file_calls = parse_file(file_path, alias)
                folder_calls[file_path] = file_calls
    return folder_calls


def parse_file(file_path: str, alias: Dict[str, Union[str, None]]):
    with open(file_path) as f:
        data = f.read()
        tree = ast.parse(data)
        treeVisitor = CheckTextVisitor(alias)
        treeVisitor.visit(tree)
        treeVisitor.process_calls(data)
        return {
            'literal_calls': treeVisitor.literal_calls,
            'complex_calls': treeVisitor.expression_calls
        }

def get_translation_object(file_path: str, domain: str, languages: List[str]):
    missing_translations = []
    translations = {}
    for lang in languages:
        try:
            translations[lang] = gettext.translation(domain, file_path, [lang], class_=CheckTextTranslation)
        except FileNotFoundError:
            missing_translations.append(lang)
    if missing_translations:
        print('Missing translations detected: ')
        for missing_translation in missing_translations:
            print('Translation {language} is missing'.format(language=missing_translation))
    return translations

def validate_translations(translators: Dict[str, gettext.translation], calls: Dict[str, Dict[str, List[Dict[str, Union[str, List[str]]]]]]):
    for lang, translator in translators.items():
        plural_options = predict_plurals(translator)
        for file_name, call_objs in calls.items():
            literal_calls = call_objs['literal_calls']
            for call in literal_calls:
                if call['function'] in ['gettext', 'dgettext', 'pgettext', 'dpgettext', 'lgettext', 'ldgettext']:
                    translation = getattr(translator, call['function'])(*call['args'])
                    if isinstance(translation, tuple):
                        print("msgid '{}' is missing a translation in language '{}'".format(translation[0], lang))
                else:
                    for plural_form in plural_options:
                        translation = getattr(translator, call['function'])(*call['args'], plural_form)
                        if isinstance(translation, tuple):
                            print("msgid '{}' is missing a translation in language '{}' for plural id {}".format(translation[0], lang, plural_options[plural_form]))

def predict_plurals(translator: gettext.translation) -> Dict[int, int]:
    # A survey of the reported plural for examples from 
    # 'http://docs.translatehouse.org/projects/localization-guide/en/latest/l10n/pluralforms.html'
    # Suggests that the number of required test ints is quite small
    # TODO: Verify coverage of these example
    test_ints = [*range(0, 30), 100, 101, 200, 201, 1000, 1001]
    options = {}
    result_indexes = set()
    for test_int in test_ints:
        result_index = translator.plural(test_int)
        if result_index not in result_indexes:
            result_indexes.add(result_index)
            options[test_int] = result_index
    return options

parser = argparse.ArgumentParser(description='pyCheckText Argument Parser')
parser.add_argument_group('File path')
parser.add_argument('--folder_path')
parser.add_argument('--file_path')
parser.add_argument_group('Validation options')
parser.add_argument('--alias', action='append', nargs='+', help="List of function aliases to include in search", metavar='<alias> <target>')
parser.add_argument('--translation_path', help='Path to the locale folder, match the path used to install the translation')
parser.add_argument('--domain', help="Translation domain")
parser.add_argument('--languages', action='append', nargs='+', help="List of languages to examine")
args = parser.parse_args()

alias_dict = {}
if args.alias is not None:
    assert len(args.alias[0]) % 2 == 0, "Provide aliases as 'alias' 'builtin', eg. '--alias _s gettext'"
    alias_list = args.alias[0]
    for alias, built_in in zip(alias_list[::2], alias_list[1::2]):
        alias_dict[alias] = built_in

if args.folder_path is not None:
    calls = parse_folder(args.folder_path, alias_dict)   
elif args.file_path is not None:
    calls = parse_file(args.file_path, alias_dict)
else:
    raise ValueError('No path provided, exiting...')

translation_objs = get_translation_object(args.translation_path, args.domain, args.languages[0])
validate_translations(translation_objs, calls)