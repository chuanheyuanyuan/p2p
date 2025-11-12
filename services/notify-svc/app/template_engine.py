import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

from jinja2 import Environment, StrictUndefined


class TemplateError(Exception):
    """Base class for template related failures."""


class TemplateNotFoundError(TemplateError):
    pass


class ChannelNotSupportedError(TemplateError):
    pass


class MissingTemplateVariableError(TemplateError):
    def __init__(self, missing: List[str]):
        super().__init__(f'Missing template variables: {", ".join(missing)}')
        self.missing = missing


@dataclass
class TemplateDefinition:
    key: str
    description: str
    channels: List[str]
    required_variables: List[str]
    body_variants: Dict[str, str]
    locale: str
    category: str

    def body_for_channel(self, channel: str) -> str:
        if channel in self.body_variants:
            return self.body_variants[channel]
        if 'default' in self.body_variants:
            return self.body_variants['default']
        raise ChannelNotSupportedError(f'channel "{channel}" is not configured for template {self.key}')


class TemplateStore:
    def __init__(self, path: Path):
        self.path = path
        self._env = Environment(undefined=StrictUndefined, autoescape=False)
        self._templates = self._load()

    def _load(self) -> Dict[str, TemplateDefinition]:
        if not self.path.exists():
            raise FileNotFoundError(f'Template catalog not found at {self.path}')
        with self.path.open('r', encoding='utf-8') as fp:
            raw = json.load(fp)
        catalog: Dict[str, TemplateDefinition] = {}
        for key, value in raw.items():
            catalog[key] = TemplateDefinition(
                key=key,
                description=value.get('description', ''),
                channels=value.get('channels', []),
                required_variables=value.get('requiredVariables', []),
                body_variants=value.get('bodies', {}),
                locale=value.get('locale', 'en_GH'),
                category=value.get('category', 'system'),
            )
        return catalog

    def reload(self) -> None:
        self._templates = self._load()

    def get(self, key: str) -> TemplateDefinition:
        try:
            return self._templates[key]
        except KeyError as exc:
            raise TemplateNotFoundError(f'template "{key}" not found') from exc

    def render(self, template_key: str, channel: str, variables: Dict[str, Any]) -> str:
        definition = self.get(template_key)
        if channel not in definition.channels:
            raise ChannelNotSupportedError(f'template "{template_key}" does not support channel "{channel}"')
        variables = variables or {}
        missing = [var for var in definition.required_variables if var not in variables]
        if missing:
            raise MissingTemplateVariableError(missing)
        template_str = definition.body_for_channel(channel)
        template = self._env.from_string(template_str)
        return template.render(**variables)

    def required_variables(self, template_key: str) -> List[str]:
        definition = self.get(template_key)
        return definition.required_variables

    def channels(self, template_key: str) -> List[str]:
        definition = self.get(template_key)
        return definition.channels
