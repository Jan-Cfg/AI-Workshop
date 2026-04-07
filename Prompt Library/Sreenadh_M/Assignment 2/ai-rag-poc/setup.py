from setuptools import setup, find_packages

setup(
    name='ai-rag-poc',
    version='0.1.0',
    author='Your Name',
    author_email='your.email@example.com',
    description='A project implementing a retrieval-augmented generation (RAG) pipeline with Ollama and a vector store.',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'requests',  # For making HTTP requests to the Ollama model
        'psycopg2-binary',  # PostgreSQL database adapter
        'pinecone-client',  # Pinecone vector database client
        'python-dotenv',  # For loading environment variables from .env files
        'numpy',  # For numerical operations
        'scikit-learn',  # For any machine learning utilities
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)