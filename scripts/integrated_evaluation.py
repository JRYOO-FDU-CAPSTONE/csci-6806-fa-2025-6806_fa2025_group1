#!/usr/bin/env python3
"""
Integrated Evaluation Pipeline for BCacheSim

This script integrates:
1. Simulation execution (running BCacheSim with different configurations)
2. Result collection and parsing
3. Data analysis and metrics extraction
4. Figure generation and visualization

Usage:
    python scripts/integrated_evaluation.py --run-simulations --analyze --generate-figures
    python scripts/integrated_evaluation.py --analyze-only  # Skip simulations
    python scripts/integrated_evaluation.py --config configs/evaluation.yaml
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time
from datetime import datetime
import logging

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import lzma

# Add BCacheSim to path
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
sys.path.insert(0, str(PROJECT_ROOT / 'BCacheSim'))

from cachesim import simulate_ap

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimulationConfig:
    """Configuration for a single simulation run"""
    
    def __init__(self, name: str, policy: str, **kwargs):
        self.name = name
        self.policy = policy
        self.params = kwargs
        
    def to_cmd_args(self, trace_file: str, output_dir: str) -> List[str]:
        """Convert configuration to command-line arguments for simulate_ap.py"""
        args = [
            sys.executable,
            str(PROJECT_ROOT / 'BCacheSim' / 'cachesim' / 'simulate_ap.py'),
            '--trace', trace_file,
        ]
        
        # Eviction policy
        if self.policy in ['lru', 'fifo', 'lirs', 'dt-slru', 'ede', 'ttl']:
            args.extend(['--eviction-policy', self.policy])
        
        # Admission policy
        if 'admission_policy' in self.params:
            args.extend(['--ap', self.params['admission_policy']])
        
        # Cache size
        if 'cache_size_gb' in self.params:
            args.extend(['--cache-size-gb', str(self.params['cache_size_gb'])])
        
        # DT-SLRU specific
        if 'dt_per_byte_score' in self.params:
            args.extend(['--dt-per-byte-score', str(self.params['dt_per_byte_score'])])
        if 'protected_cap' in self.params:
            args.extend(['--protected-cap', str(self.params['protected_cap'])])
        
        # EDE specific
        if 'alpha_tti' in self.params:
            args.extend(['--alpha-tti', str(self.params['alpha_tti'])])
        
        # ML admission policy
        if 'ml_model' in self.params:
            args.extend(['--ml-model', self.params['ml_model']])
        if 'ap_threshold' in self.params:
            args.extend(['--ap-threshold', str(self.params['ap_threshold'])])
        
        # Prefetch settings
        if 'prefetch_when' in self.params:
            args.extend(['--prefetch-when', self.params['prefetch_when']])
        if 'prefetch_range' in self.params:
            args.extend(['--prefetch-range', self.params['prefetch_range']])
        
        # Output settings
        args.extend(['--output-dir', output_dir])
        
        return args


class ResultParser:
    """Parse and load simulation results"""
    
    @staticmethod
    def load_result_file(filepath: Path) -> Dict:
        """Load a result file (supports .txt, .txt.lzma, .json)"""
        if filepath.suffix == '.lzma':
            with lzma.open(filepath, 'rt') as f:
                content = f.read()
                return json.loads(content)
        elif filepath.suffix == '.json':
            with open(filepath, 'r') as f:
                return json.load(f)
        elif filepath.suffix == '.txt':
            with open(filepath, 'r') as f:
                return json.loads(f.read())
        else:
            raise ValueError(f"Unsupported file format: {filepath.suffix}")
    
    @staticmethod
    def extract_metrics(result_data: Dict) -> Dict:
        """Extract key metrics from result data"""
        metrics = {}
        
        # Core performance metrics
        metrics['write_rate_mbps'] = result_data.get('Write Rate (MB/s)', 0)
        metrics['iops_saved_ratio'] = result_data.get('IOPS Saved Ratio', 0)
        metrics['service_time_saved_ratio'] = result_data.get('Service Time Saved Ratio', 0)
        metrics['hit_rate_hz'] = result_data.get('Hit Rate (Hz)', 0)
        
        # Latency metrics
        metrics['peak_service_time'] = result_data.get('PeakServiceTimeUsed1', 0)
        metrics['p99_service_time'] = result_data.get('P99ServiceTimeUsed1', 0)
        metrics['p50_service_time'] = result_data.get('P50ServiceTimeUsed1', 0)
        
        # Cache efficiency
        metrics['wasted_ratio'] = result_data.get('Wasted', 0)
        metrics['evictions'] = result_data.get('Evictions', 0)
        
        # Configuration
        metrics['cache_size_gb'] = result_data.get('Cache Size (GB)', 0)
        metrics['ap_threshold'] = result_data.get('AP Threshold', 0)
        
        return metrics
    
    @staticmethod
    def load_progress_data(result_data: Dict, interval_seconds: int = 600) -> pd.DataFrame:
        """Extract time-series progress data"""
        if 'progress' not in result_data:
            return pd.DataFrame()
        
        progress = result_data['progress']
        if 'GET+PUT' not in progress or interval_seconds not in progress['GET+PUT']:
            return pd.DataFrame()
        
        df = pd.DataFrame(progress['GET+PUT'][interval_seconds])
        if 'Elapsed Trace Time' in df.columns:
            df['Days'] = df['Elapsed Trace Time'] / 3600 / 24
        
        return df


class EvaluationPipeline:
    """Main evaluation pipeline orchestrator"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config = self._load_config(config_file) if config_file else self._default_config()
        self.results = {}
        
    def _default_config(self) -> Dict:
        """Default evaluation configuration"""
        return {
            'trace_file': 'data/traces/full_0_0.1.trace',
            'output_base_dir': 'runs/evaluation',
            'cache_size_gb': 366.475,
            'simulations': [
                {
                    'name': 'Baseline',
                    'policy': 'lru',
                    'admission_policy': 'acceptall',
                },
                {
                    'name': 'DT-SLRU',
                    'policy': 'dt-slru',
                    'admission_policy': 'acceptall',
                    'dt_per_byte_score': 0.0051,
                    'protected_cap': 0.3,
                },
                {
                    'name': 'EDE',
                    'policy': 'ede',
                    'admission_policy': 'acceptall',
                    'alpha_tti': 0.5,
                    'protected_cap': 0.3,
                },
            ],
            'analysis': {
                'metrics': ['service_time_saved_ratio', 'hit_rate_hz', 'peak_service_time'],
                'generate_progress_plots': True,
                'generate_comparison_tables': True,
            },
            'figures': {
                'output_dir': 'figures/evaluation',
                'formats': ['png', 'pdf'],
                'dpi': 300,
            }
        }
    
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from YAML or JSON file"""
        config_path = Path(config_file)
        if config_path.suffix == '.yaml' or config_path.suffix == '.yml':
            import yaml
            with open(config_path) as f:
                return yaml.safe_load(f)
        elif config_path.suffix == '.json':
            with open(config_path) as f:
                return json.load(f)
        else:
            raise ValueError(f"Unsupported config format: {config_path.suffix}")
    
    def run_simulations(self, parallel: bool = False) -> Dict[str, Path]:
        """Run all configured simulations"""
        logger.info(f"Starting {len(self.config['simulations'])} simulations...")
        
        result_files = {}
        
        for sim_config_dict in self.config['simulations']:
            name = sim_config_dict['name']
            logger.info(f"Running simulation: {name}")
            
            # Create simulation config
            sim_config = SimulationConfig(
                name=name,
                policy=sim_config_dict['policy'],
                cache_size_gb=self.config.get('cache_size_gb', 366.475),
                **{k: v for k, v in sim_config_dict.items() if k not in ['name', 'policy']}
            )
            
            # Prepare output directory
            output_dir = Path(self.config['output_base_dir']) / name.lower().replace(' ', '_')
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Build command
            cmd = sim_config.to_cmd_args(
                trace_file=self.config['trace_file'],
                output_dir=str(output_dir)
            )
            
            logger.info(f"Command: {' '.join(cmd)}")
            
            # Run simulation
            start_time = time.time()
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=True
                )
                elapsed = time.time() - start_time
                logger.info(f"Simulation '{name}' completed in {elapsed:.2f}s")
                
                # Find result file
                result_file = self._find_result_file(output_dir)
                if result_file:
                    result_files[name] = result_file
                    logger.info(f"Result file: {result_file}")
                else:
                    logger.warning(f"No result file found for '{name}'")
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"Simulation '{name}' failed: {e}")
                logger.error(f"stdout: {e.stdout}")
                logger.error(f"stderr: {e.stderr}")
        
        return result_files
    
    def _find_result_file(self, output_dir: Path) -> Optional[Path]:
        """Find the result file in the output directory"""
        # Look for common result file patterns
        patterns = [
            '*_cache_perf.txt.lzma',
            '*_cache_perf.txt',
            'results.json',
        ]
        
        for pattern in patterns:
            files = list(output_dir.glob(f'**/{pattern}'))
            if files:
                return files[0]
        
        return None
    
    def load_results(self, result_files: Optional[Dict[str, Path]] = None) -> Dict[str, Dict]:
        """Load and parse all result files"""
        if result_files is None:
            # Auto-discover result files
            result_files = self._discover_result_files()
        
        logger.info(f"Loading {len(result_files)} result files...")
        
        for name, filepath in result_files.items():
            logger.info(f"Loading results for '{name}' from {filepath}")
            try:
                data = ResultParser.load_result_file(filepath)
                self.results[name] = {
                    'raw_data': data,
                    'metrics': ResultParser.extract_metrics(data),
                    'progress': ResultParser.load_progress_data(data),
                }
            except Exception as e:
                logger.error(f"Failed to load '{name}': {e}")
        
        return self.results
    
    def _discover_result_files(self) -> Dict[str, Path]:
        """Auto-discover result files in output directory"""
        result_files = {}
        output_base = Path(self.config['output_base_dir'])
        
        if not output_base.exists():
            logger.warning(f"Output directory does not exist: {output_base}")
            return result_files
        
        for sim_dir in output_base.iterdir():
            if sim_dir.is_dir():
                result_file = self._find_result_file(sim_dir)
                if result_file:
                    name = sim_dir.name.replace('_', ' ').title()
                    result_files[name] = result_file
        
        return result_files
    
    def analyze_results(self) -> pd.DataFrame:
        """Analyze loaded results and create summary dataframe"""
        logger.info("Analyzing results...")
        
        if not self.results:
            logger.error("No results loaded. Run load_results() first.")
            return pd.DataFrame()
        
        # Create summary dataframe
        rows = []
        for name, data in self.results.items():
            row = {'Policy': name}
            row.update(data['metrics'])
            rows.append(row)
        
        df_summary = pd.DataFrame(rows)
        
        # Calculate relative improvements (vs baseline if exists)
        if 'Baseline' in df_summary['Policy'].values:
            baseline_idx = df_summary[df_summary['Policy'] == 'Baseline'].index[0]
            baseline_st = df_summary.loc[baseline_idx, 'service_time_saved_ratio']
            baseline_hit = df_summary.loc[baseline_idx, 'hit_rate_hz']
            
            df_summary['st_improvement_vs_baseline'] = (
                (df_summary['service_time_saved_ratio'] - baseline_st) / baseline_st * 100
            )
            df_summary['hit_improvement_vs_baseline'] = (
                (df_summary['hit_rate_hz'] - baseline_hit) / baseline_hit * 100
            )
        
        logger.info("Analysis complete")
        return df_summary
    
    def generate_figures(self, df_summary: pd.DataFrame):
        """Generate all visualization figures"""
        logger.info("Generating figures...")
        
        figures_dir = Path(self.config['figures']['output_dir'])
        figures_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 6)
        
        # Figure 1: Performance Comparison Bar Chart
        self._generate_performance_comparison(df_summary, figures_dir)
        
        # Figure 2: Time Series (if progress data available)
        if self.config['analysis'].get('generate_progress_plots', True):
            self._generate_progress_plots(figures_dir)
        
        # Figure 3: Metrics Heatmap
        self._generate_metrics_heatmap(df_summary, figures_dir)
        
        logger.info(f"Figures saved to {figures_dir}")
    
    def _generate_performance_comparison(self, df_summary: pd.DataFrame, output_dir: Path):
        """Generate performance comparison bar chart"""
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        metrics = [
            ('service_time_saved_ratio', 'Service Time Saved Ratio', axes[0]),
            ('hit_rate_hz', 'Hit Rate (Hz)', axes[1]),
            ('peak_service_time', 'Peak Service Time (ms)', axes[2]),
        ]
        
        for metric, title, ax in metrics:
            df_summary.plot(
                x='Policy',
                y=metric,
                kind='bar',
                ax=ax,
                legend=False,
                color='steelblue'
            )
            ax.set_title(title)
            ax.set_xlabel('')
            ax.set_ylabel(title)
            ax.tick_params(axis='x', rotation=45)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self._save_figure(fig, output_dir / 'performance_comparison')
        plt.close(fig)
    
    def _generate_progress_plots(self, output_dir: Path):
        """Generate time-series progress plots"""
        fig, ax = plt.subplots(figsize=(12, 6))
        
        for name, data in self.results.items():
            if not data['progress'].empty and 'Days' in data['progress'].columns:
                df_progress = data['progress']
                if 'Util' in df_progress.columns:
                    ax.plot(
                        df_progress['Days'],
                        df_progress['Util'],
                        label=name,
                        linewidth=2
                    )
        
        ax.set_xlabel('Days')
        ax.set_ylabel('Service Time Utilization')
        ax.set_title('Service Time Utilization Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        self._save_figure(fig, output_dir / 'progress_utilization')
        plt.close(fig)
    
    def _generate_metrics_heatmap(self, df_summary: pd.DataFrame, output_dir: Path):
        """Generate heatmap of normalized metrics"""
        # Select numeric columns for heatmap
        numeric_cols = df_summary.select_dtypes(include=[np.number]).columns
        metrics_to_plot = [col for col in numeric_cols if not col.endswith('_vs_baseline')]
        
        if len(metrics_to_plot) < 2:
            logger.warning("Not enough metrics for heatmap")
            return
        
        # Normalize metrics to 0-1 range
        df_normalized = df_summary[['Policy'] + list(metrics_to_plot)].copy()
        for col in metrics_to_plot:
            min_val = df_normalized[col].min()
            max_val = df_normalized[col].max()
            if max_val > min_val:
                df_normalized[col] = (df_normalized[col] - min_val) / (max_val - min_val)
        
        df_normalized.set_index('Policy', inplace=True)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.heatmap(
            df_normalized.T,
            annot=True,
            fmt='.2f',
            cmap='YlGnBu',
            ax=ax,
            cbar_kws={'label': 'Normalized Score'}
        )
        ax.set_title('Normalized Performance Metrics Heatmap')
        
        plt.tight_layout()
        self._save_figure(fig, output_dir / 'metrics_heatmap')
        plt.close(fig)
    
    def _save_figure(self, fig, filepath: Path):
        """Save figure in configured formats"""
        formats = self.config['figures'].get('formats', ['png'])
        dpi = self.config['figures'].get('dpi', 300)
        
        for fmt in formats:
            output_path = filepath.with_suffix(f'.{fmt}')
            fig.savefig(output_path, dpi=dpi, bbox_inches='tight')
            logger.info(f"Saved figure: {output_path}")
    
    def generate_report(self, df_summary: pd.DataFrame, output_path: Optional[str] = None):
        """Generate markdown report"""
        if output_path is None:
            output_path = Path(self.config['figures']['output_dir']) / 'evaluation_report.md'
        
        output_path = Path(output_path)
        
        with open(output_path, 'w') as f:
            f.write("# BCacheSim Evaluation Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("## Configuration\n\n")
            f.write(f"- **Trace File:** {self.config['trace_file']}\n")
            f.write(f"- **Cache Size:** {self.config['cache_size_gb']} GB\n")
            f.write(f"- **Number of Simulations:** {len(self.config['simulations'])}\n\n")
            
            f.write("## Results Summary\n\n")
            f.write(df_summary.to_markdown(index=False))
            f.write("\n\n")
            
            f.write("## Key Findings\n\n")
            
            # Find best performing policy for each metric
            best_st = df_summary.loc[df_summary['service_time_saved_ratio'].idxmax(), 'Policy']
            best_hit = df_summary.loc[df_summary['hit_rate_hz'].idxmax(), 'Policy']
            best_peak = df_summary.loc[df_summary['peak_service_time'].idxmin(), 'Policy']
            
            f.write(f"- **Best Service Time Saved:** {best_st}\n")
            f.write(f"- **Best Hit Rate:** {best_hit}\n")
            f.write(f"- **Lowest Peak Service Time:** {best_peak}\n\n")
            
            f.write("## Figures\n\n")
            f.write("![Performance Comparison](performance_comparison.png)\n\n")
            f.write("![Progress Utilization](progress_utilization.png)\n\n")
            f.write("![Metrics Heatmap](metrics_heatmap.png)\n\n")
        
        logger.info(f"Report saved to {output_path}")
    
    def run_full_pipeline(self, skip_simulations: bool = False):
        """Run the complete evaluation pipeline"""
        logger.info("="*80)
        logger.info("Starting Integrated Evaluation Pipeline")
        logger.info("="*80)
        
        # Step 1: Run simulations (optional)
        result_files = None
        if not skip_simulations:
            result_files = self.run_simulations()
        
        # Step 2: Load results
        self.load_results(result_files)
        
        # Step 3: Analyze
        df_summary = self.analyze_results()
        
        # Step 4: Generate figures
        self.generate_figures(df_summary)
        
        # Step 5: Generate report
        self.generate_report(df_summary)
        
        logger.info("="*80)
        logger.info("Pipeline Complete!")
        logger.info("="*80)
        
        return df_summary


def main():
    parser = argparse.ArgumentParser(
        description="Integrated evaluation pipeline for BCacheSim"
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to configuration file (YAML or JSON)'
    )
    parser.add_argument(
        '--run-simulations',
        action='store_true',
        help='Run simulations (otherwise load existing results)'
    )
    parser.add_argument(
        '--analyze-only',
        action='store_true',
        help='Skip simulations and only analyze existing results'
    )
    parser.add_argument(
        '--generate-figures',
        action='store_true',
        help='Generate visualization figures'
    )
    parser.add_argument(
        '--output-dir',
        type=str,
        help='Override output directory'
    )
    
    args = parser.parse_args()
    
    # Create pipeline
    pipeline = EvaluationPipeline(config_file=args.config)
    
    # Override output dir if specified
    if args.output_dir:
        pipeline.config['output_base_dir'] = args.output_dir
    
    # Determine what to run
    if args.analyze_only:
        # Just analyze existing results
        pipeline.load_results()
        df_summary = pipeline.analyze_results()
        if args.generate_figures:
            pipeline.generate_figures(df_summary)
        pipeline.generate_report(df_summary)
    else:
        # Run full pipeline
        skip_sims = not args.run_simulations
        pipeline.run_full_pipeline(skip_simulations=skip_sims)


if __name__ == '__main__':
    main()
