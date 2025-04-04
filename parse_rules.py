from utils import Rule
from utils import Condition
from typing import List

n = 0
def rule_from_line(line) -> Rule:
    line = line.strip()
    if not line:
        return None  # Skip empty lines

    parts = line.split(" => ")
    if len(parts) != 2:
        print(f"Warning: Invalid rule format: {line}")
        return None

    conditions_str, result = parts # result is 'donor_is_old'
    conditions = []

    # Split conditions by " AND "
    for condition_str in conditions_str.split(" AND "):
        condition_str = condition_str.strip()
        negated = False
        if condition_str.startswith("NOT "):
            negated = True
            condition_str = condition_str[4:].strip()

        conditions.append(Condition(condition_str, negated))

    global n
    n += 1
    return Rule(n, conditions) 



file_path = "rules.txt"
def read_rules(file_path = file_path) -> List[Rule]:
    """
    Reads and interprets rules from a file, returning a list of dictionaries.

    Args:
        file_path (str): The path to the file containing the rules.

    Returns:
        list: A list of dictionaries, where each dictionary represents a rule.
    """
    rules = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                rule = rule_from_line(line)
                if rule is not None:
                    rules.append(rule)
        # for rule in rules:
        #     print(rule)
        return rules
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

