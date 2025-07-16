from setuptools import setup, find_packages
exec(open('setup_package/__init__.py').read())
setup(
    name="Setup-Package",
    version=__version__,
    packages=find_packages(),
    author="Saad Habib",
    description="Version management for Colab notebooks",
    url="https://github.com/Mohsin-h27/Setup_Package.git",
    python_requires='>=3.6',
)
