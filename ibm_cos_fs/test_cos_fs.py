from ibm_cos_fs.bucket_tree import COSBucketTree


def test_tree():
    flat_object_list = [
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
        "source/year=2019/month=01/day=01/test.txt",
        "source/year=2020/month=01/"
    ]

    tree = COSBucketTree(bucket_name='test-bucket', object_list=flat_object_list)
    r = tree.get_leaf_paths() # From root node
    assert(r == ['test-bucket/source/year=2018/month=08/day=28/test1.txt',
                 'test-bucket/source/year=2018/month=08/day=28/test.txt',
                 'test-bucket/source/year=2018/month=08/day=29/test.txt',
                 'test-bucket/source/year=2018/month=08/day=30/test.txt',
                 'test-bucket/source/year=2018/month=08/day=31/test.txt',
                 'test-bucket/source/year=2019/month=01/day=01/test.txt',
                 'test-bucket/source/year=2020/month=01/'])

    t = str(tree)
    assert(t ==
'''\
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
   └─ year=2020/ 
      └─ month=01/ 
''')
    print(t)

    node0 = tree.get_node_from_path('mybucket/source/year=2018/month=08/')
    contents0 = node0.ls()
    assert(contents0 == ['day=28/', 'day=29/', 'day=30/', 'day=31/'])

    # Test change directory
    node = tree.get_node_from_key('source/year=2018/month=08/')

    # Test list the contents under directory; use children property to return all children nodes
    contents = node.ls()
    assert(contents == ['day=28/', 'day=29/', 'day=30/', 'day=31/'])

    assert([l.path for l in tree.get_leaves(node)] == ['test-bucket/source/year=2018/month=08/day=28/test1.txt',
                                                           'test-bucket/source/year=2018/month=08/day=28/test.txt',
                                                           'test-bucket/source/year=2018/month=08/day=29/test.txt',
                                                           'test-bucket/source/year=2018/month=08/day=30/test.txt',
                                                           'test-bucket/source/year=2018/month=08/day=31/test.txt'])

    # Test searching all leaf nodes under this directory
    assert(tree.get_leaf_paths(node) == ['test-bucket/source/year=2018/month=08/day=28/test1.txt',
                                              'test-bucket/source/year=2018/month=08/day=28/test.txt',
                                              'test-bucket/source/year=2018/month=08/day=29/test.txt',
                                              'test-bucket/source/year=2018/month=08/day=30/test.txt',
                                              'test-bucket/source/year=2018/month=08/day=31/test.txt'])

    # Return leaves as boto3 keys
    assert(tree.get_leaf_keys(node) == ['source/year=2018/month=08/day=28/test1.txt',
                                           'source/year=2018/month=08/day=28/test.txt',
                                           'source/year=2018/month=08/day=29/test.txt',
                                           'source/year=2018/month=08/day=30/test.txt',
                                           'source/year=2018/month=08/day=31/test.txt'])
    # Test common parent, this is reverse operation to get_leaves()
    common = tree.get_common_parent_for_leaves(tree.get_leaves(node))
    assert(common.path == 'test-bucket/source/year=2018/month=08/')


def test_tree1():
    flat_object_list = [
        "source/",
        "test1.txt",
        "test2.txt",
    ]

    tree = COSBucketTree(bucket_name='test-bucket', object_list=flat_object_list)
    all_leaf_nodes = tree.get_leaves()
    assert([str(l) for l in all_leaf_nodes] == ['test-bucket/source/',
                                                'test-bucket/test1.txt',
                                                'test-bucket/test2.txt'])
    assert([l.key for l in all_leaf_nodes] == ['source/', 'test1.txt', 'test2.txt'])
    assert([l.is_dir for l in all_leaf_nodes] == [True, False, False])

    root = tree.root
    assert([c.key for c in root.children if not c.is_dir] == ['test1.txt', 'test2.txt'])


test_tree()
test_tree1()
