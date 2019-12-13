# Copyright 2019 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
import logging
import re
import time
from xml.etree import cElementTree as ETree

import requests
import urllib3

# Ensure Python 2 and 3 compatibility
from six import BytesIO, b

from s4.clarity._internal.stepfactory import StepFactory, ElementFactory
from s4.clarity._internal.udffactory import UdfFactory
from s4.clarity._internal.lazy_property import lazy_property
from .exception import ClarityException


log = logging.getLogger(__name__)


class LIMS(object):
    """

    :ivar ElementFactory steps: Factory for :class:`s4.clarity.step.Step`
    :ivar ElementFactory samples: Factory for :class:`s4.clarity.sample.Sample`
    :ivar ElementFactory artifacts: Factory for :class:`s4.clarity.artifact.Artifact`
    :ivar ElementFactory files: Factory for :class:`s4.clarity.file.File`
    :ivar ElementFactory containers: Factory for :class:`s4.clarity.container.Container`
    :ivar ElementFactory projects: Factory for :class:`s4.clarity.project.Project`
    :ivar ElementFactory workflows: Factory for :class:`s4.clarity.configuration.workflow.Workflow`
    :ivar ElementFactory protocols: Factory for :class:`s4.clarity.configuration.protocol.Protocol`
    :ivar ElementFactory process_types: Factory for :class:`s4.clarity.configuration.process_type.ProcessType`
    :ivar ElementFactory process_templates: Factory for :class:`s4.clarity.configuration.process_type.ProcessTemplate`
    :ivar ElementFactory processes: Factory for :class:`s4.clarity.process.Process`
    :ivar ElementFactory researchers: Factory for :class:`s4.clarity.researcher.Researcher`
    :ivar ElementFactory roles: Factory for :class:`s4.clarity.role.Role`
    :ivar ElementFactory permissions: Factory for :class:`s4.clarity.permission.Permission`
    """

    def __init__(self, root_uri, username, password, dry_run=False, insecure=False, log_requests=False):
        """
        Constructs a new LIMS object. This will provide an interface to the Clarity LIMS server, found
        at the Root URI. The user name and password provided will be used to authenticate with Clarity and
        all actions taken by the script will be done as that user.

        If a Dry Run is selected then no data will be sent back to Clarity.

        If Insecure is selected then the SSL Certificate used does not need to be signed by a signing authority.
        This is useful in the case where you are operating against a development server using a self signed cert.

        Log Requests will create log entries for each HTTP request made.

        :param str root_uri: Location of the clarity server e.g. (https://<clarity server>/api/v2/)
        :param str username: Clarity User Name
        :param str password: Clarity Password
        :param bool dry_run: If True, do not actually make calls to Clarity
        :param bool insecure: Disables SSL validation
        :param log_requests: Log extra information about HTTP requests
        """

        # strip off the trailing `/` from the URI if one was included
        self.root_uri = root_uri.rstrip("/")
        self.hostname = self._get_hostname()

        self._opened_ssh_tunnel = False
        self._insecure = insecure
        self.log_requests = log_requests
        self.environment = self._get_environment()

        self.username = username
        self.password = password
        self.dry_run = dry_run

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
        from .researcher import Researcher
        from .role import Role
        from .permission import Permission
        from .process import Process
        from .configuration.stage import Stage
        from .lab import Lab

        # Initialise the list of factories. The element factories will
        # add themselves to this dictionary when they are created
        self.factories = {}

        self.steps = StepFactory(self, Step)

        self.processes = ElementFactory(self, Process)

        self.samples = ElementFactory(self, Sample)

        self.artifacts = ElementFactory(self, Artifact)

        self.files = ElementFactory(self, File)

        self.containers = ElementFactory(self, Container)

        self.container_types = ElementFactory(self, ContainerType)

        self.projects = ElementFactory(self, Project)

        self.control_types = ElementFactory(self, ControlType)

        self.queues = ElementFactory(self, Queue)

        self.reagent_lots = ElementFactory(self, ReagentLot)

        self.reagent_kits = ElementFactory(self, ReagentKit)

        self.reagent_types = ElementFactory(self, ReagentType)

        self.researchers = ElementFactory(self, Researcher)

        self.labs = ElementFactory(self, Lab)

        self.roles = ElementFactory(self, Role)

        self.permissions = ElementFactory(self, Permission)

        # configuration
        from .configuration import Workflow, Protocol, ProcessType, Udf, ProcessTemplate, Automation

        self.workflows = ElementFactory(self, Workflow)

        self.protocols = ElementFactory(self, Protocol)

        self.udfs = UdfFactory(self, Udf)

        self.process_types = ElementFactory(self, ProcessType)

        self.process_templates = ElementFactory(self, ProcessTemplate)

        self.automations = ElementFactory(self, Automation)

        self.stages = ElementFactory(self, Stage)

    def _get_hostname(self):
        # type: () -> str
        """
        Verify that we have a valid hostname in our root uri
        and isolate the host name from it.
        :return: The name of the Clarity server.
        """

        # Compile a regex statement to isolate the host name
        # and verify that our root uri looks like a properly formed URI
        hostname_finding_regex = re.compile(r'https?://([^/:]+)')

        # Then use it to validate our uri
        hostname_match = hostname_finding_regex.match(self.root_uri)
        if not hostname_match:
            raise Exception("No hostname found in LIMS uri: %s" % self.root_uri)

        # Using the same RegEx query select out the hostname from the URI
        return hostname_match.group(1)

    def _get_environment(self):
        """
        We make some assumptions about the server's purpose based on
        the presence of keywords in the name. This matches the common naming
        schemes for servers.

        ex: clarity-dev.client_domain.com
            clarity-test.client_domain.com
            clarity.client_domain.com

        :return: A string identifying the environment.
        """

        if "dev" in self.hostname:
            return "dev"

        if "test" in self.hostname:
            return "test"

        return "production"

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
            s = s4.clarity.utils.fakesession.FakeSession()
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

        response = self._session.request(method, uri, allow_redirects=False, **kwargs)

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
