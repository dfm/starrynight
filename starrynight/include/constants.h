/**
\file utils.h
\brief Miscellaneous utilities and definitions used throughout the code.

*/

#ifndef _STARRY_CONSTANTS_H_
#define _STARRY_CONSTANTS_H_

namespace starry {
namespace constants {

// Integration codes
#define FLUX_ZERO  0
#define FLUX_DAY_OCC  1
#define FLUX_DAY_VIS  2
#define FLUX_NIGHT_OCC  3
#define FLUX_NIGHT_VIS  4
#define FLUX_SIMPLE_OCC  5
#define FLUX_SIMPLE_REFL  6
#define FLUX_SIMPLE_OCC_REFL  7
#define FLUX_TRIP_DAY_OCC  8
#define FLUX_TRIP_NIGHT_OCC  9
#define FLUX_QUAD_DAY_VIS  10
#define FLUX_QUAD_NIGHT_VIS  11

// Maximum number of iterations when computing `el2` and `rj`
#define STARRY_EL2_MAX_ITER  100
#define STARRY_CRJ_MAX_ITER  100

// Tolerances in `rj`
#define STARRY_CRJ_LO_LIM  2e-26
#define STARRY_CRJ_HI_LIM  3e24
#define STARRY_CRJ_TOL  2e-2

// Maximum number of iterations & tolerance when computing 2F1
#define STARRY_2F1_MAXITER  200
#define STARRY_2F1_MAXTOL  1e-15
#define STARRY_2F1_MINTOL  1e-12

// Square root of the desired precision in `el2`
#define STARRY_EL2_CA  1e-8

// Replace `inf` with this value in argument to `el2`
#define STARRY_HUGE_TAN  1e15

// If |sin(theta)| or |cos(theta)| is less than this, set  0
#define STARRY_T_TOL  1e-12

// Low, medium, and high tolerance for root polishing
#define STARRY_ROOT_TOL_LOW  1e-2
#define STARRY_ROOT_TOL_MED  1e-10
#define STARRY_ROOT_TOL_HIGH  1e-15

// Tolerance for duplicate roots
#define STARRY_ROOT_TOL_DUP  1e-8

// Maximum number of root polishing iterations
#define STARRY_ROOT_MAX_ITER  50

// If |b| is less than this value, set  0
#define STARRY_B_ZERO_TOL  1e-8

// Tolerance for various functions that calculate phi, xi, and lam
#define STARRY_ANGLE_TOL  1e-13

// Nudge k^2 away from 1 when it gets this close
#define STARRY_K2_ONE_TOL 1e-12

/*
Hacks. Determining the integration paths close to the singular
points of the occultation is quite hard, and the solution can
often oscillate between two regimes. These tolerances prevent us
from entering those regimes, at the cost of precision loss near
these singular points.
*/
#define STARRY_COMPLETE_OCC_TOL  1e-8
#define STARRY_NO_OCC_TOL  1e-8
#define STARRY_GRAZING_TOL  1e-8

// Tolerance for the Pal (2012) solver, which is very unstable
#define STARRY_PAL_BO_EQUALS_RO_TOL  1e-3
#define STARRY_PAL_BO_EQUALS_RO_MINUS_ONE_TOL  1e-3
#define STARRY_PAL_BO_EQUALS_ONE_MINUS_RO_TOL  1e-3

// Number of Gaussian-Legendre quadrature points for numerical integration
#define STARRY_QUAD_POINTS 50


} // namespace constants
} // namespace starry
#endif