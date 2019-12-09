#  Copyright (c) 2019 Seven Bridges. See LICENSE

from typing import List

from .basetype import CWLBaseType, MapSubjectPredicate, TypeCheck, Match
from .unknowntype import CWLUnknownType
from .anytype import CWLAnyType
from .namespacedtype import CWLNameSpacedType


def infer_type(node, allowed_types,
               key: str = None, map_sp: MapSubjectPredicate = None) -> CWLBaseType:
    type_check_results = check_types(node, allowed_types, key, map_sp)
    for tcr in type_check_results:
        if tcr.match == Match.Yes:
            res = tcr.cwl_type
            break
    else:
        for tcr in type_check_results:
            if tcr.match == Match.Maybe:
                res = tcr.cwl_type
                break
        else:
            if len(type_check_results) == 1:
                res = type_check_results[0].cwl_type
            else:
                res = CWLUnknownType(name="(unknown)",
                                     expected=[tr.cwl_type.name for tr in type_check_results])
    return res


def check_types(node, allowed_types, key, map_sp) -> List[TypeCheck]:

    type_check_results = []

    explicit_type = get_explicit_type_str(node, key, map_sp)

    if explicit_type is not None:
        if ":" in explicit_type:
            return [TypeCheck(CWLNameSpacedType(explicit_type))]

        for _type in allowed_types:
            if isinstance(_type, CWLAnyType):
                req_type = _type.if_you_can_be_anything_be_this_kind(explicit_type)
                if req_type is not None:
                    return [TypeCheck(req_type)]
                else:
                    return [TypeCheck(
                        CWLUnknownType(name=explicit_type,
                                       expected=_type.all_possible_type_names()),
                        match=Match.No)]

            if explicit_type == _type.name:
                return [TypeCheck(_type)]

        return [
            TypeCheck(CWLUnknownType(
                name=explicit_type,
                expected=[t.name for t in allowed_types]),
                match=Match.No)]

    for _type in allowed_types:
        if _type.name == 'null':
            if node is None:
                return [TypeCheck(CWLBaseType(name=_type))]
            else:
                type_check_results += [TypeCheck(CWLBaseType(name=_type), match=Match.No)]
                continue

        # string greedily matches Expression, so we have to take care of this ...
        if _type.name == "string":
            if node is None:
                return [TypeCheck(_type)]

            elif isinstance(node, str):
                type_check_results += [TypeCheck(_type, match=Match.Maybe)]

            else:
                type_check_results += [TypeCheck(_type, match=Match.No)]

            continue

        # For now, don't closely validate these base types
        if _type.name in ['boolean', 'int', 'long']:
            if node is None or isinstance(node, (str, bool, int)):
                return [TypeCheck(_type)]
            else:
                type_check_results += [TypeCheck(_type, match=Match.No)]
                continue

        check_result = _type.check(node, key, map_sp)
        if check_result.match == Match.Yes:
            return [check_result]

        type_check_results += [check_result]

    return type_check_results


def get_explicit_type_str(node, key: str, map_sp: MapSubjectPredicate):
    if map_sp is not None:
        if map_sp.subject == "class":
            return key
        else:
            return None
    elif isinstance(node, dict):
        return node.get("class")
    else:
        return None
