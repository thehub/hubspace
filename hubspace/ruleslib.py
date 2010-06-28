import hubspace.model as model
import hubspace.invoice as invoicelib
import hubspace.utilities.permissions as permissionslib
from sqlobject import AND

class ConditionGrammerCheckFailed(Exception): pass

rule_order = {model.Invoice: [model.TaxExemptionRule]}
object_hash = lambda obj: obj.__class__.__name__ + '.' + str(obj.id)

def db_load_rules(rules_processor):
    on_type = rules_processor.on_type
    for_object = rules_processor.for_object
    rule_select = tuple(rule for rule in model.Rule.selectBy(for_object=object_hash(for_object)) if rule.on_type == on_type)
    sorter = lambda rule: rule_order[on_type].index(rule.__class__)
    rules = sorted (rule_select, key=sorter)
    return rules

class RulesProcessor(object):
    def __init__(self, on_type, for_object):
        self.on_type = on_type
        self.for_object = for_object
    def load_rules(self):
        return db_load_rules(self)
    def process(self, on_object, value):
        rules = self.load_rules()
        for rule in rules:
            value = rule.apply(on_object, value)
        return value

def get_rule_for_object(rule_cls, for_object):
    select = list(rule_cls.selectBy(for_object=object_hash(for_object)))
    if select:
        return select[0]

# EUVE = EU Tax Exemption
def find_locations_with_euve():
    return [rule.for_object for rule in model.TaxExemptionRule.select() if rule.enabled]

def find_locations_available_to_user_for_euve(user):
    return [loc for loc in permissionslib.user_locations(user, levels=['member']) if loc in find_locations_with_euve()]

def is_euve_enabled(location):
    rule = get_rule_for_object(model.TaxExemptionRule, location)
    return rule and rule.enabled

#from hubspace.ruleslib import *
#
#location = Location.get(1)
#rule = TaxExemptionRule(enabled=True, for_object=location)
#invoice = Invoice.get(123)
#invoices_rules = RulesProcessor(Invoice, invoice.location)
#value = dict(rusages_cost_and_tax=invoice.rusages_cost_and_tax, total_tax=invoice.total_tax, amount=invoice.amount, resource_tax_dict=invoice.resource_tax_dict)
#print invoices_rules.process(invoice, value)
#
#print find_locations_with_euve()
#print find_locations_available_to_user_for_euve(invoice.user)
#
