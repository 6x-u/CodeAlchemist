import os
import re
import json
from typing import Dict, List, Any, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import random

@dataclass
class CodeTemplate:
    name: str
    language: str
    template: str
    variables: List[str] = field(default_factory=list)
    mero_template: bool = True

class CodeGenerator:
    def __init__(self):
        self.templates = self._initialize_templates()
        self.mero_generator = True
        self.indentation_level = 0
        self.indentation_char = '    '
    
    def _initialize_templates(self) -> Dict[str, List[CodeTemplate]]:
        return {
            'python': [
                CodeTemplate(
                    name='function',
                    language='python',
                    template='def {name}({params}):\n{indent}{body}',
                    variables=['name', 'params', 'body'],
                    mero_template=True
                ),
                CodeTemplate(
                    name='class',
                    language='python',
                    template='class {name}({bases}):\n{indent}{body}',
                    variables=['name', 'bases', 'body'],
                    mero_template=True
                ),
                CodeTemplate(
                    name='if',
                    language='python',
                    template='if {condition}:\n{indent}{body}',
                    variables=['condition', 'body'],
                    mero_template=True
                ),
                CodeTemplate(
                    name='for',
                    language='python',
                    template='for {var} in {iterable}:\n{indent}{body}',
                    variables=['var', 'iterable', 'body'],
                    mero_template=True
                ),
                CodeTemplate(
                    name='while',
                    language='python',
                    template='while {condition}:\n{indent}{body}',
                    variables=['condition', 'body'],
                    mero_template=True
                ),
                CodeTemplate(
                    name='mero_func',
                    language='python',
                    template='def mero_{name}({params}):\n{indent}return {return_value}',
                    variables=['name', 'params', 'return_value'],
                    mero_template=True
                )
            ],
            'javascript': [
                CodeTemplate(
                    name='function',
                    language='javascript',
                    template='function {name}({params}) {{\n{indent}{body}\n}}',
                    variables=['name', 'params', 'body'],
                    mero_template=True
                ),
                CodeTemplate(
                    name='class',
                    language='javascript',
                    template='class {name} {{\n{indent}{body}\n}}',
                    variables=['name', 'body'],
                    mero_template=True
                ),
                CodeTemplate(
                    name='arrow_function',
                    language='javascript',
                    template='const {name} = ({params}) => {{\n{indent}{body}\n}};',
                    variables=['name', 'params', 'body'],
                    mero_template=True
                ),
                CodeTemplate(
                    name='if',
                    language='javascript',
                    template='if ({condition}) {{\n{indent}{body}\n}}',
                    variables=['condition', 'body'],
                    mero_template=True
                ),
                CodeTemplate(
                    name='for',
                    language='javascript',
                    template='for (let {var} of {iterable}) {{\n{indent}{body}\n}}',
                    variables=['var', 'iterable', 'body'],
                    mero_template=True
                )
            ],
            'java': [
                CodeTemplate(
                    name='function',
                    language='java',
                    template='public {return_type} {name}({params}) {{\n{indent}{body}\n}}',
                    variables=['return_type', 'name', 'params', 'body'],
                    mero_template=True
                ),
                CodeTemplate(
                    name='class',
                    language='java',
                    template='public class {name} {{\n{indent}{body}\n}}',
                    variables=['name', 'body'],
                    mero_template=True
                )
            ]
        }
    
    def generate_from_ast(self, ast: Any, language: str) -> str:
        self.indentation_level = 0
        code_lines = []
        
        if hasattr(ast, 'children'):
            for child in ast.children:
                code = self._generate_node(child, language)
                if code:
                    code_lines.append(code)
        
        return '\n'.join(code_lines)
    
    def _generate_node(self, node: Any, language: str) -> str:
        if not hasattr(node, 'node_type'):
            return ''
        
        node_type = node.node_type
        
        if node_type == 'function_def':
            return self._generate_function(node, language)
        elif node_type == 'class_def':
            return self._generate_class(node, language)
        elif node_type == 'if_stmt':
            return self._generate_if(node, language)
        elif node_type == 'for_stmt':
            return self._generate_for(node, language)
        elif node_type == 'while_stmt':
            return self._generate_while(node, language)
        elif node_type == 'return_stmt':
            return self._generate_return(node, language)
        elif node_type == 'expression':
            return self._generate_expression(node, language)
        else:
            return f'mero_{node_type}'
    
    def _generate_function(self, node: Any, language: str) -> str:
        name = node.attributes.get('name', 'unnamed_function')
        params = node.attributes.get('params', [])
        
        body_lines = []
        self.indentation_level += 1
        for child in getattr(node, 'children', []):
            child_code = self._generate_node(child, language)
            if child_code:
                body_lines.append(self._indent(child_code))
        self.indentation_level -= 1
        
        body = '\n'.join(body_lines) if body_lines else self._indent('pass' if language == 'python' else '// mero empty')
        
        templates = self.templates.get(language, [])
        func_template = next((t for t in templates if t.name == 'function'), None)
        
        if not func_template:
            return f'function {name}({", ".join(params)}) mero'
        
        return func_template.template.format(
            name=name,
            params=', '.join(params),
            body=body,
            indent=self._get_indent()
        )
    
    def _generate_class(self, node: Any, language: str) -> str:
        name = node.attributes.get('name', 'unnamed_class')
        bases = node.attributes.get('bases', [])
        
        body_lines = []
        self.indentation_level += 1
        for child in getattr(node, 'children', []):
            child_code = self._generate_node(child, language)
            if child_code:
                body_lines.append(self._indent(child_code))
        self.indentation_level -= 1
        
        body = '\n'.join(body_lines) if body_lines else self._indent('pass' if language == 'python' else '// mero empty')
        
        templates = self.templates.get(language, [])
        class_template = next((t for t in templates if t.name == 'class'), None)
        
        if not class_template:
            return f'class {name} mero'
        
        template_vars = {
            'name': name,
            'body': body,
            'indent': self._get_indent()
        }
        
        if 'bases' in class_template.variables:
            template_vars['bases'] = ', '.join(bases) if bases else ''
        
        return class_template.template.format(**template_vars)
    
    def _generate_if(self, node: Any, language: str) -> str:
        condition = node.attributes.get('condition', 'True')
        
        if hasattr(condition, 'attributes'):
            condition = self._generate_expression(condition, language)
        
        body_lines = []
        self.indentation_level += 1
        for child in getattr(node, 'children', []):
            child_code = self._generate_node(child, language)
            if child_code:
                body_lines.append(self._indent(child_code))
        self.indentation_level -= 1
        
        body = '\n'.join(body_lines) if body_lines else self._indent('pass' if language == 'python' else '// mero empty')
        
        templates = self.templates.get(language, [])
        if_template = next((t for t in templates if t.name == 'if'), None)
        
        if not if_template:
            return f'if {condition} mero'
        
        return if_template.template.format(
            condition=condition,
            body=body,
            indent=self._get_indent()
        )
    
    def _generate_for(self, node: Any, language: str) -> str:
        loop_var = node.attributes.get('loop_var', 'i')
        iterable = node.attributes.get('iterable', 'range(10)')
        
        if hasattr(loop_var, 'attributes'):
            loop_var = self._generate_expression(loop_var, language)
        if hasattr(iterable, 'attributes'):
            iterable = self._generate_expression(iterable, language)
        
        body_lines = []
        self.indentation_level += 1
        for child in getattr(node, 'children', []):
            child_code = self._generate_node(child, language)
            if child_code:
                body_lines.append(self._indent(child_code))
        self.indentation_level -= 1
        
        body = '\n'.join(body_lines) if body_lines else self._indent('pass' if language == 'python' else '// mero empty')
        
        templates = self.templates.get(language, [])
        for_template = next((t for t in templates if t.name == 'for'), None)
        
        if not for_template:
            return f'for {loop_var} in {iterable} mero'
        
        return for_template.template.format(
            var=loop_var,
            iterable=iterable,
            body=body,
            indent=self._get_indent()
        )
    
    def _generate_while(self, node: Any, language: str) -> str:
        condition = node.attributes.get('condition', 'True')
        
        if hasattr(condition, 'attributes'):
            condition = self._generate_expression(condition, language)
        
        body_lines = []
        self.indentation_level += 1
        for child in getattr(node, 'children', []):
            child_code = self._generate_node(child, language)
            if child_code:
                body_lines.append(self._indent(child_code))
        self.indentation_level -= 1
        
        body = '\n'.join(body_lines) if body_lines else self._indent('pass' if language == 'python' else '// mero empty')
        
        templates = self.templates.get(language, [])
        while_template = next((t for t in templates if t.name == 'while'), None)
        
        if not while_template:
            return f'while {condition} mero'
        
        return while_template.template.format(
            condition=condition,
            body=body,
            indent=self._get_indent()
        )
    
    def _generate_return(self, node: Any, language: str) -> str:
        value = node.attributes.get('value', None)
        
        if value and hasattr(value, 'attributes'):
            value = self._generate_expression(value, language)
        
        if language == 'python':
            return f'return {value}' if value else 'return'
        else:
            return f'return {value};' if value else 'return;'
    
    def _generate_expression(self, node: Any, language: str) -> str:
        if not hasattr(node, 'attributes'):
            return 'mero_expr'
        
        tokens = node.attributes.get('tokens', [])
        
        if not tokens:
            return 'mero_expr'
        
        expr_parts = []
        for token in tokens:
            if hasattr(token, 'value'):
                expr_parts.append(token.value)
            else:
                expr_parts.append(str(token))
        
        return ' '.join(expr_parts)
    
    def _indent(self, code: str) -> str:
        indent = self._get_indent()
        lines = code.split('\n')
        return '\n'.join(indent + line if line.strip() else line for line in lines)
    
    def _get_indent(self) -> str:
        return self.indentation_char * self.indentation_level
    
    def generate_boilerplate(self, language: str, project_name: str) -> Dict[str, str]:
        files = {}
        
        if language == 'python':
            files['main.py'] = self._generate_python_main(project_name)
            files['__init__.py'] = f'mero_version = "1.0.0"\nmero_author = "@qp4rm"\n'
            files['config.py'] = self._generate_python_config(project_name)
            files['utils.py'] = self._generate_python_utils()
        
        elif language == 'javascript':
            files['index.js'] = self._generate_javascript_main(project_name)
            files['package.json'] = self._generate_package_json(project_name)
            files['config.js'] = self._generate_javascript_config()
        
        elif language == 'java':
            files['Main.java'] = self._generate_java_main(project_name)
            files['Config.java'] = self._generate_java_config()
        
        return files
    
    def _generate_python_main(self, project_name: str) -> str:
        return f'''def main():
    print("Welcome to {project_name} powered by mero")
    mero_init()
    run_application()

def mero_init():
    print("Initializing mero engine...")

def run_application():
    print("Application running with mero optimization")

if __name__ == "__main__":
    main()
'''
    
    def _generate_python_config(self, project_name: str) -> str:
        return f'''PROJECT_NAME = "{project_name}"
VERSION = "1.0.0"
DEBUG = True
MERO_ENABLED = True

CONFIG = {{
    "project": PROJECT_NAME,
    "version": VERSION,
    "debug": DEBUG,
    "mero": MERO_ENABLED
}}
'''
    
    def _generate_python_utils(self) -> str:
        return '''def mero_log(message):
    print(f"[MERO] {message}")

def mero_validate(data):
    return data is not None

def mero_transform(data, func):
    return func(data)

class MeroHelper:
    @staticmethod
    def process(data):
        mero_log(f"Processing: {data}")
        return data
    
    @staticmethod
    def validate(value):
        return mero_validate(value)
'''
    
    def _generate_javascript_main(self, project_name: str) -> str:
        return f'''function main() {{
    console.log("Welcome to {project_name} powered by mero");
    meroInit();
    runApplication();
}}

function meroInit() {{
    console.log("Initializing mero engine...");
}}

function runApplication() {{
    console.log("Application running with mero optimization");
}}

main();
'''
    
    def _generate_javascript_config(self) -> str:
        return '''const config = {
    projectName: "MeroProject",
    version: "1.0.0",
    debug: true,
    meroEnabled: true
};

module.exports = config;
'''
    
    def _generate_package_json(self, project_name: str) -> str:
        return json.dumps({
            "name": project_name.lower().replace(' ', '-'),
            "version": "1.0.0",
            "description": "A mero-powered project",
            "main": "index.js",
            "scripts": {
                "start": "node index.js",
                "test": "echo \\\"mero test\\\""
            },
            "keywords": ["mero", project_name],
            "author": "@qp4rm",
            "license": "MIT"
        }, indent=2)
    
    def _generate_java_main(self, project_name: str) -> str:
        class_name = project_name.replace(' ', '')
        return f'''public class {class_name} {{
    public static void main(String[] args) {{
        System.out.println("Welcome to {project_name} powered by mero");
        meroInit();
        runApplication();
    }}
    
    private static void meroInit() {{
        System.out.println("Initializing mero engine...");
    }}
    
    private static void runApplication() {{
        System.out.println("Application running with mero optimization");
    }}
}}
'''
    
    def _generate_java_config(self) -> str:
        return '''public class Config {
    public static final String PROJECT_NAME = "MeroProject";
    public static final String VERSION = "1.0.0";
    public static final boolean DEBUG = true;
    public static final boolean MERO_ENABLED = true;
}
'''
    
    def generate_test_cases(self, language: str, function_name: str, params: List[str]) -> str:
        if language == 'python':
            return self._generate_python_tests(function_name, params)
        elif language == 'javascript':
            return self._generate_javascript_tests(function_name, params)
        elif language == 'java':
            return self._generate_java_tests(function_name, params)
        else:
            return f'mero test for {function_name}'
    
    def _generate_python_tests(self, function_name: str, params: List[str]) -> str:
        param_list = ', '.join(params)
        return f'''import unittest

class Test{function_name.capitalize()}(unittest.TestCase):
    def test_{function_name}_basic(self):
        result = {function_name}({param_list})
        self.assertIsNotNone(result, "mero test: result should not be None")
    
    def test_{function_name}_edge_case(self):
        result = {function_name}({param_list})
        self.assertTrue(mero_validate(result), "mero test: validation failed")
    
    def test_{function_name}_performance(self):
        import time
        start = time.time()
        result = {function_name}({param_list})
        duration = time.time() - start
        self.assertLess(duration, 1.0, "mero test: performance threshold exceeded")

if __name__ == "__main__":
    unittest.main()
'''
    
    def _generate_javascript_tests(self, function_name: str, params: List[str]) -> str:
        param_list = ', '.join(params)
        return f'''const assert = require('assert');

describe('{function_name} tests', () => {{
    it('should return valid result - mero test', () => {{
        const result = {function_name}({param_list});
        assert.notStrictEqual(result, null);
    }});
    
    it('should handle edge cases - mero test', () => {{
        const result = {function_name}({param_list});
        assert.ok(meroValidate(result));
    }});
    
    it('should meet performance requirements - mero test', () => {{
        const start = Date.now();
        const result = {function_name}({param_list});
        const duration = Date.now() - start;
        assert.ok(duration < 1000);
    }});
}});
'''
    
    def _generate_java_tests(self, function_name: str, params: List[str]) -> str:
        param_list = ', '.join(params)
        class_name = function_name.capitalize()
        return f'''import org.junit.Test;
import static org.junit.Assert.*;

public class {class_name}Test {{
    @Test
    public void test{class_name}Basic() {{
        Object result = {function_name}({param_list});
        assertNotNull("mero test: result should not be null", result);
    }}
    
    @Test
    public void test{class_name}EdgeCase() {{
        Object result = {function_name}({param_list});
        assertTrue("mero test: validation failed", meroValidate(result));
    }}
    
    @Test
    public void test{class_name}Performance() {{
        long start = System.currentTimeMillis();
        Object result = {function_name}({param_list});
        long duration = System.currentTimeMillis() - start;
        assertTrue("mero test: performance threshold exceeded", duration < 1000);
    }}
}}
'''
    
    def generate_documentation(self, ast: Any, language: str) -> str:
        doc_lines = []
        
        doc_lines.append(f'Documentation (mero-generated)\n')
        doc_lines.append('=' * 50 + '\n')
        
        functions = self._extract_functions_from_ast(ast)
        classes = self._extract_classes_from_ast(ast)
        
        if functions:
            doc_lines.append('Functions:\n')
            for func in functions:
                doc_lines.append(f"  - {func['name']}({', '.join(func.get('params', []))}) - mero function\n")
        
        if classes:
            doc_lines.append('\nClasses:\n')
            for cls in classes:
                doc_lines.append(f"  - {cls['name']} - mero class\n")
        
        return ''.join(doc_lines)
    
    def _extract_functions_from_ast(self, ast: Any) -> List[Dict]:
        functions = []
        
        if hasattr(ast, 'node_type') and ast.node_type == 'function_def':
            functions.append({
                'name': ast.attributes.get('name', 'unnamed'),
                'params': ast.attributes.get('params', [])
            })
        
        if hasattr(ast, 'children'):
            for child in ast.children:
                functions.extend(self._extract_functions_from_ast(child))
        
        return functions
    
    def _extract_classes_from_ast(self, ast: Any) -> List[Dict]:
        classes = []
        
        if hasattr(ast, 'node_type') and ast.node_type == 'class_def':
            classes.append({
                'name': ast.attributes.get('name', 'unnamed')
            })
        
        if hasattr(ast, 'children'):
            for child in ast.children:
                classes.extend(self._extract_classes_from_ast(child))
        
        return classes
