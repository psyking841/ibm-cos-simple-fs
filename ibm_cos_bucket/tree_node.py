import os

class COSBucketTreeNode:
    """
    This class is to represent a folder/file as a node in the COS Tree.
    """
    def __init__(self, name, parent, children=None):
        """

        :param name: could be a directory name like 'source/' or a file name 'test.txt'
        :param parent:
        :param children: a dict of format {child_name: COSBucketTreeNode object} that represents the children of current node
        """
        self.name = name
        self.parent = parent
        self.children = children or {}
        self.path = self._generate_path()

    def get_name(self):
        return self.name

    def get_parent(self):
        return self.parent

    def get_children(self):
        return self.children

    def get_path(self):
        return self.path

    def _generate_path(self):
        """
        Get the directory representation of a path till current node.
        :return: String representation of a directory
        """
        # If this is root node
        if not self.parent:
            return self.name
        return os.path.join(self.parent.path, self.name)

    def list_children(self):
        """

        :return: All children as string under this node
        """
        return list(self.children.keys())

    def __str__(self):
        return self.path
