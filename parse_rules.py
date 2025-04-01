from parse_dataset import read_donors
import re

def interpret_rules(file_path):
    """
    Reads and interprets rules from a file, returning a list of dictionaries.

    Args:
        file_path (str): The path to the file containing the rules.

    Returns:
        list: A list of dictionaries, where each dictionary represents a rule.
    """
    rules = []
    n = 1
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue  # Skip empty lines

                parts = line.split(" => ")
                if len(parts) != 2:
                    print(f"Warning: Invalid rule format: {line}")
                    continue

                conditions_str, result = parts
                conditions = []

                # Split conditions by " AND "
                for condition_str in conditions_str.split(" AND "):
                    condition_str = condition_str.strip()
                    negated = False
                    if condition_str.startswith("NOT "):
                        negated = True
                        condition_str = condition_str[4:].strip()

                    conditions.append({"variable": condition_str, "negated": negated})

                rules.append({"id": n, "conditions": conditions, "result": result})
                n += 1

        return rules

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def evaluate_rule(rule, data):
    for condition in rule["conditions"]:
        variable = condition["variable"]
        negated = condition["negated"]

        if variable not in data:
          return False #if a required variable is missing, the rule can not be evaluated.

        # print(data[variable])
        # print(type(data[variable]))
        if negated:
            if data[variable] == 'FALSE': #if negated, and the variable is true, the rule fails.
                # print('same')
                return False
        else:
            if data[variable] == 'TRUE': #if not negated, and the variable is false, the rule fails.
                # print('same')
                return False

    return True #all conditions were met.


def main():
    file_path = "rules.txt"  # Replace with your file path
    rules = interpret_rules(file_path)
    
    # print(rules)
    donors = read_donors()
    bad_rules = []

    # print(donors)
    for rule in rules:
        count_old = 0
        count_young = 0
        for donor in donors:
            # print("\n\n\n\nDONOR\n")
            # print(donor)
            # exit(0)
            if (evaluate_rule(rule, donor['atrributes'])):
                # print(f"{rule['result']} + {donor['donor_is_old']}")
                if (donor['donor_is_old']):
                    count_old += 1
                else:
                    count_young += 1
                # pass
        a = count_old
        b = count_old + count_young
        if b == 0:
            # print(f"bad rule {rule['id']}")
            bad_rules.append(rule)
            continue

        if (a != b):
            print(f"{a}/{b} ({100 * a / b})% for rule {rule['id']}")
            raise ExceptionType("This rule doesn't satisfy all requirements")
        
        rule['count'] = a

    rules = [rule for rule in rules if rule not in bad_rules]
    # print(rules)
    rules = sorted(rules, key=lambda x: x['count'], reverse=True)
    for rule in rules:
        # print(rule['count'])
        print(rule)

main()