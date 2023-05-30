from itertools import combinations


class FPTreeNode:

    def __init__(self, fpt_item=None, fpt_support_count=0):
        """
        Initialise a Frequent Pattern Growth Tree Node.

        :param fpt_item: String - Item to assign to node
        :param fpt_support_count: Int - Number of node usages
        """
        self.fpt_item = fpt_item
        self.fpt_support_count = fpt_support_count
        self.fpt_children = {}

    def search_below(self, sb_item):
        """
        Takes a given item and returns the number of occurrences of that
        item in the nodes below.

        :param sb_item: String - Item to be found
        :return sb_count: Int - Occurrences of given Item
        """
        sb_count = 0
        sb_child: FPTreeNode
        for sb_child in self.fpt_children.values():  # Searches all the
            # nodes children for given item
            if sb_child.fpt_item == sb_item:
                sb_count += 1
            else:
                sb_count += sb_child.search_below(sb_item)  # Recursively
                # searches child node's children
        return sb_count


def initial_format(if_data, if_support_threshold):
    """
    Turns transactions into Ordered-Item Sets

    :param if_data: List - List of Transactions
    :param if_support_threshold: Float - Support Threshold Value
    :return if_ordered_transactions: List - List of Ordered Item Sets
    :return if_sorted_items: List - List of frequent items
    """
    # Counts occurrences of each item in dictionary
    if_item_count = {}
    for if_transaction in if_data:
        for if_item in if_transaction:
            if if_item in if_item_count:
                if_item_count[if_item] += 1
            else:
                if_item_count[if_item] = 1

    # Calculates Minimum support
    if_min_support = if_support_threshold*len(if_data)

    # Removes non-frequent items from dictionary
    if_items = list(if_item_count.keys())
    for if_item in if_items:
        if if_item_count[if_item] < if_min_support:
            if_item_count.pop(if_item)

    # Prepare Items in sorted list
    if_sorted_item_counts = sorted(if_item_count.items(), key=lambda x: x[1])
    if_sorted_items = []
    for item in if_sorted_item_counts:
        if_sorted_items.append(item[0])

    # Uses frequent items to create ordered item sets
    if_ordered_transactions = []
    for if_transaction in if_data:
        if_ordered_items = []
        for if_item in if_transaction:
            if if_item in if_item_count.keys():
                if_ordered_items.append(if_item)
        if_ordered_items = sorted(if_ordered_items, key=if_item_count.get,
                                  reverse=True)
        if_ordered_transactions.append(if_ordered_items)

    return if_ordered_transactions, if_sorted_items


def insert_transaction(it_root, it_transaction):
    """
    Insert a given transaction into the tree from given root node

    :param it_root: FPTreeNode - Root node of the FPG Tree
    :param it_transaction: List - Transaction to be added to tree
    """
    it_current_node: FPTreeNode = it_root

    for it_item in it_transaction:
        if it_item not in it_current_node.fpt_children.keys():
            # Creates new node if node doesn't exist
            it_current_node.fpt_children[it_item] = FPTreeNode(it_item)
        it_current_node = it_current_node.fpt_children[it_item]
        it_current_node.fpt_support_count += 1  # Increases support count for
        # each node covered


def find_paths(fp_current_node, fp_item, fp_main_path, fp_results):
    """
    Recursively searches the tree for paths to a given item

    :param fp_current_node: FPTreeNode - Current node, initially root node
    :param fp_item: String - Item to search for
    :param fp_main_path: List - Path taken to reach current node
    :param fp_results: List - List of paths found with support count
    :return fp_results: List - List of paths found with support count
    """
    # Adds current node to the main path, unless root node
    if fp_current_node.fpt_item is not None:
        fp_main_path.append(fp_current_node.fpt_item)

    # Search the children of the current node
    fp_search_nodes = []
    fp_child: FPTreeNode
    for fp_child in fp_current_node.fpt_children.values():
        # Add the current path and child support count to the results if item
        # is found
        if fp_child.fpt_item == fp_item and len(fp_main_path) > 0:
            fp_results.append([list(fp_main_path), fp_child.fpt_support_count])
        # Creates a list of child nodes which have the item below them
        elif fp_child.search_below(fp_item):
            fp_search_nodes.append(fp_child)

    # Recursively searches the possible nodes
    for fp_node in fp_search_nodes:
        fp_results = find_paths(fp_node, fp_item, list(fp_main_path),
                                fp_results)

    return fp_results


def conditional_frequent_pattern_tree_calc(cfpt_sorted_items,
                                           cfpt_conditional_pattern_bases):
    """
    Produces a Conditional Frequent Pattern Tree for each item in the tree

    :param cfpt_sorted_items: List - Ordered List of items in the tree
    :param cfpt_conditional_pattern_bases: Dict - Conditional Pattern Bases
    for each Item
    :return cfpt_conditional_frequent_pattern_trees: Dict - Conditional
    Frequent Pattern Tree for each item
    """
    cfpt_conditional_frequent_pattern_trees = {}
    for cfpt_item1 in cfpt_sorted_items:
        cfpt_recurring_items = []
        cfpt_conditional_pattern_base = cfpt_conditional_pattern_bases[
            cfpt_item1]

        # Finds items that occur in each CPB of given Item
        for cfpt_item2 in cfpt_sorted_items:
            cfpt_occurrences = 0
            for cfpt_path in cfpt_conditional_pattern_base:
                if cfpt_item2 in cfpt_path[0]:
                    cfpt_occurrences += 1
            if cfpt_occurrences == len(cfpt_conditional_pattern_base) and \
                    cfpt_occurrences > 0:
                cfpt_recurring_items.append(cfpt_item2)

        # Calculates the support count and formats the CFPT
        if len(cfpt_recurring_items) > 0:
            cfpt_support_count_sum = 0
            for cfpt_path in cfpt_conditional_pattern_base:
                cfpt_support_count_sum += cfpt_path[1]
            cfpt_conditional_frequent_pattern_trees[cfpt_item1] = [
                cfpt_recurring_items, cfpt_support_count_sum]

    return cfpt_conditional_frequent_pattern_trees


def frequent_patterns_calc(fp_conditional_frequent_pattern_trees):
    """
    Produces the Frequent Patterns

    :param fp_conditional_frequent_pattern_trees: Dict - Conditional Frequent
    Pattern Tree for each item
    :return fp_frequent_patterns: Dict - Frequent patterns for each item
    """
    fp_frequent_patterns = {}
    for fp_item in fp_conditional_frequent_pattern_trees.keys():

        fp_items = fp_conditional_frequent_pattern_trees[fp_item][0]
        fp_item_combinations = []
        # Calculates all the possible combinations of Items for each item
        for fp_combination_length in range(len(fp_items)):
            fp_item_combinations.append(list(
                combinations(fp_items, fp_combination_length + 1)))

        fp_frequent_patterns[fp_item] = []
        # Formats each Frequent Pattern with Support Value
        for fp_combination1 in fp_item_combinations:
            for fp_combination2 in fp_combination1:
                fp_combination2 = list(fp_combination2)
                fp_combination2.append(fp_item)
                fp_frequent_patterns[fp_item] \
                    .append([fp_combination2,
                             fp_conditional_frequent_pattern_trees[
                                 fp_item][1]])

    return fp_frequent_patterns


def run_fpgrowth(rfpg_test_data, rfpg_support_threshold):
    """
    Main Function to run the Frequent Pattern Growth Algorithm with given data

    :param rfpg_test_data: List - List containing each transaction
    :param rfpg_support_threshold: Float - Support Threshold Value
    :return frequent_patterns: Dict - Frequent Patterns Generated
    """

    # Produce Ordered Item Sets and Sorted Items
    ordered_transactions, sorted_items = initial_format(rfpg_test_data,
                                                        rfpg_support_threshold)

    # Create Tree
    root = FPTreeNode()
    for transaction in ordered_transactions:
        insert_transaction(root, transaction)

    # Sorts items depending on frequency
    sorted_items = sorted(sorted_items, key=lambda x: root.search_below(x),
                          reverse=True)

    # Produce Conditional Pattern Base
    conditional_pattern_bases = {}
    for item in sorted_items:
        conditional_pattern_bases[item] = find_paths(root, item, [], [])

    # Produce Conditional Frequent Pattern Tree
    conditional_frequent_pattern_trees = \
        conditional_frequent_pattern_tree_calc(sorted_items,
                                               conditional_pattern_bases)

    # Produce Frequent Patterns
    frequent_patterns = frequent_patterns_calc(
        conditional_frequent_pattern_trees)

    return frequent_patterns


if __name__ == '__main__':

    support_threshold = 0.6

    test_data = [["I1", "I2", "I3"],
                 ["I2", "I3", "I4"],
                 ["I4", "I5"],
                 ["I1", "I2", "I4"],
                 ["I1", "I2", "I3", "I5"],
                 ["I1", "I2", "I3", "I4"]]

    test_data_2 = [["E", "K", "M", "N", "O", "Y"],
                   ["D", "E", "K", "N", "O", "Y"],
                   ["A", "E", "K", "M"],
                   ["C", "K", "M", "U", "Y"],
                   ["C", "E", "I", "K", "O"]]

    print(run_fpgrowth(test_data_2, support_threshold))
