"""Example script demonstrating programmatic use of moltbot-repo-scout."""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from moltbot_scout.config import Config
from moltbot_scout.discovery import RepoDiscovery
from moltbot_scout.scoring import RepoScorer
from moltbot_scout.cloner import SafeCloner
from moltbot_scout.security import SecurityScanner
from moltbot_scout.parser import StrategyParser
from moltbot_scout.normalizer import SpecNormalizer
from moltbot_scout.indexer import ArtifactIndexer


def main():
    """Example of using moltbot-repo-scout programmatically."""
    print("🤖 Moltbot Repository Scout - Example\n")
    
    # Load configuration
    config = Config()
    
    # Initialize components
    discovery = RepoDiscovery(
        github_token=os.getenv('GITHUB_TOKEN'),
        max_results_per_query=3  # Small number for demo
    )
    
    scorer = RepoScorer()
    cloner = SafeCloner()
    scanner = SecurityScanner()
    parser = StrategyParser()
    normalizer = SpecNormalizer()
    indexer = ArtifactIndexer()
    
    # Search for repositories
    print("🔍 Searching for repositories...")
    repos = discovery.discover(['trading bot python stars:>50'])
    print(f"Found {len(repos)} repositories\n")
    
    # Analyze first repository as example
    if repos:
        repo = repos[0]
        print(f"📦 Analyzing: {repo['full_name']}")
        print(f"   Description: {repo['description']}")
        
        # Score it
        score_info = scorer.score_repository(repo)
        print(f"\n⭐ Trustworthiness Score: {score_info['overall_score']}")
        print(f"   Level: {score_info['trustworthiness']}")
        print(f"   Component Scores:")
        for component, score in score_info['component_scores'].items():
            print(f"     - {component}: {score:.3f}")
        
        # Clone (in demo, we'll skip to save time)
        print(f"\n📥 Cloning would happen here...")
        print(f"   Clone URL: {repo['clone_url']}")
        
        # What security scanning would find
        print(f"\n🔒 Security scanning would check for:")
        print(f"   - Hardcoded secrets")
        print(f"   - Suspicious code patterns (eval, exec, etc.)")
        print(f"   - Potentially dangerous imports")
        
        # What parsing would extract
        print(f"\n📊 Code parsing would extract:")
        print(f"   - Trading strategy classes and functions")
        print(f"   - Technical indicators (SMA, EMA, RSI, etc.)")
        print(f"   - Risk management logic (stop loss, position sizing)")
        
        print(f"\n✅ Full analysis would save:")
        print(f"   - JSON specification: artifacts/{repo['full_name'].replace('/', '_')}.json")
        print(f"   - Markdown docs: artifacts/{repo['full_name'].replace('/', '_')}.md")
        print(f"   - Updated index: artifacts/index.json")
    else:
        print("No repositories found. Try adjusting search terms or check your GitHub token.")
    
    print("\n💡 To run a full analysis, use: moltbot-scout discover")


if __name__ == '__main__':
    main()
