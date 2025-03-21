from typing import Any, TYPE_CHECKING

from gitlab import cli
from gitlab import exceptions as exc
from gitlab import types
from gitlab.base import RESTObject, RESTObjectList
from gitlab.client import GitlabList
from gitlab.mixins import (
    CRUDMixin,
    ObjectDeleteMixin,
    PromoteMixin,
    SaveMixin,
    UpdateMethod,
)
from gitlab.types import RequiredOptional

from .issues import GroupIssue, GroupIssueManager, ProjectIssue, ProjectIssueManager
from .merge_requests import (
    GroupMergeRequest,
    GroupMergeRequestManager,
    ProjectMergeRequest,
    ProjectMergeRequestManager,
)

__all__ = [
    "GroupMilestone",
    "GroupMilestoneManager",
    "ProjectMilestone",
    "ProjectMilestoneManager",
]


class GroupMilestone(SaveMixin, ObjectDeleteMixin, RESTObject):
    _repr_attr = "title"

    @cli.register_custom_action(cls_names="GroupMilestone")
    @exc.on_http_error(exc.GitlabListError)
    def issues(self, **kwargs: Any) -> RESTObjectList[GroupIssue]:
        """List issues related to this milestone.

        Args:
            get_all: If True, return all the items, without pagination
            per_page: Number of items to retrieve per request
            page: ID of the page to return (starts with page 1)
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabListError: If the list could not be retrieved

        Returns:
            The list of issues
        """

        path = f"{self.manager.path}/{self.encoded_id}/issues"
        data_list = self.manager.gitlab.http_list(path, iterator=True, **kwargs)
        if TYPE_CHECKING:
            assert isinstance(data_list, GitlabList)
        manager = GroupIssueManager(self.manager.gitlab, parent=self.manager._parent)
        # FIXME(gpocentek): the computed manager path is not correct
        return RESTObjectList(manager, GroupIssue, data_list)

    @cli.register_custom_action(cls_names="GroupMilestone")
    @exc.on_http_error(exc.GitlabListError)
    def merge_requests(self, **kwargs: Any) -> RESTObjectList[GroupMergeRequest]:
        """List the merge requests related to this milestone.

        Args:
            get_all: If True, return all the items, without pagination
            per_page: Number of items to retrieve per request
            page: ID of the page to return (starts with page 1)
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabListError: If the list could not be retrieved

        Returns:
            The list of merge requests
        """
        path = f"{self.manager.path}/{self.encoded_id}/merge_requests"
        data_list = self.manager.gitlab.http_list(path, iterator=True, **kwargs)
        if TYPE_CHECKING:
            assert isinstance(data_list, GitlabList)
        manager = GroupMergeRequestManager(
            self.manager.gitlab, parent=self.manager._parent
        )
        # FIXME(gpocentek): the computed manager path is not correct
        return RESTObjectList(manager, GroupMergeRequest, data_list)


class GroupMilestoneManager(CRUDMixin[GroupMilestone]):
    _path = "/groups/{group_id}/milestones"
    _obj_cls = GroupMilestone
    _from_parent_attrs = {"group_id": "id"}
    _create_attrs = RequiredOptional(
        required=("title",), optional=("description", "due_date", "start_date")
    )
    _update_attrs = RequiredOptional(
        optional=("title", "description", "due_date", "start_date", "state_event")
    )
    _list_filters = ("iids", "state", "search")
    _types = {"iids": types.ArrayAttribute}


class ProjectMilestone(PromoteMixin, SaveMixin, ObjectDeleteMixin, RESTObject):
    _repr_attr = "title"
    _update_method = UpdateMethod.POST

    @cli.register_custom_action(cls_names="ProjectMilestone")
    @exc.on_http_error(exc.GitlabListError)
    def issues(self, **kwargs: Any) -> RESTObjectList[ProjectIssue]:
        """List issues related to this milestone.

        Args:
            get_all: If True, return all the items, without pagination
            per_page: Number of items to retrieve per request
            page: ID of the page to return (starts with page 1)
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabListError: If the list could not be retrieved

        Returns:
            The list of issues
        """

        path = f"{self.manager.path}/{self.encoded_id}/issues"
        data_list = self.manager.gitlab.http_list(path, iterator=True, **kwargs)
        if TYPE_CHECKING:
            assert isinstance(data_list, GitlabList)
        manager = ProjectIssueManager(self.manager.gitlab, parent=self.manager._parent)
        # FIXME(gpocentek): the computed manager path is not correct
        return RESTObjectList(manager, ProjectIssue, data_list)

    @cli.register_custom_action(cls_names="ProjectMilestone")
    @exc.on_http_error(exc.GitlabListError)
    def merge_requests(self, **kwargs: Any) -> RESTObjectList[ProjectMergeRequest]:
        """List the merge requests related to this milestone.

        Args:
            get_all: If True, return all the items, without pagination
            per_page: Number of items to retrieve per request
            page: ID of the page to return (starts with page 1)
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabListError: If the list could not be retrieved

        Returns:
            The list of merge requests
        """
        path = f"{self.manager.path}/{self.encoded_id}/merge_requests"
        data_list = self.manager.gitlab.http_list(path, iterator=True, **kwargs)
        if TYPE_CHECKING:
            assert isinstance(data_list, GitlabList)
        manager = ProjectMergeRequestManager(
            self.manager.gitlab, parent=self.manager._parent
        )
        # FIXME(gpocentek): the computed manager path is not correct
        return RESTObjectList(manager, ProjectMergeRequest, data_list)


class ProjectMilestoneManager(CRUDMixin[ProjectMilestone]):
    _path = "/projects/{project_id}/milestones"
    _obj_cls = ProjectMilestone
    _from_parent_attrs = {"project_id": "id"}
    _create_attrs = RequiredOptional(
        required=("title",),
        optional=("description", "due_date", "start_date", "state_event"),
    )
    _update_attrs = RequiredOptional(
        optional=("title", "description", "due_date", "start_date", "state_event")
    )
    _list_filters = ("iids", "state", "search")
    _types = {"iids": types.ArrayAttribute}
