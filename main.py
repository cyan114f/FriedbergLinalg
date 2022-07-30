
from array import array
import math
import time
import sys

sys.setrecursionlimit(500000)
start = time.time()


class Vector:
    typecode = 'd'

    def __init__(self, components):
        self.components = array(self.typecode, components)

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

    def __abs__(self):
        square_sum = 0
        for i in self.components:
            square_sum += i ** 2
        return square_sum ** 0.5

    def __iter__(self):
        return iter(self.components)

    def __mul__(self, scalar):
        try:
            factor = float(scalar)
        except TypeError:
            return NotImplemented
        return Vector(n * factor for n in self)

    def __rmul__(self, scalar):
        return self * scalar

    def __add__(self, other):
        if other == 0:
            return self
        try:
            pairs = zip(self.components, other.components)
            return Vector(a + b for a, b in pairs)
        except TypeError:
            return NotImplemented

    def __radd__(self, other):
        return self + other

    def __neg__(self):
        return Vector(-x for x in self)

    def __pos__(self):
        return Vector(self)

    def __bool__(self):
        return bool(abs(self))

    def __sub__(self, other):
        return self + -other

    def __rsub__(self, other):
        return -self + other

    def normalized(self):
        return self * (1 / abs(self))


class Matrix:
    typecode = 'd'

    def __init__(self, mtx):
        self.rows_num = len(mtx[0])
        self.cols_num = len(mtx)
        self.rows = [Vector([col[i] for col in mtx]) for i in range(self.rows_num)]
        self.cols = [Vector(col) for col in mtx]
        if not (all(len(self.rows[i]) == len(self.rows[0]) for i in range(self.rows_num)) or len(self.cols[i]) == len(
                self.cols[0]) for i in range(self.cols_num)):
            raise NotImplementedError
        self.components = array(self.typecode, [i for row in self.rows for i in row])
        self.size = (self.rows_num, self.cols_num)

    def __iter__(self):
        return iter(self.cols)

    def __len__(self):
        return len(self.cols)

    def __repr__(self):
        s = ('{:8.3f}' * self.cols_num + '\n') * self.rows_num
        return ('Matrix(\n' + s + ')').format(*self.components)

    def __add__(self, other):
        if other == 0:
            return self
        if self.rows_num == other.rows_num and self.cols_num == other.cols_num:
            return Matrix([i + j for i, j in zip(self.cols, other.cols)])
        else:
            raise NotImplementedError

    def __radd__(self, other):
        return self + other

    def __str__(self):
        return repr(self)

    def transpose(self):
        return Matrix(self.rows)

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

    @staticmethod
    def identity(size):
        return Matrix([Vector([delta(i, j) for i in range(size)]) for j in range(size)])

    @staticmethod
    def elementary_row_swap(size, r1, r2):
        mtx = Matrix([Vector([delta(i, j) for i in range(size)]) for j in range(size)])
        mtx[r1, r1] = 0
        mtx[r2, r2] = 0
        mtx[r1, r2] = 1
        mtx[r2, r1] = 1
        return mtx

    @staticmethod
    def elementary_scalar_multiplication(size, r, scalar):
        mtx = Matrix.identity(size)
        mtx[r, r] *= scalar
        return mtx

    @staticmethod
    def elementary_row_sum(size, r1, r2, scalar):
        mtx = Matrix.identity(size)
        mtx[r2, r1] = scalar
        return mtx

    def is_square(self):
        if self.rows_num == self.cols_num:
            return True
        else:
            return False


def square(mtx, r):
    m = mtx
    for _ in range(r - 1):
        m = dot(m, mtx)
    return m


def delta(i, j):
    if i == j:
        return 1
    else:
        return 0


class BlockMatrix:

    def __init__(self, components):
        self.mtx_rows_num = len(components)
        self.mtx_cols_num = len(components[0])
        self.rows = [components[i] for i in range(self.mtx_rows_num)]
        self.cols = [[components[i][j] for i in range(self.mtx_rows_num)] for j in range(self.mtx_cols_num)]
        for row in self.rows:
            for mtx in row:
                if mtx.size[0] == row[0].size[0]:
                    continue
                else:
                    raise NotImplementedError
        for col in self.cols:
            for mtx in col:
                if mtx.size[1] == col[0].size[1]:
                    continue
                else:
                    raise NotImplementedError

        self.size = (self.mtx_rows_num, self.mtx_cols_num)
        self.whole_size = (sum(i.size[0] for i in self.cols[0]), sum(i.size[1] for i in self.rows[0]))
        self.components = []
        for mtx_row in self.rows:
            for i in range(mtx_row[0].size[0]):
                for mtx in mtx_row:
                    for j in mtx.rows[i]:
                        self.components.append(j)

    def __repr__(self):
        s = ''
        last_row = self.rows[-1]
        for row in self.rows:
            for _ in range(row[0].size[0]):
                for col in self.cols:
                    s += '{:8.3f}' * col[0].size[1] + '|'
                s = s[:-1] + '\n'
            if row != last_row:
                s += '-' * (8 * self.whole_size[1] + self.size[1] - 1) + '\n'
        return ('BlockMatrix(\n' + s + ')').format(*self.components)

    def __str__(self):
        return repr(self)

    def tomatrix(self):
        mtx = []
        for i in range(self.whole_size[0]):
            mtx.append(Vector(self.components[i * self.whole_size[1]:(i + 1) * self.whole_size[1]]))
        return Matrix(mtx).transpose()


def dot(a, b):
    if isinstance(a, Vector) and isinstance(b, Vector):
        return sum(i * j for i, j in zip(a.components, b.components))
    elif isinstance(a, Matrix) and isinstance(b, Vector):
        return sum(i * j for i, j in zip(a, b))
    elif isinstance(a, Matrix) and isinstance(b, Matrix):
        return Matrix([dot(a, col) for col in b.cols])
    elif isinstance(a, BlockMatrix) and isinstance(b, BlockMatrix):
        return BlockMatrix(
            [[sum([dot(i, j) for i, j in zip(a.rows[k], b.cols[l])]) for l in range(b.mtx_cols_num)] for k in
             range(a.mtx_rows_num)])
    else:
        raise NotImplementedError


def angle(v1, v2):
    return math.acos(dot(v1, v2) / (abs(v1) * abs(v2)))


mtx1 = Matrix([[2, 1], [-3, 5], [1, -2]])
mtx2 = Matrix([[0, 3], [-4, -1]])
mtx3 = Matrix([[0], [-4], [-2]])
mtx4 = Matrix([[7], [-1]])
mtx5 = Matrix([[6, -2, -3], [4, 1, 7]])
mtx6 = Matrix([[-1, 5], [3, 2]])
m1 = BlockMatrix([[mtx1, mtx2], [mtx3, mtx4]])
m2 = BlockMatrix([[mtx5], [mtx6]])
mtx7 = Matrix([[1, 1], [0, 1]])
# m3 = dot(m1, m2)
# print(dot(m1, m2))
# print(dot(m1.tomatrix(), m2.tomatrix()))
print(square(mtx7, 10000).components)
print(f"{time.time() - start:.20f} sec")
