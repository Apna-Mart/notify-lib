from setuptools import setup, find_packages


# Read requirements from requirements.txt
def parse_requirements(filename):
    with open(filename, 'r') as f:
        return [
            line.strip()
            for line in f.readlines()
            if line.strip() and not line.startswith('#')
        ]


setup(
    name="notify_lib",
    version="1.0.0.3",
    packages=find_packages(),
    include_package_data=True,
    install_requires=parse_requirements('requirements.txt'),
    description="A helper library, which provides multiple notification support",
    license='MIT',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author="Mayank Jain",
    author_email="mayank@apnamart.in",
    url="https://github.com/Apna-Mart/notify-lib",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"])
