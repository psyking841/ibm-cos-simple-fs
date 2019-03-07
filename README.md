# IBM Cloud Object Storage Simple File System Library

## Problems with ibm_boto3 library
The IBMCloud Cloud Object Service has very awful representation of objects under a bucket.

For example, if you are using ibm_boto3, you can only list all objects under a bucket so that you will probably end up 
with a Python List of objects in that bucket, such as:

```python
[
    "source/",
    "source/year=2018/",
    "source/year=2018/month=08/",
    "source/year=2018/month=08/day=28/",
    "source/year=2018/month=08/day=28/test1.txt",
    "source/year=2018/month=08/day=28/test.txt",
    "source/year=2018/month=08/day=29/",
    "source/year=2018/month=08/day=29/test.txt",
    "source/year=2018/month=08/day=30/",
    "source/year=2018/month=08/day=30/test.txt",
    "source/year=2018/month=08/day=31/",
    "source/year=2018/month=08/day=31/test.txt",
    "source/year=2019/month=01/day=01/",
    "source/year=2019/month=01/day=01/test.txt" 
]
```

This is really awful when you are trying to get the "real objects" (i.e. those test.txt files in above example).

## What this library does?
This library adds a presentation layer above boto3, which expresses the flat representation of objects in a bucket (i.e. Python list) as a tree-like data structure. As such, the bucket 
can be represented as a file system, with the concepts of folders/directories and files. Currently, this library is able to simulate file
system commands such as "cd" and "ls". See the Usages in next section.

For the above bucket objects, this library will represent it as

```
test-bucket/ 
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
```

## Concepts
* Boto3 object and Key: in boto3, an object's key is represented as string like "test-bucket/source/".
* Path: a path in this simple FS starts with bucket name, for example a path "test-bucket/source/" represents boto3 object "source/".
* Leaves: a leaf is a COSBucketTreeNode object whose boto3 object representation is NOT a common prefix for any other boto3 objects. For example, "source/year=2018/month=08/day=28/test1.txt" in above example is a leaf's boto3 object representation.

## Installation
Project is available at Pypi: https://pypi.org/project/ibm-cos-simple-fs/
```
pip install ibm-cos-simple-fs
```

## Usage
**Note, paths output from this library is ALWAYS appended by bucket name thus in the form of 'bucket_name/path/to/your/stuff.txt'.
When using paths with boto3 library, please post-process them to ignore the "bucket_name/" part.**
**However, ```get_node_from()``` from tree object is designed to convert boto3 path representation to internal tree representation, so it will take boto3 path.**
```
> from ibm_cos_sfs.bucket_tree import COSBucketTree

# Given flat_object_list being the one in Problem Statement, building a tree structure using
> tree = COSBucketTree(bucket_name='test-bucket', object_list=flat_object_list)

# Get all leaves as path string
> leaf_paths = tree.get_leaf_paths()

# Print the flat objects representation to be a tree
> tree.print() 

# To get all the children nodes of a given path, say 'source/year=2018/month=8/'
> node = tree.get_node_from('source/year=2018/month=8/') # This is to simulate 'cd source/year=2018/month=8/' in a file system.
> node.get_children() # To get the children_name to children_node map
# Or
> node.list_children() # To get a list of children as string. This is to simulate 'ls source/year=2018/month=8/' in a file system.

# To get all the leaves under a given path, say 'source/year=2018/month=8/day=29/'
> node = tree.get_node_from('source/year=2018/month=8/day=29/') 
> leaf_nodes = tree._search_leaves(node) 
# These are a list of tree nodes, you can then convert them to str representation by
> [str(l) for l in leaf_nodes] # or [l.path for l in leaf_nodes]
# In addition, you can get leaves as boto3 keys
> [l.key for l in leaf_nodes]

# To get the directory that contains all given leaves
> common_parent_node = tree.get_common_parent_for_leaves(leaf_nodes)
```

## Creator
Copyright © 2019 Shengyi Pan
