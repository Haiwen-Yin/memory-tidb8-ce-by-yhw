# task_plan_api.py — TiDB Task Plan Management API
# Version: v0.1.0
# Author: Haiwen Yin (胖头鱼 🐟 / yhw)
# License: Apache 2.0

"""
High-level Python API for managing AI Agent task plans on TiDB.
Supports creation, resumption, completion tracking, and historical search.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional


class TaskPlanAPI:
    """Manage task plans in TiDB memory system."""
    
    def __init__(self, host='127.0.0.1', port=4000, user='root@memcluster', 
                 password='', database='memory_cluster'):
        self.host = os.environ.get('TIDB_HOST', host)
        self.port = int(os.environ.get('TIDB_PORT', port))
        self.user = os.environ.get('TIDB_USER', user)
        self.password = os.environ.get('TIDB_PASS', password)
        self.database = os.environ.get('TIDB_DATABASE', database)
        
    def connect(self):
        """Establish connection to TiDB tenant database."""
        import pymysql
        return pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    
    def create_task_plan(self, plan_name: str, goal: str, 
                        description: Optional[str] = None,
                        plan_type: str = 'task') -> int:
        """Create a new task plan.
        
        Args:
            plan_name: Unique name for the task
            goal: Task objective description
            description: Detailed description (optional)
            plan_type: Type identifier (default: 'task')
            
        Returns:
            New plan_id
        """
        conn = self.connect()
        try:
            cursor = conn.cursor()
            
            # Insert new task plan
            cursor.execute("""
                INSERT INTO task_plans (plan_name, plan_type, description, goal, status)
                VALUES (%s, %s, %s, %s, 'PENDING')
            """, (plan_name, plan_type, description or '', goal))
            
            conn.commit()
            
            # Return the generated ID
            return cursor.lastrowid
            
        finally:
            conn.close()
    
    def resume_task(self, plan_id: int) -> Dict:
        """Resume an existing task from its latest context snapshot.
        
        Args:
            plan_id: Task plan identifier to resume
            
        Returns:
            Dictionary containing task status and next steps info
        """
        conn = self.connect()
        try:
            cursor = conn.cursor()
            
            # Get current plan status
            cursor.execute("SELECT * FROM task_plans WHERE plan_id = %s", (plan_id,))
            plan = cursor.fetchone()
            
            if not plan or plan['status'] in ['SUCCESS', 'CANCELLED']:
                return {'success': False, 'error': f'Plan {plan_id} cannot be resumed'}
            
            # Get latest context snapshot
            cursor.execute("""
                SELECT * FROM task_context_snapshots 
                WHERE plan_id = %s ORDER BY timestamp DESC LIMIT 1
            """, (plan_id,))
            
            snapshot = cursor.fetchone()
            
            if not snapshot:
                return {'success': False, 'error': f'No context snapshot found for plan {plan_id}'}
            
            # Update status to RUNNING
            cursor.execute("""
                UPDATE task_plans SET status = 'RUNNING', updated_at = NOW() 
                WHERE plan_id = %s
            """, (plan_id,))
            conn.commit()
            
            return {
                'success': True,
                'plan_id': plan_id,
                'status': 'RUNNING',
                'snapshot_timestamp': snapshot['timestamp'].isoformat(),
                'next_steps': snapshot['context_snapshot']  # Simplified extraction
            }
            
        finally:
            conn.close()
    
    def search_completed_tasks(self, filters: Optional[Dict] = None) -> List:
        """Search for completed tasks with optional filtering.
        
        Args:
            filters: Dictionary of filter conditions (status, type, date range)
                    
        Returns:
            List of matching task plans
        """
        if not filters:
            filters = {'status': 'SUCCESS'}
        
        # Build query dynamically
        where_clauses = []
        params = []
        
        for key, value in filters.items():
            if isinstance(value, str):
                where_clauses.append(f"{key} = %s")
                params.append(value)
            elif isinstance(value, list):
                placeholders = ','.join(['%s'] * len(value))
                where_clauses.append(f"{key} IN ({placeholders})")
                params.extend(value)
        
        if not where_clauses:
            return []
        
        query = f"SELECT * FROM task_plans WHERE {' AND '.join(where_clauses)} ORDER BY created_at DESC LIMIT 100"
        
        conn = self.connect()
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            return [dict(row) for row in results]
            
        finally:
            conn.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Task plan management API')
    parser.add_argument('--action', choices=['create', 'resume', 'search'], required=True)
    parser.add_argument('--plan-id', type=int, help='Plan ID for resume/search')
    
    args = parser.parse_args()
    
    api = TaskPlanAPI()
    
    if args.action == 'create':
        plan_id = api.create_task_plan(
            plan_name="demo_task",
            goal="Demonstrate task creation functionality",
            description="Sample task for testing purposes"
        )
        print(f"Created task plan with ID: {plan_id}")
        
    elif args.action == 'resume':
        if not args.plan_id:
            print("Error: --plan-id required for resume")
            exit(1)
        
        result = api.resume_task(args.plan_id)
        print(f"Resume result: {result}")
        
    elif args.action == 'search':
        results = api.search_completed_tasks({'status': 'SUCCESS'})
        print(f"Found {len(results)} completed tasks")
