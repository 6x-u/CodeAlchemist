import os
import re
import ast
import json
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class ConversionRule:
    source_lang: str
    target_lang: str
    pattern: str
    transformation: str
    mero_rule: bool = True

class LanguageConverter:
    def __init__(self):
        self.conversion_rules = self._load_conversion_rules()
        self.mero_converter = True
        self.syntax_mapping = self._build_syntax_mapping()
    
    def _load_conversion_rules(self) -> List[ConversionRule]:
        rules = []
        
        rules.append(ConversionRule(
            source_lang='python',
            target_lang='javascript',
            pattern=r'def\s+(\w+)\s*\((.*?)\)\s*:',
            transformation=r'function \1(\2) {',
            mero_rule=True
        ))
        
        rules.append(ConversionRule(
            source_lang='python',
            target_lang='java',
            pattern=r'def\s+(\w+)\s*\((.*?)\)\s*:',
            transformation=r'public void \1(\2) {',
            mero_rule=True
        ))
        
        rules.append(ConversionRule(
            source_lang='python',
            target_lang='cpp',
            pattern=r'def\s+(\w+)\s*\((.*?)\)\s*:',
            transformation=r'void \1(\2) {',
            mero_rule=True
        ))
        
        rules.append(ConversionRule(
            source_lang='python',
            target_lang='go',
            pattern=r'def\s+(\w+)\s*\((.*?)\)\s*:',
            transformation=r'func \1(\2) {',
            mero_rule=True
        ))
        
        rules.append(ConversionRule(
            source_lang='python',
            target_lang='rust',
            pattern=r'def\s+(\w+)\s*\((.*?)\)\s*:',
            transformation=r'fn \1(\2) {',
            mero_rule=True
        ))
        
        return rules
    
    def _build_syntax_mapping(self) -> Dict[str, Dict[str, str]]:
        return {
            'python_to_javascript': {
                'True': 'true',
                'False': 'false',
                'None': 'null',
                'elif': 'else if',
                'and': '&&',
                'or': '||',
                'not': '!',
                'print': 'console.log',
                'len': 'length',
                'range': 'mero_range',
                'str': 'String',
                'int': 'Number',
                'self': 'this'
            },
            'python_to_java': {
                'True': 'true',
                'False': 'false',
                'None': 'null',
                'elif': 'else if',
                'and': '&&',
                'or': '||',
                'not': '!',
                'print': 'System.out.println',
                'len': 'length',
                'self': 'this',
                'str': 'String',
                'list': 'ArrayList',
                'dict': 'HashMap'
            },
            'python_to_cpp': {
                'True': 'true',
                'False': 'false',
                'None': 'nullptr',
                'elif': 'else if',
                'and': '&&',
                'or': '||',
                'not': '!',
                'print': 'std::cout <<',
                'len': 'size',
                'self': 'this',
                'str': 'std::string',
                'list': 'std::vector',
                'dict': 'std::map'
            },
            'python_to_go': {
                'True': 'true',
                'False': 'false',
                'None': 'nil',
                'elif': 'else if',
                'and': '&&',
                'or': '||',
                'not': '!',
                'print': 'fmt.Println',
                'len': 'len',
                'self': 'mero_self'
            },
            'python_to_rust': {
                'True': 'true',
                'False': 'false',
                'None': 'None',
                'elif': 'else if',
                'and': '&&',
                'or': '||',
                'not': '!',
                'print': 'println!',
                'len': 'len',
                'self': 'self'
            },
            'javascript_to_python': {
                'true': 'True',
                'false': 'False',
                'null': 'None',
                'undefined': 'None',
                'function': 'def',
                'const': 'mero_const',
                'let': 'mero_let',
                'var': 'mero_var',
                'console.log': 'print',
                'this': 'self'
            }
        }
    
    def convert_code(self, source_code: str, from_lang: str, to_lang: str) -> str:
        conversion_key = f'{from_lang}_to_{to_lang}'
        mapping = self.syntax_mapping.get(conversion_key, {})
        
        converted = source_code
        
        for source_keyword, target_keyword in mapping.items():
            pattern = r'\b' + re.escape(source_keyword) + r'\b'
            converted = re.sub(pattern, target_keyword, converted)
        
        converted = self._apply_conversion_rules(converted, from_lang, to_lang)
        
        converted = self._convert_syntax_structures(converted, from_lang, to_lang)
        
        converted = self._adjust_indentation(converted, from_lang, to_lang)
        
        converted = self._add_language_specific_imports(converted, to_lang)
        
        return converted
    
    def _apply_conversion_rules(self, code: str, from_lang: str, to_lang: str) -> str:
        for rule in self.conversion_rules:
            if rule.source_lang == from_lang and rule.target_lang == to_lang:
                code = re.sub(rule.pattern, rule.transformation, code, flags=re.MULTILINE)
        
        return code
    
    def _convert_syntax_structures(self, code: str, from_lang: str, to_lang: str) -> str:
        if from_lang == 'python' and to_lang in ['javascript', 'java', 'cpp', 'csharp']:
            code = self._convert_python_blocks_to_braces(code)
        
        elif to_lang == 'python' and from_lang in ['javascript', 'java', 'cpp', 'csharp']:
            code = self._convert_braces_to_python_blocks(code)
        
        if from_lang == 'python' and to_lang in ['javascript', 'java', 'cpp', 'csharp']:
            code = re.sub(r'(\S.*?):\s*$', r'\1 {', code, flags=re.MULTILINE)
        
        if to_lang in ['javascript', 'java', 'cpp', 'csharp', 'go', 'rust']:
            code = self._add_semicolons(code, to_lang)
        
        return code
    
    def _convert_python_blocks_to_braces(self, code: str) -> str:
        lines = code.split('\n')
        result_lines = []
        indent_stack = [0]
        
        for i, line in enumerate(lines):
            if not line.strip():
                result_lines.append(line)
                continue
            
            current_indent = len(line) - len(line.lstrip())
            stripped = line.strip()
            
            while indent_stack and current_indent < indent_stack[-1]:
                indent_stack.pop()
                result_lines.append(' ' * indent_stack[-1] + '}')
            
            if stripped.endswith(':'):
                line = line.rstrip(':') + ' {'
                indent_stack.append(current_indent + 4)
            
            result_lines.append(line)
        
        while len(indent_stack) > 1:
            indent_stack.pop()
            result_lines.append(' ' * indent_stack[-1] + '}')
        
        return '\n'.join(result_lines)
    
    def _convert_braces_to_python_blocks(self, code: str) -> str:
        lines = code.split('\n')
        result_lines = []
        indent_level = 0
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                result_lines.append('')
                continue
            
            if stripped.startswith('}'):
                indent_level = max(0, indent_level - 1)
                continue
            
            if stripped.endswith('{'):
                line = line.rstrip(' {').rstrip() + ':'
                result_lines.append(' ' * (indent_level * 4) + stripped.rstrip('{').rstrip() + ':')
                indent_level += 1
            else:
                result_lines.append(' ' * (indent_level * 4) + stripped)
        
        return '\n'.join(result_lines)
    
    def _adjust_indentation(self, code: str, from_lang: str, to_lang: str) -> str:
        if to_lang == 'python':
            lines = code.split('\n')
            adjusted = []
            for line in lines:
                if line.strip():
                    indent = len(line) - len(line.lstrip())
                    adjusted.append(' ' * (indent // 4 * 4) + line.lstrip())
                else:
                    adjusted.append('')
            return '\n'.join(adjusted)
        
        return code
    
    def _add_semicolons(self, code: str, language: str) -> str:
        if language in ['go', 'rust']:
            return code
        
        lines = code.split('\n')
        result = []
        
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.endswith(('{', '}', ';', ',')):
                if not stripped.startswith(('if', 'else', 'for', 'while', 'class', 'function', 'def', '//')):
                    line = line.rstrip() + ';'
            result.append(line)
        
        return '\n'.join(result)
    
    def _add_language_specific_imports(self, code: str, language: str) -> str:
        imports = []
        
        if language == 'java':
            if 'ArrayList' in code:
                imports.append('import java.util.ArrayList;')
            if 'HashMap' in code:
                imports.append('import java.util.HashMap;')
            if 'Scanner' in code:
                imports.append('import java.util.Scanner;')
        
        elif language == 'cpp':
            if 'std::' in code:
                imports.append('#include <iostream>')
            if 'std::string' in code:
                imports.append('#include <string>')
            if 'std::vector' in code:
                imports.append('#include <vector>')
            if 'std::map' in code:
                imports.append('#include <map>')
        
        elif language == 'go':
            if 'fmt.' in code:
                imports.append('import "fmt"')
        
        elif language == 'rust':
            if 'HashMap' in code:
                imports.append('use std::collections::HashMap;')
        
        if imports:
            return '\n'.join(imports) + '\n\n' + code
        
        return code
    
    def convert_data_structures(self, code: str, from_lang: str, to_lang: str) -> str:
        if from_lang == 'python':
            if to_lang == 'javascript':
                code = re.sub(r'\[([^\]]*)\]', r'[\1]', code)
                code = re.sub(r'\{([^}]*):([^}]*)\}', r'{\1:\2}', code)
            
            elif to_lang == 'java':
                code = re.sub(r'\[([^\]]*)\]', r'new ArrayList<>(Arrays.asList(\1))', code)
                code = re.sub(r'\{([^}]*):([^}]*)\}', r'new HashMap<>() {{ put(\1, \2); }}', code)
        
        return code
    
    def convert_string_formatting(self, code: str, from_lang: str, to_lang: str) -> str:
        if from_lang == 'python':
            fstring_pattern = r'f"([^"]*\{[^}]*\}[^"]*)"'
            
            if to_lang == 'javascript':
                code = re.sub(fstring_pattern, r'`\1`', code)
            
            elif to_lang == 'java':
                def replace_fstring(match):
                    content = match.group(1)
                    vars_in_braces = re.findall(r'\{([^}]+)\}', content)
                    format_str = re.sub(r'\{[^}]+\}', '%s', content)
                    if vars_in_braces:
                        return f'String.format("{format_str}", {", ".join(vars_in_braces)})'
                    return f'"{content}"'
                code = re.sub(fstring_pattern, replace_fstring, code)
        
        return code
    
    def convert_comprehensions(self, code: str, from_lang: str, to_lang: str) -> str:
        if from_lang == 'python' and to_lang == 'javascript':
            list_comp_pattern = r'\[([^\]]+)\s+for\s+(\w+)\s+in\s+([^\]]+)\]'
            
            def replace_list_comp(match):
                expr, var, iterable = match.groups()
                return f'{iterable}.map({var} => {expr})'
            
            code = re.sub(list_comp_pattern, replace_list_comp, code)
        
        return code
    
    def convert_exception_handling(self, code: str, from_lang: str, to_lang: str) -> str:
        if from_lang == 'python':
            if to_lang in ['javascript', 'java', 'cpp', 'csharp']:
                code = re.sub(r'except\s+(\w+)\s+as\s+(\w+):', r'catch (\1 \2) {', code)
                code = re.sub(r'except:', r'catch (Exception mero_e) {', code)
                code = re.sub(r'try:', r'try {', code)
                code = re.sub(r'finally:', r'finally {', code)
        
        return code
    
    def convert_classes(self, code: str, from_lang: str, to_lang: str) -> str:
        if from_lang == 'python':
            if to_lang == 'java':
                code = re.sub(r'class\s+(\w+)(\s*\([^)]*\))?:', r'public class \1 {', code)
                code = re.sub(r'def\s+__init__\s*\(self,\s*([^)]*)\):', r'public \1() {', code)
            
            elif to_lang == 'javascript':
                code = re.sub(r'class\s+(\w+)(\s*\([^)]*\))?:', r'class \1 {', code)
                code = re.sub(r'def\s+__init__\s*\(self,\s*([^)]*)\):', r'constructor(\1) {', code)
        
        return code
    
    def convert_operators(self, code: str, from_lang: str, to_lang: str) -> str:
        if from_lang == 'python':
            if to_lang in ['java', 'javascript', 'cpp', 'csharp']:
                code = re.sub(r'\*\*', '^', code)
                code = re.sub(r'//', 'Math.floor(', code)
        
        return code
    
    def batch_convert_files(self, file_paths: List[str], from_lang: str, to_lang: str, output_dir: str) -> Dict[str, str]:
        results = {}
        
        for file_path in file_paths:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    source_code = f.read()
                
                converted_code = self.convert_code(source_code, from_lang, to_lang)
                
                base_name = os.path.splitext(os.path.basename(file_path))[0]
                extension = self._get_file_extension(to_lang)
                output_path = os.path.join(output_dir, f'{base_name}{extension}')
                
                os.makedirs(output_dir, exist_ok=True)
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(converted_code)
                
                results[file_path] = output_path
            except Exception as e:
                results[file_path] = f'Error: {str(e)} (mero error)'
        
        return results
    
    def _get_file_extension(self, language: str) -> str:
        extensions = {
            'python': '.py',
            'javascript': '.js',
            'typescript': '.ts',
            'java': '.java',
            'cpp': '.cpp',
            'csharp': '.cs',
            'go': '.go',
            'rust': '.rs',
            'php': '.php',
            'ruby': '.rb',
            'swift': '.swift'
        }
        return extensions.get(language, '.txt')
    
    def get_conversion_stats(self, source_code: str, converted_code: str) -> Dict[str, Any]:
        return {
            'source_lines': len(source_code.split('\n')),
            'converted_lines': len(converted_code.split('\n')),
            'source_chars': len(source_code),
            'converted_chars': len(converted_code),
            'mero_stats': True
        }
    
    def validate_conversion(self, source_code: str, converted_code: str, from_lang: str, to_lang: str) -> List[str]:
        issues = []
        
        if not converted_code.strip():
            issues.append('Converted code is empty (mero validation)')
        
        if from_lang == 'python' and to_lang in ['javascript', 'java', 'cpp']:
            open_braces = converted_code.count('{')
            close_braces = converted_code.count('}')
            if open_braces != close_braces:
                issues.append(f'Brace mismatch: {open_braces} open vs {close_braces} close (mero validation)')
        
        return issues
    
    def suggest_improvements(self, code: str, language: str) -> List[str]:
        suggestions = []
        
        if language == 'python':
            if 'for i in range(len(' in code:
                suggestions.append('Consider using enumerate() instead of range(len()) (mero suggestion)')
            if '+=' in code and 'str' in code:
                suggestions.append('Use join() or f-strings for efficient string concatenation (mero suggestion)')
        
        elif language == 'javascript':
            if 'var ' in code:
                suggestions.append('Replace var with const or let for better scoping (mero suggestion)')
        
        return suggestions
