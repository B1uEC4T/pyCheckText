import gettext
import _ast
import ast
from typing import Dict, Union
import argparse
import os
from pychecktext import teamcity, get_timestamp
import datetime

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
    if teamcity:
        timestamp = get_timestamp()
        print("##teamcity[message text='Checking tokens in folder {}' status='INFO' timestamp='{}'".format(folder_path, timestamp))
    else:
        print("Checking gettext tokens in folder '{}'".format(folder_path))
    folder_calls = {}
    for subdir, _, files in os.walk(folder_path):
        for filename in files:
            file_path = subdir + os.sep + filename
            if not filename.startswith('.') and file_path.endswith('.py'):
                file_calls = parse_file(file_path, alias)
                folder_calls[file_path] = file_calls
    return folder_calls

def parse_file(file_path: str, alias: Dict[str, Union[str, None]] = {}):
    if teamcity:
        timestamp = get_timestamp()
        print("##teamcity[message text='Checking tokens in file {}' status='INFO' timestamp='{}'".format(file_path, timestamp))
    else:
        print("Checking gettext tokens in file '{}'".format(file_path))
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