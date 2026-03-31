"""
Benchmark dataset definitions
"""

from typing import List, Dict

BENCHMARK_DATASETS = {
    "simple_code": [
        "Write a Python function for fibonacci",
        "Create a sorting algorithm",
        "Make a class for linked lists",
    ],
    
    "verbose_code": [
        "I was wondering if you could please help me write a Python function that calculates fibonacci numbers. It would be great if you could include comments too!",
        "Could you kindly write me a sorting algorithm? Please make it efficient and add documentation.",
        "Would you mind helping me create a class structure for a binary tree? It would be really helpful if you included all the main operations.",
    ],
    
    "debugging": [
        "Fix this bug: def add(a,b) return a+b",
        "Debug this code: if x = 5: print('five')",
        "What's wrong with this? for i in range(10) print(i)",
    ],
    
    "explanations": [
        "Explain decorators in Python",
        "What is async/await?",
        "How do generators work?",
    ],
    
    "complex": [
        "Build a complete REST API with authentication, rate limiting, and error handling",
        "Create a machine learning pipeline with data preprocessing, model training, and evaluation",
        "Design a database schema for a multi-tenant SaaS application",
    ]
}

def get_benchmark_prompts() -> List[Dict]:
    """Get all benchmark prompts"""
    prompts = []
    for category, texts in BENCHMARK_DATASETS.items():
        for text in texts:
            prompts.append({
                "category": category,
                "text": text,
                "tokens": None,  # Will be calculated
            })
    return prompts
