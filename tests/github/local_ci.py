#!/usr/bin/env python3
"""
Local GitHub Actions Emulator
Runs the same validation steps as GitHub Actions locally
"""

import subprocess
import sys
import json
import os
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import time
import shutil


class LocalCIEmulator:
    """Local GitHub Actions emulator for validation workflow with container runtime detection."""
    
    def __init__(self, project_root: Path = None, force_runtime: str = None):
        self.project_root = project_root or Path.cwd()
        self.results = {}
        self.start_time = time.time()
        self.forced_runtime = force_runtime or os.environ.get("CI_CONTAINER_RUNTIME")
        self.container_runtime = self._detect_container_runtime()
        self.cache_dir = self._get_cache_dir()
        
    def _detect_container_runtime(self) -> str:
        """Detect available container runtime, prioritizing Singularity for HPC compatibility."""
        # If runtime is forced via environment or parameter
        if self.forced_runtime:
            runtime = self.forced_runtime.lower()
            if runtime in ["singularity", "apptainer", "docker", "native"]:
                if runtime == "native" or shutil.which(runtime):
                    return runtime
                else:
                    print(f"⚠️ Warning: Forced runtime '{runtime}' not found, falling back to auto-detection")
        
        # Auto-detection: Prioritize Apptainer → Singularity → Docker for HPC environments
        if shutil.which("apptainer"):
            return "apptainer"
        elif shutil.which("singularity"):
            return "singularity"
        elif shutil.which("docker"):
            return "docker"
        else:
            return "native"
    
    def _get_cache_dir(self) -> Path:
        """Get cache directory for containers."""
        if self.container_runtime in ["singularity", "apptainer"]:
            # HPC-style cache directory
            cache_dir = Path(os.environ.get("SLURM_SUBMIT_DIR", str(Path.home()))) / ".hpc_ci_cache"
        else:
            # Standard cache directory
            cache_dir = Path.home() / ".local_ci_cache"
        
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    def _run_in_container(self, cmd: str, container_image: str = "python:3.11-slim") -> Tuple[bool, str, str]:
        """Run command in container using available runtime."""
        if self.container_runtime == "docker":
            # Docker command
            docker_cmd = [
                "docker", "run", "--rm", 
                "-v", f"{self.project_root}:/workspace",
                "-w", "/workspace",
                container_image,
                "bash", "-c", cmd
            ]
            result = subprocess.run(docker_cmd, capture_output=True, text=True, cwd=self.project_root)
            
        elif self.container_runtime in ["singularity", "apptainer"]:
            # Singularity/Apptainer command
            container_name = container_image.replace(":", "_").replace("/", "_")
            sif_file = self.cache_dir / f"{container_name}.sif"
            
            # Pull container if not cached
            if not sif_file.exists():
                print(f"  📥 Pulling container: {container_image}")
                pull_cmd = [self.container_runtime, "pull", str(sif_file), f"docker://{container_image}"]
                pull_result = subprocess.run(pull_cmd, capture_output=True, text=True)
                if pull_result.returncode != 0:
                    return False, "", f"Failed to pull container: {pull_result.stderr}"
            
            # Run in container
            exec_cmd = [
                self.container_runtime, "exec",
                "--bind", f"{self.project_root}:/workspace",
                "--pwd", "/workspace",
                str(sif_file),
                "bash", "-c", cmd
            ]
            result = subprocess.run(exec_cmd, capture_output=True, text=True, cwd=self.project_root)
            
        else:
            # Native execution
            result = subprocess.run(["bash", "-c", cmd], capture_output=True, text=True, cwd=self.project_root)
        
        success = result.returncode == 0
        return success, result.stdout, result.stderr
        
    def run_command(self, cmd: List[str], step_name: str, allow_failure: bool = False, use_container: bool = False, container_image: str = "python:3.11-slim") -> Tuple[bool, str, str]:
        """Run a command and capture output."""
        print(f"🔄 Running: {step_name}")
        if use_container and self.container_runtime != "native":
            print(f"   Container: {container_image} via {self.container_runtime}")
        print(f"   Command: {' '.join(cmd)}")
        
        try:
            if use_container and self.container_runtime != "native":
                # Run in container
                cmd_str = ' '.join(cmd)
                success, stdout, stderr = self._run_in_container(cmd_str, container_image)
            else:
                # Run natively
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    cwd=self.project_root,
                    timeout=300  # 5 minute timeout
                )
                success = result.returncode == 0 or allow_failure
                stdout = result.stdout
                stderr = result.stderr
            
            success = success or allow_failure
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"   {status}")
            
            if stdout:
                print(f"   Output: {stdout.strip()}")
            if stderr and not success:
                print(f"   Error: {stderr.strip()}")
                
            return success, stdout, stderr
            
        except subprocess.TimeoutExpired:
            print(f"   ⏰ TIMEOUT after 5 minutes")
            return False, "", "Timeout after 5 minutes"
        except Exception as e:
            print(f"   💥 ERROR: {e}")
            return False, "", str(e)
    
    def check_python_setup(self) -> bool:
        """Check Python setup and dependencies."""
        print("\n" + "="*60)
        print("🐍 PYTHON SETUP")
        print("="*60)
        
        # Check Python version
        success, stdout, _ = self.run_command([sys.executable, "--version"], "Python version check")
        if not success:
            return False
            
        # Check if project can be installed
        success, _, _ = self.run_command([
            sys.executable, "-m", "pip", "install", "-e", ".[dev]"
        ], "Install project in development mode")
        
        return success
    
    def run_linting(self) -> bool:
        """Run linting checks."""
        print("\n" + "="*60) 
        print("🔍 LINTING")
        print("="*60)
        
        # Run ruff check
        success, _, _ = self.run_command([
            "ruff", "check", "src/", "--output-format=json"
        ], "Ruff linting", allow_failure=True)
        
        if not success:
            # Try with make command
            success, _, _ = self.run_command(["make", "lint"], "Make lint")
            
        return success
    
    def run_tests(self) -> bool:
        """Run tests with coverage."""
        print("\n" + "="*60)
        print("🧪 TESTS & COVERAGE")  
        print("="*60)
        
        # Run tests with coverage
        success, stdout, stderr = self.run_command([
            "pytest", "tests/", 
            "--cov=src/minimal_pip_project",
            "--cov-report=term-missing",
            "--cov-report=json",
            "--cov-fail-under=100",
            "-v"
        ], "Run tests with 100% coverage requirement")
        
        # Try to extract coverage info
        coverage_file = self.project_root / "tests/coverage.json"
        if coverage_file.exists():
            try:
                with open(coverage_file) as f:
                    coverage_data = json.load(f)
                    total_coverage = coverage_data.get("totals", {}).get("percent_covered", 0)
                    print(f"   📊 Coverage: {total_coverage:.2f}%")
                    self.results["coverage"] = total_coverage
            except Exception as e:
                print(f"   ⚠️  Could not parse coverage: {e}")
                
        return success
    
    def check_src_test_agreement(self) -> bool:
        """Check src-test agreement."""
        print("\n" + "="*60)
        print("🤝 SRC-TEST AGREEMENT")
        print("="*60)
        
        agreement_script = self.project_root / "tests/custom/test_src_test_agreement.py"
        if not agreement_script.exists():
            print("   ⚠️  Agreement script not found, skipping")
            return True
            
        success, _, _ = self.run_command([
            sys.executable, str(agreement_script)
        ], "Check src-test agreement")
        
        return success
    
    def generate_report(self) -> Dict:
        """Generate final report."""
        duration = time.time() - self.start_time
        
        report = {
            "workflow": "Local CI Validation",
            "status": "success" if all(self.results.values()) else "failure", 
            "duration_seconds": round(duration, 2),
            "steps": self.results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "coverage": self.results.get("coverage", 0)
        }
        
        return report
    
    def run_full_validation(self) -> bool:
        """Run the complete validation pipeline."""
        print("🚀 LOCAL GITHUB ACTIONS EMULATOR")
        print("=" * 60)
        print(f"Project: {self.project_root}")
        print(f"Python: {sys.executable}")
        
        # Show container runtime detection
        runtime_icons = {
            "docker": "🐳 Docker",
            "singularity": "📦 Singularity",
            "apptainer": "📦 Apptainer", 
            "native": "💻 Native"
        }
        print(f"Runtime: {runtime_icons.get(self.container_runtime, self.container_runtime)}")
        if self.container_runtime != "native":
            print(f"Cache: {self.cache_dir}")
        
        print("=" * 60)
        
        steps = [
            ("python_setup", self.check_python_setup),
            ("linting", self.run_linting), 
            ("tests", self.run_tests),
            ("agreement", self.check_src_test_agreement)
        ]
        
        all_passed = True
        
        for step_name, step_func in steps:
            try:
                result = step_func()
                self.results[step_name] = result
                if not result:
                    all_passed = False
            except Exception as e:
                print(f"💥 Step {step_name} failed with exception: {e}")
                self.results[step_name] = False
                all_passed = False
        
        # Generate report
        report = self.generate_report()
        
        print("\n" + "="*60)
        print("📊 FINAL REPORT")
        print("="*60)
        
        for step, passed in self.results.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{step:20} {status}")
            
        print(f"\nOverall Status: {'✅ SUCCESS' if all_passed else '❌ FAILURE'}")
        print(f"Duration: {report['duration_seconds']}s")
        if "coverage" in self.results:
            print(f"Coverage: {report['coverage']:.2f}%")
        
        # Save report
        report_file = self.project_root / "tests/github/local_ci_report.json"
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2)
        print(f"Report saved: {report_file}")
        
        return all_passed


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Local GitHub Actions CI Emulator")
    parser.add_argument(
        "--runtime", 
        choices=["apptainer", "singularity", "docker", "native"],
        help="Force specific container runtime (overrides auto-detection)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true", 
        help="Verbose output"
    )
    
    args = parser.parse_args()
    project_root = Path.cwd()
    
    # Check if we're in the right directory
    if not (project_root / "pyproject.toml").exists():
        print("❌ Error: pyproject.toml not found. Run from project root.")
        sys.exit(1)
        
    emulator = LocalCIEmulator(project_root, force_runtime=args.runtime)
    success = emulator.run_full_validation()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()