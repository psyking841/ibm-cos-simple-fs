import re
from ibm_cos_sfs.bucket_tree_node import COSBucketTreeNode

class COSBucketTree:
    """
    This class is to convert the flat representation of IBMCloud COS bucket to a tree representation.

    For example, given a list (flat) representation of all objects under a bucket "mybucket":
    [
        'source/',
        'source/year=2018/',
        'source/year=2018/month=08/',
        'source/year=2018/month=08/day=28/',
        'source/year=2018/month=08/day=28/test1.txt',
        'source/year=2018/month=08/day=28/test.txt',
        'source/year=2018/month=08/day=29/',
        'source/year=2018/month=08/day=29/test.txt',
        'source/year=2018/month=08/day=30/',
        'source/year=2018/month=08/day=30/test.txt',
        'source/year=2018/month=08/day=31/',
        'source/year=2018/month=08/day=31/test.txt',
        'source/year=2019/month=01/day=01/',
        'source/year=2019/month=01/day=01/test.txt'
     ]

    This class converts it to a tree structure like:

    test-bucket
    └─ source/
       └─ year=2018/
          └─ month=08/
             └─ day=28/
                └─ test1.txt
                └─ test.txt
             └─ day=29/
                └─ test.txt
             └─ day=30/
                └─ test.txt
             └─ day=31/
                └─ test.txt
       └─ year=2019/
          └─ month=01/
             └─ day=01/
                └─ test.txt

    The tree will be rooted with bucket name.
    """

    def __init__(self, bucket_name, object_list):
        self.bucket_name = bucket_name
        self.root = self._populate_tree(bucket_name, object_list)

    def _populate_tree(self, bucket_name, object_list):
        """
        Populate the whole tree given the flat representation (i.e. list).
        :param bucket_name: String. Name of the bucket
        :param object_list: List. A list of object strings
        :return:
        """
        def add_node(elem_list, node):
            """
            Recursively add an object (in terms of list) to the tree.
            :param elem_list: List. The list representation of the elements in a object string.
            For example, element list ['source/', 'year=2018/', 'month=08/', 'day=31/', 'test.txt'] stands for 'source/year=2018/month=08/day=31/test.txt' COS object string.
            :param node: the parent node
            :return: current node
            """
            if not elem_list:
                return

            first = elem_list[0]
            rest = elem_list[1:]
            if first not in node.get_children().keys():
                node.get_children().update({first: COSBucketTreeNode(first, node)})

            return add_node(rest, node.get_children().get(first))

        root = COSBucketTreeNode(bucket_name, None)
        for obj_str in object_list:
            element_list = re.findall(r'.*?\/|.*?\..+', obj_str)
            add_node(element_list, root)

        return root

    def _search_leaves(self, node):
        """
        Search all leaves from a node
        :param node:
        :return:
        """
        if not node.get_children():
            return [node]
        res = []
        for k,c in node.get_children().items():
            res += self._search_leaves(c)
        return res

    def _get_leaves(self):
        """
        List all leaf nodes.
        :return: a list of full paths to all the leaves
        """
        return self._search_leaves(self.root)

    def get_leaves_paths(self):
        """
        Return all leaves of this tree in the form of paths
        :return:
        """
        return [c.get_path() for c in self._get_leaves()]

    def __str__(self):
        """
        Get the tree representation in String
        :param node:
        :return:
        """
        def print_tree(node, level):
            indent = ' ' * (level - 1) * 3
            if not node.children:
                return indent + '└─ {} \n'.format(node.name)
            res = indent + '└─ {} \n'.format(node.name)
            for k,c in node.get_children().items():
                res += print_tree(c, level + 1)
            return res

        printed_tree = self.bucket_name + '/ \n'
        for k, c in self.root.get_children().items():
            printed_tree += print_tree(c, 1)
        return printed_tree

    def print(self):
        print(self.__str__())

    def get_node_from(self, bucket_path):
        """
        Search the tree for the node for a given bucket_path
        :param bucket_path: A path to a directory or file that EXCLUDES the bucket name, for example 'source/year=2018/'
        :return: The COSBucketTreeNode object the represents this dir or file
        """
        def search_node(l, p_node):
            if not l:
                return None
            first = l[0]
            rest = l[1:]
            if first in p_node.list_children():
                curr_node = p_node.get_children().get(first)
                return search_node(rest, curr_node) or curr_node
            return None
        element_list = re.findall(r'.*?\/|.*?\..+', bucket_path)
        return search_node(element_list, self.root)
