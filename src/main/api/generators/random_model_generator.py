import random
import uuid
from datetime import datetime, timedelta
from typing import (Annotated, Any, Callable, get_args, get_origin,
                    get_type_hints)

import rstr

from src.main.api.generators.generating_rule import GeneratingRule


class RandomModelGenerator:
    @staticmethod
    def generate(cls_model: type) -> Any:
        type_hints = get_type_hints(cls_model, include_extras=True)
        init_data = {}

        for field_name, annotated_type in type_hints.items():
            rule = None
            actual_type = annotated_type

            if get_origin(annotated_type) is Annotated:
                actual_type, *annotations = get_args(annotated_type)
                for ann in annotations:
                    if isinstance(ann, GeneratingRule):
                        rule = ann
            if rule:
                value = RandomModelGenerator._generate_from_regex(rule.regex, actual_type)
            else:
                value = RandomModelGenerator._generate_value(actual_type)

            init_data[field_name] = value

        return cls_model(**init_data)

    @staticmethod
    def _generate_from_regex(regex: str, field_type: type) -> Any:
        generated = rstr.xeger(regex)
        if field_type is int:
            return int(generated)
        if field_type is float:
            return float(generated)
        return generated

    @staticmethod
    def _generate_value(field_type: type) -> Any:
        generators: dict[type, Callable[[], Any]] = {
            str: lambda: str(uuid.uuid4())[:8],
            int: lambda: random.randint(0, 1000),
            float: lambda: round(random.uniform(0, 100.0), 2),
            bool: lambda: random.choice([True, False]),
            datetime: lambda: datetime.now() - timedelta(seconds=random.randint(0, 100000)),
            list: lambda: [str(uuid.uuid4())[:5] for _ in range(random.randint(3, 10))],
        }

        if isinstance(field_type, type) and field_type not in generators:
            return RandomModelGenerator.generate(field_type)

        generator = generators.get(field_type, lambda: None)
        return generator()
