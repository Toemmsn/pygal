# -*- coding: utf-8 -*-
# This file is part of pygal
#
# A python svg graph plotting library
# Copyright © 2012-2014 Kozea
#
# This library is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This library is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with pygal. If not, see <http://www.gnu.org/licenses/>.
"""
Dot chart

"""

from __future__ import division
from math import pi
from pygal.graph.graph import Graph
from pygal.adapters import positive
from pygal.util import decorate, cut, safe_enumerate, cached_property


class PieDot(Graph):
    """PieDot graph"""

    _adapters = [positive]

    def dot(self, serie, r_max):
        """Draw a dot line"""
        serie_node = self.svg.serie(serie)
        view_values = list(map(self.view, serie.points))
        for i, values in safe_enumerate(serie.values):
            x, y = view_values[i]
            radius = r_max * values[self.base_value_index]
            value = self._format(values[self.base_value_index])
            metadata = serie.metadata.get(i)
            dots = decorate(
                self.svg,
                self.svg.node(serie_node['plot'], class_="slices"),
                metadata)

            # slices = self.svg.node(serie_node['plot'], class_="slices")
            current_angle = 0
            total = sum(values)
            slice_num = 0
            for slice_value in values:
                slice_color = (serie.index + slice_num) % len(self.style['colors'])
                slice_num += 1
                perc = slice_value / total
                angle = 2 * pi * perc
                slice_ = decorate(
                    self.svg,
                    self.svg.node(dots, class_="slice color-%d" % (slice_color, )),
                    metadata)
                big_radius = radius * .9
                small_radius = radius * serie.inner_radius
                val = '{0:d}'.format(slice_value)
                self.svg.slice(
                    serie_node, slice_, big_radius, small_radius,
                    angle, current_angle, (x, y), val)
                current_angle += angle

            self._tooltip_data(dots, value, x, y, classes='centered')
            self._static_value(serie_node, value, x, y)

    @cached_property
    def _min(self):
        return min([val[0]
                    for serie in self.all_series
                    for val in serie.values
                    if val[0] is not None])

    @cached_property
    def _max(self):
        return max([val[0]
                    for serie in self.all_series
                    for val in serie.values
                    if val[0] is not None])

    def _has_data(self):
        """Check if there is any data"""
        return sum(
            map(len, map(lambda s: s.safe_values, self.series))) != 0

    def _compute(self):
        x_len = self._len
        y_len = self._order
        self._box.xmax = x_len
        self._box.ymax = y_len

        x_pos = [n / 2 for n in range(1, 2 * x_len, 2)]
        y_pos = [n / 2 for n in reversed(range(1, 2 * y_len, 2))]

        for j, serie in enumerate(self.series):
            serie.points = [
                (x_pos[i], y_pos[j])
                for i in range(x_len)]

        self._x_labels = self.x_labels and list(zip(self.x_labels, x_pos))
        self._y_labels = list(zip(
            self.y_labels or cut(self.series, 'title'), y_pos))

    def _plot(self):
        r_max = min(
            self.view.x(1) - self.view.x(0),
            (self.view.y(0) or 0) - self.view.y(1)) / (2 * (self._max or 1) * 1.05)
        for serie in self.series:
            self.dot(serie, r_max)
