"""Independent verification of the thesis' Chapter 4 growth calculations (Python, 2026).

Reproduces the closed-form approximations evaluated in Maple in the 2008 thesis and
compares them with the exact linear growing mode for a universe with matter,
curvature and a cosmological constant (Heath 1977 integral solution).

Usage:  python scripts/make_figures.py
Writes: figures/*.png and results/verification.json
"""
import json, os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, TwoSlopeNorm
from scipy.integrate import quad

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(ROOT); os.makedirs('figures', exist_ok=True); os.makedirs('results', exist_ok=True)

# ---------------------------------------------------------------- physics
def f_thesis(m, l):  # growth rate as evaluated in the thesis (exponent 4/7)
    return m**(4/7) + l/70*(1 + m/2)
def f_lahav(m, l):   # Lahav et al. (1991) form with exponent 0.6, eq. (4-20) as printed
    return m**0.6 + l/70*(1 + m/2)
def g_cpt(m, l):     # Carroll, Press & Turner (1992) growth-suppression factor, eq. (4-21)
    return 2.5*m/(m**(4/7) - l + (1 + m/2)*(1 + l/70))
def E2(a, m, l):     # H^2/H0^2 for matter + curvature + Lambda
    return m/a**3 + (1 - m - l)/a**2 + l
def growth(a, m, l):
    """Exact growing mode D(a) (normalised D -> a early) and f = dlnD/dlna (Heath 1977)."""
    I = quad(lambda x: (x*np.sqrt(E2(x, m, l)))**-3, 0, a, limit=200)[0]
    e2 = E2(a, m, l); E = np.sqrt(e2)
    D = 2.5*m*E*I
    dlnE = (-3*m/a**3 - 2*(1 - m - l)/a**2)/(2*e2)
    return D, dlnE + 1/(a**2*E**3*I), m/a**3/e2   # D, f, Omega_m(a)
def age(m, l):       # H0 * t0
    return quad(lambda a: 1/(a*np.sqrt(E2(a, m, l))), 0, 1, limit=200)[0]

# ---------------------------------------------------------------- style
SURF='#fcfcfb'; INK='#0b0b0b'; INK2='#52514e'; MUTED='#898781'; GRID='#e1e0d9'; AXIS='#c3c2b7'
BLUE='#2a78d6'; ORANGE='#eb6834'; AQUA='#1baf7a'; YELLOW='#eda100'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.edgecolor':AXIS,'axes.labelcolor':INK2,
    'xtick.color':MUTED,'ytick.color':MUTED,'text.color':INK,'figure.facecolor':SURF,'axes.facecolor':SURF,
    'savefig.facecolor':SURF,'mathtext.fontset':'dejavusans'})
DIV = LinearSegmentedColormap.from_list('div', ['#184f95','#5598e7','#f0efec','#ec835a','#b02a2a'])
def style(ax, grid='both'):
    for s in ['top','right']: ax.spines[s].set_visible(False)
    if grid: ax.grid(axis=grid, color=GRID, lw=0.6)
    ax.set_axisbelow(True)
def title(fig, t, sub=None):
    fig.text(0.015, 0.985, t, fontsize=12, fontweight='bold', va='top')
    if sub: fig.text(0.015, 0.935, sub, fontsize=8.5, color=INK2, va='top')

res = {}

# ---------------------------------------------------------------- 1. reproduce thesis table
pts = [(0.1,0.7),(0.2,0.7),(0.3,0.7),(0.3,0.85),(0.3,1.0)]
tab = []
for m, l in pts:
    D, f, _ = growth(1, m, l)
    tab.append(dict(Om=m, OL=l, f_thesis=round(f_thesis(m,l),4), f_lahav06=round(f_lahav(m,l),4), f_exact=round(f,4),
                    g_thesis=round(g_cpt(m,l),4), g_exact=round(D,4), H0t0=round(age(m,l),4)))
res['table'] = tab

# ---------------------------------------------------------------- 2. error maps over the thesis grid
Om = np.linspace(0.02, 0.30, 57); OL = np.linspace(0.70, 1.00, 61)
FE = np.zeros((len(OL), len(Om))); GE = np.zeros_like(FE)
for i, l in enumerate(OL):
    for j, m in enumerate(Om):
        GE[i, j], FE[i, j], _ = growth(1, m, l)
M, L = np.meshgrid(Om, OL)
err = {'f_thesis': 100*(f_thesis(M, L)/FE - 1), 'f_lahav06': 100*(f_lahav(M, L)/FE - 1), 'g_thesis': 100*(g_cpt(M, L)/GE - 1)}
res['error_pct'] = {k: dict(min=round(float(v.min()),2), max=round(float(v.max()),2),
                            rms=round(float(np.sqrt((v**2).mean())),2)) for k, v in err.items()}
res['error_pct_Om_ge_0.2'] = {k: dict(max_abs=round(float(np.abs(v[:, Om >= 0.2]).max()),2)) for k, v in err.items()}

# sensitivities (exact vs thesis)
def pct(a, b): return round(100*(b/a - 1), 1)
f03 = [growth(1, 0.3, l)[1] for l in (0.7, 1.0)]; g03 = [growth(1, 0.3, l)[0] for l in (0.7, 1.0)]
fm = [growth(1, m, 0.7)[1] for m in (0.1, 0.3)]; gm = [growth(1, m, 0.7)[0] for m in (0.1, 0.3)]
res['sensitivity_pct'] = {
  'OL_0.7_to_1.0_at_Om_0.3': dict(f_thesis=pct(f_thesis(.3,.7), f_thesis(.3,1)), f_exact=pct(*f03),
                                  g_thesis=pct(g_cpt(.3,.7), g_cpt(.3,1)), g_exact=pct(*g03)),
  'Om_0.1_to_0.3_at_OL_0.7': dict(f_thesis=pct(f_thesis(.1,.7), f_thesis(.3,.7)), f_exact=pct(*fm),
                                  g_thesis=pct(g_cpt(.1,.7), g_cpt(.3,.7)), g_exact=pct(*gm))}

# ---------------------------------------------------------------- 3. history for the fiducial model
z = np.linspace(0, 5, 101)
hist = np.array([growth(1/(1+zz), 0.3, 0.7) for zz in z])
D_z, f_z, om_z = hist[:, 0], hist[:, 1], hist[:, 2]
gam = np.log(f_z)/np.log(om_z)
res['fiducial'] = dict(Om=0.3, OL=0.7, H0t0=round(age(.3,.7),4), t0_Gyr_for_H0_70=round(age(.3,.7)*977.8/70,2),
                       gamma_eff_z0=round(float(gam[0]),4), gamma_eff_z1=round(float(gam[20]),4),
                       gamma_eff_z5=round(float(gam[-1]),4), D0_over_a0=round(float(D_z[0]),4))
json.dump(res, open('results/verification.json', 'w'), indent=2)
print(json.dumps(res, indent=1))

# ================================================================ figures
# F1 Omega_m - Omega_Lambda plane
mm = np.linspace(0.0, 1.0, 201); ll = np.linspace(-0.2, 1.6, 241)
MM, LL = np.meshgrid(mm, ll)
AGE = np.full(MM.shape, np.nan)
mb = np.linspace(0.001, 0.5, 300)
bounce = 4*mb*np.cosh(np.arccosh((1-mb)/mb)/3)**3
for i in range(0, len(ll), 4):
    for j in range(0, len(mm), 4):
        m_, l_ = mm[j], ll[i]
        if m_ < 0.5 and l_ >= 4*max(m_,1e-3)*np.cosh(np.arccosh((1-max(m_,1e-3))/max(m_,1e-3))/3)**3: continue
        if m_ == 0 and l_ >= 1: continue
        try: AGE[i, j] = age(max(m_,1e-3), l_)
        except Exception: pass
fig, ax = plt.subplots(figsize=(7.2, 6.2), dpi=160)
ax.fill_between(mb, bounce, 1.6, color='#f0efec', lw=0)
ax.text(0.04, 1.47, 'No Big Bang\n(bouncing models)', fontsize=9, color=INK2)
ax.plot([0, 1], [1, 0], color=INK, lw=1.4); ax.text(0.47, 0.57, 'Flat (Ω$_k$ = 0)', rotation=-36, fontsize=9, color=INK)
ax.plot([0, 1], [0, 0.5], color=ORANGE, lw=1.4, ls=(0,(4,3)))
ax.text(0.80, 0.56, 'Accelerating today', fontsize=8.5, color=ORANGE, va='center'); ax.text(0.80, 0.27, 'Decelerating today', fontsize=8.5, color=ORANGE, va='center')
ax.text(0.25, -0.12, 'Open', fontsize=9, color=INK2); ax.text(0.85, 0.85, 'Closed', fontsize=9, color=INK2)
cs = ax.contour(MM[::4, ::4], LL[::4, ::4], AGE[::4, ::4], levels=[0.7, 0.8, 0.9, 1.0, 1.2], colors=MUTED, linewidths=0.8)
ax.clabel(cs, fmt=lambda v: f'H₀t₀={v:g}', fontsize=7.5)
ax.add_patch(plt.Rectangle((0, 0.7), 0.3, 0.3, fill=True, facecolor=BLUE, alpha=0.18, edgecolor=BLUE, lw=1.6))
ax.text(0.155, 1.03, 'Thesis grid', color=BLUE, fontsize=9, ha='center', fontweight='bold')
ax.plot(0.3, 0.7, marker='o', ms=8, mfc=YELLOW, mec=SURF, mew=1.5); ax.annotate('Fiducial\n(0.3, 0.7)', (0.3, 0.7), xytext=(10, 6), textcoords='offset points', fontsize=8.5, color=INK2)
ax.set_xlim(0, 1); ax.set_ylim(-0.2, 1.6); ax.set_xlabel('Ω$_M$ (matter)'); ax.set_ylabel('Ω$_Λ$ (cosmological constant)'); style(ax)
title(fig, 'Where the thesis grid sits in the Ω$_M$–Ω$_Λ$ plane', 'Grey contours: age of the universe in units of 1/H₀. Every grid model has a Big Bang and accelerates today.')
fig.tight_layout(rect=(0, 0, 1, 0.91)); fig.savefig('figures/omega_plane.png'); plt.close()

# F2 slices: thesis formula vs exact
sl_m = np.linspace(0.02, 0.3, 57); sl_l = np.linspace(0.7, 1.0, 61)
ex_m = np.array([growth(1, m, 0.7)[:2] for m in sl_m]); ex_l = np.array([growth(1, 0.3, l)[:2] for l in sl_l])
fig, axs = plt.subplots(2, 2, figsize=(9, 6.4), dpi=160)
panels = [(axs[0,0], sl_m, f_thesis(sl_m, .7), ex_m[:,1], 'Ω$_M$', 'f  at Ω$_Λ$ = 0.7'),
          (axs[0,1], sl_l, f_thesis(.3, sl_l), ex_l[:,1], 'Ω$_Λ$', 'f  at Ω$_M$ = 0.3'),
          (axs[1,0], sl_m, g_cpt(sl_m, .7), ex_m[:,0], 'Ω$_M$', 'g  at Ω$_Λ$ = 0.7'),
          (axs[1,1], sl_l, g_cpt(.3, sl_l), ex_l[:,0], 'Ω$_Λ$', 'g  at Ω$_M$ = 0.3')]
for k, (ax, x, ya, ye, xl, tt) in enumerate(panels):
    ax.plot(x, ye, color=ORANGE, lw=2.4, label='Exact (ODE solution)')
    ax.plot(x, ya, color=BLUE, lw=2, ls=(0,(4,2)), label='Thesis formula (Maple)')
    ax.set_xlabel(xl); ax.set_title(tt, loc='left', fontsize=10, color=INK); style(ax)
    if k == 1: ax.set_ylim(0.49, 0.54)
axs[0,0].legend(loc='lower right', facecolor=SURF, edgecolor=GRID, fontsize=8.5)
title(fig, 'Thesis approximations vs. exact linear growth', 'Same slices as thesis Figs. 4-4 to 4-7, with the exact growing mode overlaid.')
fig.tight_layout(rect=(0, 0, 1, 0.91)); fig.savefig('figures/slices_vs_exact.png'); plt.close()

# F3 error maps
fig, axs = plt.subplots(1, 3, figsize=(11, 3.9), dpi=160, sharey=True)
names = [('f_thesis', 'f, exponent 4/7 (thesis)'), ('f_lahav06', 'f, exponent 0.6 (Lahav, as printed)'), ('g_thesis', 'g, Carroll–Press–Turner (thesis)')]
for ax, (k, t) in zip(axs, names):
    v = err[k]; lim = max(abs(v.min()), abs(v.max()))
    im = ax.pcolormesh(Om, OL, v, cmap=DIV, norm=TwoSlopeNorm(0, -lim, lim), shading='auto')
    c = ax.contour(Om, OL, v, levels=[-5, -2, -1, 1, 2, 5], colors=INK2, linewidths=0.6)
    ax.clabel(c, fmt='%g%%', fontsize=7)
    ax.set_title(t, loc='left', fontsize=9.5); ax.set_xlabel('Ω$_M$'); style(ax, None)
    cb = fig.colorbar(im, ax=ax, shrink=0.85, pad=0.02); cb.set_label('error (%)', color=INK2); cb.outline.set_edgecolor(AXIS); cb.ax.tick_params(colors=MUTED)
axs[0].set_ylabel('Ω$_Λ$')
title(fig, 'Relative error of the closed-form approximations over the thesis grid', 'Error = approximation / exact − 1. Red: overestimate, blue: underestimate, grey: within ~0.')
fig.tight_layout(rect=(0, 0, 1, 0.88)); fig.savefig('figures/error_maps.png'); plt.close()

# F4 growth history
fig, (ax, bx) = plt.subplots(1, 2, figsize=(10, 4.2), dpi=160)
ax.plot(z, f_z, color=ORANGE, lw=2.4, label='Exact f(z)')
for gm_, c_, ls_ in [(0.55, BLUE, '-'), (4/7, AQUA, (0,(4,2))), (0.6, YELLOW, (0,(1,1.5)))]:
    ax.plot(z, om_z**gm_, color=c_, lw=1.8, ls=ls_, label=f'Ω$_M$(z)$^{{{gm_:.3g}}}$' if gm_ != 4/7 else 'Ω$_M$(z)$^{4/7}$')
ax.set_xlabel('Redshift z'); ax.set_ylabel('Growth rate f'); ax.legend(facecolor=SURF, edgecolor=GRID, fontsize=8.5, loc='lower right'); style(ax)
ax.set_title('Growth rate approaches 1 in the matter era', loc='left', fontsize=10)
bx.plot(z, D_z*(1+z), color=ORANGE, lw=2.4)
bx.axhline(1, color=MUTED, lw=1, ls=(0,(3,3))); bx.text(4.9, 1.0, 'Einstein–de Sitter (g = 1)', fontsize=8.5, color=INK2, ha='right', va='bottom')
bx.set_xlabel('Redshift z'); bx.set_ylabel('g(z) = D/a'); style(bx); bx.set_ylim(0.7, 1.03)
bx.annotate(f'g today = {D_z[0]:.3f}', (0, D_z[0]), xytext=(12, -4), textcoords='offset points', fontsize=9, color=INK2)
bx.set_title('Λ suppresses growth only at late times', loc='left', fontsize=10)
title(fig, 'Growth history of the fiducial model (Ω$_M$ = 0.3, Ω$_Λ$ = 0.7)')
fig.tight_layout(rect=(0, 0, 1, 0.93)); fig.savefig('figures/growth_history.png'); plt.close()

# F5 growth index
fig, ax = plt.subplots(figsize=(7.2, 3.8), dpi=160)
ax.plot(z, gam, color=ORANGE, lw=2.4)
for v, lab in [(4/7, 'γ = 4/7 ≈ 0.571 (thesis)'), (0.55, 'γ = 0.55 (Linder 2005)'), (0.6, 'γ = 0.6 (Lahav et al. 1991)')]:
    ax.axhline(v, color=MUTED, lw=1, ls=(0,(3,3))); ax.text(5, v, lab+' ', fontsize=8.5, color=INK2, ha='right', va='bottom')
ax.set_xlabel('Redshift z'); ax.set_ylabel('γ$_{eff}$ = ln f / ln Ω$_M$(z)'); style(ax, 'y'); ax.set_ylim(0.53, 0.61)
ax.annotate(f'Exact: {gam[0]:.3f} today', (0, gam[0]), xytext=(10, 10), textcoords='offset points', fontsize=9, color=INK2)
title(fig, 'Effective growth index of the exact solution', 'If f = Ω$_M$(z)$^γ$ held exactly, the orange curve would be flat.')
fig.tight_layout(rect=(0, 0, 1, 0.89)); fig.savefig('figures/growth_index.png'); plt.close()
