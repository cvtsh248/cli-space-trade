import json
import math
import uuid
# import numpy as np
import random
from dataclasses import dataclass, asdict
from enum import StrEnum
import config.constants as constants

'''
star:
    planets:
        moons

''' 

class PlanetType(StrEnum):
    TERRESTRIAL_ROCKY = "terrestrial_rocky"
    GAS_GIANT = "gas_giant"
    ICE_GIANT = "ice_giant"

@dataclass
class Star:
    id: str
    name: str
    luminosity: float
    mass_kg: int
    radius_km: int

@dataclass
class Moon:
    id: str
    name: str
    semi_major_axis_km: int
    current_orbit_angle: float

@dataclass
class Planet:
    id: str
    name: str
    planet_type: PlanetType
    semi_major_axis_km: int
    current_orbit_angle: float
    mass_kg: int
    radius_km: int
    moons: list[Moon]

@dataclass
class SolarSystem:
    star: Star
    planets: list[Planet]


class SolarSystemGen:

    @staticmethod
    def calculate_star_frost_line(luminosity: float) -> int: # sublimation limit for water, km
        return int(((278*(luminosity**0.25))/constants.T_FROST)**2)*constants.AU_TO_KM_RATIO
    
    @staticmethod
    def calculate_inner_planet_edge(luminosity: float) -> int: # sublimation limit for planets, km
        return int(((278*(luminosity**0.25))/constants.T_DUST_SUBLIMATION)**2)*constants.AU_TO_KM_RATIO
    

    @staticmethod
    def calculate_outer_planet_edge(mass: int) -> int:
        return int(100*((mass*constants.KG_TO_SOLAR_MASS_RATIO)**0.333))*constants.AU_TO_KM_RATIO
    
    @staticmethod
    def calculate_star_radius(mass: int) -> int:
        if mass >= constants.KG_TO_SOLAR_MASS_RATIO:
            return int((mass*constants.KG_TO_SOLAR_MASS_RATIO)**0.57)*constants.SOLAR_R_TO_KM_RATIO
        elif mass < constants.KG_TO_SOLAR_MASS_RATIO:
            return int((mass*constants.KG_TO_SOLAR_MASS_RATIO)**0.8)*constants.SOLAR_R_TO_KM_RATIO
        return 0

    @staticmethod
    def calculate_moon_inner_edge(mass_p: int, mass_m: int):
        pass

    @staticmethod
    def generate_system() -> SolarSystem:
        s_luminosity: float = random.uniform(0.1,100)
        s_mass: int = random.randint(int(constants.KG_TO_SOLAR_MASS_RATIO/10),constants.KG_TO_SOLAR_MASS_RATIO*100)
        s_frost_line: int = SolarSystemGen.calculate_star_frost_line(s_luminosity)
        planet_count: int = random.randint(5,15)

        star: Star = Star(str(uuid.uuid4()), "x", s_luminosity, s_mass, SolarSystemGen.calculate_star_radius(s_mass))

        planet_temp_array: list[Planet] = []
        inner_edge: int = SolarSystemGen.calculate_inner_planet_edge(star.luminosity)
        outer_edge: int = SolarSystemGen.calculate_outer_planet_edge(star.mass_kg)
        for i in range(0,planet_count):
            step: int = random.randint(1*constants.AU_TO_KM_RATIO,3*constants.AU_TO_KM_RATIO)

            if step*i+inner_edge >= outer_edge:
                break

            # default case is terrestrial rocky
            p_type: PlanetType = PlanetType.TERRESTRIAL_ROCKY
            p_mass: int = random.randint(1*constants.KG_TO_EARTH_MASS_RATIO, 300*constants.KG_TO_EARTH_MASS_RATIO)
            p_radius: int = 0

            if p_mass >= 10*constants.KG_TO_EARTH_MASS_RATIO:
                p_radius = int(3.5*(p_mass/constants.KG_TO_EARTH_MASS_RATIO)**0.03)
            elif p_mass < 10*constants.KG_TO_EARTH_MASS_RATIO:
                p_radius = int((p_mass/constants.KG_TO_EARTH_MASS_RATIO)**0.27)

            if step*i+inner_edge >= s_frost_line and p_mass >= 10*constants.KG_TO_EARTH_MASS_RATIO:
                p_type = PlanetType.ICE_GIANT
            elif step*i+inner_edge < s_frost_line and p_mass >= 10*constants.KG_TO_EARTH_MASS_RATIO:
                p_type = PlanetType.GAS_GIANT

            planet: Planet = Planet(str(uuid.uuid4()), "p", p_type, step*i+inner_edge, random.uniform(0, 2*math.pi), p_mass, p_radius, [])
            planet_temp_array.append(planet)

        system = SolarSystem(star, planet_temp_array)
        return system
    
    @staticmethod
    def generate_system_json() -> str:
        system: SolarSystem = SolarSystemGen.generate_system()
        jsonified: str = json.dumps(asdict(system))

        return jsonified
        