"""Main entry point for the project."""


from typing import NoReturn


def greet(name: str) -> str:
    """Return a greeting message.

    Args:
        name: The name to greet.

    Returns:
        A formatted greeting string.
    """
    return f"Hello, {name}!"


def main() -> int:
    """Run the main program.

    Returns:
        Exit status code.
    """
    try:
        from src.config_loader import ConfigError, load_config
        from sys import argv

        if len(argv) != 2:
            print(
                "Error: expected exactly one argument "
                f"(got {len(argv) - 1})\n"
                "Usage: python3 pac-man.py <config.json>"
            )
            return 1

        try:
            config = load_config(argv[1])
        except ConfigError as error:
            print(f"Error: {error}")
            return 1

        print(config)
        return 0
    except KeyboardInterrupt:
        return 1
    except Exception as error:
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
