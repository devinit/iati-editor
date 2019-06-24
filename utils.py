import os
import re
from lxml import etree
import pandas as pd
from collections import OrderedDict
import iati.default
import iati.validator
import iati.utilities


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
    "other-identifier/owner-org": 11,
    "owner-org/narrative": 12,
    "iati-activity/activity-status": 13,
    "iati-activity/activity-date": 14,
    "activity-date/narrative": 15,
    "iati-activity/contact-info": 16,
    "contact-info/organisation": 17,
    "organisation/narrative": 18,
    "contact-info/department": 19,
    "department/narrative": 20,
    "contact-info/person-name": 21,
    "person-name/narrative": 22,
    "contact-info/job-title": 23,
    "job-title/narrative": 24,
    "contact-info/telephone": 25,
    "contact-info/email": 26,
    "contact-info/website": 27,
    "contact-info/mailing-address": 28,
    "mailing-address/narrative": 29,
    "iati-activity/activity-scope": 30,
    "iati-activity/recipient-country": 31,
    "recipient-country/narrative": 32,
    "iati-activity/recipient-region": 33,
    "recipient-region/narrative": 34,
    "iati-activity/location": 35,
    "location/location-reach": 36,
    "location/location-id": 37,
    "location/name": 38,
    "name/narrative": 39,
    "location/description": 40,
    "location/activity-description": 41,
    "activity-description/narrative": 42,
    "location/administrative": 43,
    "location/point": 44,
    "point/pos": 45,
    "location/exactness": 46,
    "location/location-class": 47,
    "location/feature-designation": 48,
    "iati-activity/sector": 49,
    "sector/narrative": 50,
    "iati-activity/country-budget-items": 51,
    "country-budget-items/budget-item": 52,
    "budget-item/description": 53,
    "iati-activity/policy-marker": 54,
    "policy-marker/narrative": 55,
    "iati-activity/collaboration-type": 56,
    "iati-activity/default-flow-type": 57,
    "iati-activity/default-finance-type": 58,
    "iati-activity/default-aid-type": 59,
    "iati-activity/default-tied-status": 60,
    "iati-activity/budget": 61,
    "budget/period-start": 62,
    "budget/period-end": 63,
    "budget/value": 64,
    "iati-activity/planned-disbursement": 65,
    "planned-disbursement/period-start": 66,
    "planned-disbursement/period-end": 67,
    "planned-disbursement/value": 68,
    "iati-activity/capital-spend": 69,
    "iati-activity/transaction": 70,
    "transaction/transaction-type": 71,
    "transaction/transaction-date": 72,
    "transaction/value": 73,
    "transaction/description": 74,
    "transaction/provider-org": 75,
    "provider-org/narrative": 76,
    "transaction/receiver-org": 77,
    "receiver-org/narrative": 78,
    "transaction/disbursement-channel": 79,
    "transaction/sector": 80,
    "transaction/recipient-country": 81,
    "transaction/recipient-region": 82,
    "transaction/flow-type": 83,
    "transaction/finance-type": 84,
    "transaction/aid-type": 85,
    "transaction/tied-status": 86,
    "iati-activity/document-link": 87,
    "document-link/title": 88,
    "document-link/category": 89,
    "document-link/language": 90,
    "iati-activity/related-activity": 91,
    "iati-activity/legacy-data": 92,
    "iati-activity/conditions": 93,
    "conditions/condition": 94,
    "condition/narrative": 95,
    "iati-activity/result": 96,
    "result/title": 97,
    "result/description": 98,
    "result/indicator": 99,
    "indicator/title": 100,
    "indicator/description": 101,
    "indicator/baseline": 102,
    "baseline/comment": 103,
    "comment/narrative": 104,
    "indicator/period": 105,
    "period/period-start": 106,
    "period/period-end": 107,
    "period/target": 108,
    "target/comment": 109,
    "period/actual": 110,
    "actual/comment": 111,
    "iati-activity/crs-add": 112,
    "crs-add/other-flags": 113,
    "crs-add/loan-terms": 114,
    "loan-terms/repayment-type": 115,
    "loan-terms/repayment-plan": 116,
    "loan-terms/commitment-date": 117,
    "loan-terms/repayment-first-date": 118,
    "loan-terms/repayment-final-date": 119,
    "crs-add/loan-status": 120,
    "loan-status/interest-received": 121,
    "loan-status/principal-outstanding": 122,
    "loan-status/principal-arrears": 123,
    "loan-status/interest-arrears": 124,
    "iati-activity/fss": 125,
    "fss/forecast": 126
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


def xpath_sort(xpath_key):
    pattern = re.compile(r"\[(\d+)\]")
    xpath_hierarchy = len(xpath_key.split(XPATH_SEPERATOR))
    path_indexes = [int(found) for found in pattern.findall(xpath_key)]
    return xpath_hierarchy, path_indexes, xpath_key


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


def cast_iati(activities_list, transactions_list, budgets_list, iati_version="2.03"):
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


def xml_to_csv(xml_filename, csv_dir=None):
    if not csv_dir:
        csv_dir = os.path.splitext(xml_filename)[0]
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    print("Converting IATI XML at '{}' to CSV in '{}'".format(xml_filename, csv_dir))

    # Validate FocalPoint input
    v203_schema = iati.default.activity_schema('2.03')
    dataset = iati.utilities.load_as_dataset(xml_filename)
    print("Input is valid XML: {}".format(iati.validator.is_xml(dataset)))
    print("Input is valid IATI: {}".format(iati.validator.is_iati_xml(dataset, v203_schema)))
    fully_valid = iati.validator.is_valid(dataset, v203_schema)
    print("Input has valid IATI schema and rules: {}".format(fully_valid))
    if not fully_valid:
        print("Writing input validation error CSV... Done.")
        error_log = iati.validator.full_validation(dataset, v203_schema)
        error_records = [{"info": err_rec.info, "description": err_rec.description, "status": err_rec.status} for err_rec in error_log]
        pd.DataFrame(error_records).to_csv(os.path.join(csv_dir, "input_validation_errors.csv"))

    a_filename = os.path.join(csv_dir, "activities.csv")
    t_filename = os.path.join(csv_dir, "transactions.csv")
    b_filename = os.path.join(csv_dir, "budgets.csv")

    with open(xml_filename, "r") as xmlfile:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(xmlfile, parser=parser)
        root = tree.getroot()

        activities, transactions, budgets = melt_iati(root)
        a_df = pd.DataFrame(activities, dtype=str)
        a_df = a_df.reindex(sorted(a_df.columns, key=xpath_sort), axis=1)
        a_df.to_csv(a_filename, index=False)
        t_df = pd.DataFrame(transactions, dtype=str)
        t_df = t_df.reindex(sorted(t_df.columns, key=xpath_sort), axis=1)
        t_df.to_csv(t_filename, index=False)
        b_df = pd.DataFrame(budgets, dtype=str)
        b_df = b_df.reindex(sorted(b_df.columns, key=xpath_sort), axis=1)
        b_df.to_csv(b_filename, index=False)


def open_csv_dir(csv_dir):
    a_filename = os.path.join(csv_dir, "activities.csv")
    t_filename = os.path.join(csv_dir, "transactions.csv")
    b_filename = os.path.join(csv_dir, "budgets.csv")

    a_df = pd.read_csv(a_filename, dtype=str).fillna("")
    a_df = a_df.reindex(sorted(a_df.columns, key=xpath_sort), axis=1).sort_values('iati-activity/iati-identifier[1]')
    t_df = pd.read_csv(t_filename, dtype=str).fillna("")
    t_df = t_df.reindex(sorted(t_df.columns, key=xpath_sort), axis=1).sort_values('iati-activity/iati-identifier[1]')
    b_df = pd.read_csv(b_filename, dtype=str).fillna("")
    b_df = b_df.reindex(sorted(b_df.columns, key=xpath_sort), axis=1).sort_values('iati-activity/iati-identifier[1]')
    activities = a_df.to_dict(into=OrderedDict, orient='records')
    transactions = t_df.to_dict(into=OrderedDict, orient='records')
    budgets = b_df.to_dict(into=OrderedDict, orient='records')
    return (activities, transactions, budgets)


def csv_to_xml(csv_dir, xml_filename=None):
    if not xml_filename:
        xml_filename = os.path.normpath(csv_dir) + "_converted.xml"
    print("Converting CSV files from '{}' to IATI XML at '{}'".format(csv_dir, xml_filename))

    activities, transactions, budgets = open_csv_dir(csv_dir)
    doc = cast_iati(activities, transactions, budgets)

    with open(xml_filename, "wb") as xmlfile:
        doc.write(xmlfile, encoding="utf-8", pretty_print=True)

    # Validate
    v203_schema = iati.default.activity_schema('2.03')
    dataset = iati.utilities.load_as_dataset(xml_filename)
    print("Output is valid XML: {}".format(iati.validator.is_xml(dataset)))
    print("Output is valid IATI: {}".format(iati.validator.is_iati_xml(dataset, v203_schema)))
    fully_valid = iati.validator.is_valid(dataset, v203_schema)
    print("Output has valid IATI schema and rules: {}".format(fully_valid))
    if not fully_valid:
        print("Writing output validation error CSV... Done.")
        error_log = iati.validator.full_validation(dataset, v203_schema)
        error_records = [{"info": err_rec.info, "description": err_rec.description, "status": err_rec.status} for err_rec in error_log]
        pd.DataFrame(error_records).to_csv(os.path.join(csv_dir, "output_validation_errors.csv"))


def elements_equal(e1, e2):
    if e1.tag != e2.tag:
        return False
    if e1.text != e2.text:
        return False
    if e1.tail != e2.tail:
        return False
    if e1.attrib != e2.attrib:
        return False
    if len(e1) != len(e2):
        return False
    if not all(elements_equal(c1, c2) for c1, c2 in zip(e1, e2)):
        return False
    return True


def xml_differencer(past_xml_filename, current_xml_filename, updated_xml_filename):
    print("Finding updated activities from '{}' to '{}'. Saving as '{}'... Done.".format(past_xml_filename, current_xml_filename, updated_xml_filename))
    past_xmlfile = open(past_xml_filename, "r")
    past_tree = etree.parse(past_xmlfile)
    past_root = past_tree.getroot()

    current_xmlfile = open(current_xml_filename, "r")
    current_tree = etree.parse(current_xmlfile)
    current_root = current_tree.getroot()

    past_ids = [iati_id.text for iati_id in past_root.xpath("//iati-identifier")]
    current_ids = [iati_id.text for iati_id in current_root.xpath("//iati-identifier")]
    new_ids = [current_id for current_id in current_ids if current_id not in past_ids]
    removed_ids = [past_id for past_id in past_ids if past_id not in current_ids]
    common_ids = [past_id for past_id in past_ids if past_id in current_ids]
    print("{} new activities, {} common activities, {} removed activities".format(len(new_ids), len(common_ids), len(removed_ids)))
    for common_id in common_ids:
        past_elem = past_root.xpath("//iati-activity[iati-identifier/text()='{}']".format(common_id))[0]
        current_elem = current_root.xpath("//iati-activity[iati-identifier/text()='{}']".format(common_id))[0]
        if elements_equal(past_elem, current_elem):
            current_elem.getparent().remove(current_elem)

    doc = etree.ElementTree(current_root)
    with open(updated_xml_filename, "wb") as xmlfile:
        doc.write(xmlfile, encoding="utf-8", pretty_print=True)


if __name__ == "__main__":
    xml_differencer("test_data/DIPR IATI data February 2018.xml", "test_data/DIPR IATI data June 2019.xml", "test_data/new_and_updated.xml")
    xml_to_csv("test_data/new_and_updated.xml")
    csv_to_xml("test_data/new_and_updated")
