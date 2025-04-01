from parse_dataset import read_donors
from parse_rules import read_rules


def test_rule_on_donor(rule, donor_atributes):
    for condition in rule["conditions"]:
        variable = condition["variable"]
        negated = condition["negated"]

        if variable not in donor_atributes:
            return False #if a required variable is missing, the rule can not be evaluated.

        # print(donor_atributes[variable])
        # print(type(donor_atributes[variable]))
        if negated:
            if donor_atributes[variable] == 'TRUE': #if negated, and the variable is true, the rule fails.
                return False
        else:
            if donor_atributes[variable] == 'FALSE': #if not negated, and the variable is false, the rule fails.
                return False

    return True #all conditions were met.

def is_subrule_of(smaller_rule, bigger_rule) -> bool:
    if (smaller_rule['matching_donors'].issubset(bigger_rule['matching_donors'])):
        # print(f"Rule: \n{smaller_rule} \
        #                 \nis subset of rule:\n{bigger_rule}\n")
        return True
    return False

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


import math

# https://en.wikipedia.org/wiki/Phi_coefficient
def mean_square_contingency_coefficient(true_positives, false_positives, true_negatives, false_negatives):
    """
    Calculates the mean square contingency coefficient (Phi coefficient).

    Returns:
        float: The mean square contingency coefficient (Phi coefficient).
    """
    numerator = (true_positives * true_negatives) - (false_positives * false_negatives)
    denominator = math.sqrt((true_positives + false_positives) *
                            (true_negatives + false_negatives) *
                            (true_positives + false_negatives) *
                            (true_negatives + false_positives))

    return float('-inf') if denominator == 0 else numerator / denominator


def evaluate_rule(rule, donors):
    true_positives = 0
    false_positives = 0
    true_negatives = 0
    false_negatives = 0

    matching_donors = set()
    for donor in donors:
        if (test_rule_on_donor(rule, donor['atrributes'])):
            if (donor['donor_is_old'] == 'TRUE'):
                true_positives += 1
                matching_donors.add(donor['id'])
            else:
                false_positives += 1
        else:
            if (donor['donor_is_old'] == 'TRUE'):
                false_negatives += 1
            else:
                true_negatives += 1

    # print(f"{true_positives} {false_positives} {true_negatives} {false_negatives}")

    phi = mean_square_contingency_coefficient(true_positives, false_positives, true_negatives, false_negatives)
    rule['phi'] = round(phi, 4)
    rule['matching_donors'] = matching_donors

    if true_positives + false_positives == 0:
        rule['precision'] = -1
    else:
        rule['precision'] = round(true_positives / (true_positives + false_positives), 4)


def text(conditions):
    s: string = ""
    for i, condition in enumerate(conditions):
        if i != 0:
            s += " AND "
        if condition['negated']:
            s += "NOT "
        s += condition['variable']

    s += " => donor_is_old"
    return s

phi_threshold = 0.15
def filter_rules(rules, donors):
    for rule in rules:
        evaluate_rule(rule, donors)

    rules = [rule for rule in rules if rule['phi'] > phi_threshold]
    rules = sorted(rules, key=lambda x: x['phi'], reverse=True)
    merge_rules(rules)
    for rule in rules:
        del rule['matching_donors']
        del rule['id']
        rule['conditions'] = text(rule['conditions'])

    return rules


def main():
    print("program start..................\n")

    rules = read_rules()
    (attributes, donors) = read_donors()

    old_donors_count  = len([donor for donor in donors if donor['donor_is_old'] == 'TRUE'])
    young_donor_count = len([donor for donor in donors if donor['donor_is_old'] == 'FALSE'])

    rules = filter_rules(rules, donors)
    for rule in rules:
        # print()
        print(rule)

    # print(attributes)

    n = 100

    synthetic_rules = []
    for variable in attributes:
        for negated in [False, True]:
            n += 1
            conditions = [{"variable": variable, "negated": negated}]
            rule = {"id": n, "conditions": conditions, "result": "donor_is_old"}
            synthetic_rules.append(rule)
    
    print('\n' + "#" * 100 + '\n')

    synthetic_rules = filter_rules(synthetic_rules, donors)
    for rule in synthetic_rules:
        # print()
        print(rule)
        pass


    

main()
