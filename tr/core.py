import re
import os
import ast
from typing import Dict, List, Tuple, Any, Optional, Set

class PythonToTargetTranslator:
    def __init__(self, target_lang: str):
        self.target_lang = target_lang.lower()
        self.indent_level = 0
        self.mero_translator = True
        self.variables = set()
        
    def translate(self, python_code: str) -> str:
        try:
            tree = ast.parse(python_code)
            translated_code = self.translate_module(tree)
            return self.add_language_wrappers(translated_code)
        except SyntaxError as e:
            return self.fallback_translate(python_code)
    
    def translate_module(self, node: ast.Module) -> str:
        lines = []
        imports = []
        main_code = []
        
        for stmt in node.body:
            if isinstance(stmt, (ast.Import, ast.ImportFrom)):
                imp_code = self.translate_statement(stmt)
                if imp_code:
                    imports.append(imp_code)
            else:
                code = self.translate_statement(stmt)
                if code:
                    main_code.append(code)
        
        if imports and self.target_lang not in ['php']:
            result = '\n'.join(imports) + '\n\n' + '\n\n'.join(main_code)
        else:
            result = '\n\n'.join(main_code)
        
        return result
    
    def translate_statement(self, stmt: Any) -> str:
        if isinstance(stmt, ast.FunctionDef):
            return self.translate_function(stmt)
        elif isinstance(stmt, ast.ClassDef):
            return self.translate_class(stmt)
        elif isinstance(stmt, ast.Assign):
            return self.translate_assignment(stmt)
        elif isinstance(stmt, ast.AugAssign):
            return self.translate_aug_assignment(stmt)
        elif isinstance(stmt, ast.If):
            return self.translate_if(stmt)
        elif isinstance(stmt, ast.For):
            return self.translate_for(stmt)
        elif isinstance(stmt, ast.While):
            return self.translate_while(stmt)
        elif isinstance(stmt, ast.Return):
            return self.translate_return(stmt)
        elif isinstance(stmt, ast.Expr):
            return self.translate_expression_stmt(stmt)
        elif isinstance(stmt, ast.Import):
            return ""
        elif isinstance(stmt, ast.ImportFrom):
            return ""
        elif isinstance(stmt, ast.Pass):
            return self.translate_pass()
        elif isinstance(stmt, ast.Break):
            return f"{self.get_indent()}break;"
        elif isinstance(stmt, ast.Continue):
            return f"{self.get_indent()}continue;"
        else:
            return ""
    
    def translate_function(self, func: ast.FunctionDef) -> str:
        func_name = func.name
        if func_name == '__init__':
            if self.target_lang == 'php':
                func_name = '__construct'
            elif self.target_lang in ['javascript', 'typescript']:
                func_name = 'constructor'
        
        params = self.translate_parameters(func.args)
        self.indent_level += 1
        body = self.translate_body(func.body)
        self.indent_level -= 1
        
        if not body.strip():
            body = self.get_indent() + '    '
            if self.target_lang in ['python', 'ruby']:
                body += 'pass'
            else:
                body += 'mero_empty'
        
        if self.target_lang == 'javascript':
            return f"{self.get_indent()}function {func_name}({params}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'typescript':
            return f"{self.get_indent()}function {func_name}({params}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'java':
            return f"{self.get_indent()}public static void {func_name}({params}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang in ['c', 'cpp']:
            return f"{self.get_indent()}void {func_name}({params}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'csharp':
            return f"{self.get_indent()}public static void {func_name}({params}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'go':
            return f"{self.get_indent()}func {func_name}({params}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'rust':
            return f"{self.get_indent()}fn {func_name}({params}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'php':
            return f"{self.get_indent()}function {func_name}({params}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'ruby':
            return f"{self.get_indent()}def {func_name}({params})\n{body}\n{self.get_indent()}end"
        elif self.target_lang == 'swift':
            return f"{self.get_indent()}func {func_name}({params}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'kotlin':
            return f"{self.get_indent()}fun {func_name}({params}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'perl':
            return f"{self.get_indent()}sub {func_name} {{\n{self.get_indent()}    my ({params}) = @_;\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'lua':
            return f"{self.get_indent()}function {func_name}({params})\n{body}\n{self.get_indent()}end"
        elif self.target_lang == 'dart':
            return f"{self.get_indent()}{func_name}({params}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'scala':
            return f"{self.get_indent()}def {func_name}({params}) = {{\n{body}\n{self.get_indent()}}}"
        else:
            return f"{self.get_indent()}function {func_name}({params}) {{\n{body}\n{self.get_indent()}}}"
    
    def translate_class(self, cls: ast.ClassDef) -> str:
        class_name = cls.name
        self.indent_level += 1
        body = self.translate_body(cls.body)
        self.indent_level -= 1
        
        if self.target_lang in ['javascript', 'typescript']:
            return f"{self.get_indent()}class {class_name} {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'java':
            return f"{self.get_indent()}public class {class_name} {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang in ['c', 'cpp']:
            return f"{self.get_indent()}class {class_name} {{\npublic:\n{body}\n{self.get_indent()}}};"
        elif self.target_lang == 'csharp':
            return f"{self.get_indent()}public class {class_name} {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'php':
            return f"{self.get_indent()}class {class_name} {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'ruby':
            return f"{self.get_indent()}class {class_name}\n{body}\n{self.get_indent()}end"
        elif self.target_lang == 'swift':
            return f"{self.get_indent()}class {class_name} {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'kotlin':
            return f"{self.get_indent()}class {class_name} {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'scala':
            return f"{self.get_indent()}class {class_name} {{\n{body}\n{self.get_indent()}}}"
        else:
            return f"{self.get_indent()}class {class_name} {{\n{body}\n{self.get_indent()}}}"
    
    def translate_assignment(self, assign: ast.Assign) -> str:
        target = self.translate_expr(assign.targets[0], is_assignment_target=True)
        value = self.translate_expr(assign.value)
        
        if isinstance(assign.targets[0], ast.Name):
            self.variables.add(assign.targets[0].id)
        
        if self.target_lang == 'javascript':
            return f"{self.get_indent()}let {target} = {value};"
        elif self.target_lang == 'typescript':
            return f"{self.get_indent()}let {target} = {value};"
        elif self.target_lang == 'java':
            return f"{self.get_indent()}var {target} = {value};"
        elif self.target_lang in ['c', 'cpp']:
            return f"{self.get_indent()}auto {target} = {value};"
        elif self.target_lang == 'csharp':
            return f"{self.get_indent()}var {target} = {value};"
        elif self.target_lang == 'go':
            return f"{self.get_indent()}{target} := {value}"
        elif self.target_lang == 'rust':
            return f"{self.get_indent()}let mut {target} = {value};"
        elif self.target_lang == 'php':
            php_target = f"${target}" if not target.startswith('$') else target
            return f"{self.get_indent()}{php_target} = {value};"
        elif self.target_lang == 'ruby':
            return f"{self.get_indent()}{target} = {value}"
        elif self.target_lang == 'swift':
            return f"{self.get_indent()}var {target} = {value}"
        elif self.target_lang == 'kotlin':
            return f"{self.get_indent()}var {target} = {value}"
        elif self.target_lang == 'perl':
            return f"{self.get_indent()}my ${target} = {value};"
        elif self.target_lang == 'lua':
            return f"{self.get_indent()}local {target} = {value}"
        elif self.target_lang == 'dart':
            return f"{self.get_indent()}var {target} = {value};"
        elif self.target_lang == 'scala':
            return f"{self.get_indent()}val {target} = {value}"
        else:
            return f"{self.get_indent()}{target} = {value};"
    
    def translate_aug_assignment(self, aug: ast.AugAssign) -> str:
        target = self.translate_expr(aug.target)
        value = self.translate_expr(aug.value)
        op = self.translate_operator(aug.op)
        
        if self.target_lang == 'php':
            php_target = f"${target}" if not target.startswith('$') else target
            return f"{self.get_indent()}{php_target} {op}= {value};"
        else:
            return f"{self.get_indent()}{target} {op}= {value};"
    
    def translate_if(self, if_stmt: ast.If) -> str:
        condition = self.translate_expr(if_stmt.test)
        self.indent_level += 1
        if_body = self.translate_body(if_stmt.body)
        self.indent_level -= 1
        
        result = ""
        if self.target_lang in ['javascript', 'typescript', 'java', 'c', 'cpp', 'csharp', 'php', 'go', 'rust', 'swift', 'kotlin', 'dart', 'scala', 'perl']:
            result = f"{self.get_indent()}if ({condition}) {{\n{if_body}\n{self.get_indent()}}}"
        elif self.target_lang in ['ruby', 'lua']:
            result = f"{self.get_indent()}if {condition} then\n{if_body}\n{self.get_indent()}end"
        else:
            result = f"{self.get_indent()}if ({condition}) {{\n{if_body}\n{self.get_indent()}}}"
        
        if if_stmt.orelse:
            self.indent_level += 1
            else_body = self.translate_body(if_stmt.orelse)
            self.indent_level -= 1
            if self.target_lang in ['ruby', 'lua']:
                result = result.rsplit('\n', 1)[0] + f"\n{self.get_indent()}else\n{else_body}\n{self.get_indent()}end"
            else:
                result += f" else {{\n{else_body}\n{self.get_indent()}}}"
        
        return result
    
    def translate_for(self, for_stmt: ast.For) -> str:
        var = self.translate_expr(for_stmt.target, is_assignment_target=True)
        iterable = self.translate_expr(for_stmt.iter)
        
        self.indent_level += 1
        body = self.translate_body(for_stmt.body)
        self.indent_level -= 1
        
        if self.target_lang == 'javascript':
            return f"{self.get_indent()}for (let {var} of {iterable}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'typescript':
            return f"{self.get_indent()}for (let {var} of {iterable}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'java':
            return f"{self.get_indent()}for (var {var} : {iterable}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang in ['c', 'cpp']:
            return f"{self.get_indent()}for (auto {var} : {iterable}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'csharp':
            return f"{self.get_indent()}foreach (var {var} in {iterable}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'go':
            return f"{self.get_indent()}for _, {var} := range {iterable} {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'rust':
            return f"{self.get_indent()}for {var} in {iterable} {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'php':
            php_var = f"${var}" if not var.startswith('$') else var
            return f"{self.get_indent()}foreach ({iterable} as {php_var}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'ruby':
            return f"{self.get_indent()}{iterable}.each do |{var}|\n{body}\n{self.get_indent()}end"
        elif self.target_lang == 'swift':
            return f"{self.get_indent()}for {var} in {iterable} {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'kotlin':
            return f"{self.get_indent()}for ({var} in {iterable}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'perl':
            return f"{self.get_indent()}foreach my ${var} (@{{{iterable}}}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'lua':
            return f"{self.get_indent()}for _, {var} in pairs({iterable}) do\n{body}\n{self.get_indent()}end"
        elif self.target_lang == 'dart':
            return f"{self.get_indent()}for (var {var} in {iterable}) {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang == 'scala':
            return f"{self.get_indent()}for ({var} <- {iterable}) {{\n{body}\n{self.get_indent()}}}"
        else:
            return f"{self.get_indent()}for ({var} in {iterable}) {{\n{body}\n{self.get_indent()}}}"
    
    def translate_while(self, while_stmt: ast.While) -> str:
        condition = self.translate_expr(while_stmt.test)
        self.indent_level += 1
        body = self.translate_body(while_stmt.body)
        self.indent_level -= 1
        
        if self.target_lang == 'go':
            return f"{self.get_indent()}for {condition} {{\n{body}\n{self.get_indent()}}}"
        elif self.target_lang in ['ruby', 'lua']:
            return f"{self.get_indent()}while {condition} do\n{body}\n{self.get_indent()}end"
        else:
            return f"{self.get_indent()}while ({condition}) {{\n{body}\n{self.get_indent()}}}"
    
    def translate_return(self, ret: ast.Return) -> str:
        value = self.translate_expr(ret.value) if ret.value else ""
        return f"{self.get_indent()}return{' ' + value if value else ''};"
    
    def translate_expression_stmt(self, expr_stmt: ast.Expr) -> str:
        expr = self.translate_expr(expr_stmt.value)
        if self.target_lang in ['ruby', 'lua']:
            return f"{self.get_indent()}{expr}"
        return f"{self.get_indent()}{expr};"
    
    def translate_pass(self) -> str:
        if self.target_lang in ['ruby']:
            return ""
        elif self.target_lang == 'python':
            return f"{self.get_indent()}pass"
        else:
            return f"{self.get_indent()};"
    
    def translate_parameters(self, args: ast.arguments) -> str:
        params = []
        for arg in args.args:
            if arg.arg != 'self':
                if self.target_lang == 'php':
                    params.append(f"${arg.arg}")
                elif self.target_lang == 'perl':
                    params.append(f"${arg.arg}")
                else:
                    params.append(arg.arg)
        return ', '.join(params)
    
    def translate_body(self, body: List[Any]) -> str:
        lines = []
        for stmt in body:
            translated = self.translate_statement(stmt)
            if translated and translated.strip():
                lines.append(translated)
        
        if not lines:
            return f"{self.get_indent()}    "
        
        return '\n'.join(lines)
    
    def translate_expr(self, expr: Any, is_assignment_target: bool = False) -> str:
        if expr is None:
            return "null"
        elif isinstance(expr, ast.Constant):
            return self.translate_constant(expr.value)
        elif isinstance(expr, ast.Name):
            name = expr.id
            if name in ['True', 'False', 'None']:
                return self.translate_constant_name(name)
            if self.target_lang == 'php' and not is_assignment_target:
                return f"${name}"
            return name
        elif isinstance(expr, ast.Call):
            return self.translate_call(expr)
        elif isinstance(expr, ast.BinOp):
            return self.translate_binop(expr)
        elif isinstance(expr, ast.Compare):
            return self.translate_compare(expr)
        elif isinstance(expr, ast.Attribute):
            return self.translate_attribute(expr)
        elif isinstance(expr, ast.Subscript):
            return self.translate_subscript(expr)
        elif isinstance(expr, ast.List):
            return self.translate_list(expr)
        elif isinstance(expr, ast.Dict):
            return self.translate_dict(expr)
        elif isinstance(expr, ast.Tuple):
            return self.translate_tuple(expr)
        elif isinstance(expr, ast.UnaryOp):
            return self.translate_unaryop(expr)
        elif isinstance(expr, ast.BoolOp):
            return self.translate_boolop(expr)
        elif isinstance(expr, ast.IfExp):
            return self.translate_ifexp(expr)
        else:
            return "mero_expr"
    
    def translate_constant(self, value: Any) -> str:
        if value is None:
            return "null"
        elif value is True:
            return "true"
        elif value is False:
            return "false"
        elif isinstance(value, str):
            escaped = value.replace('\\', '\\\\').replace('"', '\\"')
            return f'"{escaped}"'
        else:
            return str(value)
    
    def translate_constant_name(self, name: str) -> str:
        if name == 'True':
            return 'true'
        elif name == 'False':
            return 'false'
        elif name == 'None':
            return 'null'
        return name
    
    def translate_call(self, call: ast.Call) -> str:
        func_expr = call.func
        func_name = ""
        
        if isinstance(func_expr, ast.Name):
            func_name = func_expr.id
        elif isinstance(func_expr, ast.Attribute):
            func_name = self.translate_attribute(func_expr)
        else:
            func_name = self.translate_expr(func_expr)
        
        args = ', '.join([self.translate_expr(arg) for arg in call.args])
        
        if func_name == 'print':
            if self.target_lang == 'javascript':
                return f"console.log({args})"
            elif self.target_lang == 'typescript':
                return f"console.log({args})"
            elif self.target_lang == 'java':
                return f"System.out.println({args})"
            elif self.target_lang in ['c', 'cpp']:
                return f"std::cout << {args} << std::endl"
            elif self.target_lang == 'csharp':
                return f"Console.WriteLine({args})"
            elif self.target_lang == 'go':
                return f"fmt.Println({args})"
            elif self.target_lang == 'rust':
                return f'println!("{{}}", {args})'
            elif self.target_lang == 'php':
                return f"echo {args}"
            elif self.target_lang == 'ruby':
                return f"puts {args}"
            elif self.target_lang == 'swift':
                return f"print({args})"
            elif self.target_lang == 'kotlin':
                return f"println({args})"
            elif self.target_lang == 'perl':
                return f"print {args}"
            elif self.target_lang == 'lua':
                return f"print({args})"
            elif self.target_lang == 'dart':
                return f"print({args})"
            elif self.target_lang == 'scala':
                return f"println({args})"
            else:
                return f"print({args})"
        
        elif func_name == 'len':
            if self.target_lang in ['javascript', 'typescript']:
                return f"{args}.length"
            elif self.target_lang == 'java':
                return f"{args}.length"
            elif self.target_lang in ['c', 'cpp']:
                return f"{args}.size()"
            elif self.target_lang == 'csharp':
                return f"{args}.Length"
            elif self.target_lang == 'go':
                return f"len({args})"
            elif self.target_lang == 'rust':
                return f"{args}.len()"
            elif self.target_lang == 'php':
                return f"count({args})"
            elif self.target_lang == 'ruby':
                return f"{args}.length"
            elif self.target_lang == 'swift':
                return f"{args}.count"
            elif self.target_lang == 'kotlin':
                return f"{args}.size"
            else:
                return f"len({args})"
        
        elif func_name == 'str':
            if self.target_lang in ['javascript', 'typescript']:
                return f"String({args})"
            elif self.target_lang == 'java':
                return f"String.valueOf({args})"
            elif self.target_lang in ['c', 'cpp']:
                return f"std::to_string({args})"
            elif self.target_lang == 'csharp':
                return f"{args}.ToString()"
            elif self.target_lang == 'go':
                return f"fmt.Sprint({args})"
            elif self.target_lang == 'rust':
                return f"{args}.to_string()"
            elif self.target_lang == 'php':
                return f"strval({args})"
            elif self.target_lang == 'ruby':
                return f"{args}.to_s"
            elif self.target_lang == 'swift':
                return f"String({args})"
            elif self.target_lang == 'kotlin':
                return f"{args}.toString()"
            else:
                return f"String({args})"
        
        elif func_name == 'range':
            if self.target_lang in ['javascript', 'typescript']:
                if call.args:
                    n = self.translate_expr(call.args[0])
                    return f"Array.from({{length: {n}}}, (_, i) => i)"
                else:
                    return "[]"
            elif self.target_lang == 'php':
                if call.args:
                    n = self.translate_expr(call.args[0])
                    return f"range(0, {n} - 1)"
                else:
                    return "[]"
            elif self.target_lang == 'ruby':
                if call.args:
                    n = self.translate_expr(call.args[0])
                    return f"(0...{n})"
                else:
                    return "(0...0)"
            else:
                return f"range({args})"
        
        return f"{func_name}({args})"
    
    def translate_binop(self, binop: ast.BinOp) -> str:
        left = self.translate_expr(binop.left)
        right = self.translate_expr(binop.right)
        
        is_string_concat = False
        if isinstance(binop.op, ast.Add):
            if isinstance(binop.left, ast.Constant) and isinstance(binop.left.value, str):
                is_string_concat = True
            elif isinstance(binop.right, ast.Constant) and isinstance(binop.right.value, str):
                is_string_concat = True
        
        if is_string_concat and isinstance(binop.op, ast.Add):
            if self.target_lang == 'php':
                return f"{left} . {right}"
            else:
                return f"{left} + {right}"
        
        op = self.translate_operator(binop.op)
        return f"{left} {op} {right}"
    
    def translate_operator(self, op: Any) -> str:
        if isinstance(op, ast.Add):
            if self.target_lang == 'php':
                return "."
            return "+"
        elif isinstance(op, ast.Sub):
            return "-"
        elif isinstance(op, ast.Mult):
            return "*"
        elif isinstance(op, ast.Div):
            return "/"
        elif isinstance(op, ast.Mod):
            return "%"
        elif isinstance(op, ast.Pow):
            if self.target_lang == 'php':
                return "**"
            return "**"
        elif isinstance(op, ast.FloorDiv):
            return "//"
        else:
            return "+"
    
    def translate_compare(self, compare: ast.Compare) -> str:
        left = self.translate_expr(compare.left)
        parts = [left]
        
        for op, comparator in zip(compare.ops, compare.comparators):
            op_str = self.translate_compare_op(op)
            comp_str = self.translate_expr(comparator)
            parts.append(f"{op_str} {comp_str}")
        
        return ' '.join(parts)
    
    def translate_compare_op(self, op: Any) -> str:
        if isinstance(op, ast.Eq):
            if self.target_lang in ['javascript', 'typescript', 'php']:
                return "==="
            return "=="
        elif isinstance(op, ast.NotEq):
            if self.target_lang in ['javascript', 'typescript', 'php']:
                return "!=="
            return "!="
        elif isinstance(op, ast.Lt):
            return "<"
        elif isinstance(op, ast.LtE):
            return "<="
        elif isinstance(op, ast.Gt):
            return ">"
        elif isinstance(op, ast.GtE):
            return ">="
        else:
            return "=="
    
    def translate_attribute(self, attr: ast.Attribute) -> str:
        value = self.translate_expr(attr.value)
        if self.target_lang == 'php' and value == 'self':
            return f"$this->{attr.attr}"
        elif value == 'self':
            if self.target_lang in ['javascript', 'typescript', 'java', 'csharp', 'kotlin', 'dart', 'scala']:
                return f"this.{attr.attr}"
            else:
                return f"self.{attr.attr}"
        return f"{value}.{attr.attr}"
    
    def translate_subscript(self, subscript: ast.Subscript) -> str:
        value = self.translate_expr(subscript.value)
        slice_val = self.translate_expr(subscript.slice)
        return f"{value}[{slice_val}]"
    
    def translate_list(self, lst: ast.List) -> str:
        elements = ', '.join([self.translate_expr(el) for el in lst.elts])
        if self.target_lang == 'php':
            return f"array({elements})"
        return f"[{elements}]"
    
    def translate_dict(self, dct: ast.Dict) -> str:
        pairs = []
        for key, value in zip(dct.keys, dct.values):
            key_str = self.translate_expr(key)
            value_str = self.translate_expr(value)
            if self.target_lang == 'php':
                pairs.append(f"{key_str} => {value_str}")
            else:
                pairs.append(f"{key_str}: {value_str}")
        
        if self.target_lang == 'php':
            return f"array({', '.join(pairs)})"
        return f"{{{', '.join(pairs)}}}"
    
    def translate_tuple(self, tpl: ast.Tuple) -> str:
        elements = ', '.join([self.translate_expr(el) for el in tpl.elts])
        if self.target_lang == 'php':
            return f"array({elements})"
        elif self.target_lang in ['javascript', 'typescript']:
            return f"[{elements}]"
        return f"({elements})"
    
    def translate_unaryop(self, unaryop: ast.UnaryOp) -> str:
        operand = self.translate_expr(unaryop.operand)
        if isinstance(unaryop.op, ast.Not):
            return f"!{operand}"
        elif isinstance(unaryop.op, ast.UAdd):
            return f"+{operand}"
        elif isinstance(unaryop.op, ast.USub):
            return f"-{operand}"
        else:
            return operand
    
    def translate_boolop(self, boolop: ast.BoolOp) -> str:
        values = [self.translate_expr(v) for v in boolop.values]
        if isinstance(boolop.op, ast.And):
            return ' && '.join(values)
        elif isinstance(boolop.op, ast.Or):
            return ' || '.join(values)
        else:
            return ' && '.join(values)
    
    def translate_ifexp(self, ifexp: ast.IfExp) -> str:
        test = self.translate_expr(ifexp.test)
        body = self.translate_expr(ifexp.body)
        orelse = self.translate_expr(ifexp.orelse)
        return f"{test} ? {body} : {orelse}"
    
    def get_indent(self) -> str:
        return '    ' * self.indent_level
    
    def add_language_wrappers(self, code: str) -> str:
        if self.target_lang == 'java':
            lines = code.strip().split('\n')
            main_calls = []
            class_members = []
            
            for line in lines:
                stripped = line.strip()
                if stripped.startswith('public static void') or stripped.startswith('public class') or stripped.startswith('class '):
                    class_members.append(line)
                elif stripped and not stripped.startswith('}') and not stripped.startswith('{'):
                    main_calls.append('        ' + stripped)
            
            class_body = '\n'.join(class_members)
            main_body = '\n'.join(main_calls)
            
            return f"public class MeroTranslated {{\n{class_body}\n\n    public static void main(String[] args) {{\n{main_body}\n    }}\n}}"
        elif self.target_lang in ['c', 'cpp']:
            return f"#include <iostream>\nusing namespace std;\n\n{code}"
        elif self.target_lang == 'go':
            return f"package main\nimport \"fmt\"\n\nfunc main() {{\n{self.indent_code(code, 1)}\n}}"
        elif self.target_lang == 'php':
            return f"<?php\n{code}\n?>"
        elif self.target_lang == 'rust':
            return f"fn main() {{\n{self.indent_code(code, 1)}\n}}"
        else:
            return code
    
    def indent_code(self, code: str, level: int) -> str:
        indent = '    ' * level
        lines = code.split('\n')
        return '\n'.join(indent + line if line.strip() else '' for line in lines)
    
    def fallback_translate(self, code: str) -> str:
        return code

class CodeTranslator:
    def __init__(self):
        self.mero_translator = True
    
    def smart_translate(self, code: str, from_lang: str, to_lang: str) -> str:
        lang_map = {
            'Python': 'python', 'Java': 'java', 'C': 'c', 'C++': 'cpp',
            'C#': 'csharp', 'JavaScript': 'javascript', 'TypeScript': 'typescript',
            'Go': 'go', 'Rust': 'rust', 'Ruby': 'ruby', 'PHP': 'php',
            'Swift': 'swift', 'Kotlin': 'kotlin', 'Perl': 'perl', 'Lua': 'lua',
            'Dart': 'dart', 'Scala': 'scala'
        }
        
        from_lang_key = lang_map.get(from_lang, from_lang.lower())
        to_lang_key = lang_map.get(to_lang, to_lang.lower())
        
        if from_lang_key == 'python':
            translator = PythonToTargetTranslator(to_lang_key)
            return translator.translate(code)
        else:
            return code
