"""AST-based code parser module for strategy extraction."""
import ast
import os
from typing import Dict, Any, List, Set


class StrategyParser:
    """Parses Python code using AST to extract trading strategies without imports."""
    
    def __init__(self, max_file_size: int = 1048576):
        """Initialize strategy parser.
        
        Args:
            max_file_size: Maximum file size to parse (default: 1MB)
        """
        self.max_file_size = max_file_size
    
    def parse_repository(self, repo_path: str) -> Dict[str, Any]:
        """Parse all Python files in repository.
        
        Args:
            repo_path: Path to cloned repository
            
        Returns:
            Dictionary with extracted information
        """
        results = {
            'strategies': [],
            'indicators': [],
            'risk_logic': [],
            'classes': [],
            'functions': [],
            'files_parsed': 0,
            'parse_errors': [],
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Skip .git and common non-source directories
            dirs[:] = [d for d in dirs if d not in {'.git', '__pycache__', 'venv', 'env', 'node_modules'}]
            
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)
                    
                    # Skip files that are too large
                    if os.path.getsize(file_path) > self.max_file_size:
                        continue
                    
                    file_results = self._parse_file(file_path, rel_path)
                    if file_results:
                        results['strategies'].extend(file_results.get('strategies', []))
                        results['indicators'].extend(file_results.get('indicators', []))
                        results['risk_logic'].extend(file_results.get('risk_logic', []))
                        results['classes'].extend(file_results.get('classes', []))
                        results['functions'].extend(file_results.get('functions', []))
                        results['files_parsed'] += 1
                    else:
                        results['parse_errors'].append(rel_path)
        
        return results
    
    def _parse_file(self, file_path: str, rel_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """Parse a single Python file using AST.
        
        Args:
            file_path: Absolute path to file
            rel_path: Relative path for reporting
            
        Returns:
            Dictionary with extracted elements
        """
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=rel_path)
            
            visitor = StrategyVisitor(rel_path)
            visitor.visit(tree)
            
            return {
                'strategies': visitor.strategies,
                'indicators': visitor.indicators,
                'risk_logic': visitor.risk_logic,
                'classes': visitor.classes,
                'functions': visitor.functions,
            }
            
        except SyntaxError as e:
            print(f"Syntax error in {rel_path}: {e}")
            return None
        except Exception as e:
            print(f"Error parsing {rel_path}: {e}")
            return None


class StrategyVisitor(ast.NodeVisitor):
    """AST visitor for extracting trading strategy elements."""
    
    def __init__(self, file_path: str):
        """Initialize visitor.
        
        Args:
            file_path: Path to file being parsed
        """
        self.file_path = file_path
        self.strategies = []
        self.indicators = []
        self.risk_logic = []
        self.classes = []
        self.functions = []
        
        # Keywords for identification
        self.strategy_keywords = {'strategy', 'trade', 'signal', 'backtest', 'order', 'position'}
        self.indicator_keywords = {'indicator', 'sma', 'ema', 'rsi', 'macd', 'bollinger', 'moving_average'}
        self.risk_keywords = {'risk', 'stop_loss', 'take_profit', 'position_size', 'drawdown'}
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit class definitions.
        
        Args:
            node: AST ClassDef node
        """
        class_info = {
            'name': node.name,
            'file': self.file_path,
            'line': node.lineno,
            'bases': [self._get_name(base) for base in node.bases],
            'methods': [],
            'docstring': ast.get_docstring(node),
        }
        
        # Extract methods
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                class_info['methods'].append({
                    'name': item.name,
                    'args': [arg.arg for arg in item.args.args],
                    'line': item.lineno,
                })
        
        self.classes.append(class_info)
        
        # Check if it's a strategy class
        if self._contains_keywords(node.name.lower(), self.strategy_keywords):
            self.strategies.append({
                'type': 'class',
                'name': node.name,
                'file': self.file_path,
                'line': node.lineno,
                'docstring': class_info['docstring'],
                'methods': [m['name'] for m in class_info['methods']],
            })
        
        # Continue visiting child nodes
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definitions.
        
        Args:
            node: AST FunctionDef node
        """
        func_info = {
            'name': node.name,
            'file': self.file_path,
            'line': node.lineno,
            'args': [arg.arg for arg in node.args.args],
            'returns': self._get_name(node.returns) if node.returns else None,
            'docstring': ast.get_docstring(node),
        }
        
        self.functions.append(func_info)
        
        # Check if it's a strategy function
        if self._contains_keywords(node.name.lower(), self.strategy_keywords):
            self.strategies.append({
                'type': 'function',
                'name': node.name,
                'file': self.file_path,
                'line': node.lineno,
                'docstring': func_info['docstring'],
                'args': func_info['args'],
            })
        
        # Check if it's an indicator function
        if self._contains_keywords(node.name.lower(), self.indicator_keywords):
            self.indicators.append({
                'name': node.name,
                'file': self.file_path,
                'line': node.lineno,
                'docstring': func_info['docstring'],
                'args': func_info['args'],
            })
        
        # Check if it's risk management logic
        if self._contains_keywords(node.name.lower(), self.risk_keywords):
            self.risk_logic.append({
                'name': node.name,
                'file': self.file_path,
                'line': node.lineno,
                'docstring': func_info['docstring'],
                'args': func_info['args'],
            })
        
        # Continue visiting child nodes
        self.generic_visit(node)
    
    def _get_name(self, node) -> str:
        """Get name from AST node.
        
        Args:
            node: AST node
            
        Returns:
            String representation of name
        """
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif node is None:
            return None
        else:
            return str(node)
    
    def _contains_keywords(self, text: str, keywords: Set[str]) -> bool:
        """Check if text contains any of the keywords.
        
        Args:
            text: Text to check
            keywords: Set of keywords
            
        Returns:
            True if any keyword found
        """
        return any(keyword in text for keyword in keywords)
