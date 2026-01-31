"""Safe repository cloner module (without execution)."""
import os
import shutil
from typing import Optional, Dict, Any
from git import Repo, GitCommandError
import subprocess


class SafeCloner:
    """Safely clones repositories without executing any code."""
    
    def __init__(self, clone_dir: str = "data/repos", max_depth: int = 1, timeout: int = 300):
        """Initialize safe cloner.
        
        Args:
            clone_dir: Directory to clone repositories into
            max_depth: Git clone depth (shallow clone)
            timeout: Timeout in seconds for clone operation
        """
        self.clone_dir = clone_dir
        self.max_depth = max_depth
        self.timeout = timeout
        os.makedirs(clone_dir, exist_ok=True)
    
    def clone_repository(self, clone_url: str, repo_name: str) -> Dict[str, Any]:
        """Safely clone a repository.
        
        Args:
            clone_url: Git clone URL
            repo_name: Name for the cloned repository
            
        Returns:
            Dictionary with clone status and path
        """
        safe_name = repo_name.replace('/', '_')
        target_path = os.path.join(self.clone_dir, safe_name)
        
        # Remove existing directory if present
        if os.path.exists(target_path):
            shutil.rmtree(target_path)
        
        try:
            # Use shallow clone for efficiency and safety
            repo = Repo.clone_from(
                clone_url,
                target_path,
                depth=self.max_depth,
                no_checkout=False,  # We do checkout but won't execute
            )
            
            # Disable automatic execution of hooks
            self._disable_hooks(target_path)
            
            return {
                'success': True,
                'path': target_path,
                'message': f'Successfully cloned {repo_name}',
                'branch': repo.active_branch.name if repo.active_branch else 'unknown',
            }
            
        except GitCommandError as e:
            return {
                'success': False,
                'path': None,
                'message': f'Failed to clone {repo_name}: {str(e)}',
            }
        except Exception as e:
            return {
                'success': False,
                'path': None,
                'message': f'Unexpected error cloning {repo_name}: {str(e)}',
            }
    
    def _disable_hooks(self, repo_path: str):
        """Disable Git hooks to prevent code execution.
        
        Args:
            repo_path: Path to cloned repository
        """
        hooks_dir = os.path.join(repo_path, '.git', 'hooks')
        if os.path.exists(hooks_dir):
            # Rename hooks directory to prevent execution
            disabled_hooks_dir = os.path.join(repo_path, '.git', 'hooks.disabled')
            if not os.path.exists(disabled_hooks_dir):
                try:
                    os.rename(hooks_dir, disabled_hooks_dir)
                except Exception:
                    pass  # Best effort
    
    def cleanup_repository(self, repo_name: str) -> bool:
        """Clean up a cloned repository.
        
        Args:
            repo_name: Name of the repository to clean up
            
        Returns:
            True if cleanup successful, False otherwise
        """
        safe_name = repo_name.replace('/', '_')
        target_path = os.path.join(self.clone_dir, safe_name)
        
        if os.path.exists(target_path):
            try:
                shutil.rmtree(target_path)
                return True
            except Exception as e:
                print(f"Error cleaning up {repo_name}: {e}")
                return False
        return True
