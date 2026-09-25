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

    s = agent.status()
    click.echo("✅ Agent started! Press Ctrl+C to stop.")
    click.echo(f"📡 Channel: {s['channel'].upper()} -> {s['target']}")
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

@cli.command(name="test-notify")
def test_notify():
    """Send a test notification to verify Telegram / SMS setup"""
    click.echo("🔔 Sending test notification...")
    test_msg = (
        "🎯 <b>Contest Agent Notification Test</b>\n\n"
        "If you are seeing this, your notification channel is working perfectly! 🚀"
    )
    success = agent.notifier.send(test_msg)
    if success:
        click.echo("✅ Notification sent successfully!")
    else:
        click.echo("❌ Failed to send notification. Please check your credentials.")

@cli.command()
def status():
    """Show current agent status"""
    s = agent.status()
    click.echo("\n" + "=" * 40)
    click.echo("🎯 CONTEST AGENT STATUS")
    click.echo("=" * 40)
    click.echo(f"Status:      {'🟢 RUNNING' if s['running'] else '🔴 STOPPED'}")
    click.echo(f"Channel:     {s['channel'].upper()}")
    click.echo(f"Target:      {s['target']}")
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
