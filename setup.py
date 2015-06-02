from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name = 'pntools',
      version = '0.3.0',
      description = 'Petri net and labelled partial order tools',
      long_description = readme(),
      classifiers = [
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3',
      ],
      keywords = 'Petri net labelled partial order pnml lpo',
      url = 'https://github.com/irgangla/pntools',
      author = 'Thomas Irgang',
      author_email = 'pntools@irgang-la.com',
      license = 'MIT',
      packages = ['pntools'],
      include_package_data = True,
      zip_safe = False)


