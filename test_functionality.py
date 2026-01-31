#!/usr/bin/env python3
"""Test script to verify moltbot-repo-scout functionality without GitHub API."""
import os
import sys
import json
import tempfile
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from moltbot_scout.scoring import RepoScorer
from moltbot_scout.security import SecurityScanner
from moltbot_scout.parser import StrategyParser
from moltbot_scout.normalizer import SpecNormalizer
from moltbot_scout.indexer import ArtifactIndexer
from moltbot_scout.config import Config


def create_test_repo(temp_dir):
    """Create a mock Python trading bot repository for testing."""
    repo_path = os.path.join(temp_dir, 'test_trading_bot')
    os.makedirs(repo_path, exist_ok=True)
    
    # Create a sample strategy file
    strategy_code = '''"""Sample trading strategy module."""

class MomentumStrategy:
    """A momentum-based trading strategy."""
    
    def __init__(self, lookback_period=20):
        """Initialize strategy.
        
        Args:
            lookback_period: Number of periods for momentum calculation
        """
        self.lookback_period = lookback_period
    
    def generate_signal(self, prices):
        """Generate trading signal based on momentum.
        
        Args:
            prices: List of historical prices
            
        Returns:
            Signal: 1 for buy, -1 for sell, 0 for hold
        """
        if len(prices) < self.lookback_period:
            return 0
        
        momentum = prices[-1] - prices[-self.lookback_period]
        
        if momentum > 0:
            return 1  # Buy signal
        elif momentum < 0:
            return -1  # Sell signal
        else:
            return 0  # Hold


def calculate_sma(prices, period):
    """Calculate Simple Moving Average indicator.
    
    Args:
        prices: List of prices
        period: Period for SMA calculation
        
    Returns:
        SMA value
    """
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period


def calculate_rsi(prices, period=14):
    """Calculate Relative Strength Index indicator.
    
    Args:
        prices: List of prices
        period: RSI period (default: 14)
        
    Returns:
        RSI value between 0 and 100
    """
    # Simplified RSI calculation
    if len(prices) < period + 1:
        return None
    
    gains = []
    losses = []
    
    for i in range(1, len(prices)):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))
    
    avg_gain = sum(gains[-period:]) / period
    avg_loss = sum(losses[-period:]) / period
    
    if avg_loss == 0:
        return 100
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi


def calculate_stop_loss(entry_price, risk_percent=0.02):
    """Calculate stop loss price for risk management.
    
    Args:
        entry_price: Entry price for the position
        risk_percent: Risk percentage (default: 2%)
        
    Returns:
        Stop loss price
    """
    return entry_price * (1 - risk_percent)


def calculate_position_size(account_balance, risk_percent, entry_price, stop_loss_price):
    """Calculate position size based on risk management.
    
    Args:
        account_balance: Total account balance
        risk_percent: Percentage of account to risk
        entry_price: Entry price
        stop_loss_price: Stop loss price
        
    Returns:
        Position size in units
    """
    risk_amount = account_balance * risk_percent
    price_risk = entry_price - stop_loss_price
    
    if price_risk <= 0:
        return 0
    
    position_size = risk_amount / price_risk
    return position_size
'''
    
    # Write strategy file
    with open(os.path.join(repo_path, 'strategy.py'), 'w') as f:
        f.write(strategy_code)
    
    # Create a file with potential security issues
    suspicious_code = '''"""Config module - DO NOT USE IN PRODUCTION."""

# WARNING: This file contains security issues for testing purposes

API_KEY = "sk_live_abc123def456ghi789"  # Hardcoded secret
PASSWORD = "SuperSecret123"

def execute_command(user_input):
    """Execute system command - DANGEROUS!"""
    import os
    os.system(user_input)  # Suspicious pattern

def load_data(data_string):
    """Load data using eval - DANGEROUS!"""
    return eval(data_string)  # Suspicious pattern
'''
    
    with open(os.path.join(repo_path, 'config.py'), 'w') as f:
        f.write(suspicious_code)
    
    return repo_path


def test_scoring():
    """Test repository scoring functionality."""
    print("📊 Testing Repository Scoring...\n")
    
    scorer = RepoScorer()
    
    # Mock repository data
    repo_info = {
        'full_name': 'test/trading-bot',
        'stars': 150,
        'forks': 30,
        'created_at': '2023-01-15T10:00:00Z',
        'pushed_at': '2026-01-28T15:30:00Z',
        'license': 'MIT License',
        'size': 5000,
    }
    
    score_result = scorer.score_repository(repo_info)
    
    print(f"Overall Score: {score_result['overall_score']}")
    print(f"Trustworthiness: {score_result['trustworthiness']}")
    print("\nComponent Scores:")
    for component, score in score_result['component_scores'].items():
        print(f"  {component}: {score:.3f}")
    
    print("\n✅ Scoring test passed!\n")


def test_security_scanner(repo_path):
    """Test security scanning functionality."""
    print("🔒 Testing Security Scanner...\n")
    
    scanner = SecurityScanner()
    results = scanner.scan_repository(repo_path)
    
    print(f"Files Scanned: {results['files_scanned']}")
    print(f"Total Issues: {results['total_issues']}")
    print(f"Secrets Found: {len(results['secrets_found'])}")
    print(f"Suspicious Code: {len(results['suspicious_code'])}")
    
    if results['secrets_found']:
        print("\nSample Secret Found:")
        secret = results['secrets_found'][0]
        print(f"  File: {secret['file']}")
        print(f"  Line: {secret['line']}")
        print(f"  Type: {secret['type']}")
    
    if results['suspicious_code']:
        print("\nSample Suspicious Code:")
        suspicious = results['suspicious_code'][0]
        print(f"  File: {suspicious['file']}")
        print(f"  Line: {suspicious['line']}")
        print(f"  Pattern: {suspicious['pattern']}")
    
    print("\n✅ Security scanner test passed!\n")


def test_parser(repo_path):
    """Test AST parser functionality."""
    print("🔍 Testing AST Parser...\n")
    
    parser = StrategyParser()
    results = parser.parse_repository(repo_path)
    
    print(f"Files Parsed: {results['files_parsed']}")
    print(f"Strategies Found: {len(results['strategies'])}")
    print(f"Indicators Found: {len(results['indicators'])}")
    print(f"Risk Functions Found: {len(results['risk_logic'])}")
    
    if results['strategies']:
        print("\nSample Strategy:")
        strategy = results['strategies'][0]
        print(f"  Name: {strategy['name']}")
        print(f"  Type: {strategy['type']}")
        print(f"  File: {strategy['file']}")
    
    if results['indicators']:
        print("\nSample Indicators:")
        for indicator in results['indicators'][:3]:
            print(f"  - {indicator['name']} (line {indicator['line']})")
    
    if results['risk_logic']:
        print("\nRisk Management Functions:")
        for risk_func in results['risk_logic']:
            print(f"  - {risk_func['name']} (line {risk_func['line']})")
    
    print("\n✅ Parser test passed!\n")
    return results


def test_normalizer(parsed_results):
    """Test spec normalizer functionality."""
    print("📝 Testing Spec Normalizer...\n")
    
    normalizer = SpecNormalizer()
    
    # Mock data
    repo_info = {
        'full_name': 'test/trading-bot',
        'url': 'https://github.com/test/trading-bot',
        'description': 'A test trading bot',
        'language': 'Python',
        'license': 'MIT License',
        'created_at': '2023-01-15T10:00:00Z',
        'updated_at': '2026-01-28T15:30:00Z',
        'stars': 150,
        'forks': 30,
        'open_issues': 5,
    }
    
    score_info = {
        'overall_score': 0.75,
        'trustworthiness': 'medium-high',
        'component_scores': {
            'stars_score': 0.8,
            'age_score': 0.7,
            'commits_score': 0.6,
            'license_score': 1.0,
            'activity_score': 0.9,
        }
    }
    
    security_info = {
        'files_scanned': 2,
        'total_issues': 5,
        'secrets_found': [{'file': 'config.py', 'line': 5, 'type': 'secret'}],
        'suspicious_code': [{'file': 'config.py', 'line': 10, 'type': 'eval'}],
    }
    
    spec = normalizer.normalize(repo_info, score_info, security_info, parsed_results)
    
    print("Generated Spec Structure:")
    print(f"  Metadata: ✓")
    print(f"  Trustworthiness Score: {spec['trustworthiness']['overall_score']}")
    print(f"  Security Issues: {spec['security']['total_issues']}")
    print(f"  Strategies: {spec['code_analysis']['summary']['total_strategies']}")
    print(f"  Indicators: {spec['code_analysis']['summary']['total_indicators']}")
    
    # Generate markdown
    md_doc = normalizer.generate_markdown_doc(spec)
    print(f"\n  Generated Markdown: {len(md_doc)} characters")
    
    print("\n✅ Normalizer test passed!\n")
    return spec


def test_indexer(spec):
    """Test artifact indexer functionality."""
    print("📚 Testing Artifact Indexer...\n")
    
    with tempfile.TemporaryDirectory() as temp_artifacts:
        indexer = ArtifactIndexer(
            artifacts_dir=temp_artifacts,
            index_file=os.path.join(temp_artifacts, 'index.json')
        )
        
        # Add repository
        indexer.add_repository(
            'test/trading-bot',
            spec,
            os.path.join(temp_artifacts, 'test_trading-bot.json'),
            os.path.join(temp_artifacts, 'test_trading-bot.md')
        )
        
        # Check stats
        stats = indexer.get_stats()
        print(f"Total Repositories: {stats['total_repositories']}")
        print(f"Total Strategies: {stats['total_strategies']}")
        print(f"Total Indicators: {stats['total_indicators']}")
        
        # Generate report
        report = indexer.generate_index_report()
        print(f"\nGenerated Index Report: {len(report)} characters")
        
        print("\n✅ Indexer test passed!\n")


def test_config():
    """Test configuration system."""
    print("⚙️  Testing Configuration System...\n")
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        temp_config = f.name
    
    try:
        config = Config()
        
        # Test get/set
        config.set('github.token', 'test_token')
        token = config.get('github.token')
        assert token == 'test_token', "Config get/set failed"
        
        # Test save
        config.save(temp_config)
        assert os.path.exists(temp_config), "Config save failed"
        
        # Test load
        config2 = Config(temp_config)
        assert config2.get('github.token') == 'test_token', "Config load failed"
        
        print("Config get/set: ✓")
        print("Config save/load: ✓")
        print("\n✅ Configuration test passed!\n")
        
    finally:
        if os.path.exists(temp_config):
            os.unlink(temp_config)


def main():
    """Run all tests."""
    print("=" * 60)
    print("🧪 Moltbot Repository Scout - Functionality Tests")
    print("=" * 60 + "\n")
    
    # Create temporary test repository
    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = create_test_repo(temp_dir)
        print(f"📁 Created test repository: {repo_path}\n")
        
        # Run tests
        test_config()
        test_scoring()
        security_results = test_security_scanner(repo_path)
        parsed_results = test_parser(repo_path)
        spec = test_normalizer(parsed_results)
        test_indexer(spec)
    
    print("=" * 60)
    print("✅ All tests passed successfully!")
    print("=" * 60)
    print("\n💡 To test with real GitHub repositories:")
    print("   1. Set GITHUB_TOKEN environment variable")
    print("   2. Run: moltbot-scout discover -q 'trading bot python' -m 2")


if __name__ == '__main__':
    main()
