from ILP import MCF,Graph_construc
import networkx as nx

numnodes_list = [16,32,64,128]

for numnodes in numnodes_list:
    f = open("../comodity/commo_%d.txt"%numnodes, "r")
    for l in f:
        data = l.split(" ")
        if data[0] == "numnodes":
            numnodes = int(data[2])
            print("numnodes =", numnodes)
        else:
            commo = eval(l)
            g = Graph_construc(numnodes,commo)
            G = nx.DiGraph()
            test_ = []
            for i in range(numnodes):
                for j in range(numnodes):
                    test_.append(int(g[i,j]))
                    G.add_edge(i,j,weight=g[i,j])
            print(test_)
            print(MCF(numnodes,G,commo))
