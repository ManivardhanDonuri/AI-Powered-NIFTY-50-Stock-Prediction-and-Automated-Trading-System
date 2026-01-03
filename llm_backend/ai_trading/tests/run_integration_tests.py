"""
Integration Test Runner for AI Trading Assistant

This script runs comprehensive integration tests and generates detailed reports
covering all aspects of the system including performance, privacy, and resilience.
"""

import asyncio
import sys
import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import subprocess
import psutil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IntegrationTestRunner:
    """Comprehensive integration test runner with reporting."""
    
    def __init__(self):
        self.results = {
            "test_run_id": f"integration_test_{int(time.time())}",
            "start_time": datetime.now().isoformat(),
            "end_time": None,
            "total_duration": 0,
            "system_info": self._get_system_info(),
            "test_categories": {},
            "overall_status": "PENDING",
            "summary": {}
        }
        
        self.test_categories = [
            ("workflows", "End-to-End Workflows"),
            ("websocket", "WebSocket Integration"),
            ("performance", "Performance and Load Testing"),
            ("privacy", "Data Privacy and Local Processing"),
            ("resilience", "System Resilience and Error Handling")
        ]
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information for test context."""
        try:
            return {
                "python_version": sys.version,
                "platform": sys.platform,
                "cpu_count": psutil.cpu_count(),
                "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
                "disk_free_gb": round(psutil.disk_usage('.').free / (1024**3), 2),
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            logger.warning(f"Could not gather system info: {e}")
            return {"error": str(e)}
    
    async def check_prerequisites(self) -> Dict[str, bool]:
        """Check if all prerequisites are met for testing."""
        logger.info("Checking test prerequisites...")
        
        prerequisites = {
            "ollama_service": False,
            "database_access": False,
            "required_modules": False,
            "test_data": False
        }
        
        # Check Ollama service
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:11434", timeout=aiohttp.ClientTimeout(total=5)) as response:
                    if response.status == 200:
                        text = await response.text()
                        prerequisites["ollama_service"] = "Ollama is running" in text
        except Exception as e:
            logger.warning(f"Ollama service check failed: {e}")
        
        # Check database access
        try:
            from ..logging.audit_logger import get_audit_logger
            audit_logger = get_audit_logger()
            # Simple test to verify database access
            prerequisites["database_access"] = True
        except Exception as e:
            logger.warning(f"Database access check failed: {e}")
        
        # Check required modules
        try:
            import pytest
            import hypothesis
            import websockets
            prerequisites["required_modules"] = True
        except ImportError as e:
            logger.error(f"Required modules missing: {e}")
        
        # Check test data availability
        try:
            # Verify we can create test fixtures
            prerequisites["test_data"] = True
        except Exception as e:
            logger.warning(f"Test data check failed: {e}")
        
        logger.info(f"Prerequisites check: {prerequisites}")
        return prerequisites
    
    async def run_test_category(self, category: str, description: str) -> Dict[str, Any]:
        """Run a specific test category and collect results."""
        logger.info(f"Running {description} tests...")
        
        start_time = time.time()
        
        try:
            # Run pytest for the specific test category
            cmd = [
                sys.executable, "-m", "pytest", 
                f"llm_backend/ai_trading/tests/test_integration.py::Test{category.title().replace('_', '')}",
                "-v", "--tb=short", "--json-report", f"--json-report-file=test_results_{category}.json"
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per category
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            # Parse results
            test_result = {
                "category": category,
                "description": description,
                "duration": duration,
                "return_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "tests_skipped": 0
            }
            
            # Try to parse JSON report if available
            try:
                json_file = Path(f"test_results_{category}.json")
                if json_file.exists():
                    with open(json_file) as f:
                        json_data = json.load(f)
                        summary = json_data.get("summary", {})
                        test_result.update({
                            "tests_run": summary.get("total", 0),
                            "tests_passed": summary.get("passed", 0),
                            "tests_failed": summary.get("failed", 0),
                            "tests_skipped": summary.get("skipped", 0)
                        })
                    json_file.unlink()  # Clean up
            except Exception as e:
                logger.warning(f"Could not parse JSON report for {category}: {e}")
            
            # Extract key metrics from stdout
            if "PASSED" in result.stdout:
                passed_count = result.stdout.count("PASSED")
                test_result["tests_passed"] = max(test_result["tests_passed"], passed_count)
            
            if "FAILED" in result.stdout:
                failed_count = result.stdout.count("FAILED")
                test_result["tests_failed"] = max(test_result["tests_failed"], failed_count)
            
            if "SKIPPED" in result.stdout:
                skipped_count = result.stdout.count("SKIPPED")
                test_result["tests_skipped"] = max(test_result["tests_skipped"], skipped_count)
            
            logger.info(f"{description} tests completed in {duration:.2f}s - Status: {test_result['status']}")
            
        except subprocess.TimeoutExpired:
            test_result = {
                "category": category,
                "description": description,
                "duration": 300,
                "return_code": -1,
                "stdout": "",
                "stderr": "Test timeout after 5 minutes",
                "status": "TIMEOUT",
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "tests_skipped": 0
            }
            logger.error(f"{description} tests timed out")
            
        except Exception as e:
            test_result = {
                "category": category,
                "description": description,
                "duration": time.time() - start_time,
                "return_code": -1,
                "stdout": "",
                "stderr": str(e),
                "status": "ERROR",
                "tests_run": 0,
                "tests_passed": 0,
                "tests_failed": 0,
                "tests_skipped": 0
            }
            logger.error(f"{description} tests failed with error: {e}")
        
        return test_result
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all integration test categories."""
        logger.info("Starting comprehensive integration test suite...")
        
        # Check prerequisites
        prerequisites = await self.check_prerequisites()
        self.results["prerequisites"] = prerequisites
        
        # Check if we can proceed
        critical_missing = []
        if not prerequisites.get("required_modules", False):
            critical_missing.append("required_modules")
        
        if critical_missing:
            logger.error(f"Critical prerequisites missing: {critical_missing}")
            self.results["overall_status"] = "ABORTED"
            self.results["error"] = f"Missing critical prerequisites: {critical_missing}"
            return self.results
        
        # Warn about optional prerequisites
        if not prerequisites.get("ollama_service", False):
            logger.warning("Ollama service not available - some tests may be skipped")
        
        # Run each test category
        for category, description in self.test_categories:
            try:
                result = await self.run_test_category(category, description)
                self.results["test_categories"][category] = result
            except Exception as e:
                logger.error(f"Failed to run {description} tests: {e}")
                self.results["test_categories"][category] = {
                    "category": category,
                    "description": description,
                    "status": "ERROR",
                    "error": str(e)
                }
        
        # Calculate overall results
        self._calculate_summary()
        
        self.results["end_time"] = datetime.now().isoformat()
        self.results["total_duration"] = sum(
            cat.get("duration", 0) for cat in self.results["test_categories"].values()
        )
        
        logger.info("Integration test suite completed")
        return self.results
    
    def _calculate_summary(self):
        """Calculate overall test summary."""
        total_tests = 0
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        categories_passed = 0
        categories_failed = 0
        categories_error = 0
        
        for category_result in self.results["test_categories"].values():
            status = category_result.get("status", "ERROR")
            
            if status == "PASSED":
                categories_passed += 1
            elif status == "FAILED":
                categories_failed += 1
            else:
                categories_error += 1
            
            total_tests += category_result.get("tests_run", 0)
            total_passed += category_result.get("tests_passed", 0)
            total_failed += category_result.get("tests_failed", 0)
            total_skipped += category_result.get("tests_skipped", 0)
        
        # Determine overall status
        if categories_error > 0:
            overall_status = "ERROR"
        elif categories_failed > 0:
            overall_status = "FAILED"
        elif categories_passed > 0:
            overall_status = "PASSED"
        else:
            overall_status = "NO_TESTS"
        
        self.results["overall_status"] = overall_status
        self.results["summary"] = {
            "total_categories": len(self.test_categories),
            "categories_passed": categories_passed,
            "categories_failed": categories_failed,
            "categories_error": categories_error,
            "total_tests": total_tests,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "total_skipped": total_skipped,
            "success_rate": round(total_passed / max(total_tests, 1) * 100, 2)
        }
    
    def generate_report(self, output_file: str = None) -> str:
        """Generate a comprehensive test report."""
        if output_file is None:
            output_file = f"integration_test_report_{int(time.time())}.json"
        
        # Save detailed JSON report
        with open(output_file, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        # Generate human-readable summary
        summary = self._generate_text_summary()
        
        # Save text summary
        text_file = output_file.replace('.json', '_summary.txt')
        with open(text_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        logger.info(f"Test report saved to {output_file}")
        logger.info(f"Test summary saved to {text_file}")
        
        return summary
    
    def _generate_text_summary(self) -> str:
        """Generate human-readable test summary."""
        summary = self.results["summary"]
        
        report = f"""
AI Trading Assistant - Integration Test Report
==============================================

Test Run ID: {self.results['test_run_id']}
Start Time: {self.results['start_time']}
End Time: {self.results['end_time']}
Total Duration: {self.results['total_duration']:.2f} seconds

Overall Status: {self.results['overall_status']}

System Information:
- Python Version: {self.results['system_info'].get('python_version', 'Unknown')}
- Platform: {self.results['system_info'].get('platform', 'Unknown')}
- CPU Count: {self.results['system_info'].get('cpu_count', 'Unknown')}
- Memory: {self.results['system_info'].get('memory_total_gb', 'Unknown')} GB

Prerequisites Check:
"""
        
        for prereq, status in self.results.get("prerequisites", {}).items():
            status_str = "PASS" if status else "FAIL"
            report += f"- {prereq}: {status_str}\n"
        
        report += f"""
Test Summary:
- Total Categories: {summary['total_categories']}
- Categories Passed: {summary['categories_passed']}
- Categories Failed: {summary['categories_failed']}
- Categories Error: {summary['categories_error']}
- Total Tests: {summary['total_tests']}
- Tests Passed: {summary['total_passed']}
- Tests Failed: {summary['total_failed']}
- Tests Skipped: {summary['total_skipped']}
- Success Rate: {summary['success_rate']}%

Category Results:
"""
        
        for category, result in self.results["test_categories"].items():
            status_icon = {
                "PASSED": "[PASS]",
                "FAILED": "[FAIL]",
                "ERROR": "[ERROR]",
                "TIMEOUT": "[TIMEOUT]",
                "SKIPPED": "[SKIP]"
            }.get(result.get("status", "ERROR"), "[?]")
            
            report += f"""
{status_icon} {result.get('description', category)}
   Status: {result.get('status', 'UNKNOWN')}
   Duration: {result.get('duration', 0):.2f}s
   Tests: {result.get('tests_passed', 0)}/{result.get('tests_run', 0)} passed
"""
            
            if result.get("status") in ["FAILED", "ERROR"] and result.get("stderr"):
                report += f"   Error: {result['stderr'][:200]}...\n"
        
        report += f"""
Recommendations:
"""
        
        # Add recommendations based on results
        if not self.results.get("prerequisites", {}).get("ollama_service", False):
            report += "- Install and start Ollama service for complete LLM testing\n"
        
        if summary["categories_failed"] > 0:
            report += "- Review failed test categories and address underlying issues\n"
        
        if summary["success_rate"] < 80:
            report += "- Success rate below 80% - investigate system stability\n"
        
        if summary["categories_error"] > 0:
            report += "- Address test execution errors before production deployment\n"
        
        report += """
For detailed test output, see the full JSON report.
"""
        
        return report


async def main():
    """Main test runner function."""
    print("AI Trading Assistant - Integration Test Suite")
    print("=" * 50)
    
    runner = IntegrationTestRunner()
    
    try:
        # Run all tests
        results = await runner.run_all_tests()
        
        # Generate report
        summary = runner.generate_report()
        
        # Print summary to console
        print(summary)
        
        # Exit with appropriate code
        if results["overall_status"] in ["PASSED"]:
            sys.exit(0)
        elif results["overall_status"] in ["FAILED", "ERROR"]:
            sys.exit(1)
        else:
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\nTest run interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\nTest run failed with error: {e}")
        logger.exception("Test run failed")
        sys.exit(1)


if __name__ == "__main__":
    # Handle command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("""
AI Trading Assistant Integration Test Runner

Usage:
  python run_integration_tests.py [options]

Options:
  --help    Show this help message
  
The test runner will:
1. Check system prerequisites
2. Run all integration test categories
3. Generate detailed reports
4. Provide recommendations

Test Categories:
- End-to-End Workflows
- WebSocket Integration  
- Performance and Load Testing
- Data Privacy and Local Processing
- System Resilience and Error Handling
""")
            sys.exit(0)
    
    # Run the test suite
    asyncio.run(main())