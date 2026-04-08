import argparse

def get_parser():
    parser = argparse.ArgumentParser(description="IOL - Intelligent OS Layer")
    parser.add_argument("--config", type=str, default="config_example.yaml", help="Path to config file")
    parser.add_argument("--dry-run", action="store_true", help="Do not actually modify processes")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    return parser
