"""Calculte sky values based on Radiance's gendaylit.

This code is parts of genddaylit.c whic is copyrighted by:
    Copyright (c) 1994,2006 *Fraunhofer Institut for Solar Energy Systems
        Heidenhofstr. 2, D-79110 Freiburg, Germany
        Agence de l'Environnement et de la Maitrise de l'Energie
        Centre de Valbonne, 500 route des Lucioles, 06565 Sophia Antipolis Cedex, France
        *BOUYGUES
        1 Avenue Eugene Freyssinet, Saint-Quentin-Yvelines, France

You can check the source code at:
    https://github.com/NREL/Radiance/blob/53485a7fb48727293d62f98d7bac830aa34ccba4/src/
        gen/gendaylit.c
"""
import math
from datetime import datetime


def gendaylit(altitude, month, day, hour, directirradiance, diffuseirradiance,
              output_type=0):
    """Get solar irradiance.

    Args:
        altitude: Sun altitude in degrees.
        month: A value for month between 1-12.
        day: A value for day between 1-31.
        hour: A value for hour between 0-23.
        directirradiance: Direct irradiance value.
        diffuseirradiance: Diffuse irradiance value.
        output_type: An integer between 0-2. 0=output in W/m^2/sr visible,
            1=output in W/m^2/sr solar, 2=output in candela/m^2 (default: 0).
    Returns:
        solarradiance: solar irradiance.
    """
    #
    coeff_perez = [
        1.3525, -0.2576, -0.2690, -1.4366, -0.7670, 0.0007, 1.2734, -0.1233, 2.8000,
        0.6004, 1.2375, 1.000, 1.8734, 0.6297, 0.9738, 0.2809, 0.0356, -0.1246,
        -0.5718, 0.9938, -1.2219, -0.7730, 1.4148, 1.1016, -0.2054, 0.0367, -3.9128,
        0.9156, 6.9750, 0.1774, 6.4477, -0.1239, -1.5798, -0.5081, -1.7812, 0.1080,
        0.2624, 0.0672, -0.2190, -0.4285, -1.1000, -0.2515, 0.8952, 0.0156, 0.2782,
        -0.1812, -4.5000, 1.1766, 24.7219, -13.0812, -37.7000, 34.8438, -5.0000, 1.5218,
        3.9229, -2.6204, -0.0156, 0.1597, 0.4199, -0.5562, -0.5484, -0.6654, -0.2672,
        0.7117, 0.7234, -0.6219, -5.6812, 2.6297, 33.3389, -18.3000, -62.2500, 52.0781,
        -3.5000, 0.0016, 1.1477, 0.1062, 0.4659, -0.3296, -0.0876, -0.0329, -0.6000,
        -0.3566, -2.5000, 2.3250, 0.2937, 0.0496, -5.6812, 1.8415, 21.0000, -4.7656,
        -21.5906, 7.2492, -3.5000, -0.1554, 1.4062, 0.3988, 0.0032, 0.0766, -0.0656,
        -0.1294, -1.0156, -0.3670, 1.0078, 1.4051, 0.2875, -0.5328, -3.8500, 3.3750,
        14.0000, -0.9999, -7.1406, 7.5469, -3.4000, -0.1078, -1.0750, 1.5702, -0.0672,
        0.4016, 0.3017, -0.4844, -1.0000, 0.0211, 0.5025, -0.5119, -0.3000, 0.1922,
        0.7023, -1.6317, 19.0000, -5.0000, 1.2438, -1.9094, -4.0000, 0.0250, 0.3844,
        0.2656, 1.0468, -0.3788, -2.4517, 1.4656, -1.0500, 0.0289, 0.4260, 0.3590,
        -0.3250, 0.1156, 0.7781, 0.0025, 31.0625, -14.5000, -46.1148, 55.3750, -7.2312,
        0.4050, 13.3500, 0.6234, 1.5000, -0.6426, 1.8564, 0.5636]

    defangle_theta = [
        84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 84,
        84, 84, 84, 84, 84, 84, 84, 84, 84, 84, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72,
        72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72, 72,
        60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60, 60,
        60, 60, 60, 60, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48, 48,
        48, 48, 48, 48, 48, 48, 48, 48, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36, 36,
        36, 36, 36, 36, 36, 36, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 24, 12, 12,
        12, 12, 12, 12, 0]

    defangle_phi = [
        0, 12, 24, 36, 48, 60, 72, 84, 96, 108, 120, 132, 144, 156, 168, 180, 192, 204,
        216, 228, 240, 252, 264, 276, 288, 300, 312, 324, 336, 348, 0, 12, 24, 36, 48,
        60, 72, 84, 96, 108, 120, 132, 144, 156, 168, 180, 192, 204, 216, 228, 240, 252,
        264, 276, 288, 300, 312, 324, 336, 348, 0, 15, 30, 45, 60, 75, 90, 105, 120, 135,
        150, 165, 180, 195, 210, 225, 240, 255, 270, 285, 300, 315, 330, 345, 0, 15, 30,
        45, 60, 75, 90, 105, 120, 135, 150, 165, 180, 195, 210, 225, 240, 255, 270, 285,
        300, 315, 330, 345, 0, 20, 40, 60, 80, 100, 120, 140, 160, 180, 200, 220, 240,
        260, 280, 300, 320, 340, 0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330,
        0, 60, 120, 180, 240, 300, 0]

    WHTEFFICACY = 179.0  # luminous efficacy of uniform white light

    # calculate solar direction
    daynumber = datetime(2017, month, day, int(hour)).timetuple().tm_yday

    # print '# Solar altitude and azimuth: %.2f %.2f' % (sun.altitude, sun.azimuth - 180)
    # print '# Day number: %d' % daynumber
    # print -1 * sun.sun_vector

    day_angle = 2 * math.pi * (daynumber - 1) / 365

    # altitude correction if too close to zenith
    if altitude > 87.0:
        print("warning - sun too close to zenith, reducing altitude to 87 degrees.")
        altitude = 87.0

    sunzenith = 90 - altitude

    # print '#Zenith: %f' % sunzenith
    if directirradiance + diffuseirradiance == 0 or altitude <= 0:
        return 0

    directirradiance, diffuseirradiance = \
        check_input_values(directirradiance, diffuseirradiance, altitude)

    skybrightness = sky_brightness(diffuseirradiance, sunzenith, day_angle)
    skyclearness = sky_clearness(diffuseirradiance, directirradiance, sunzenith)

    skyclearness, skybrightness = check_parametrization(skyclearness, skybrightness)

    # print '# clearness: %f, brighness: %f' % (skyclearness, skybrightness)

    # diffuse horizontal illuminance
    diffuseilluminance = diffuseirradiance * \
        glob_h_diffuse_effi_perez(skyclearness, skybrightness, sunzenith)

    directilluminance = directirradiance * \
        direct_n_effi_perez(skyclearness, skybrightness, sunzenith)

    directilluminance, diffuseilluminance = \
        check_input_values(directilluminance, diffuseilluminance, altitude)

    # print '# Illuminance direct %f, diffuse %f' \
    # % (directilluminance, diffuseilluminance)

    # calculate sky
    #  read the angles * \
    half_sun_angle = 0.2665
    theta_o = defangle_theta
    phi_o = defangle_phi
    lv_mod = []  # 145 illuminance values

    #  parameters for the perez model * \
    skybrightness = \
        coeff_lum_perez(radians(sunzenith), skyclearness, skybrightness, coeff_perez)

    # calculation of the modelled luminance * \
    for j in xrange(145):
        dzeta, gamma = theta_phi_to_dzeta_gamma(
            radians(theta_o[j]), radians(phi_o[j]), radians(sunzenith)
        )

        v = calc_rel_lum_perez(
            dzeta, gamma, radians(sunzenith), skyclearness, skybrightness, coeff_perez
        )

        lv_mod.append(v)
        # print "theta, phi, lv_mod %f\t %f\t %f\n" % (theta_o[j], phi_o[j], lv_mod[j])

    #   integration of luminance for the normalization factor, diffuse part of the sky
    diffnormalization = integ_lv(lv_mod, theta_o)

    # normalization coefficient in lumen or in watt * \
    if output_type == 0:
        diffnormalization = diffuseilluminance / diffnormalization / WHTEFFICACY
    elif output_type == 1:
        diffnormalization = diffuseirradiance / diffnormalization
    elif output_type == 2:
        diffnormalization = diffuseilluminance / diffnormalization

    #  calculation for the solar source * \
    if output_type == 0:
        solarradiance = directilluminance / \
            (2 * math.pi * (1 - math.cos(half_sun_angle * math.pi / 180))) / WHTEFFICACY

    elif output_type == 1:
        solarradiance = directirradiance / \
            (2 * math.pi * (1 - math.cos(half_sun_angle * math.pi / 180)))

    else:
        solarradiance = directilluminance / \
            (2 * math.pi * (1 - math.cos(half_sun_angle * math.pi / 180)))

    return solarradiance


def radians(degres):
    # /* degrees into radians */
    return degres * math.pi / 180.0


def integ_lv(lv, theta):
    # int i
    buffer = 0.0

    for i in xrange(145):
        buffer += lv[i] * math.cos(radians(theta[i]))

    return buffer * 2 * math.pi / 144


def get_numlin(epsilon):

    if (epsilon < 1.065):
        return 0
    elif (epsilon < 1.230):
        return 1
    elif (epsilon < 1.500):
        return 2
    elif (epsilon < 1.950):
        return 3
    elif (epsilon < 2.800):
        return 4
    elif (epsilon < 4.500):
        return 5
    elif (epsilon < 6.200):
        return 6
    return 7


def theta_phi_to_dzeta_gamma(theta, phi, z):
    """Calculation of the angles dzeta and gamma."""
    dzeta = theta

    if ((math.cos(z) * math.cos(theta) + math.sin(z) * math.sin(theta) *
         math.cos(phi)) > 1 and (math.cos(z) * math.cos(theta) + math.sin(z) *
                                 math.sin(theta) * math.cos(phi) < 1.1)):
        gamma = 0
    elif math.cos(z) * math.cos(theta) + math.sin(z) * math.sin(theta) * \
            math.cos(phi) > 1.1:
        raise ValueError("error in calculation of gamma (angle between point and sun)")
    else:
        gamma = math.acos(math.cos(z) * math.cos(theta) + math.sin(z) *
                          math.sin(theta) * math.cos(phi))

    return dzeta, gamma


def calc_rel_lum_perez(dzeta, gamma, z, epsilon, delta, coeff_perez):
    """Sky luminance perez model."""
    x = [[], [], [], [], []]
    c_perez = range(5)

    # limitations for the variation of the Perez parameters */
    skyclearinf = 1.0
    skyclearsup = 12.01

    if epsilon < skyclearinf or epsilon >= skyclearsup:
        raise ValueError("Error: epsilon out of range in function calc_rel_lum_perez!\n")

    #  correction de modele de Perez solar energy ...* \
    if epsilon > 1.065 and epsilon < 2.8:
        if (delta < 0.2):
            delta = 0.2

    num_lin = get_numlin(epsilon)
    # print "nline %d epsilon %f\n" % (num_lin, epsilon)

    for i in xrange(5):
        for j in xrange(4):
            x[i].append(coeff_perez[20 * num_lin + 4 * i + j % 60])
            # print "inside_loop %d %d vaut %f\n" % (i, j, x[i][j])

    if num_lin:
        for i in xrange(5):
            c_perez[i] = x[i][0] + x[i][1] * z + delta * (x[i][2] + x[i][3] * z)
    else:
        c_perez[0] = x[0][0] + x[0][1] * z + delta * (x[0][2] + x[0][3] * z)
        c_perez[1] = x[1][0] + x[1][1] * z + delta * (x[1][2] + x[1][3] * z)
        c_perez[4] = x[4][0] + x[4][1] * z + delta * (x[4][2] + x[4][3] * z)
        c_perez[2] = math.exp(
            math.pow(delta * (x[2][0] + x[2][1] * z), x[2][2])) - x[2][3]
        c_perez[3] = -math.exp(
            delta * (x[3][0] + x[3][1] * z)) + x[3][2] + delta * x[3][3]

    return (1 + c_perez[0] * math.exp(c_perez[1] / math.cos(dzeta))) * \
        (1 + c_perez[2] * math.exp(c_perez[3] * gamma) +
         c_perez[4] * math.cos(gamma) * math.cos(gamma))


def sky_clearness(diffuseirradiance, directirradiance, sunzenith):
    """Perez sky's clearness."""
    try:
        value = (
            (diffuseirradiance + directirradiance) / (diffuseirradiance) +
            1.041 * sunzenith * math.pi / 180 * sunzenith * math.pi /
            180 * sunzenith * math.pi / 180) / (1 + 1.041 * sunzenith * math.pi / 180 *
                                                sunzenith * math.pi / 180 * sunzenith *
                                                math.pi / 180)
    except ZeroDivisionError:
        msg = 'diff: {}, dir: {}, zenith: {}'.format(diffuseirradiance,
                                                     directirradiance, sunzenith)
        raise ZeroDivisionError(msg)

    return value


def sky_brightness(diffuseirradiance, sunzenith, day_angle):
    solar_constant_e = 1367    # solar constant W/m^2
    """Perez sky's brightness"""
    brighness = diffuseirradiance * \
        air_mass(sunzenith) / (solar_constant_e * get_eccentricity(day_angle))
    return brighness


def get_eccentricity(day_angle):
    """Enter day number, return E0 = square(R0/R): eccentricity correction factor."""
    e0 = 1.00011 + 0.034221 * math.cos(day_angle) + 0.00128 * math.sin(day_angle) + \
        0.000719 * math.cos(2 * day_angle) + 0.000077 * math.sin(2 * day_angle)

    return e0


def air_mass(sunzenith):
    """Enter sunzenith angle (degrees) return relative air mass (double)."""
    if sunzenith > 90:
        # print("Warning: air mass has reached the maximal value: %f \n" % sunzenith)
        sunzenith = 90

    m = 1 / (math.cos(sunzenith * math.pi / 180) + 0.15 *
             math.exp(math.log(93.885 - sunzenith) * (-1.253)))
    return m


def check_parametrization(skyclearness, skybrightness):
    """Check the range of epsilon and delta indexes of the perez parametrization."""
    # #  limitations for the variation of the Perez parameters * \
    skyclearinf = 1.0
    skyclearsup = 12.01
    skybriginf = 0.01
    skybrigsup = 0.6
    if skyclearness < skyclearinf or skyclearness > skyclearsup \
            or skybrightness < skybriginf or skybrightness > skybrigsup:
        # #   limit sky clearness or sky brightness, 2009 11 13 by J. Wienold */

        if (skyclearness < skyclearinf):
            # #  if (suppress_warnings==0)
                    # print(stderr,"Range warning: sky clearness too low (%lf)\n",
                    # skyclearness) */
            skyclearness = skyclearinf

        if (skyclearness > skyclearsup):
            # #  if (suppress_warnings==0)
            #     print(stderr,"Range warning: sky clearness too high (%lf)\n",
            # skyclearness) */
            skyclearness = skyclearsup - 0.001

        if (skybrightness < skybriginf):
            # #  if (suppress_warnings==0)
            #     print(stderr,"Range warning: sky brightness too low (%lf)\n",
            # skybrightness) */
            skybrightness = skybriginf

        if (skybrightness > skybrigsup):
            # #  if (suppress_warnings==0)
            # print(stderr,"Range warning: sky brightness too high (%lf)\n",
            # skybrightness) */
            skybrightness = skybrigsup

    return skyclearness, skybrightness


def glob_h_diffuse_effi_perez(skyclearness, skybrightness, sunzenith):
    """Global horizontal diffuse efficacy model, according to PEREZ."""
    # #  initialize category bounds (clearness index bounds) */
    atm_preci_water = 2

    # //XXX:  category_bounds > 0.1 started from 1!
    category_bounds = (1, 1.065, 1.230, 1.500, 1.950, 2.800, 4.500, 6.200, 12.01)

    # #  initialize model coefficients * \
    a = (97.24, 107.22, 104.97, 102.39, 100.71, 106.42, 141.88, 152.23)

    b = (-0.46, 1.15, 2.96, 5.59, 5.94, 3.83, 1.90, 0.35)

    c = (12.00, 0.59, -5.53, -13.95, -22.75, -36.15, -53.24, -45.27)

    d = (-8.91, -3.95, -8.77, -13.90, -23.74, -28.83, -14.03, -7.98)

    category_number = -1
    for i in xrange(1, 8):
        if category_bounds[i - 1] <= skyclearness < category_bounds[i]:
            category_number = i - 1

    if category_number == -1:
        ValueError(
            "Warning: sky clearness (= %.3f) too high,"
            " printing error sky\n".format(skyclearness))

    value = a[category_number] + b[category_number] * atm_preci_water + \
        c[category_number] * math.cos(sunzenith * math.pi / 180) + \
        d[category_number] * math.log(skybrightness)

    return value


def direct_n_effi_perez(skyclearness, skybrightness, sunzenith):
    """Direct normal efficacy model, according to PEREZ."""
    atm_preci_water = 2
    # #  initialize category bounds(clearness index bounds) * \
    category_bounds = (1, 1.065, 1.230, 1.500, 1.950, 2.800, 4.500, 6.200, 12.01)

    # #  initialize model coefficients * \
    a = (57.20, 98.99, 109.83, 110.34, 106.36, 107.19, 105.75, 101.18)

    b = (-4.55, -3.46, -4.90, -5.84, -3.97, -1.25, 0.77, 1.58)

    c = (-2.98, -1.21, -1.71, -1.99, -1.75, -1.51, -1.26, -1.10)

    d = (117.12, 12.38, -8.81, -4.56, -6.16, -26.73, -34.44, -8.29)

    category_number = -1
    for i in xrange(1, 8):
        if category_bounds[i - 1] <= skyclearness < category_bounds[i]:
            category_number = i - 1

    value = a[category_number] + b[category_number] * atm_preci_water + \
        c[category_number] * math.exp(5.73 * sunzenith * math.pi / 180 - 5) + \
        d[category_number] * skybrightness

    if value < 0:
        value = 0

    return value


def check_input_values(directilluminance, diffuseilluminance, altitude):
    """Validity of the direct and diffuse components."""
    solar_constant_l = 127500   # solar constant lux
    if directilluminance < 0:
        print("Warning: direct illuminance < 0. Using 0.0\n")
        directilluminance = 0.0

    if diffuseilluminance < 0:
        print("Warning: diffuse illuminance < 0. Using 0.0\n")
        diffuseilluminance = 0.0

    if directilluminance + diffuseilluminance == 0 and altitude > 0:
        raise ValueError("Warning: zero illuminance at sun altitude > 0\n")

    if directilluminance > solar_constant_l:
        raise ValueError("Warning: direct illuminance exceeds solar constant\n")

    if directilluminance != 0 and diffuseilluminance == 0:
        diffuseilluminance = 0.00000001

    return directilluminance, diffuseilluminance


def coeff_lum_perez(z, epsilon, delta, coeff_perez):
    """Coefficients for the sky luminance perez model."""
    x = [[], [], [], [], []]
    c_perez = range(5)

    # limitations for the variation of the Perez parameters */
    skyclearinf = 1.0
    skyclearsup = 12.01

    if epsilon < skyclearinf or epsilon >= skyclearsup:
        raise ValueError("Error: epsilon out of range in function coeff_lum_perez!\n")

    # /* correction du modele de Perez solar energy ...*/
    if epsilon > 1.065 and epsilon < 2.8:
        if delta < 0.2:
            delta = 0.2

    return delta

    # This part of the code won't be executed and is only important for prez sky
    num_lin = get_numlin(epsilon)

    # /*fprintf(stderr,"numlin %d\n", num_lin)*/

    for i in range(5):
        for j in range(4):
            x[i].append(coeff_perez[(20 * num_lin + 4 * i + j) % 60])

    if (num_lin):
        for i in range(5):
            c_perez[i] = x[i][0] + x[i][1] * z + delta * (x[i][2] + x[i][3] * z)

    else:
        c_perez[0] = x[0][0] + x[0][1] * z + delta * (x[0][2] + x[0][3] * z)
        c_perez[1] = x[1][0] + x[1][1] * z + delta * (x[1][2] + x[1][3] * z)
        c_perez[4] = x[4][0] + x[4][1] * z + delta * (x[4][2] + x[4][3] * z)
        c_perez[2] = math.exp(math.pow(delta * (x[2][0] + x[2][1] * z), x[2][2])) \
            - x[2][3]
        c_perez[3] = -math.exp(delta * (x[3][0] + x[3][1] * z)) + x[3][2] + \
            delta * x[3][3]
