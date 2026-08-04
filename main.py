#!/usr/bin/env python3
"""Entry point for Contest Agent

Usage:
    python main.py --mode cli start      # Start agent via CLI
    python main.py --mode web            # Start web dashboard
    python main.py --mode cli status     # Check status
    python main.py --mode cli run        # Manual run
"""
import sys
import argparse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

def main():
    parser = argparse.ArgumentParser(
        description="🎯 Weekly Coding Contest Agent",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --mode cli start          # Start scheduler in CLI mode
  %(prog)s --mode web --port 8080    # Start web dashboard on port 8080
  %(prog)s --mode cli run            # Trigger manual run
  %(prog)s --mode cli status         # Show agent status
        """
    )
    parser.add_argument(
        "--mode", 
        choices=["cli", "web"], 
        default="cli",
        help="Run mode: cli (command line) or web (dashboard)"
    )
    parser.add_argument(
        "--host", 
        default="0.0.0.0", 
        help="Web dashboard host (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=5000, 
        help="Web dashboard port (default: 5000)"
    )

    args, unknown = parser.parse_known_args()

    if args.mode == "web":
        from web.dashboard import run_dashboard
        print("""
╔══════════════════════════════════════════╗
║     🎯 Weekly Contest Agent Dashboard    ║
╠══════════════════════════════════════════╣
║  Open your browser at:                   ║
║  http://localhost:{:<4}                    ║
╚══════════════════════════════════════════╝
        """.format(args.port))
        run_dashboard(host=args.host, port=args.port)
    else:
        # Pass remaining args to CLI
        from cli import cli
        sys.argv = [sys.argv[0]] + unknown
        cli()

if __name__ == "__main__":
    main()
