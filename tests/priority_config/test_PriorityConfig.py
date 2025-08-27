#!/usr/bin/env python3
"""Tests for priority_config module."""

import os
import pytest
from priority_config import PriorityConfig


class TestPriorityConfig:
    """Test cases for PriorityConfig class."""

    def test_initialization_default(self):
        """Test default initialization."""
        config = PriorityConfig()
        assert config.config_dict == {}
        assert config.env_prefix == ""
        assert config.auto_uppercase is True
        assert config.resolution_log == []

    def test_initialization_with_params(self):
        """Test initialization with parameters."""
        config_dict = {"test": "value"}
        config = PriorityConfig(config_dict, "APP_", False)
        assert config.config_dict == config_dict
        assert config.env_prefix == "APP_"
        assert config.auto_uppercase is False

    def test_repr(self):
        """Test string representation."""
        config = PriorityConfig({"a": 1, "b": 2}, "TEST_")
        result = repr(config)
        assert "PriorityConfig" in result
        assert "prefix='TEST_'" in result
        assert "configs=2" in result

    def test_get_method(self):
        """Test get method for config dict access."""
        config_dict = {"key1": "value1", "key2": "value2"}
        config = PriorityConfig(config_dict)
        
        assert config.get("key1") == "value1"
        assert config.get("key2") == "value2"
        assert config.get("missing") is None

    def test_resolve_direct_value(self):
        """Test resolution with direct value (highest precedence)."""
        config = PriorityConfig({"key": "config_val"}, "TEST_")
        os.environ["TEST_KEY"] = "env_val"
        
        result = config.resolve("key", direct_val="direct_val", default="default_val")
        
        assert result == "direct_val"
        assert len(config.resolution_log) == 1
        assert config.resolution_log[0]["source"] == "direct"
        
        # Clean up
        del os.environ["TEST_KEY"]

    def test_resolve_config_value(self):
        """Test resolution from config dict."""
        config = PriorityConfig({"key": "config_val"}, "TEST_")
        
        result = config.resolve("key", default="default_val")
        
        assert result == "config_val"
        assert config.resolution_log[0]["source"] == "config"

    def test_resolve_env_value(self):
        """Test resolution from environment variable."""
        config = PriorityConfig({}, "TEST_")
        os.environ["TEST_KEY"] = "env_val"
        
        result = config.resolve("key", default="default_val")
        
        assert result == "env_val"
        assert config.resolution_log[0]["source"] == "env:TEST_KEY"
        
        # Clean up
        del os.environ["TEST_KEY"]

    def test_resolve_env_value_no_uppercase(self):
        """Test resolution with auto_uppercase=False."""
        config = PriorityConfig({}, "test_", auto_uppercase=False)
        os.environ["test_key"] = "env_val"
        
        result = config.resolve("key", default="default_val")
        
        assert result == "env_val"
        assert config.resolution_log[0]["source"] == "env:test_key"
        
        # Clean up
        del os.environ["test_key"]

    def test_resolve_default_value(self):
        """Test resolution falling back to default."""
        config = PriorityConfig({}, "TEST_")
        
        result = config.resolve("missing_key", default="default_val")
        
        assert result == "default_val"
        assert config.resolution_log[0]["source"] == "default"

    def test_type_conversion_int(self):
        """Test integer type conversion."""
        config = PriorityConfig({}, "TEST_")
        os.environ["TEST_PORT"] = "8080"
        
        result = config.resolve("port", default=3000, type=int)
        
        assert result == 8080
        assert isinstance(result, int)
        
        # Clean up
        del os.environ["TEST_PORT"]

    def test_type_conversion_float(self):
        """Test float type conversion."""
        config = PriorityConfig({}, "TEST_")
        os.environ["TEST_RATE"] = "3.14"
        
        result = config.resolve("rate", default=1.0, type=float)
        
        assert result == 3.14
        assert isinstance(result, float)
        
        # Clean up
        del os.environ["TEST_RATE"]

    def test_type_conversion_bool_true(self):
        """Test boolean type conversion (true values)."""
        config = PriorityConfig({}, "TEST_")
        
        for env_val in ["true", "True", "TRUE", "1", "yes", "YES"]:
            os.environ["TEST_FLAG"] = env_val
            result = config.resolve("flag", default=False, type=bool)
            assert result is True
            config.clear_log()
        
        # Clean up
        del os.environ["TEST_FLAG"]

    def test_type_conversion_bool_false(self):
        """Test boolean type conversion (false values)."""
        config = PriorityConfig({}, "TEST_")
        os.environ["TEST_FLAG"] = "false"
        
        result = config.resolve("flag", default=True, type=bool)
        
        assert result is False
        
        # Clean up
        del os.environ["TEST_FLAG"]

    def test_type_conversion_list(self):
        """Test list type conversion."""
        config = PriorityConfig({}, "TEST_")
        os.environ["TEST_ITEMS"] = "item1,item2,item3"
        
        result = config.resolve("items", default=[], type=list)
        
        assert result == ["item1", "item2", "item3"]
        assert isinstance(result, list)
        
        # Clean up
        del os.environ["TEST_ITEMS"]

    def test_sensitive_detection(self):
        """Test sensitive key detection and masking."""
        config = PriorityConfig({}, "")
        
        sensitive_keys = ["password", "SECRET", "api_key", "TOKEN", "private_key"]
        
        for key in sensitive_keys:
            result = config.resolve(key, direct_val="secret123", default="")
            # The actual value should be returned
            assert result == "secret123"
            # But logged value should be masked
            log_entry = config.resolution_log[-1]
            assert "*" in log_entry["value"]
            config.clear_log()

    def test_masking_override(self):
        """Test overriding automatic masking."""
        config = PriorityConfig({}, "")
        
        # Force no masking
        result = config.resolve("password", direct_val="secret123", default="", mask=False)
        
        assert result == "secret123"
        log_entry = config.resolution_log[0]
        assert log_entry["value"] == "secret123"  # Not masked

    def test_mask_value_method(self):
        """Test the _mask_value method directly."""
        config = PriorityConfig({}, "")
        
        # Test different value lengths
        assert config._mask_value(None) is None
        assert config._mask_value("ab") == "****"
        assert config._mask_value("abcd") == "****"
        assert config._mask_value("abcde") == "ab*de"
        assert config._mask_value("secret123") == "se*****23"

    def test_print_resolutions(self, capsys):
        """Test printing resolution log."""
        config = PriorityConfig({"test": "value"}, "")
        config.resolve("test")
        config.resolve("missing", default="default")
        
        config.print_resolutions()
        
        captured = capsys.readouterr()
        assert "Configuration Resolution Log:" in captured.out
        assert "test" in captured.out
        assert "missing" in captured.out

    def test_print_resolutions_empty(self, capsys):
        """Test printing empty resolution log."""
        config = PriorityConfig({}, "")
        
        config.print_resolutions()
        
        captured = capsys.readouterr()
        assert "No configurations resolved yet" in captured.out

    def test_clear_log(self):
        """Test clearing resolution log."""
        config = PriorityConfig({"test": "value"}, "")
        config.resolve("test")
        
        assert len(config.resolution_log) == 1
        
        config.clear_log()
        
        assert len(config.resolution_log) == 0

    def test_is_sensitive_method(self):
        """Test the _is_sensitive method."""
        config = PriorityConfig({}, "")
        
        # Sensitive keys
        sensitive = ["password", "PASSWORD", "secret", "api_key", "token", "private", "auth", "credential", "cert"]
        for key in sensitive:
            assert config._is_sensitive(key) is True
        
        # Non-sensitive keys
        non_sensitive = ["username", "host", "port", "debug", "timeout"]
        for key in non_sensitive:
            assert config._is_sensitive(key) is False

    def test_integration_workflow(self):
        """Test a complete workflow example."""
        # Set up environment
        os.environ["MYAPP_DEBUG"] = "true"
        os.environ["MYAPP_SECRET"] = "topsecret123"
        
        config_dict = {
            "host": "localhost",
            "port": 3000
        }
        
        config = PriorityConfig(config_dict, "MYAPP_")
        
        # Resolve different values
        host = config.resolve("host", default="0.0.0.0")  # From config
        port = config.resolve("port", direct_val=8080, default=5000, type=int)  # Direct
        debug = config.resolve("debug", default=False, type=bool)  # From env
        secret = config.resolve("secret", default="")  # From env (sensitive)
        timeout = config.resolve("timeout", default=30, type=int)  # Default
        
        # Verify results
        assert host == "localhost"  # From config
        assert port == 8080  # Direct value
        assert debug is True  # From environment 
        assert secret == "topsecret123"  # From environment
        assert timeout == 30  # Default
        
        # Verify log
        assert len(config.resolution_log) == 5
        
        sources = [entry["source"] for entry in config.resolution_log]
        assert "config" in sources
        assert "direct" in sources
        assert "env:MYAPP_DEBUG" in sources
        assert "env:MYAPP_SECRET" in sources
        assert "default" in sources
        
        # Verify sensitive masking in log
        secret_entry = next(e for e in config.resolution_log if e["key"] == "secret")
        assert "*" in secret_entry["value"]
        
        # Clean up
        del os.environ["MYAPP_DEBUG"]
        del os.environ["MYAPP_SECRET"]


if __name__ == "__main__":
    pytest.main([__file__])