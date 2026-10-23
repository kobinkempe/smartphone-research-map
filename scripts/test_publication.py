"""Check that valid annotations cannot conceal a wrong publication destination."""
import unittest
from check_publication import Links, check_dependency_destination

REGISTRY={'nodes':[{'id':'speaker'},{'id':'wire'},{'id':'glass'}],
          'routes':[{'id':'make-speaker','output':'speaker'}]}

class DestinationTests(unittest.TestCase):
    def node_link(self,href='../nodes/wire.html',page='nodes/wire'):
        return {'href':href,'data-page':page,'data-dependency-source':'make-speaker','data-dependency-target':'wire'}

    def test_valid_annotation_with_wrong_page_or_href_is_rejected(self):
        for attrs in (self.node_link(href='../nodes/glass.html'),self.node_link(page='nodes/glass')):
            with self.assertRaises(ValueError):check_dependency_destination(attrs,'nodes/speaker',Links(),REGISTRY)
        check_dependency_destination(self.node_link(),'nodes/speaker',Links(),REGISTRY)

    def test_route_link_must_open_correct_output_and_identified_route(self):
        attrs={'href':'#making','data-dependency-source':'speaker','data-dependency-target':'make-speaker'}
        parser=Links();parser.feed('<h2 id="making" data-route-id="make-speaker">Making</h2>')
        check_dependency_destination(attrs,'nodes/speaker',parser,REGISTRY)
        for key,view in (('nodes/glass',parser),('nodes/speaker',Links())):
            with self.assertRaises(ValueError):check_dependency_destination(attrs,key,view,REGISTRY)

    def test_standalone_destination_is_also_bound(self):
        check_dependency_destination(self.node_link('nodes/wire.html'),'nodes/speaker',Links(),REGISTRY,True)
        with self.assertRaises(ValueError):
            check_dependency_destination(self.node_link('nodes/glass.html'),'nodes/speaker',Links(),REGISTRY,True)

    def test_cached_paths_do_not_allow_a_different_target(self):
        cache={}
        check_dependency_destination(self.node_link(),'nodes/speaker',Links(),REGISTRY,resolution_cache=cache)
        with self.assertRaises(ValueError):
            check_dependency_destination(self.node_link(href='../nodes/glass.html'),'nodes/speaker',Links(),REGISTRY,resolution_cache=cache)

if __name__=='__main__':unittest.main()
