from ast import literal_eval
from distutils.util import strtobool
from typing import Any
from urllib.parse import unquote

from parsimonious.grammar import Grammar
from parsimonious.nodes import NodeVisitor

cgrammar = Grammar(
    r"""
    text            = ( function / dict / namedlist / namedlist5 / include / include2 / pair / comment / emptyline )*

    pair            = key space+ numerical endline inlinecom*
    function        = key space+ key space+ numerical endline inlinecom*
    include         = key space+ key space+ includestr endline inlinecom*
    include2        = key space+ includestr inlinecom*
    dict            = key emptyline+ space* lbr dictmember* rbr inlinecom*
    namedlist       = key emptyline+ space* lpar listmember* rpar endline inlinecom*
    namedlist2      = key space+ lpar tensormember2* rpar
    namedlist3      = key space+ key space+ lpar namedlistmember* rpar
    namedlist4      = key space+ key space+ lpar tensormember2* rpar endline
    namedlist5      = number emptyline+ space* lpar listmember* rpar inlinecom*

    listvalue       = namedlist3 / namedlist2 / tensor / dict
    dictvalue       = namedlist / namedlist4 / function / pair / dict

    list            = lsqbr tensormember+ rsqbr
    tensor          = lpar tensormember2+ rpar space*
    tensormember    = space* num+ space*
    tensormember2   = space* numerical+ space*
    dictmember      = space* dictvalue+ space*
    listmember      = space* listvalue* space*
    namedlistmember = space* numerical* space*
    numerical       = tensor / list / expression / num
    num             = number / bool / string

    key             = ~"[#\w]+"
    space           = ~"\s"
    endline         = ";"
    emptyline       = "\n"
    comment         = singlecom / multicom / inlinecom
    multicom        = ~"/\*[\w\W]+\*/"
    singlecom       = ~"//[\w\W][^\n]+//"
    inlinecom       = ~"//[\w\W][^\n]+"

    number          = ~"[-+]?[\d]*\.?[\d]+(?:[eE][-+]?[\d]+)?"
    string          = ~"[\w\"\$\#\/.\d\-\#]+"
    includestr      = ~"\"[\w\W][^\n;]+\""
    expression      = number tensor
    bool            = true / false

    true            = "true"
    false           = "false"

    lbr             = "{"
    rbr             = "}"
    lsqbr           = "["
    rsqbr           = "]"
    lpar            = "("
    rpar            = ")"
    """
)


dictgrammar = Grammar(
    r"""
    text        = textmember+
    textmember  = dict / dim / include / includepair / funcpair / tensorpair / pair / namedlist / namedlist4
    funcpair    = key colon space function
    includepair = key colon space lsqbr key comma* space* includestr rsqbr comma* space*
    tensorpair  = key colon space tensor
    pair        = key colon space pairmember+ comma* space*
    include     = includekey colon space includestr+ comma* space*
    dict        = key colon space lbr dictmember* rbr comma* space*
    namedlist   = key colon space lsqbr listmember* rsqbr comma* space*
    namedlist2  = key2 colon space lsqbr pairmember+ rsqbr comma* space*
    namedlist3  = key2 colon space lsqbr namedlistmember+ rsqbr comma* space*
    namedlist4  = number colon space lsqbr listmember+ rsqbr comma* space*
    dim         = dimkey colon space lsqbr dimmember+ rsqbr comma* space*

    function    = lsqbr key comma space pairmember+ rsqbr comma* space*
    listdict    = lbr pair rbr comma* space*
    listdict2   = lbr namedlist2 rbr comma* space*
    listdict3   = lbr dict rbr comma* space*
    tensor      = lsqbr tenmember+ rsqbr comma* space*

    dimmember   = number comma* space*
    tenmember   = pairmember comma* space*
    namedlistmember = value comma* space*
    pairmember  = tensor / value
    dictmember  = funcpair / namedlist / namedlist2 / namedlist3 / tensorpair / pair  / dict / dim
    listmember  = tensor / function / listdict / listdict2 / listdict3

    value       = bool  / expression / number / string / letter

    space       = ~"\s"
    key         = ~"[#\w][^\:\,\s]+"
    key2        = key* space* key*


    number      = ~"[-+]?[\d]*\.?[\d]+(?:[eE][-+]?[\d]+)?"
    string      = ~"[\w\"\$][^\}\,\]\[]+"
    expression  = ~"[\d\w\"\(\)][^\}\{\,\]\[]+"
    includestr  = ~"\"[\w\W][^\[\]]+\""
    letter      = ~"[A-Za-z]"
    bool        = true / false

    true        = "True"
    false       = "False"
    dimkey      = "dimensions"
    includekey  = "#include"

    lbr         = "{"
    rbr         = "}"
    lsqbr       = "["
    rsqbr       = "]"
    colon       = ":"
    comma       = ","
    quote       = "'"
    """
)


class CVisitor(NodeVisitor):
    def visit_text(self, node, visited_children):
        """Returns the overall output."""
        output = {}
        for child in visited_children:
            res = child.pop()
            if type(res) == dict:
                output.update(**res)
        return output

    def visit_pair(self, node, visited_children):
        """Gets each key/value pair, returns a tuple."""
        key, _, value, *_ = visited_children
        return {key: value}

    def visit_function(self, node, visited_children):
        """Gets each key/value pair, returns a tuple."""
        key1, _, key2, _, value, *_ = visited_children
        return {key1: [key2, value]}

    def visit_include(self, node, visited_children):
        return self.visit_function(node, visited_children)

    def visit_include2(self, node, visited_children):
        return self.visit_pair(node, visited_children)

    def visit_dict(self, node, visited_children):
        key, _, _, _, dictmember, *_ = visited_children
        return {
            key: {
                dictkey: value
                for member in dictmember
                for dictkey, value in member.items()
            }
        }

    def visit_namedlist(self, node, visited_children):
        key, _, _, _, listmember, *_ = visited_children
        output = []
        for member in listmember:
            output += member
        return {key: output}

    def visit_namedlist2(self, node, visited_children):
        key, _, _, listmember, _ = visited_children
        return {key: listmember}

    def visit_namedlist3(self, node, visited_children):
        key1, _, key2, _, _, listmember, *_ = visited_children
        if type(listmember) == list:
            if len(listmember) == 1:
                listmember = listmember.pop()
        return {f"{key1} {key2}": listmember}

    def visit_namedlist4(self, node, visited_children):
        return self.visit_namedlist3(node, visited_children)

    def visit_namedlist5(self, node, visited_children):
        key, _, _, _, listmember, *_ = visited_children
        output = []
        for member in listmember:
            output += member
        return {str(key): output}

    def visit_list(self, node, visited_children):
        _, member, _ = visited_children
        return member

    def visit_tensor(self, node, visited_children):
        _, member, *_ = visited_children
        if isinstance(member, list):
            if len(member) == 1 and (
                (isinstance(member[0], list) and node.expr_name == "tensor")
                or node.expr_name != "tensor"
            ):
                member = member.pop()
        return member

    def visit_dictmember(self, node, visited_children):
        return self.visit_tensor(node, visited_children)

    def visit_listmember(self, node, visited_children):
        return self.visit_list(node, visited_children)

    def visit_namedlistmember(self, node, visited_children):
        return self.visit_list(node, visited_children)

    def visit_tensormember(self, node, visited_children):
        return self.visit_tensor(node, visited_children)

    def visit_tensormember2(self, node, visited_children):
        return self.visit_tensormember(node, visited_children)

    def visit_numerical(self, node, visited_children):
        if visited_children:
            val = visited_children.pop()
        else:
            val = None
        return val

    def visit_num(self, node, visited_children):
        return self.visit_numerical(node, visited_children)

    def visit_dictvalue(self, node, visited_children):
        return self.visit_numerical(node, visited_children)

    def visit_listvalue(self, node, visited_children):
        return self.visit_numerical(node, visited_children)

    def visit_key(self, node, visited_children):
        return self.visit_string(node, visited_children)

    def visit_string(self, node, visited_children):
        return node.text

    def visit_number(self, node, visited_children):
        return literal_eval(node.text)

    def visit_bool(self, node, visited_children):
        return bool(strtobool(node.text))

    def generic_visit(self, node, visited_children):
        """The generic visit method."""
        return visited_children or node.text

    def visit_comment(self, node, visited_children):
        pass

    def visit_emptyline(self, node, visited_children):
        pass

    def visit_expression(self, node, visited_children):
        number, tensor = visited_children
        return f"{number}({' '.join(tensor)})"


class DictVisitor(NodeVisitor):
    def visit_text(self, node, visited_children):
        """Returns the overall output."""
        return self._gather_members(visited_children, endswith="\n")

    def visit_textmember(self, node, visited_children):
        return visited_children.pop()

    def visit_funcpair(self, node, visited_children):
        return self.visit_pair(node, visited_children)

    def visit_tensorpair(self, node, visited_children):
        return self.visit_pair(node, visited_children)

    def visit_pair(self, node, visited_children):
        key, _, _, member, *_ = visited_children
        return f"{key}\t{self._gather_members(member)};\n"

    def visit_dict(self, node, visited_children):
        key, _, _, _, member, *_ = visited_children
        return f"{key}\n{{\n{self._gather_members(member)}\n}}\n"

    def visit_includepair(self, node, visited_children):
        key1, _, _, _, key2, _, _, string, *_ = visited_children
        return f"{key1} {key2} {string};"

    def visit_listdict(self, node, visited_children):
        _, member, *_ = visited_children
        return member.replace(";", "")

    def visit_listdict2(self, node, visited_children):
        return self.visit_listdict(node, visited_children)

    def visit_listdict3(self, node, visited_children):
        _, member, *_ = visited_children
        return member

    def visit_namedlist(self, node, visited_children):
        key, _, _, _, member, *_ = visited_children
        return f"{key}\n(\n{self._gather_members(member)}\n);\n"

    def visit_namedlist2(self, node, visited_children):
        return self.visit_namedlist(node, visited_children)

    def visit_namedlist3(self, node, visited_children):
        return self.visit_namedlist(node, visited_children)

    def visit_namedlist4(self, node, visited_children):
        key, _, _, _, member, *_ = visited_children
        return f"{key}\n(\n{self._gather_members(member)}\n)\n"

    def visit_dim(self, node, visited_children):
        key, _, _, _, member, *_ = visited_children
        return f"{key}\t[{self._gather_members(member, endswith=' ')}];\n"

    def visit_tensor(self, node, visited_children):
        _, member, *_ = visited_children
        return f"({self._gather_members(member)})"

    def visit_function(self, node, visited_chilrdren):
        _, key, _, _, member, *_ = visited_chilrdren
        return f"{key}\t{self._gather_members(member)}"

    def visit_dictmember(self, node, visited_children):
        member = f"\n{visited_children.pop()}"
        return member.replace("\n", "\n\t")

    def visit_pairmember(self, node, visited_children):
        return visited_children.pop()

    def visit_listmember(self, node, visited_children):
        member = f"\n{visited_children.pop()}"
        return member.replace("\n", "\n\t")

    def visit_dimmember(self, node, visited_children):
        member, *_ = visited_children
        return member

    def visit_namedlistmember(self, node, visited_children):
        return self.visit_tenmember(node, visited_children)

    def visit_tenmember(self, node, visited_children):
        return f"\t{self.visit_dimmember(node, visited_children)}"

    def visit_value(self, node, visited_children):
        return f"\t{visited_children.pop()}"

    def visit_bool(self, node, visited_children):
        return visited_children.pop().lower()

    def visit_key2(self, node, visited_children):
        key1, _, key2 = visited_children
        if type(key1) == list:
            key1 = key1.pop()
        if type(key2) == list:
            key2 = key2.pop()
        return f"{key1} {key2}"

    def visit_include(self, node, visited_children):
        key, _, _, member, *_ = visited_children
        return f"{key}\t{self._gather_members(member)}\n"

    def visit_key(self, node, visited_children):
        return node.text

    def generic_visit(self, node, visited_children):
        """The generic visit method."""
        return visited_children or node.text

    def _gather_members(self, members: list, endswith: str = None):
        content = str()
        for child in members:
            content += str(child)
            if endswith:
                content += endswith
        return content


def check_type(key: str):
    if key.isdigit() or key.isdecimal():
        return literal_eval(key)
    else:
        try:
            return bool(strtobool(key))
        except Exception:
            return key


def serialize(dictionary: dict):
    content = str(dictionary)
    content = content[1:-1].replace("'", str())
    res = dictgrammar.parse(content)
    n = DictVisitor()
    return n.visit(res)


def run_parser(filepath):
    with open(filepath, "r+") as file:
        content = file.read()
    res = cgrammar.parse(content)
    n = CVisitor()
    return n.visit(res)


def get_sub(parse_dict, key, next_key):
    if type(parse_dict) == list:
        if type(key) != int:
            raise TypeError(f"Index {key} for list {parse_dict} must be of type <int>.")
        try:
            return_list = parse_dict[key]
        except IndexError:
            parse_dict += [0] * (key + 1 - len(parse_dict))
        if type(next_key) != str:
            parse_dict[key] = []
        else:
            parse_dict[key] = {}
        return parse_dict[key]
    elif type(parse_dict) == dict:
        if key not in parse_dict.keys():
            if type(next_key) != str:
                parse_dict[key] = []
            else:
                parse_dict[key] = {}
        return parse_dict[key]


def insert(parse_dict, key, value):
    if type(parse_dict) == list:
        if type(key) != int:
            raise TypeError(f"Index {key} for list {parse_dict} must be of type <int>.")
        try:
            parse_dict[key] = value
        except IndexError:
            parse_dict += [0] * (key + 1 - len(parse_dict))
            parse_dict[key] = value
    elif type(parse_dict) == dict:
        parse_dict[key] = value


def replace(filepath: str, path: str, value: Any) -> str:
    content = run_parser(filepath)
    replaced = deep_replace(content, path, value)
    return serialize(replaced)


def deep_replace(content: dict, path: str, value: Any) -> dict:
    keys = [unquote(key) for key in path.split(".")]
    parse_dict = content
    for ikey in range(len(keys)):
        key = keys[ikey]
        key = check_type(key)
        if ikey == len(keys) - 1:
            insert(parse_dict, key, value)
        else:
            next_key = keys[ikey + 1]
            next_key = check_type(next_key)
            parse_dict = get_sub(parse_dict, key, next_key)
    return content
