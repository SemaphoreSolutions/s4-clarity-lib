# Copyright 2017 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from .factory import ElementFactory, NoMatchingElement


class UdfFactory(ElementFactory):
    _udfs_by_attach_to_key = {}

    def _query_uri_and_tag(self):
        return self.lims.root_uri + "/configuration/udfs", "udfconfig"

    def get_by_name(self, udf_name, attach_to_key):
        """
        :type udf_name: str
        :type attach_to_key: (str, str)
        :param attach_to_key: tuple comprising the element's attach-to-name and attach-to-category properties
        :return: s4.clarity.configuration.Udf
        :raises NoMatchingElement: if no match
        """
        udfs_for_attach_to_key = self._get_udfs_by_attach_to_key(attach_to_key)

        udf = udfs_for_attach_to_key.get(udf_name)

        if not udf:
            raise NoMatchingElement("UDF with name: '%s', attach-to-name: '%s', and attach-to-category: '%s' could not "
                            "be retrieved." % (udf_name, attach_to_key[0], attach_to_key[1]))

        return udf

    def _get_udfs_by_attach_to_key(self, attach_to_key):
        udfs_for_attach_to_key = self._udfs_by_attach_to_key.get(attach_to_key)

        if not udfs_for_attach_to_key:
            udfs = self.query(prefetch=False,
                              **{"attach-to-name": attach_to_key[0],
                                 "attach-to-category" :attach_to_key[1]})
            udfs_for_attach_to_key = dict((udf.name, udf) for udf in udfs)
            self._udfs_by_attach_to_key[attach_to_key] = udfs_for_attach_to_key

        return udfs_for_attach_to_key
