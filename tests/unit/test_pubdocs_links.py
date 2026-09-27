import unittest, os, re
H = os.path.dirname(os.path.abspath(__file__)); W = os.path.join(H, "..", "..")
P = os.path.join(W, "pubdocs")
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


class PubdocsLinks(unittest.TestCase):
    def docs(self):
        return [f for f in sorted(os.listdir(P)) if f.endswith(".md")]

    def test_index_lists_every_document(self):
        index = open(os.path.join(P, "README.md")).read()
        for f in self.docs():
            if f != "README.md":
                self.assertIn(f, index, "not linked from the index: " + f)

    def test_relative_links_resolve(self):
        for f in self.docs():
            for target in LINK.findall(open(os.path.join(P, f)).read()):
                if target.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                path = os.path.normpath(os.path.join(P, target.split("#")[0]))
                self.assertTrue(os.path.exists(path), "%s -> %s" % (f, target))


if __name__ == "__main__": unittest.main()
