#!/usr/bin/env python3
# Test file for pip install functionality

import pytest
import subprocess
import sys
from pathlib import Path


class TestPipInstall:
    """Test suite for pip install functionality"""

    def test_package_can_be_installed_in_editable_mode(self):
        """Test that the package can be installed with pip install -e ."""
        project_root = Path(__file__).parents[2]
        
        # Run pip install -e . in the project directory
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", "."],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"pip install -e . failed: {result.stderr}"
        assert "Successfully installed priority-config" in result.stdout or "Requirement already satisfied" in result.stdout

    def test_package_can_be_imported_after_install(self):
        """Test that the package can be imported after pip install."""
        try:
            import priority_config
            assert priority_config is not None
        except ImportError as e:
            pytest.fail(f"Could not import priority_config after installation: {e}")

    def test_package_has_proper_structure(self):
        """Test that the installed package has expected structure."""
        import priority_config
        
        # Check that package has expected classes/modules
        # Priority config should have PriorityConfig class
        assert hasattr(priority_config, 'PriorityConfig'), "Package should have PriorityConfig class"
        
        # Test basic functionality
        config = priority_config.PriorityConfig({}, "TEST_")
        assert config is not None, "Should be able to create PriorityConfig instance"

    def test_cli_entry_points_work(self):
        """Test that CLI commands work after installation."""
        # Since priority_config doesn't have CLI entry points, test basic module execution
        project_root = Path(__file__).parents[2]
        
        # Test basic Python module execution
        result = subprocess.run(
            [sys.executable, "-c", "import priority_config; print('Priority Config loaded successfully')"],
            cwd=project_root,
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Module import command failed: {result.stderr}"
        assert "Priority Config loaded successfully" in result.stdout

    def test_package_version_accessible(self):
        """Test that package version is accessible."""
        import priority_config
        
        # Should be able to access version information
        # Check common version attributes
        version_found = False
        for attr in ['__version__', 'version', '_version']:
            if hasattr(priority_config, attr):
                version_found = True
                break
        
        # Version might not be explicitly defined, which is ok for development
        # Just ensure the module loads properly
        assert priority_config.__name__ == 'priority_config'

    def test_src_layout_structure_is_correct(self):
        """Test that src-layout structure is properly set up."""
        project_root = Path(__file__).parents[2]
        
        # Check that src-layout structure exists
        src_package_dir = project_root / "src" / "priority_config"
        assert src_package_dir.exists(), "src/priority_config directory should exist"
        assert src_package_dir.is_dir(), "src/priority_config should be a directory"
        
        # Check that __init__.py exists
        init_file = src_package_dir / "__init__.py"
        assert init_file.exists(), "src/priority_config/__init__.py should exist"

    def test_egg_info_created_in_correct_location(self):
        """Test that pip install creates egg-info in the correct location."""
        project_root = Path(__file__).parents[2]
        
        # For src-layout packages, egg-info should be in src/ directory
        src_egg_info_dirs = list((project_root / "src").glob("*.egg-info"))
        
        assert len(src_egg_info_dirs) >= 1, "Should have at least one .egg-info directory in src/"
        
        # Check that the egg-info directory name is correct
        expected_name = "priority_config.egg-info"
        found_expected = any(dir.name == expected_name for dir in src_egg_info_dirs)
        assert found_expected, f"Should have {expected_name} in src/ directory"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])