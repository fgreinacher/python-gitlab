from __future__ import annotations

import base64
from typing import Any, Callable, Iterator, Literal, overload, TYPE_CHECKING

import requests

from gitlab import cli
from gitlab import exceptions as exc
from gitlab import utils
from gitlab.base import RESTObject
from gitlab.mixins import (
    CreateMixin,
    DeleteMixin,
    ObjectDeleteMixin,
    SaveMixin,
    UpdateMixin,
)
from gitlab.types import RequiredOptional

__all__ = ["ProjectFile", "ProjectFileManager"]


class ProjectFile(SaveMixin, ObjectDeleteMixin, RESTObject):
    _id_attr = "file_path"
    _repr_attr = "file_path"
    branch: str
    commit_message: str
    file_path: str
    manager: ProjectFileManager
    content: str  # since the `decode()` method uses `self.content`

    def decode(self) -> bytes:
        """Returns the decoded content of the file.

        Returns:
            The decoded content.
        """
        return base64.b64decode(self.content)

    # NOTE(jlvillal): Signature doesn't match SaveMixin.save() so ignore
    # type error
    def save(  # type: ignore[override]
        self, branch: str, commit_message: str, **kwargs: Any
    ) -> None:
        """Save the changes made to the file to the server.

        The object is updated to match what the server returns.

        Args:
            branch: Branch in which the file will be updated
            commit_message: Message to send with the commit
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabUpdateError: If the server cannot perform the request
        """
        self.branch = branch
        self.commit_message = commit_message
        self.file_path = utils.EncodedId(self.file_path)
        super().save(**kwargs)

    @exc.on_http_error(exc.GitlabDeleteError)
    # NOTE(jlvillal): Signature doesn't match DeleteMixin.delete() so ignore
    # type error
    def delete(  # type: ignore[override]
        self, branch: str, commit_message: str, **kwargs: Any
    ) -> None:
        """Delete the file from the server.

        Args:
            branch: Branch from which the file will be removed
            commit_message: Commit message for the deletion
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabDeleteError: If the server cannot perform the request
        """
        file_path = self.encoded_id
        if TYPE_CHECKING:
            assert isinstance(file_path, str)
        self.manager.delete(file_path, branch, commit_message, **kwargs)


class ProjectFileManager(
    CreateMixin[ProjectFile], UpdateMixin[ProjectFile], DeleteMixin[ProjectFile]
):
    _path = "/projects/{project_id}/repository/files"
    _obj_cls = ProjectFile
    _from_parent_attrs = {"project_id": "id"}
    _optional_get_attrs: tuple[str, ...] = ()
    _create_attrs = RequiredOptional(
        required=("file_path", "branch", "content", "commit_message"),
        optional=(
            "encoding",
            "author_email",
            "author_name",
            "execute_filemode",
            "start_branch",
        ),
    )
    _update_attrs = RequiredOptional(
        required=("file_path", "branch", "content", "commit_message"),
        optional=(
            "encoding",
            "author_email",
            "author_name",
            "execute_filemode",
            "start_branch",
            "last_commit_id",
        ),
    )

    @cli.register_custom_action(
        cls_names="ProjectFileManager", required=("file_path", "ref")
    )
    @exc.on_http_error(exc.GitlabGetError)
    def get(self, file_path: str, ref: str, **kwargs: Any) -> ProjectFile:
        """Retrieve a single file.

        Args:
            file_path: Path of the file to retrieve
            ref: Name of the branch, tag or commit
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabGetError: If the file could not be retrieved

        Returns:
            The generated RESTObject
        """
        if TYPE_CHECKING:
            assert file_path is not None
        file_path = utils.EncodedId(file_path)
        path = f"{self.path}/{file_path}"
        server_data = self.gitlab.http_get(path, ref=ref, **kwargs)
        if TYPE_CHECKING:
            assert isinstance(server_data, dict)
        return self._obj_cls(self, server_data)

    @exc.on_http_error(exc.GitlabHeadError)
    def head(
        self, file_path: str, ref: str, **kwargs: Any
    ) -> requests.structures.CaseInsensitiveDict[Any]:
        """Retrieve just metadata for a single file.

        Args:
            file_path: Path of the file to retrieve
            ref: Name of the branch, tag or commit
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabGetError: If the file could not be retrieved

        Returns:
            The response headers as a dictionary
        """
        if TYPE_CHECKING:
            assert file_path is not None
        file_path = utils.EncodedId(file_path)
        path = f"{self.path}/{file_path}"
        return self.gitlab.http_head(path, ref=ref, **kwargs)

    @cli.register_custom_action(
        cls_names="ProjectFileManager",
        required=("file_path", "branch", "content", "commit_message"),
        optional=(
            "encoding",
            "author_email",
            "author_name",
            "execute_filemode",
            "start_branch",
        ),
    )
    @exc.on_http_error(exc.GitlabCreateError)
    def create(self, data: dict[str, Any] | None = None, **kwargs: Any) -> ProjectFile:
        """Create a new object.

        Args:
            data: parameters to send to the server to create the
                         resource
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            a new instance of the managed object class built with
                the data sent by the server

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabCreateError: If the server cannot perform the request
        """

        if TYPE_CHECKING:
            assert data is not None
        self._create_attrs.validate_attrs(data=data)
        new_data = data.copy()
        file_path = utils.EncodedId(new_data.pop("file_path"))
        path = f"{self.path}/{file_path}"
        server_data = self.gitlab.http_post(path, post_data=new_data, **kwargs)
        if TYPE_CHECKING:
            assert isinstance(server_data, dict)
        return self._obj_cls(self, server_data)

    @exc.on_http_error(exc.GitlabUpdateError)
    # NOTE(jlvillal): Signature doesn't match UpdateMixin.update() so ignore
    # type error
    def update(  # type: ignore[override]
        self, file_path: str, new_data: dict[str, Any] | None = None, **kwargs: Any
    ) -> dict[str, Any]:
        """Update an object on the server.

        Args:
            id: ID of the object to update (can be None if not required)
            new_data: the update data for the object
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            The new object data (*not* a RESTObject)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabUpdateError: If the server cannot perform the request
        """
        new_data = new_data or {}
        data = new_data.copy()
        file_path = utils.EncodedId(file_path)
        data["file_path"] = file_path
        path = f"{self.path}/{file_path}"
        self._update_attrs.validate_attrs(data=data)
        result = self.gitlab.http_put(path, post_data=data, **kwargs)
        if TYPE_CHECKING:
            assert isinstance(result, dict)
        return result

    @cli.register_custom_action(
        cls_names="ProjectFileManager",
        required=("file_path", "branch", "commit_message"),
    )
    @exc.on_http_error(exc.GitlabDeleteError)
    # NOTE(jlvillal): Signature doesn't match DeleteMixin.delete() so ignore
    # type error
    def delete(  # type: ignore[override]
        self, file_path: str, branch: str, commit_message: str, **kwargs: Any
    ) -> None:
        """Delete a file on the server.

        Args:
            file_path: Path of the file to remove
            branch: Branch from which the file will be removed
            commit_message: Commit message for the deletion
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabDeleteError: If the server cannot perform the request
        """
        file_path = utils.EncodedId(file_path)
        path = f"{self.path}/{file_path}"
        data = {"branch": branch, "commit_message": commit_message}
        self.gitlab.http_delete(path, query_data=data, **kwargs)

    @overload
    def raw(
        self,
        file_path: str,
        ref: str | None = None,
        streamed: Literal[False] = False,
        action: None = None,
        chunk_size: int = 1024,
        *,
        iterator: Literal[False] = False,
        **kwargs: Any,
    ) -> bytes: ...

    @overload
    def raw(
        self,
        file_path: str,
        ref: str | None = None,
        streamed: bool = False,
        action: None = None,
        chunk_size: int = 1024,
        *,
        iterator: Literal[True] = True,
        **kwargs: Any,
    ) -> Iterator[Any]: ...

    @overload
    def raw(
        self,
        file_path: str,
        ref: str | None = None,
        streamed: Literal[True] = True,
        action: Callable[[bytes], Any] | None = None,
        chunk_size: int = 1024,
        *,
        iterator: Literal[False] = False,
        **kwargs: Any,
    ) -> None: ...

    @cli.register_custom_action(
        cls_names="ProjectFileManager", required=("file_path",), optional=("ref",)
    )
    @exc.on_http_error(exc.GitlabGetError)
    def raw(
        self,
        file_path: str,
        ref: str | None = None,
        streamed: bool = False,
        action: Callable[..., Any] | None = None,
        chunk_size: int = 1024,
        *,
        iterator: bool = False,
        **kwargs: Any,
    ) -> bytes | Iterator[Any] | None:
        """Return the content of a file for a commit.

        Args:
            file_path: Path of the file to return
            ref: ID of the commit
            streamed: If True the data will be processed by chunks of
                `chunk_size` and each chunk is passed to `action` for
                treatment
            action: Callable responsible for dealing with each chunk of
                data
            chunk_size: Size of each chunk
            iterator: If True directly return the underlying response
                iterator
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabGetError: If the file could not be retrieved

        Returns:
            The file content
        """
        file_path = utils.EncodedId(file_path)
        path = f"{self.path}/{file_path}/raw"
        if ref is not None:
            query_data = {"ref": ref}
        else:
            query_data = None
        result = self.gitlab.http_get(
            path, query_data=query_data, streamed=streamed, raw=True, **kwargs
        )
        if TYPE_CHECKING:
            assert isinstance(result, requests.Response)
        return utils.response_content(
            result, streamed, action, chunk_size, iterator=iterator
        )

    @cli.register_custom_action(
        cls_names="ProjectFileManager", required=("file_path", "ref")
    )
    @exc.on_http_error(exc.GitlabListError)
    def blame(self, file_path: str, ref: str, **kwargs: Any) -> list[dict[str, Any]]:
        """Return the content of a file for a commit.

        Args:
            file_path: Path of the file to retrieve
            ref: Name of the branch, tag or commit
            **kwargs: Extra options to send to the server (e.g. sudo)

        Raises:
            GitlabAuthenticationError: If authentication is not correct
            GitlabListError:  If the server failed to perform the request

        Returns:
            A list of commits/lines matching the file
        """
        file_path = utils.EncodedId(file_path)
        path = f"{self.path}/{file_path}/blame"
        query_data = {"ref": ref}
        result = self.gitlab.http_list(path, query_data, **kwargs)
        if TYPE_CHECKING:
            assert isinstance(result, list)
        return result
