from __future__ import annotations

from typing import Any

from gitlab import cli
from gitlab import exceptions as exc
from gitlab.base import RESTObject
from gitlab.mixins import (
    DeleteMixin,
    GetMixin,
    ListMixin,
    ObjectDeleteMixin,
    RetrieveMixin,
)

__all__ = [
    "GroupRegistryRepositoryManager",
    "ProjectRegistryRepository",
    "ProjectRegistryRepositoryManager",
    "ProjectRegistryTag",
    "ProjectRegistryTagManager",
    "RegistryRepository",
    "RegistryRepositoryManager",
]


class ProjectRegistryRepository(ObjectDeleteMixin, RESTObject):
    tags: ProjectRegistryTagManager


class ProjectRegistryRepositoryManager(
    DeleteMixin[ProjectRegistryRepository], ListMixin[ProjectRegistryRepository]
):
    _path = "/projects/{project_id}/registry/repositories"
    _obj_cls = ProjectRegistryRepository
    _from_parent_attrs = {"project_id": "id"}


class ProjectRegistryTag(ObjectDeleteMixin, RESTObject):
    _id_attr = "name"


class ProjectRegistryTagManager(
    DeleteMixin[ProjectRegistryTag], RetrieveMixin[ProjectRegistryTag]
):
    _obj_cls = ProjectRegistryTag
    _from_parent_attrs = {"project_id": "project_id", "repository_id": "id"}
    _path = "/projects/{project_id}/registry/repositories/{repository_id}/tags"

    @cli.register_custom_action(
        cls_names="ProjectRegistryTagManager",
        required=("name_regex_delete",),
        optional=("keep_n", "name_regex_keep", "older_than"),
    )
    @exc.on_http_error(exc.GitlabDeleteError)
    def delete_in_bulk(self, name_regex_delete: str, **kwargs: Any) -> None:
        """Delete Tag in bulk

        Args:
            name_regex_delete: The regex of the name to delete. To delete all
                tags specify .*.
            keep_n: The amount of latest tags of given name to keep.
            name_regex_keep: The regex of the name to keep. This value
                overrides any matches from name_regex.
            older_than: Tags to delete that are older than the given time,
                written in human readable form 1h, 1d, 1month.
            **kwargs: Extra options to send to the server (e.g. sudo)
        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabDeleteError: If the server cannot perform the request
        """
        valid_attrs = ["keep_n", "name_regex_keep", "older_than"]
        data = {"name_regex_delete": name_regex_delete}
        data.update({k: v for k, v in kwargs.items() if k in valid_attrs})
        self.gitlab.http_delete(self.path, query_data=data, **kwargs)


class GroupRegistryRepositoryManager(ListMixin[ProjectRegistryRepository]):
    _path = "/groups/{group_id}/registry/repositories"
    _obj_cls = ProjectRegistryRepository
    _from_parent_attrs = {"group_id": "id"}


class RegistryRepository(RESTObject):
    _repr_attr = "path"


class RegistryRepositoryManager(GetMixin[RegistryRepository]):
    _path = "/registry/repositories"
    _obj_cls = RegistryRepository
