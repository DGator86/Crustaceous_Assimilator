"""Repository scoring and trustworthiness evaluation module."""
from typing import Dict, Any
from datetime import datetime, timezone
import math


class RepoScorer:
    """Scores repository trustworthiness based on multiple factors."""
    
    def __init__(self, weights: Dict[str, float] = None):
        """Initialize repository scorer.
        
        Args:
            weights: Dictionary of scoring weights for different factors
        """
        self.weights = weights or {
            'stars': 0.3,
            'age': 0.2,
            'commits': 0.2,
            'license': 0.15,
            'activity': 0.15
        }
    
    def score_repository(self, repo_info: Dict[str, Any]) -> Dict[str, Any]:
        """Score a repository for trustworthiness.
        
        Args:
            repo_info: Repository information dictionary
            
        Returns:
            Dictionary with overall score and component scores
        """
        scores = {
            'stars_score': self._score_stars(repo_info.get('stars', 0)),
            'age_score': self._score_age(repo_info.get('created_at')),
            'commits_score': self._score_commits(repo_info),
            'license_score': self._score_license(repo_info.get('license')),
            'activity_score': self._score_activity(repo_info),
        }
        
        # Calculate weighted overall score
        overall_score = sum(
            scores[f'{factor}_score'] * weight
            for factor, weight in self.weights.items()
        )
        
        return {
            'overall_score': round(overall_score, 3),
            'component_scores': scores,
            'trustworthiness': self._get_trustworthiness_level(overall_score)
        }
    
    def _score_stars(self, stars: int) -> float:
        """Score based on star count (logarithmic scale).
        
        Args:
            stars: Number of stars
            
        Returns:
            Score between 0 and 1
        """
        if stars <= 0:
            return 0.0
        # Logarithmic scoring: 10 stars = 0.5, 100 stars = 0.75, 1000 stars = 1.0
        score = math.log10(stars + 1) / 3.0
        return min(score, 1.0)
    
    def _score_age(self, created_at: str) -> float:
        """Score based on repository age.
        
        Args:
            created_at: ISO format creation date
            
        Returns:
            Score between 0 and 1
        """
        if not created_at:
            return 0.0
        
        try:
            created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            age_days = (datetime.now(timezone.utc) - created).days
            
            # Linear scoring: 30 days = 0.25, 180 days = 0.5, 365 days = 0.75, 730+ days = 1.0
            if age_days < 30:
                return 0.25
            elif age_days < 180:
                return 0.25 + (age_days - 30) / 150 * 0.25
            elif age_days < 365:
                return 0.5 + (age_days - 180) / 185 * 0.25
            else:
                return min(0.75 + (age_days - 365) / 365 * 0.25, 1.0)
        except (ValueError, AttributeError):
            return 0.0
    
    def _score_commits(self, repo_info: Dict[str, Any]) -> float:
        """Score based on commit activity (estimated from repo size).
        
        Args:
            repo_info: Repository information
            
        Returns:
            Score between 0 and 1
        """
        # Using repo size as proxy for commits (not perfect but available)
        size = repo_info.get('size', 0)
        
        if size <= 0:
            return 0.0
        
        # Logarithmic scoring based on size
        score = math.log10(size + 1) / 4.0
        return min(score, 1.0)
    
    def _score_license(self, license_name: str) -> float:
        """Score based on license presence and type.
        
        Args:
            license_name: Name of the license
            
        Returns:
            Score between 0 and 1
        """
        if not license_name:
            return 0.0
        
        # Preferred open source licenses get higher scores
        preferred_licenses = {
            'MIT License': 1.0,
            'Apache License 2.0': 1.0,
            'GNU General Public License v3.0': 0.9,
            'BSD 3-Clause "New" or "Revised" License': 1.0,
            'BSD 2-Clause "Simplified" License': 1.0,
        }
        
        return preferred_licenses.get(license_name, 0.7)
    
    def _score_activity(self, repo_info: Dict[str, Any]) -> float:
        """Score based on recent activity.
        
        Args:
            repo_info: Repository information
            
        Returns:
            Score between 0 and 1
        """
        pushed_at = repo_info.get('pushed_at')
        if not pushed_at:
            return 0.0
        
        try:
            last_push = datetime.fromisoformat(pushed_at.replace('Z', '+00:00'))
            days_since_push = (datetime.now(timezone.utc) - last_push).days
            
            # Recent activity gets higher scores
            if days_since_push < 7:
                return 1.0
            elif days_since_push < 30:
                return 0.9
            elif days_since_push < 90:
                return 0.7
            elif days_since_push < 180:
                return 0.5
            elif days_since_push < 365:
                return 0.3
            else:
                return 0.1
        except (ValueError, AttributeError):
            return 0.0
    
    def _get_trustworthiness_level(self, score: float) -> str:
        """Convert numeric score to trustworthiness level.
        
        Args:
            score: Overall score (0-1)
            
        Returns:
            Trustworthiness level string
        """
        if score >= 0.8:
            return 'high'
        elif score >= 0.6:
            return 'medium-high'
        elif score >= 0.4:
            return 'medium'
        elif score >= 0.2:
            return 'low-medium'
        else:
            return 'low'
