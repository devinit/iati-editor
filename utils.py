from lxml import etree
import pandas as pd
from collections import OrderedDict
import pdb

XPATH_SEPERATOR = "/"
ATTRIB_SEPERATOR = "@"
EXCLUDED_CHILDREN_TAGS = ["budget", "transaction"]


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

    pdb.set_trace()

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
    t_df = pd.read_csv(t_filename, dtype=str).fillna("")
    b_df = pd.read_csv(b_filename, dtype=str).fillna("")
    activities = a_df.to_dict(into=OrderedDict, orient='records')
    transactions = t_df.to_dict(into=OrderedDict, orient='records')
    budgets = b_df.to_dict(into=OrderedDict, orient='records')

    doc = cast_iati(activities, transactions, budgets)

    with open(xml_filename, "w") as xmlfile:
        doc.write(xmlfile, encoding="utf-8")


if __name__ == "__main__":
    xml_to_csv()
    csv_to_xml()
