import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
    name='yaml2workflow',
    version='0.1',
    license='MIT',
    author="Isaac Chung",
    author_email='chungisaac1217@gmail.com',
    description="Manage and create Clarifai workflows with yaml files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages('src'),
    url='https://github.com/isaac-chung/yaml2workflow',
    python_requires='>=3.7',
    install_requires=[
          'clarifai-grpc>=8.11.0',
      ],

)