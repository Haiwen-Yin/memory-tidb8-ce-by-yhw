#!/usr/bin/env python3
"""
Multi-Agent Architecture Test Script for memory-tidb8-ce-by-yhw v0.1.2
Author: 胖头鱼 🐟
License: Apache-2.0

Tests all Multi-Agent components before production deployment.
Run this script after TiDB is online and schema is applied.

Usage:
    python test_multi_agent.py [--host HOST] [--port PORT] [--db DATABASE]
"""

import sys
import argparse
from datetime import datetime


def _continue_without_db():
    """Automatically continue without database connection (non-interactive)"""
    return True


def main():
    parser = argparse.ArgumentParser(description="Test Multi-Agent Architecture")
    parser.add_argument("--host", default="10.10.10.142", help="TiDB host address")
    parser.add_argument("--port", type=int, default=4000, help="TiDB port (default: 4000)")
    parser.add_argument("--db", default="memory_system", help="Database name")
    parser.add_argument("--password", default="", help="TiDB password")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🧪 Memory-TiDB8 Multi-Agent Architecture Test Suite v0.1.2")
    print("=" * 60)
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Target: {args.host}:{args.port}/{args.db}")
    print("-" * 60)
    
    test_results = []
    
    # Test 1: Database Connectivity
    print("\n[TEST 1] Database Connectivity Check...")
    try:
        import pymysql
        conn = pymysql.connect(
            host=args.host, port=args.port, user='root', 
            password=args.password or 'tidb#123',
            database=args.db, cursorclass=pymysql.cursors.DictCursor
        )
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()[0]
        
        print(f"  ✅ Connected successfully!")
        print(f"     TiDB Version: {version}")
        test_results.append(("Database Connectivity", "PASS"))
    except Exception as e:
        error_details = str(e)
        if hasattr(e, 'errno') and e.errno:
            error_details += f" (错误码:{e.errno})"
        print(f"  ❌ Connection failed: {error_details}")
        print("  💡 Solution: Ensure TiDB is running and accessible")
        test_results.append(("Database Connectivity", "FAIL"))
        
        # Don't continue if no connection - but still run module tests
        if not _continue_without_db():
            return
    
    # Test 2: Multi-Agent Schema Tables Existence
    print("\n[TEST 2] Multi-Agent Schema Verification...")
    
    expected_tables = [
        'agent_registry', 'agent_session', 
        'collaboration_request', 'shared_context',
        'coordination_log', 'agent_cache', 'agent_metrics'
    ]
    
    if 'conn' in locals():
        cursor.execute("SHOW TABLES")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = [t for t in expected_tables if t not in existing_tables]
        
        if missing_tables:
            print(f"  ⚠️  Missing tables: {', '.join(missing_tables)}")
            print("      Run 'scripts/multi_agent_schema.sql' to create them")
            test_results.append(("Schema Verification", "WARNING"))
        else:
            print(f"  ✅ All {len(expected_tables)} Multi-Agent tables present!")
            test_results.append(("Schema Verification", "PASS"))
    
    # Test 3: Python API Import Check
    print("\n[TEST 3] Python API Module Import...")
    try:
        from scripts.multi_agent_api import (
            AgentRegistryAPI, SessionAPI, CollaborationAPI,
            SharedContextAPI, MonitoringAPI,
            AgentConfig, AgentRole, SessionState, CollaborationRequest
        )
        print("  ✅ All Multi-Agent API modules imported successfully!")
        test_results.append(("Python API Import", "PASS"))
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        print("      Ensure you're running from the skill root directory")
        test_results.append(("Python API Import", "FAIL"))
    
    # Test 4: Agent Registration (if connected)
    if 'conn' in locals():
        print("\n[TEST 4] Agent Registration Test...")
        try:
            from scripts.multi_agent_api import AgentRegistryAPI, AgentConfig, AgentRole
            
            registry = AgentRegistryAPI()
            
            # Try to register a test agent (will fail gracefully if not connected)
            test_config = AgentConfig(
                agent_id="test-agent-01",
                name="Test Agent",
                role=AgentRole.WORKER,
                description="Automated test agent"
            )
            
            result = registry.register_agent(test_config)
            print(f"  ✅ Agent registration successful!")
            test_results.append(("Agent Registration", "PASS"))
        except Exception as e:
            if "Can't connect" in str(e):
                print("  ⚠️  Cannot register agent - TiDB not accessible")
                test_results.append(("Agent Registration", "SKIP (connection)"))
            else:
                print(f"  ❌ Registration failed: {e}")
                test_results.append(("Agent Registration", "FAIL"))
    
    # Test 5: Session Management (if connected)
    if 'conn' in locals():
        print("\n[TEST 5] Session Management Test...")
        try:
            from scripts.multi_agent_api import SessionAPI, SessionState
            
            session_api = SessionAPI()
            
            task_context = {"test": "session creation"}
            session_api.create_session("test-session-01", "test-agent-01", task_context)
            print(f"  ✅ Session created successfully!")
            test_results.append(("Session Management", "PASS"))
        except Exception as e:
            if "Can't connect" in str(e):
                print("  ⚠️  Cannot create session - TiDB not accessible")
                test_results.append(("Session Management", "SKIP (connection)"))
            else:
                print(f"  ❌ Session creation failed: {e}")
                test_results.append(("Session Management", "FAIL"))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, status in test_results if status == "PASS")
    failed = sum(1 for _, status in test_results if status == "FAIL")
    warnings = sum(1 for _, status in test_results if status == "WARNING")
    skipped = sum(1 for _, status in test_results if "SKIP" in str(status))
    
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  ⚠️  Warnings: {warnings}")
    print(f"  📝 Skipped: {skipped}")
    print()
    
    for test_name, status in test_results:
        icon = {"PASS": "✅", "FAIL": "❌", "WARNING": "⚠️", "SKIP (connection)": "📝"}[status]
        print(f"  {icon} {test_name}: {status}")
    
    print()
    if failed == 0 and skipped == 0:
        print("🎉 All tests passed! Multi-Agent architecture is ready for production.")
    elif failed > 0:
        print("⚠️  Some tests failed. Please review the errors above.")
    else:
        print("ℹ️  Tests were skipped due to TiDB unavailability. Run when TiDB is online.")


if __name__ == "__main__":
    main()
