# Copyright 2016 Semaphore Solutions, Inc.
# ---------------------------------------------------------------------------

from unittest import TestCase
from mock import patch, Mock, MagicMock, PropertyMock
from six import assertCountEqual

from s4.clarity.step import Step
from s4.clarity.artifact import Artifact
from s4.clarity.scripts.stepepp import StepEPP


class TestStepEPP(TestCase):

    @patch("s4.clarity.LIMS")
    def test_prefetch(self, mock_lims):
        stepepp = SomeStepEPP(FakeOptions)

        inputs = [Mock(Artifact, name='Input A'),
            Mock(Artifact, name='Input B'),
            Mock(Artifact, name='Input C')]

        outputs = [Mock(Artifact, name='Output A'),
            Mock(Artifact, name='Output B'),
            Mock(Artifact, name='Output C')]

        samples = ["sample0", "sample1", "sample2"]
        for i in range(len(inputs)):
            inputs[i].sample = samples[i]
            outputs[i].sample = samples[i]

        stepepp.step = MagicMock(Step)
        type(stepepp.step.details).inputs = PropertyMock(return_value=inputs)
        type(stepepp.step.details).outputs = PropertyMock(return_value=outputs)

        self.assertRaises(ValueError, lambda: stepepp.prefetch('junk'))

        def assert_fetches(arguments, should_fetch_artifacts, should_fetch_samples):
            stepepp.prefetch(*arguments)

            if should_fetch_artifacts:
                actual_artifacts = stepepp.lims.artifacts.batch_fetch.call_args[0][0]
                assertCountEqual(self, should_fetch_artifacts, actual_artifacts)
                stepepp.lims.artifacts.batch_fetch.reset_mock()
            else:
                stepepp.lims.artifacts.batch_fetch.assert_not_called()

            if should_fetch_samples:
                actual_samples = stepepp.lims.samples.batch_fetch.call_args[0][0]
                assertCountEqual(self, should_fetch_samples, actual_samples)
                stepepp.lims.samples.batch_fetch.reset_mock()
            else:
                stepepp.lims.samples.batch_fetch.assert_not_called()

        assert_fetches(['inputs'], inputs, None)
        assert_fetches(['outputs'], outputs, None)
        assert_fetches(['inputs', 'outputs'], inputs + outputs, None)

        assert_fetches(['samples'], inputs, samples)
        assert_fetches(['inputs', 'samples'], inputs, samples)
        assert_fetches(['outputs', 'samples'], outputs, samples)

        assert_fetches(['inputs', 'outputs', 'samples'], inputs + outputs, samples)



class SomeStepEPP(StepEPP):

    def run(self):
        pass


class FakeOptions(object):
    username = 'a_username'
    password = 'a_password'
    lims_root_uri = 'some.example.com'
    step_uri = 'some_step_uri'
    dry_run = False
    insecure = False
