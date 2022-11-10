from agents.hybrid_agent import KnowledgeBase

test_KB = KnowledgeBase()

c1 = [(True, "a"),(True, "b")]
c2 = [(False, "a"),(True, "b")]
#c2 = [(False, "a"),(False, "b")]

test_KB.tell(c1)
test_KB.tell(c2)
test_KB.resolution()