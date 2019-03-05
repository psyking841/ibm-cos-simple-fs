from ibm_cos_sfs.bucket_tree import COSBucketTree

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


def test_tree():
    tree = COSBucketTree(bucket_name='test-bucket', object_list=flat_object_list)
    r = tree.get_leaves_paths()
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

    # Test change directory
    node = tree.get_node_from('source/year=2018/month=08/')

    # Test list directory
    contents = node.list_children()
    assert(contents == ['day=28/', 'day=29/', 'day=30/', 'day=31/'])

    leaves_nodes = tree._search_leaves(node)
    assert([str(l) for l in leaves_nodes] == ['test-bucket/source/year=2018/month=08/day=28/test1.txt',
                                              'test-bucket/source/year=2018/month=08/day=28/test.txt',
                                              'test-bucket/source/year=2018/month=08/day=29/test.txt',
                                              'test-bucket/source/year=2018/month=08/day=30/test.txt',
                                              'test-bucket/source/year=2018/month=08/day=31/test.txt'])

test_tree()