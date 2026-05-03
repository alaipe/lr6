import math
import uvicorn #сервер, запускает FastAPI
from fastapi import FastAPI #сам фреймворк

app=FastAPI()

def calc_x_system(S_kz, U): #расчет X энергосистемы
    return U**2/S_kz
def calc_x_transformer(u_k, U_nom, S_nom): #расчет X трансформатора
    return (u_k/100)*(U_nom**2)/S_nom
def calc_r_transformer(P_k, U_nom, S_nom): #расчет R трансформатора
    return (P_k/1000)*(U_nom**2)/(S_nom**2)
def calc_x_line(L, x0): #расчет X линии
    return L*x0
def calc_r_line(L, r0): #расчет R линии
    return L*r0
def calc_z_total(x_total,r_total): #расчет суммарного сопротивления ПП Z
    return math.sqrt(r_total**2+x_total**2)
def privedenie_Z(z, u_from, u_to): #приведение сопротивления к напряжению сети, в которой происходит КЗ
    return z*(u_to/u_from)**2
def calc_i3(u,z): #расчет трехфазного тока КЗ
    return u/(z*math.sqrt(3))
def calc_i2(i3): #расчет двухфазного тока КЗ
    return (math.sqrt(3)/2)*i3

def calculate(data):
    system=data["system"]
    tr=data["transformer"]
    line=data["line"]
    fault_point=data["fault_point"]

    if fault_point=="bus_system": #если точка КЗ на шине ЭЭС, то при приведении используем напряжение ВН ТР
        u_fault=tr["U_vn_nom"]
    else: #если точка КЗ не на шине ЭЭС, то при приведении используем напряжение НН ТР
        u_fault=tr["U_nn_nom"]

    x_system=calc_x_system(system["S_kz"], system["U"]) #считаем сопротивление ЭЭС, приведено к ВН ТР
    x_system_privedennoe=privedenie_Z(x_system, tr["U_vn_nom"], u_fault) #приводим к той ступени напряжения, где происходит КЗ

    if fault_point=="bus_system": #КЗ у шины ЭЭС/на ВН ТР
        x_total=x_system_privedennoe
        r_total=0
    elif fault_point=="bus_nn_tr": #КЗ на НН ТР/в начале ЛЭП
        x_tr_privedennoe=calc_x_transformer(tr["u_k"], u_fault, tr["S_nom"])
        r_tr_privedennoe=calc_r_transformer(tr["P_k"], u_fault, tr["S_nom"])
        x_total=x_system_privedennoe+x_tr_privedennoe
        r_total=r_tr_privedennoe
    elif fault_point=="bus_line": #КЗ в конце ЛЭП
        x_tr_privedennoe=calc_x_transformer(tr["u_k"], u_fault, tr["S_nom"])
        r_tr_privedennoe=calc_r_transformer(tr["P_k"], u_fault, tr["S_nom"])
        x_line_privedennoe=calc_x_line(line["L"], line["x0"])
        r_line_privedennoe=calc_r_line(line["L"], line["r0"])
        x_total=x_system_privedennoe+x_tr_privedennoe+x_line_privedennoe
        r_total=r_tr_privedennoe+r_line_privedennoe
    else:
        x_total=0
        r_total=0
    z_total=calc_z_total(x_total, r_total)
    if z_total>0:
        i3=calc_i3(system["U"]*u_fault/tr["U_vn_nom"], z_total)
        i2=calc_i2(i3)
    else:
        i3=0
        i2=0
    return {
        "fault_point": fault_point,
        "r_total_ohm": r_total,
        "x_total_ohm": x_total,
        "z_total_ohm": z_total,
        "i3_ka": i3,
        "i2_ka": i2,
    }

LAST_DATA={}

@app.post("/scheme")
def post_calc(data: dict):
    global LAST_DATA
    LAST_DATA = data
    return {"status": "ok"}

@app.get("/scheme")
def get_scheme():
    return LAST_DATA

@app.get("/calculate_kz")
def get_calc():
    if LAST_DATA!={}:
        return calculate(LAST_DATA)
    else:
        return {"status": "Not loaded scheme"}

if __name__=="__main__":
    uvicorn.run("server:app",host="localhost",port=8080,reload=True)