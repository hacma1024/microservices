import random
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

# variable for humidity
hum = [76.69, 76.69, 76.59, 76.69, 76.69, 76.69, 76.69, 76.69, 76.69, 76.59, 76.59, 76.59, 76.59, 76.59, 76.5, 76.5,
       76.5, 76.59, 76.39, 76.39, 76.29, 76.29, 76.39, 76.39, 76.29, 76.29, 76.29, 76.19, 76.19, 76.19, 76.19, 76.19,
       76.19, 76.19, 76.2]
hum_std = [77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77, 77,
           76, 76, 76, 77, 76, 76, 76, 76]

# variable for temperature
tmp = [26.5, 26.5, 26.5, 26.5, 26.5, 26.5, 26.5, 26.5, 26.5, 26.5, 26.5, 26.6, 26.6, 26.6, 26.6, 26.6, 26.6, 26.6, 26.6,
       26.6, 26.7, 26.7,
       25.1, 25.6, 25.6, 25.6, 25.6, 25.6, 25.6, 25.6, 25.6, 25.6, 25.6, 25.6, 26]

tmp_std = [27.1, 27.2, 27.1, 27.2, 26.9, 27.1, 27.1, 27, 27, 27, 27, 27.2, 27.2, 27.2, 27.2, 27.2, 27, 27.3, 27.3, 27.3,
           27.2, 27.2, 26,
           26.4, 26.3, 26.3, 26.3, 26.3, 26.3, 26.3, 26.3, 26.3, 26.3, 26.3, 26.8]

# variable for ph
ph = [8.4, 8.4, 8.4, 8.4, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5, 8.5,
      8.5, 8.5, 8.5, 8.6, 8.6,
      8.6, 8.5, 8.5, 8.5, 8.6, 8.5, 8.6]

quytim = [8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 8, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9, 9]

# variable for uv
uv = [0.1495] * len(hum)
uv_std = [0.15] * len(hum)

t1 = np.arange(0, len(hum), 1)

matplotlib.use('TkAgg')
fig, ((ax1s), (ax2s)) = plt.subplots(2, 2)

ax1s[0].plot(t1, tmp, 'b', t1, tmp_std, 'red')
ax1s[0].legend(['Monitoring value', 'Meter value'])
ax1s[1].plot(t1, hum, 'b', t1, hum_std, 'red')
ax1s[1].legend(['Monitoring value', 'Meter value'])
ax2s[0].plot(t1, ph, 'b', t1, quytim, 'red')
ax2s[0].legend(['Monitoring value', 'Litmus value'])
ax2s[1].plot(t1, uv, 'b', t1, uv_std, 'red')
ax2s[1].legend(['Monitoring value', 'Datasheet '])

ax1s[0].set_ylim([20, 50])
ax1s[0].set_ylabel("($^\degree$C)", rotation='horizontal', ha='right')
ax1s[0].set_xlabel("Number of measurements")

ax1s[1].set_ylim([60, 100])
ax1s[1].set_ylabel("(%)", rotation='horizontal', ha='right')
ax1s[1].set_xlabel("Number of measurements")

ax2s[0].set_ylim([0, 14])
# ax2s[0].set_ylabel("", rotation = 'horizontal', ha = 'right')
ax2s[0].set_xlabel("Number of measurements")

ax2s[1].set_ylim([0.12, 0.18])
# ax2s[1].set_ylabel("", rotation = 'horizontal', ha = 'right')
ax2s[1].set_xlabel("Number of measurements")

ax1s[0].set_title("Temperature")
ax1s[1].set_title("Humidity")
ax2s[0].set_title("pH")
ax2s[1].set_title("UV")

fig.tight_layout()
plt.show()

