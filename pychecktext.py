import ast
import _ast
import argparse
from typing import Union, List, Dict

class CheckTextVisitor(ast.NodeVisitor):
    def __init__(self, aliases: Dict[str, str] = {}):
        self.literal_calls = []
        self.expression_calls = []
        self.function_signatures = {
            "dgettext": [1],
            "dngettext": [1,2],
            "dnpgettext": [2,3],
            "dpgettext": [2],
            "gettext": [0],
            "ldgettext": [1],
            "ldngettext": [1,2],
            "lgettext": [0],
            "lngettext": [0,1],
            "ngettext": [0,1],
            "npgettext": [1,2],
            "pgettext": [1]}
        for alias, source in aliases.items():
            self.function_signatures[alias] = self.function_signatures[source]
    
    def visit_Call(self, node: _ast.Call):
        func_object = node.func
        if hasattr(node, 'args'):
            for arg in node.args:
                if isinstance(arg, _ast.Call):
                    self.visit_Call(arg)
        if hasattr(func_object, 'id') and func_object.id in self.function_signatures:
            # A call to gettext or one of its aliases, check if we have a literal
            called_args = []
            message_args = [node.args[index] for index in self.function_signatures[func_object.id]]
            if not isinstance(message_args, list):
                message_args = [message_args]
            has_expr_arg = False
            for arg in message_args:
                if isinstance(arg, _ast.Constant):
                    called_args.append(arg.value)
                elif isinstance(arg, _ast.Expr):
                    has_expr_arg = True
                    called_args.append(arg)
                elif isinstance(arg, _ast.BinOp):
                    has_expr_arg = True
                    called_args.append(arg)
            call_struct = {
                "function": func_object.id,
                "args": called_args
            }
            if has_expr_arg:
                self.expression_calls.append(call_struct)
            else:
                self.literal_calls.append(call_struct)
    
    def process_calls(self, source: str):
        for call in self.expression_calls:
            for call_arg in call['args']:
                if not isinstance(call_arg, _ast.Constant):
                    source_call = ast.get_source_segment(source, call_arg)
                    call_arg = source_call

def parse_folder(folder_path: str, alias: Union[None, List[str]]):
    pass


def parse_file(file_path: str, alias: Dict[str, Union[str, None]]):
    with open(file_path) as f:
        data = f.read()
        tree = ast.parse(data)
        treeVisitor = CheckTextVisitor(alias)
        treeVisitor.visit(tree)
        treeVisitor.process_calls(data)
        print(treeVisitor.literal_calls)
        print(treeVisitor.expression_calls)

print(str(min(range(1,10))))

parser = argparse.ArgumentParser(description='pyCheckText Argument Parser')
parser.add_argument_group('File path')
parser.add_argument('--folder_path')
parser.add_argument('--file_path')
parser.add_argument_group('Validation options')
parser.add_argument('--alias', action='append', nargs='+')
args = parser.parse_args()

alias_dict = {}
if args.alias is not None:
    assert len(args.alias[0]) % 2 == 0, "Provide aliases as 'alias' 'builtin', eg. '--alias _s gettext'"
    alias_list = args.alias[0]
    for alias, built_in in zip(alias_list[::2], alias_list[1::2]):
        alias_dict[alias] = built_in

if args.folder_path is not None:
    parse_folder(args.folder_path, alias_dict)
elif args.file_path is not None:
    parse_file(args.file_path, alias_dict)
else:
    raise ValueError('No path provided, exiting...')
