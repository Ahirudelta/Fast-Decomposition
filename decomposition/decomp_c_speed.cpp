#include <iostream>
#include <vector>
#include <random>
#include <algorithm>
#include <cmath>
#include "gurobi_c++.h"
#include <climits>
#include <map>
#include <chrono>

#include <fstream>
#include <sstream>
#include <string>
#include <chrono>




using namespace std;


vector<vector<vector<int>>> decomp(vector<vector<int>> &arr){
    int num_nodes = arr.size();
    int degree = 0;
    for (int i = 0; i < num_nodes; i++){
        degree += arr[0][i];
    }
    int max_degree = degree;
    cout << "degree " << degree << endl;

    vector<vector<vector<int>>> mat_list;

    bool finish = true;
    for (int d = 0; d< max_degree; d++){


        GRBEnv env = GRBEnv(true);
        env.set("OutputFlag","0");
        env.start();

        GRBModel decomp_no_objective = GRBModel(env); // also norandom
        // GRBModel decomp_objective = GRBModel(env);


        vector<vector<GRBVar>> matching(num_nodes, vector<GRBVar>(num_nodes));

        for (int i=0; i<num_nodes; i++){
            for (int j=0; j<num_nodes; j++){
                matching[i][j] = decomp_no_objective.addVar(0.0,1.0,0.0,GRB_BINARY);
            }
        }


        // *****************************************
        for (int i = 0; i < num_nodes; ++i) {
            for (int j = 0; j < num_nodes; ++j) {
                decomp_no_objective.addConstr(matching[i][j] <= arr[i][j]);
            }
        }
        // *****************************************


        // fix constraints
        for (int i = 0; i<num_nodes; i++) {
            GRBLinExpr expr = 0;
            for(int j = 0; j<num_nodes; j++){
                decomp_no_objective.addConstr(matching[i][j] == matching[j][i]);
                expr += matching[i][j];
            }
            decomp_no_objective.addConstr(expr == 1);
        }

        decomp_no_objective.optimize();


        int optimstatus = decomp_no_objective.get(GRB_IntAttr_Status);

        if (optimstatus == GRB_OPTIMAL){
            vector<vector<int>> mat(num_nodes, vector<int>(num_nodes,0));
            for (int i = 0; i < num_nodes; i++){
                for (int j = 0; j < num_nodes; j++){
                    mat[i][j] = round(matching[i][j].get(GRB_DoubleAttr_X));
                    arr[i][j] -= mat[i][j];
                }
            }
            mat_list.push_back(mat);
            degree-=1;
        }
        else{
            // cout << "cannot grab one " << endl;
            // cout << "degree " << degree << endl;
            finish = false;
            break;
        }
    }



    while (!finish){
        // cout << "start decomp all " << endl;
        degree += 1;
        for (int i = 0; i<num_nodes; i++){
            for (int j = 0; j < num_nodes; j++){
                arr[i][j] += mat_list.back()[i][j];
            }
        }
        mat_list.pop_back();

        GRBEnv env = GRBEnv(true);
        env.set("OutputFlag","0");
        env.start();

        GRBModel decomp_objective = GRBModel(env);


        vector<vector<vector<GRBVar>>> matching_set(degree, vector<vector<GRBVar>>(num_nodes,vector<GRBVar>(num_nodes)));


        for (int d = 0; d < degree; d++) {
            for (int i = 0; i < num_nodes; i++) {
                for (int j = 0; j < num_nodes; j++) {
                    matching_set[d][i][j] = decomp_objective.addVar(0.0, 1.0, 0.0, GRB_BINARY);
                }
            }
        }


        for (int i = 0;i<num_nodes;i++){
            for (int j = 0; j<num_nodes;j++){
                GRBLinExpr expr = 0;
                for (int d = 0; d < degree; d++) {
                    expr += matching_set[d][i][j];
                }
                decomp_objective.addConstr(expr <= arr[i][j]);
            }
        }


        for (int d = 0; d < degree; d++) {
            for (int i = 0; i < num_nodes; i++) {
                GRBLinExpr expr = 0;
                for (int j = 0; j < num_nodes; j++) {
                    expr += matching_set[d][i][j];
                    decomp_objective.addConstr(matching_set[d][i][j] == matching_set[d][j][i]);

                }
                decomp_objective.addConstr(expr == 1);
            }
        }
        decomp_objective.optimize();

        int optimstatus = decomp_objective.get(GRB_IntAttr_Status);
        if (optimstatus == GRB_OPTIMAL){
            for (int d = 0; d<degree;d++){
                vector<vector<int>> temp(num_nodes, vector<int>(num_nodes,0));
                for (int i = 0; i < num_nodes;i++){
                    for (int j = 0; j<num_nodes;j++){
                        temp[i][j] = round(matching_set[d][i][j].get(GRB_DoubleAttr_X));
                    }
                }
                mat_list.push_back(temp);
            }
            finish = true;
        }
        // else{
        //     std::cerr << "cannot decomp" << std::endl;
        //     std::exit(EXIT_FAILURE);
        // }

    }

    return mat_list;
}





std::vector<int> parseLine(const std::string &line) {
    std::vector<int> result;
    std::stringstream ss(line);
    std::string temp;

    // Remove the leading '[' and trailing ']'
    std::string cleanedLine = line.substr(1, line.size() - 2);
    ss.str(cleanedLine);

    while (std::getline(ss, temp, ',')) {
        result.push_back(std::stoi(temp));
    }

    return result;
}


int main(int argc, char const *argv[])
{
    std::ifstream inputFile("topo_2_16.txt");
    std::string line;
    std::vector<std::vector<int>> allData;

    if (!inputFile.is_open()) {
        std::cerr << "Unable to open file" << std::endl;
        return 1;
    }

    while (std::getline(inputFile, line)) {
        std::vector<int> lineData = parseLine(line);
        allData.push_back(lineData);
    }

    inputFile.close();


    int input_num_nodes = 16;
    int Nsw = 3;
    ofstream Myfile("test_tp_16.txt");

    for (vector<int> one_line: allData){
        vector<vector<int>> arr;
        // int count = 1;
        vector<int> temp_vec;
        for (int i = 0; i < (int)one_line.size();i++){
            temp_vec.push_back(one_line[i]);
            // cout << i << " ";
            if (i>0 && (i+1)%input_num_nodes == 0){
                // cout << "helo 2" << endl;
                // cout << "temvec_size " << temp_vec.size() << endl;
                arr.push_back(temp_vec);
                temp_vec = {};
                // count = 1;
            }
            // count++;
        }
        

        // for (vector<int> vec : arr){
        //     for (int i : vec){
        //         cout << i << " ";
        //     }
        //     cout << endl;
        // }
        // cout << "-----------" << endl;
        // cout << "hello " << endl;
        auto start = std::chrono::high_resolution_clock::now();
        vector<vector<vector<int>>> result = decomp(arr);
        auto end = std::chrono::high_resolution_clock::now();

        auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end - start);

        std::cout << duration.count() << std::endl;
        Myfile << duration.count() << endl;
    }
    Myfile.close();

    return 0;


    return 0;
}
