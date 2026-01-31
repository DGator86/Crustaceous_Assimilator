"""GitHub repository discovery module."""
from typing import List, Dict, Any
from github import Github, GithubException
import time


class RepoDiscovery:
    """Discovers GitHub repositories related to Moltbot and trading bots."""
    
    def __init__(self, github_token: str = None, max_results_per_query: int = 20):
        """Initialize repository discovery.
        
        Args:
            github_token: GitHub API token for authentication
            max_results_per_query: Maximum results per search query
        """
        self.github = Github(github_token) if github_token else Github()
        self.max_results_per_query = max_results_per_query
    
    def discover(self, search_queries: List[str]) -> List[Dict[str, Any]]:
        """Discover repositories based on search queries.
        
        Args:
            search_queries: List of search query strings
            
        Returns:
            List of repository information dictionaries
        """
        discovered_repos = []
        seen_repos = set()
        
        for query in search_queries:
            try:
                repos = self._search_repos(query)
                for repo in repos:
                    if repo['full_name'] not in seen_repos:
                        seen_repos.add(repo['full_name'])
                        discovered_repos.append(repo)
                
                # Rate limit handling
                time.sleep(1)
                
            except GithubException as e:
                print(f"Error searching for '{query}': {e}")
                continue
        
        return discovered_repos
    
    def _search_repos(self, query: str) -> List[Dict[str, Any]]:
        """Search for repositories with given query.
        
        Args:
            query: Search query string
            
        Returns:
            List of repository information dictionaries
        """
        repos = []
        try:
            results = self.github.search_repositories(
                query=query,
                sort='stars',
                order='desc'
            )
            
            count = 0
            for repo in results:
                if count >= self.max_results_per_query:
                    break
                
                repos.append(self._extract_repo_info(repo))
                count += 1
                
        except GithubException as e:
            error_msg = f"GitHub API error: {e.status}"
            if hasattr(e, 'message'):
                error_msg += f" - {e.message}"
            print(error_msg)
        
        return repos
    
    def _extract_repo_info(self, repo) -> Dict[str, Any]:
        """Extract relevant information from repository object.
        
        Args:
            repo: GitHub repository object
            
        Returns:
            Dictionary with repository information
        """
        return {
            'full_name': repo.full_name,
            'name': repo.name,
            'owner': repo.owner.login,
            'description': repo.description,
            'url': repo.html_url,
            'clone_url': repo.clone_url,
            'stars': repo.stargazers_count,
            'forks': repo.forks_count,
            'created_at': repo.created_at.isoformat() if repo.created_at else None,
            'updated_at': repo.updated_at.isoformat() if repo.updated_at else None,
            'pushed_at': repo.pushed_at.isoformat() if repo.pushed_at else None,
            'language': repo.language,
            'license': repo.license.name if repo.license else None,
            'topics': repo.get_topics(),
            'default_branch': repo.default_branch,
            'size': repo.size,
            'open_issues': repo.open_issues_count,
        }
