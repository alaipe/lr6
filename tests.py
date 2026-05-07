import math
import unittest
from server import calc_x_system, calc_x_transformer, calc_r_transformer, calc_x_line, calc_r_line, calc_z_total, privedenie_Z, calc_i3, calc_i2, calculate

data={
    "system": {
        "S_kz": 80,
        "U": 220
    },
    "transformer": {
        "S_nom": 80,
        "U_vn_nom": 242,
        "U_nn_nom": 10.5,
        "u_k": 11,
        "P_k": 320,
        "type": "ТДЦ-80000/220 У(ХЛ)"
    },
    "line": {
        "L": 50,
        "x0": 0.406,
        "r0": 0.204,
        "marka": "АС 150/19"
    },
    "fault_point": "bus_system"
}

class TestFunctions(unittest.TestCase):
    def test_calc_x_system(self):
        #X=220*220/80=605
        self.assertAlmostEqual(calc_x_system(80, 220),605,places=0)
    def test_calc_x_transformer(self):
        #X=0,11*10,5^2/80=0,15159375
        self.assertAlmostEqual(calc_x_transformer(11,10.5,80),0.15159375,places=4)
    def test_calc_r_transformer(self):
        #R=0,32*10.5^2/80^2=0,0055125
        self.assertAlmostEqual(calc_r_transformer(320,10.5,80),0.0055125,places=5)
    def test_calc_x_line(self):
        #X=50*0,406=20,3
        self.assertAlmostEqual(calc_x_line(50,0.406),20.3,places=1)
    def test_calc_r_line(self):
        #R=50*0,204=10,2
        self.assertAlmostEqual(calc_r_line(50,0.204),10.2, places=1)
    def test_calc_z_total(self):
        x=10
        r=5
        self.assertAlmostEqual(calc_z_total(x, r), math.sqrt(x**2+r**2), places=4)
    def test_privedenie_Z(self):
        self.assertAlmostEqual(privedenie_Z(605.0,242,10.5),1.1389462809917355371900826446281,places=4)
    def test_calc_i3(self):
        #10,5/(1,5*3^0,5)=4,0414518843273803515640414635137
        self.assertAlmostEqual(calc_i3(10.5,1.5),4.0414518843273803515640414635137, places=4)
    def test_calc_i2(self):
        #3^0,5/2=0,86602540378443864676372317075294
        self.assertAlmostEqual(calc_i2(1), 0.86602540378443864676372317075294, places=4)

    def test_bus_system(self):
        r=calculate({**data})
        self.assertAlmostEqual(r["i3_ka"], 0.2099,places=4)
    def test_bus_nn_tr(self):
        r=calculate({**data, "fault_point": "bus_nn_tr"})
        self.assertAlmostEqual(r["i3_ka"], 4.2703,places=4)
    def test_bus_line(self):
        r=calculate({**data, "fault_point": "bus_line"})
        self.assertAlmostEqual(r["i3_ka"], 0.2307,places=4)
if __name__ == "__main__":
    unittest.main()