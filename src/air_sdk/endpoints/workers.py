# SPDX-FileCopyrightText: Copyright (c) 2022-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: MIT

from __future__ import annotations

from dataclasses import _MISSING_TYPE, MISSING, dataclass, field
from datetime import datetime
from http import HTTPStatus
from typing import Any, Iterator, TypedDict

from air_sdk.air_model import AirModel, BaseEndpointAPI, DataDict, PrimaryKey
from air_sdk.endpoints import mixins
from air_sdk.endpoints.fleets import Fleet
from air_sdk.utils import join_urls, raise_if_invalid_response, validate_payload_types


@dataclass(eq=False)
class Worker(AirModel):
    id: str = field(repr=False)
    created: datetime = field(repr=False)
    modified: datetime = field(repr=False)
    fqdn: str
    fleet: Fleet = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    cpu: int = field(repr=False)
    memory: int = field(repr=False)
    storage: int = field(repr=False)
    available: bool
    cpu_arch: str
    ip_address: str

    # Only populated upon creation
    registration_token: str | None = field(repr=False)

    @classmethod
    def get_model_api(cls) -> type[WorkerEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model."""
        return WorkerEndpointAPI

    @validate_payload_types
    def update(
        self,
        *,
        fqdn: str | _MISSING_TYPE = MISSING,
        ip_address: str | _MISSING_TYPE = MISSING,
        cpu: int | _MISSING_TYPE = MISSING,
        memory: int | _MISSING_TYPE = MISSING,
        storage: int | _MISSING_TYPE = MISSING,
        available: bool | _MISSING_TYPE = MISSING,
    ) -> None:
        """Update specific fields of the worker.


        Example
        -------
            >>> worker = api.workers.get('123e4567-e89b-12d3-a456-426614174000')
            >>> worker.update(cpu=16)
        """
        data = {
            'fqdn': fqdn,
            'ip_address': ip_address,
            'cpu': cpu,
            'memory': memory,
            'storage': storage,
            'available': available,
        }
        payload = {key: value for (key, value) in data.items() if value is not MISSING}
        super().update(**payload)

    def issue_certificate(self) -> PEMCertificateData:
        """
        Issue a new client certificate for the worker.

        Example
        -------
            >>> worker = api.workers.get('123e4567-e89b-12d3-a456-426614174000')
            >>> cert_data = worker.issue_certificate()
            >>> cert, key = cert_data['certificate'], cert_data['private_key']
        """
        issue_certificate_response = self.__api__.client.post(
            join_urls(
                self.detail_url,
                self.get_model_api().ISSUE_CERTIFICATE_PATH,
            )
        )
        raise_if_invalid_response(
            issue_certificate_response, status_code=HTTPStatus.CREATED
        )
        certificate_data: PEMCertificateData = issue_certificate_response.json()

        return certificate_data


@dataclass(eq=False)
class WorkerClientCertificate(AirModel):
    id: str = field(repr=False)
    worker: Worker = field(metadata=AirModel.FIELD_FOREIGN_KEY, repr=False)
    worker_fqdn: str
    usable: bool = field(repr=False)
    expires: datetime
    fingerprint: str = field(repr=False)
    last_used: datetime | None = field(repr=False)
    revoked: bool

    @classmethod
    def get_model_api(cls) -> type[WorkerClientCertificateEndpointAPI]:
        """Returns the respective `AirModelAPI` type for this model."""
        return WorkerClientCertificateEndpointAPI

    def revoke(self) -> None:
        """
        Revoke this client certificate.
        Once a certificate is revoked, it may no longer be used!

        Example
        -------
            >>> certificates = api.worker_client_certificates.list()
            >>> for certificate in certificates:
            ...     if certificate.fingerprint == '...':
            ...         certificate.revoke()
        """
        revoke_certificate_response = self.__api__.client.patch(
            join_urls(
                self.detail_url,
                self.get_model_api().REVOKE_PATH,
            )
        )
        raise_if_invalid_response(revoke_certificate_response, status_code=HTTPStatus.OK)
        self.refresh()


class PEMCertificateData(TypedDict):
    """Certificate data issued for the worker in PEM format."""

    certificate: str
    private_key: str


class WorkerEndpointAPI(
    mixins.ListApiMixin[Worker],
    mixins.CreateApiMixin[Worker],
    mixins.GetApiMixin[Worker],
    mixins.PatchApiMixin[Worker],
    mixins.DeleteApiMixin,
    BaseEndpointAPI[Worker],
):
    API_PATH = 'infra/workers/'
    ISSUE_CERTIFICATE_PATH = 'issue-certificate'
    model = Worker

    @validate_payload_types
    def list(
        self,
        fqdn: str | _MISSING_TYPE = MISSING,
        search: str | _MISSING_TYPE = MISSING,
        ordering: str | _MISSING_TYPE = MISSING,
        **params: Any,
    ) -> Iterator[Worker]:
        """List all workers.

        Example
        -------
            >>> for worker in api.workers.list(ordering='fqdn'):
            ...     print(worker.fqdn)
        """
        params.update(
            {
                k: v
                for k, v in {
                    'fqdn': fqdn,
                    'search': search,
                    'ordering': ordering,
                }.items()
                if v is not MISSING
            }
        )
        return super().list(**params)

    @validate_payload_types
    def create(
        self,
        *,
        fleet: Fleet | PrimaryKey,
        ip_address: str,
        fqdn: str,
        cpu_arch: str | _MISSING_TYPE = MISSING,
    ) -> Worker:
        """Create a new worker.

        Example
        -------
            >>> fleet = api.fleets.get('123e4567-e89b-12d3-a456-426614174000')
            >>> image = api.images.get('456e89ab-cdef-0123-4567-89abcdef0123')
            >>> node = api.nodes.create(simulation=sim, image=image, name='my-node')
        """
        data: DataDict = {
            'fleet': fleet,
            'ip_address': ip_address,
            'fqdn': fqdn,
            'cpu_arch': cpu_arch,
        }
        payload = {key: value for (key, value) in data.items() if value is not MISSING}
        return super().create(**payload)


class WorkerClientCertificateEndpointAPI(
    mixins.ListApiMixin[WorkerClientCertificate],
    mixins.GetApiMixin[WorkerClientCertificate],
    BaseEndpointAPI[WorkerClientCertificate],
):
    API_PATH = 'infra/workers/certificates/'
    REVOKE_PATH = 'revoke'
    model = WorkerClientCertificate

    @validate_payload_types
    def list(
        self,
        worker: Worker | PrimaryKey | _MISSING_TYPE = MISSING,
        search: str | _MISSING_TYPE = MISSING,
        ordering: str | _MISSING_TYPE = MISSING,
        **params: Any,
    ) -> Iterator[WorkerClientCertificate]:
        """List all worker certificates.

        Example
        -------
            >>> worker = api.workers.get('123e4567-e89b-12d3-a456-426614174000')
            >>> for certificate in api.worker_client_certificates.list(worker=worker):
            ...     print(certificate.fingerprint)
        """
        params.update(
            {
                k: v
                for k, v in {
                    'worker': worker,
                    'search': search,
                    'ordering': ordering,
                }.items()
                if v is not MISSING
            }
        )
        return super().list(**params)
