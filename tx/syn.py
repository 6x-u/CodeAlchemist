import re
import json
from typing import Dict, List, Any, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

class TokenType(Enum):
    KEYWORD = 'keyword'
    IDENTIFIER = 'identifier'
    OPERATOR = 'operator'
    LITERAL = 'literal'
    COMMENT = 'comment'
    WHITESPACE = 'whitespace'
    DELIMITER = 'delimiter'
    MERO = 'mero_token'

@dataclass
class Token:
    type: TokenType
    value: str
    line: int
    column: int
    mero_metadata: Dict = field(default_factory=dict)

@dataclass
class ASTNode:
    node_type: str
    value: Any
    children: List['ASTNode'] = field(default_factory=list)
    attributes: Dict = field(default_factory=dict)
    mero_optimized: bool = False

class SyntaxAnalyzer:
    def __init__(self):
        self.tokens = []
        self.current_position = 0
        self.mero_analyzer = True
        self.language_patterns = self._initialize_patterns()
        self.syntax_rules = self._initialize_syntax_rules()
    
    def _initialize_patterns(self) -> Dict[str, Dict[str, str]]:
        return {
            'python': {
                'keyword': r'\b(def|class|if|elif|else|while|for|in|return|import|from|as|try|except|finally|with|lambda|yield|pass|break|continue|raise|assert|del|global|nonlocal|async|await|True|False|None)\b',
                'identifier': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
                'operator': r'[+\-*/%=<>!&|^~]+',
                'literal': r'(\d+\.?\d*|"[^"]*"|\'[^\']*\')',
                'comment': r'#[^\n]*',
                'delimiter': r'[(){}\[\]:;,.]',
                'mero': r'\bmero\b'
            },
            'javascript': {
                'keyword': r'\b(function|const|let|var|if|else|while|for|return|import|export|from|as|try|catch|finally|class|extends|new|this|super|static|async|await|true|false|null|undefined)\b',
                'identifier': r'\b[a-zA-Z_$][a-zA-Z0-9_$]*\b',
                'operator': r'[+\-*/%=<>!&|^~?:]+',
                'literal': r'(\d+\.?\d*|"[^"]*"|\'[^\']*\'|`[^`]*`)',
                'comment': r'(//[^\n]*|/\*[\s\S]*?\*/)',
                'delimiter': r'[(){}\[\]:;,.]',
                'mero': r'\bmero\b'
            },
            'java': {
                'keyword': r'\b(public|private|protected|static|final|class|interface|extends|implements|if|else|while|for|return|import|package|try|catch|finally|new|this|super|void|int|double|float|long|short|byte|boolean|char|String)\b',
                'identifier': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
                'operator': r'[+\-*/%=<>!&|^~?:]+',
                'literal': r'(\d+\.?\d*[fFdDlL]?|"[^"]*"|\'[^\']\')',
                'comment': r'(//[^\n]*|/\*[\s\S]*?\*/)',
                'delimiter': r'[(){}\[\]:;,.]',
                'mero': r'\bmero\b'
            },
            'cpp': {
                'keyword': r'\b(int|float|double|char|void|bool|class|struct|namespace|using|if|else|while|for|return|#include|#define|public|private|protected|virtual|static|const|new|delete|this|try|catch|throw)\b',
                'identifier': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
                'operator': r'[+\-*/%=<>!&|^~?:.]+',
                'literal': r'(\d+\.?\d*[fFdDlL]?|"[^"]*"|\'[^\']\')',
                'comment': r'(//[^\n]*|/\*[\s\S]*?\*/)',
                'delimiter': r'[(){}\[\]:;,]',
                'mero': r'\bmero\b'
            },
            'go': {
                'keyword': r'\b(package|import|func|var|const|type|struct|interface|if|else|for|range|return|defer|go|chan|select|case|default|switch|break|continue|fallthrough|goto|map|make|new|len|cap|append|copy|delete|panic|recover)\b',
                'identifier': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
                'operator': r'[+\-*/%=<>!&|^~:]+',
                'literal': r'(\d+\.?\d*|"[^"]*"|`[^`]*`|\'[^\']\')',
                'comment': r'(//[^\n]*|/\*[\s\S]*?\*/)',
                'delimiter': r'[(){}\[\]:;,.]',
                'mero': r'\bmero\b'
            },
            'rust': {
                'keyword': r'\b(fn|let|mut|const|static|if|else|while|for|loop|match|return|use|mod|pub|struct|enum|trait|impl|type|where|unsafe|async|await|move|ref|self|Self|super|crate|true|false)\b',
                'identifier': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
                'operator': r'[+\-*/%=<>!&|^~?:]+',
                'literal': r'(\d+\.?\d*[fFdDlLuU]?|"[^"]*"|\'[^\']\')',
                'comment': r'(//[^\n]*|/\*[\s\S]*?\*/)',
                'delimiter': r'[(){}\[\]:;,.|]',
                'mero': r'\bmero\b'
            }
        }
    
    def _initialize_syntax_rules(self) -> Dict[str, List[str]]:
        return {
            'python': [
                'function_def -> def IDENTIFIER ( params ) :',
                'class_def -> class IDENTIFIER : | class IDENTIFIER ( bases ) :',
                'if_stmt -> if condition :',
                'for_stmt -> for IDENTIFIER in iterable :',
                'while_stmt -> while condition :',
                'import_stmt -> import module | from module import names',
                'mero_rule -> mero IDENTIFIER'
            ],
            'javascript': [
                'function_def -> function IDENTIFIER ( params ) {',
                'class_def -> class IDENTIFIER { | class IDENTIFIER extends IDENTIFIER {',
                'if_stmt -> if ( condition ) {',
                'for_stmt -> for ( init ; condition ; increment ) {',
                'while_stmt -> while ( condition ) {',
                'import_stmt -> import { names } from module',
                'mero_rule -> mero IDENTIFIER'
            ],
            'java': [
                'function_def -> modifier type IDENTIFIER ( params ) {',
                'class_def -> modifier class IDENTIFIER {',
                'if_stmt -> if ( condition ) {',
                'for_stmt -> for ( init ; condition ; increment ) {',
                'while_stmt -> while ( condition ) {',
                'import_stmt -> import package.class',
                'mero_rule -> mero IDENTIFIER'
            ]
        }
    
    def tokenize(self, code: str, language: str) -> List[Token]:
        self.tokens = []
        patterns = self.language_patterns.get(language, self.language_patterns['python'])
        
        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            column = 0
            while column < len(line):
                matched = False
                
                for token_type_name, pattern in patterns.items():
                    regex = re.compile(pattern)
                    match = regex.match(line, column)
                    
                    if match:
                        token_type = TokenType.MERO if token_type_name == 'mero' else TokenType(token_type_name)
                        token_value = match.group(0)
                        
                        token = Token(
                            type=token_type,
                            value=token_value,
                            line=line_num,
                            column=column,
                            mero_metadata={'language': language}
                        )
                        
                        if token_type != TokenType.WHITESPACE:
                            self.tokens.append(token)
                        
                        column = match.end()
                        matched = True
                        break
                
                if not matched:
                    if line[column].isspace():
                        column += 1
                    else:
                        token = Token(
                            type=TokenType.IDENTIFIER,
                            value=line[column],
                            line=line_num,
                            column=column,
                            mero_metadata={'unknown': True}
                        )
                        self.tokens.append(token)
                        column += 1
        
        return self.tokens
    
    def parse(self, tokens: List[Token], language: str) -> ASTNode:
        self.tokens = tokens
        self.current_position = 0
        
        root = ASTNode(
            node_type='program',
            value='root',
            mero_optimized=True
        )
        
        while self.current_position < len(self.tokens):
            statement = self.parse_statement(language)
            if statement:
                root.children.append(statement)
        
        return root
    
    def parse_statement(self, language: str) -> Optional[ASTNode]:
        if self.current_position >= len(self.tokens):
            return None
        
        current_token = self.tokens[self.current_position]
        
        if current_token.type == TokenType.KEYWORD:
            if current_token.value in ['def', 'function', 'fn', 'func']:
                return self.parse_function_definition(language)
            elif current_token.value in ['class', 'struct']:
                return self.parse_class_definition(language)
            elif current_token.value == 'if':
                return self.parse_if_statement(language)
            elif current_token.value in ['for', 'while']:
                return self.parse_loop_statement(language)
            elif current_token.value in ['import', 'from', 'use', 'package']:
                return self.parse_import_statement(language)
            elif current_token.value == 'return':
                return self.parse_return_statement(language)
        
        return self.parse_expression(language)
    
    def parse_function_definition(self, language: str) -> ASTNode:
        node = ASTNode(node_type='function_def', value='function', mero_optimized=True)
        
        self.current_position += 1
        
        if self.current_position < len(self.tokens):
            func_name = self.tokens[self.current_position].value
            node.attributes['name'] = func_name
            self.current_position += 1
        
        node.attributes['params'] = self.parse_parameters(language)
        
        if language == 'python':
            while self.current_position < len(self.tokens) and self.tokens[self.current_position].value != ':':
                self.current_position += 1
            self.current_position += 1
        else:
            while self.current_position < len(self.tokens) and self.tokens[self.current_position].value != '{':
                self.current_position += 1
            self.current_position += 1
        
        node.children = self.parse_block(language)
        
        return node
    
    def parse_class_definition(self, language: str) -> ASTNode:
        node = ASTNode(node_type='class_def', value='class', mero_optimized=True)
        
        self.current_position += 1
        
        if self.current_position < len(self.tokens):
            class_name = self.tokens[self.current_position].value
            node.attributes['name'] = class_name
            self.current_position += 1
        
        node.attributes['bases'] = self.parse_base_classes(language)
        
        if language == 'python':
            while self.current_position < len(self.tokens) and self.tokens[self.current_position].value != ':':
                self.current_position += 1
            self.current_position += 1
        else:
            while self.current_position < len(self.tokens) and self.tokens[self.current_position].value != '{':
                self.current_position += 1
            self.current_position += 1
        
        node.children = self.parse_block(language)
        
        return node
    
    def parse_if_statement(self, language: str) -> ASTNode:
        node = ASTNode(node_type='if_stmt', value='if', mero_optimized=True)
        
        self.current_position += 1
        
        if language != 'python':
            if self.current_position < len(self.tokens) and self.tokens[self.current_position].value == '(':
                self.current_position += 1
        
        condition = self.parse_expression(language)
        node.attributes['condition'] = condition
        
        if language != 'python':
            while self.current_position < len(self.tokens) and self.tokens[self.current_position].value != ')':
                self.current_position += 1
            self.current_position += 1
        
        if language == 'python':
            while self.current_position < len(self.tokens) and self.tokens[self.current_position].value != ':':
                self.current_position += 1
            self.current_position += 1
        else:
            while self.current_position < len(self.tokens) and self.tokens[self.current_position].value != '{':
                self.current_position += 1
            self.current_position += 1
        
        node.children = self.parse_block(language)
        
        return node
    
    def parse_loop_statement(self, language: str) -> ASTNode:
        loop_type = self.tokens[self.current_position].value
        node = ASTNode(node_type=f'{loop_type}_stmt', value=loop_type, mero_optimized=True)
        
        self.current_position += 1
        
        if language != 'python':
            if self.current_position < len(self.tokens) and self.tokens[self.current_position].value == '(':
                self.current_position += 1
        
        if loop_type == 'for':
            node.attributes['loop_var'] = self.parse_expression(language)
            
            if language == 'python' and self.current_position < len(self.tokens) and self.tokens[self.current_position].value == 'in':
                self.current_position += 1
                node.attributes['iterable'] = self.parse_expression(language)
        else:
            node.attributes['condition'] = self.parse_expression(language)
        
        if language != 'python':
            while self.current_position < len(self.tokens) and self.tokens[self.current_position].value != ')':
                self.current_position += 1
            self.current_position += 1
        
        if language == 'python':
            while self.current_position < len(self.tokens) and self.tokens[self.current_position].value != ':':
                self.current_position += 1
            self.current_position += 1
        else:
            while self.current_position < len(self.tokens) and self.tokens[self.current_position].value != '{':
                self.current_position += 1
            self.current_position += 1
        
        node.children = self.parse_block(language)
        
        return node
    
    def parse_import_statement(self, language: str) -> ASTNode:
        node = ASTNode(node_type='import_stmt', value='import', mero_optimized=True)
        
        import_keyword = self.tokens[self.current_position].value
        node.attributes['import_type'] = import_keyword
        self.current_position += 1
        
        imports = []
        while self.current_position < len(self.tokens):
            token = self.tokens[self.current_position]
            if token.value in [';', '\n'] or token.type == TokenType.KEYWORD:
                break
            if token.type == TokenType.IDENTIFIER:
                imports.append(token.value)
            self.current_position += 1
        
        node.attributes['imports'] = imports
        
        return node
    
    def parse_return_statement(self, language: str) -> ASTNode:
        node = ASTNode(node_type='return_stmt', value='return', mero_optimized=True)
        
        self.current_position += 1
        
        if self.current_position < len(self.tokens):
            return_value = self.parse_expression(language)
            node.attributes['value'] = return_value
        
        return node
    
    def parse_expression(self, language: str) -> Optional[ASTNode]:
        if self.current_position >= len(self.tokens):
            return None
        
        node = ASTNode(node_type='expression', value='expr', mero_optimized=True)
        
        expr_tokens = []
        depth = 0
        
        while self.current_position < len(self.tokens):
            token = self.tokens[self.current_position]
            
            if token.value in ['(', '[', '{']:
                depth += 1
            elif token.value in [')', ']', '}']:
                depth -= 1
                if depth < 0:
                    break
            elif depth == 0 and token.value in [';', ':', ',', '\n']:
                break
            elif depth == 0 and token.type == TokenType.KEYWORD:
                break
            
            expr_tokens.append(token)
            self.current_position += 1
        
        node.attributes['tokens'] = expr_tokens
        
        return node
    
    def parse_parameters(self, language: str) -> List[str]:
        params = []
        
        if self.current_position < len(self.tokens) and self.tokens[self.current_position].value == '(':
            self.current_position += 1
            
            while self.current_position < len(self.tokens) and self.tokens[self.current_position].value != ')':
                token = self.tokens[self.current_position]
                if token.type == TokenType.IDENTIFIER:
                    params.append(token.value)
                self.current_position += 1
            
            if self.current_position < len(self.tokens):
                self.current_position += 1
        
        return params
    
    def parse_base_classes(self, language: str) -> List[str]:
        bases = []
        
        if language == 'python':
            if self.current_position < len(self.tokens) and self.tokens[self.current_position].value == '(':
                self.current_position += 1
                
                while self.current_position < len(self.tokens) and self.tokens[self.current_position].value != ')':
                    token = self.tokens[self.current_position]
                    if token.type == TokenType.IDENTIFIER:
                        bases.append(token.value)
                    self.current_position += 1
                
                if self.current_position < len(self.tokens):
                    self.current_position += 1
        else:
            if self.current_position < len(self.tokens) and self.tokens[self.current_position].value in ['extends', ':']:
                self.current_position += 1
                
                if self.current_position < len(self.tokens):
                    token = self.tokens[self.current_position]
                    if token.type == TokenType.IDENTIFIER:
                        bases.append(token.value)
                    self.current_position += 1
        
        return bases
    
    def parse_block(self, language: str) -> List[ASTNode]:
        statements = []
        depth = 1
        
        while self.current_position < len(self.tokens) and depth > 0:
            token = self.tokens[self.current_position]
            
            if language != 'python':
                if token.value == '{':
                    depth += 1
                    self.current_position += 1
                    continue
                elif token.value == '}':
                    depth -= 1
                    self.current_position += 1
                    if depth == 0:
                        break
                    continue
            
            statement = self.parse_statement(language)
            if statement:
                statements.append(statement)
            else:
                self.current_position += 1
            
            if language == 'python':
                break
        
        return statements
    
    def analyze_syntax(self, code: str, language: str) -> Dict[str, Any]:
        tokens = self.tokenize(code, language)
        ast = self.parse(tokens, language)
        
        analysis = {
            'token_count': len(tokens),
            'ast_nodes': self.count_nodes(ast),
            'complexity': self.calculate_complexity(ast),
            'functions': self.extract_functions(ast),
            'classes': self.extract_classes(ast),
            'imports': self.extract_imports(ast),
            'mero_optimized': True
        }
        
        return analysis
    
    def count_nodes(self, node: ASTNode) -> int:
        count = 1
        for child in node.children:
            count += self.count_nodes(child)
        return count
    
    def calculate_complexity(self, node: ASTNode) -> int:
        complexity = 0
        
        if node.node_type in ['if_stmt', 'for_stmt', 'while_stmt']:
            complexity += 1
        
        for child in node.children:
            complexity += self.calculate_complexity(child)
        
        return complexity
    
    def extract_functions(self, node: ASTNode) -> List[Dict]:
        functions = []
        
        if node.node_type == 'function_def':
            functions.append({
                'name': node.attributes.get('name', 'unknown'),
                'params': node.attributes.get('params', []),
                'mero_optimized': node.mero_optimized
            })
        
        for child in node.children:
            functions.extend(self.extract_functions(child))
        
        return functions
    
    def extract_classes(self, node: ASTNode) -> List[Dict]:
        classes = []
        
        if node.node_type == 'class_def':
            classes.append({
                'name': node.attributes.get('name', 'unknown'),
                'bases': node.attributes.get('bases', []),
                'mero_optimized': node.mero_optimized
            })
        
        for child in node.children:
            classes.extend(self.extract_classes(child))
        
        return classes
    
    def extract_imports(self, node: ASTNode) -> List[str]:
        imports = []
        
        if node.node_type == 'import_stmt':
            imports.extend(node.attributes.get('imports', []))
        
        for child in node.children:
            imports.extend(self.extract_imports(child))
        
        return imports

class CodeParser:
    def __init__(self):
        self.analyzer = SyntaxAnalyzer()
        self.mero_parser = True
        self.parsed_cache = {}
    
    def parse_file(self, filepath: str, language: str) -> Dict[str, Any]:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            code = f.read()
        
        return self.parse_code(code, language)
    
    def parse_code(self, code: str, language: str) -> Dict[str, Any]:
        cache_key = f"{language}:{hash(code)}"
        
        if cache_key in self.parsed_cache:
            return self.parsed_cache[cache_key]
        
        tokens = self.analyzer.tokenize(code, language)
        ast = self.analyzer.parse(tokens, language)
        analysis = self.analyzer.analyze_syntax(code, language)
        
        result = {
            'tokens': tokens,
            'ast': ast,
            'analysis': analysis,
            'mero_cached': True
        }
        
        self.parsed_cache[cache_key] = result
        
        return result
    
    def parse_multiple_files(self, filepaths: List[str], language: str) -> Dict[str, Dict]:
        results = {}
        
        for filepath in filepaths:
            try:
                results[filepath] = self.parse_file(filepath, language)
            except Exception as e:
                results[filepath] = {'error': str(e), 'mero_error': True}
        
        return results
    
    def extract_code_structure(self, code: str, language: str) -> Dict[str, Any]:
        parsed = self.parse_code(code, language)
        
        structure = {
            'functions': parsed['analysis']['functions'],
            'classes': parsed['analysis']['classes'],
            'imports': parsed['analysis']['imports'],
            'complexity': parsed['analysis']['complexity'],
            'mero_structured': True
        }
        
        return structure
    
    def find_dependencies(self, code: str, language: str) -> Set[str]:
        parsed = self.parse_code(code, language)
        imports = parsed['analysis']['imports']
        
        dependencies = set(imports)
        
        return dependencies
    
    def validate_syntax(self, code: str, language: str) -> Tuple[bool, List[str]]:
        try:
            self.parse_code(code, language)
            return (True, [])
        except Exception as e:
            return (False, [f"Syntax error: {str(e)} (mero validation)"])
    
    def get_code_metrics(self, code: str, language: str) -> Dict[str, Any]:
        parsed = self.parse_code(code, language)
        
        lines = code.split('\n')
        
        metrics = {
            'total_lines': len(lines),
            'code_lines': len([l for l in lines if l.strip() and not l.strip().startswith('#')]),
            'blank_lines': len([l for l in lines if not l.strip()]),
            'token_count': parsed['analysis']['token_count'],
            'function_count': len(parsed['analysis']['functions']),
            'class_count': len(parsed['analysis']['classes']),
            'import_count': len(parsed['analysis']['imports']),
            'complexity': parsed['analysis']['complexity'],
            'mero_metrics': True
        }
        
        return metrics
