# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------
from __future__ import division
import math
import logging

log = logging.getLogger(__name__)

# MAD constant reason: http://www.itl.nist.gov/div898/handbook/eda/section3/eda35h.htm
MADCONSTANT = 1.48258


def find_dilution_factor(iomap, outputdilutionudf, inputdilutionudf):
    dilutions = list(filter(None, [output.get(outputdilutionudf) for output in iomap.outputs]))
    if len(dilutions) != 0:
        if calculatecv(dilutions) != 0:
            log.warning("%s's outputs have different dilution factors; choosing the largest.", iomap.input)
        return max(dilutions)
    else:
        log.info("%s's outputs have no dilution factors; checking for previously set one.", iomap.input)
        return iomap.input.get(inputdilutionudf)


def compute_average(epp, sourceudf, averageudf, excludeudf, cvudf, outputdilutionudf=None, inputdilutionudf=None):
    log.info("Calculating averages.")
    for iomap in epp.step.details.iomaps:
        includedsources = [output[sourceudf] for output in iomap.outputs if not output.get(excludeudf) == True]
        if len(includedsources) == 0:
            iomap.input[cvudf] = 100
            iomap.input[averageudf] = 0
        else:
            iomap.input[cvudf] = calculatecv(includedsources)
            iomap.input[averageudf] = sum(includedsources) / len(includedsources)
            if outputdilutionudf is not None and inputdilutionudf is not None:
                dilution_factor = find_dilution_factor(iomap, outputdilutionudf, inputdilutionudf)
                if dilution_factor is not None:
                    iomap.input[inputdilutionudf] = dilution_factor
                    iomap.input[averageudf] *= iomap.input[inputdilutionudf]

            log.info("%s average set to %.3f and %% CV set to %.3f.",
                         iomap.input,
                         iomap.input[averageudf],
                         iomap.input[cvudf])
    epp.lims.artifacts.batch_update(epp.step.details.inputs)
    log.info("Completed average calculation.")


def discard_outliers(epp, sourceudf, excludeudf, cvthreshold, madthreshold):
    log.info("Calculating outliers.")
    for iomap in epp.step.details.iomaps:

        # if 'exclude' was already set by xls parsing, leave it and continue to next iomap
        # so we don't clobber the exlusion already set to mark dropped samples to be skipped
        if all([output.get(excludeudf, None) for output in iomap.outputs]):
            continue

        includedsources = sorted([output[sourceudf] for output in iomap.outputs])
        if calculatecv(includedsources) < cvthreshold:
            for output in iomap.outputs:
                output[excludeudf] = False
        else:
            medianofsources = median(includedsources)
            medianabsolutedeviation = median([abs(source - medianofsources) for source in includedsources])
            exclusionthresholdcalculated = medianabsolutedeviation * madthreshold * MADCONSTANT
            for output in iomap.outputs:
                if abs(output[sourceudf] - medianofsources) > exclusionthresholdcalculated:
                    output[excludeudf] = True
                    log.info("%s with value of %.3f excluded.",
                                 output,
                                 output[sourceudf])
                else:
                    output[excludeudf] = False
    epp.lims.artifacts.batch_update(epp.step.details.outputs)
    log.info("Completed outlier calculation.")


def calculatecv(lst):
    if len(lst) <= 1:
        return 0
    mean = sum(lst) / len(lst)
    if mean == 0:
        return 0
    standarddeviation = math.sqrt(sum([math.pow(source - mean, 2) for source in lst]) / (len(lst) - 1))
    return (standarddeviation / mean) * 100


def median(lst):
    if len(lst) < 1:
        return None

    lst = sorted(lst)
    if len(lst) % 2 == 1:
        return lst[((len(lst) + 1) // 2) - 1]
    else:
        return sum(lst[(len(lst) // 2) - 1:(len(lst) // 2) + 1]) / 2
