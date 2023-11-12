"""Run with: ``invoke <task> [task ...]``"""

import os

from invoke import task

os.environ['PYTHONPATH'] = 'src:test:' + os.environ.get('PYTHONPATH', '')


@task
def test(c):
    """Run tests with coverage."""
    c.run('coverage run '
          '--branch '
          '--source=src '
          '-m unittest discover voicebox_test')


@task
def cov(c):
    """Generate coverage report."""
    c.run('coverage report')
