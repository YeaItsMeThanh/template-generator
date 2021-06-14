from logging import getLogger
from typing import *

import onlinejudge_template.analyzer.codeforces
import onlinejudge_template.analyzer.constants
import onlinejudge_template.analyzer.html
import onlinejudge_template.analyzer.minimum_tree
import onlinejudge_template.analyzer.output_types
import onlinejudge_template.analyzer.parser
import onlinejudge_template.analyzer.simple_patterns
import onlinejudge_template.analyzer.topcoder
import onlinejudge_template.analyzer.typing
import onlinejudge_template.analyzer.variables
from onlinejudge_template.types import *

logger = getLogger(__name__)


def prepare_from_html(html: bytes, *, url: str, sample_cases: Optional[List[SampleCase]] = None) -> AnalyzerResources:
    input_format_string: Optional[str] = None
    try:
        input_format_string = onlinejudge_template.analyzer.html.parse_input_format_string(html, url=url)
        logger.debug('input format string: %s', repr(input_format_string))
    except AnalyzerError as e:
        logger.info('failed to detect the input format string: %s', e)
    except NotImplementedError as e:
        logger.debug('The detection of input format strings is not supported for this problem: %s', e)

    output_format_string: Optional[str] = None
    try:
        output_format_string = onlinejudge_template.analyzer.html.parse_output_format_string(html, url=url)
        logger.debug('output format string: %s', repr(output_format_string))
    except AnalyzerError as e:
        logger.info('failed to detect the output format string: %s', e)
    except NotImplementedError as e:
        logger.debug('The detection of output format strings is not supported for this problem: %s', e)

    resources = AnalyzerResources(
        url=url,
        html=html,
        input_format_string=input_format_string,
        output_format_string=output_format_string,
        sample_cases=sample_cases,
    )
    return resources


def run(resources: AnalyzerResources) -> AnalyzerResult:

    # It seems that topcoder_class_definition should be included in resources.
    topcoder_class_definition: Optional[TopcoderClassDefinition] = None
    try:
        if resources.url is not None and onlinejudge_template.analyzer.topcoder.is_topcoder_url(resources.url):
            if resources.html is not None:
                topcoder_class_definition = onlinejudge_template.analyzer.topcoder.parse_topcoder_class_definition(resources.html, url=resources.url)
    except AnalyzerError as e:
        logger.exception('failed to analyze the class definition of the Topcoder problem: %s', e)

    multiple_test_cases = False
    try:
        if resources.url is not None and onlinejudge_template.analyzer.codeforces.is_codeforces_url(resources.url):
            if resources.html is not None:
                multiple_test_cases = onlinejudge_template.analyzer.codeforces.has_multiple_testcases(resources.html, url=resources.url)
                if multiple_test_cases:
                    logger.info('Each input of this problem has multiple test cases.')
    except AnalyzerError as e:
        logger.exception('failed to decide wheter the Codeforces problem has multiple test cases: %s', e)

    # parse the format tree for input
    input_format: Optional[FormatNode] = None
    try:
        if resources.input_format_string is not None:
            input_format = onlinejudge_template.analyzer.parser.run(resources.input_format_string)
        elif topcoder_class_definition is not None:
            input_format = onlinejudge_template.analyzer.topcoder.convert_topcoder_class_definition_to_input_format(topcoder_class_definition)
    except AnalyzerError as e:
        logger.info('failed to parse the input format string: %s', e)
    try:
        if input_format is None and resources.sample_cases:
            input_samples = [case.input.decode() for case in resources.sample_cases]
            if not multiple_test_cases:
                input_format = onlinejudge_template.analyzer.simple_patterns.guess_format_with_pattern_matching(instances=input_samples)
            if input_format is None:
                input_format = onlinejudge_template.analyzer.minimum_tree.construct_minimum_input_format_tree(instances=input_samples, multiple_test_cases=multiple_test_cases)
    except AnalyzerError as e:
        logger.info('failed to analyze the input format from the input sample cases: %s', e)
    if input_format is None:
        logger.info('failed to analyze the input format: all analyzers failed')

    # list the variables for input
    input_variables: Optional[Dict[VarName, VarDecl]] = None
    try:
        if resources.input_format_string is None and topcoder_class_definition is not None:
            input_variables = onlinejudge_template.analyzer.topcoder.convert_topcoder_class_definition_to_input_variables(topcoder_class_definition)

        elif input_format is not None:
            input_variables = onlinejudge_template.analyzer.variables.list_declared_variables(input_format)
            if input_format is not None and input_variables is not None and resources.sample_cases:
                input_samples = [case.input.decode() for case in resources.sample_cases]
                input_types = onlinejudge_template.analyzer.typing.infer_types_from_instances(input_format, variables=input_variables, instances=input_samples)
                input_variables = onlinejudge_template.analyzer.typing.update_variables_with_types(variables=input_variables, types=input_types)
    except AnalyzerError as e:
        logger.info('failed to list variables in the input format: %s', e)

    # parse the format tree for output
    output_format: Optional[FormatNode] = None
    try:
        if resources.output_format_string is not None:
            output_format = onlinejudge_template.analyzer.parser.run(resources.output_format_string)
        elif topcoder_class_definition is not None:
            output_format = onlinejudge_template.analyzer.topcoder.convert_topcoder_class_definition_to_output_format(topcoder_class_definition)
    except AnalyzerError as e:
        logger.info('failed to parse the output format string: %s', e)
    try:
        if output_format is None and resources.sample_cases:
            if input_format is not None and input_variables is not None:
                if not multiple_test_cases:
                    output_format = onlinejudge_template.analyzer.simple_patterns.guess_output_format_with_pattern_matching_using_input_format(instances=resources.sample_cases, input_format=input_format, input_variables=input_variables)
                if output_format is None:
                    output_format = onlinejudge_template.analyzer.minimum_tree.construct_minimum_output_format_tree_using_input_format(instances=resources.sample_cases, input_format=input_format, input_variables=input_variables, multiple_test_cases=multiple_test_cases)
            else:
                output_samples = [case.output.decode() for case in resources.sample_cases]
                output_format = onlinejudge_template.analyzer.simple_patterns.guess_format_with_pattern_matching(instances=output_samples)
                if output_format is None:
                    output_format = onlinejudge_template.analyzer.minimum_tree.construct_minimum_output_format_tree(instances=output_samples)
    except AnalyzerError as e:
        logger.info('failed to analyze the output format from the sample cases: %s', e)
    if output_format is None:
        logger.info('failed to analyze the output format: all analyzers failed')

    # list the variables for output
    output_variables: Optional[Dict[VarName, VarDecl]] = None
    try:
        if resources.output_format_string is None and topcoder_class_definition is not None:
            output_variables = onlinejudge_template.analyzer.topcoder.convert_topcoder_class_definition_to_output_variables(topcoder_class_definition)

        elif output_format is not None:
            output_variables = onlinejudge_template.analyzer.variables.list_declared_variables(output_format)
            if output_format is not None and output_variables is not None and resources.sample_cases:
                output_samples = [case.output.decode() for case in resources.sample_cases]
                output_types = onlinejudge_template.analyzer.typing.infer_types_from_instances(output_format, variables=output_variables, instances=output_samples)
                output_variables = onlinejudge_template.analyzer.typing.update_variables_with_types(variables=output_variables, types=output_types)
    except AnalyzerError as e:
        logger.info('failed to list variables in the output format: %s', e)

    # list constants
    constants: Dict[VarName, ConstantDecl] = {}
    try:
        if resources.html is not None or resources.sample_cases:
            constants.update(onlinejudge_template.analyzer.constants.list_constants(html=resources.html, sample_cases=resources.sample_cases))
    except AnalyzerError as e:
        logger.exception('failed to list used constants: %s', e)

    # simplify the output format
    output_type: Optional[OutputType] = None
    try:
        if output_format is not None and output_variables is not None:
            output_type = onlinejudge_template.analyzer.output_types.analyze_output_type(output_format=output_format, output_variables=output_variables, constants=constants)
    except AnalyzerError as e:
        logger.info('failed to analyze the type of the output format: %s', e)

    return AnalyzerResult(
        resources=resources,
        input_format=input_format,
        output_format=output_format,
        input_variables=input_variables,
        output_variables=output_variables,
        constants=constants,
        output_type=output_type,
        topcoder_class_definition=topcoder_class_definition,
    )


def get_empty_analyzer_result(resources: AnalyzerResources) -> AnalyzerResult:
    return AnalyzerResult(
        resources=resources,
        input_format=None,
        output_format=None,
        input_variables=None,
        output_variables=None,
        constants={},
        output_type=None,
        topcoder_class_definition=None,
    )
