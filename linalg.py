from array import array


class Vector:

    def __init__(self, components):
        self.components = array('d', components)

    def __len__(self):
        return len(self.components)

    def __getitem__(self, key):
        if isinstance(key, slice):
            cls = type(self)
            return cls(self.components[key])
        return self.components[key]

    def __setitem__(self, key, value):
        self.components[key] = value

    def __repr__(self):
        components = repr(self.components)[repr(self.components).find('[') + 1: repr(self.components).find(']')]
        return f'Vector({components})'

    def __str__(self):
        return repr(self)

    def __iter__(self):
        return iter(self.components)

    def __add__(self, other):  # 벡터의 덧셈
        if other == 0:
            return self
        try:
            pairs = zip(self.components, other.components)
            return Vector(a + b for a, b in pairs)
        except TypeError:
            return NotImplemented

    def __radd__(self, other):
        return self + other

    def __mul__(self, scalar):  # 벡터의 스칼라 곱
        try:
            factor = float(scalar)
        except TypeError:
            return NotImplemented
        return Vector(n * factor for n in self)

    def __rmul__(self, scalar):
        return self * scalar

    def __pos__(self):
        return Vector(self)

    def __neg__(self):
        return Vector(-x for x in self)

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return -self + other

    def transpose(self):
        return Matrix(self)


class Matrix:
    def __init__(self, mtx):
        self.rows_num = len(mtx)
        self.cols_num = len(mtx[0])
        self.rows = [Vector(row) for row in mtx]
        self.cols = [Vector([row[i] for row in mtx]) for i in range(self.cols_num)]
        self.components = array('d', [i for row in self.rows for i in row])
        self.size = (self.rows_num, self.cols_num)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            r, c = key
            if isinstance(r, slice):
                if isinstance(c, slice):
                    return Matrix([Vector([row[i] for row in self.rows[r]]) for i in range(self.cols_num)[c]])
                else:
                    return Vector([row[c] for row in self.rows[r]])
            elif isinstance(c, slice):
                return Vector([col[r] for col in self.cols[c]])
            else:
                return self.cols[c][r]

        elif isinstance(key, int):
            return self.cols[key]

    def __setitem__(self, key, value):
        r, c = key
        self.cols[c][r] = value
        self.rows[r][c] = value
        self.components[self.rows_num * r + c] = value

    def __repr__(self):
        s = ('{:8.3f}' * self.cols_num + '\n') * self.rows_num
        return ('Matrix(\n' + s + ')').format(*self.components)

    def __str__(self):
        return repr(self)

    def __add__(self, other):
        if other == 0:
            return self
        if self.rows_num == other.rows_num and self.cols_num == other.cols_num:
            return Matrix([i + j for i, j in zip(self.cols, other.cols)])
        else:
            raise NotImplementedError

    def __radd__(self, other):
        return self + other

    def __mul__(self, scalar):
        try:
            factor = float(scalar)
        except TypeError:
            return NotImplemented
        for i in range(len(self.components)):
            self.components[i] *= factor
        for i in range(self.rows_num):
            for j in range(self.cols_num):
                self.rows[i][j] *= factor
                self.cols[j][i] *= factor

        return self

    def __rmul__(self, other):
        return self * other

    def transpose(self):
        return Matrix(self.cols)

    def trace(self):
        if self.rows_num != self.cols_num:
            raise ValueError
        tr = 0

        for i in range(self.rows_num):
            tr += self[i, i]
        return tr