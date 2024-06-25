from ILP import MCF
import networkx as nx



f = open("commo.txt", "r")
result = open("result_a2a.txt", "w")

a2a_graph = nx.Graph()

num_nodes = 0
tp_list = []
tp_str = ""
for l in f:
    data = l.split(" ")
    # print(data)
    if data[0] == "numnodes":
        print("num_nodes", num_nodes)
        print(tp_str)
        num_nodes = int(data[2])
        result.write(tp_str + "\n")
        result.write("numnodes = %d \n"%num_nodes)
        a2a_graph = nx.DiGraph()
        for i in range(num_nodes):
            for j in range(num_nodes):
                if i!=j:
                    a2a_graph.add_edge(i,j,weight=1)
        tp_list = []
        tp_str = ""
    else:
        list_of_tuples = eval(l)
        # print(list_of_tuples)
        tp = MCF(num_nodes,a2a_graph,list_of_tuples)
        tp = tp*(num_nodes-1)/num_nodes
        print(tp)
        result.write(str(tp))
        tp_list.append(tp)
        tp_str = "%s_%s"%(tp_str,str(tp))
result.write(str(tp_list))
f.close()
result.close()