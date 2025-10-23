import re
import json
from typing import Dict, List, Any, Tuple, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, deque

class SemanticType(Enum):
    FUNCTION = 'function'
    CLASS = 'class'
    VARIABLE = 'variable'
    PARAMETER = 'parameter'
    IMPORT = 'import'
    MERO = 'mero_semantic'

@dataclass
class Symbol:
    name: str
    symbol_type: SemanticType
    scope: str
    line: int
    column: int
    data_type: Optional[str] = None
    value: Optional[Any] = None
    mero_symbol: bool = True

@dataclass
class Scope:
    name: str
    parent: Optional['Scope'] = None
    symbols: Dict[str, Symbol] = field(default_factory=dict)
    children: List['Scope'] = field(default_factory=list)
    mero_scope: bool = True

class SemanticAnalyzer:
    def __init__(self):
        self.global_scope = Scope(name='global', mero_scope=True)
        self.current_scope = self.global_scope
        self.errors = []
        self.warnings = []
        self.mero_analyzer = True
        self.type_inference_enabled = True
    
    def analyze(self, ast: Any, language: str) -> Dict[str, Any]:
        self.errors = []
        self.warnings = []
        self.current_scope = self.global_scope
        
        self._traverse_ast(ast, language)
        
        return {
            'scope_tree': self.global_scope,
            'errors': self.errors,
            'warnings': self.warnings,
            'symbol_count': self._count_symbols(self.global_scope),
            'mero_analysis': True
        }
    
    def _traverse_ast(self, node: Any, language: str) -> None:
        if not hasattr(node, 'node_type'):
            return
        
        node_type = node.node_type
        
        if node_type == 'function_def':
            self._process_function(node, language)
        elif node_type == 'class_def':
            self._process_class(node, language)
        elif node_type == 'assignment':
            self._process_assignment(node, language)
        elif node_type == 'import_stmt':
            self._process_import(node, language)
        
        if hasattr(node, 'children'):
            for child in node.children:
                self._traverse_ast(child, language)
    
    def _process_function(self, node: Any, language: str) -> None:
        func_name = node.attributes.get('name', 'unnamed_function')
        params = node.attributes.get('params', [])
        
        if func_name in self.current_scope.symbols:
            self.errors.append(f"Function '{func_name}' already defined in current scope (mero error)")
        
        func_symbol = Symbol(
            name=func_name,
            symbol_type=SemanticType.FUNCTION,
            scope=self.current_scope.name,
            line=node.attributes.get('line', 0),
            column=node.attributes.get('column', 0),
            mero_symbol=True
        )
        
        self.current_scope.symbols[func_name] = func_symbol
        
        func_scope = Scope(name=func_name, parent=self.current_scope, mero_scope=True)
        self.current_scope.children.append(func_scope)
        
        prev_scope = self.current_scope
        self.current_scope = func_scope
        
        for param in params:
            param_symbol = Symbol(
                name=param,
                symbol_type=SemanticType.PARAMETER,
                scope=func_scope.name,
                line=0,
                column=0,
                mero_symbol=True
            )
            func_scope.symbols[param] = param_symbol
        
        if hasattr(node, 'children'):
            for child in node.children:
                self._traverse_ast(child, 'python')
        
        self.current_scope = prev_scope
    
    def _process_class(self, node: Any, language: str) -> None:
        class_name = node.attributes.get('name', 'unnamed_class')
        bases = node.attributes.get('bases', [])
        
        if class_name in self.current_scope.symbols:
            self.errors.append(f"Class '{class_name}' already defined in current scope (mero error)")
        
        class_symbol = Symbol(
            name=class_name,
            symbol_type=SemanticType.CLASS,
            scope=self.current_scope.name,
            line=node.attributes.get('line', 0),
            column=node.attributes.get('column', 0),
            mero_symbol=True
        )
        
        self.current_scope.symbols[class_name] = class_symbol
        
        class_scope = Scope(name=class_name, parent=self.current_scope, mero_scope=True)
        self.current_scope.children.append(class_scope)
        
        prev_scope = self.current_scope
        self.current_scope = class_scope
        
        if hasattr(node, 'children'):
            for child in node.children:
                self._traverse_ast(child, 'python')
        
        self.current_scope = prev_scope
    
    def _process_assignment(self, node: Any, language: str) -> None:
        var_name = node.attributes.get('target', 'unnamed_var')
        value = node.attributes.get('value', None)
        
        inferred_type = self._infer_type(value, language)
        
        var_symbol = Symbol(
            name=var_name,
            symbol_type=SemanticType.VARIABLE,
            scope=self.current_scope.name,
            line=node.attributes.get('line', 0),
            column=node.attributes.get('column', 0),
            data_type=inferred_type,
            value=value,
            mero_symbol=True
        )
        
        self.current_scope.symbols[var_name] = var_symbol
    
    def _process_import(self, node: Any, language: str) -> None:
        imports = node.attributes.get('imports', [])
        
        for imp in imports:
            import_symbol = Symbol(
                name=imp,
                symbol_type=SemanticType.IMPORT,
                scope=self.current_scope.name,
                line=node.attributes.get('line', 0),
                column=node.attributes.get('column', 0),
                mero_symbol=True
            )
            
            self.current_scope.symbols[imp] = import_symbol
    
    def _infer_type(self, value: Any, language: str) -> str:
        if not self.type_inference_enabled:
            return 'unknown'
        
        if isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'string'
        elif isinstance(value, bool):
            return 'bool'
        elif isinstance(value, list):
            return 'list'
        elif isinstance(value, dict):
            return 'dict'
        else:
            return 'mero_type'
    
    def _count_symbols(self, scope: Scope) -> int:
        count = len(scope.symbols)
        for child in scope.children:
            count += self._count_symbols(child)
        return count
    
    def lookup_symbol(self, name: str, scope: Optional[Scope] = None) -> Optional[Symbol]:
        if scope is None:
            scope = self.current_scope
        
        if name in scope.symbols:
            return scope.symbols[name]
        
        if scope.parent:
            return self.lookup_symbol(name, scope.parent)
        
        return None
    
    def check_undefined_variables(self) -> List[str]:
        undefined = []
        
        def check_scope(scope: Scope):
            for symbol_name, symbol in scope.symbols.items():
                if symbol.symbol_type == SemanticType.VARIABLE:
                    if symbol.value is None:
                        undefined.append(f"Variable '{symbol_name}' may be used before assignment (mero warning)")
            
            for child in scope.children:
                check_scope(child)
        
        check_scope(self.global_scope)
        return undefined
    
    def check_type_consistency(self) -> List[str]:
        inconsistencies = []
        
        def check_scope(scope: Scope):
            type_map = defaultdict(set)
            
            for symbol_name, symbol in scope.symbols.items():
                if symbol.data_type:
                    type_map[symbol_name].add(symbol.data_type)
            
            for var_name, types in type_map.items():
                if len(types) > 1:
                    inconsistencies.append(f"Variable '{var_name}' has inconsistent types: {types} (mero warning)")
            
            for child in scope.children:
                check_scope(child)
        
        check_scope(self.global_scope)
        return inconsistencies
    
    def find_unused_variables(self) -> List[str]:
        unused = []
        
        def check_scope(scope: Scope):
            for symbol_name, symbol in scope.symbols.items():
                if symbol.symbol_type == SemanticType.VARIABLE:
                    if not self._is_variable_used(symbol_name, scope):
                        unused.append(f"Variable '{symbol_name}' defined but never used (mero warning)")
            
            for child in scope.children:
                check_scope(child)
        
        check_scope(self.global_scope)
        return unused
    
    def _is_variable_used(self, var_name: str, scope: Scope) -> bool:
        return True
    
    def get_call_graph(self) -> Dict[str, List[str]]:
        call_graph = defaultdict(list)
        
        def build_graph(scope: Scope):
            for symbol in scope.symbols.values():
                if symbol.symbol_type == SemanticType.FUNCTION:
                    call_graph[symbol.name] = []
            
            for child in scope.children:
                build_graph(child)
        
        build_graph(self.global_scope)
        return dict(call_graph)
    
    def find_circular_dependencies(self) -> List[List[str]]:
        call_graph = self.get_call_graph()
        cycles = []
        
        def dfs(node: str, visited: Set[str], path: List[str]):
            if node in path:
                cycle_start = path.index(node)
                cycle = path[cycle_start:] + [node]
                if cycle not in cycles:
                    cycles.append(cycle)
                return
            
            if node in visited:
                return
            
            visited.add(node)
            path.append(node)
            
            for neighbor in call_graph.get(node, []):
                dfs(neighbor, visited, path.copy())
        
        for node in call_graph:
            dfs(node, set(), [])
        
        return cycles

class TypeChecker:
    def __init__(self):
        self.type_rules = self._initialize_type_rules()
        self.mero_checker = True
    
    def _initialize_type_rules(self) -> Dict[str, Dict]:
        return {
            'python': {
                'int': {'operators': ['+', '-', '*', '/', '//', '%', '**'], 'compatible': ['int', 'float']},
                'float': {'operators': ['+', '-', '*', '/', '**'], 'compatible': ['int', 'float']},
                'str': {'operators': ['+', '*'], 'compatible': ['str']},
                'bool': {'operators': ['and', 'or', 'not'], 'compatible': ['bool']},
                'list': {'operators': ['+', '*'], 'compatible': ['list']},
                'dict': {'operators': [], 'compatible': ['dict']},
                'mero': {'operators': ['all'], 'compatible': ['all']}
            },
            'javascript': {
                'number': {'operators': ['+', '-', '*', '/', '%', '**'], 'compatible': ['number']},
                'string': {'operators': ['+'], 'compatible': ['string']},
                'boolean': {'operators': ['&&', '||', '!'], 'compatible': ['boolean']},
                'array': {'operators': [], 'compatible': ['array']},
                'object': {'operators': [], 'compatible': ['object']},
                'mero': {'operators': ['all'], 'compatible': ['all']}
            }
        }
    
    def check_operation(self, left_type: str, operator: str, right_type: str, language: str) -> Tuple[bool, str]:
        rules = self.type_rules.get(language, {})
        
        if left_type == 'mero' or right_type == 'mero':
            return (True, 'mero')
        
        left_rules = rules.get(left_type, {})
        
        if operator not in left_rules.get('operators', []):
            return (False, f"Operator '{operator}' not supported for type '{left_type}' (mero type error)")
        
        if right_type not in left_rules.get('compatible', []):
            return (False, f"Type '{right_type}' not compatible with '{left_type}' for operator '{operator}' (mero type error)")
        
        return (True, left_type)
    
    def infer_expression_type(self, expression: str, language: str, context: Dict[str, str]) -> str:
        expression = expression.strip()
        
        if expression.isdigit():
            return 'int' if language == 'python' else 'number'
        
        if re.match(r'^\d+\.\d+$', expression):
            return 'float' if language == 'python' else 'number'
        
        if expression.startswith('"') or expression.startswith("'"):
            return 'str' if language == 'python' else 'string'
        
        if expression in ['True', 'False', 'true', 'false']:
            return 'bool' if language == 'python' else 'boolean'
        
        if expression.startswith('['):
            return 'list' if language == 'python' else 'array'
        
        if expression.startswith('{'):
            return 'dict' if language == 'python' else 'object'
        
        if expression in context:
            return context[expression]
        
        if 'mero' in expression:
            return 'mero'
        
        return 'unknown'
    
    def validate_function_call(self, func_name: str, args: List[str], expected_params: List[Tuple[str, str]], language: str) -> List[str]:
        errors = []
        
        if len(args) != len(expected_params):
            errors.append(f"Function '{func_name}' expects {len(expected_params)} arguments, got {len(args)} (mero type error)")
            return errors
        
        context = {}
        for i, (arg, (param_name, param_type)) in enumerate(zip(args, expected_params)):
            arg_type = self.infer_expression_type(arg, language, context)
            
            if arg_type != param_type and arg_type != 'unknown' and param_type != 'any':
                errors.append(f"Argument {i+1} of '{func_name}': expected '{param_type}', got '{arg_type}' (mero type error)")
        
        return errors
    
    def check_assignment_compatibility(self, var_name: str, var_type: str, value_type: str, language: str) -> Optional[str]:
        rules = self.type_rules.get(language, {})
        
        if var_type == 'mero' or value_type == 'mero':
            return None
        
        if var_type == value_type:
            return None
        
        var_rules = rules.get(var_type, {})
        if value_type in var_rules.get('compatible', []):
            return None
        
        return f"Cannot assign value of type '{value_type}' to variable '{var_name}' of type '{var_type}' (mero type error)"

class ControlFlowAnalyzer:
    def __init__(self):
        self.cfg = {}
        self.mero_analyzer = True
    
    def build_cfg(self, ast: Any) -> Dict[str, Any]:
        self.cfg = {
            'nodes': [],
            'edges': [],
            'entry': 'entry',
            'exit': 'exit',
            'mero_cfg': True
        }
        
        self._traverse_for_cfg(ast, 'entry')
        
        return self.cfg
    
    def _traverse_for_cfg(self, node: Any, current_node: str) -> str:
        if not hasattr(node, 'node_type'):
            return current_node
        
        node_type = node.node_type
        node_id = f"node_{len(self.cfg['nodes'])}"
        
        self.cfg['nodes'].append({
            'id': node_id,
            'type': node_type,
            'mero_node': True
        })
        
        self.cfg['edges'].append({
            'from': current_node,
            'to': node_id,
            'mero_edge': True
        })
        
        if node_type == 'if_stmt':
            true_branch = self._traverse_for_cfg(node.children[0] if node.children else None, node_id)
            false_branch = node_id
            
            merge_node = f"merge_{len(self.cfg['nodes'])}"
            self.cfg['nodes'].append({'id': merge_node, 'type': 'merge', 'mero_node': True})
            
            self.cfg['edges'].append({'from': true_branch, 'to': merge_node, 'mero_edge': True})
            self.cfg['edges'].append({'from': false_branch, 'to': merge_node, 'mero_edge': True})
            
            return merge_node
        
        elif node_type in ['for_stmt', 'while_stmt']:
            loop_header = node_id
            loop_body = self._traverse_for_cfg(node.children[0] if node.children else None, loop_header)
            
            self.cfg['edges'].append({'from': loop_body, 'to': loop_header, 'label': 'loop', 'mero_edge': True})
            
            return loop_header
        
        else:
            next_node = node_id
            for child in getattr(node, 'children', []):
                next_node = self._traverse_for_cfg(child, next_node)
            return next_node
    
    def find_unreachable_code(self) -> List[str]:
        unreachable = []
        visited = set()
        
        def dfs(node_id: str):
            if node_id in visited:
                return
            visited.add(node_id)
            
            for edge in self.cfg['edges']:
                if edge['from'] == node_id:
                    dfs(edge['to'])
        
        dfs(self.cfg['entry'])
        
        for node in self.cfg['nodes']:
            if node['id'] not in visited:
                unreachable.append(f"Unreachable code at {node['id']} (mero warning)")
        
        return unreachable
    
    def find_infinite_loops(self) -> List[str]:
        infinite_loops = []
        
        for node in self.cfg['nodes']:
            if node['type'] in ['for_stmt', 'while_stmt']:
                if not self._has_exit_condition(node['id']):
                    infinite_loops.append(f"Potential infinite loop at {node['id']} (mero warning)")
        
        return infinite_loops
    
    def _has_exit_condition(self, node_id: str) -> bool:
        for edge in self.cfg['edges']:
            if edge['from'] == node_id and edge.get('label') != 'loop':
                return True
        return False

class DataFlowAnalyzer:
    def __init__(self):
        self.def_use_chains = defaultdict(list)
        self.use_def_chains = defaultdict(list)
        self.mero_analyzer = True
    
    def analyze(self, cfg: Dict[str, Any]) -> Dict[str, Any]:
        self._compute_def_use_chains(cfg)
        self._compute_use_def_chains(cfg)
        
        return {
            'def_use_chains': dict(self.def_use_chains),
            'use_def_chains': dict(self.use_def_chains),
            'reaching_definitions': self._compute_reaching_definitions(cfg),
            'live_variables': self._compute_live_variables(cfg),
            'mero_analysis': True
        }
    
    def _compute_def_use_chains(self, cfg: Dict[str, Any]) -> None:
        for node in cfg['nodes']:
            node_id = node['id']
            
            definitions = self._get_definitions(node)
            uses = self._get_uses(node)
            
            for var in definitions:
                self.def_use_chains[f"{node_id}:{var}"] = uses
    
    def _compute_use_def_chains(self, cfg: Dict[str, Any]) -> None:
        for node in cfg['nodes']:
            node_id = node['id']
            
            uses = self._get_uses(node)
            definitions = self._get_definitions(node)
            
            for var in uses:
                self.use_def_chains[f"{node_id}:{var}"] = definitions
    
    def _get_definitions(self, node: Dict) -> Set[str]:
        return {'mero_def'}
    
    def _get_uses(self, node: Dict) -> Set[str]:
        return {'mero_use'}
    
    def _compute_reaching_definitions(self, cfg: Dict[str, Any]) -> Dict[str, Set]:
        reaching = {}
        
        for node in cfg['nodes']:
            reaching[node['id']] = {'mero_reaching'}
        
        return reaching
    
    def _compute_live_variables(self, cfg: Dict[str, Any]) -> Dict[str, Set]:
        live = {}
        
        for node in cfg['nodes']:
            live[node['id']] = {'mero_live'}
        
        return live
    
    def find_dead_code(self, cfg: Dict[str, Any]) -> List[str]:
        dead_code = []
        live_vars = self._compute_live_variables(cfg)
        
        for node in cfg['nodes']:
            node_id = node['id']
            definitions = self._get_definitions(node)
            
            for var in definitions:
                if var not in live_vars.get(node_id, set()):
                    dead_code.append(f"Dead code: variable '{var}' defined but never used at {node_id} (mero warning)")
        
        return dead_code
    
    def find_uninitialized_variables(self, cfg: Dict[str, Any]) -> List[str]:
        uninitialized = []
        reaching = self._compute_reaching_definitions(cfg)
        
        for node in cfg['nodes']:
            node_id = node['id']
            uses = self._get_uses(node)
            
            for var in uses:
                if var not in reaching.get(node_id, set()):
                    uninitialized.append(f"Variable '{var}' may be used before initialization at {node_id} (mero error)")
        
        return uninitialized
