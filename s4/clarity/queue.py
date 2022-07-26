# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from six.moves.urllib.parse import urlencode

from ._internal import ClarityElement, WrappedXml
from ._internal.props import subnode_property
from s4.clarity import types


class Queue(ClarityElement):
    UNIVERSAL_TAG = "{http://genologics.com/ri/queue}queue"

    @property
    def queued_artifacts(self):
        return self.query()

    def query(self, prefetch=True, **params):
        queued_elements = []

        for k in params:
            if "_" in k:
                new_k = k.replace("_", "-")
                params[new_k] = params[k]
                del params[k]

        query_uri = self.uri + "?" + urlencode(params, doseq=True)

        while query_uri is not None:
            next_page_node = self.lims.request("get", query_uri)
            queued_elements += next_page_node.findall("./artifacts/artifact")
            next_page_link = next_page_node.find("./next-page")
            if next_page_link is not None:
                query_uri = next_page_link.get("uri")
            else:
                query_uri = None

        queued_artifacts = [QueueArtifact(self.lims, p) for p in queued_elements]

        if prefetch:
            self.lims.artifacts.batch_fetch([queued_artifact.artifact for queued_artifact in queued_artifacts])

        return queued_artifacts


class QueueArtifact(WrappedXml):

    @property
    def limsid(self):
        return self.xml_root.get("limsid")

    @property
    def uri(self):
        return self.xml_root.get("uri")

    @property
    def artifact(self):
        return self.lims.artifacts.get(uri=self.uri, limsid=self.limsid)

    queue_time = subnode_property("queue-time", types.DATETIME)
