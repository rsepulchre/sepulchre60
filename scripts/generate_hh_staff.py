"""Reproducible, deterministic HH simulation and minimalist staff banner.

Run: python generate_hh_staff.py
This is a model illustration, not an experimental recording.
"""
from pathlib import Path
import json
import numpy as np
import scipy
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
from scipy.signal import find_peaks

OUT = Path(__file__).resolve().parent.parent / 'dist' / 'assets'
CM, GNA, GK, GL = 1.0, 120.0, 36.0, 0.3
ENA, EK, EL = 50.0, -77.0, -54.3
T_STOP, DT = 100.0, 0.005
# Identical stimulus translated 33.49 ms later to center the spike in a wider
# time window. This changes neither the HH parameters nor the waveform.
PULSE_START, PULSE_END, PULSE_AMP = 47.49, 48.49, 10.0


def vtrap(x, y):
    z = x / y
    return y * (1 - z / 2 + z*z / 12) if abs(z) < 1e-6 else x / np.expm1(z)


def rates(v):
    return np.array([
        0.1 * vtrap(-(v + 40), 10),
        4 * np.exp(-(v + 65) / 18),
        0.07 * np.exp(-(v + 65) / 20),
        1 / (np.exp(-(v + 35) / 10) + 1),
        0.01 * vtrap(-(v + 55), 10),
        0.125 * np.exp(-(v + 65) / 80),
    ])


def steady_gates(v):
    am, bm, ah, bh, an, bn = rates(v)
    return np.array([am/(am+bm), ah/(ah+bh), an/(an+bn)])


def rhs(t, state, current):
    v, m, h, n = state
    am, bm, ah, bh, an, bn = rates(v)
    ina = GNA*m**3*h*(v-ENA)
    ik = GK*n**4*(v-EK)
    il = GL*(v-EL)
    return [(current-ina-ik-il)/CM,
            am*(1-m)-bm*m, ah*(1-h)-bh*h, an*(1-n)-bn*n]


rest = brentq(lambda v: rhs(0, [v, *steady_gates(v)], 0)[0], -70, -60,
              xtol=1e-13)
initial_state = np.array([rest, *steady_gates(rest)])
times = np.linspace(0, T_STOP, round(T_STOP/DT)+1)


def solve(max_step):
    states = np.empty((4, len(times)))
    state = initial_state.copy()
    for a, b, current in [(0, PULSE_START, 0),
                           (PULSE_START, PULSE_END, PULSE_AMP),
                           (PULSE_END, T_STOP, 0)]:
        sol = solve_ivp(lambda t, y: rhs(t, y, current), [a, b], state,
                        method='DOP853', rtol=1e-10, atol=1e-12,
                        max_step=max_step, dense_output=True)
        assert sol.success, sol.message
        mask = (times >= a) & (times <= b)
        states[:, mask] = sol.sol(times[mask])
        state = sol.y[:, -1]
    return states


states = solve(0.025)
verification_states = solve(0.0125)
voltage = states[0]
peaks, _ = find_peaks(voltage, height=0)
assert len(peaks) == 1, f'Expected one action potential, got {len(peaks)}'
assert np.all((states[1:] >= 0) & (states[1:] <= 1)), 'Gating probability bounds'
error = float(np.max(np.abs(states[0] - verification_states[0])))
assert error < 1e-5, error
current = np.where((times >= PULSE_START) & (times < PULSE_END), PULSE_AMP, 0)
np.savetxt(OUT/'hh-trace.csv', np.column_stack((times, voltage,
           states[1:].T, current)), delimiter=',', fmt='%.16g', comments='',
           header='time_ms,voltage_mV,m,h,n,injected_current_uA_per_cm2')

# Both coordinates are affine transforms of the simulation. No shape editing.
def crossing_width(level):
    """Width between interpolated rising/falling crossings around the AP peak."""
    p = peaks[0]
    left = np.flatnonzero(voltage[:p] < level)[-1]
    right = p + np.flatnonzero(voltage[p:] < level)[0]
    start = np.interp(level, voltage[left:left+2], times[left:left+2])
    end = np.interp(level, voltage[right-1:right+1][::-1], times[right-1:right+1][::-1])
    return float(end-start)

half_height_width = crossing_width(rest + (voltage[peaks[0]]-rest)/2)
main_width = crossing_width(rest + 5.0)
WIDTH, HEIGHT = 1000, 86
X0, X1, BASE_Y, MV_TO_PX = 4, 996, 64, 0.52
points = np.column_stack((X0 + times/T_STOP*(X1-X0),
                          BASE_Y - (voltage-rest)*MV_TO_PX))


def simplify(p, tolerance=0.02):
    """Ramer-Douglas-Peucker in SVG coordinates, tolerance in pixels."""
    if len(p) <= 2:
        return p
    d = p[-1]-p[0]
    # Distance to the finite line segment, not its unbounded supporting line.
    s = np.clip((p-p[0]) @ d / (d @ d), 0, 1)
    dist = np.linalg.norm(p-(p[0]+s[:, None]*d), axis=1)
    i = int(np.argmax(dist))
    if dist[i] <= tolerance:
        return np.stack((p[0], p[-1]))
    return np.vstack((simplify(p[:i+1], tolerance)[:-1],
                      simplify(p[i:], tolerance)))


plot_points = simplify(points)
path = 'M' + ' L'.join(f'{x:.3f},{y:.3f}' for x, y in plot_points)
staff = '\n'.join(f'    <path d="M4 {y}H996"/>' for y in [24,34,44,54,64])
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="86" viewBox="0 0 1000 86" role="img" aria-labelledby="title desc">
  <title id="title">Hodgkin–Huxley action potential on a musical staff</title>
  <desc id="desc">A single numerically simulated Hodgkin–Huxley action potential at 6.3 degrees Celsius, drawn in dark blue across five light gray staff lines. The horizontal span is 100 milliseconds, with a single spike centered near 50 milliseconds. Illustrative model simulation, not experimental data.</desc>
  <g fill="none" stroke="#d9dfe5" stroke-width="0.7">
{staff}
  </g>
  <path d="{path}" fill="none" stroke="#253e59" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
'''
(OUT/'hh-staff.svg').write_text(svg)
metadata = {
    'title': 'Hodgkin–Huxley spike on a five-line musical staff',
    'data_type': 'Illustrative deterministic numerical simulation; not an experimental recording',
    'model': 'Classical space-clamped squid-axon Hodgkin–Huxley model (1952), modern inside-minus-outside voltage convention used by NEURON hh.mod',
    'temperature_degC': 6.3,
    'q10_rate_factor': 1.0,
    'units': {'time': 'ms', 'voltage': 'mV', 'capacitance_density': 'uF/cm^2',
              'conductance_density': 'mS/cm^2', 'current_density': 'uA/cm^2',
              'gating_variables': 'dimensionless'},
    'parameters': {'C_m': CM, 'g_Na_max': GNA, 'g_K_max': GK, 'g_L': GL,
                   'E_Na': ENA, 'E_K': EK, 'E_L': EL},
    'equations': {
        'membrane': 'C_m*dV/dt = I_inj - g_Na_max*m^3*h*(V-E_Na) - g_K_max*n^4*(V-E_K) - g_L*(V-E_L)',
        'gate': 'dx/dt = alpha_x(V)*(1-x)-beta_x(V)*x, x in {m,h,n}',
        'alpha_m': '0.1*(V+40)/(1-exp(-(V+40)/10))',
        'beta_m': '4*exp(-(V+65)/18)',
        'alpha_h': '0.07*exp(-(V+65)/20)',
        'beta_h': '1/(exp(-(V+35)/10)+1)',
        'alpha_n': '0.01*(V+55)/(1-exp(-(V+55)/10))',
        'beta_n': '0.125*exp(-(V+65)/80)',
        'rate_units': '1/ms',
        'singularities': 'Removable singularities in alpha_m at -40 mV and alpha_n at -55 mV evaluated by their continuous limits.'
    },
    'initial_condition': {'method': 'Zero-current equilibrium solved by Brent root finding; gates initialized at alpha/(alpha+beta)',
                          'V_mV': float(rest), 'm': float(initial_state[1]),
                          'h': float(initial_state[2]), 'n': float(initial_state[3])},
    'stimulus': {'type': 'single rectangular depolarizing current-density pulse',
                 'amplitude_uA_per_cm2': PULSE_AMP, 'start_ms': PULSE_START,
                 'end_ms_exclusive': PULSE_END, 'otherwise_uA_per_cm2': 0,
                 'note': 'Illustrative stimulus selected for this banner, not a claimed reproduction of a particular experiment.'},
    'numerics': {'solver': 'scipy.integrate.solve_ivp DOP853', 'scipy_version': scipy.__version__,
                 'rtol': 1e-10, 'atol': 1e-12, 'max_step_ms': 0.025,
                 'integration': 'Three segments ending exactly at stimulus discontinuities',
                 'output_interval_ms': DT, 'time_range_ms': [0,T_STOP], 'output_rows': len(times)},
    'validation': {'spikes_with_peak_above_0_mV': len(peaks),
                   'peak_voltage_mV': float(voltage[peaks[0]]),
                   'peak_time_ms': float(times[peaks[0]]),
                   'minimum_voltage_mV': float(voltage.min()),
                   'width_at_half_height_above_rest_ms': half_height_width,
                   'width_above_rest_plus_5_mV_ms': main_width,
                   'width_at_half_height_above_rest_px': half_height_width*(X1-X0)/T_STOP,
                   'width_above_rest_plus_5_mV_px': main_width*(X1-X0)/T_STOP,
                   'gating_variables_within_0_1': True,
                   'max_voltage_difference_mV_when_max_step_halved': error},
    'rendering': {'size_px': [WIDTH,HEIGHT], 'background': 'transparent',
                  'staff_lines_y_px': [24,34,44,54,64], 'staff_color': '#d9dfe5',
                  'trace_color': '#253e59', 'staff_stroke_px': 0.7,
                  'trace_stroke_px': 1.5, 'visible_text': False,
                  'mapping': f'x = {X0} + time_ms/{T_STOP}*{X1-X0}; y = {BASE_Y} - (voltage_mV-({rest}))*{MV_TO_PX}',
                  'coordinate_mapping': 'Linear in both time and voltage',
                  'revision': {
                      'prior_window_ms': 40.0,
                      'current_window_ms': T_STOP,
                      'horizontal_waveform_scale_relative_to_prior': 40.0/T_STOP,
                      'stimulus_translation_ms': PULSE_START-14.0,
                      'reason': 'Sharper and narrower visual spike by expanding the time window while centering the action potential. No waveform reshaping or nonuniform time warping.',
                      'unchanged': ['HH conductances, reversals, capacitance, temperature, gating kinetics', '1 ms stimulus duration and 10 uA/cm^2 amplitude', '0.52 px per mV vertical scale', 'five staff positions and colors'],
                      'trace_stroke_change_px': [1.75, 1.5]
                  },
                  'path_simplification': 'Ramer-Douglas-Peucker, maximum geometric error 0.02 SVG pixels before 0.001 pixel coordinate rounding',
                  'path_vertices': len(plot_points)},
    'sources': [
        {'title': 'Hodgkin and Huxley (1952). A quantitative description of membrane current and its application to conduction and excitation in nerve. J Physiol 117:500–544.',
         'url': 'https://doi.org/10.1113/jphysiol.1952.sp004764',
         'role': 'Original primary publication'},
        {'title': 'NEURON official hh.mod source',
         'url': 'https://raw.githubusercontent.com/neuronsimulator/nrn/master/src/nrnoc/hh.mod',
         'role': 'Verified voltage convention, six gating rates, sodium/potassium/leak conductances, leak reversal, and temperature scaling',
         'accessed': '2026-09-13'},
        {'title': 'Oberlin College NEURON tutorial: building a basic soma',
         'url': 'https://www2.oberlin.edu/octet/HowTo/NEURON/A1_MyFirstNeuon.html',
         'role': 'Institutional implementation documentation confirming NEURON HH sodium and potassium reversal defaults (+50 and -77 mV)',
         'accessed': '2026-09-13'}
    ],
    'files': {'banner': 'hh-staff.svg', 'sampled_data': 'hh-trace.csv',
              'reproducible_code': '../../scripts/generate_hh_staff.py', 'preview': 'hh_spike_staff_preview.png'}
}
(OUT/'hh-model.json').write_text(json.dumps(metadata, indent=2, ensure_ascii=False)+'\n')

# Rasterize the actual SVG for inspection; this is a preview, not the source.
import fitz
doc = fitz.open(stream=svg.encode(), filetype='svg')
doc[0].get_pixmap(matrix=fitz.Matrix(2,2), alpha=False).save(OUT/'hh_spike_staff_preview.png')
assert main_width*(X1-X0)/T_STOP < 60, 'Spike body must stay narrower than 60 px'
print(json.dumps(metadata['validation'], indent=2))
print(f'SVG vertices: {len(plot_points)}; SVG bytes: {len(svg.encode())}')
