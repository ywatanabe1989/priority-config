#!/usr/bin/env python3
"""
Getting Started with priority-config

This example demonstrates the core functionality of the priority-config package.
"""

import os
import tempfile
from priority_config import PriorityConfig

print("🔧 Getting Started with priority-config")
print("=" * 50)

# 1. Basic Configuration Resolution
print("\n1. 📝 Basic Configuration Resolution")
print("-" * 30)

# Create a simple configuration
config_dict = {
    "database_host": "localhost",
    "database_port": 5432,
    "debug": False
}

config = PriorityConfig(config_dict)

# Resolve values
host = config.resolve("database_host", default="remote.db.com")
port = config.resolve("database_port", default=3306, type=int)
debug = config.resolve("debug", default=True, type=bool)

print(f"Host: {host}")
print(f"Port: {port}")  
print(f"Debug: {debug}")

# 2. Precedence Hierarchy in Action
print("\n2. ⚡ Precedence Hierarchy: direct → config → env → default")
print("-" * 60)

# Set up environment variable
os.environ["MYAPP_TIMEOUT"] = "60"

# Create config with environment prefix
app_config = PriorityConfig({"timeout": 30}, env_prefix="MYAPP_")

# Test different precedence levels
timeout_config = app_config.resolve("timeout", default=10, type=int)
print(f"Config only: {timeout_config} (from config dict)")

timeout_env = app_config.resolve("timeout", default=10, type=int)  
print(f"Environment: {timeout_env} (from MYAPP_TIMEOUT)")

timeout_direct = app_config.resolve("timeout", direct_val=120, default=10, type=int)
print(f"Direct value: {timeout_direct} (highest precedence)")

timeout_default = app_config.resolve("missing_key", default=5, type=int)
print(f"Default: {timeout_default} (fallback)")

# 3. Type Conversion
print("\n3. 🏷️ Type Conversion Examples")
print("-" * 30)

# Set up various environment variables for testing
test_env_vars = {
    "TEST_COUNT": "42",
    "TEST_RATE": "3.14",
    "TEST_ENABLED": "true", 
    "TEST_TAGS": "web,api,backend",
    "TEST_DISABLED": "false"
}

for key, value in test_env_vars.items():
    os.environ[key] = value

test_config = PriorityConfig({}, env_prefix="TEST_")

# Test different type conversions
count = test_config.resolve("count", default=0, type=int)
rate = test_config.resolve("rate", default=1.0, type=float)
enabled = test_config.resolve("enabled", default=False, type=bool)
disabled = test_config.resolve("disabled", default=True, type=bool)
tags = test_config.resolve("tags", default=[], type=list)

print(f"Integer: {count} (type: {type(count).__name__})")
print(f"Float: {rate} (type: {type(rate).__name__})")
print(f"Bool (true): {enabled} (type: {type(enabled).__name__})")
print(f"Bool (false): {disabled} (type: {type(disabled).__name__})")
print(f"List: {tags} (type: {type(tags).__name__})")

# 4. Sensitive Data Masking
print("\n4. 🔐 Sensitive Data Masking")
print("-" * 30)

# Set up sensitive data
os.environ["SECRET_API_KEY"] = "sk-1234567890abcdef"
os.environ["DB_PASSWORD"] = "supersecret123"

secure_config = PriorityConfig({}, env_prefix="")

# Resolve sensitive values
api_key = secure_config.resolve("secret_api_key", default="")
password = secure_config.resolve("db_password", default="")

print(f"API Key retrieved: {len(api_key)} characters")
print(f"Password retrieved: {len(password)} characters")

print("\n📊 Resolution log shows masked values:")
secure_config.print_resolutions()

# 5. Configuration from Multiple Sources
print("\n5. 🌟 Real-world Example: Web Application Config")
print("-" * 45)

# Simulate a web application configuration
web_config_dict = {
    "host": "0.0.0.0",
    "port": 8000,
    "workers": 4,
    "log_level": "INFO"
}

# Set some environment overrides
os.environ["WEBAPP_HOST"] = "127.0.0.1"
os.environ["WEBAPP_SECRET_KEY"] = "prod-secret-key-2024"
os.environ["WEBAPP_DEBUG"] = "false"

web_config = PriorityConfig(web_config_dict, env_prefix="WEBAPP_")

# Resolve all configuration
print("Web Application Configuration:")
print(f"  Host: {web_config.resolve('host', default='localhost')}")
print(f"  Port: {web_config.resolve('port', default=5000, type=int)}")
print(f"  Workers: {web_config.resolve('workers', default=1, type=int)}")
print(f"  Debug: {web_config.resolve('debug', default=True, type=bool)}")
print(f"  Log Level: {web_config.resolve('log_level', default='DEBUG')}")
print(f"  Secret Key: {'*' * len(web_config.resolve('secret_key', default=''))}")

print("\n📋 Complete Resolution Log:")
web_config.print_resolutions()

# 6. Django-style Configuration
print("\n6. 🎯 Django-style Configuration Example")
print("-" * 40)

# Simulate Django settings
os.environ["DJANGO_DEBUG"] = "False"
os.environ["DJANGO_SECRET_KEY"] = "django-secret-production-key"
os.environ["DJANGO_DATABASE_URL"] = "postgresql://user:pass@db:5432/mydb"

django_config = PriorityConfig({}, env_prefix="DJANGO_", auto_uppercase=True)

# Django-style resolution
DEBUG = django_config.resolve("debug", default=True, type=bool)
SECRET_KEY = django_config.resolve("secret_key", default="dev-key")
DATABASE_URL = django_config.resolve("database_url", default="sqlite:///db.sqlite3")
ALLOWED_HOSTS = django_config.resolve("allowed_hosts", default="localhost,127.0.0.1", type=list)

print("Django Settings:")
print(f"  DEBUG = {DEBUG}")
print(f"  SECRET_KEY = {'*' * len(SECRET_KEY)}")
print(f"  DATABASE_URL = {DATABASE_URL}")
print(f"  ALLOWED_HOSTS = {ALLOWED_HOSTS}")

# Clean up environment variables
cleanup_vars = [
    "MYAPP_TIMEOUT", "TEST_COUNT", "TEST_RATE", "TEST_ENABLED", 
    "TEST_TAGS", "TEST_DISABLED", "SECRET_API_KEY", "DB_PASSWORD",
    "WEBAPP_HOST", "WEBAPP_SECRET_KEY", "WEBAPP_DEBUG",
    "DJANGO_DEBUG", "DJANGO_SECRET_KEY", "DJANGO_DATABASE_URL"
]

for var in cleanup_vars:
    if var in os.environ:
        del os.environ[var]

print("\n✅ Tutorial completed! You now understand:")
print("   🔧 Basic configuration resolution")
print("   ⚡ Precedence hierarchy (direct → config → env → default)")
print("   🏷️ Automatic type conversion") 
print("   🔐 Sensitive data masking")
print("   📊 Resolution logging for debugging")
print("   🌟 Real-world usage patterns")

print("\n📚 Next steps:")
print("   • Try the CLI examples with different frameworks")
print("   • Check out the comprehensive test suite")  
print("   • Explore advanced features in the documentation")