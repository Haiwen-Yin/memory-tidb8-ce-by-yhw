# vector_similarity.py — TiDB Vector Similarity Calculator
# Version: v0.1.0
# Author: Haiwen Yin (胖头鱼 🐟 / yhw)
# License: Apache 2.0

"""
Vector similarity calculation utilities for AI Agent memory retrieval.
Supports cosine similarity, Euclidean distance, and TiDB binary vector conversion.
"""

import numpy as np
import struct
from typing import List, Tuple, Optional


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculate cosine similarity between two vectors.
    
    Args:
        vec_a: First embedding vector
        vec_b: Second embedding vector
        
    Returns:
        Cosine similarity score (-1 to 1, higher = more similar)
    """
    if len(vec_a) != len(vec_b):
        raise ValueError(f"Vector dimensions mismatch: {len(vec_a)} vs {len(vec_b)}")
    
    a_array = np.array(vec_a, dtype=np.float32)
    b_array = np.array(vec_b, dtype=np.float32)
    
    dot_product = np.dot(a_array, b_array)
    norm_a = np.linalg.norm(a_array)
    norm_b = np.linalg.norm(b_array)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    similarity = dot_product / (norm_a * norm_b)
    return float(similarity)


def euclidean_distance(vec_a: List[float], vec_b: List[float]) -> float:
    """Calculate Euclidean distance between two vectors.
    
    Args:
        vec_a: First vector
        vec_b: Second vector
        
    Returns:
        Euclidean distance (lower = more similar)
    """
    a_array = np.array(vec_a, dtype=np.float32)
    b_array = np.array(vec_b, dtype=np.float32)
    
    return float(np.linalg.norm(a_array - b_array))


def binary_to_vector(binary_data: bytes, dim: int = 1024) -> List[float]:
    """Convert TiDB VARBINARY embedding to Python list of floats.
    
    Args:
        binary_data: Raw bytes from TiDB (float32 format)
        dim: Expected vector dimension
        
    Returns:
        List of float values
    """
    if len(binary_data) != dim * 4:  # Float32 = 4 bytes
        raise ValueError(f"Binary size mismatch: expected {dim*4} bytes, got {len(binary_data)}")
    
    return list(struct.unpack(f'{dim}f', binary_data))


def vector_to_binary(vector: List[float]) -> bytes:
    """Convert Python float list to TiDB VARBINARY format.
    
    Args:
        vector: List of float values
        
    Returns:
        Bytes in float32 format (big-endian)
    """
    return struct.pack(f'>{len(vector)}f', *vector)


def find_similar_nodes(query_vector: List[float], limit: int = 10, 
                       threshold: Optional[float] = None):
    """Find similar nodes using application-layer calculation.
    
    NOTE: This requires connecting to TiDB and fetching all embeddings.
    For production use with large datasets, consider TiFlash columnar acceleration.
    
    Args:
        query_vector: Query embedding vector
        limit: Maximum number of results
        threshold: Minimum similarity score filter
        
    Returns:
        List of tuples (node_id, content, similarity_score)
    """
    from schema_loader import SchemaLoader
    
    conn = SchemaLoader().connect()
    
    try:
        cursor = conn.cursor()
        
        # Query all memory nodes with embeddings (TiFlash accelerates this!)
        cursor.execute("""
            SELECT node_id, content, embedding 
            FROM memory_nodes 
            WHERE node_type = 'memory' AND embedding IS NOT NULL
        """)
        
        results = []
        for row in cursor.fetchall():
            node_id, content, embedding_bytes = row
            
            # Convert bytes to numpy array (TiDB stores as varbinary)
            dim = len(embedding_bytes) // 4  # Float32 = 4 bytes
            values = list(struct.unpack(f'{dim}f', embedding_bytes))
            
            similarity = cosine_similarity(query_vector, values)
            
            if threshold is None or similarity >= threshold:
                results.append((node_id, content, similarity))
        
        cursor.close()
        
        # Sort by similarity descending and return top N
        sorted_results = sorted(results, key=lambda x: x[2], reverse=True)[:limit]
        
        return sorted_results
        
    finally:
        conn.close()


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Vector similarity calculator')
    parser.add_argument('--dim', type=int, default=1024, help='Vector dimension')
    
    args = parser.parse_args()
    
    # Generate sample vectors for demonstration
    np.random.seed(42)
    vec_a = list(np.random.randn(args.dim))
    vec_b = [v * 1.1 + np.random.randn() * 0.1 for v in vec_a]  # Slightly modified
    
    sim = cosine_similarity(vec_a, vec_b)
    dist = euclidean_distance(vec_a, vec_b)
    
    print(f"Sample Vector Similarity Test (dim={args.dim}):")
    print(f"  Cosine Similarity: {sim:.6f}")
    print(f"  Euclidean Distance: {dist:.6f}")
