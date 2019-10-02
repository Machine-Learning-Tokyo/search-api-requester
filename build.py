from pybuilder.core import use_plugin, init

use_plugin("python.core")
#use_plugin("python.unittest")
use_plugin("python.install_dependencies")
use_plugin("python.flake8")
#use_plugin("python.coverage")
use_plugin("python.distutils")

requires_python = "==3.6.9"
name = "search-api-requester"
default_task = ["install_dependencies", "publish"]


@init
def set_properties(project):
    project.depends_on_requirements("requirements.txt")
