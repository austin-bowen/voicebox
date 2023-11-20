"""Run with: ``invoke <task> [task ...]``"""

from invoke import task


@task
def test(c):
    """Run tests with coverage."""
    c.run('coverage run --branch --source=src -m unittest')


@task
def cov(c):
    """Generate coverage report."""
    c.run('coverage report -m')


@task
def build(c):
    """Build distribution files."""
    c.run('rm dist/voicebox*')
    c.run('python -m build')


@task
def publish(c):
    """Upload the distribution files to PyPI."""
    c.run('python -m twine -r testpypi dist/*')


@task
def clean(c):
    """Remove auto-generated files."""
    c.run('rm -r .coverage build/ dist/ src/voicebox_tts.egg-info/')
