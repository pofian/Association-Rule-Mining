from __future__ import annotations
from typing import List
import math


class Rule:
    phi_threshold = 0.2
    precision_threshold = 0.5
    sensitivity_threshold = 0.35

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

    @staticmethod
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

    def evaluate(self, donors: List[Donor]):
        true_positives = 0
        false_positives = 0
        true_negatives = 0
        false_negatives = 0

        matching_donors = set()
        na_donors = set()
        for donor in donors:
            test = self.test(donor.attributes)
            if test == 'NA':
                # na_donors.add(donor.id)
                # continue
                test = donor.is_old

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
                    # matching_donors.add(-donor.id)

        phi = Rule.mean_square_contingency_coefficient(true_positives, false_positives, true_negatives, false_negatives)
        self.phi = round(phi, 2)
        self.matching_donors = matching_donors
        if na_donors:
            self.na_donors = na_donors

        if true_positives + false_positives == 0:
            self.precision_stats = (0, 0)
            self.precision = 0
            self.sensitivity = 0
        else:
            self.precision_stats = (true_positives, true_positives + false_positives)
            precision = true_positives / (true_positives + false_positives)
            sensitivity = true_positives / (true_positives + false_negatives)
            self.precision = round(precision, 2)
            self.sensitivity = round(sensitivity, 2)


    def test_thresholds(self) -> bool:
        return  self.phi > Rule.phi_threshold \
            and self.precision > Rule.precision_threshold \
            and self.sensitivity > Rule.sensitivity_threshold
    
    def discard_threshold_message(self) -> str:
        text1 = None if self.phi > Rule.phi_threshold else f"phi = {self.phi} <= {Rule.phi_threshold}"
        text2 = None if self.precision > Rule.precision_threshold else f"precision = {self.precision} <= {Rule.precision_threshold}"
        text3 = None if self.sensitivity > Rule.sensitivity_threshold else f"sensitivity = {self.sensitivity} <= {Rule.sensitivity_threshold}"
        text = None
        for t in [text1, text2, text3]:
            if t is None:
                continue
            if text is None:
                text = t
            else:
                text += " and " + t
        return text

    def is_subrule_of(self, bigger_rule: Rule) -> bool:
        return self.matching_donors.issubset(bigger_rule.matching_donors)

    def __str__(self):        
        s: str = ""
        for i, condition in enumerate(self.conditions):
            if i != 0:
                s += " AND "
            if condition.negated:
                s += "NOT "
            s += condition.variable

        s += " => donor_is_old"
        return s

    def __str__detailed__(self, padding_lenght):
        s = self.__str__() + ' '
        s += '.' * (padding_lenght - len(s))
        if hasattr(self, 'phi'):
            s += f" | {self.phi:.2f} | {self.precision:.2f} " + \
                f"({self.precision_stats[0]:02d}/{self.precision_stats[1]:02d}) |    {self.sensitivity:.2f}     |"
        return s



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