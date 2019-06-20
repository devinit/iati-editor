from lxml import etree
import pandas as pd
from collections import OrderedDict

XPATH_SEPERATOR = "/"
ATTRIB_SEPERATOR = "@"
EXCLUDED_CHILDREN_TAGS = ["budget", "transaction"]
SORT_ORDER = {
    "iati-activities/iati-activity": 0,
    "iati-activity/iati-identifier": 1,
    "iati-activity/reporting-org": 2,
    "reporting-org/narrative": 3,
    "iati-activity/title": 4,
    "title/narrative": 5,
    "iati-activity/description": 6,
    "description/narrative": 7,
    "iati-activity/participating-org": 8,
    "participating-org/narrative": 9,
    "iati-activity/other-identifier": 10,
    "iati-activity/activity-status": 11,
    "iati-activity/activity-date": 12,
    "activity-date/narrative": 13,
    "iati-activity/contact-info": 14,
    "contact-info/organisation": 15,
    "organisation/narrative": 16,
    "contact-info/department": 17,
    "department/narrative": 18,
    "contact-info/person-name": 19,
    "person-name/narrative": 20,
    "contact-info/job-title": 21,
    "job-title/narrative": 22,
    "contact-info/telephone": 23,
    "contact-info/email": 24,
    "contact-info/website": 25,
    "contact-info/mailing-address": 26,
    "mailing-address/narrative": 27,
    "iati-activity/activity-scope": 28,
    "iati-activity/recipient-country": 29,
    "recipient-country/narrative": 30,
    "iati-activity/recipient-region": 31,
    "recipient-region/narrative": 32,
    "iati-activity/location": 33,
    "location/location-reach": 34,
    "location/location-id": 35,
    "location/name": 36,
    "name/narrative": 37,
    "location/description": 38,
    "location/activity-description": 39,
    "activity-description/narrative": 40,
    "location/administrative": 41,
    "location/point": 42,
    "point/pos": 43,
    "location/exactness": 44,
    "location/location-class": 45,
    "location/feature-designation": 46,
    "iati-activity/sector": 47,
    "sector/narrative": 48,
    "iati-activity/country-budget-items": 49,
    "country-budget-items/budget-item": 50,
    "budget-item/description": 51,
    "iati-activity/policy-marker": 52,
    "policy-marker/narrative": 53,
    "iati-activity/collaboration-type": 54,
    "iati-activity/default-flow-type": 55,
    "iati-activity/default-finance-type": 56,
    "iati-activity/default-aid-type": 57,
    "iati-activity/default-tied-status": 58,
    "iati-activity/budget": 59,
    "budget/period-start": 60,
    "budget/period-end": 61,
    "budget/value": 62,
    "iati-activity/planned-disbursement": 63,
    "planned-disbursement/period-start": 64,
    "planned-disbursement/period-end": 65,
    "planned-disbursement/value": 66,
    "iati-activity/capital-spend": 67,
    "iati-activity/transaction": 68,
    "transaction/transaction-type": 69,
    "transaction/transaction-date": 70,
    "transaction/value": 71,
    "transaction/description": 72,
    "transaction/provider-org": 73,
    "provider-org/narrative": 74,
    "transaction/receiver-org": 75,
    "receiver-org/narrative": 76,
    "transaction/disbursement-channel": 77,
    "transaction/sector": 78,
    "transaction/recipient-country": 79,
    "transaction/recipient-region": 80,
    "transaction/flow-type": 81,
    "transaction/finance-type": 82,
    "transaction/aid-type": 83,
    "transaction/tied-status": 84,
    "iati-activity/document-link": 85,
    "document-link/title": 86,
    "document-link/category": 87,
    "document-link/language": 88,
    "iati-activity/related-activity": 89,
    "iati-activity/legacy-data": 90,
    "iati-activity/conditions": 91,
    "conditions/condition": 92,
    "condition/narrative": 93,
    "iati-activity/result": 94,
    "result/title": 95,
    "result/description": 96,
    "result/indicator": 97,
    "indicator/title": 98,
    "indicator/description": 99,
    "indicator/baseline": 100,
    "baseline/comment": 101,
    "comment/narrative": 102,
    "indicator/period": 103,
    "period/period-start": 104,
    "period/period-end": 105,
    "period/target": 106,
    "target/comment": 107,
    "period/actual": 108,
    "actual/comment": 109,
    "iati-activity/crs-add": 110,
    "crs-add/other-flags": 111,
    "crs-add/loan-terms": 112,
    "loan-terms/repayment-type": 113,
    "loan-terms/repayment-plan": 114,
    "loan-terms/commitment-date": 115,
    "loan-terms/repayment-first-date": 116,
    "loan-terms/repayment-final-date": 117,
    "crs-add/loan-status": 118,
    "loan-status/interest-received": 119,
    "loan-status/principal-outstanding": 120,
    "loan-status/principal-arrears": 121,
    "loan-status/interest-arrears": 122,
    "iati-activity/fss": 123,
    "fss/forecast": 124
}
REQUIRED_CHILDREN = [
    ("//iati-activities", "iati-activity"),
    ("//iati-activity", "iati-identifier"),
    ("//iati-activity", "reporting-org"),
    ("//iati-activity", "title"),
    ("//iati-activity", "description"),
    ("//iati-activity", "participating-org"),
    ("//iati-activity", "activity-status"),
    ("//iati-activity", "activity-date"),
    ("//point", "pos"),
    ("//country-budget-items", "budget-item"),
    ("//budget", "period-start"),
    ("//budget", "period-end"),
    ("//budget", "value"),
    ("//planned-disbursement", "period-start"),
    ("//planned-disbursement", "value"),
    ("//transaction", "transaction-type"),
    ("//transaction", "transaction-date"),
    ("//transaction", "value"),
    ("//document-link", "title"),
    ("//document-link", "category"),
    ("//document-link", "language"),
    ("//reporting-org", "narrative"),
    ("//result", "title"),
    ("//result", "indicator"),
    ("//indicator", "title"),
    ("//period", "period-start"),
    ("//period", "period-end"),
    ("//title", "narrative"),
    ("//description", "narrative"),
    ("//organisation", "narrative"),
    ("//department", "narrative"),
    ("//person-name", "narrative"),
    ("//job-title", "narrative"),
    ("//mailing-address", "narrative"),
    ("//name", "narrative"),
    ("//activity-description", "narrative"),
    ("//condition", "narrative"),
    ("//comment", "narrative"),
]
REQUIRED_ATTRIBUTES = [
    ("//document-link", "format"),
    ("//category", "code"),
    ("//language", "code"),
    ("//sector", "code")
]


def iati_order(xml_element):
    family_tag = "{}{}{}".format(xml_element.getparent().tag, XPATH_SEPERATOR, xml_element.tag)
    return SORT_ORDER[family_tag]


def remove_xpath_index(relative_xpath):
    split_path = relative_xpath.split("[")
    indexless_path = "[".join(split_path[:-1])
    return indexless_path


def increment_xpath(absolute_xpath):
    split_path = absolute_xpath.split("[")
    indexless_path = "[".join(split_path[:-1])
    path_index = int(split_path[-1][:-1])
    path_index += 1
    incremented_xpath = "{}[{}]".format(indexless_path, path_index)
    return incremented_xpath


def recursive_tree_traversal(element, absolute_xpath, element_dictionary):
    # Main value
    element_value = str(element.text) if element.text else ""
    while absolute_xpath in element_dictionary:
        absolute_xpath = increment_xpath(absolute_xpath)

    element_dictionary[absolute_xpath] = element_value

    # Attribute values
    element_attributes = element.attrib
    for attrib_key in element_attributes.keys():
        attribute_xpath = ATTRIB_SEPERATOR.join([absolute_xpath, attrib_key])
        attribute_value = str(element_attributes[attrib_key]) if element_attributes[attrib_key] else ""
        element_dictionary[attribute_xpath] = attribute_value

    # Child values
    element_children = element.getchildren()
    if not element_children:
        return element_dictionary
    else:
        for child_elem in element_children:
            child_elem_tag = child_elem.tag
            if child_elem_tag not in EXCLUDED_CHILDREN_TAGS:
                child_absolute_xpath = XPATH_SEPERATOR.join([absolute_xpath, child_elem_tag]) + "[1]"
                element_dictionary = recursive_tree_traversal(child_elem, child_absolute_xpath, element_dictionary)

    return element_dictionary


def melt_iati(root):
    activities_list = []
    transactions_list = []
    budgets_list = []
    activities = root.getchildren()
    for activity in activities:
        activity_dict = recursive_tree_traversal(activity, "iati-activity", {})
        activities_list.append(activity_dict)

        # To key transactions and budgets
        activity_id = activity_dict["iati-activity/iati-identifier[1]"]

        transactions = activity.xpath("transaction")
        for transaction in transactions:
            transaction_dict = recursive_tree_traversal(transaction, "transaction", {})
            transaction_dict["iati-activity/iati-identifier[1]"] = activity_id
            transactions_list.append(transaction_dict)

        budgets = activity.xpath("budget")
        for budget in budgets:
            budget_dict = recursive_tree_traversal(budget, "budget", {})
            budget_dict["iati-activity/iati-identifier[1]"] = activity_id
            budgets_list.append(budget_dict)

    return (activities_list, transactions_list, budgets_list)


def cast_iati(activities_list, transactions_list, budgets_list, iati_version="2.02"):
    root = etree.Element('iati-activities', version=iati_version)
    doc = etree.ElementTree(root)

    activity_elems = {}
    for activity in activities_list:
        activity_id = activity["iati-activity/iati-identifier[1]"]
        activity_elem = etree.SubElement(root, 'iati-activity')
        activity_elems[activity_id] = activity_elem
        activity_filtered = OrderedDict((k[len('iati-activity')+1:], v) for k, v in activity.items() if v != "" and k[len('iati-activity'):len('iati-activity')+1] != ATTRIB_SEPERATOR)
        for xpath_key in activity_filtered.keys():  # Once through first to create the elements in the correct order
            xpath_without_attribute = xpath_key.split(ATTRIB_SEPERATOR)[0]
            xpath_query = activity_elem.xpath(xpath_without_attribute)
            parent_elem = activity_elem
            xpath_split = xpath_without_attribute.split(XPATH_SEPERATOR)
            creation_index = 0
            while not xpath_query:
                parent_elem_xpath_query = parent_elem.xpath(xpath_split[creation_index])
                if parent_elem_xpath_query:
                    parent_elem = parent_elem_xpath_query[0]
                    creation_index += 1
                    continue
                child_elem_tag = remove_xpath_index(xpath_split[creation_index])
                parent_elem = etree.SubElement(parent_elem, child_elem_tag)
                creation_index += 1
                xpath_query = activity_elem.xpath(xpath_without_attribute)
        activity_attributes = OrderedDict((k[len('iati-activity')+1:], v) for k, v in activity.items() if v != "" and k[len('iati-activity'):len('iati-activity')+1] == ATTRIB_SEPERATOR)
        for activity_attribute_key in activity_attributes.keys():  # Attributes applied to top level activity
            activity_attribute_value = activity_attributes[activity_attribute_key]
            activity_elem.attrib[activity_attribute_key] = activity_attribute_value
        for child_elem_xpath in activity_filtered:  # Apply text and attribute values to child elements
            child_elem_value = activity_filtered[child_elem_xpath]
            if ATTRIB_SEPERATOR not in child_elem_xpath:
                child_elem = activity_elem.xpath(child_elem_xpath)[0]
                child_elem.text = child_elem_value
            else:
                child_xpath_without_attribute, child_attribute_key = child_elem_xpath.split(ATTRIB_SEPERATOR)
                child_elem = activity_elem.xpath(child_xpath_without_attribute)[0]
                child_elem.attrib[child_attribute_key] = child_elem_value

    for transaction in transactions_list:
        activity_id = transaction["iati-activity/iati-identifier[1]"]
        try:
            activity_elem = activity_elems[activity_id]
        except KeyError:
            continue
        transaction_elem = etree.SubElement(activity_elem, 'transaction')
        transaction_filtered = OrderedDict((k[len('transaction')+1:], v) for k, v in transaction.items() if v != "" and k[len('transaction'):len('transaction')+1] != ATTRIB_SEPERATOR and k != "iati-activity/iati-identifier[1]")
        for xpath_key in transaction_filtered.keys():  # Once through first to create the elements in the correct order
            xpath_without_attribute = xpath_key.split(ATTRIB_SEPERATOR)[0]
            xpath_query = transaction_elem.xpath(xpath_without_attribute)
            parent_elem = transaction_elem
            xpath_split = xpath_without_attribute.split(XPATH_SEPERATOR)
            creation_index = 0
            while not xpath_query:
                parent_elem_xpath_query = parent_elem.xpath(xpath_split[creation_index])
                if parent_elem_xpath_query:
                    parent_elem = parent_elem_xpath_query[0]
                    creation_index += 1
                    continue
                child_elem_tag = remove_xpath_index(xpath_split[creation_index])
                parent_elem = etree.SubElement(parent_elem, child_elem_tag)
                creation_index += 1
                xpath_query = transaction_elem.xpath(xpath_without_attribute)
        transaction_attributes = OrderedDict((k[len('transaction')+1:], v) for k, v in transaction.items() if v != "" and k[len('transaction'):len('transaction')+1] == ATTRIB_SEPERATOR)
        for transaction_attribute_key in transaction_attributes.keys():  # Attributes applied to top level transaction
            transaction_attribute_value = transaction_attributes[transaction_attribute_key]
            transaction_elem.attrib[transaction_attribute_key] = transaction_attribute_value
        for child_elem_xpath in transaction_filtered:  # Apply text and attribute values to child elements
            child_elem_value = transaction_filtered[child_elem_xpath]
            if ATTRIB_SEPERATOR not in child_elem_xpath:
                child_elem = transaction_elem.xpath(child_elem_xpath)[0]
                child_elem.text = child_elem_value
            else:
                child_xpath_without_attribute, child_attribute_key = child_elem_xpath.split(ATTRIB_SEPERATOR)
                child_elem = transaction_elem.xpath(child_xpath_without_attribute)[0]
                child_elem.attrib[child_attribute_key] = child_elem_value

    for budget in budgets_list:
        activity_id = budget["iati-activity/iati-identifier[1]"]
        try:
            activity_elem = activity_elems[activity_id]
        except KeyError:
            continue
        budget_elem = etree.SubElement(activity_elem, 'budget')
        budget_filtered = OrderedDict((k[len('budget')+1:], v) for k, v in budget.items() if v != "" and k[len('budget'):len('budget')+1] != ATTRIB_SEPERATOR and k != "iati-activity/iati-identifier[1]")
        for xpath_key in budget_filtered.keys():  # Once through first to create the elements in the correct order
            xpath_without_attribute = xpath_key.split(ATTRIB_SEPERATOR)[0]
            xpath_query = budget_elem.xpath(xpath_without_attribute)
            parent_elem = budget_elem
            xpath_split = xpath_without_attribute.split(XPATH_SEPERATOR)
            creation_index = 0
            while not xpath_query:
                parent_elem_xpath_query = parent_elem.xpath(xpath_split[creation_index])
                if parent_elem_xpath_query:
                    parent_elem = parent_elem_xpath_query[0]
                    creation_index += 1
                    continue
                child_elem_tag = remove_xpath_index(xpath_split[creation_index])
                parent_elem = etree.SubElement(parent_elem, child_elem_tag)
                creation_index += 1
                xpath_query = budget_elem.xpath(xpath_without_attribute)
        budget_attributes = OrderedDict((k[len('budget')+1:], v) for k, v in budget.items() if v != "" and k[len('budget'):len('budget')+1] == ATTRIB_SEPERATOR)
        for budget_attribute_key in budget_attributes.keys():  # Attributes applied to top level budget
            budget_attribute_value = budget_attributes[budget_attribute_key]
            budget_elem.attrib[budget_attribute_key] = budget_attribute_value
        for child_elem_xpath in budget_filtered:  # Apply text and attribute values to child elements
            child_elem_value = budget_filtered[child_elem_xpath]
            if ATTRIB_SEPERATOR not in child_elem_xpath:
                child_elem = budget_elem.xpath(child_elem_xpath)[0]
                child_elem.text = child_elem_value
            else:
                child_xpath_without_attribute, child_attribute_key = child_elem_xpath.split(ATTRIB_SEPERATOR)
                child_elem = budget_elem.xpath(child_xpath_without_attribute)[0]
                child_elem.attrib[child_attribute_key] = child_elem_value

    # Add missing mandatory elements
    for required_child in REQUIRED_CHILDREN:
        parent_xpath, child_tag = required_child
        matching_parents = doc.xpath(parent_xpath)
        for matching_parent in matching_parents:
            child_query = matching_parent.xpath(child_tag)
            if not child_query:
                etree.SubElement(matching_parent, child_tag)

    # Add missing mandatory attributes
    for required_attrib in REQUIRED_ATTRIBUTES:
        parent_xpath, attrib_key = required_attrib
        matching_parents = doc.xpath(parent_xpath)
        for matching_parent in matching_parents:
            if attrib_key not in matching_parent.attrib:
                matching_parent.attrib[attrib_key] = ""

    # Enforce IATI order
    for parent in doc.xpath('//*[./*]'):  # Search for parent elements, reorder
        parent[:] = sorted(parent, key=lambda x: iati_order(x))
    return doc


def xml_to_csv(xml_filename="test_data/DIPR IATI data June 2019.xml", a_filename="test_data/activities.csv", t_filename="test_data/transactions.csv", b_filename="test_data/budgets.csv"):
    with open(xml_filename, "r") as xmlfile:
        tree = etree.parse(xmlfile)
        root = tree.getroot()

        activities, transactions, budgets = melt_iati(root)
        a_df = pd.DataFrame(activities, dtype=str)
        a_df = a_df.reindex(sorted(a_df.columns), axis=1)
        a_df.to_csv(a_filename, index=False)
        t_df = pd.DataFrame(transactions, dtype=str)
        t_df = t_df.reindex(sorted(t_df.columns), axis=1)
        t_df.to_csv(t_filename, index=False)
        b_df = pd.DataFrame(budgets, dtype=str)
        b_df = b_df.reindex(sorted(b_df.columns), axis=1)
        b_df.to_csv(b_filename, index=False)


def csv_to_xml(a_filename="test_data/activities.csv", t_filename="test_data/transactions.csv", b_filename="test_data/budgets.csv", xml_filename="test_data/output.xml"):
    a_df = pd.read_csv(a_filename, dtype=str).fillna("")
    a_df = a_df.reindex(sorted(a_df.columns), axis=1)
    t_df = pd.read_csv(t_filename, dtype=str).fillna("")
    t_df = t_df.reindex(sorted(t_df.columns), axis=1)
    b_df = pd.read_csv(b_filename, dtype=str).fillna("")
    b_df = b_df.reindex(sorted(b_df.columns), axis=1)
    activities = a_df.to_dict(into=OrderedDict, orient='records')
    transactions = t_df.to_dict(into=OrderedDict, orient='records')
    budgets = b_df.to_dict(into=OrderedDict, orient='records')

    doc = cast_iati(activities, transactions, budgets)

    with open(xml_filename, "wb") as xmlfile:
        doc.write(xmlfile, encoding="utf-8", pretty_print=True)


if __name__ == "__main__":
    xml_to_csv()
    csv_to_xml()
