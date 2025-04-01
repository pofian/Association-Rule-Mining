import math

# https://en.wikipedia.org/wiki/Phi_coefficient
def mean_square_contingency_coefficient(true_positives, false_positives, true_negatives, false_negatives):
    """
    Calculates the mean square contingency coefficient (Phi coefficient).
    """
    numerator = (true_positives * true_negatives) - (false_positives * false_negatives)
    denominator = math.sqrt((true_positives + false_positives) *
                            (true_negatives + false_negatives) *
                            (true_positives + false_negatives) *
                            (true_negatives + false_positives))
    return float('-inf') if denominator == 0 else numerator / denominator


class Rule:
    def __init__(self, id, condition):
        self.id: int = id
        self.conditions: list[Condition] = condition

    def test(self, donor_attributes):
        test_result = True

        for condition in self.conditions:
            result = condition.test(donor_attributes)
            if result is False:
                return False
            if result == 'NA':
                test_result = 'NA'

        return test_result

    def evaluate(self, donors):
        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0

        matching_donors = set()
        for donor in donors:
            test = self.test(donor.attributes)
            if test == 'NA':
                continue # Will ignore for now

            match (test, donor.is_old):
                case (True, True):
                    true_positives += 1
                    matching_donors.add(donor.id)
                case (True, False):
                    false_positives += 1
                case (False, True):
                    false_negatives += 1
                case (False, False):
                    true_negatives += 1
                    matching_donors.add(donor.id)

        phi = mean_square_contingency_coefficient(true_positives, false_positives, true_negatives, false_negatives)
        self.phi = round(phi, 3)
        self.matching_donors = matching_donors

        if true_positives + false_positives == 0:
            self.precision = -1
        else:
            precision = true_positives / (true_positives + false_positives)
            self.precision = round(precision, 3)

    def __repr__conditions__(self):        
        s: string = ""
        for i, condition in enumerate(self.conditions):
            if i != 0:
                s += " AND "
            if condition.negated:
                s += "NOT "
            s += condition.variable

        s += " => donor_is_old"
        return s

    def __repr__(self):
        repr = self.__repr__conditions__() + ' '
        repr += '.' * (85 - len(repr))
        if hasattr(self, 'phi') and hasattr(self, 'precision'):
            repr += f" phi: {self.phi} precision: {self.precision}"
        return repr



class Condition:
    def __init__(self, variable, negated):
        self.variable: str = variable
        self.negated: bool = negated

    def test(self, donor_attributes):
        if self.variable not in donor_attributes:
            return False #if a required variable is missing, the rule can not be evaluated.

        if donor_attributes[self.variable] == 'NA':
            return 'NA'

        return donor_attributes[self.variable] is not self.negated


    def __repr__(self):
        return self.variable if not self.negated else f"NOT {self.variable}"


class Donor:
    def __init__(self, id, attributes, row):
        self.id: int = id
        self.is_old = True if row[0] == 'TRUE' else False
        self.attributes = {attribute: Donor.process_attribute_value(value) for attribute, value in zip(attributes[1:], row[1:])}

    @staticmethod
    def process_attribute_value(attribute: str):
        match attribute:
            case 'TRUE':
                return True
            case 'FALSE':
                return False
            case _:
                return 'NA'