# Linear growth rate f and growth factor g in a universe with matter and a cosmological constant.
# Reconstructed from equations (4-20) and (4-21) of the thesis (Chapter 4).
# The original 2008 Maple worksheet is not part of this repository.
#
# Note: equation (4-20) is printed with exponent 0.6 (Lahav et al. 1991), but the values
# reported in the thesis (e.g. f = 0.5142 at Omega_m = 0.3, Omega_Lambda = 0.7) correspond to
# exponent 4/7. Both are defined below.

restart:
with(plots):

f   := (Om, OL) -> Om^(4/7) + OL/70*(1 + Om/2):           # as evaluated in the thesis
f06 := (Om, OL) -> Om^(3/5) + OL/70*(1 + Om/2):           # as printed in eq. (4-20)
g   := (Om, OL) -> 5*Om/(2*(Om^(4/7) - OL + (1 + Om/2)*(1 + OL/70))):

# Figures 4-2 and 4-3: surfaces over the thesis grid
plot3d(f(m, L), m = 0 .. 0.3, L = 0.7 .. 1.0, axes = boxed,
       labels = ["Omega_m", "Omega_Lambda", "f"], title = "Linear growth rate f");
plot3d(g(m, L), m = 0 .. 0.3, L = 0.7 .. 1.0, axes = boxed,
       labels = ["Omega_m", "Omega_Lambda", "g"], title = "Linear growth factor g");

# Figures 4-4 to 4-7: one-dimensional slices
plot(f(m, 0.7), m = 0 .. 0.3, labels = ["Omega_m", "f"], title = "f at Omega_Lambda = 0.7");
plot(f(0.3, L), L = 0.7 .. 1.0, labels = ["Omega_Lambda", "f"], title = "f at Omega_m = 0.3");
plot(g(m, 0.7), m = 0 .. 0.3, labels = ["Omega_m", "g"], title = "g at Omega_Lambda = 0.7");
plot(g(0.3, L), L = 0.7 .. 1.0, labels = ["Omega_Lambda", "g"], title = "g at Omega_m = 0.3");

# Values reported in the README
for p in [[0.1, 0.7], [0.2, 0.7], [0.3, 0.7], [0.3, 0.85], [0.3, 1.0]] do
    printf("Omega_m = %.2f  Omega_Lambda = %.2f  f = %.4f  g = %.4f\n",
           p[1], p[2], f(p[1], p[2]), g(p[1], p[2]));
end do;
