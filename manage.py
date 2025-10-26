#!/usr/bin/env python3
"""Django-style management commands for FastAPI"""
import click
import uvicorn
from alembic import command
from alembic.config import Config
import sys
import os

# Добавить app в path
sys.path.insert(0, os.path.dirname(__file__))


@click.group()
def cli():
    """Medical Information System CLI"""
    pass


@cli.command()
@click.option('--host', default='0.0.0.0', help='Host to bind')
@click.option('--port', default=8000, help='Port to bind')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
def runserver(host, port, reload):
    """Запустить сервер разработки"""
    click.echo(f"🚀 Starting server on {host}:{port}")
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload
    )


@cli.command()
@click.option('--message', '-m', default='auto migration', help='Migration message')
def makemigrations(message):
    """Создать новую миграцию"""
    click.echo("📝 Creating migration...")
    alembic_cfg = Config("alembic.ini")
    try:
        command.revision(alembic_cfg, autogenerate=True, message=message)
        click.echo(f"✅ Migration '{message}' created")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def migrate():
    """Применить миграции"""
    click.echo("🔄 Applying migrations...")
    alembic_cfg = Config("alembic.ini")
    try:
        command.upgrade(alembic_cfg, "head")
        click.echo("✅ Migrations applied successfully")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--steps', '-n', default=1, help='Number of migrations to rollback')
def rollback(steps):
    """Откатить миграции"""
    click.echo(f"⏪ Rolling back {steps} migration(s)...")
    alembic_cfg = Config("alembic.ini")
    try:
        command.downgrade(alembic_cfg, f"-{steps}")
        click.echo(f"✅ Rolled back {steps} migration(s)")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def shell():
    """Запустить интерактивную оболочку"""
    import code
    from app.db.session import SessionLocal
    
    db = SessionLocal()
    
    banner = """
🐍 Medical System Shell
Available objects:
  - db: Database session
"""
    
    code.interact(banner=banner, local={'db': db})


@cli.command()
def createsuperuser():
    """Создать суперпользователя"""
    from app.db.session import SessionLocal
    from app.core.security import get_password_hash
    
    click.echo("👤 Create Superuser")
    
    username = click.prompt("Username")
    email = click.prompt("Email")
    full_name = click.prompt("Full name")
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    
    db = SessionLocal()
    
    try:
        # TODO: Раскомментируй когда создашь модель User
        # from app.modules.auth.models import User
        
        # if db.query(User).filter(User.username == username).first():
        #     click.echo(f"❌ User '{username}' already exists", err=True)
        #     sys.exit(1)
        
        # user = User(
        #     username=username,
        #     email=email,
        #     full_name=full_name,
        #     hashed_password=get_password_hash(password),
        #     role="admin"
        # )
        
        # db.add(user)
        # db.commit()
        
        click.echo(f"⚠️  User model not created yet. Implement auth module first.")
        click.echo(f"Username: {username}, Email: {email}")
    
    except Exception as e:
        db.rollback()
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)
    finally:
        db.close()


@cli.command()
def test():
    """Запустить тесты"""
    import pytest
    
    click.echo("🧪 Running tests...")
    exit_code = pytest.main(["-v", "--cov=app", "tests/"])
    sys.exit(exit_code)


@cli.command()
def initdb():
    """Инициализировать базу данных"""
    click.echo("🗄️  Initializing database...")
    
    from app.db.session import engine
    from app.db.base import Base
    
    try:
        Base.metadata.create_all(bind=engine)
        click.echo("✅ Database initialized successfully")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()
