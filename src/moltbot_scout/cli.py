"""Command-line interface for moltbot-repo-scout."""
import click
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from moltbot_scout.config import Config
from moltbot_scout.discovery import RepoDiscovery
from moltbot_scout.scoring import RepoScorer
from moltbot_scout.cloner import SafeCloner
from moltbot_scout.security import SecurityScanner
from moltbot_scout.parser import StrategyParser
from moltbot_scout.normalizer import SpecNormalizer
from moltbot_scout.indexer import ArtifactIndexer


@click.group()
@click.version_option(version='0.1.0')
def main():
    """Moltbot Repository Scout - GitHub repository discovery and analysis tool."""
    pass


@main.command()
@click.option('--config', '-c', type=click.Path(), help='Path to config file')
@click.option('--token', '-t', help='GitHub API token')
@click.option('--query', '-q', multiple=True, help='Search query (can be specified multiple times)')
@click.option('--max-results', '-m', type=int, default=5, help='Maximum results per query')
@click.option('--min-score', '-s', type=float, default=0.3, help='Minimum trustworthiness score')
@click.option('--cleanup/--no-cleanup', default=True, help='Clean up cloned repos after analysis')
def discover(config, token, query, max_results, min_score, cleanup):
    """Discover and analyze GitHub repositories."""
    click.echo("🔍 Starting repository discovery...\n")
    
    # Load configuration
    cfg = Config(config) if config else Config()
    
    # Override with CLI options
    if token:
        cfg.set('github.token', token)
    
    if query:
        cfg.set('github.search_queries', list(query))
    
    if max_results:
        cfg.set('github.max_results_per_query', max_results)
    
    if min_score:
        cfg.set('scoring.min_score', min_score)
    
    # Initialize components
    discovery = RepoDiscovery(
        github_token=cfg.get('github.token'),
        max_results_per_query=cfg.get('github.max_results_per_query')
    )
    scorer = RepoScorer(weights=cfg.get('scoring.weights'))
    cloner = SafeCloner(
        clone_dir=cfg.get('cloner.clone_dir'),
        max_depth=cfg.get('cloner.max_depth'),
        timeout=cfg.get('cloner.timeout')
    )
    scanner = SecurityScanner(
        secret_patterns=cfg.get('security.secret_patterns'),
        suspicious_patterns=cfg.get('security.suspicious_patterns')
    )
    parser = StrategyParser(max_file_size=cfg.get('parser.max_file_size'))
    normalizer = SpecNormalizer()
    indexer = ArtifactIndexer(
        artifacts_dir=cfg.get('output.artifacts_dir'),
        index_file=cfg.get('output.index_file')
    )
    
    # Discover repositories
    click.echo("Searching for repositories...")
    repos = discovery.discover(cfg.get('github.search_queries'))
    click.echo(f"Found {len(repos)} repositories\n")
    
    analyzed_count = 0
    
    for repo in repos:
        click.echo(f"📦 Analyzing: {repo['full_name']}")
        
        # Score repository
        score_info = scorer.score_repository(repo)
        click.echo(f"   Trust Score: {score_info['overall_score']} ({score_info['trustworthiness']})")
        
        # Check minimum score
        if score_info['overall_score'] < cfg.get('scoring.min_score'):
            click.echo(f"   ⚠️  Score below minimum threshold, skipping\n")
            continue
        
        # Clone repository
        click.echo(f"   Cloning repository...")
        clone_result = cloner.clone_repository(repo['clone_url'], repo['full_name'])
        
        if not clone_result['success']:
            click.echo(f"   ❌ Clone failed: {clone_result['message']}\n")
            continue
        
        repo_path = clone_result['path']
        
        # Security scan
        click.echo(f"   Running security scan...")
        security_info = scanner.scan_repository(repo_path)
        click.echo(f"   Security: {security_info['total_issues']} issues found")
        
        # Parse code
        click.echo(f"   Parsing code...")
        parsed_info = parser.parse_repository(repo_path)
        click.echo(f"   Found: {len(parsed_info['strategies'])} strategies, "
                  f"{len(parsed_info['indicators'])} indicators")
        
        # Normalize and save
        spec = normalizer.normalize(repo, score_info, security_info, parsed_info)
        
        # Save artifacts
        safe_name = repo['full_name'].replace('/', '_')
        spec_path = os.path.join(cfg.get('output.artifacts_dir'), f"{safe_name}.json")
        doc_path = os.path.join(cfg.get('output.artifacts_dir'), f"{safe_name}.md")
        
        normalizer.save_spec(spec, spec_path)
        normalizer.save_markdown_doc(spec, doc_path)
        
        # Add to index
        indexer.add_repository(repo['full_name'], spec, spec_path, doc_path)
        
        click.echo(f"   ✅ Analysis complete\n")
        analyzed_count += 1
        
        # Cleanup
        if cleanup:
            cloner.cleanup_repository(repo['full_name'])
    
    # Generate index report
    report_path = os.path.join(cfg.get('output.artifacts_dir'), 'INDEX.md')
    with open(report_path, 'w') as f:
        f.write(indexer.generate_index_report())
    
    click.echo(f"\n✨ Discovery complete!")
    click.echo(f"Analyzed {analyzed_count} repositories")
    click.echo(f"Results saved to: {cfg.get('output.artifacts_dir')}")
    click.echo(f"Index: {cfg.get('output.index_file')}")


@main.command()
@click.option('--config', '-c', type=click.Path(), help='Path to save config file')
def init_config(config):
    """Initialize a configuration file."""
    cfg = Config()
    
    if not config:
        config = 'config.yaml'
    
    cfg.save(config)
    click.echo(f"✅ Configuration file created: {config}")


@main.command()
@click.option('--artifacts-dir', '-a', type=click.Path(), default='artifacts',
              help='Artifacts directory')
def stats(artifacts_dir):
    """Show statistics from indexed repositories."""
    index_file = os.path.join(artifacts_dir, 'index.json')
    
    if not os.path.exists(index_file):
        click.echo(f"❌ Index file not found: {index_file}")
        return
    
    indexer = ArtifactIndexer(artifacts_dir=artifacts_dir, index_file=index_file)
    stats = indexer.get_stats()
    
    click.echo("\n📊 Repository Statistics\n")
    click.echo(f"Total Repositories: {stats['total_repositories']}")
    click.echo(f"Total Strategies: {stats['total_strategies']}")
    click.echo(f"Total Indicators: {stats['total_indicators']}")
    click.echo(f"Total Security Issues: {stats['total_security_issues']}")


@main.command()
@click.option('--artifacts-dir', '-a', type=click.Path(), default='artifacts',
              help='Artifacts directory')
@click.option('--min-score', '-s', type=float, help='Minimum trustworthiness score')
@click.option('--max-issues', '-i', type=int, help='Maximum security issues')
def list_repos(artifacts_dir, min_score, max_issues):
    """List indexed repositories with optional filtering."""
    index_file = os.path.join(artifacts_dir, 'index.json')
    
    if not os.path.exists(index_file):
        click.echo(f"❌ Index file not found: {index_file}")
        return
    
    indexer = ArtifactIndexer(artifacts_dir=artifacts_dir, index_file=index_file)
    repos = indexer.get_repositories(min_score=min_score, max_security_issues=max_issues)
    
    click.echo(f"\n📚 Found {len(repos)} repositories\n")
    
    for repo in sorted(repos, key=lambda x: x['trustworthiness_score'], reverse=True):
        click.echo(f"• {repo['name']}")
        click.echo(f"  Score: {repo['trustworthiness_score']} ({repo['trustworthiness_level']})")
        click.echo(f"  Security: {repo['security_issues']} issues")
        click.echo(f"  Strategies: {repo['strategies_count']}, Indicators: {repo['indicators_count']}")
        click.echo(f"  Spec: {repo['spec_path']}\n")


if __name__ == '__main__':
    main()
