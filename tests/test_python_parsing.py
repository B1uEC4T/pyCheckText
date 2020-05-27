import sys
import pytest
import os
sys.path.extend('../../')
from pychecktext.checktext_parser import parse_file

# test one isntance of each named call

calls = [
    ("dgettext('test', 'test.single')", "dgettext", ["test", "test.single"]),
    ("dngettext('test', 'test.single', 'test.plural', 1)", "dngettext", ["test", "test.single", "test.plural"]),
    ("dnpgettext('test', 'test_context', 'test.single', 'test.plural', 1)", "dnpgettext", ["test", "test_context", "test.single", "test.plural"]),
    ("dpgettext('test', 'test_context', 'test.single')", "dpgettext", ["test", "test_context", "test.single"]),
    ("gettext('test.single')", "gettext", ["test.single"]),
    ("ldgettext('test', 'test.single')", "ldgettext", ["test", "test.single"]),
    ("ldngettext('test', 'test.single', 'test.plural', 1)", "ldngettext", ["test", "test.single", "test.plural"]),
    ("lgettext('test.single')", "lgettext", ["test.single"]),
    ("lngettext('test.single', 'test.plural', 1)", "lngettext", ["test.single", "test.plural"]),
    ("ngettext('test.single', 'test.plural', 1)", "ngettext", ["test.single", "test.plural"]),
    ("npgettext('test_context', 'test.single', 'test.plural', 1)", "npgettext", ["test_context", "test.single", "test.plural"]),
    ("pgettext('test_context', 'test.single')", "pgettext", ["test_context", "test.single"])
]

plural_rules = {
    'en': {1: 0, 2: 1},
    'ar': {0: 0, 1: 1, 2: 2, 4: 3, 110: 4, 114: 5},
    'ay': {1: 0}
}

expected_translations = {
    'test.single': 'singular',
    'test.plural': 'plural'
}

@pytest.fixture
def cleanup_fixture():
    yield
    try:
        os.remove('./tests/test_module/test_file.py')
    except OSError:
        pass

@pytest.mark.parametrize("call_str, call_name, expected", calls)
def test_single_call(cleanup_fixture, call_str, call_name, expected):
    with open('./tests/test_artifacts/single_call_template.py', 'r') as f:
        test_file = f.readlines()
        for line_no, line in enumerate(test_file):
            test_file[line_no] = line.replace('{call}', call_str)
    with open('./tests/test_module/test_file.py', 'w') as f:
        f.writelines(test_file)

    calls = parse_file('./tests/test_module/test_file.py')
    assert len(calls['literal_calls']) == 1
    result = calls['literal_calls'][0]
    assert result['function'] == call_name
    assert result['args'] == expected

@pytest.mark.parametrize("call_str, call_name, expected", calls)
def test_alias_call(cleanup_fixture, call_str, call_name, expected):
    import string
    import random
    with open('./tests/test_artifacts/single_call_template.py', 'r') as f:
        random = ''.join(random.choice(string.ascii_letters) for _ in range(6))
        alias = {random: call_name}
        call_str = call_str.replace(call_name, random)
        call_name = random
        test_file = f.readlines()
        for line_no, line in enumerate(test_file):
            test_file[line_no] = line.replace('{call}', call_str)
    with open('./tests/test_module/test_file.py', 'w') as f:
        f.writelines(test_file)

    calls = parse_file('./tests/test_module/test_file.py', alias=alias)
    assert len(calls['literal_calls']) == 1
    result = calls['literal_calls'][0]
    assert result['function'] == alias[call_name]
    assert result['args'] == expected

@pytest.mark.parametrize("call_str, call_name, expected", calls)
def test_multiple_call(cleanup_fixture, call_str, call_name, expected):
    with open('./tests/test_artifacts/multiplicate_call_template.py', 'r') as f:
        test_file = f.readlines()
        for line_no, line in enumerate(test_file):
            test_file[line_no] = line.replace('{call}', call_str)
    with open('./tests/test_module/test_file.py', 'w') as f:
        f.writelines(test_file)

    calls = parse_file('./tests/test_module/test_file.py')
    assert len(calls['literal_calls']) == 4
    for call in calls['literal_calls']:
        assert call['function'] == call_name
        assert call['args'] == expected

def test_multiple_tokens(cleanup_fixture):
    import re
    from operator import itemgetter
    with open('./tests/test_artifacts/multiple_token_template.py', 'r') as f:
        test_file = f.readlines()
        for line_no, line in enumerate(test_file):
            call_token = re.search(r"{call_([\d])}", line)
            if call_token:
                test_file[line_no] = line.replace(call_token.group(0), calls[int(call_token.group(1))][0])
    with open('./tests/test_module/test_file.py', 'w') as f:
        f.writelines(test_file)

    parsed_calls = parse_file('./tests/test_module/test_file.py')
    assert len(parsed_calls['literal_calls']) == 10
    for call in parsed_calls['literal_calls']:
        assert call['function'] in [function[1] for function in calls]
        current_call = list(map(itemgetter(1), calls)).index(call['function'])
        assert call['args'] == calls[current_call][2]

# test invalid python

# test complex call