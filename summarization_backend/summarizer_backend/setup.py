from setuptools import setup, find_packages

setup(
    name="summarizer",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'Django==4.2.7',
        'djangorestframework==3.14.0',
        'django-cors-headers==4.3.1',
        'python-dotenv==1.0.0',
        'Pillow==12.0.0',
    ],
)
