from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from kraken.core import Project, Property, Supplier, Task, TaskResult

from ..buildsystem import PythonBuildSystem
from ..settings import python_settings

logger = logging.getLogger(__name__)


class BuildTask(Task):
    build_system: Property[Optional[PythonBuildSystem]]
    output_directory: Property[Path]
    as_version: Property[Optional[str]] = Property.config(default=None)
    output_files: Property[list[Path]] = Property.output()

    def execute(self) -> TaskResult:
        build_system = self.build_system.get()
        if not build_system:
            logger.error("no build system configured")
            return TaskResult.FAILED
        output_directory = self.output_directory.get_or(self.project.build_directory / "python-dist")
        output_directory.mkdir(exist_ok=True, parents=True)
        self.output_files.set(build_system.build(output_directory, self.as_version.get()))
        return TaskResult.SUCCEEDED


def build(
    *,
    name: str = "pythonBuild",
    group: str | None = "build",
    as_version: str | None = None,
    project: Project | None = None,
) -> BuildTask:
    """Creates a build task for the given project.

    The build task relies on the build system configured in the Python project settings."""

    project = project or Project.current()
    task = project.do(
        name,
        BuildTask,
        default=False,
        group=group,
        build_system=Supplier.of_callable(lambda: python_settings(project).build_system),
        as_version=as_version,
    )
    return task
