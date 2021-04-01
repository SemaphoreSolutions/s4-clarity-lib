# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from ._internal import ClarityElement

from six import BytesIO, StringIO, string_types

import logging
import os

from . import ETree
from ._internal.props import subnode_property
from .exception import FileNotFoundException
from s4.clarity import types

log = logging.getLogger(__name__)


class File(ClarityElement):
    """
    This is a file in Clarity. It is also a Python file (more or less).
    You can read, write, and do everything else you can normally do with a Python file.
    NOTE: nothing will be committed to Clarity until you call close, or commit.
    """

    UNIVERSAL_TAG = "{http://genologics.com/ri/file}file"

    def __init__(self, lims, uri=None, xml_root=None, name=None, limsid=None):
        super(File, self).__init__(lims, uri, xml_root, name, limsid)
        self._data = None
        self._dirty = False
        self.content_type = 'text/plain'
        self.writeable = True
        self.only_write_locally = False
        self.mode = "r"

    @classmethod
    def new_empty(cls, attachment_point_element, name=None):
        """
        Create a new empty :class:`File`.

        :param attachment_point_element: An element to attach the file to.
        :type attachment_point_element: ClarityElement
        :param name: A name for the file.
        :type name: str
        :rtype: File
        """
        root = ETree.Element(cls.UNIVERSAL_TAG)

        f = File(uri=None, xml_root=root, lims=attachment_point_element.lims)
        if name is not None:
            f.name = name
        f.attached_to = attachment_point_element.uri
        return f

    @classmethod
    def new_from_local(cls, attachment_point_element, local_file_path, mode="r+b"):
        """
        Create a new :class:`File` from a local file.

        :param attachment_point_element: An element to attach the file to.
        :type attachment_point_element: ClarityElement
        :param local_file_path: Path to the local file.
        :type local_file_path: str
        :param mode: Mode to open the file with.
        :type mode: str
        :rtype: File
        """
        root = ETree.Element(cls.UNIVERSAL_TAG)

        f = File(uri=None, xml_root=root, lims=attachment_point_element.lims)

        f.name = local_file_path
        f.attached_to = attachment_point_element.uri
        f._data = open(local_file_path, mode)
        f._dirty = True

        return f

    name = subnode_property('original-location')
    attached_to = subnode_property('attached-to')
    content_location = subnode_property('content-location')
    is_published = subnode_property('is-published', typename=types.BOOLEAN)

    @property
    def is_binary_mode(self):
        """
        :type: bool
        """
        return "b" in self.mode

    def pipe_to(self, target_file_object):
        """
        :raises FileNotFoundException: if the file does not exist in Clarity.
        """
        response = self.lims.raw_request('GET', self.uri + '/download')
        self.content_type = response.headers.get("Content-Type")

        if self.is_binary_mode:
            file_contents = response.content
        else:
            file_contents = response.content if isinstance(response.content, string_types) else response.text

        target_file_object.write(file_contents)

    def replace_and_commit_from_local(self, local_file_path, content_type='text/plain', mode="r+b"):
        self.mode = mode
        other_file = open(local_file_path, self.mode)
        self.replace_and_commit(other_file, local_file_path, content_type)
        other_file.close()

    def replace_and_commit(self, stream, name, content_type='text/plain'):
        if not self.writeable:
            raise Exception("file not writeable")
        self.name = name
        self.data.write(stream.read())
        self.content_type = content_type
        self._dirty = True
        self.commit()

    @property
    def data(self):
        """
        :return: The file data IO stream.
        :rtype:  io.IOBase
        """
        if self._data is None:
            if self.only_write_locally:
                pathstrippedname = os.path.basename(self.name)
                if os.path.exists(self.name):
                    file_name = self.name
                else:
                    file_name = pathstrippedname

                self._data = open(file_name, self.mode)
            else:
                self._data = BytesIO() if self.is_binary_mode else StringIO()

            if self.uri is not None:
                try:
                    log.debug("Getting file contents from lims...")

                    # convenient!
                    self.pipe_to(self._data)
                    self._data.seek(0)

                except FileNotFoundException:
                    log.debug("File not found at %s" % self.uri)

                    # this is ok, we just leave the buffer empty.
                    # uri = None means we will need a new uri, later, allocated through glsstorage.
                    self.uri = None

        return self._data

    # Implementation for standard io.IOBase methods to support being used as a file:
    def read(self, n=-1):
        return self.data.read(n)

    def readline(self, length=None):
        return self.data.readline(length)

    def readlines(self, sizehint=0):
        return self.data.readlines(sizehint)

    def write(self, s):
        if not self.writeable:
            raise Exception("file not writeable")

        self._dirty = True
        return self.data.write(s)

    def writelines(self, iterable):
        if not self.writeable:
            raise Exception("file not writeable")

        self._dirty = True
        return self.data.writelines(iterable)

    def flush(self):
        # don't do anything at all
        return

    def getvalue(self):
        return self.data.getvalue()

    def truncate(self, size=None):
        if not self.writeable:
            raise Exception("file not writeable")

        self._dirty = True

        if size is None and self._data is None:
            self._data = BytesIO() if self.is_binary_mode else StringIO()
        else:
            self._data.truncate(size)

    def tell(self):
        return self.data.tell()

    def isatty(self):
        return False

    def close(self):
        """
        Commit the file and close the data stream.
        """
        self.commit()
        return self.data.close()

    def __iter__(self):
        return self.data.__iter__()

    def seek(self, pos, mode=0):
        return self.data.seek(pos, mode)

    def readable(self):
        return self.data.readable()

    def writable(self):
        return self.data.writable()

    def seekable(self):
        return self.data.seekable()

    # end file-like functions

    def seek_to_end(self):
        return self.data.seek(0, 2)

    def commit(self):
        if not self.writeable or self._data is None:
            return

        if self.only_write_locally:
            self._data.flush()
            return

        if self.name is None:
            raise Exception("Value for .name required.")

        if self.uri is not None:
            # If we are overwriting an existing file, first delete to
            # allow name to be changed.
            self.lims.raw_request('DELETE', self.uri)
            self.uri = None

        # first we get an allocation from glsstorage
        self.post_and_parse(self.lims.root_uri + '/glsstorage')

        # then we post ourselves to files, which gives us a uri.
        self.post_and_parse(self.lims.root_uri + '/files')

        if self._dirty:
            old_pos = self.data.tell()
            self.data.seek(0)
            self.lims.raw_request('POST', self.uri + '/upload',
                                  files={'file': (self.name, self.data, self.content_type)}
                                  )
            self._dirty = False
            self.data.seek(old_pos)
