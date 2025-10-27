#!/usr/bin/env python3
"""Django-style management commands for FastAPI"""
import click
import uvicorn
from alembic import command
from alembic.config import Config
import sys
import os
import asyncio

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
    from app.db.session import AsyncSessionLocal
    
    click.echo("🐍 Medical System Async Shell")
    click.echo("Available objects:")
    click.echo("  - AsyncSessionLocal: Async session factory")
    click.echo("  - asyncio: Asyncio module")
    click.echo("\nExample usage:")
    click.echo("  async with AsyncSessionLocal() as db:")
    click.echo("      result = await db.execute(select(User))")
    click.echo("      users = result.scalars().all()")
    
    banner = """
🐍 Medical System Async Shell
Available objects:
  - AsyncSessionLocal: Async session factory
  - asyncio: For running async code
"""
    
    code.interact(banner=banner, local={'AsyncSessionLocal': AsyncSessionLocal, 'asyncio': asyncio})


@cli.command()
def createsuperuser():
    """Создать суперпользователя"""
    click.echo("👤 Create Superuser")
    
    username = click.prompt("Username")
    email = click.prompt("Email")
    full_name = click.prompt("Full name")
    password = click.prompt("Password", hide_input=True, confirmation_prompt=True)
    
    # Запускаем async функцию
    asyncio.run(_create_superuser_async(username, email, full_name, password))


async def _create_superuser_async(username: str, email: str, full_name: str, password: str):
    """Async функция для создания суперпользователя"""
    from app.db.session import AsyncSessionLocal
    from app.core.security import get_password_hash
    from app.modules.auth.models import User
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        try:
            # Проверяем, существует ли пользователь
            result = await db.execute(select(User).filter(User.username == username))
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                click.echo(f"❌ User '{username}' already exists", err=True)
                sys.exit(1)
            
            # Создаем пользователя
            user = User(
                username=username,
                email=email,
                full_name=full_name,
                hashed_password=get_password_hash(password),
                role="admin",
                is_active="Y"
            )
            
            db.add(user)
            await db.commit()
            await db.refresh(user)
            
            click.echo(f"✅ Superuser '{username}' created successfully!")
            click.echo(f"   ID: {user.id}")
            click.echo(f"   Email: {user.email}")
            click.echo(f"   Role: {user.role}")
        
        except Exception as e:
            await db.rollback()
            click.echo(f"❌ Error: {e}", err=True)
            import traceback
            traceback.print_exc()
            sys.exit(1)


@cli.command()
def test():
    """Запустить тесты"""
    import pytest
    
    click.echo("🧪 Running tests...")
    exit_code = pytest.main(["-v", "--cov=app", "tests/"])
    sys.exit(exit_code)


@cli.command()
def initdb():
    """Инициализировать базу данных (использует Alembic миграции)"""
    click.echo("🗄️  Initializing database with migrations...")
    
    try:
        # Просто применяем все миграции
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")
        click.echo("✅ Database initialized successfully")
    except Exception as e:
        click.echo(f"❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


@cli.command()
@click.option('--limit', default=10, help='Number of users to show')
def listusers(limit):
    """Показать список пользователей"""
    asyncio.run(_list_users_async(limit))


async def _list_users_async(limit: int):
    """Async функция для вывода списка пользователей"""
    from app.db.session import AsyncSessionLocal
    from app.modules.auth.models import User
    from sqlalchemy import select
    
    click.echo(f"👥 Listing users (limit: {limit})...")
    
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(User).limit(limit))
            users = result.scalars().all()
            
            if not users:
                click.echo("No users found")
                return
            
            click.echo("\n" + "="*80)
            click.echo(f"{'ID':<5} {'Username':<15} {'Email':<30} {'Role':<15} {'Active':<8}")
            click.echo("="*80)
            
            for user in users:
                active = "✓" if user.is_active == "Y" else "✗"
                click.echo(f"{user.id:<5} {user.username:<15} {user.email:<30} {user.role:<15} {active:<8}")
            
            click.echo("="*80)
            click.echo(f"\nTotal: {len(users)} user(s)")
            
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            import traceback
            traceback.print_exc()
            sys.exit(1)


@cli.command()
@click.argument('username')
def deleteuser(username):
    """Удалить пользователя по username"""
    if not click.confirm(f"Are you sure you want to delete user '{username}'?"):
        click.echo("Cancelled.")
        return
    
    asyncio.run(_delete_user_async(username))


async def _delete_user_async(username: str):
    """Async функция для удаления пользователя"""
    from app.db.session import AsyncSessionLocal
    from app.modules.auth.models import User
    from sqlalchemy import select
    
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(User).filter(User.username == username))
            user = result.scalar_one_or_none()
            
            if not user:
                click.echo(f"❌ User '{username}' not found", err=True)
                sys.exit(1)
            
            await db.delete(user)
            await db.commit()
            
            click.echo(f"✅ User '{username}' deleted successfully!")
            
        except Exception as e:
            await db.rollback()
            click.echo(f"❌ Error: {e}", err=True)
            import traceback
            traceback.print_exc()
            sys.exit(1)


@cli.command()
def dbstats():
    """Показать статистику базы данных"""
    asyncio.run(_show_db_stats_async())


async def _show_db_stats_async():
    """Async функция для вывода статистики БД"""
    from app.db.session import AsyncSessionLocal
    from app.modules.auth.models import User
    from app.modules.patients.models import Patient
    from app.modules.appointments.models import Appointment
    from app.modules.visits.models import Visit
    from app.modules.prescriptions.models import Prescription
    from sqlalchemy import select, func
    
    click.echo("📊 Database Statistics")
    click.echo("="*50)
    
    async with AsyncSessionLocal() as db:
        try:
            # Считаем пользователей
            result = await db.execute(select(func.count(User.id)))
            users_count = result.scalar()
            
            # Считаем пациентов
            result = await db.execute(select(func.count(Patient.id)))
            patients_count = result.scalar()
            
            # Считаем записи
            result = await db.execute(select(func.count(Appointment.id)))
            appointments_count = result.scalar()
            
            # Считаем визиты
            result = await db.execute(select(func.count(Visit.id)))
            visits_count = result.scalar()
            
            # Считаем рецепты
            result = await db.execute(select(func.count(Prescription.id)))
            prescriptions_count = result.scalar()
            
            click.echo(f"👥 Users:         {users_count}")
            click.echo(f"🏥 Patients:      {patients_count}")
            click.echo(f"📅 Appointments:  {appointments_count}")
            click.echo(f"🩺 Visits:        {visits_count}")
            click.echo(f"💊 Prescriptions: {prescriptions_count}")
            click.echo("="*50)
            
        except Exception as e:
            click.echo(f"❌ Error: {e}", err=True)
            import traceback
            traceback.print_exc()
            sys.exit(1)


if __name__ == "__main__":
    cli()