import os
import re

class COSBucketTreeNode:
    """
    This class is to represent a folder/file as a node in the COS Tree.
    """
    def __init__(self, name, parent, children_map=None):
        """

        :param name: could be a directory name like 'source/' or a file name 'test.txt'
        :param parent: parent node of current node
        :param children_map: a dict of format {child_name: COSBucketTreeNode object} that represents the children of current node
        :param children: a dict of format {child_name: COSBucketTreeNode object} that represents the children of current node
        :param path: internal representation of object, which includes the bucket name
        :param key: boto3 representation of object, which excludes the bucket name
        :param is_dir: whether or not this node represents a directory
        """
        self._name = name
        self._parent = parent
        self._children_map = children_map or {}
        self._path = self._generate_path()
        self._key = self._generate_key()
        self._is_dir = False

    @property
    def name(self):
        return self._name

    @property
    def parent(self):
        return self._parent

    @property
    def children_map(self):
        return self._children_map

    @property
    def children(self):
        return None if not self._children_map else self._children_map.values()

    @property
    def path(self):
        return self._path

    @property
    def key(self):
        return self._key

    @property
    def is_dir(self):
        return True if re.match(r'.+(?=\/)', self.name) else False

    def _generate_key(self):
        """
        Generate the boto3 key name.
        :return:
        """
        if not self.parent:
            return None
        elif not self.parent.key:
            return self.name
        return os.path.join(self.parent.key, self.name)

    def _generate_path(self):
        """
        Get the directory representation of a path till current node.
        :return: String representation of a directory
        """
        # If this is root node
        if not self.parent:
            return self.name
        return os.path.join(self.parent.path, self.name)

    def ls(self):
        """

        :return: All children as object keys under this node
        """
        return list(self.children_map.keys())

    def __str__(self):
        return self.path
