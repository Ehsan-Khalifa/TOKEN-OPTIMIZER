from setuptools import setup, find_packages

setup(
    name="token-optimizer",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "tiktoken>=0.5.0",
        "httpx>=0.25.0",
        "pydantic>=2.0.0",
    ],
    extras_require={
        "deepl": ["deepl>=1.16.0"],
        "llmlingua": ["llmlingua>=0.2.0"],
        "openai": ["openai>=1.0.0"],
        "anthropic": ["anthropic>=0.18.0"],
        "all": [
            "deepl>=1.16.0",
            "llmlingua>=0.2.0",
            "openai>=1.0.0",
            "anthropic>=0.18.0",
        ]
    },
    python_requires=">=3.9",
)
