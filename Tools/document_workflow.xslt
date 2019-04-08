<?xml version="1.0" encoding="utf-8"?>
<!-- Copyright 2016 Semaphore Solutions, Inc. -->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:msxsl="urn:schemas-microsoft-com:xslt" exclude-result-prefixes="msxsl"
    xmlns:wkfcnf="http://genologics.com/ri/workflowconfiguration"
    xmlns:protcnf="http://genologics.com/ri/protocolconfiguration"
    xmlns:ptm="http://genologics.com/ri/processtemplate"
    xmlns:ptp="http://genologics.com/ri/processtype"
  >
  <xsl:output method="html" indent="yes"/>

  <xsl:template match="/config">
    <HTML>
      <HEAD>
        <script type='text/javascript' src='http://code.jquery.com/jquery-1.9.1.js'></script>
        <script type='text/javascript'>
          //<![CDATA[
$(window).load(function(){
$(".header").click(function () {

    $header = $(this);
    $header.toggleClass("open")
    //getting the next element
    $content = $header.next();
    //open up the content needed - toggle the slide- if visible, slide up, if not slidedown.
    $content.slideToggle(500, function () {
        //execute this after slideToggle is done
        });

});
});//]]>

        </script>
        <style type='text/css'>
          .content {
          padding-left : 20px;
          }
          .header.open:before {
            content:"-"
          }
          .header:before {
            content:"+"
          }
          code {
            white-space: pre;
          }
        </style>

      </HEAD>
      <BODY>
        <xsl:for-each select="Workflows/wkfcnf:workflow">
          <H1 class="header open">
            Workflow - <xsl:value-of select="@name"/>
          </H1>
          <div class="content">
            <xsl:for-each select="protocols/protocol">
              <xsl:variable name="protocolName" select="@name"/>
              <H2 class="header">
                Protocol - <xsl:value-of select="$protocolName"/>
              </H2>
              <div class="content" style="display:none">
                <xsl:for-each select="/config/Protocols/protcnf:protocol[@name=$protocolName]">
                  <xsl:for-each select="steps/step">
                    <xsl:variable name="processName" select="process-type/text()"/>
                    <xsl:variable name="processType" select="/config/ProcessTypes/ptp:process-type[@name=$processName]"/>
                    <H3 class="header">
                      Step - <xsl:value-of select="@name"/>
                    </H3>
                    <div class="content" style="display:none">
                      <xsl:for-each select="$processType/process-output[output-generation-type='PerInput']">
                        Per Analyte Output: "<xsl:value-of select="display-name"/>" (<xsl:value-of select="artifact-type"/>) <xsl:if test="number-of-outputs > 1">
                          *<xsl:value-of select="number-of-outputs"/>
                        </xsl:if>
                        Name: <xsl:value-of select="output-name"/><BR/>
                        <xsl:call-template name="optional_list">
                          <xsl:with-param name="title">Fields</xsl:with-param>
                          <xsl:with-param name="list" select="field-definition/@name"/>
                        </xsl:call-template>
                      </xsl:for-each>
                      <xsl:for-each select="$processType/process-output[output-generation-type='PerReagentLabel']">
                        Per Reagent Label Output: "<xsl:value-of select="display-name"/>" (<xsl:value-of select="artifact-type"/>) <xsl:if test="number-of-outputs > 1">
                          *<xsl:value-of select="number-of-outputs"/>
                        </xsl:if>
                        Name: <xsl:value-of select="output-name"/><BR/>
                        <xsl:call-template name="optional_list">
                          <xsl:with-param name="title">Fields</xsl:with-param>
                          <xsl:with-param name="list" select="field-definition/@name"/>
                        </xsl:call-template>
                      </xsl:for-each>
                      <xsl:for-each select="$processType/process-output[output-generation-type='PerAllInputs']">
                        Shared Output: <xsl:value-of select="output-name"/><BR/>
                        <xsl:call-template name="optional_list">
                          <xsl:with-param name="title">Fields</xsl:with-param>
                          <xsl:with-param name="list" select="field-definition/@name"/>
                        </xsl:call-template>
                      </xsl:for-each>
                      <H4>Queue View</H4>
                      <P>Columns</P>
                      <UL>
                        <xsl:for-each select="queue-fields/queue-field[@detail='false']">
                          <LI>
                            <xsl:value-of select="concat(@name, ' (', @attach-to, ')')"/>
                          </LI>
                        </xsl:for-each>
                      </UL>
                      <xsl:if test="queue-fields/queue-field[@detail='true']">
                        <P>Details</P>
                        <UL>
                          <xsl:for-each select="queue-fields/queue-field[@detail='true']">
                            <LI>
                              <xsl:value-of select="concat(@name, ' (', @attach-to, ')')"/>
                            </LI>
                          </xsl:for-each>
                        </UL>
                      </xsl:if>
                      <P>
                        Group By: <xsl:value-of select="default-grouping"/>
                      </P>

                      <xsl:call-template name="optional_list">
                        <xsl:with-param name="title">Available Control Samples</xsl:with-param>
                        <xsl:with-param name="list" select="permitted-control-types/control-type/@name"/>
                      </xsl:call-template>

                      <H4>Ice Bucket</H4>

                      <xsl:call-template name="optional_list">
                        <xsl:with-param name="title">Destination Containers</xsl:with-param>
                        <xsl:with-param name="list" select="permitted-containers/container-type"/>
                      </xsl:call-template>
                      <xsl:call-template name="optional_epp">
                        <xsl:with-param name="point">AFTER</xsl:with-param>
                        <xsl:with-param name="status">STARTED</xsl:with-param>
                        <xsl:with-param name="processType" select="$processType"/>
                      </xsl:call-template>

                      <H4>Placement</H4>
                      <xsl:call-template name="optional_list">
                        <xsl:with-param name="title">Required Reagent Kits</xsl:with-param>
                        <xsl:with-param name="list" select="required-reagent-kits/reagent-kit/@name"/>
                      </xsl:call-template>
                      <xsl:call-template name="optional_epp">
                        <xsl:with-param name="point">BEFORE</xsl:with-param>
                        <xsl:with-param name="status">PLACEMENT</xsl:with-param>
                        <xsl:with-param name="processType" select="$processType"/>
                      </xsl:call-template>
                      <xsl:call-template name="optional_epp">
                        <xsl:with-param name="point">AFTER</xsl:with-param>
                        <xsl:with-param name="status">PLACEMENT</xsl:with-param>
                        <xsl:with-param name="processType" select="$processType"/>
                      </xsl:call-template>
                      <H4>Add Reagents</H4>
                      <xsl:call-template name="optional_list">
                        <xsl:with-param name="title">Permitted Reagent Categories</xsl:with-param>
                        <xsl:with-param name="list" select="permitted-reagent-categories/reagent-category"/>
                      </xsl:call-template>
                      <xsl:call-template name="optional_epp">
                        <xsl:with-param name="point">BEFORE</xsl:with-param>
                        <xsl:with-param name="status">ADD_REAGENTS</xsl:with-param>
                        <xsl:with-param name="processType" select="$processType"/>
                      </xsl:call-template>
                      <xsl:call-template name="optional_epp">
                        <xsl:with-param name="point">AFTER</xsl:with-param>
                        <xsl:with-param name="status">ADD_REAGENTS</xsl:with-param>
                        <xsl:with-param name="processType" select="$processType"/>
                      </xsl:call-template>
                      <H4>Record Details</H4>
                      <xsl:call-template name="optional_list">
                        <xsl:with-param name="title">Step Fields</xsl:with-param>
                        <xsl:with-param name="list" select="step-fields/step-field/@name"/>
                      </xsl:call-template>
                      <P>Sample Columns</P>
                      <UL>
                        <xsl:for-each select="sample-fields/sample-field">
                          <LI>
                            <xsl:value-of select="concat(@name, ' (', @attach-to, ')')"/>
                          </LI>
                        </xsl:for-each>
                      </UL>
                      <xsl:call-template name="optional_epp">
                        <xsl:with-param name="point">BEFORE</xsl:with-param>
                        <xsl:with-param name="status">RECORD_DETAILS</xsl:with-param>
                        <xsl:with-param name="processType" select="$processType"/>
                      </xsl:call-template>
                      <xsl:call-template name="manual_epp">
                        <xsl:with-param name="point">BEFORE</xsl:with-param>
                        <xsl:with-param name="status">RECORD_DETAILS</xsl:with-param>
                        <xsl:with-param name="processType" select="$processType"/>
                      </xsl:call-template>
                      <xsl:call-template name="optional_epp">
                        <xsl:with-param name="point">AFTER</xsl:with-param>
                        <xsl:with-param name="status">RECORD_DETAILS</xsl:with-param>
                        <xsl:with-param name="processType" select="$processType"/>
                      </xsl:call-template>
                      <H4>Next Steps</H4>
                      <UL>
                        <xsl:for-each select="transitions/transition">
                          <LI>
                            <xsl:value-of select="@name"/>
                          </LI>
                        </xsl:for-each>
                      </UL>
                      <xsl:call-template name="optional_epp">
                        <xsl:with-param name="point">BEFORE</xsl:with-param>
                        <xsl:with-param name="status">COMPLETE</xsl:with-param>
                        <xsl:with-param name="processType" select="$processType"/>
                      </xsl:call-template>
                    </div>
                  </xsl:for-each>
                </xsl:for-each>
              </div>
            </xsl:for-each>
          </div>
        </xsl:for-each>
      </BODY>
    </HTML>
  </xsl:template>

  <xsl:template name="optional_comma_separated">
    <xsl:param name="title"/>
    <xsl:param name="list"/>
    <xsl:if test="$list">
      <P>
        <xsl:value-of select="$title"/>:
        <xsl:for-each select="$list">
          <xsl:if test="position()!=1">, </xsl:if>
          <xsl:value-of select ="."/>
        </xsl:for-each>
      </P>
    </xsl:if>
  </xsl:template>

  <xsl:template name="optional_list">
    <xsl:param name="title"/>
    <xsl:param name="list"/>
    <xsl:if test="$list">
      <P>
        <xsl:value-of select="$title"/>:
      </P>
      <UL>
        <xsl:for-each select="$list">
          <LI>
            <xsl:value-of select ="."/>
          </LI>
        </xsl:for-each>
      </UL>
    </xsl:if>
  </xsl:template>

  <xsl:template name="optional_epp">
    <xsl:param name="status"/>
    <xsl:param name="point"/>
    <xsl:param name ="processType"/>
    <xsl:for-each select="epp-triggers/epp-trigger[@status=$status and @point=$point]">
      <P>
        <xsl:value-of select="concat(@point, ' ', @status, ' ', @name)"/>
      </P>
      <code>
        <xsl:variable name="eppName" select="@name"/>
        <xsl:value-of select="$processType/parameter[@name=$eppName]/string"/>
      </code>
    </xsl:for-each>
  </xsl:template>

  <xsl:template name="manual_epp">
    <xsl:param name ="processType"/>
    <xsl:for-each select="epp-triggers/epp-trigger[@type='MANUAL']">
      <P>
        <xsl:value-of select="concat('Button ', @name)"/>
      </P>
      <code>
        <xsl:variable name="eppName" select="@name"/>
        <xsl:value-of select="$processType/parameter[@name=$eppName]/string"/>
      </code>
    </xsl:for-each>
  </xsl:template>

</xsl:stylesheet>
