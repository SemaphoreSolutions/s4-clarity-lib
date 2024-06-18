# Copyright 2019 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
import logging
import re
import time

try:
    import urllib.parse as urlparse  # Python 3
except ImportError:
    import urlparse  # Python 2

from xml.etree import cElementTree as ETree

import requests
import urllib3

# Ensure Python 2 and 3 compatibility
from six import BytesIO, b

from s4.clarity._internal.factory import BatchFlags
from s4.clarity._internal.stepfactory import StepFactory, ElementFactory
from s4.clarity._internal.udffactory import UdfFactory
from s4.clarity._internal.lazy_property import lazy_property
from s4.clarity._internal.fakesession import FakeSession
from .exception import ClarityException


log = logging.getLogger(__name__)


class LIMS(object):
    """
    :param str root_uri: Location of the clarity server e.g. (https://<clarity server>/api/v2/)
    :param str username: Clarity User Name
    :param str password: Clarity Password
    :param bool dry_run: If true, no destructive requests will be made to the Clarity API. Default false.
    :param bool insecure: Disables SSL validation. Default false.
    :param int timeout: Number of seconds to wait for connections and for reads from the Clarity API. Default None, which is no timeout.

    :ivar ElementFactory steps: Factory for :class:`s4.clarity.step.Step`
    :ivar ElementFactory samples: Factory for :class:`s4.clarity.sample.Sample`
    :ivar ElementFactory artifacts: Factory for :class:`s4.clarity.artifact.Artifact`
    :ivar ElementFactory files: Factory for :class:`s4.clarity.file.File`
    :ivar ElementFactory containers: Factory for :class:`s4.clarity.container.Container`
    :ivar ElementFactory projects: Factory for :class:`s4.clarity.project.Project`
    :ivar ElementFactory instruments: Factory for :class:`s4.clarity.instrument.Instrument`
    :ivar ElementFactory workflows: Factory for :class:`s4.clarity.configuration.workflow.Workflow`
    :ivar ElementFactory protocols: Factory for :class:`s4.clarity.configuration.protocol.Protocol`
    :ivar ElementFactory process_types: Factory for :class:`s4.clarity.configuration.process_type.ProcessType`
    :ivar ElementFactory process_templates: Factory for :class:`s4.clarity.configuration.process_type.ProcessTemplate`
    :ivar ElementFactory processes: Factory for :class:`s4.clarity.process.Process`
    :ivar ElementFactory researchers: Factory for :class:`s4.clarity.researcher.Researcher`
    :ivar ElementFactory roles: Factory for :class:`s4.clarity.role.Role`
    :ivar ElementFactory permissions: Factory for :class:`s4.clarity.permission.Permission`
    """

    _HOST_RE = re.compile(r'https?://([^/:]+)')
    DEFAULT_TIMEOUT=None

    def __init__(self, root_uri, username, password, dry_run=False, insecure=False, log_requests=False, timeout=DEFAULT_TIMEOUT):
        if root_uri.endswith("/"):
            self.root_uri = root_uri[:-1]  # strip off /
        else:
            self.root_uri = root_uri

        hostname_match = self._HOST_RE.match(self.root_uri)
        if not hostname_match:
            raise Exception("No hostname found in LIMS uri: %s" % self.root_uri)
        self.hostname = hostname_match.group(1)
        self._opened_ssh_tunnel = False
        self._insecure = insecure
        self.log_requests = log_requests

        if "dev" in self.hostname:
            self.environment = "dev"
        elif "test" in self.hostname:
            self.environment = "test"
        else:
            self.environment = "production"

        self.username = username
        self.password = password
        self.dry_run = dry_run
        self.timeout = timeout

        from .step import Step
        from .artifact import Artifact
        from .container import Container
        from .container import ContainerType
        from .sample import Sample
        from .file import File
        from .project import Project
        from .control_type import ControlType
        from .queue import Queue
        from .reagent_kit import ReagentKit
        from .reagent_lot import ReagentLot
        from .reagent_type import ReagentType
        from .instrument import Instrument
        from .researcher import Researcher
        from .role import Role
        from .permission import Permission
        from .process import Process
        from .configuration.stage import Stage
        from .lab import Lab

        self.factories = {}

        # there's no need to make these lazy, we are probably using at least a couple of them
        self.steps = StepFactory(self, Step, batch_flags=BatchFlags.QUERY)

        self.processes = ElementFactory(self, Process, batch_flags=BatchFlags.QUERY, request_path='/processes')

        self.samples = ElementFactory(self, Sample, batch_flags=BatchFlags.BATCH_ALL)

        self.artifacts = ElementFactory(self, Artifact, batch_flags=BatchFlags.BATCH_ALL & ~BatchFlags.BATCH_CREATE)

        self.files = ElementFactory(self, File, batch_flags=BatchFlags.BATCH_ALL & ~BatchFlags.BATCH_CREATE)

        self.containers = ElementFactory(self, Container, batch_flags=BatchFlags.BATCH_ALL)

        self.container_types = ElementFactory(self, ContainerType, batch_flags=BatchFlags.QUERY)

        self.projects = ElementFactory(self, Project, batch_flags=BatchFlags.QUERY)

        self.control_types = ElementFactory(self, ControlType)

        self.queues = ElementFactory(self, Queue)

        self.instruments = ElementFactory(self, Instrument, batch_flags=BatchFlags.QUERY)

        self.reagent_lots = ElementFactory(self, ReagentLot, batch_flags=BatchFlags.QUERY)

        self.reagent_kits = ElementFactory(self, ReagentKit, batch_flags=BatchFlags.QUERY)

        self.reagent_types = ElementFactory(self, ReagentType, batch_flags=BatchFlags.QUERY)

        self.researchers = ElementFactory(self, Researcher, batch_flags=BatchFlags.QUERY)

        self.labs = ElementFactory(self, Lab, batch_flags=BatchFlags.QUERY)

        self.roles = ElementFactory(self, Role, batch_flags=BatchFlags.QUERY)

        self.permissions = ElementFactory(self, Permission, batch_flags=BatchFlags.QUERY)

        # configuration
        from .configuration import Workflow, Protocol, ProcessType, Udf, ProcessTemplate, Automation

        self.workflows = ElementFactory(self, Workflow, batch_flags=BatchFlags.QUERY,
                                        request_path='/configuration/workflows')
        self.protocols = ElementFactory(self, Protocol, batch_flags=BatchFlags.QUERY,
                                        request_path='/configuration/protocols')
        self.udfs = UdfFactory(self, Udf, batch_flags=BatchFlags.QUERY,
                               request_path='/configuration/udfs')
        self.process_types = ElementFactory(self, ProcessType, batch_flags=BatchFlags.QUERY,
                                            name_attribute="displayname")
        self.process_templates = ElementFactory(self, ProcessTemplate, batch_flags=BatchFlags.QUERY,
                                                name_attribute="name")
        self.automations = ElementFactory(self, Automation, batch_flags=BatchFlags.QUERY,
                                          name_attribute="name", request_path="/configuration/automations")

        self.stages = ElementFactory(self, Stage)

    def factory_for(self, element_type):
        """
        :type element_type: type[ClarityElement]
        :rtype: ElementFactory
        """
        factory = self.factories.get(element_type)

        if factory is None:
            raise Exception("No Clarity ElementFactory for type %s" % element_type.__name__)

        return factory

    @lazy_property
    def _session(self):
        if self.dry_run:
            log.info("LIMS dry run. No destructive requests will be sent to real LIMS.")
            s = FakeSession()
        else:
            s = requests.Session()
        if self._insecure:
            log.warning("WARNING - This machine is not validating SSL certificates. DO NOT ENABLE IN PRODUCTION.")
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            s.verify = False

        s.auth = (self.username, self.password)
        return s

    def step_from_uri(self, uri):
        """
        :type uri: str
        :rtype: Step
        """
        return self.steps.get(uri)

    def artifact_from_uri(self, uri):
        """
        :type uri: str
        :rtype: Artifact
        """
        return self.artifacts.get(uri)

    def stepconfiguration_from_uri(self, uri):
        """
        :type uri: str
        :rtype: StepConfiguration
        """
        splituri = uri.split('/')
        protocol_uri = '/'.join(splituri[:-2])
        step_id = splituri[-1]
        protocol = self.protocols.get(protocol_uri, force_full_get=True)
        return protocol.step_from_id(step_id)

    def stage_from_uri(self, uri):
        """
        :type uri: str
        :rtype: Stage
        """
        splituri = uri.split('/')
        workflow_uri = '/'.join(splituri[:-2])
        stage_id = splituri[-1]
        workflow = self.workflows.get(workflow_uri, force_full_get=True)
        return workflow.stage_from_id(stage_id)

    def step(self, limsid):
        """
        :type limsid: str
        :rtype: Step
        """
        return self.steps.get(self.root_uri + "/steps/" + limsid, limsid=limsid)

    def sample(self, limsid):
        """
        :type limsid: str
        :rtype: Sample
        """
        return self.samples.get(self.root_uri + "/samples/" + limsid, limsid=limsid)

    def artifact(self, limsid):
        """
        :type limsid: str
        :rtype: Artifact
        """
        return self.artifacts.get(self.root_uri + "/artifacts/" + limsid, limsid=limsid)

    @lazy_property
    def properties(self):
        """
        :type: dict
        """
        root = self.request("get", self.root_uri + "/configuration/properties" )
        properties = root.findall("property")
        return dict( (property.get("name"), property.get("value")) for property in properties )

    @lazy_property
    def versions(self):
        """
        :type: list[dict]
        """
        root = self.request("get", self.root_uri + "/..")
        versions = root.findall("version")
        return list({
            "uri": version.get("uri"),
            "major": version.get("major"),
            "minor": version.get("minor")
        } for version in versions)

    @lazy_property
    def current_minor_version(self):
        """
        :type: str
        """
        path = urlparse.urlparse(self.root_uri).path
        current_major_version = [x for x in path.split("/") if x][-1]
        root = self.request("get", self.root_uri + "/..")
        xpath = "version[@major='%s']" % current_major_version
        version = root.findall(xpath)[0]
        return version.get("minor")

    def raw_request(self, method, uri, **kwargs):
        """
        :type method: str
        :type uri: str
        :raises ClarityException: if Clarity returns an exception as XML
        :rtype: requests.Response
        """

        log.debug("Sending %s %s", method, uri)

        if ":ssh/" in uri:
            host_match = self._HOST_RE.match(uri)
            if not host_match:
                raise Exception("malformed uri: " % uri)
            real_host = host_match.group(1)
            uri = uri.replace(real_host + ":ssh", "localhost:9080")
            if not self._opened_ssh_tunnel:
                s4.clarity.utils.ssh.tunnel(real_host, 9080, "glsai")
                self._opened_ssh_tunnel = True

        response = self._session.request(method, uri, timeout=self.timeout, allow_redirects=False, **kwargs)

        ClarityException.raise_if_present(response, data=kwargs.get("data"), username=self.username)
        log.debug("Received: %s", response.text)
        return response

    def request(self, method, uri, xml_root=None):
        """
        :type method: str
        :type uri: str
        :type xml_root: ETree.Element
        :rtype: ETree.Element
        :raises ClarityException: if Clarity returns an exception as XML
        """
        request_start_seconds = time.perf_counter() if self.log_requests else 0
        if xml_root is None:
            response = self.raw_request(method, uri)
        else:
            # Falls back to StringIO and regular string for Python 2
            outbuffer = BytesIO(b('<?xml version="1.0" encoding="UTF-8"?>\n'))
            ETree.ElementTree(xml_root).write(outbuffer)
            outbuffer.seek(0)
            log.debug("Data for request: %s", outbuffer.read())
            outbuffer.seek(0)
            response = self.raw_request(method, uri, data=outbuffer.getvalue(),
                                        headers={'Content-Type': 'application/xml'})
            outbuffer.close()

        xml_response_root = ETree.XML(response.content) if response.content else None

        if self.log_requests:
            request_elapsed_seconds = time.perf_counter() - request_start_seconds
            log.info("clarity request method: '%s' uri: %s took: %.3f s", method, uri, request_elapsed_seconds)

        return xml_response_root
