# %%
import gurobipy as gp
from gurobipy import GRB
import numpy as np
import networkx as nx
import random

# %%
def random_commo(num_nodes, num_commo):
    commo_set = []
    for _ in range(num_commo):
        i = random.choice([k for k in range(num_nodes)])
        j = random.choice([k for k in range(num_nodes)])
        while i == j or (i,j) in commo_set:
            j = random.choice([k for k in range(num_nodes)])
        commo_set.append((i,j))
    return(commo_set)


# %%
def MCF(num_nodes,Graph,large_commo):

    nodes = [i for i in range(num_nodes)]
    links = list(Graph.edges())
    commoSet = [commo for commo in large_commo]


    allpair = [(a, b) for a in nodes for b in nodes]
    # Gen capacity matrix from input dict graph G
    c = dict()
    for a,b in allpair:
        c[a,b] = 0 
    for i,j in links:
        c[i,j] = 1




    # construct model
    mod = gp.Model('Test')

    mintheta = mod.addVar(vtype = GRB.CONTINUOUS, lb = 0, name = "mintheta")
    Flow = mod.addVars(commoSet, nodes, nodes, vtype = GRB.CONTINUOUS, lb = 0, name = "Flow")
    theta = mod.addVars(commoSet, vtype = GRB.CONTINUOUS, lb = 0, name = "theta")


    mod.addConstrs(sum(Flow[u,v,i,j] for u,v in commoSet) <= Graph[i][j]['weight'] for i,j in links)



    mod.setObjective(sum(theta[u,v] for (u,v) in commoSet) + 10*mintheta , GRB.MAXIMIZE)

    # F_out - F_in = theta[u,v]
    mod.addConstrs(sum(Flow[u,v,i,j] for j in nodes if c[i,j] != 0 and i!=j) - sum(Flow[u,v,j,i] for j in nodes if c[i,j] != 0 and i!=j) == theta[u,v] for u,v in commoSet for i in nodes if i==u)
    mod.addConstrs(sum(Flow[u,v,i,j] for j in nodes if c[i,j] != 0 and i!=j) - sum(Flow[u,v,j,i] for j in nodes if c[i,j] != 0 and i!=j) == -theta[u,v] for u,v in commoSet for i in nodes if i==v)
    mod.addConstrs(sum(Flow[u,v,i,j] for j in nodes if c[i,j] != 0 and i!=j) - sum(Flow[u,v,j,i] for j in nodes if c[i,j] != 0 and i!=j) == 0 for u,v in commoSet for i in nodes if (i!=u and i!=v))

    # flow*Traffic <= capacity(i,j)
    # mod.addConstrs(sum(Flow[u,v,i,j]*traffic[u,v] for u,v in commoSet if traffic[u,v] != 0 ) <= c[i,j] for i,j in allpair if i!=j)
    # mod.addConstrs(sum(Flow[u,v,i,j] for u,v in commoSet if traffic[u,v] == 0 ) == 0 for i,j in allpair if i!=j )
    mod.addConstrs(Flow[u,v,i,j] == 0 for (u,v) in commoSet for i,j in allpair if i!=u and i!=v and j!=u and j!=v)
    mod.addConstrs(Flow[u,v,i,j] >= 0 for (u,v) in commoSet for i,j in allpair if i!=j)

    mod.addConstrs(mintheta <= theta[u,v] for u,v in commoSet)


    #mod.addConstr(sumtheta == sum(theta[u,v] for (u,v) in commoSet))
    mod.Params.LogToconsole = 0



    mod.optimize()
    # print("\n","LP_simple_node_based")
    # print("######################################################")
    # print("               Maximize    sum_theta                  ")
    # print("######################################################\n")

    #print(sumtheta.x)
    sum_theta = 0
    # mod.write("Test.lp")
    for u,v in commoSet:
        if theta[u,v].x != 0:
            # print(u,v, "=>", theta[u,v].x) 
            sum_theta += theta[u,v].x
    # for idx in Flow:
    #     if Flow[idx].x == 0:
    #         continue
    #     print(idx, Flow[idx].x)

    sum_of_weights = 0
    for i in range(num_nodes):
        if Graph.has_edge(0,i):
            sum_of_weights += Graph[0][i]['weight']

    # print(sum_of_weights)
    return sum_theta/sum_of_weights





# %%
def Graph_construc(num_nodes, large_commo):
    N = [n for n in range(num_nodes)]
    # modify


    # order = [i for i in range(num_nodes)]
    # random.shuffle(order)
    # print(order)
    # circle = [(order[i],order[(i+1)%num_nodes]) for i in range(num_nodes)]
    # print(circle)


  

    nodes = [n for n in N]
    links = [(i,j) for i in nodes for j in nodes if i!=j]
    # remove_links = [(0,1), (1,0), (0,2), (2,0), (0,3), (3,0)]
    # for l in remove_links:
    #     links.remove(l)

    # links = [(i,j) for i in N for j in N if i!=j and (x[i,j].x >= 1 or x[j,i].x >= 1)]
    # print(f'links = {links}')
    # commoSet = [(a, b) for a in nodes for b in nodes if a!=b]
    commoSet = large_commo.copy()
    # for i in circle:
    #     if i not in commoSet:
    #         commoSet.append(i)

    # print("commoSet =", commoSet)
    allpair = [(a, b) for a in nodes for b in nodes]
    # print("allpair =", allpair)  
    # Gen capacity matrix from input dict graph G
    c = dict()
    for a,b in allpair:
        c[a,b] = 0 
    for i,j in links:
        c[i,j] = 1


    # print(c)
    traffic = dict()
    for u,v in commoSet:
        traffic[u,v] = 1


    # construct model
    mod = gp.Model('Test')

    mintheta = mod.addVar(vtype = GRB.CONTINUOUS, lb = 0, name = "mintheta")
    Flow = mod.addVars(commoSet, nodes, nodes, vtype = GRB.CONTINUOUS, lb = 0, name = "Flow")
    theta = mod.addVars(commoSet, vtype = GRB.CONTINUOUS, lb = 0, name = "theta")
    max_flow = mod.addVar(lb=0, ub=num_nodes,vtype=GRB.CONTINUOUS, name="max_flow")

    G = mod.addVars(num_nodes, num_nodes, vtype=GRB.INTEGER, lb = 0, name = "Graph")
    # C = mod.addVars(N,N, vtype=GRB.INTEGER, lb = 0, name = "Capacity")
    Degree = mod.addVar(lb = 2, ub = num_nodes-1, name = 'degree')
    # Degree = num_nodes-1
    # Degree = num_nodes

    # k = mod.addVar(lb=1,ub=num_nodes//2, vtype=GRB.INTEGER, name="k")
    # mod.addConstr(Degree == 2*k)
    

    #sumtheta = mod.addVar(vtype = GRB.CONTINUOUS, lb = 0, name = "sumtheta")
    #mod.setObjective(alpha, GRB.MAXIMIZE)
    mod.setObjective(sum(theta[u,v] for (u,v) in large_commo) - max_flow*max_flow -Degree*num_nodes/2, GRB.MAXIMIZE)



    mod.addConstrs(sum(G[i,j] for i in nodes) == Degree for j in nodes)
    mod.addConstrs(G[i,j] == G[j,i] for i in nodes for j in nodes)
    mod.addConstrs(G[i,i] == 0 for i in nodes)
    mod.addConstrs(G[i,j] <= Degree/4 for i in nodes for j in nodes)


    mod.addConstrs(sum(Flow[u,v,i,j] for u,v in commoSet) <= G[i,j] for i in nodes for j in nodes)



    # F_out - F_in = theta[u,v]
    mod.addConstrs(sum(Flow[u,v,i,j] for j in nodes if c[i,j] != 0 and i!=j) - sum(Flow[u,v,j,i] for j in nodes if c[i,j] != 0 and i!=j) == theta[u,v] for u,v in commoSet for i in nodes if i==u)
    mod.addConstrs(sum(Flow[u,v,i,j] for j in nodes if c[i,j] != 0 and i!=j) - sum(Flow[u,v,j,i] for j in nodes if c[i,j] != 0 and i!=j) == -theta[u,v] for u,v in commoSet for i in nodes if i==v)
    mod.addConstrs(sum(Flow[u,v,i,j] for j in nodes if c[i,j] != 0 and i!=j) - sum(Flow[u,v,j,i] for j in nodes if c[i,j] != 0 and i!=j) == 0 for u,v in commoSet for i in nodes if (i!=u and i!=v))

    # flow*Traffic <= capacity(i,j)
    mod.addConstrs(sum(Flow[u,v,i,j]*traffic[u,v] for u,v in commoSet if traffic[u,v] != 0 ) <= G[i,j] for i,j in allpair if i!=j)
    # mod.addConstrs(sum(Flow[u,v,i,j] for u,v in commoSet if traffic[u,v] == 0 ) == 0 for i,j in allpair if i!=j )
    mod.addConstrs(Flow[u,v,i,j] == 0 for (u,v) in commoSet for i,j in allpair if i!=u and i!=v and j!=u and j!=v)
    # mod.addConstrs(Flow[u,v,i,j] >= 0 for (u,v) in commoSet for i,j in allpair if i!=j)


    # mod.addConstrs(sum(Flow[u,v,i,j] for i in nodes for j in nodes) >= 0.1 for u,v in commoSet)

    mod.addConstrs(mintheta <= theta[u,v] for u,v in large_commo)




    mod.addConstrs(max_flow >= Flow[u,v,i,j] for u,v in commoSet for i in nodes for j in nodes if i!=j)
    # mod.addConstr(max_flow <= Degree/4)
    # # # Subtour elimination constraints (Miller-Tucker-Zemlin formulation)
    # d = mod.addVars(num_nodes, vtype=GRB.CONTINUOUS, name="d")
    # mod.addConstrs((d[i] - d[j] + num_nodes * G[i, j] <= num_nodes - 1 for i in nodes for j in nodes if i != j), name="SubtourElimination")
    # mod.addConstr((d[0] == 0), name="FixNode")


    #mod.addConstr(sumtheta == sum(theta[u,v] for (u,v) in commoSet))
    mod.Params.LogToconsole = 0



    mod.optimize()
    # print("\n","LP_simple_node_based")
    # print("######################################################")
    # print("               Maximize    sum_theta                  ")
    # print("######################################################\n")

    #print(sumtheta.x)
    # mod.write("Test.lp")
    # sum_theta = 0
    # for u,v in large_commo:
    #     if theta[u,v].x != 0:
    #         print(u,v, "=>", theta[u,v].x) 

    # for idx in Flow:
    #     if Flow[idx].x == 0:
    #         continue
    #     print(idx, Flow[idx].x)

    # print("degree" ,Degree.x)



    # import networkx as nx
    import numpy as np
    # GG = nx.DiGraph()
    # GG.add_nodes_from(nodes)
    # edges_list = []
    result_adj = np.zeros(shape=(num_nodes, num_nodes))
    for i in nodes:
        for j in nodes:
            if G[i,j].x > 0:
                # GG.add_edge(i,j,weight=int(G[i,j].x))
                # edges_list.append((i,j))
                result_adj[i,j] += int(G[i,j].x)
                # print(i,j,G[i,j].x)
    # nx.draw_circular(GG,with_labels=True)

    return result_adj
