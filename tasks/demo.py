"""Replacement for Makefile."""
import os
from time import sleep

from invoke import Context, task

from .shared import (
    AVAILABLE_SERVICES,
    BUILD_NAME,
    COMPOSE_FILES_MEMGRAPH,
    COMPOSE_FILES_NEO4J,
    DEFAULT_FILE_NAME,
    DEV_COMPOSE_FILES_MEMGRAPH,
    DEV_COMPOSE_FILES_NEO4J,
    DEV_OVERRIDE_FILE_NAME,
    ENV_VARS,
    OVERRIDE_FILE_NAME,
    PYTHON_VER,
    SUPPORTED_DATABASES,
    VOLUME_NAMES,
    DatabaseType,
)
from .utils import REPO_BASE


def build_compose_files_cmd(database: str) -> str:
    if database not in SUPPORTED_DATABASES:
        exit(f"{database} is not a valid database ({SUPPORTED_DATABASES})")

    if database == DatabaseType.MEMGRAPH.value:
        COMPOSE_FILES = COMPOSE_FILES_MEMGRAPH
    elif database == DatabaseType.NEO4J.value:
        COMPOSE_FILES = COMPOSE_FILES_NEO4J

    if os.path.exists(OVERRIDE_FILE_NAME):
        print("!! Found an override file for docker-compose !!")
        COMPOSE_FILES.append(OVERRIDE_FILE_NAME)
    else:
        COMPOSE_FILES.append(DEFAULT_FILE_NAME)

    return f"-f {' -f '.join(COMPOSE_FILES)}"


def build_dev_compose_files_cmd(database: str) -> str:
    if database not in SUPPORTED_DATABASES:
        exit(f"{database} is not a valid database ({SUPPORTED_DATABASES})")

    if database == DatabaseType.MEMGRAPH.value:
        DEV_COMPOSE_FILES = DEV_COMPOSE_FILES_MEMGRAPH
    elif database == DatabaseType.NEO4J.value:
        DEV_COMPOSE_FILES = DEV_COMPOSE_FILES_NEO4J

    if os.path.exists(DEV_OVERRIDE_FILE_NAME):
        print("!! Found a dev override file for docker-compose !!")
        DEV_COMPOSE_FILES.append(DEV_OVERRIDE_FILE_NAME)

    return f"-f {' -f '.join(DEV_COMPOSE_FILES)}"


@task(optional=["database"])
def build(
    context, service: str = None, python_ver: str = PYTHON_VER, nocache: bool = False, database: str = "memgraph"
):  # pylint: disable=too-many-arguments
    """Build an image with the provided name and python version.

    Args:
        context (obj): Used to run specific commands
        python_ver (str): Define the Python version docker image to build from
        nocache (bool): Do not use cache when building the image
    """
    print("Building images")

    if service and service not in AVAILABLE_SERVICES:
        exit(f"{service} is not a valid service ({AVAILABLE_SERVICES})")

    with context.cd(REPO_BASE):
        compose_files_cmd = build_compose_files_cmd(database=database)
        exec_cmd = (
            f"{ENV_VARS} docker compose {compose_files_cmd} -p {BUILD_NAME} build --build-arg PYTHON_VER={python_ver}"
        )
        if nocache:
            exec_cmd += " --no-cache"

        if service:
            exec_cmd += f" {service}"

        context.run(exec_cmd, pty=True)


# ----------------------------------------------------------------------------
# Local Environment tasks
# ----------------------------------------------------------------------------
@task(optional=["database"])
def debug(context: Context, database: str = "memgraph"):
    """Start a local instance of Infrahub in debug mode."""
    with context.cd(REPO_BASE):
        compose_files_cmd = build_compose_files_cmd(database=database)
        exec_cmd = f"{ENV_VARS} docker compose {compose_files_cmd} -p {BUILD_NAME} up"
        return context.run(exec_cmd, pty=True)


@task(optional=["database"])
def start(context: Context, database: str = "memgraph"):
    """Start a local instance of Infrahub within docker compose."""
    with context.cd(REPO_BASE):
        compose_files_cmd = build_compose_files_cmd(database=database)
        exec_cmd = f"{ENV_VARS} docker compose {compose_files_cmd} -p {BUILD_NAME} up -d"
        return context.run(exec_cmd, pty=True)


@task(optional=["database"])
def restart(context: Context, database: str = "memgraph"):
    """Restart Infrahub API Server and Git Agent within docker compose."""
    with context.cd(REPO_BASE):
        compose_files_cmd = build_compose_files_cmd(database=database)
        context.run(
            f"{ENV_VARS} docker compose {compose_files_cmd} -p {BUILD_NAME} restart infrahub-server",
            pty=True,
        )
        context.run(
            f"{ENV_VARS} docker compose {compose_files_cmd} -p {BUILD_NAME} restart infrahub-git",
            pty=True,
        )
        context.run(
            f"{ENV_VARS} docker compose {compose_files_cmd} -p {BUILD_NAME} restart frontend",
        )


@task(optional=["database"])
def stop(context: Context, database: str = "memgraph"):
    """Stop the running instance of Infrahub."""
    with context.cd(REPO_BASE):
        compose_files_cmd = build_compose_files_cmd(database=database)
        exec_cmd = f"{ENV_VARS} docker compose  {compose_files_cmd} -p {BUILD_NAME} down"
        return context.run(exec_cmd, pty=True)


@task
def destroy(context: Context, database: str = "memgraph"):
    """Destroy all containers and volumes."""
    with context.cd(REPO_BASE):
        compose_files_cmd = build_compose_files_cmd(database=database)
        context.run(f"{ENV_VARS} docker compose {compose_files_cmd} -p {BUILD_NAME} down --remove-orphans", pty=True)

        for volume in VOLUME_NAMES:
            context.run(f"{ENV_VARS} docker volume rm -f {BUILD_NAME}_{volume}", pty=True)


@task(optional=["database"])
def cli_server(context: Context, database: str = "memgraph"):
    """Launch a bash shell inside the running Infrahub container."""
    with context.cd(REPO_BASE):
        compose_files_cmd = build_compose_files_cmd(database=database)
        context.run(
            f"{ENV_VARS} docker compose {compose_files_cmd} -p {BUILD_NAME} run infrahub-server bash",
            pty=True,
        )


@task(optional=["database"])
def cli_git(context: Context, database: str = "memgraph"):
    """Launch a bash shell inside the running Infrahub container."""
    with context.cd(REPO_BASE):
        compose_files_cmd = build_compose_files_cmd(database=database)
        context.run(
            f"{ENV_VARS} docker compose {compose_files_cmd} -p {BUILD_NAME} run infrahub-git bash",
            pty=True,
        )


@task(optional=["database"])
def cli_frontend(context: Context, database: str = "memgraph"):
    """Launch a bash shell inside the running Infrahub container."""
    with context.cd(REPO_BASE):
        compose_files_cmd = build_compose_files_cmd(database=database)
        context.run(
            f"{ENV_VARS} docker compose {compose_files_cmd} -p {BUILD_NAME} run frontend bash",
            pty=True,
        )


@task
def init(context: Context, database: str = "memgraph"):
    """Initialize Infrahub database before using it the first time."""
    with context.cd(REPO_BASE):
        compose_files_cmd = build_compose_files_cmd(database=database)
        context.run(
            f"{ENV_VARS} docker compose {compose_files_cmd} -p {BUILD_NAME} run infrahub-server infrahub db init",
            pty=True,
        )


@task(optional=["database"])
def status(context: Context, database: str = "memgraph"):
    """Display the status of all containers."""
    with context.cd(REPO_BASE):
        compose_files_cmd = build_compose_files_cmd(database=database)
        context.run(
            f"{ENV_VARS} docker compose {compose_files_cmd} -p {BUILD_NAME} ps",
            pty=True,
        )


@task(optional=["database"])
def load_infra_schema(context: Context, database: str = "memgraph"):
    """Load the base schema for infrastructure."""
    with context.cd(REPO_BASE):
        compose_files_cmd = build_compose_files_cmd(database=database)
        context.run(
            f"{ENV_VARS} docker compose {compose_files_cmd} -p {BUILD_NAME} run infrahub-git infrahubctl schema load models/infrastructure_base.yml",
            pty=True,
        )

        context.run(
            f"{ENV_VARS} docker compose {compose_files_cmd} -p {BUILD_NAME} restart infrahub-server",
            pty=True,
        )


@task(optional=["database"])
def load_infra_data(context: Context, database: str = "memgraph"):
    """Load some demo data."""
    with context.cd(REPO_BASE):
        compose_files_cmd = build_compose_files_cmd(database=database)
        context.run(
            f"{ENV_VARS} docker compose {compose_files_cmd} -p {BUILD_NAME} run infrahub-git infrahubctl run models/infrastructure_edge.py",
            pty=True,
        )


# ----------------------------------------------------------------------------
# Dev Environment tasks
# ----------------------------------------------------------------------------
@task(optional=["database"])
def dev_start(context: Context, database: str = "memgraph"):
    """Start a local instance of NEO4J & RabbitMQ."""
    with context.cd(REPO_BASE):
        dev_compose_files_cmd = build_dev_compose_files_cmd(database=database)
        exec_cmd = f"{ENV_VARS} docker compose {dev_compose_files_cmd} -p {BUILD_NAME} up -d"
        return context.run(exec_cmd, pty=True)


@task(optional=["database"])
def dev_stop(context: Context, database: str = "memgraph"):
    """Start a local instance of NEO4J & RabbitMQ."""
    with context.cd(REPO_BASE):
        dev_compose_files_cmd = build_dev_compose_files_cmd(database=database)
        exec_cmd = f"{ENV_VARS} docker compose  {dev_compose_files_cmd} -p {BUILD_NAME} down"
        return context.run(exec_cmd, pty=True)


@task(optional=["expected"])
def wait_healthy(context: Context, expected: int = 2):
    """Wait until containers are healthy before continuing."""
    missing_healthy = True
    while missing_healthy:
        output = context.run("docker ps --filter 'health=healthy' --format '{{ .Names}}'", hide=True)
        containers = output.stdout.splitlines()
        if len(containers) >= expected:
            missing_healthy = False
        else:
            print(f"Expected {expected} healthy containers only saw: {', '.join(containers)}")
            sleep(1)
