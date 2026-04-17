"""
This module makes it possible to instantiate a new Troposphere Template object
from an existing CloudFormation Template.

Usage:
    from troposphere.template_generator import TemplateGenerator
    import json

    with open("myCloudFormationTemplate.json") as f:
        json_template = json.load(f)

    template = TemplateGenerator(json_template)
    template.to_json()
"""

import importlib
import inspect
import os
import pkgutil
from collections.abc import Mapping, Sequence

from troposphere import AWSObject  # covers resources
from troposphere import GenericHelperFn  # covers ref, fn::, etc
from troposphere import Parameter  # AWSDeclarations
from troposphere import (
    AWSHelperFn,
    Cidr,
    Export,
    GetAZs,
    Output,
    Ref,
    Split,
    Tags,
    Template,
    autoscaling,
    cloudformation,
)
from troposphere.policies import CreationPolicy, UpdatePolicy

AWS_LIST_RETURN_FUNCTIONS = (Cidr, GetAZs, Split)


class TemplateGenerator(Template):
    DEPRECATED_MODULES = ["troposphere.dynamodb2"]
    EXCLUDE_MODULES = DEPRECATED_MODULES + [
        "troposphere.openstack.heat",
        "troposphere.openstack.neutron",
        "troposphere.openstack.nova",
    ]

    _inspect_members = set()  # type: ignore
    _inspect_resources = {}  # type: ignore
    _custom_members = set()  # type: ignore
    _inspect_functions = {}  # type: ignore

    def __init__(self, cf_template, **kwargs):
        """
        Instantiates a new Troposphere Template based on an existing
        Cloudformation Template.
        """
        super().__init__()
        if "CustomMembers" in kwargs:
            self._custom_members = set(kwargs["CustomMembers"])

        self._reference_map = {}
        if "AWSTemplateFormatVersion" in cf_template:
            self.set_version(cf_template["AWSTemplateFormatVersion"])
        if "Transform" in cf_template:
            self.set_transform(cf_template["Transform"])
        if "Description" in cf_template:
            self.set_description(cf_template["Description"])
        if "Metadata" in cf_template:
            self.set_metadata(cf_template["Metadata"])
        for k, v in cf_template.get("Parameters", {}).items():
            self.add_parameter(self._create_instance(Parameter, v, k))
        for k, v in cf_template.get("Mappings", {}).items():
            self.add_mapping(k, self._convert_definition(v))
        for k, v in cf_template.get("Conditions", {}).items():
            self.add_condition(k, self._convert_definition(v, k))
        for k, v in cf_template.get("Resources", {}).items():
            self.add_resource(
                self._convert_definition(v, k, self._get_resource_type_cls(k, v))
            )
        for k, v in cf_template.get("Outputs", {}).items():
            self.add_output(self._create_instance(Output, v, k))

    @property
    def inspect_members(self):
        """
        Returns the list of all troposphere members we are able to
        construct
        """
        pass

    @property
    def inspect_resources(self):
        """Returns a map of `ResourceType: ResourceClass`"""
        pass

    @property
    def inspect_functions(self):
        """Returns a map of `FunctionName: FunctionClass`"""
        pass

    def _get_resource_type_cls(self, name, resource):
        """Attempts to return troposphere class that represents Type of
        provided resource. Attempts to find the troposphere class who's
        `resource_type` field is the same as the provided resources `Type`
        field.

        :param resource: Resource to find troposphere class for
        :return: None: If no class found for provided resource
                 type: Type of provided resource
        :raise ResourceTypeNotDefined:
                  Provided resource does not have a `Type` field
        """
        pass

    def _convert_definition(self, definition, ref=None, cls=None):
        """
        Converts any object to its troposphere equivalent, if applicable.
        This function will recurse into lists and mappings to create
        additional objects as necessary.

        :param {*} definition: Object to convert
        :param str ref: Name of key in parent dict that the provided definition
                        is from, can be None
        :param type cls: Troposphere class which represents provided definition
        """
        pass

    def _create_instance(self, cls, args, ref=None):
        """
        Returns an instance of `cls` with `args` passed as arguments.

        Recursively inspects `args` to create nested objects and functions as
        necessary.

        `cls` will only be considered only if it's an object we track
         (i.e.: troposphere objects).

        If `cls` has a `props` attribute, nested properties will be
         instanciated as troposphere Property objects as necessary.

        If `cls` is a list and contains a single troposphere type, the
         returned value will be a list of instances of that type.
        """
        pass

    def _normalize_properties(self, definition):
        """
        Inspects the definition and returns a copy of it that is updated
        with any special property such as Condition, UpdatePolicy and the
        like.
        """
        pass

    def _generate_custom_type(self, resource_type):
        """
        Dynamically allocates a new CustomResource class definition using the
        specified Custom::SomeCustomName resource type. This special resource
        type is equivalent to the AWS::CloudFormation::CustomResource.
        """
        pass

    def _generate_autoscaling_metadata(self, cls, args):
        """Provides special handling for the autoscaling.Metadata object"""
        pass

    def _get_function_type(self, function_name):
        """
        Returns the function object that matches the provided name.
        Only Fn:: and Ref functions are supported here so that other
        functions specific to troposphere are skipped.
        """
        pass

    def _import_all_troposphere_modules(self):
        """Imports all troposphere modules and returns them"""
        pass


class ResourceTypeNotFound(Exception):
    def __init__(self, resource, resource_type):
        Exception.__init__(
            self, "ResourceType not found for " + resource_type + " - " + resource
        )
        self.resource_type = resource_type
        self.resource = resource


class ResourceTypeNotDefined(Exception):
    def __init__(self, resource):
        Exception.__init__(self, "ResourceType not defined for " + resource)
        self.resource = resource
