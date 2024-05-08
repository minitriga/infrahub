from __future__ import annotations

import re
from typing import TYPE_CHECKING, Optional

from invoke.tasks import task

from .container_ops import (
    build_images,
    destroy_environment,
    migrate_database,
    pull_images,
    restart_services,
    show_service_status,
    start_services,
    stop_services,
    update_core_schema,
)
from .infra_ops import load_infrastructure_data, load_infrastructure_schema
from .shared import (
    BUILD_NAME,
    INFRAHUB_ADDRESS,
    INFRAHUB_DATABASE,
    PYTHON_VER,
    build_compose_files_cmd,
    build_dev_compose_files_cmd,
    execute_command,
    get_env_vars,
)
from .utils import ESCAPED_REPO_PATH

if TYPE_CHECKING:
    from invoke.context import Context


NAMESPACE = "DEV"


@task(optional=["database"])
def build(
    context: Context,
    service: Optional[str] = None,
    python_ver: str = PYTHON_VER,
    nocache: bool = False,
    database: str = INFRAHUB_DATABASE,
):
    """Build an image with the provided name and python version.

    Args:
        context (obj): Used to run specific commands
        python_ver (str): Define the Python version docker image to build from
        nocache (bool): Do not use cache when building the image
    """
    build_images(
        context=context, service=service, python_ver=python_ver, nocache=nocache, database=database, namespace=NAMESPACE
    )


@task(optional=["database"])
def debug(context: Context, database: str = INFRAHUB_DATABASE):
    """Start a local instance of Infrahub in debug mode."""
    with context.cd(ESCAPED_REPO_PATH):
        compose_files_cmd = build_compose_files_cmd(database=database)
        command = f"{get_env_vars(context, namespace=NAMESPACE)} docker compose {compose_files_cmd} -p {BUILD_NAME} up"
        execute_command(context=context, command=command)


@task(optional=["database"])
def deps(context: Context, database: str = INFRAHUB_DATABASE):
    """Start local instances of dependencies (Databases and Message Bus)."""
    with context.cd(ESCAPED_REPO_PATH):
        dev_compose_files_cmd = build_dev_compose_files_cmd(database=database)
        command = (
            f"{get_env_vars(context, namespace=NAMESPACE)} docker compose {dev_compose_files_cmd} -p {BUILD_NAME} up -d"
        )
        execute_command(context=context, command=command)


@task
def destroy(context: Context, database: str = INFRAHUB_DATABASE):
    """Destroy all containers and volumes."""
    destroy_environment(context=context, database=database, namespace=NAMESPACE)


@task(optional=["database"])
def infra_git_create(
    context: Context,
    database: str = INFRAHUB_DATABASE,
    name="demo-edge",
    location="/remote/infrahub-demo-edge",
):
    """Load some demo data."""

    add_repo_query = """
    mutation($name: String!, $location: String!){
    CoreRepositoryCreate(
        data: {
        name: { value: $name }
        location: { value: $location }
        }
    ) {
        ok
    }
    }
    """

    clean_query = re.sub(r"\n\s*", "", add_repo_query)

    exec_cmd = """
    curl -g \
    -X POST \
    -H "Content-Type: application/json" \
    -H "X-INFRAHUB-KEY: 06438eb2-8019-4776-878c-0941b1f1d1ec" \
    -d '{"query":"%s", "variables": {"name": "%s", "location": "%s"}}' \
    %s/graphql
    """ % (clean_query, name, location, INFRAHUB_ADDRESS)
    execute_command(context=context, command=exec_cmd, print_cmd=True)


@task(optional=["database"])
def infra_git_import(context: Context, database: str = INFRAHUB_DATABASE):
    """Load some demo data."""
    REPO_NAME = "infrahub-demo-edge"
    with context.cd(ESCAPED_REPO_PATH):
        compose_files_cmd = build_compose_files_cmd(database=database, namespace=NAMESPACE)
        base_cmd = f"{get_env_vars(context, namespace=NAMESPACE)} docker compose {compose_files_cmd} -p {BUILD_NAME}"
        execute_command(
            context=context,
            command=f"{base_cmd} run infrahub-git cp -r backend/tests/fixtures/repos/{REPO_NAME}/initial__main /remote/{REPO_NAME}",
        )
        execute_command(
            context=context,
            command=f"{base_cmd} exec --workdir /remote/{REPO_NAME} infrahub-git git init --initial-branch main",
        )
        execute_command(
            context=context,
            command=f"{base_cmd} exec --workdir /remote/{REPO_NAME} infrahub-git git add .",
        )
        execute_command(
            context=context,
            command=f"{base_cmd} exec --workdir /remote/{REPO_NAME} infrahub-git git commit -m first",
        )


@task(optional=["database"])
def load_infra_data(context: Context, database: str = INFRAHUB_DATABASE):
    """Load infrastructure demo data."""
    load_infrastructure_data(context=context, database=database, namespace=NAMESPACE)


@task(optional=["database"])
def load_infra_schema(context: Context, database: str = INFRAHUB_DATABASE):
    """Load the base schema for infrastructure."""
    load_infrastructure_schema(context=context, database=database, namespace=NAMESPACE)


@task(optional=["database"])
def pull(context: Context, database: str = INFRAHUB_DATABASE):
    """Pull external containers from registry."""
    pull_images(context=context, database=database, namespace=NAMESPACE)


@task(optional=["database"])
def restart(context: Context, database: str = INFRAHUB_DATABASE):
    """Restart Infrahub API Server and Git Agent within docker compose."""
    restart_services(context=context, database=database, namespace=NAMESPACE)


@task(optional=["database"])
def status(context: Context, database: str = INFRAHUB_DATABASE):
    """Display the status of all containers."""
    show_service_status(context=context, database=database, namespace=NAMESPACE)


@task(optional=["database"])
def start(context: Context, database: str = INFRAHUB_DATABASE):
    """Start a local instance of Infrahub within docker compose."""
    start_services(context=context, database=database, namespace=NAMESPACE)


@task(optional=["database"])
def stop(context: Context, database: str = INFRAHUB_DATABASE):
    """Stop the running instance of Infrahub."""
    stop_services(context=context, database=database, namespace=NAMESPACE)


@task(optional=["database"])
def migrate(context: Context, database: str = INFRAHUB_DATABASE):
    """Apply the latest database migrations."""
    migrate_database(context=context, database=database, namespace=NAMESPACE)
    update_core_schema(context=context, database=database, namespace=NAMESPACE, debug=True)


@task
def gen_config_env(context: Context):
    """Generate list of env vars required for configuration."""
    from pydantic_settings import BaseSettings
    from pydantic_settings.sources import EnvSettingsSource

    from infrahub.config import Settings

    # These are environment variables used outside of Pydantic settings
    env_vars = {
        "INFRAHUB_LOG_LEVEL",
        "INFRAHUB_PRODUCTION",
        "INFRAHUB_CONFIG",
        "OTEL_RESOURCE_ATTRIBUTES",
        "INFRAHUB_ADDRESS",
    }
    settings = Settings()

    def fetch_fields(subset: BaseSettings):
        env_settings = EnvSettingsSource(
            subset.__class__,
            env_prefix=subset.model_config.get("env_prefix"),
        )
        for field_name, field in subset.model_fields.items():
            field_inst = getattr(subset, field_name)
            if issubclass(field_inst.__class__, BaseSettings):
                fetch_fields(field_inst)
            else:
                for _, field_env_name, _ in env_settings._extract_field_info(field, field_name):
                    env_vars.add(field_env_name.upper())

    for subsetting in dict(settings):
        subsettings = getattr(settings, subsetting)
        fetch_fields(subsettings)

    env_vars.remove("PATH")
    for var in sorted(env_vars):
        print(f"{var}:")
