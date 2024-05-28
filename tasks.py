"""Run with: ``invoke <task> [task ...]``"""

from invoke import task


@task
def test(c):
    """Run tests with coverage."""
    c.run('coverage run --branch --source=src -m pytest tests/unit')


@task
def integration(c):
    """Run integration tests."""
    c.run('pytest tests/integration')


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

    c.run('python -m twine check dist/*')

    repo = 'testpypi' if test else 'pypi'
    config = '.pypirc-test' if test else '.pypirc'
    c.run(f'python -m twine upload -r {repo} --config-file {config} dist/*')


@task
def make_docs(c):
    """Generate the documentation files."""

    c.run('sphinx-apidoc -f --maxdepth 1 -o docs src/voicebox')
    c.run('rm docs/modules.rst')
    c.run('cd docs && make html')
