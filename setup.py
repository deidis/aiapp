from setuptools import setup, find_packages

setup(
    name="aiapp",
    version="1.1",
    packages=find_packages(),
    install_requires=[
        'python-decouple',
        'openai',
        'IPython'
    ],
    author="Evaldas Taroza",
    author_email="evaldas@dialexity.com",
    description="A simple way to interact with OpenAI API",
    keywords="openai api gpt3 gpt-3 gpt4 gpt-4",
)
