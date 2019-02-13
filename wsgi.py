from app import create_app

app = create_app()


@app.cli.command()
def test():
    """Run the unit tests with 'flask test'"""
    import unittest

    tests = unittest.TestLoader().discover("tests")
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':
    app.run()
