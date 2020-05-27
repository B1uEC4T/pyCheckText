import argparse
import sys
sys.path.extend('..')
from pychecktext import teamcity, get_timestamp
from pychecktext import checktext_parser, validator

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

if teamcity:
    timestamp = get_timestamp()
    print("##teamcity[testSuiteStarted name='checkGettextTokens' timestamp='{}'".format(timestamp))
else:
    print("Validating gettext tokens")
if args.folder_path is not None:
    calls = checktext_parser.parse_folder(args.folder_path, alias_dict)   
elif args.file_path is not None:
    calls = checktext_parser.parse_file(args.file_path, alias_dict)
else:
    raise ValueError('No path provided, exiting...')

translation_objs = validator.get_translation_object(args.translation_path, args.domain, args.languages[0])
validator.validate_translations(translation_objs, calls)
