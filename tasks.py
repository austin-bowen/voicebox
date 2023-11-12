from invoke import task


@task
def test(c):
    """Run tests with coverage."""
    c.run('coverage run -m unittest discover voicebox_test')


@task
def cov(c):
    """Generate coverage report."""
    c.run('coverage report --omit=test/*')
