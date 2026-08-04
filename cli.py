"""CLI Interface for Contest Agent"""
import sys
import io

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

import click
import time
from agent.scheduler import ContestAgent

agent = ContestAgent()

@click.group()
def cli():
    """🎯 Weekly Coding Contest Agent — CLI Control"""
    pass

@cli.command()
def start():
    """Start the agent scheduler (runs until Ctrl+C)"""
    click.echo("🚀 Starting Contest Agent...")
    success = agent.start()
    if not success:
        click.echo("❌ Agent is already running!")
        return

    click.echo("✅ Agent started! Press Ctrl+C to stop.")
    click.echo(f"📱 Notifications will be sent to: {agent.config['phone_number']}")
    click.echo("⏰ Scheduled: Sundays 10:00 AM | Wednesdays 6:00 AM | Daily 8:00 AM alert")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        click.echo("\n🛑 Interrupted. Stopping agent...")
        agent.stop()
        click.echo("👋 Agent stopped.")

@cli.command()
def stop():
    """Stop the agent scheduler"""
    success = agent.stop()
    if success:
        click.echo("🛑 Agent stopped.")
    else:
        click.echo("❌ Agent is not running.")

@cli.command()
def run():
    """Run a manual weekly digest immediately"""
    click.echo("🚀 Triggering manual weekly digest...")
    agent.run_now()

@cli.command(name="run-daily")
def run_daily():
    """Trigger today's daily contest alert immediately (for testing)"""
    click.echo("🌅 Triggering daily morning alert...")
    agent.send_daily_alert()

@cli.command()
def status():
    """Show current agent status"""
    s = agent.status()
    click.echo("\n" + "=" * 40)
    click.echo("🎯 CONTEST AGENT STATUS")
    click.echo("=" * 40)
    click.echo(f"Status:      {'🟢 RUNNING' if s['running'] else '🔴 STOPPED'}")
    click.echo(f"Phone:       {s['phone']}")
    click.echo(f"Platforms:   {', '.join(s['platforms_enabled'])}")
    click.echo(f"Last Run:    {s['last_run'] or 'Never'}")
    click.echo(f"Next Run:    {s['next_run'] or 'N/A'}")
    click.echo(f"Cached:      {s['total_contests_cached']} contests")
    click.echo("=" * 40)

@cli.command()
def test_fetch():
    """Test all fetchers (no SMS sent)"""
    click.echo("🔍 Testing all platform fetchers...\n")
    contests = agent.fetch_all_contests()
    click.echo(f"\n📊 Total contests found: {len(contests)}")
    for c in contests[:10]:
        click.echo(f"  • [{c['platform']}] {c['name']} — {c['start_time'].strftime('%Y-%m-%d %H:%M')}")

if __name__ == "__main__":
    cli()
