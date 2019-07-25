import os
import re
import sys
import glob
import datetime
import pytz
from lxml import etree
import pandas as pd
from collections import OrderedDict
import iati
import iati.validator
import iati.utilities
import iati.resources


# Initialize app, checking if frozen in exe
if getattr(sys, 'frozen', False):
    IATI_FOLDER = os.path.abspath(os.path.join(sys.executable, '..', 'iati'))
else:
    dir_path = os.path.dirname(os.path.realpath(__file__))
    IATI_FOLDER = os.path.abspath(os.path.join(dir_path, "iati"))


# Override methods to allow freezing in one file
def get_codelist_paths(version):
    folder_path = os.path.join(IATI_FOLDER, "resources", "standard", iati.resources.folder_name_for_version(version), "codelists")
    files = glob.glob(os.path.join(folder_path, "*.xml"))
    return files


iati.resources.get_codelist_paths = get_codelist_paths


def resource_filesystem_path(path):
    return os.path.join(IATI_FOLDER, path)


iati.resources.resource_filesystem_path = resource_filesystem_path

v203_schema = iati.default.activity_schema("2.03")

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
    "iati-activity/tag": 51,
    "tag/narrative": 52,
    "iati-activity/country-budget-items": 53,
    "country-budget-items/budget-item": 54,
    "budget-item/description": 55,
    "iati-activity/humanitarian-scope": 56,
    "humanitarian-scope/narrative": 57,
    "iati-activity/policy-marker": 58,
    "policy-marker/narrative": 59,
    "iati-activity/collaboration-type": 60,
    "iati-activity/default-flow-type": 61,
    "iati-activity/default-finance-type": 62,
    "iati-activity/default-aid-type": 63,
    "iati-activity/default-tied-status": 64,
    "iati-activity/budget": 65,
    "budget/period-start": 66,
    "budget/period-end": 67,
    "budget/value": 68,
    "iati-activity/planned-disbursement": 69,
    "planned-disbursement/period-start": 70,
    "planned-disbursement/period-end": 71,
    "planned-disbursement/value": 72,
    "iati-activity/capital-spend": 73,
    "iati-activity/transaction": 74,
    "transaction/transaction-type": 75,
    "transaction/transaction-date": 76,
    "transaction/value": 77,
    "transaction/description": 78,
    "transaction/provider-org": 79,
    "provider-org/narrative": 80,
    "transaction/receiver-org": 81,
    "receiver-org/narrative": 82,
    "transaction/disbursement-channel": 83,
    "transaction/sector": 84,
    "transaction/recipient-country": 85,
    "transaction/recipient-region": 86,
    "transaction/flow-type": 87,
    "transaction/finance-type": 88,
    "transaction/aid-type": 89,
    "transaction/tied-status": 90,
    "iati-activity/document-link": 91,
    "document-link/title": 92,
    "document-link/category": 93,
    "document-link/language": 94,
    "document-link/document-date": 95,
    "iati-activity/related-activity": 96,
    "iati-activity/legacy-data": 97,
    "iati-activity/conditions": 98,
    "conditions/condition": 99,
    "condition/narrative": 100,
    "iati-activity/result": 101,
    "result/title": 102,
    "result/description": 103,
    "result/document-link": 104,
    "result/reference": 105,
    "result/indicator": 106,
    "indicator/title": 107,
    "indicator/description": 108,
    "indicator/document-link": 109,
    "indicator/reference": 110,
    "indicator/baseline": 111,
    "baseline/comment": 112,
    "comment/narrative": 113,
    "indicator/period": 114,
    "period/period-start": 115,
    "period/period-end": 116,
    "period/target": 117,
    "target/comment": 118,
    "period/actual": 119,
    "actual/comment": 120,
    "iati-activity/crs-add": 121,
    "crs-add/other-flags": 122,
    "crs-add/loan-terms": 123,
    "loan-terms/repayment-type": 124,
    "loan-terms/repayment-plan": 125,
    "loan-terms/commitment-date": 126,
    "loan-terms/repayment-first-date": 127,
    "loan-terms/repayment-final-date": 128,
    "crs-add/loan-status": 129,
    "loan-status/interest-received": 130,
    "loan-status/principal-outstanding": 131,
    "loan-status/principal-arrears": 132,
    "loan-status/interest-arrears": 133,
    "iati-activity/fss": 134,
    "fss/forecast": 135
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
ADDITIONAL_TAGS = [
    "iati-activity/iati-identifier",
    "iati-activity/activity-scope",
    "iati-activity/recipient-region",
    "iati-activity/location",
    "iati-activity/tag",
    "iati-activity/humanitarian-scope",
    "iati-activity/policy-marker",
    "iati-activity/collaboration-type",
    "iati-activity/default-flow-type",
    "iati-activity/default-finance-type",
    "iati-activity/default-aid-type",
    "iati-activity/default-tied-status",
    "iati-activity/conditions",
    "iati-activity/result"
]
DEFAULT_ADDITIONAL_COLUMNS = [
    ("iati-activity@humanitarian", "false"),
    ("iati-activity/iati-identifier[1]", ""),
    ("iati-activity/activity-scope[1]", ""),
    ("iati-activity/activity-scope[1]@code", ""),
    ("iati-activity/recipient-region[1]", ""),
    ("iati-activity/recipient-region[1]@code", ""),
    ("iati-activity/recipient-region[1]@vocabulary", ""),
    ("iati-activity/recipient-region[1]@percentage", ""),
    ("iati-activity/location[1]", ""),
    ("iati-activity/location[1]@ref", ""),
    ("iati-activity/location[1]/location-reach[1]", ""),
    ("iati-activity/location[1]/location-reach[1]@code", "2"),
    ("iati-activity/location[1]/location-id[1]", ""),
    ("iati-activity/location[1]/location-id[1]@vocabulary", ""),
    ("iati-activity/location[1]/location-id[1]@code", ""),
    ("iati-activity/location[1]/name[1]", ""),
    ("iati-activity/location[1]/name[1]/narrative[1]", ""),
    ("iati-activity/location[1]/exactness[1]", ""),
    ("iati-activity/location[1]/exactness[1]@code", "2"),
    ("iati-activity/tag[1]", ""),
    ("iati-activity/tag[1]@vocabulary", ""),
    ("iati-activity/tag[1]@code", ""),
    ("iati-activity/tag[1]/narrative", ""),
    ("iati-activity/humanitarian-scope[1]", ""),
    ("iati-activity/humanitarian-scope[1]@type", ""),
    ("iati-activity/humanitarian-scope[1]@vocabulary", ""),
    ("iati-activity/humanitarian-scope[1]@code", ""),
    ("iati-activity/humanitarian-scope[1]/narrative[1]", ""),
    ("iati-activity/policy-marker[1]", ""),
    ("iati-activity/policy-marker[1]@vocabulary", ""),
    ("iati-activity/policy-marker[1]@code", ""),
    ("iati-activity/policy-marker[1]@significance", ""),
    ("iati-activity/policy-marker[1]/narrative[1]", ""),
    ("iati-activity/collaboration-type[1]", ""),
    ("iati-activity/collaboration-type[1]@code", ""),
    ("iati-activity/default-flow-type[1]", ""),
    ("iati-activity/default-flow-type[1]@code", ""),
    ("iati-activity/default-finance-type[1]", ""),
    ("iati-activity/default-finance-type[1]@code", ""),
    ("iati-activity/default-aid-type[1]", ""),
    ("iati-activity/default-aid-type[1]@code", ""),
    ("iati-activity/default-aid-type[1]@vocabulary", ""),
    ("iati-activity/default-tied-status[1]", ""),
    ("iati-activity/default-tied-status[1]@code", ""),
    ("iati-activity/conditions[1]", ""),
    ("iati-activity/conditions[1]@attached", ""),
    ("iati-activity/conditions[1]/condition[1]", ""),
    ("iati-activity/conditions[1]/condition[1]@type", ""),
    ("iati-activity/conditions[1]/condition[1]/narrative[1]", ""),
    ("iati-activity/result[1]/reference[1]", ""),
    ("iati-activity/result[1]@type", ""),
    ("iati-activity/result[1]@aggregation-status", ""),
    ("iati-activity/result[1]/title[1]", ""),
    ("iati-activity/result[1]/title[1]/narrative[1]", ""),
    ("iati-activity/result[1]/description[1]", ""),
    ("iati-activity/result[1]/description[1]/narrative[1]", ""),
    ("iati-activity/result[1]/indicator[1]", ""),
    ("iati-activity/result[1]/indicator[1]@measure", ""),
    ("iati-activity/result[1]/indicator[1]@ascending", ""),
    ("iati-activity/result[1]/indicator[1]@aggregation-status", ""),
    ("iati-activity/result[1]/indicator[1]/title[1]", ""),
    ("iati-activity/result[1]/indicator[1]/title[1]/narrative[1]", ""),
    ("iati-activity/result[1]/indicator[1]/description[1]", ""),
    ("iati-activity/result[1]/indicator[1]/description[1]/narrative[1]", ""),
    ("iati-activity/result[1]/indicator[1]/reference[1]", ""),
    ("iati-activity/result[1]/indicator[1]/reference[1]@code", ""),
    ("iati-activity/result[1]/indicator[1]/reference[1]@vocabulary", ""),
    ("iati-activity/result[1]/indicator[1]/baseline[1]", ""),
    ("iati-activity/result[1]/indicator[1]/baseline[1]@iso-date", ""),
    ("iati-activity/result[1]/indicator[1]/baseline[1]@year", ""),
    ("iati-activity/result[1]/indicator[1]/baseline[1]@value", ""),
    ("iati-activity/result[1]/indicator[1]/period[1]", ""),
    ("iati-activity/result[1]/indicator[1]/period[1]/period-start[1]", ""),
    ("iati-activity/result[1]/indicator[1]/period[1]/period-start[1]@iso-date", ""),
    ("iati-activity/result[1]/indicator[1]/period[1]/period-end[1]", ""),
    ("iati-activity/result[1]/indicator[1]/period[1]/period-end[1]@iso-date", ""),
    ("iati-activity/result[1]/indicator[1]/period[1]/period-start[1]", ""),
    ("iati-activity/result[1]/indicator[1]/period[1]/target[1]", ""),
    ("iati-activity/result[1]/indicator[1]/period[1]/target[1]@value", ""),
    ("iati-activity/result[1]/indicator[1]/period[1]/actual[1]", ""),
    ("iati-activity/result[1]/indicator[1]/period[1]/actual[1]@value", ""),
]


def xpath_sort(xpath_key):
    pattern = re.compile(r"\[(\d+)\]")
    xpath_hierarchy = len(xpath_key.split(XPATH_SEPERATOR))
    path_indexes = [int(found) for found in pattern.findall(xpath_key)]
    return xpath_hierarchy, path_indexes, xpath_key


def iati_order(xml_element):
    family_tag = "{}{}{}".format(xml_element.getparent().tag, XPATH_SEPERATOR, xml_element.tag)
    return SORT_ORDER[family_tag]


def iati_order_xpath(xpath_key):
    xpath_without_attribute = xpath_key.split(ATTRIB_SEPERATOR)[0]
    xpath_split = [elem_xpath.split("[")[0] for elem_xpath in xpath_without_attribute.split(XPATH_SEPERATOR)]
    top_index = 0
    sort_orders = [0]
    if len(xpath_split) > 1:
        top_index = int(xpath_without_attribute.split(XPATH_SEPERATOR)[1].split("[")[-1][:-1])
        sort_orders.append(top_index)
        for i in range(1, len(xpath_split)):
            elem_tag = xpath_split[i]
            parent_tag = xpath_split[i-1]
            family_tag = "{}{}{}".format(parent_tag, XPATH_SEPERATOR, elem_tag)
            sort_orders.append(SORT_ORDER[family_tag])
    return sort_orders, xpath_key


def create_ancestor_tag(absolute_xpath):
    xpath_without_attribute = absolute_xpath.split(ATTRIB_SEPERATOR)[0]
    xpath_split = [elem_xpath.split("[")[0] for elem_xpath in xpath_without_attribute.split(XPATH_SEPERATOR)]
    if len(xpath_split) > 1:
        elem_tag = xpath_split[1]
        parent_tag = xpath_split[0]
        ancestor_tag = "{}{}{}".format(parent_tag, XPATH_SEPERATOR, elem_tag)
    else:
        ancestor_tag = xpath_without_attribute
    return ancestor_tag


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
    activities_list_static = []
    activities_list_additions = []
    transactions_list = []
    budgets_list = []
    activities = root.getchildren()
    for activity in activities:
        activity_dict = recursive_tree_traversal(activity, "iati-activity", {})
        activity_dict_static = {k: v for k, v in activity_dict.items() if create_ancestor_tag(k) not in ADDITIONAL_TAGS or create_ancestor_tag(k) == "iati-activity/iati-identifier"}
        activity_dict_additions = {k: v for k, v in activity_dict.items() if create_ancestor_tag(k) in ADDITIONAL_TAGS}
        for default_col, default_val in DEFAULT_ADDITIONAL_COLUMNS:
            if default_col not in activity_dict_additions.keys():
                activity_dict_additions[default_col] = default_val
        activities_list_static.append(activity_dict_static)
        activities_list_additions.append(activity_dict_additions)

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

    return (activities_list_static, activities_list_additions, transactions_list, budgets_list)


def cast_iati(activities_list, transactions_list, budgets_list, iati_version="2.03"):
    root = etree.Element('iati-activities', version=iati_version)
    root.attrib["generated-datetime"] = datetime.datetime.now(pytz.utc).strftime('%Y-%m-%dT%H:%M:%S')
    doc = etree.ElementTree(root)

    activity_elems = {}
    for activity in activities_list:
        activity_id = activity["iati-activity/iati-identifier[1]"]
        activity_elem = etree.SubElement(root, 'iati-activity')
        activity_elem.attrib['{http://www.w3.org/XML/1998/namespace}lang'] = "en"
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

    a_filename = os.path.join(csv_dir, "activities_static.csv")
    a_add_filename = os.path.join(csv_dir, "activities_additions.csv")
    t_filename = os.path.join(csv_dir, "transactions.csv")
    b_filename = os.path.join(csv_dir, "budgets.csv")

    with open(xml_filename, "r") as xmlfile:
        parser = etree.XMLParser(remove_blank_text=True)
        tree = etree.parse(xmlfile, parser=parser)
        root = tree.getroot()

        activities_static, activities_additions, transactions, budgets = melt_iati(root)
        a_df = pd.DataFrame(activities_static, dtype=str)
        a_df = a_df.reindex(sorted(a_df.columns, key=iati_order_xpath), axis=1).sort_values('iati-activity/iati-identifier[1]')
        a_df.to_csv(a_filename, index=False)
        a_add_df = pd.DataFrame(activities_additions, dtype=str)
        a_add_df = a_add_df.reindex(sorted(a_add_df.columns, key=iati_order_xpath), axis=1).sort_values('iati-activity/iati-identifier[1]')
        a_add_df.to_csv(a_add_filename, index=False)
        t_df = pd.DataFrame(transactions, dtype=str)
        t_df = t_df.reindex(sorted(t_df.columns, key=iati_order_xpath), axis=1).sort_values('iati-activity/iati-identifier[1]')
        t_df.to_csv(t_filename, index=False)
        b_df = pd.DataFrame(budgets, dtype=str)
        b_df = b_df.reindex(sorted(b_df.columns, key=iati_order_xpath), axis=1).sort_values('iati-activity/iati-identifier[1]')
        b_df.to_csv(b_filename, index=False)


def open_csv_dir(csv_dir):
    a_filename = os.path.join(csv_dir, "activities_static.csv")
    a_add_filename = os.path.join(csv_dir, "activities_additions.csv")
    t_filename = os.path.join(csv_dir, "transactions.csv")
    b_filename = os.path.join(csv_dir, "budgets.csv")

    a_static_df = pd.read_csv(a_filename, dtype=str).fillna("")
    a_add_df = pd.read_csv(a_add_filename, dtype=str).fillna("")
    a_df = pd.merge(a_static_df, a_add_df, on='iati-activity/iati-identifier[1]')
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
