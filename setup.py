from setuptools import setup, find_packages

setup(
    name='invest_guard',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'guard = src.main:run'
        ]
    },
    install_requires=[
        'rich',
        'tabulate',
        'yfinance',
        'pandas',
        'numpy',
        'tqdm',
    ],
    author='Phoenix Interface',
    author_email='info@phoenixui.cloud',
    description='Invest Guard is a command-line interface (CLI) tool for fetching and analyzing financial data from various sources. With Invest Guard, you can easily retrieve stock prices, market trends, and other relevant financial information directly from your terminal.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Work-With-Phoenix/invest-guard',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        
    ],
)
