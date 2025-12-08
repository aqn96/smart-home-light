#!/usr/bin/env python3
"""
Smart Home Light - Management CLI
Usage: ./manage.py <command> [subcommand] [args]
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import SessionLocal, User, LightHistory, hash_password

def print_help():
    help_text = """
╔══════════════════════════════════════════════════════════════╗
║           🏠 Smart Home Light - Management CLI               ║
╚══════════════════════════════════════════════════════════════╝

USAGE:
    ./manage.py <command> [subcommand] [arguments]

COMMANDS:

  users                     Manage users
    list                    Show all users
    add <user> <pass> [email]  Create a new user (email optional)
    delete <username>       Delete a user
    reset <username>         Reset password (prompts for new password)
    clear                   Delete ALL users (asks confirmation)

  history                   Manage action history
    list                    Show recent history (last 20)
    list all                Show all history
    clear                   Delete ALL history (asks confirmation)

  db                        Database operations
    info                    Show database statistics
    reset                   Wipe entire database (asks confirmation)

  help, --help, -h          Show this help message

EXAMPLES:
    ./manage.py users list
    ./manage.py users add john mypassword123
    ./manage.py users add john mypassword123 john@email.com
    ./manage.py users delete john
    ./manage.py users reset john
    ./manage.py history list
    ./manage.py db info
    ./manage.py db reset
"""
    print(help_text)

def get_db():
    return SessionLocal()

# ============ USER COMMANDS ============

def users_list():
    db = get_db()
    users = db.query(User).all()
    if not users:
        print("📭 No users found.")
        return
    print(f"\n👥 Users ({len(users)} total):")
    print("-" * 60)
    for u in users:
        print(f"  ID: {u.id}")
        print(f"      Username: {u.username}")
        print(f"      Email:    {u.email}")
        print(f"      Created:  {u.created_at}")
        print()
    db.close()

def users_add(username, password, email=None):
    db = get_db()
    existing = db.query(User).filter(User.username == username).first()
    if existing:
        print(f"❌ User '{username}' already exists.")
        db.close()
        return
    if not email:
        email = f"{username}@local.home"
    existing_email = db.query(User).filter(User.email == email).first()
    if existing_email:
        print(f"❌ Email '{email}' already in use.")
        db.close()
        return
    hashed = hash_password(password)
    user = User(username=username, email=email, hashed_password=hashed)
    db.add(user)
    db.commit()
    print(f"✅ User '{username}' created (email: {email}).")
    db.close()

def users_delete(username):
    db = get_db()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"❌ User '{username}' not found.")
        db.close()
        return
    db.delete(user)
    db.commit()
    print(f"✅ User '{username}' deleted.")
    db.close()

def users_password(username, new_password):
    db = get_db()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"❌ User '{username}' not found.")
        db.close()
        return
    user.hashed_password = hash_password(new_password)
    db.commit()
    print(f"✅ Password updated for '{username}'.")
    db.close()

def users_reset(username):
    import getpass
    db = get_db()
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"❌ User '{username}' not found.")
        db.close()
        return
    new_password = getpass.getpass("Enter new password: ")
    if not new_password:
        print("❌ Password cannot be empty.")
        db.close()
        return
    confirm = getpass.getpass("Confirm new password: ")
    if new_password != confirm:
        print("❌ Passwords don't match.")
        db.close()
        return
    user.hashed_password = hash_password(new_password)
    db.commit()
    print(f"✅ Password updated for '{username}'.")
    db.close()

def users_clear():
    confirm = input("⚠️  Delete ALL users? Type 'yes' to confirm: ")
    if confirm.lower() != 'yes':
        print("❌ Cancelled.")
        return
    db = get_db()
    count = db.query(User).count()
    db.query(User).delete()
    db.commit()
    print(f"✅ Deleted {count} user(s).")
    db.close()

# ============ HISTORY COMMANDS ============

def history_list(show_all=False):
    db = get_db()
    query = db.query(LightHistory).order_by(LightHistory.timestamp.desc())
    if not show_all:
        query = query.limit(20)
    history = query.all()
    if not history:
        print("📭 No history found.")
        return
    total = db.query(LightHistory).count()
    showing = "all" if show_all else f"last {len(history)}"
    print(f"\n📜 Action History ({showing} of {total} total):")
    print("-" * 60)
    for h in history:
        print(f"  [{h.timestamp}] {h.action} by {h.username}")
    print()
    db.close()

def history_clear():
    confirm = input("⚠️  Delete ALL history? Type 'yes' to confirm: ")
    if confirm.lower() != 'yes':
        print("❌ Cancelled.")
        return
    db = get_db()
    count = db.query(LightHistory).count()
    db.query(LightHistory).delete()
    db.commit()
    print(f"✅ Deleted {count} history record(s).")
    db.close()

# ============ DATABASE COMMANDS ============

def db_info():
    db = get_db()
    user_count = db.query(User).count()
    history_count = db.query(LightHistory).count()
    print(f"""
╔══════════════════════════════════════╗
║         📊 Database Info             ║
╠══════════════════════════════════════╣
║  👥 Users:          {user_count:<16} ║
║  📜 History:        {history_count:<16} ║
╚══════════════════════════════════════╝
""")
    db.close()

def db_reset():
    confirm = input("⚠️  WIPE ENTIRE DATABASE? Type 'yes' to confirm: ")
    if confirm.lower() != 'yes':
        print("❌ Cancelled.")
        return
    db = get_db()
    users = db.query(User).count()
    history = db.query(LightHistory).count()
    db.query(User).delete()
    db.query(LightHistory).delete()
    db.commit()
    print(f"✅ Database reset. Deleted {users} user(s) and {history} history record(s).")
    db.close()

# ============ MAIN ============

def main():
    args = sys.argv[1:]
    
    if not args or args[0] in ['help', '--help', '-h']:
        print_help()
        return
    
    cmd = args[0]
    sub = args[1] if len(args) > 1 else None
    
    if cmd == 'users':
        if sub == 'list':
            users_list()
        elif sub == 'add':
            if len(args) < 4:
                print("❌ Usage: ./manage.py users add <username> <password> [email]")
                return
            email = args[4] if len(args) > 4 else None
            users_add(args[2], args[3], email)
        elif sub == 'delete':
            if len(args) < 3:
                print("❌ Usage: ./manage.py users delete <username>")
                return
            users_delete(args[2])
        elif sub == 'reset':
            if len(args) < 3:
                print("❌ Usage: ./manage.py users reset <username>")
                return
            users_reset(args[2])
        elif sub == 'clear':
            users_clear()
        else:
            print("❌ Unknown subcommand. Use: list, add, delete, reset, clear")
    
    elif cmd == 'history':
        if sub == 'list':
            show_all = len(args) > 2 and args[2] == 'all'
            history_list(show_all)
        elif sub == 'clear':
            history_clear()
        else:
            print("❌ Unknown subcommand. Use: list, clear")
    
    elif cmd == 'db':
        if sub == 'info':
            db_info()
        elif sub == 'reset':
            db_reset()
        else:
            print("❌ Unknown subcommand. Use: info, reset")
    
    else:
        print(f"❌ Unknown command: {cmd}")
        print("   Run ./manage.py --help for usage.")

if __name__ == "__main__":
    main()
