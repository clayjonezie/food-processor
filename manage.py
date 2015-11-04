import os
from app import create_app, db, models
import sys
sys.path.append('.')

from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app('shell')
manager = Manager(app)
migrate = Migrate(app, db)

app.debug=True

def make_shell_context():
    return dict(app=app, db=db, models=models)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("db", MigrateCommand)

@manager.command
def fill():
    from app.fplib.ndb_import import import_all
    import_all()

@manager.command
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == "__main__":
    manager.run()
