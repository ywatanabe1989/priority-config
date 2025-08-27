import pytest


def test_package_import():
    """Test that the package can be imported correctly."""
    try:
        import priority_config
        assert hasattr(priority_config, 'PriorityConfig')
    except ImportError:
        pytest.fail("Failed to import priority_config package")


def test_priority_config_import():
    """Test that PriorityConfig can be imported directly from the package."""
    from priority_config import PriorityConfig
    
    assert PriorityConfig is not None
    assert callable(PriorityConfig)


def test_priority_config_instantiation():
    """Test that PriorityConfig can be instantiated."""
    from priority_config import PriorityConfig
    
    config = PriorityConfig()
    assert config is not None
    assert hasattr(config, 'config_dict')
    assert hasattr(config, 'env_prefix')
    assert hasattr(config, 'auto_uppercase')
    assert hasattr(config, 'resolution_log')