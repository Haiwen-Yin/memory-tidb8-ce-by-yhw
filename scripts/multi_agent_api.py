#!/usr/bin/env python3
"""
Multi-Agent Architecture Python API
Part of Memory-TiDB8 CE v0.1.2 (Multi-Agent Edition)
Author: 胖头鱼 🐟
License: Apache-2.0

Provides high-level APIs for multi-agent system operations including:
- Agent registration and discovery
- Session management
- Task delegation and collaboration
- Shared state access
- Performance monitoring
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


# =============================================
# DATA CLASSES AND ENUMS
# =============================================

class AgentRole(Enum):
    """Agent role classification"""
    COORDINATOR = "coordinator"  # Orchestrates tasks across agents
    SPECIALIST = "specialist"   # Expert in specific domain
    WORKER = "worker"           # Executes assigned tasks
    EVALUATOR = "evaluator"     # Validates and scores outputs


class AgentStatus(Enum):
    """Agent operational status"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PAUSED = "paused"
    DECOMMISSIONED = "decommissioned"


class SessionState(Enum):
    """Session lifecycle state"""
    INITIALIZED = "initialized"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentConfig:
    """Configuration for a registered agent"""
    agent_id: str
    name: str
    role: AgentRole
    description: Optional[str] = None
    model_config: Optional[Dict[str, Any]] = None
    capabilities: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        config = {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "description": self.description,
            "model_config": json.loads(json.dumps(self.model_config)) if self.model_config else None,
            "capabilities": self.capabilities,
        }
        return config


@dataclass 
class CollaborationRequest:
    """Multi-agent collaboration request"""
    request_id: str
    initiator_agent_id: str
    target_agents: List[str]
    task_description: str
    priority: int = 5
    result_callback: Optional[Callable] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "initiator_agent_id": self.initiator_agent_id,
            "target_agents": self.target_agents,
            "task_description": self.task_description,
            "priority": self.priority,
        }


# =============================================
# DATABASE CONNECTION MANAGEMENT
# =============================================

class ConnectionManager:
    """Manages database connections for TiDB"""
    
    _connection_pool = {}
    
    @classmethod
    def get_connection(cls, host='10.10.10.142', port=4000, user='root', password='', database='memory'):
        """Get or create a database connection"""
        pool_key = f"{host}:{port}"
        
        if pool_key not in cls._connection_pool:
            try:
                import pymysql
                conn = pymysql.connect(
                    host=host, port=port, user=user, password=password,
                    database=database, cursorclass=pymysql.cursors.DictCursor
                )
                cls._connection_pool[pool_key] = conn
                logger.info(f"Connected to TiDB at {host}:{port}")
            except Exception as e:
                logger.error(f"Failed to connect to TiDB: {e}")
                raise
        
        return cls._connection_pool[pool_key]


# =============================================
# AGENT REGISTRY API
# =============================================

class AgentRegistryAPI:
    """API for agent registration and management"""
    
    def __init__(self, connection_manager=None):
        self.conn_mgr = connection_manager or ConnectionManager
    
    def register_agent(self, config: AgentConfig) -> bool:
        """Register a new AI agent in the system"""
        conn = self.conn_mgr.get_connection()
        
        sql = """INSERT INTO agent_registry 
        (agent_id, agent_name, description, model_config, role, capabilities, status, metadata)
        VALUES (%s, %s, %s, %s, %s, %s, 'active', %s)
        ON DUPLICATE KEY UPDATE updated_at = CURRENT_TIMESTAMP"""
        
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (
                config.agent_id, config.name, config.description or "",
                json.dumps(config.model_config), config.role.value,
                json.dumps(config.capabilities) if config.capabilities else None,
                "{}"  # Empty metadata
            ))
            conn.commit()
            logger.info(f"Agent registered: {config.name} ({config.agent_id})")
            return True
        except Exception as e:
            logger.error(f"Failed to register agent: {e}")
            raise
    
    def get_agent(self, agent_id: str) -> Optional[Dict]:
        """Retrieve agent configuration by ID"""
        conn = self.conn_mgr.get_connection()
        
        sql = "SELECT * FROM agent_registry WHERE agent_id = %s"
        cursor = conn.cursor()
        cursor.execute(sql, (agent_id,))
        
        result = cursor.fetchone()
        if result:
            # Convert JSON fields from strings to objects
            for field in ['model_config', 'capabilities']:
                if isinstance(result.get(field), str):
                    try:
                        result[field] = json.loads(result[field])
                    except:
                        pass
        return result
    
    def list_agents(self, role: Optional[AgentRole] = None) -> List[Dict]:
        """List all registered agents with optional filter by role"""
        conn = self.conn_mgr.get_connection()
        
        sql = "SELECT * FROM agent_registry WHERE status = 'active'"
        params = []
        
        if role:
            sql += " AND role = %s"
            params.append(role.value)
        
        cursor = conn.cursor()
        cursor.execute(sql, tuple(params))
        return cursor.fetchall()


# =============================================
# SESSION MANAGEMENT API  
# =============================================

class SessionAPI:
    """Manages agent execution sessions"""
    
    def __init__(self):
        pass
    
    def create_session(self, session_id: str, agent_id: str, task_context: Dict) -> bool:
        """Create a new execution session for an agent"""
        conn = ConnectionManager.get_connection()
        
        sql = """INSERT INTO agent_session 
        (session_id, agent_id, task_context, state, started_at)
        VALUES (%s, %s, %s, 'initialized', CURRENT_TIMESTAMP)"""
        
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (session_id, agent_id, json.dumps(task_context)))
            conn.commit()
            logger.info(f"Session created: {session_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    def update_session_state(self, session_id: str, new_state: SessionState):
        """Update the state of an existing session"""
        conn = ConnectionManager.get_connection()
        
        sql = "UPDATE agent_session SET state = %s WHERE session_id = %s"
        cursor = conn.cursor()
        cursor.execute(sql, (new_state.value, session_id))
        
        if new_state == SessionState.COMPLETED or new_state == SessionState.FAILED:
            sql_complete = "UPDATE agent_session SET ended_at = CURRENT_TIMESTAMP WHERE session_id = %s"
            conn.cursor().execute(sql_complete, (session_id,))
        
        conn.commit()


# =============================================
# COLLABORATION API
# =============================================

class CollaborationAPI:
    """Handles multi-agent collaboration and task delegation"""
    
    def submit_request(self, request: CollaborationRequest) -> str:
        """Submit a new collaboration request"""
        conn = ConnectionManager.get_connection()
        
        sql = """INSERT INTO collaboration_request 
        (request_id, initiator_agent_id, target_agent_ids, task_description, priority, status)
        VALUES (%s, %s, %s, %s, %s, 'pending')"""
        
        try:
            cursor = conn.cursor()
            cursor.execute(sql, (
                request.request_id,
                request.initiator_agent_id,
                json.dumps(request.target_agents),
                request.task_description,
                request.priority
            ))
            conn.commit()
            
            # Record coordination log entry
            self._log_coordination(
                request.request_id,
                request.initiator_agent_id,
                "submit",
                {"task": request.task_description}
            )
            
            return request.request_id
        except Exception as e:
            logger.error(f"Failed to submit collaboration request: {e}")
            raise
    
    def assign_request(self, request_id: str, agent_id: str):
        """Assign a collaboration request to a specific agent"""
        conn = ConnectionManager.get_connection()
        
        sql_update = "UPDATE collaboration_request SET status = 'assigned' WHERE request_id = %s"
        cursor = conn.cursor()
        cursor.execute(sql_update, (request_id,))
        conn.commit()
        
        self._log_coordination(request_id, agent_id, "assign", {"status": "assigned"})
    
    def _log_coordination(self, request_id: str, agent_id: str, action_type: str, payload: Dict):
        """Record a coordination log entry"""
        conn = ConnectionManager.get_connection()
        
        sql = """INSERT INTO coordination_log 
        (request_id, agent_id, action_type, payload) VALUES (%s, %s, %s, %s)"""
        
        cursor = conn.cursor()
        cursor.execute(sql, (request_id, agent_id, action_type, json.dumps(payload)))
        conn.commit()


# =============================================
# SHARED STATE API
# =============================================

class SharedContextAPI:
    """Manages shared context between agents"""
    
    def set_context(self, key: str, value: Any, ttl_seconds: int = 0):
        """Store shared context for other agents to access"""
        conn = ConnectionManager.get_connection()
        
        sql = """INSERT INTO shared_context (context_key, context_value, ttl_seconds)
        VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE context_value = %s, accessed_at = CURRENT_TIMESTAMP"""
        
        cursor = conn.cursor()
        cursor.execute(sql, (key, json.dumps(value), ttl_seconds, json.dumps(value)))
        conn.commit()
    
    def get_context(self, key: str) -> Optional[Any]:
        """Retrieve shared context value"""
        conn = ConnectionManager.get_connection()
        
        sql = "SELECT * FROM shared_context WHERE context_key = %s"
        cursor = conn.cursor()
        cursor.execute(sql, (key,))
        
        result = cursor.fetchone()
        if result and isinstance(result['context_value'], str):
            return json.loads(result['context_value'])
        return result


# =============================================
# MONITORING API
# =============================================

class MonitoringAPI:
    """Provides system monitoring and metrics"""
    
    def record_metric(self, agent_id: str, metric_name: str, value: float):
        """Record a performance metric for an agent"""
        conn = ConnectionManager.get_connection()
        
        sql = "INSERT INTO agent_metrics (agent_id, metric_name, metric_value) VALUES (%s, %s, %s)"
        cursor = conn.cursor()
        cursor.execute(sql, (agent_id, metric_name, value))
        conn.commit()
    
    def get_system_health(self) -> Dict:
        """Get current system health status"""
        conn = ConnectionManager.get_connection()
        
        sql_active_agents = "SELECT COUNT(*) as count FROM agent_registry WHERE status = 'active'"
        cursor = conn.cursor()
        cursor.execute(sql_active_agents)
        active_count = cursor.fetchone()['count']
        
        return {
            "timestamp": datetime.now().isoformat(),
            "active_agents": active_count,
            "status": "healthy" if active_count > 0 else "warning",
        }


# =============================================
# MAIN ENTRY POINT
# =============================================

def main():
    """Demonstrate multi-agent API usage"""
    logging.basicConfig(level=logging.INFO)
    
    print("🤖 Memory-TiDB8 Multi-Agent Architecture Demo")
    print("=" * 50)
    
    # Initialize APIs
    registry = AgentRegistryAPI()
    session_api = SessionAPI()
    collaboration_api = CollaborationAPI()
    monitoring_api = MonitoringAPI()
    
    try:
        # Register agents
        coordinator = AgentConfig(
            agent_id="coordinator-01",
            name="Task Orchestrator",
            role=AgentRole.COORDINATOR,
            description="Main task coordination agent"
        )
        registry.register_agent(coordinator)
        
        specialist = AgentConfig(
            agent_id="specialist-db-01", 
            name="Database Specialist",
            role=AgentRole.SPECIALIST,
            capabilities=["schema_analysis", "query_optimization"]
        )
        registry.register_agent(specialist)
        
        print("\n✅ Agents registered successfully")
        
        # Create session
        task_context = {"objective": "Optimize database schema"}
        session_api.create_session("session-001", coordinator.agent_id, task_context)
        
        print("✅ Session created")
        
        # Submit collaboration request
        request = CollaborationRequest(
            request_id="collab-001",
            initiator_agent_id=coordinator.agent_id,
            target_agents=[specialist.agent_id],
            task_description="Analyze and optimize database schema for performance"
        )
        collaboration_api.submit_request(request)
        
        print("✅ Collaboration request submitted")
        
        # Check system health
        health = monitoring_api.get_system_health()
        print(f"\n📊 System Health: {health}")
        
    except Exception as e:
        logger.error(f"Demo failed: {e}")
        raise


if __name__ == "__main__":
    main()
