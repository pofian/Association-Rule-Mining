from parse_dataset import read_donors
from parse_rules import read_rules
from utils import Rule
from utils import Donor
from utils import Condition
from typing import List


def log_merged_rules(merged_rules: List[tuple[Rule, Rule]]) -> None:
    filename = 'logs/subset_removed_rules.txt'
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            for pair in merged_rules:
                smaller_rule: Rule = pair[0]
                bigger_rule: Rule = pair[1]
                file.write("First rule is a subset of the second rule ----- will be discarded.\n" \
                    + str(smaller_rule) + '\n' + str(bigger_rule) + '\n\n')
                # print(pair[0])
    except Exception as e:
        print(f"Error writing to {filename}: {e}")

def merge_rules(rules: List[Rule]) -> None:
    i = 0
    merged_rules = []
    while i < len(rules):
        j = i + 1
        while j < len(rules):
            if rules[j].is_subrule_of(rules[i]):
                merged_rules.append([rules[j], rules[i]])
                del rules[j]
            else:
                j += 1
        i += 1
    log_merged_rules(merged_rules)


def log_removed_rules(removed_rules: List[Rule]) -> None:
    filename = 'logs/threshold_removed_rules.txt'
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            for rule in removed_rules:
                s = f"Rule '{rule}'\nwill be discarded because "
                s += rule.discard_threshold_message()
                s += '\n\n'
                file.write(s)
    except Exception as e:
        print(f"Error writing to {filename}: {e}")


def generate_synthetic_rules(attributes: List[str]) -> List[Rule]:
    possible_conditions = []
    synthetic_rules = []
    for variable in attributes:
        for negated in [False, True]:
            possible_conditions.append(Condition(variable, negated))

    n = len(possible_conditions)
    for i in range(0, n):
        for j in range(i, n):
            for k in range(j if i == j else j + 1, n):
                s = {i, j, k}   # All unique subsets of {0, 1, 2, ... n - 1} of lenght 1, 2 or 3
                conditions = [possible_conditions[index] for index in s]
                rule = Rule(n, conditions)
                synthetic_rules.append(rule)

    return synthetic_rules


padding_lenght = 81
def log_compressed_rules(rules: List[Rule]) -> None:
    try:
        with open('compressed_rules.txt', 'w', encoding='utf-8') as f, \
            open('compressed_rules_detailed.txt', 'w', encoding='utf-8') as g:
            g.write('.' * padding_lenght)
            g.write(' |  phi |  precision   | sensitivity |\n')
            for rule in rules:
                f.write(str(rule) + '\n')
                g.write(rule.__str__detailed__(padding_lenght) + '\n')
    except Exception as e:
        print(f"An error occurred: {e}")


max_rules_count = 50
def filter_rules(rules: List[Rule], donors: List[Donor]) -> List[Rule]:
    for rule in rules:
        rule.evaluate(donors)

    removed_rules = [rule for rule in rules if not rule.test_thresholds()]
    rules =         [rule for rule in rules if rule not in removed_rules]
    log_removed_rules(removed_rules)

    rules = sorted(rules, key=lambda rule: rule.phi, reverse=True)
    merge_rules(rules)
    rules = rules[:max_rules_count]
    return rules


def main(*argv):
    (attributes, donors) = read_donors()

    rules: List[Rule]
    if len(argv) == 2 and argv[1] == 'synthetic':
        rules = generate_synthetic_rules(attributes)
    else:
        rules = read_rules()

    rules = filter_rules(rules, donors)
    log_compressed_rules(rules)


from sys import argv
if __name__ == "__main__":
    main(*argv)
