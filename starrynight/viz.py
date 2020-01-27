from .geometry import get_angles
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Arc


def visualize(b, theta, bo, ro, tol=1e-7, res=4999):

    # Find angles of intersection
    phi, lam, xi, _ = get_angles(b, theta, bo, ro, tol=tol)

    # Equation of half-ellipse
    x = np.linspace(-1, 1, 1000)
    y = b * np.sqrt(1 - x ** 2)
    x_t = x * np.cos(theta) - y * np.sin(theta)
    y_t = x * np.sin(theta) + y * np.cos(theta)

    # Shaded regions
    p = np.linspace(-1, 1, res)
    xpt, ypt = np.meshgrid(p, p)
    cond1 = xpt ** 2 + (ypt - bo) ** 2 < ro ** 2  # inside occultor
    cond2 = xpt ** 2 + ypt ** 2 < 1  # inside occulted
    xr = xpt * np.cos(theta) + ypt * np.sin(theta)
    yr = -xpt * np.sin(theta) + ypt * np.cos(theta)
    cond3 = yr > b * np.sqrt(1 - xr ** 2)  # above terminator
    img_day_occ = np.zeros_like(xpt)
    img_day_occ[cond1 & cond2 & cond3] = 1
    img_night_occ = np.zeros_like(xpt)
    img_night_occ[cond1 & cond2 & ~cond3] = 1
    img_night = np.zeros_like(xpt)
    img_night[~cond1 & cond2 & ~cond3] = 1

    # Plot
    if len(lam):
        fig, ax = plt.subplots(1, 3, figsize=(14, 5))
        fig.subplots_adjust(left=0.025, right=0.975, bottom=0.05, top=0.825)
        ax[0].set_title("T", color="r")
        ax[1].set_title("P", color="r")
        ax[2].set_title("Q", color="r")
    else:
        fig, ax = plt.subplots(1, 2, figsize=(9, 5))
        fig.subplots_adjust(left=0.025, right=0.975, bottom=0.05, top=0.825)
        ax[0].set_title("T", color="r")
        ax[1].set_title("P", color="r")

    # Labels
    for i in range(len(phi)):
        ax[0].annotate(
            r"$\xi_{} = {:.1f}^\circ$".format(i + 1, xi[i] * 180 / np.pi),
            xy=(0, 0),
            xycoords="axes fraction",
            xytext=(5, 25 - i * 20),
            textcoords="offset points",
            fontsize=10,
            color="C0",
        )
        ax[1].annotate(
            r"$\phi_{} = {:.1f}^\circ$".format(i + 1, phi[i] * 180 / np.pi),
            xy=(0, 0),
            xycoords="axes fraction",
            xytext=(5, 25 - i * 20),
            textcoords="offset points",
            fontsize=10,
            color="C0",
        )
    for i in range(len(lam)):
        ax[2].annotate(
            r"$\lambda_{} = {:.1f}^\circ$".format(i + 1, lam[i] * 180 / np.pi),
            xy=(0, 0),
            xycoords="axes fraction",
            xytext=(5, 25 - i * 20),
            textcoords="offset points",
            fontsize=10,
            color="C0",
        )

    # Draw basic shapes
    for axis in ax:
        axis.axis("off")
        axis.add_artist(plt.Circle((0, bo), ro, fill=False))
        axis.add_artist(plt.Circle((0, 0), 1, fill=False))
        axis.plot(x_t, y_t, "k-", lw=1)
        axis.set_xlim(-1.25, 1.25)
        axis.set_ylim(-1.25, 1.25)
        axis.set_aspect(1)
        axis.imshow(
            img_day_occ,
            origin="lower",
            extent=(-1, 1, -1, 1),
            alpha=0.25,
            cmap=LinearSegmentedColormap.from_list("cmap1", [(0, 0, 0, 0), "k"], 2),
        )
        axis.imshow(
            img_night_occ,
            origin="lower",
            extent=(-1, 1, -1, 1),
            alpha=0.5,
            cmap=LinearSegmentedColormap.from_list("cmap1", [(0, 0, 0, 0), "k"], 2),
        )
        axis.imshow(
            img_night,
            origin="lower",
            extent=(-1, 1, -1, 1),
            alpha=0.75,
            cmap=LinearSegmentedColormap.from_list("cmap1", [(0, 0, 0, 0), "k"], 2),
        )

    # Draw integration paths
    if len(phi):
        for k in range(0, len(phi) // 2 + 1, 2):

            # T
            # This is the *actual* angle along the ellipse
            xi_p = np.arctan(np.abs(b) * np.tan(xi))
            xi_p[xi_p < 0] += np.pi
            if np.abs(b) < 1e-4:
                ax[0].plot(
                    [np.cos(xi[k]) * np.cos(theta), np.cos(xi[k + 1]) * np.cos(theta),],
                    [np.cos(xi[k]) * np.sin(theta), np.cos(xi[k + 1]) * np.sin(theta),],
                    color="r",
                    lw=2,
                    zorder=3,
                )
            else:
                if xi_p[k] > xi_p[k + 1]:
                    # TODO: CHECK ME
                    xi_p[[k, k + 1]] = xi_p[[k + 1, k]]
                arc = Arc(
                    (0, 0),
                    2,
                    2 * np.abs(b),
                    theta * 180 / np.pi,
                    np.sign(b) * xi_p[k + 1] * 180 / np.pi,
                    np.sign(b) * xi_p[k] * 180 / np.pi,
                    color="r",
                    lw=2,
                    zorder=3,
                )
                ax[0].add_patch(arc)

            # P
            arc = Arc(
                (0, bo),
                2 * ro,
                2 * ro,
                0,
                phi[k] * 180 / np.pi,
                phi[k + 1] * 180 / np.pi,
                color="r",
                lw=2,
                zorder=3,
            )
            ax[1].add_patch(arc)

    if len(lam):

        # Q
        arc = Arc(
            (0, 0),
            2,
            2,
            0,
            lam[0] * 180 / np.pi,
            lam[1] * 180 / np.pi,
            color="r",
            lw=2,
            zorder=3,
        )
        ax[2].add_patch(arc)

    # Draw axes
    ax[0].plot(
        [-np.cos(theta), np.cos(theta)],
        [-np.sin(theta), np.sin(theta)],
        color="k",
        ls="--",
        lw=0.5,
    )
    ax[0].plot([0], [0], "C0o", ms=4, zorder=4)
    ax[1].plot(
        [-ro, ro], [bo, bo], color="k", ls="--", lw=0.5,
    )
    ax[1].plot([0], [bo], "C0o", ms=4, zorder=4)
    if len(lam):
        ax[2].plot(
            [-1, 1], [0, 0], color="k", ls="--", lw=0.5,
        )
        ax[2].plot(0, 0, "C0o", ms=4, zorder=4)

    # Draw points of intersection & angles
    sz = [0.25, 0.5, 0.75, 1.0]
    for i, xi_i in enumerate(xi):

        # -- T --

        # xi angle
        ax[0].plot(
            [0, np.cos(np.sign(b) * xi_i + theta)],
            [0, np.sin(np.sign(b) * xi_i + theta)],
            color="C0",
            lw=1,
        )

        # tangent line
        x0 = np.cos(xi_i) * np.cos(theta)
        y0 = np.cos(xi_i) * np.sin(theta)
        ax[0].plot(
            [x0, np.cos(np.sign(b) * xi_i + theta)],
            [y0, np.sin(np.sign(b) * xi_i + theta)],
            color="k",
            ls="--",
            lw=0.5,
        )

        # mark the polar angle
        ax[0].plot(
            [np.cos(np.sign(b) * xi_i + theta)],
            [np.sin(np.sign(b) * xi_i + theta)],
            "C0o",
            ms=4,
            zorder=4,
        )

        # draw and label the angle arc
        if np.sin(xi_i) != 0:
            angle = sorted([theta, np.sign(b) * xi_i + theta])
            arc = Arc(
                (0, 0),
                sz[i],
                sz[i],
                0,
                angle[0] * 180 / np.pi,
                angle[1] * 180 / np.pi,
                color="C0",
                lw=0.5,
            )
            ax[0].add_patch(arc)
            ax[0].annotate(
                r"$\xi_{}$".format(i + 1),
                xy=(
                    0.5 * sz[i] * np.cos(0.5 * np.sign(b) * xi_i + theta),
                    0.5 * sz[i] * np.sin(0.5 * np.sign(b) * xi_i + theta),
                ),
                xycoords="data",
                xytext=(
                    7 * np.cos(0.5 * np.sign(b) * xi_i + theta),
                    7 * np.sin(0.5 * np.sign(b) * xi_i + theta),
                ),
                textcoords="offset points",
                ha="center",
                va="center",
                fontsize=8,
                color="C0",
            )

        # points of intersection?
        for phi_i in phi:
            x_phi = ro * np.cos(phi_i)
            y_phi = bo + ro * np.sin(phi_i)
            x_xi = np.cos(theta) * np.cos(xi_i) - b * np.sin(theta) * np.sin(xi_i)
            y_xi = np.sin(theta) * np.cos(xi_i) + b * np.cos(theta) * np.sin(xi_i)
            if np.abs(y_phi - y_xi) < tol and np.abs(x_phi - x_xi) < tol:
                ax[0].plot(
                    [ro * np.cos(phi_i)],
                    [bo + ro * np.sin(phi_i)],
                    "C0o",
                    ms=4,
                    zorder=4,
                )

    for i, phi_i in enumerate(phi):

        # -- P --

        # points of intersection
        ax[1].plot(
            [0, ro * np.cos(phi_i)],
            [bo, bo + ro * np.sin(phi_i)],
            color="C0",
            ls="-",
            lw=1,
        )
        ax[1].plot(
            [ro * np.cos(phi_i)], [bo + ro * np.sin(phi_i)], "C0o", ms=4, zorder=4,
        )

        # draw and label the angle arc
        angle = sorted([0, phi_i])
        arc = Arc(
            (0, bo),
            sz[i],
            sz[i],
            0,
            angle[0] * 180 / np.pi,
            angle[1] * 180 / np.pi,
            color="C0",
            lw=0.5,
        )
        ax[1].add_patch(arc)
        ax[1].annotate(
            r"${}\phi_{}$".format("-" if phi_i < 0 else "", i + 1),
            xy=(
                0.5 * sz[i] * np.cos(0.5 * (phi_i % (2 * np.pi))),
                bo + 0.5 * sz[i] * np.sin(0.5 * (phi_i % (2 * np.pi))),
            ),
            xycoords="data",
            xytext=(
                7 * np.cos(0.5 * (phi_i % (2 * np.pi))),
                7 * np.sin(0.5 * (phi_i % (2 * np.pi))),
            ),
            textcoords="offset points",
            ha="center",
            va="center",
            fontsize=8,
            color="C0",
            zorder=4,
        )

    for i, lam_i in zip(range(len(lam)), lam):

        # -- Q --

        # points of intersection
        ax[2].plot(
            [0, np.cos(lam_i)], [0, np.sin(lam_i)], color="C0", ls="-", lw=1,
        )
        ax[2].plot(
            [np.cos(lam_i)], [np.sin(lam_i)], "C0o", ms=4, zorder=4,
        )

        # draw and label the angle arc
        angle = sorted([0, lam_i])
        arc = Arc(
            (0, 0),
            sz[i],
            sz[i],
            0,
            angle[0] * 180 / np.pi,
            angle[1] * 180 / np.pi,
            color="C0",
            lw=0.5,
        )
        ax[2].add_patch(arc)
        ax[2].annotate(
            r"${}\lambda_{}$".format("-" if lam_i < 0 else "", i + 1),
            xy=(0.5 * sz[i] * np.cos(0.5 * lam_i), 0.5 * sz[i] * np.sin(0.5 * lam_i),),
            xycoords="data",
            xytext=(7 * np.cos(0.5 * lam_i), 7 * np.sin(0.5 * lam_i),),
            textcoords="offset points",
            ha="center",
            va="center",
            fontsize=8,
            color="C0",
            zorder=4,
        )

    return fig, ax

