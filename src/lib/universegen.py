import json
import math
import uuid
# import numpy as np
import random
from dataclasses import dataclass, asdict
from enum import StrEnum
import lib.config.constants as constants

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
class Moon: # all moons are rocky (for now)
    id: str
    name: str
    semi_major_axis_km: int
    current_orbit_angle: float
    mass_kg: int
    radius_km: int

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
        return int((((278*(luminosity**0.25))/constants.T_DUST_SUBLIMATION)**2)*constants.AU_TO_KM_RATIO)
    

    @staticmethod
    def calculate_outer_planet_edge(mass: int) -> int: # kinda arbitrarily decided
        return int(100*((mass*constants.KG_TO_SOLAR_MASS_RATIO)**(1/3)))*constants.AU_TO_KM_RATIO
    
    @staticmethod
    def calculate_star_radius(mass: int) -> int:
        if mass >= constants.KG_TO_SOLAR_MASS_RATIO:
            return int((mass/constants.KG_TO_SOLAR_MASS_RATIO)**0.57*constants.SOLAR_R_TO_KM_RATIO)
        elif mass < constants.KG_TO_SOLAR_MASS_RATIO:
            return int((mass/constants.KG_TO_SOLAR_MASS_RATIO)**0.8*constants.SOLAR_R_TO_KM_RATIO)
        return 0
    
    # source for this is gemini but I'm blindly trusting it hasn't hallucinated these equations for now
    @staticmethod
    def calculate_star_luminosity(mass: int) -> float:
        if mass/constants.KG_TO_SOLAR_MASS_RATIO < 0.43:
            return 0.23*((mass/constants.KG_TO_SOLAR_MASS_RATIO)**2.3)
        elif mass/constants.KG_TO_SOLAR_MASS_RATIO < 2.0:
            return (mass/constants.KG_TO_SOLAR_MASS_RATIO)**4.0
        elif mass/constants.KG_TO_SOLAR_MASS_RATIO < 55.0:
            return 1.4*((mass/constants.KG_TO_SOLAR_MASS_RATIO))**3.5
        else:
            return 29090 * (mass/constants.KG_TO_SOLAR_MASS_RATIO)

    @staticmethod
    def calculate_moon_inner_edge(mass_p: int, radius_p: int, mass_m: int, radius_m: int) -> int: # roche limit
        return int(2.44 * radius_m * ((mass_p / mass_m) ** (1/3)))

    @staticmethod
    def calculate_moon_outer_edge(mass_p: int, mass_s: int, semi_major_axis_p: int) -> int: # hill sphere
        return int(semi_major_axis_p*((mass_p/(3*mass_s))**(1/3)))

    @staticmethod
    def generate_system() -> SolarSystem:
        s_mass: int = random.randint(int(constants.KG_TO_SOLAR_MASS_RATIO),constants.KG_TO_SOLAR_MASS_RATIO*100)
        s_luminosity: float = SolarSystemGen.calculate_star_luminosity(s_mass)
        s_frost_line: int = SolarSystemGen.calculate_star_frost_line(s_luminosity)
        planet_count: int = random.randint(5,15)

        star: Star = Star(str(uuid.uuid4()), "x", s_luminosity, s_mass, SolarSystemGen.calculate_star_radius(s_mass))

        planet_temp_array: list[Planet] = []
        inner_edge: int = SolarSystemGen.calculate_inner_planet_edge(star.luminosity)
        outer_edge: int = SolarSystemGen.calculate_outer_planet_edge(star.mass_kg)

        for i in range(0,planet_count):
            step: int = random.randint(1*constants.AU_TO_KM_RATIO,3*constants.AU_TO_KM_RATIO)

            semi_major_axis_temp: int = step*i+inner_edge

            if semi_major_axis_temp >= outer_edge:
                break

            # default case is terrestrial rocky
            p_type: PlanetType = PlanetType.TERRESTRIAL_ROCKY
            p_mass: int = random.randint(1*constants.KG_TO_EARTH_MASS_RATIO, 300*constants.KG_TO_EARTH_MASS_RATIO)
            p_radius: int = 0

            # loosely based on https://arxiv.org/pdf/1603.08614
            if p_mass >= 10*constants.KG_TO_EARTH_MASS_RATIO:
                p_radius = int((14*(p_mass/constants.KG_TO_EARTH_MASS_RATIO)**-0.03)*constants.KM_TO_EARTH_RADIUS_RATIO)
            elif p_mass < 10*constants.KG_TO_EARTH_MASS_RATIO:
                p_radius = int(((p_mass/constants.KG_TO_EARTH_MASS_RATIO)**0.27)*constants.KM_TO_EARTH_RADIUS_RATIO)

            if semi_major_axis_temp >= s_frost_line and p_mass >= 10*constants.KG_TO_EARTH_MASS_RATIO:
                p_type = PlanetType.ICE_GIANT
            elif semi_major_axis_temp < s_frost_line and p_mass >= 10*constants.KG_TO_EARTH_MASS_RATIO:
                p_type = PlanetType.GAS_GIANT

            # moon calculations
            moon_count: int = random.randint(0,10)
            moon_temp_array: list[Moon] = []
            
            for i in range(0, moon_count):
                moon_radius: int = random.randint(100, 2000)
                moon_mass: int = int((4/3)*math.pi*(moon_radius**3)*3000*(10**9)) # rocky density?
                # print(f"{moon_radius=},{moon_mass=},{p_radius=},{p_mass=},{s_mass=}")
                inner_moon_edge: int = SolarSystemGen.calculate_moon_inner_edge(p_mass, p_radius, moon_mass, moon_radius)
                outer_moon_edge: int = SolarSystemGen.calculate_moon_outer_edge(p_mass, s_mass, semi_major_axis_temp)
                moon: Moon = Moon(str(uuid.uuid4()),"m",random.randint(inner_moon_edge, outer_moon_edge),random.uniform(0,2*math.pi), moon_mass, moon_radius)
                moon_temp_array.append(moon)

            planet: Planet = Planet(str(uuid.uuid4()), "p", p_type, semi_major_axis_temp, random.uniform(0, 2*math.pi), p_mass, p_radius, moon_temp_array)
            planet_temp_array.append(planet)

        system = SolarSystem(star, planet_temp_array)
        return system
    
    @staticmethod
    def generate_system_json() -> str:
        system: SolarSystem = SolarSystemGen.generate_system()
        jsonified: str = json.dumps(asdict(system))

        return jsonified
        