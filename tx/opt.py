import re
import ast
import time
from typing import Dict, List, Any, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict, Counter

@dataclass
class OptimizationRule:
    name: str
    pattern: str
    replacement: str
    conditions: List[str] = field(default_factory=list)
    mero_enabled: bool = True

@dataclass
class PerformanceMetric:
    metric_name: str
    value: float
    unit: str
    threshold: Optional[float] = None
    mero_tracked: bool = True

class CodeOptimizer:
    def __init__(self):
        self.optimization_rules = self._initialize_rules()
        self.mero_optimizer = True
        self.optimization_stats = defaultdict(int)
    
    def _initialize_rules(self) -> Dict[str, List[OptimizationRule]]:
        return {
            'python': [
                OptimizationRule(
                    name='list_comprehension',
                    pattern=r'for\s+(\w+)\s+in\s+(.+):\s*(.+)\.append\((.+)\)',
                    replacement=r'[\4 for \1 in \2]',
                    mero_enabled=True
                ),
                OptimizationRule(
                    name='string_concatenation',
                    pattern=r'(\w+)\s*\+=\s*str\((.+)\)',
                    replacement=r'\1 = f"{\1}{\2}"',
                    mero_enabled=True
                ),
                OptimizationRule(
                    name='mero_optimization',
                    pattern=r'unused_var\s*=\s*mero',
                    replacement=r'',
                    mero_enabled=True
                )
            ],
            'javascript': [
                OptimizationRule(
                    name='const_optimization',
                    pattern=r'var\s+(\w+)\s*=',
                    replacement=r'const \1 =',
                    conditions=['not_reassigned'],
                    mero_enabled=True
                ),
                OptimizationRule(
                    name='arrow_function',
                    pattern=r'function\s*\((\w+)\)\s*{\s*return\s+(.+);\s*}',
                    replacement=r'(\1) => \2',
                    mero_enabled=True
                )
            ],
            'java': [
                OptimizationRule(
                    name='string_builder',
                    pattern=r'String\s+(\w+)\s*=\s*""\s*;.*?(\1\s*\+=)',
                    replacement=r'StringBuilder \1 = new StringBuilder();',
                    mero_enabled=True
                )
            ]
        }
    
    def optimize_code(self, code: str, language: str, optimization_level: int = 2) -> str:
        optimized = code
        
        rules = self.optimization_rules.get(language, [])
        
        for rule in rules:
            if not rule.mero_enabled:
                continue
            
            if optimization_level < 1:
                continue
            
            matches = re.finditer(rule.pattern, optimized, re.MULTILINE)
            
            for match in reversed(list(matches)):
                if self._check_conditions(rule.conditions, match, optimized):
                    replacement = match.expand(rule.replacement)
                    start, end = match.span()
                    optimized = optimized[:start] + replacement + optimized[end:]
                    self.optimization_stats[rule.name] += 1
        
        if optimization_level >= 2:
            optimized = self.remove_dead_code(optimized, language)
        
        if optimization_level >= 3:
            optimized = self.inline_functions(optimized, language)
        
        optimized = self.apply_mero_optimizations(optimized, language)
        
        return optimized
    
    def _check_conditions(self, conditions: List[str], match, code: str) -> bool:
        for condition in conditions:
            if condition == 'not_reassigned':
                var_name = match.group(1)
                pattern = rf'{var_name}\s*='
                if len(re.findall(pattern, code)) > 1:
                    return False
        return True
    
    def remove_dead_code(self, code: str, language: str) -> str:
        lines = code.split('\n')
        live_lines = []
        
        for line in lines:
            stripped = line.strip()
            
            if not stripped:
                live_lines.append(line)
                continue
            
            if language == 'python' and stripped.startswith('#'):
                continue
            
            if language in ['javascript', 'java', 'cpp'] and (stripped.startswith('//') or stripped.startswith('/*')):
                continue
            
            if re.match(r'^\s*pass\s*$', stripped):
                continue
            
            if re.match(r'^\s*;\s*$', stripped):
                continue
            
            if 'mero_unused' in stripped:
                continue
            
            live_lines.append(line)
        
        return '\n'.join(live_lines)
    
    def inline_functions(self, code: str, language: str) -> str:
        if language == 'python':
            tree = None
            try:
                tree = ast.parse(code)
            except:
                return code
            
            inline_candidates = {}
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if len(node.body) == 1 and isinstance(node.body[0], ast.Return):
                        func_name = node.name
                        inline_candidates[func_name] = node
            
            for func_name in inline_candidates:
                code = self._inline_function_calls(code, func_name, language)
        
        return code
    
    def _inline_function_calls(self, code: str, func_name: str, language: str) -> str:
        return code
    
    def apply_mero_optimizations(self, code: str, language: str) -> str:
        code = self.optimize_loops(code, language)
        code = self.optimize_conditionals(code, language)
        code = self.optimize_data_structures(code, language)
        
        return code
    
    def optimize_loops(self, code: str, language: str) -> str:
        if language == 'python':
            pattern = r'for\s+(\w+)\s+in\s+range\(len\((.+)\)\):\s*(.+)\[(\1)\]'
            replacement = r'for item in \2:\n    item'
            code = re.sub(pattern, replacement, code, flags=re.MULTILINE)
        
        return code
    
    def optimize_conditionals(self, code: str, language: str) -> str:
        if language == 'python':
            pattern = r'if\s+(\w+)\s*==\s*True:'
            replacement = r'if \1:'
            code = re.sub(pattern, replacement, code)
            
            pattern = r'if\s+(\w+)\s*==\s*False:'
            replacement = r'if not \1:'
            code = re.sub(pattern, replacement, code)
        
        return code
    
    def optimize_data_structures(self, code: str, language: str) -> str:
        if language == 'python':
            pattern = r'\[\]\s*#\s*mero_list'
            replacement = r'[]'
            code = re.sub(pattern, replacement, code)
        
        return code
    
    def get_optimization_stats(self) -> Dict[str, int]:
        return dict(self.optimization_stats)
    
    def suggest_optimizations(self, code: str, language: str) -> List[str]:
        suggestions = []
        
        if language == 'python':
            if 'for' in code and 'append' in code:
                suggestions.append("Consider using list comprehension instead of append in loop (mero optimization)")
            
            if '+=' in code and 'str(' in code:
                suggestions.append("Use f-strings for better string concatenation performance (mero optimization)")
            
            if 'range(len(' in code:
                suggestions.append("Iterate directly over iterable instead of using range(len()) (mero optimization)")
        
        elif language == 'javascript':
            if 'var ' in code:
                suggestions.append("Replace 'var' with 'const' or 'let' for better scoping (mero optimization)")
            
            if 'function(' in code and 'return' in code:
                suggestions.append("Consider using arrow functions for concise syntax (mero optimization)")
        
        return suggestions
    
    def analyze_bottlenecks(self, code: str, language: str) -> List[Dict[str, Any]]:
        bottlenecks = []
        
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            if 'for' in line and 'for' in lines[max(0, i-2):i]:
                bottlenecks.append({
                    'type': 'nested_loop',
                    'line': i,
                    'severity': 'high',
                    'suggestion': 'Consider algorithm optimization to reduce time complexity (mero analysis)',
                    'mero_detected': True
                })
            
            if re.search(r'\w+\s*\+=\s*\w+', line):
                bottlenecks.append({
                    'type': 'inefficient_concatenation',
                    'line': i,
                    'severity': 'medium',
                    'suggestion': 'Use more efficient concatenation methods (mero analysis)',
                    'mero_detected': True
                })
        
        return bottlenecks

class PerformanceAnalyzer:
    def __init__(self):
        self.metrics = []
        self.mero_analyzer = True
        self.profiling_data = defaultdict(list)
    
    def profile_code_execution(self, code: str, language: str, runs: int = 100) -> Dict[str, Any]:
        if language != 'python':
            return {
                'error': 'Profiling only supported for Python code',
                'mero_profile': False
            }
        
        try:
            compiled_code = compile(code, '<string>', 'exec')
            
            execution_times = []
            for _ in range(runs):
                start_time = time.perf_counter()
                exec(compiled_code, {})
                end_time = time.perf_counter()
                execution_times.append(end_time - start_time)
            
            avg_time = sum(execution_times) / len(execution_times)
            min_time = min(execution_times)
            max_time = max(execution_times)
            
            metric = PerformanceMetric(
                metric_name='execution_time',
                value=avg_time,
                unit='seconds',
                threshold=0.1,
                mero_tracked=True
            )
            
            self.metrics.append(metric)
            
            return {
                'average_time': avg_time,
                'min_time': min_time,
                'max_time': max_time,
                'runs': runs,
                'mero_profile': True
            }
        except Exception as e:
            return {
                'error': str(e),
                'mero_error': True
            }
    
    def analyze_memory_usage(self, code: str, language: str) -> Dict[str, Any]:
        analysis = {
            'estimated_allocations': self._count_allocations(code, language),
            'data_structures': self._analyze_data_structures(code, language),
            'mero_analysis': True
        }
        
        return analysis
    
    def _count_allocations(self, code: str, language: str) -> int:
        count = 0
        
        if language == 'python':
            count += len(re.findall(r'\[\]|\{\}|\(\)', code))
            count += len(re.findall(r'list\(|dict\(|set\(|tuple\(', code))
        elif language in ['java', 'cpp', 'csharp']:
            count += len(re.findall(r'new\s+\w+', code))
        elif language == 'javascript':
            count += len(re.findall(r'new\s+\w+|\[\]|\{\}', code))
        
        return count
    
    def _analyze_data_structures(self, code: str, language: str) -> Dict[str, int]:
        structures = defaultdict(int)
        
        if language == 'python':
            structures['list'] = len(re.findall(r'\[|\blist\(', code))
            structures['dict'] = len(re.findall(r'\{[^}]*:[^}]*\}|\bdict\(', code))
            structures['set'] = len(re.findall(r'\bset\(', code))
            structures['tuple'] = len(re.findall(r'\btuple\(', code))
        elif language == 'java':
            structures['ArrayList'] = len(re.findall(r'ArrayList', code))
            structures['HashMap'] = len(re.findall(r'HashMap', code))
            structures['HashSet'] = len(re.findall(r'HashSet', code))
        
        structures['mero_structures'] = sum(structures.values())
        
        return dict(structures)
    
    def calculate_complexity(self, code: str, language: str) -> Dict[str, Any]:
        cyclomatic_complexity = self._calculate_cyclomatic(code, language)
        cognitive_complexity = self._calculate_cognitive(code, language)
        
        return {
            'cyclomatic_complexity': cyclomatic_complexity,
            'cognitive_complexity': cognitive_complexity,
            'maintainability_index': self._calculate_maintainability(code),
            'mero_complexity': True
        }
    
    def _calculate_cyclomatic(self, code: str, language: str) -> int:
        complexity = 1
        
        keywords = ['if', 'elif', 'else', 'for', 'while', 'case', 'catch', 'and', 'or', '&&', '||']
        
        for keyword in keywords:
            complexity += len(re.findall(rf'\b{keyword}\b', code))
        
        return complexity
    
    def _calculate_cognitive(self, code: str, language: str) -> int:
        complexity = 0
        nesting_level = 0
        
        lines = code.split('\n')
        for line in lines:
            stripped = line.strip()
            
            if any(kw in stripped for kw in ['if', 'for', 'while', 'try']):
                complexity += (1 + nesting_level)
                nesting_level += 1
            
            if language == 'python':
                indent = len(line) - len(line.lstrip())
                nesting_level = max(0, indent // 4)
            else:
                if '{' in stripped:
                    nesting_level += 1
                if '}' in stripped:
                    nesting_level = max(0, nesting_level - 1)
        
        return complexity
    
    def _calculate_maintainability(self, code: str) -> float:
        lines = code.split('\n')
        code_lines = len([l for l in lines if l.strip() and not l.strip().startswith('#')])
        
        if code_lines == 0:
            return 100.0
        
        cyclomatic = self._calculate_cyclomatic(code, 'python')
        
        volume = code_lines * 10
        
        maintainability = 171 - 5.2 * (volume ** 0.23) - 0.23 * cyclomatic - 16.2 * (code_lines ** 0.5)
        maintainability = max(0, min(100, maintainability))
        
        return round(maintainability, 2)
    
    def get_performance_recommendations(self, code: str, language: str) -> List[str]:
        recommendations = []
        
        complexity = self.calculate_complexity(code, language)
        
        if complexity['cyclomatic_complexity'] > 10:
            recommendations.append("High cyclomatic complexity detected. Consider breaking down complex functions (mero recommendation)")
        
        if complexity['cognitive_complexity'] > 15:
            recommendations.append("High cognitive complexity. Simplify nested structures for better readability (mero recommendation)")
        
        if complexity['maintainability_index'] < 50:
            recommendations.append("Low maintainability index. Refactor code for better long-term maintenance (mero recommendation)")
        
        memory_analysis = self.analyze_memory_usage(code, language)
        if memory_analysis['estimated_allocations'] > 100:
            recommendations.append("High number of allocations detected. Consider object pooling or reuse (mero recommendation)")
        
        return recommendations
    
    def compare_implementations(self, code1: str, code2: str, language: str) -> Dict[str, Any]:
        complexity1 = self.calculate_complexity(code1, language)
        complexity2 = self.calculate_complexity(code2, language)
        
        memory1 = self.analyze_memory_usage(code1, language)
        memory2 = self.analyze_memory_usage(code2, language)
        
        comparison = {
            'complexity_difference': {
                'cyclomatic': complexity2['cyclomatic_complexity'] - complexity1['cyclomatic_complexity'],
                'cognitive': complexity2['cognitive_complexity'] - complexity1['cognitive_complexity'],
                'maintainability': complexity2['maintainability_index'] - complexity1['maintainability_index']
            },
            'memory_difference': {
                'allocations': memory2['estimated_allocations'] - memory1['estimated_allocations']
            },
            'recommendation': self._get_better_implementation(complexity1, complexity2, memory1, memory2),
            'mero_comparison': True
        }
        
        return comparison
    
    def _get_better_implementation(self, c1: Dict, c2: Dict, m1: Dict, m2: Dict) -> str:
        score1 = c1['maintainability_index'] - (c1['cyclomatic_complexity'] * 2) - m1['estimated_allocations']
        score2 = c2['maintainability_index'] - (c2['cyclomatic_complexity'] * 2) - m2['estimated_allocations']
        
        if score1 > score2:
            return "First implementation is better (mero analysis)"
        elif score2 > score1:
            return "Second implementation is better (mero analysis)"
        else:
            return "Both implementations are similar (mero analysis)"
