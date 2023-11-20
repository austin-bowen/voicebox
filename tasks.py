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
def clean(c, cov: bool = False):
    """Remove auto-generated files."""

    patterns = [
        'build/',
        'dist/',
        'src/voicebox_tts.egg-info/',
    ]

    if cov:
        patterns.append('.coverage')

    for pattern in patterns:
        c.run(f'rm -r {pattern}', echo=True, warn=True)


@task(pre=[clean])
def build(c):
    """Build distribution files."""
    c.run('python -m build')


@task
def publish(c, test: bool = True):
    """Upload the distribution files to PyPI."""
    repo = 'testpypi' if test else 'pypi'
    c.run(f'python -m twine upload -u __token__ -r {repo} dist/*')
