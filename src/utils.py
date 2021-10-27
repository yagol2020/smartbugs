from solidity_parser import parser
from src.logger import logs
from typing import Dict


def merge_two_dicts(x: Dict, y: Dict):
    """Given two dictionaries, merge them into a new dict as a shallow copy."""
    z = x.copy()
    z.update(y)
    return z


def get_solc_version(file: str):
    """
    get solidity compiler version
    """
    try:
        with open(file, 'r', encoding='utf-8') as fd:
            sourceUnit = parser.parse(fd.read())
            solc_version = sourceUnit['children'][0]['value']
            solc_version = solc_version.strip('^')
            solc_version = solc_version.split('.')
            return (int(solc_version[1]), int(solc_version[2]))
    except:
        logs.print(
            '\x1b[1;33m' + 'WARNING: could not parse solidity file to get solc version' + '\x1b[0m',
            'WARNING: could not parse solidity file to get solc version')
    return (None, None)
