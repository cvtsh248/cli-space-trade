import json
import math
import random
from dataclasses import dataclass, asdict

'''
star:
    planets:
        moons

''' 

@dataclass
class Star:
    name: str
    luminosity: float
    mass_su: float
    radius_au: float

@dataclass
class Moon:
    name: str

@dataclass
class Planet:
    name: str
    semi_major_axis_au: float
    current_orbit_angle: float
    moons: list[Moon]

@dataclass
class SolarSystem:
    star: Star


class SolarSystemGen:

    T_FROST: float = 170 # kelvin
    T_DUST_SUBLIMATION: float = 1500 # kelvin


    @staticmethod
    def calculate_star_frost_line(luminosity: float) -> float: # sublimation limit for water, au
        return ((278*(luminosity**0.25))/SolarSystemGen.T_FROST)**2
    
    @staticmethod
    def calculate_inner_planet_edge(luminosity: float) -> float: # sublimation limit for planets, au
        return ((278*(luminosity**0.25))/SolarSystemGen.T_DUST_SUBLIMATION)**2

    @staticmethod
    def calculate_outer_planet_edge(mass: float) -> float:
        return 100*(mass**0.333)
    
    @staticmethod
    def calculate_star_radius(mass: float) -> float:
        if mass >= 1:
            return mass**0.57
        elif mass < 1:
            return mass**0.8
        else:
            return Exception("Eh?!")

    @staticmethod
    def generate_system() -> SolarSystem:
        s_luminosity = random.random(0.1,100)
        s_mass = random.random(0.1,100)
        planet_count = random.randint(5,15)

        star = { # No position as position is assumed to be 0,0
            "name":"x",
            "luminosity":s_luminosity,
            "mass_su":s_mass, # solar units; planets will be considered under a seperate unit relative to Earth
            "radius_au": SolarSystemGen.calculate_star_radius(s_mass)
        }

        for i in range(0,planet_count):
            inner_edge = SolarSystemGen.calculate_inner_planet_edge(star.luminosity)
            step = random.random(1,3)
            planet = {
                "name":"x",
                "semi_major_axis_au":step*i
            }
    
    @staticmethod
    def generate_system_json() -> dict:
        system = SolarSystemGen.generate_system()
        jsonified = json.dumps(asdict(system))

        return jsonified
        