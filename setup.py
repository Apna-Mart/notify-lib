from setuptools import setup, find_packages


setup(
    name="notify_lib",
    version="1.1.1",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "requests>=2.31.0", "sendgrid~=6.11.0"
    ],
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
