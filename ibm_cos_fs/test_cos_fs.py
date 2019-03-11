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
    r = tree.get_leaf_paths()
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
    contents0 = node0.list_children()
    assert(contents0 == ['day=28/', 'day=29/', 'day=30/', 'day=31/'])

    # Test change directory
    node = tree.get_node_from_key('source/year=2018/month=08/')

    # Test list the contents under directory; use children property to return all children nodes
    contents = node.list_children()
    assert(contents == ['day=28/', 'day=29/', 'day=30/', 'day=31/'])

    # Test searching all leaf nodes under this directory
    leaf_nodes = tree.search_leaves(node)
    assert([l.path for l in leaf_nodes] == ['test-bucket/source/year=2018/month=08/day=28/test1.txt',
                                              'test-bucket/source/year=2018/month=08/day=28/test.txt',
                                              'test-bucket/source/year=2018/month=08/day=29/test.txt',
                                              'test-bucket/source/year=2018/month=08/day=30/test.txt',
                                              'test-bucket/source/year=2018/month=08/day=31/test.txt'])

    # Return leaves as boto3 keys
    assert([l.key for l in leaf_nodes] == ['source/year=2018/month=08/day=28/test1.txt',
                                           'source/year=2018/month=08/day=28/test.txt',
                                           'source/year=2018/month=08/day=29/test.txt',
                                           'source/year=2018/month=08/day=30/test.txt',
                                           'source/year=2018/month=08/day=31/test.txt'])
    # Test common parent
    common = tree.get_common_parent_for_leaves(leaf_nodes)
    assert(common.path == 'test-bucket/source/year=2018/month=08/')


def test_tree1():
    flat_object_list = [
        "source/",
        "test1.txt",
        "test2.txt",
    ]

    tree = COSBucketTree(bucket_name='test-bucket', object_list=flat_object_list)
    all_leaf_nodes = tree.search_leaves()
    assert([str(l) for l in all_leaf_nodes] == ['test-bucket/source/',
                                                'test-bucket/test1.txt',
                                                'test-bucket/test2.txt'])
    assert([l.key for l in all_leaf_nodes] == ['source/', 'test1.txt', 'test2.txt'])
    assert([l.is_dir for l in all_leaf_nodes] == [True, False, False])


test_tree()
test_tree1()
