# Embedding API Integration Notes

**Author**: Haiwen Yin (胖头鱼 🐟 / yhw)  
**Last Updated**: 2026-05-11 v1.0.0

---

## 🌐 BGE-M3 Embedding API Configuration

### API Endpoint

- **URL**: `http://10.10.10.1:12345/v1/embeddings`
- **Model**: `text-embedding-bge-m3`
- **Vector Dimensions**: 1024

### Request Format

```json
{
  "model": "text-embedding-bge-m3",
  "input": "Text to generate embedding for"
}
```

### Response Format

```json
{
  "data": [
    {
      "embedding": [0.1234, 0.5678, ..., 0.9012],  // 1024 dimensions
      "index": 0
    }
  ],
  "model": "text-embedding-bge-m3",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  }
}
```

---

## 🔧 Python Integration

### Using requests Library

```python
import requests
import json

embedding_api = "http://10.10.10.1:12345/v1/embeddings"
embedding_model = "text-embedding-bge-m3"

def generate_embedding(text: str) -> List[float]:
    """Generate embedding vector from text"""
    try:
        response = requests.post(
            embedding_api,
            json={"model": embedding_model, "input": text},
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        
        if 'data' in data and len(data['data']) > 0:
            return data['data'][0]['embedding']
        return []
    except Exception as e:
        print(f"Warning: Failed to generate embedding: {e}")
        return []
```

### Usage in Knowledge Base API

```python
# Generate embedding from concept name + description
embedding_text = concept_name + ' ' + (description or '')
embedding_vector = generate_embedding(embedding_text)

# Store as JSON in TEXT field
embedding_str = json.dumps(embedding_vector) if embedding_vector else None

# Store in database
cursor.execute("""
    INSERT INTO knowledge_concepts (
        CONCEPT_NAME, CONCEPT_TYPE, EMBEDDING
    ) VALUES (%s, %s, %s)
""", (concept_name, concept_type, embedding_str))
```

---

## ⚠️ Common Pitfalls

### 1. Embedding API Unavailable

**Problem**: BGE-M3 API service not running or unreachable

**Symptoms**:
```
Warning: Failed to generate embedding: HTTPConnectionPool
```

**Impact**:
- Semantic search returns empty list
- Text search still works (doesn't depend on embeddings)

**Solution**: Handle exception gracefully
```python
try:
    embedding = generate_embedding(text)
except Exception as e:
    embedding = None  # Allow concept creation without embedding
```

### 2. Empty Input Text

**Problem**: Empty string or None passed to embedding API

**Symptoms**: API returns error or empty array

**Solution**: Validate input before calling API
```python
if not text or not text.strip():
    return []

embedding_vector = generate_embedding(text.strip())
```

### 3. Timeout Issues

**Problem**: Large text causes timeout or slow response

**Symptoms**: `TimeoutError: Request timed out after 30 seconds`

**Solution**: 
- Increase timeout (from 30 to 60 seconds)
- Truncate text to reasonable length (< 1000 characters)

```python
response = requests.post(
    embedding_api,
    json={"model": embedding_model, "input": text[:1000]},
    timeout=60  # Increased timeout
)
```

### 4. JSON Serialization Errors

**Problem**: Embedding array not properly serialized for database storage

**Symptoms**: `json.dumps()` fails or produces invalid JSON

**Solution**: Ensure embedding is list of floats, not numpy array
```python
import numpy as np

# ✅ CORRECT: Convert numpy array to list
if isinstance(embedding, np.ndarray):
    embedding = embedding.tolist()

embedding_str = json.dumps(embedding)

# ❌ WRONG: Direct serialization of array
embedding_str = json.dumps(embedding)  # May fail for numpy arrays
```

---

## 📊 Vector Similarity Calculation

### Application-Layer Implementation (Current)

```python
import numpy as np

def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors"""
    query_vec = np.array(vec1, dtype=np.float64)
    doc_vec = np.array(vec2, dtype=np.float64)
    
    similarity = np.dot(query_vec, doc_vec) / (
        np.linalg.norm(query_vec) * np.linalg.norm(doc_vec)
    )
    
    return float(similarity)
```

### Usage in Semantic Search

```python
# Get all concepts with embeddings
cursor.execute("""
    SELECT CONCEPT_ID, CONCEPT_NAME, EMBEDDING
    FROM knowledge_concepts
    WHERE EMBEDDING IS NOT NULL
""")

# Calculate similarity for each concept
for row in cursor.fetchall():
    concept_id, concept_name, embedding_str = row
    embedding = json.loads(embedding_str)
    
    similarity = cosine_similarity(query_vector, embedding)
    
    if similarity >= threshold:
        results.append({
            'concept_id': concept_id,
            'concept_name': concept_name,
            'similarity': similarity
        })

# Sort by similarity descending
results.sort(key=lambda x: x['similarity'], reverse=True)
```

---

## 🚀 Future Optimization: TiDB Native vec_cosine_distance()

### Current Limitation

Application-layer semantic search has performance limitations:
- Fetches ALL concepts with embeddings from database
- Calculates similarity in Python (single-threaded)
- Not scalable for large datasets (>10k concepts)

### Planned Solution (v1.1.0)

TiDB v8.5.6 supports native vector similarity:

```sql
SELECT 
    CONCEPT_ID,
    CONCEPT_NAME,
    vec_cosine_distance(
        CAST('[0.123, 0.456, ...]' AS VECTOR(1024)),
        EMBEDDING
    ) AS distance
FROM knowledge_concepts
WHERE EMBEDDING IS NOT NULL
ORDER BY distance ASC
LIMIT 10;
```

### Benefits

1. **Database-level filtering**: Server calculates distance, returns top results
2. **Vector indexing**: H can use HNSW/IVF indexes for acceleration
3. **Scalability**: Handles millions of concepts efficiently
4. **Network efficiency**: Only transfers top K results, not all vectors

---

## 📦 Test Results (v1.0.0)

| Test | Status | Notes |
|-------|--------|-------|
| Embedding Generation | ✅ Pass | BGE-M3 API working |
| Text + Description Combined | ✅ Pass | Input concatenation working |
| JSON Serialization | ✅ Pass | Vector storage in TEXT field working |
| Similarity Calculation | ✅ Pass | Cosine similarity correct |
| Semantic Search (2 results) | ✅ Pass | Found 2 similar concepts |
| Graceful Degradation | ✅ Pass | Text search works when API unavailable |

---

**Last Updated**: 2026-05-11 v1.0.0  
**Author**: Haiwen Yin (胖头鱼 🐟 / yhw)
