"""Artifact indexer module for organizing analyzed repositories."""
import json
import os
from typing import Dict, Any, List
from datetime import datetime, timezone


class ArtifactIndexer:
    """Indexes and organizes analyzed repository artifacts."""
    
    def __init__(self, artifacts_dir: str = "artifacts", index_file: str = "artifacts/index.json"):
        """Initialize artifact indexer.
        
        Args:
            artifacts_dir: Directory to store artifacts
            index_file: Path to index file
        """
        self.artifacts_dir = artifacts_dir
        self.index_file = index_file
        os.makedirs(artifacts_dir, exist_ok=True)
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Load existing index or create new one."""
        if os.path.exists(self.index_file):
            try:
                with open(self.index_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading index: {e}")
        
        return {
            'version': '1.0',
            'created_at': datetime.now(timezone.utc).isoformat(),
            'updated_at': datetime.now(timezone.utc).isoformat(),
            'repositories': [],
            'stats': {
                'total_repositories': 0,
                'total_strategies': 0,
                'total_indicators': 0,
                'total_security_issues': 0,
            }
        }
    
    def add_repository(self, repo_name: str, spec: Dict[str, Any], 
                      spec_path: str, doc_path: str) -> None:
        """Add repository to index.
        
        Args:
            repo_name: Repository full name
            spec: Repository specification
            spec_path: Path to JSON spec file
            doc_path: Path to markdown doc file
        """
        # Check if repository already exists
        existing = [r for r in self.index['repositories'] if r['name'] == repo_name]
        
        repo_entry = {
            'name': repo_name,
            'url': spec['metadata']['repository']['url'],
            'trustworthiness_score': spec['trustworthiness']['overall_score'],
            'trustworthiness_level': spec['trustworthiness']['level'],
            'security_issues': spec['security']['total_issues'],
            'strategies_count': spec['code_analysis']['summary']['total_strategies'],
            'indicators_count': spec['code_analysis']['summary']['total_indicators'],
            'spec_path': spec_path,
            'doc_path': doc_path,
            'added_at': datetime.now(timezone.utc).isoformat(),
        }
        
        if existing:
            # Update existing entry
            idx = self.index['repositories'].index(existing[0])
            self.index['repositories'][idx] = repo_entry
        else:
            # Add new entry
            self.index['repositories'].append(repo_entry)
        
        # Update stats
        self._update_stats()
        
        # Save index
        self.save_index()
    
    def _update_stats(self):
        """Update index statistics."""
        self.index['stats'] = {
            'total_repositories': len(self.index['repositories']),
            'total_strategies': sum(r['strategies_count'] for r in self.index['repositories']),
            'total_indicators': sum(r['indicators_count'] for r in self.index['repositories']),
            'total_security_issues': sum(r['security_issues'] for r in self.index['repositories']),
        }
        self.index['updated_at'] = datetime.now(timezone.utc).isoformat()
    
    def save_index(self):
        """Save index to file."""
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def get_repositories(self, min_score: float = None, 
                        max_security_issues: int = None) -> List[Dict[str, Any]]:
        """Get repositories with optional filtering.
        
        Args:
            min_score: Minimum trustworthiness score
            max_security_issues: Maximum number of security issues
            
        Returns:
            List of repository entries
        """
        repos = self.index['repositories']
        
        if min_score is not None:
            repos = [r for r in repos if r['trustworthiness_score'] >= min_score]
        
        if max_security_issues is not None:
            repos = [r for r in repos if r['security_issues'] <= max_security_issues]
        
        return repos
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics.
        
        Returns:
            Statistics dictionary
        """
        return self.index['stats']
    
    def generate_index_report(self) -> str:
        """Generate a markdown report of all indexed repositories.
        
        Returns:
            Markdown report string
        """
        md = []
        
        md.append("# Moltbot Repository Scout - Index Report\n")
        md.append(f"Generated: {datetime.now(timezone.utc).isoformat()}\n")
        
        # Stats
        md.append("## Statistics\n")
        stats = self.index['stats']
        md.append(f"- **Total Repositories**: {stats['total_repositories']}")
        md.append(f"- **Total Strategies**: {stats['total_strategies']}")
        md.append(f"- **Total Indicators**: {stats['total_indicators']}")
        md.append(f"- **Total Security Issues**: {stats['total_security_issues']}\n")
        
        # Repositories
        md.append("## Repositories\n")
        
        # Sort by trustworthiness score
        repos = sorted(self.index['repositories'], 
                      key=lambda x: x['trustworthiness_score'], 
                      reverse=True)
        
        for repo in repos:
            md.append(f"### {repo['name']}")
            md.append(f"- **URL**: {repo['url']}")
            md.append(f"- **Trust Score**: {repo['trustworthiness_score']} ({repo['trustworthiness_level']})")
            md.append(f"- **Security Issues**: {repo['security_issues']}")
            md.append(f"- **Strategies**: {repo['strategies_count']}")
            md.append(f"- **Indicators**: {repo['indicators_count']}")
            md.append(f"- **Spec**: `{repo['spec_path']}`")
            md.append(f"- **Docs**: `{repo['doc_path']}`")
            md.append(f"- **Added**: {repo['added_at']}\n")
        
        return '\n'.join(md)
