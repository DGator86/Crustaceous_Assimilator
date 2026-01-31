"""Normalizer module for converting parsed data to JSON specs."""
import json
import os
from typing import Dict, Any, List
from datetime import datetime


class SpecNormalizer:
    """Normalizes parsed data into standardized JSON specifications."""
    
    def normalize(self, repo_info: Dict[str, Any], score_info: Dict[str, Any],
                  security_info: Dict[str, Any], parsed_info: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize all data into a standardized specification.
        
        Args:
            repo_info: Repository metadata
            score_info: Repository scores
            security_info: Security scan results
            parsed_info: Parsed code elements
            
        Returns:
            Normalized specification dictionary
        """
        spec = {
            'metadata': {
                'spec_version': '1.0',
                'generated_at': datetime.utcnow().isoformat(),
                'repository': {
                    'name': repo_info.get('full_name'),
                    'url': repo_info.get('url'),
                    'description': repo_info.get('description'),
                    'language': repo_info.get('language'),
                    'license': repo_info.get('license'),
                    'created_at': repo_info.get('created_at'),
                    'updated_at': repo_info.get('updated_at'),
                }
            },
            'trustworthiness': {
                'overall_score': score_info.get('overall_score', 0),
                'level': score_info.get('trustworthiness', 'unknown'),
                'components': score_info.get('component_scores', {}),
                'metrics': {
                    'stars': repo_info.get('stars', 0),
                    'forks': repo_info.get('forks', 0),
                    'open_issues': repo_info.get('open_issues', 0),
                }
            },
            'security': {
                'scanned': True,
                'files_scanned': security_info.get('files_scanned', 0),
                'total_issues': security_info.get('total_issues', 0),
                'secrets_found': len(security_info.get('secrets_found', [])),
                'suspicious_code_found': len(security_info.get('suspicious_code', [])),
                'issues': {
                    'secrets': security_info.get('secrets_found', []),
                    'suspicious': security_info.get('suspicious_code', []),
                }
            },
            'code_analysis': {
                'files_parsed': parsed_info.get('files_parsed', 0),
                'parse_errors': len(parsed_info.get('parse_errors', [])),
                'strategies': self._normalize_strategies(parsed_info.get('strategies', [])),
                'indicators': self._normalize_indicators(parsed_info.get('indicators', [])),
                'risk_management': self._normalize_risk_logic(parsed_info.get('risk_logic', [])),
                'summary': {
                    'total_strategies': len(parsed_info.get('strategies', [])),
                    'total_indicators': len(parsed_info.get('indicators', [])),
                    'total_risk_functions': len(parsed_info.get('risk_logic', [])),
                    'total_classes': len(parsed_info.get('classes', [])),
                    'total_functions': len(parsed_info.get('functions', [])),
                }
            }
        }
        
        return spec
    
    def _normalize_strategies(self, strategies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize strategy information.
        
        Args:
            strategies: List of strategy dictionaries
            
        Returns:
            Normalized strategy list
        """
        return [
            {
                'name': s.get('name'),
                'type': s.get('type'),
                'file': s.get('file'),
                'line': s.get('line'),
                'description': s.get('docstring', '').split('\n')[0] if s.get('docstring') else '',
                'parameters': s.get('args', []) if s.get('type') == 'function' else [],
                'methods': s.get('methods', []) if s.get('type') == 'class' else [],
            }
            for s in strategies
        ]
    
    def _normalize_indicators(self, indicators: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize indicator information.
        
        Args:
            indicators: List of indicator dictionaries
            
        Returns:
            Normalized indicator list
        """
        return [
            {
                'name': i.get('name'),
                'file': i.get('file'),
                'line': i.get('line'),
                'description': i.get('docstring', '').split('\n')[0] if i.get('docstring') else '',
                'parameters': i.get('args', []),
            }
            for i in indicators
        ]
    
    def _normalize_risk_logic(self, risk_logic: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize risk management logic.
        
        Args:
            risk_logic: List of risk logic dictionaries
            
        Returns:
            Normalized risk logic list
        """
        return [
            {
                'name': r.get('name'),
                'file': r.get('file'),
                'line': r.get('line'),
                'description': r.get('docstring', '').split('\n')[0] if r.get('docstring') else '',
                'parameters': r.get('args', []),
            }
            for r in risk_logic
        ]
    
    def save_spec(self, spec: Dict[str, Any], output_path: str):
        """Save specification to JSON file.
        
        Args:
            spec: Specification dictionary
            output_path: Path to save JSON file
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(spec, f, indent=2, ensure_ascii=False)
    
    def generate_markdown_doc(self, spec: Dict[str, Any]) -> str:
        """Generate markdown documentation from specification.
        
        Args:
            spec: Specification dictionary
            
        Returns:
            Markdown documentation string
        """
        md = []
        
        # Header
        repo_name = spec['metadata']['repository']['name']
        md.append(f"# {repo_name}\n")
        
        # Description
        desc = spec['metadata']['repository']['description']
        if desc:
            md.append(f"{desc}\n")
        
        # Metadata
        md.append("## Repository Information\n")
        md.append(f"- **URL**: {spec['metadata']['repository']['url']}")
        md.append(f"- **Language**: {spec['metadata']['repository']['language']}")
        md.append(f"- **License**: {spec['metadata']['repository']['license']}")
        md.append(f"- **Created**: {spec['metadata']['repository']['created_at']}")
        md.append(f"- **Last Updated**: {spec['metadata']['repository']['updated_at']}\n")
        
        # Trustworthiness
        md.append("## Trustworthiness Analysis\n")
        trust = spec['trustworthiness']
        md.append(f"- **Overall Score**: {trust['overall_score']} ({trust['level']})")
        md.append(f"- **Stars**: {trust['metrics']['stars']}")
        md.append(f"- **Forks**: {trust['metrics']['forks']}")
        md.append(f"- **Open Issues**: {trust['metrics']['open_issues']}\n")
        
        # Security
        md.append("## Security Scan Results\n")
        sec = spec['security']
        md.append(f"- **Files Scanned**: {sec['files_scanned']}")
        md.append(f"- **Total Issues**: {sec['total_issues']}")
        md.append(f"- **Secrets Found**: {sec['secrets_found']}")
        md.append(f"- **Suspicious Code Patterns**: {sec['suspicious_code_found']}\n")
        
        # Code Analysis
        md.append("## Code Analysis\n")
        analysis = spec['code_analysis']
        md.append(f"- **Files Parsed**: {analysis['files_parsed']}")
        md.append(f"- **Strategies Found**: {analysis['summary']['total_strategies']}")
        md.append(f"- **Indicators Found**: {analysis['summary']['total_indicators']}")
        md.append(f"- **Risk Management Functions**: {analysis['summary']['total_risk_functions']}\n")
        
        # Strategies
        if analysis['strategies']:
            md.append("### Strategies\n")
            for strategy in analysis['strategies']:
                md.append(f"- **{strategy['name']}** ({strategy['type']})")
                if strategy['description']:
                    md.append(f"  - {strategy['description']}")
                md.append(f"  - Location: `{strategy['file']}:{strategy['line']}`\n")
        
        # Indicators
        if analysis['indicators']:
            md.append("### Indicators\n")
            for indicator in analysis['indicators']:
                md.append(f"- **{indicator['name']}**")
                if indicator['description']:
                    md.append(f"  - {indicator['description']}")
                md.append(f"  - Location: `{indicator['file']}:{indicator['line']}`\n")
        
        return '\n'.join(md)
    
    def save_markdown_doc(self, spec: Dict[str, Any], output_path: str):
        """Save markdown documentation.
        
        Args:
            spec: Specification dictionary
            output_path: Path to save markdown file
        """
        md_content = self.generate_markdown_doc(spec)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
