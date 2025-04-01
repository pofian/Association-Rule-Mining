from parse_dataset import read_donors
from parse_rules import read_rules
from utils import Rule
from utils import Donor
from utils import Condition


first_write = True
def is_subrule_of(smaller_rule, bigger_rule) -> bool:
    if not smaller_rule.matching_donors.issubset(bigger_rule.matching_donors):
        return False
    
    filename = 'logs/subset_removed_rules.txt'
    try:
        with open(filename, 'a', encoding='utf-8') as file:
            global first_write
            if first_write:
                file.truncate(0)
                first_write = False
            file.write(f"First rule is a subset of the second rule ----- will be discarded.\
            \n{smaller_rule}\n{bigger_rule}\n\n")
    except Exception as e:
        print(f"Error writing to {filename}: {e}")
    return True

def merge_rules(rules):
    i = 0
    while i < len(rules):
        j = i + 1
        while j < len(rules):
            if (is_subrule_of(rules[j], rules[i])):
                del rules[j]
            else:
                j += 1
        i += 1


phi_threshold = 0.2
precision_threshold = 0.5
max_rules_count = 1000

def log_removed_rules(removed_rules):
    filename = 'logs/threshold_removed_rules.txt'
    try:
        with open(filename, 'w', encoding='utf-8') as file:
            for rule in removed_rules:
                s = f"Rule '{rule.__repr__conditions__()}' will be discarded because "
                text1 = None if rule.phi >= phi_threshold else f"phi = {rule.phi} < {phi_threshold}"
                text2 = None if rule.precision >= precision_threshold else f"precision = {rule.precision} < {precision_threshold}"
                if text1 is not None:
                    s += text1
                if text2 is not None:
                    if text1 is not None:
                        s += " AND "
                    s += text2
                s += '\n'
                file.write(s)
    except Exception as e:
        print(f"Error writing to {filename}: {e}")


def filter_rules(rules, donors):
    for rule in rules:
        rule.evaluate(donors)

    removed_rules = [rule for rule in rules if rule.phi  < phi_threshold  or rule.precision  < precision_threshold]
    rules =         [rule for rule in rules if rule.phi >= phi_threshold and rule.precision >= precision_threshold]
    log_removed_rules(removed_rules)

    rules = sorted(rules, key=lambda rule: rule.phi, reverse=True)
    rules = rules[:max_rules_count]
    merge_rules(rules)

    return rules


def generate_synthetic_rules(attributes):
    possible_conditions = []
    synthetic_rules = []
    for variable in attributes:
        for negated in [False, True]:
            possible_conditions.append(Condition(variable, negated))

    n = len(possible_conditions)
    for i in range(0, n + 1):
        for j in range(i + 1, n + 1):
            for k in range(j + 1, n + 1):
                pc1 = possible_conditions[i] if i != n else None
                pc2 = possible_conditions[j] if j != n else None
                pc3 = possible_conditions[k] if k != n else None
                conditions = [x for x in [pc1, pc2, pc3] if x is not None]
                rule = Rule(n, conditions)
                synthetic_rules.append(rule)

    return synthetic_rules


def main():
    print("program start..\n")

    rules = read_rules()
    (attributes, donors) = read_donors()

    rules = filter_rules(rules, donors)

    try:
        with open('compressed_rules.txt', 'w', encoding='utf-8') as f:
            for rule in rules:
                f.write(str(rule) + '\n')
    except Exception as e:
        print(f"An error occurred: {e}")

    # print('\n' + "#" * 100 + '\n')
    # synthetic_rules = generate_synthetic_rules(attributes)
    # synthetic_rules = filter_rules(synthetic_rules, donors)
    # for rule in synthetic_rules:
    #     print(rule)


if __name__ == "__main__":
    main()
