from pyscipopt import Model, quicksum
from contextlib import redirect_stdout
import pandas as pd

class AircraftAllocation:
    def __init__(self,path_of_file):
        self.aircrafts = []
        self.routes = []
        self.costs = []
        self.demand = []
        self.availability  = {(aircraft,route): None for aircraft in self.aircrafts for route in self.routes}
        self.capabilities  ={(aircraft,route): None for aircraft in self.aircrafts for route in self.routes}

    def readData(self,path_of_file):
        AA = pd.read_csv(path_of_file + '//AircraftAssignment_air.csv', index_col=0)
        AR = pd.read_csv(path_of_file + '//AircraftAssignment_route.csv', index_col=0)
        Acost = pd.read_csv(path_of_file + '//AircraftAssignment_cost.csv', index_col=0)
        Acap = pd.read_csv(path_of_file + '//AircraftAssignment_cap.csv', index_col=0)

        self.aircrafts = AA.index.tolist()
        self.routes = AR.index.tolist()
        self.availability = {i: AA.loc[i,'availability'] for i in self.aircrafts}
        self.demand = {i: AR.loc[i,'demand'] for i in self.routes}
        self.capabilities = {(aircraft,route): Acap.iloc[aircraft-1, route-1] for aircraft in self.aircrafts for route in self.routes}
        self.costs = {(aircraft,route): Acost.iloc[aircraft-1, route-1] for aircraft in self.aircrafts for route in self.routes}


    def run(self,taskid):
        # 创建模型
        model = Model("aircraft_allocation")

        # 创建变量
        x = {}
        for i in range(1,len(self.aircrafts)+1):
            for j in range(1,len(self.routes)+1):
                x[(i, j)] = model.addVar(vtype="I", name=f"x[{i},{j}]")
        
        #x = model.addVars(len(self.aircrafts), len(self.routes), vtype="C", name="x")

        # 设置目标函数：最小化总成本
        model.setObjective(quicksum(self.costs[i,j]* x[i, j] for i in self.aircrafts for j in self.routes), "minimize")# 


        # 添加约束条件
        # 1. 满足每条航线的需求
        for j in self.routes:
            model.addCons(quicksum(x[i, j] for i in self.aircrafts) >= self.demand[j], name=f"demand_{j}")
            #model.addConstr(quicksum(x[i, j] for i in self.aircrafts) >= self.demand[j], name=f"demand_{j}")

        # 2. 不超过每架飞机的总载客量
        for i in self.aircrafts:
            model.addCons(quicksum(x[i, j] for j in self.routes) <= self.availability[i], name=f"availability_{i}")

        # 3. 不超过每架飞机在每条航线上的最大载客量
        for i in self.aircrafts:
            for j in self.routes:
                model.addCons(x[i, j] <= self.capabilities[i,j], name=f"capabilities_{i}_{j}")

        # 优化模型
        model.optimize()

        results = ""
        if model.getStatus() == "optimal":
            results += "Optimal solution found:\n"
            for i in range(1,len(self.aircrafts)+1):
                for j in range(1,len(self.routes)+1):
                    var_value = model.getVal(x[(i, j)])
                    results += f"Aircraft {self.aircrafts[i-1]} -> Route {self.routes[j-1]}: {var_value} passengers\n"
        else:
            results += "No optimal solution found.\n"
        return results



def Solve(path_of_file,
    taskid=""
):
    '''
    本模型默认数据集如下所示：
        aircrafts = [1, 2, 3, 4] #飞机集合，包含飞机编号。
        routes = [1, 2, 3, 4],
        availability = [500, 600, 700, 800] #航线集合，包含航线编号。
        demand = [200, 300, 400, 500] #每条航线的需求数量。
        capabilities = [
            [100, 200, 300, 400],
            [200, 300, 400, 500],
            [300, 400, 500, 600],
            [400, 500, 600, 700]
        ] #每架飞机在每条航线上的最大载客量。
        costs = [
            [10, 20, 30, 40],
            [20, 30, 40, 50],
            [30, 40, 50, 60],
            [40, 50, 60, 70]
        ] #将飞机分配到航线的成本。
    '''
    
    dk = AircraftAllocation(path_of_file)
    dk.readData(path_of_file
                )
    results=dk.run(taskid=taskid)
    if results:
        return results

if __name__ == '__main__':
    # 初始化
    path_of_file ='.//input'
    dk = AircraftAllocation(path_of_file)
    Solve(path_of_file,1)
    