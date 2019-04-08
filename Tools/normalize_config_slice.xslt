<?xml version="1.0" encoding="UTF-8"?>
<!--
Copyright 2018 Semaphore Solutions, Inc.

Normalize config slice to allow files to be compared across time and machines.
Avoids spurious difference by ensuring that all elements are canonically ordered.

To use (Mac):
"xsltproc -o [normalized config slice output] normalize_config_slice.xslt [raw config slice] "

"raw config slice" and "normalized config slice" cannot be the same file.
-->
<xsl:stylesheet version="1.0"
                xmlns:cnf="http://genologics.com/ri/configuration"
                xmlns:ptp="http://genologics.com/ri/processtype"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">


    <xsl:output omit-xml-declaration="yes" method="xml" encoding="utf-8" indent="yes"
                version="1.0" />
    <xsl:strip-space elements="*"/>

    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()" />
        </xsl:copy>
    </xsl:template>

    <!--Config Slicer sorts these items by their internal id, which is the order-->
    <!--they were entered into the system. We would like it if they were alphabetical-->
    <!--so that we can easily compare files to see the differences-->
    <xsl:template match="process-output">
        <xsl:copy>
            <xsl:apply-templates select="@*" />
            <xsl:apply-templates select="node()[not(self::field-definition)]" />
            <xsl:apply-templates select="field-definition">
                <xsl:sort select="@name" data-type="text" order="ascending" />
            </xsl:apply-templates>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="SampleUDFs|ProcessTypeUDFs">
        <xsl:copy>
            <xsl:apply-templates select="@*" />
            <xsl:apply-templates select="cnf:field">
                <xsl:sort select="attach-to-name" data-type="text" order="ascending" />
                <!--Sort case insensitive-->
                <xsl:sort select="translate(name, 'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ')"
                          data-type="text" order="ascending" />
            </xsl:apply-templates>
        </xsl:copy>
    </xsl:template>

    <xsl:template match="ptp:process-type">
        <xsl:copy>
            <xsl:apply-templates select="@*" />
            <xsl:apply-templates select="field-definition">
                <xsl:sort select="@name" data-type="text" order="ascending" />
            </xsl:apply-templates>
            <xsl:apply-templates select="parameter">
                <xsl:sort select="@name" data-type="text" order="ascending" />
            </xsl:apply-templates>
            <xsl:apply-templates select="node()[not(self::field-definition|self::parameter)]" />
        </xsl:copy>
    </xsl:template>

    <xsl:template match="epp-triggers|Protocols">
        <xsl:copy>
            <xsl:apply-templates select="@*" />
            <xsl:apply-templates select="node()">
                <xsl:sort select="@name" data-type="text" order="ascending" />
            </xsl:apply-templates>
        </xsl:copy>
    </xsl:template>

</xsl:stylesheet>