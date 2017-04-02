from setuptools import setup

tests_require = [
        'cov-core',
        'mock',
        'nose2',
    ]

setup(name='steinlib',
      version='0.1',
      description='Python bindings for Steinlib format.',
      url='http://github.com/leandron/steinlib',
      author='Leandro Nunes',
      author_email='leandron85@gmail.com',
      license='MIT',
      packages=['steinlib'],
      tests_require=tests_require,
      test_suite='nose2.collector.collector',
      zip_safe=False)
