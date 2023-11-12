"""Run with: ``invoke <task> [task ...]``"""

import os

from invoke import task

os.environ['PYTHONPATH'] = 'src:' + os.environ.get('PYTHONPATH', '')


@task
def test(c):
    """Run tests with coverage."""
    c.run('coverage run --branch --source=src -m unittest')


@task
def cov(c):
    """Generate coverage report."""
    c.run('coverage report -m')
