class IndexGroup:
    __slots__ = ["name", "indices"]

    def __init__(self, name, indices=None):
        self.name = name

        if indices is None:
            indices = []
        self.indices = indices

    def __repr__(self):
        return f"{type(self).__name__}({self.name})"


class IndexFile:

    def __init__(self, groups=None):
        if groups is None:
            groups = []
        self.groups = groups

    def read(self, path):
        current_group = None

        with open(path) as ndx_file:
            while True:
                try:
                    line = next(ndx_file)
                except StopIteration:
                    break

                line = line.strip()

                if line.startswith("["):
                    # New index group
                    name = line.strip("[] ")
                    current_group = IndexGroup(name)
                    self.groups.append(current_group)
                    continue

                current_group.indices.extend(
                    [int(i) for i in line.split()]
                    )
