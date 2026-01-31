"""Static security scanner module."""
import os
import re
from typing import List, Dict, Any, Pattern


class SecurityScanner:
    """Scans repositories for security issues without execution."""
    
    def __init__(self, secret_patterns: List[str] = None, suspicious_patterns: List[str] = None):
        """Initialize security scanner.
        
        Args:
            secret_patterns: Regex patterns for detecting secrets
            suspicious_patterns: Regex patterns for detecting suspicious code
        """
        self.secret_patterns = [
            re.compile(pattern) for pattern in (secret_patterns or self._default_secret_patterns())
        ]
        self.suspicious_patterns = [
            re.compile(pattern) for pattern in (suspicious_patterns or self._default_suspicious_patterns())
        ]
    
    def _default_secret_patterns(self) -> List[str]:
        """Get default secret detection patterns."""
        return [
            r'(?i)(api[_-]?key|apikey)\s*[:=]\s*[\'"][a-zA-Z0-9]{20,}[\'"]',
            r'(?i)(secret|password|passwd|pwd)\s*[:=]\s*[\'"][^\'"]{8,}[\'"]',
            r'(?i)(token|auth)\s*[:=]\s*[\'"][a-zA-Z0-9]{20,}[\'"]',
            r'(?i)(private[_-]?key)\s*[:=]',
            r'(?i)(aws[_-]?access[_-]?key|aws[_-]?secret)',
            r'(?i)(github[_-]?token|gh[_-]?token)',
        ]
    
    def _default_suspicious_patterns(self) -> List[str]:
        """Get default suspicious code patterns."""
        return [
            r'eval\s*\(',
            r'exec\s*\(',
            r'__import__\s*\(',
            r'subprocess\.',
            r'os\.system\s*\(',
            r'os\.popen\s*\(',
            r'commands\.getoutput',
            r'pickle\.loads',
            r'marshal\.loads',
        ]
    
    def scan_repository(self, repo_path: str, file_extensions: List[str] = None) -> Dict[str, Any]:
        """Scan a repository for security issues.
        
        Args:
            repo_path: Path to cloned repository
            file_extensions: List of file extensions to scan (default: ['.py'])
            
        Returns:
            Dictionary with scan results
        """
        if file_extensions is None:
            file_extensions = ['.py']
        
        results = {
            'secrets_found': [],
            'suspicious_code': [],
            'files_scanned': 0,
            'total_issues': 0,
        }
        
        for root, dirs, files in os.walk(repo_path):
            # Skip .git directory
            if '.git' in dirs:
                dirs.remove('.git')
            
            for file in files:
                if any(file.endswith(ext) for ext in file_extensions):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)
                    
                    file_results = self._scan_file(file_path, rel_path)
                    results['secrets_found'].extend(file_results['secrets'])
                    results['suspicious_code'].extend(file_results['suspicious'])
                    results['files_scanned'] += 1
        
        results['total_issues'] = len(results['secrets_found']) + len(results['suspicious_code'])
        
        return results
    
    def _scan_file(self, file_path: str, rel_path: str) -> Dict[str, List[Dict[str, Any]]]:
        """Scan a single file for security issues.
        
        Args:
            file_path: Absolute path to file
            rel_path: Relative path to file (for reporting)
            
        Returns:
            Dictionary with secrets and suspicious code found
        """
        results = {
            'secrets': [],
            'suspicious': [],
        }
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
                
                # Scan for secrets
                for pattern in self.secret_patterns:
                    for match in pattern.finditer(content):
                        line_num = content[:match.start()].count('\n') + 1
                        results['secrets'].append({
                            'file': rel_path,
                            'line': line_num,
                            'type': 'potential_secret',
                            'pattern': pattern.pattern,
                            'context': lines[line_num - 1].strip() if line_num <= len(lines) else '',
                        })
                
                # Scan for suspicious code
                for pattern in self.suspicious_patterns:
                    for match in pattern.finditer(content):
                        line_num = content[:match.start()].count('\n') + 1
                        results['suspicious'].append({
                            'file': rel_path,
                            'line': line_num,
                            'type': 'suspicious_code',
                            'pattern': pattern.pattern,
                            'context': lines[line_num - 1].strip() if line_num <= len(lines) else '',
                        })
        except Exception as e:
            print(f"Error scanning {rel_path}: {e}")
        
        return results
