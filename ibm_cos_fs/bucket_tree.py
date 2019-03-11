import os
import re
from ibm_cos_fs.bucket_tree_node import COSBucketTreeNode


class COSBucketTree:
    """
    This class is to convert the flat representation of IBMCloud COS bucket to a tree representation.

    For example, given a list (flat) representation of all objects (in string) under a bucket "mybucket":
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

    Such a list can typically be obtained from
    >>> [o.key for o in cos_resources.objects.all()]

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
        """
        :param bucket_name: String, name of the bucket
        :param object_list: List of Strings, keys in the form of String in the bucket
        """
        self.bucket_name = self.__validate_bucket_name(bucket_name)
        self.object_list = self.__validate_object_list(object_list)
        self.root = self.__populate_tree(bucket_name, object_list)

    def __validate_bucket_name(self, bucket_name):
        """
        Validate bucket name
        :param bucket_name:
        :return:
        """
        if not isinstance(bucket_name, str):
            raise ValueError('Bucket name should be of type String.')
        return bucket_name

    def __validate_object_list(self, object_list):
        """
        Validate the object_list is a list of strings.
        :param object_list:
        :return:
        """
        res = [o for o in object_list if isinstance(o, str)]
        if len(res) != len(object_list):
            raise ValueError('Object list should be a list of strings. \
            You probably have ObjectSummary object(s) in the list.')

    def __populate_tree(self, bucket_name, object_list):
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
            if first not in node.children.keys():
                node.children.update({first: COSBucketTreeNode(first, node)})

            return add_node(rest, node.children.get(first))

        root = COSBucketTreeNode(os.path.join(bucket_name, ''), None)
        for obj_str in object_list:
            element_list = re.findall(r'.*?\/|.*?\..+', obj_str)
            add_node(element_list, root)

        return root

    def __search_leaves(self, node):
        """
        Helper method for searching leaves from a node
        :param args: The length of args should be exactly one that represents a BucketTreenode from which the leaves will be searched. If left empty, will search from root.
        :return:
        """
        if not node.children:
            return [node]
        res = []
        for k,c in node.children.items():
            res += self.__search_leaves(c)
        return res

    def get_leaves(self, node=None):
        """
        Get all leaves from a node
        :param node:
        :return:
        """
        node = node or self.root
        return self.__search_leaves(node)

    def get_leaf_paths(self, node=None):
        """
        Return all leaves of this tree in the form of paths
        :return:
        """
        return [c.path for c in self.__search_leaves(self.root if not node else node)]

    def get_leaf_keys(self, node=None):
        """
        This method is to output key names that is compatible to boto3.
        For example, the key for a leaf path 'mybucket/source/' is 'source/' or the key for a leaf path mybucket/a.txt is a.txt
        :return:
        """
        return [c.key for c in self.__search_leaves(self.root if not node else node)]

    def get_common_parent_for_leaves(self, leaves):
        """
        Given a list of leaf paths, return their common parent node
        :param: a list of COSTreeNode
        :return: TreeNode
        """
        if not leaves:
            return None

        def get_common(node, leaf1, leaf2):
            if leaf1.path == leaf2.path:
                return leaf1

            if leaf1.path == node.path:
                return leaf1

            if leaf2.path == node.path:
                return leaf2

            if not node.children:
                return None

            x = []
            for k, c in node.children.items():
                x.append(get_common(c, leaf1, leaf2))

            #Check if this node is a common parent
            y = [i for i in x if i]
            if len(y) == 1:
                return y[0]
            elif len(y) == 2:
                return node
            else:
                return None

        res = leaves[0]
        if len(leaves) == 1:
            return res

        for i in range(len(leaves) - 1):
            res = get_common(self.root, res, leaves[i + 1])
        return res

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
            for k,c in node.children.items():
                res += print_tree(c, level + 1)
            return res

        printed_tree = self.bucket_name + '/ \n'
        for k, c in self.root.children.items():
            printed_tree += print_tree(c, 1)
        return printed_tree

    def print(self):
        print(self.__str__())

    def __search_node(self, element_list, parent_node):
        """

        :param element_list: Such as ['source/', 'year=2018/']
        :param parent_node: The parent node of the node represented by the element_list
        :return:
        """
        if not element_list:
            return None
        first = element_list[0]
        rest = element_list[1:]
        if first in parent_node.list_children():
            curr_node = parent_node.children.get(first)
            return self.__search_node(rest, curr_node) or curr_node
        return None

    def get_node_from_key(self, key):
        """
        Search the tree for the node for a given boto3 object key
        :param key: Name of the  'source/year=2018/'
        :return: The COSBucketTreeNode object the represents this dir or file
        """
        element_list = re.findall(r'.*?\/|.*?\..+', key)
        return self.__search_node(element_list, self.root)

    def get_node_from_path(self, path):
        """
        Search the tree for the node for a given path
        :param key: Name of the  'mybucket/source/year=2018/'
        :return: The COSBucketTreeNode object the represents this dir or file
        """
        element_list = re.findall(r'.*?\/|.*?\..+', path)[1:]
        return self.__search_node(element_list, self.root)
