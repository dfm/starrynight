from .utils import *
from mpmath import ellipe, ellipk, ellippi
from scipy.integrate import quad
import numpy as np


C1 = 3.0 / 14.0
C2 = 1.0 / 3.0
C3 = 3.0 / 22.0
C4 = 3.0 / 26.0


def J(N, k2, kappa, gradient=False):
    # We'll need to solve this with gaussian quadrature
    func = (
        lambda x: np.sin(x) ** (2 * N) * (np.maximum(0, 1 - np.sin(x) ** 2 / k2)) ** 1.5
    )
    res = 0.0
    for i in range(0, len(kappa), 2):
        res += quad(
            func, 0.5 * kappa[i], 0.5 * kappa[i + 1], epsabs=1e-12, epsrel=1e-12,
        )[0]
    if gradient:
        # Deriv w/ respect to kappa is analytic
        dJdkappa = (
            0.5
            * (
                np.sin(0.5 * kappa) ** (2 * N)
                * (np.maximum(0, 1 - np.sin(0.5 * kappa) ** 2 / k2)) ** 1.5
            )
            * np.repeat([-1, 1], len(kappa) // 2).reshape(1, -1)
        )

        # Deriv w/ respect to k2 is tricky, need to integrate
        func = (
            lambda x: (1.5 / k2 ** 2)
            * np.sin(x) ** (2 * N + 2)
            * (np.maximum(0, 1 - np.sin(x) ** 2 / k2)) ** 0.5
        )
        dJdk2 = 0.0
        for i in range(0, len(kappa), 2):
            dJdk2 += quad(
                func, 0.5 * kappa[i], 0.5 * kappa[i + 1], epsabs=1e-12, epsrel=1e-12,
            )[0]

        return res, (dJdk2, dJdkappa)
    else:
        return res


def pal(bo, ro, kappa, gradient=False):
    z = lambda x, y: np.maximum(1e-12, np.sqrt(np.abs(1 - x ** 2 - y ** 2)))

    def G0(x, y):
        z_ = z(x, y)
        if z_ > 1 - 1e-8:
            return -0.5 * y
        else:
            return (1 - z_ ** 3) / (3 * (1 - z_ ** 2)) * (-y)

    def G1(x, y):
        z_ = z(x, y)
        if z_ > 1 - 1e-8:
            return 0.5 * x
        else:
            return (1 - z_ ** 3) / (3 * (1 - z_ ** 2)) * x

    G = [G0, G1]
    x = lambda phi: ro * np.cos(phi)
    y = lambda phi: bo + ro * np.sin(phi)
    dx = lambda phi: -ro * np.sin(phi)
    dy = lambda phi: ro * np.cos(phi)
    func = lambda theta: G[0](x(theta), y(theta)) * dx(theta) + G[1](
        x(theta), y(theta)
    ) * dy(theta)
    res, _ = quad(
        func, kappa[0] - np.pi / 2, kappa[1] - np.pi / 2, epsabs=1e-12, epsrel=1e-12,
    )

    if gradient:
        # Deriv w/ respect to kappa is analytic
        dpaldkappa = (
            0.5 * func(0.5 * kappa) * np.repeat([-1, 1], len(kappa) // 2).reshape(1, -1)
        )

        # Derivs w/ respect to b and r are tricky, need to integrate
        # TODO!!!
        dpaldbo = np.nan
        dpaldro = np.nan

        return res, (dpaldbo, dpaldro, dpaldkappa)

    else:

        return res


def hyp2f1(a, b, c, z, gradient=False):
    term = a * b * z / c
    value = 1.0 + term
    n = 1
    while (np.abs(term) > STARRY_2F1_TOL) and (n < STARRY_2F1_MAXITER):
        a += 1
        b += 1
        c += 1
        n += 1
        term *= a * b * z / c / n
        value += term
    if n == STARRY_2F1_MAXITER:
        raise ValueError("Series for 2F1 did not converge.")
    if gradient:
        dFdz = a * b / c * hyp2f1(a + 1, b + 1, c + 1, z)
        return value, dFdz
    else:
        return value


def el2(x, kc, a, b):
    """
    Vectorized implementation of the `el2` function from
    Bulirsch (1965). In this case, `x` is a *vector* of integration
    limits. The halting condition does not depend on the value of `x`,
    so it's much faster to evaluate all values of `x` at once!
    
    """
    if kc == 0:
        raise ValueError("Elliptic integral diverged because k = 1.")

    c = x * x
    d = 1 + c
    p = np.sqrt((1 + kc * kc * c) / d)
    d = x / d
    c = d / (2 * p)
    z = a - b
    i = a
    a = (b + a) / 2
    y = np.abs(1 / x)
    f = 0
    l = np.zeros_like(x)
    m = 1
    kc = np.abs(kc)

    for n in range(STARRY_EL2_MAX_ITER):

        b = i * kc + b
        e = m * kc
        g = e / p
        d = f * g + d
        f = c
        i = a
        p = g + p
        c = (d / p + c) / 2
        g = m
        m = kc + m
        a = (b / m + a) / 2
        y = -e / y + y

        y[y == 0] = np.sqrt(e) * c[y == 0] * b

        if np.abs(g - kc) > STARRY_EL2_CA * g:

            kc = np.sqrt(e) * 2
            l = l * 2
            l[y < 0] = 1 + l[y < 0]

        else:

            break

    if n == STARRY_EL2_MAX_ITER - 1:
        raise ValueError(
            "Elliptic integral EL2 failed to converge after {} iterations.".format(
                STARRY_EL2_MAX_ITER
            )
        )

    l[y < 0] = 1 + l[y < 0]
    e = (np.arctan(m / y) + np.pi * l) * a / m
    e[x < 0] = -e[x < 0]

    return e + c * z


def rj(x, y, z, p):
    """
    Carlson elliptic integral RJ.

    Bille Carlson,
    Computing Elliptic Integrals by Duplication,
    Numerische Mathematik,
    Volume 33, 1979, pages 1-16.

    Bille Carlson, Elaine Notis,
    Algorithm 577, Algorithms for Incomplete Elliptic Integrals,
    ACM Transactions on Mathematical Software,
    Volume 7, Number 3, pages 398-403, September 1981
    
    https://people.sc.fsu.edu/~jburkardt/f77_src/toms577/toms577.f

    """
    # Limit checks
    if x < STARRY_CRJ_LO_LIM:
        x = STARRY_CRJ_LO_LIM
    elif x > STARRY_CRJ_HI_LIM:
        x = STARRY_CRJ_HI_LIM

    if y < STARRY_CRJ_LO_LIM:
        y = STARRY_CRJ_LO_LIM
    elif y > STARRY_CRJ_HI_LIM:
        y = STARRY_CRJ_HI_LIM

    if z < STARRY_CRJ_LO_LIM:
        z = STARRY_CRJ_LO_LIM
    elif z > STARRY_CRJ_HI_LIM:
        z = STARRY_CRJ_HI_LIM

    if p < STARRY_CRJ_LO_LIM:
        p = STARRY_CRJ_LO_LIM
    elif p > STARRY_CRJ_HI_LIM:
        p = STARRY_CRJ_HI_LIM

    xn = x
    yn = y
    zn = z
    pn = p
    sigma = 0.0
    power4 = 1.0

    for k in range(STARRY_CRJ_MAX_ITER):

        mu = 0.2 * (xn + yn + zn + pn + pn)
        invmu = 1.0 / mu
        xndev = (mu - xn) * invmu
        yndev = (mu - yn) * invmu
        zndev = (mu - zn) * invmu
        pndev = (mu - pn) * invmu
        eps = np.max([np.abs(xndev), np.abs(yndev), np.abs(zndev), np.abs(pndev)])

        if eps < STARRY_CRJ_TOL:

            ea = xndev * (yndev + zndev) + yndev * zndev
            eb = xndev * yndev * zndev
            ec = pndev * pndev
            e2 = ea - 3.0 * ec
            e3 = eb + 2.0 * pndev * (ea - ec)
            s1 = 1.0 + e2 * (-C1 + 0.75 * C3 * e2 - 1.5 * C4 * e3)
            s2 = eb * (0.5 * C2 + pndev * (-C3 - C3 + pndev * C4))
            s3 = pndev * ea * (C2 - pndev * C3) - C2 * pndev * ec
            value = 3.0 * sigma + power4 * (s1 + s2 + s3) / (mu * np.sqrt(mu))
            return value

        xnroot = np.sqrt(xn)
        ynroot = np.sqrt(yn)
        znroot = np.sqrt(zn)
        lam = xnroot * (ynroot + znroot) + ynroot * znroot
        alpha = pn * (xnroot + ynroot + znroot) + xnroot * ynroot * znroot
        alpha = alpha * alpha
        beta = pn * (pn + lam) * (pn + lam)
        if alpha < beta:
            sigma += power4 * np.arccos(np.sqrt(alpha / beta)) / np.sqrt(beta - alpha)
        elif alpha > beta:
            sigma += power4 * np.arccosh(np.sqrt(alpha / beta)) / np.sqrt(alpha - beta)
        else:
            sigma = sigma + power4 / np.sqrt(beta)

        power4 *= 0.25
        xn = 0.25 * (xn + lam)
        yn = 0.25 * (yn + lam)
        zn = 0.25 * (zn + lam)
        pn = 0.25 * (pn + lam)

    if k == STARRY_CRJ_MAX_ITER - 1:
        raise ValueError(
            "Elliptic integral RJ failed to converge after {} iterations.".format(
                STARRY_CRJ_MAX_ITER
            )
        )


def ellip(bo, ro, kappa, k2):

    # Helper variables
    k = np.sqrt(k2)
    k2inv = 1 / k2
    kinv = np.sqrt(k2inv)
    kc2 = 1 - k2
    kc = np.sqrt(kc2)
    kc2inv = 1 - k2inv
    kcinv = np.sqrt(kc2inv)

    # Complete elliptic integrals (we'll need them to compute offsets below)
    if k2 < 1:
        K0 = float(ellipk(k2))
        E0 = float(ellipe(k2))
        E0 = np.sqrt(k2inv) * (E0 - (1 - k2) * K0)
        K0 *= np.sqrt(k2)
        RJ0 = 0.0
    else:
        K0 = float(ellipk(k2inv))
        E0 = float(ellipe(k2inv))
        if (bo != 0) and (bo != ro):
            p0 = (ro * ro + bo * bo + 2 * ro * bo) / (ro * ro + bo * bo - 2 * ro * bo)
            PI0 = float(ellippi(1 - p0, k2inv))
            RJ0 = -12.0 / (1 - p0) * (PI0 - K0)
        else:
            RJ0 = 0.0

    if k2 < 1:

        # Analytic continuation from (17.4.15-16) in Abramowitz & Stegun
        # A better format is here: https://dlmf.nist.gov/19.7#ii

        # Helper variables
        arg = kinv * np.sin(kappa / 2)
        tanphi = arg / np.sqrt(1 - arg ** 2)
        tanphi[arg >= 1] = STARRY_HUGE_TAN
        tanphi[arg <= -1] = -STARRY_HUGE_TAN

        # Compute the elliptic integrals
        F = el2(tanphi, kc, 1, 1) * k
        E = kinv * (el2(tanphi, kc, 1, kc2) - kc2 * kinv * F)

        # Add offsets to account for the limited domain of `el2`
        for i in range(len(kappa)):
            if kappa[i] > 3 * np.pi:
                F[i] += 4 * K0
                E[i] += 4 * E0
            elif kappa[i] > np.pi:
                F[i] = 2 * K0 - F[i]
                E[i] = 2 * E0 - E[i]

    else:

        # Helper variables
        tanphi = np.tan(kappa / 2)

        # Compute the elliptic integrals
        F = el2(tanphi, kcinv, 1, 1)
        E = el2(tanphi, kcinv, 1, kc2inv)

        # Add offsets to account for the limited domain of `el2`
        for i in range(len(kappa)):
            if kappa[i] > 3 * np.pi:
                F[i] += 4 * K0
                E[i] += 4 * E0
            elif kappa[i] > np.pi:
                F[i] += 2 * K0
                E[i] += 2 * E0

    # Carlson integrals
    RF = -F
    RD = (E - F) * 3 * k2

    # Carlson integral of the third kind; must compute this separately
    phi = (kappa - np.pi) % (2 * np.pi)
    p = (ro * ro + bo * bo + 2 * ro * bo * np.cos(phi)) / (
        ro * ro + bo * bo - 2 * ro * bo
    )
    cx = np.cos(phi / 2)
    sx = np.sin(phi / 2)
    w = 1 - cx ** 2 / k2
    RJ = np.zeros_like(phi)
    if np.abs(bo - ro) > STARRY_PAL_BO_EQUALS_RO_TOL:
        for i in range(len(w)):
            RJ[i] = (np.cos(phi[i]) + 1) * cx[i] * rj(w[i], sx[i] * sx[i], 1.0, p[i])

        # Add offsets to account for the limited domain
        if RJ0 != 0.0:
            for i in range(len(w)):
                if kappa[i] > 3 * np.pi:
                    RJ[i] += 2 * RJ0
                elif kappa[i] > np.pi:
                    RJ[i] += RJ0

    # Return the definite elliptic integrals
    return (pairdiff(F), pairdiff(E), pairdiff(RF), pairdiff(RD), pairdiff(RJ))

