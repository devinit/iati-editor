import os
from lxml import etree
import pandas as pd
import pdb

VALUE_SEPERATOR = "|"
XPATH_SEPERATOR = "/"
ATTRIB_SEPERATOR = "@"
EXCLUDED_CHILDREN_TAGS = ["budget", "transaction"]


def recursive_tree_traversal(element, absolute_xpath, element_dictionary):
    # Main value
    element_value = str(element.text) if element.text else ""
    if absolute_xpath not in element_dictionary:
        element_dictionary[absolute_xpath] = element_value
    else:
        element_dictionary[absolute_xpath] = VALUE_SEPERATOR.join([element_dictionary[absolute_xpath], element_value])

    # Attribute values
    element_attributes = element.attrib
    for attrib_key in element_attributes.keys():
        attribute_xpath = ATTRIB_SEPERATOR.join([absolute_xpath, attrib_key])
        attribute_value = str(element_attributes[attrib_key]) if element_attributes[attrib_key] else ""
        if attribute_xpath not in element_dictionary:
            element_dictionary[attribute_xpath] = attribute_value
        else:
            element_dictionary[attribute_xpath] = VALUE_SEPERATOR.join([element_dictionary[attribute_xpath], attribute_value])

    # Child values
    element_children = element.getchildren()
    if not element_children:
        return element_dictionary
    else:
        for child_elem in element_children:
            child_elem_tag = child_elem.tag
            if child_elem_tag not in EXCLUDED_CHILDREN_TAGS:
                child_absolute_xpath = XPATH_SEPERATOR.join([absolute_xpath, child_elem_tag])
                element_dictionary = recursive_tree_traversal(child_elem, child_absolute_xpath, element_dictionary)

    return element_dictionary


def melt_iati(root):
    activities_list = []
    transactions_list = []
    budgets_list = []
    activities = root.getchildren()
    for activity in activities:
        activity_dict = recursive_tree_traversal(activity, "activity", {})
        activities_list.append(activity_dict)

        # To key transactions and budgets
        activity_id = activity_dict["activity/iati-identifier"]

        transactions = activity.xpath("transaction")
        for transaction in transactions:
            transaction_dict = recursive_tree_traversal(transaction, "transaction", {})
            transaction_dict["activity/iati-identifier"] = activity_id
            transactions_list.append(transaction_dict)

        budgets = activity.xpath("budget")
        for budget in budgets:
            budget_dict = recursive_tree_traversal(budget, "budget", {})
            budget_dict["activity/iati-identifier"] = activity_id
            budgets_list.append(budget_dict)

    return (activities_list, transactions_list, budgets_list)


def main():
    filename = "test_data/DIPR IATI data June 2019.xml"
    with open(filename, "r") as xmlfile:
        original_basename, _ = os.path.splitext(os.path.basename(filename))
        tree = etree.parse(xmlfile)
        root = tree.getroot()

        activities, transactions, budgets = melt_iati(root)
        a_df = pd.DataFrame(activities)
        a_df = a_df.reindex(sorted(a_df.columns), axis=1)
        a_df.to_csv("test_data/activities.csv", index=False)
        t_df = pd.DataFrame(transactions)
        t_df = t_df.reindex(sorted(t_df.columns), axis=1)
        t_df.to_csv("test_data/transactions.csv", index=False)
        b_df = pd.DataFrame(budgets)
        b_df = b_df.reindex(sorted(b_df.columns), axis=1)
        b_df.to_csv("test_data/budgets.csv", index=False)


if __name__ == "__main__":
    main()
