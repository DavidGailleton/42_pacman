"""Game configuration model with validation and safe defaults."""

from typing import Annotated, Any

from pydantic import (
    BaseModel,
    Field,
    StrictInt,
    StrictStr,
    ValidationError,
    ValidationInfo,
    ValidatorFunctionWrapHandler,
    field_validator,
    model_validator,
)

# Allowed maze side length, in cells. Adjust once the A-Maze-ing
# package's own limits are known.
MazeSide = Annotated[StrictInt, Field(ge=10, le=100)]


class LevelConfig(BaseModel):
    """Maze size of one level, in cells.

    Unknown keys inside a level entry are ignored.
    """

    width: MazeSide
    height: MazeSide


# Used when 'levels' is missing or invalid: 10 levels, as the subject
# asks for at least 10.
DEFAULT_LEVELS: list[LevelConfig] = [
    LevelConfig(width=21, height=21) for _ in range(10)
]


class Config(BaseModel):
    """Validated game configuration.

    Every field has a safe default. A missing or invalid value is
    replaced by that default and a warning is printed, so a faulty
    config file never stops the game. Unknown keys are ignored.

    Strict types are used so that JSON values of the wrong type
    (e.g. ``"3"`` or ``true`` for a number) are rejected instead of
    being silently converted.
    """

    highscore_filename: StrictStr = Field(
        default="highscores.json", min_length=1
    )
    # One entry per level, played in order. Never empty.
    levels: list[LevelConfig] = Field(default=DEFAULT_LEVELS, min_length=1)
    lives: StrictInt = Field(default=3, ge=1, le=99)
    point_per_pacgum: StrictInt = Field(default=10, ge=0)
    point_per_super_pacgum: StrictInt = Field(default=50, ge=0)
    point_per_ghost: StrictInt = Field(default=200, ge=0)
    seed: StrictInt = 42
    level_max_time: StrictInt = Field(default=90, ge=1)

    @model_validator(mode="before")
    @classmethod
    def _warn_missing_keys(cls, data: Any) -> Any:
        """Check the top-level type and report keys that are missing.

        Args:
            data: Raw value decoded from the JSON file.

        Returns:
            The data to validate (an empty dict if it was not an object).
        """
        if not isinstance(data, dict):
            print(
                "Warning: config root must be a JSON object, "
                "using default values for everything"
            )
            return {}
        for name, field in cls.model_fields.items():
            if name not in data:
                print(
                    f"Warning: missing key '{name}', "
                    f"using default {field.default!r}"
                )
        return data

    @field_validator("*", mode="wrap")
    @classmethod
    def _fallback_to_default(
        cls,
        value: Any,
        handler: ValidatorFunctionWrapHandler,
        info: ValidationInfo,
    ) -> Any:
        """Validate one field, falling back to its default if invalid.

        Args:
            value: Raw value read from the config file.
            handler: Pydantic's normal validation for this field
                (type and range checks).
            info: Context of the validation, used to get the field name.

        Returns:
            The validated value, or the field's default if it is invalid.
        """
        try:
            return handler(value)
        except ValidationError as error:
            name: str = info.field_name or ""
            default: Any = cls.model_fields[name].default
            reason: str = error.errors()[0]["msg"]
            print(
                f"Warning: invalid value {value!r} for '{name}' "
                f"({reason}), using default {default!r}"
            )
            return default
