#!/usr/bin/env python3
"""
Example usage of the integrated evaluation pipeline

This script demonstrates how to use the pipeline programmatically
for custom analysis and visualization.
"""

import sys
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.integrated_evaluation import EvaluationPipeline, SimulationConfig
import matplotlib.pyplot as plt
import seaborn as sns


def example_1_basic_usage():
    """Example 1: Basic usage with default configuration"""
    print("=" * 80)
    print("Example 1: Basic Usage")
    print("=" * 80)
    
    # Create pipeline with default config
    pipeline = EvaluationPipeline()
    
    # Load existing results (from runs/example/)
    pipeline.config['output_base_dir'] = 'runs/example'
    pipeline.load_results()
    
    # Analyze
    df_summary = pipeline.analyze_results()
    print("\nResults Summary:")
    print(df_summary.to_string())
    
    # Generate figures
    pipeline.generate_figures(df_summary)
    print("\nFigures saved to:", pipeline.config['figures']['output_dir'])


def example_2_custom_config():
    """Example 2: Using custom configuration"""
    print("\n" + "=" * 80)
    print("Example 2: Custom Configuration")
    print("=" * 80)
    
    # Load from YAML config
    config_file = PROJECT_ROOT / 'configs' / 'evaluation_example.yaml'
    
    if config_file.exists():
        pipeline = EvaluationPipeline(config_file=str(config_file))
        print(f"\nLoaded configuration from {config_file}")
        print(f"Number of simulations configured: {len(pipeline.config['simulations'])}")
        
        # Show simulation names
        print("\nSimulations:")
        for sim in pipeline.config['simulations']:
            print(f"  - {sim['name']} ({sim['policy']})")
    else:
        print(f"Config file not found: {config_file}")


def example_3_custom_analysis():
    """Example 3: Custom analysis and visualization"""
    print("\n" + "=" * 80)
    print("Example 3: Custom Analysis")
    print("=" * 80)
    
    # Create pipeline and load results
    pipeline = EvaluationPipeline()
    pipeline.config['output_base_dir'] = 'runs/example'
    pipeline.load_results()
    
    # Custom metric extraction
    print("\nCustom Metric Analysis:")
    for name, data in pipeline.results.items():
        metrics = data['metrics']
        print(f"\n{name}:")
        print(f"  Hit Rate: {metrics['hit_rate_hz']:.2f} Hz")
        print(f"  Service Time Saved: {metrics['service_time_saved_ratio']:.2%}")
        print(f"  Wasted Ratio: {metrics['wasted_ratio']:.2%}")
    
    # Custom visualization - Scatter plot
    if len(pipeline.results) >= 2:
        fig, ax = plt.subplots(figsize=(10, 6))
        
        for name, data in pipeline.results.items():
            metrics = data['metrics']
            ax.scatter(
                metrics['hit_rate_hz'],
                metrics['service_time_saved_ratio'],
                s=200,
                alpha=0.6,
                label=name
            )
        
        ax.set_xlabel('Hit Rate (Hz)')
        ax.set_ylabel('Service Time Saved Ratio')
        ax.set_title('Hit Rate vs Service Time Saved')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Save custom figure
        output_dir = PROJECT_ROOT / 'figures' / 'custom'
        output_dir.mkdir(parents=True, exist_ok=True)
        fig.savefig(output_dir / 'hit_vs_st_scatter.png', dpi=300, bbox_inches='tight')
        print(f"\nCustom figure saved to: {output_dir / 'hit_vs_st_scatter.png'}")
        plt.close(fig)


def example_4_progress_analysis():
    """Example 4: Time-series progress analysis"""
    print("\n" + "=" * 80)
    print("Example 4: Progress Analysis")
    print("=" * 80)
    
    # Create pipeline and load results
    pipeline = EvaluationPipeline()
    pipeline.config['output_base_dir'] = 'runs/example'
    pipeline.load_results()
    
    # Analyze progress over time
    print("\nProgress Data Summary:")
    for name, data in pipeline.results.items():
        progress = data['progress']
        if not progress.empty and 'Util' in progress.columns:
            print(f"\n{name}:")
            print(f"  Data points: {len(progress)}")
            print(f"  Mean utilization: {progress['Util'].mean():.2%}")
            print(f"  Max utilization: {progress['Util'].max():.2%}")
            print(f"  Min utilization: {progress['Util'].min():.2%}")


def example_5_parameter_comparison():
    """Example 5: Compare different parameter settings"""
    print("\n" + "=" * 80)
    print("Example 5: Parameter Comparison")
    print("=" * 80)
    
    # This example shows how to compare different parameter settings
    # for the same policy (e.g., different alpha values for EDE)
    
    # Define configurations to compare
    configs_to_compare = {
        'EDE (α=0.3)': {'alpha_tti': 0.3, 'protected_cap': 0.3},
        'EDE (α=0.5)': {'alpha_tti': 0.5, 'protected_cap': 0.3},
        'EDE (α=0.7)': {'alpha_tti': 0.7, 'protected_cap': 0.3},
    }
    
    print("\nParameter sweep configuration:")
    print("Policy: EDE")
    print("Varying: alpha_tti")
    print("Fixed: protected_cap = 0.3")
    print("\nConfigurations:")
    for name, params in configs_to_compare.items():
        print(f"  {name}: {params}")
    
    print("\nTo run this sweep:")
    print("1. Create a YAML config with these simulations")
    print("2. Run: python scripts/integrated_evaluation.py --run-simulations --config <config.yaml>")


def example_6_generate_report():
    """Example 6: Generate custom report"""
    print("\n" + "=" * 80)
    print("Example 6: Generate Custom Report")
    print("=" * 80)
    
    # Create pipeline and load results
    pipeline = EvaluationPipeline()
    pipeline.config['output_base_dir'] = 'runs/example'
    pipeline.load_results()
    
    # Analyze
    df_summary = pipeline.analyze_results()
    
    # Generate standard report
    report_path = PROJECT_ROOT / 'figures' / 'custom' / 'custom_report.md'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    pipeline.generate_report(df_summary, output_path=str(report_path))
    print(f"\nReport generated: {report_path}")
    
    # Create custom report section
    with open(report_path, 'a') as f:
        f.write("\n## Custom Analysis\n\n")
        f.write("This section contains additional custom analysis.\n\n")
        
        # Add custom metrics
        f.write("### Efficiency Metrics\n\n")
        f.write("| Policy | Wasted Ratio | Evictions |\n")
        f.write("|--------|--------------|------------|\n")
        
        for name, data in pipeline.results.items():
            metrics = data['metrics']
            f.write(f"| {name} | {metrics['wasted_ratio']:.2%} | {metrics['evictions']:,} |\n")
        
        f.write("\n")
    
    print(f"Custom section added to report")


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "Integrated Evaluation Examples" + " " * 28 + "║")
    print("╚" + "═" * 78 + "╝")
    
    # Run examples
    example_1_basic_usage()
    example_2_custom_config()
    example_3_custom_analysis()
    example_4_progress_analysis()
    example_5_parameter_comparison()
    example_6_generate_report()
    
    print("\n" + "=" * 80)
    print("All examples completed!")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Review generated figures in figures/custom/")
    print("2. Check custom report at figures/custom/custom_report.md")
    print("3. Try creating your own YAML configuration")
    print("4. Run simulations with: ./scripts/run_evaluation.sh --run-simulations")
    print()


if __name__ == '__main__':
    main()
