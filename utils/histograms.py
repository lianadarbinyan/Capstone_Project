class Histogram:
    def __init__(self, data, num_bins=100):
        self.data = data
        self.num_bins = num_bins
        self.bins = self._create_histogram()

    def _create_histogram(self):
        min_val = min(self.data)
        max_val = max(self.data)
        bin_size = (max_val - min_val) / self.num_bins
        bins = [0] * self.num_bins

        for value in self.data:
            bin_index = min(int((value - min_val) / bin_size), self.num_bins - 1)
            bins[bin_index] += 1

        return bins

    def get_fraction_greater_than(self, value):
        min_val = min(self.data)
        max_val = max(self.data)
        bin_size = (max_val - min_val) / self.num_bins
        bin_index = min(int((value - min_val) / bin_size), self.num_bins - 1)
        fraction_greater = sum(self.bins[bin_index + 1:]) / len(self.data)
        return fraction_greater

    def get_fraction_less_than(self, value):
        min_val = min(self.data)
        max_val = max(self.data)
        bin_size = (max_val - min_val) / self.num_bins
        bin_index = min(int((value - min_val) / bin_size), self.num_bins - 1)
        fraction_less = sum(self.bins[:bin_index]) / len(self.data)
        return fraction_less

    def get_fraction_equal_to(self, value):
        min_val = min(self.data)
        max_val = max(self.data)
        bin_size = (max_val - min_val) / self.num_bins
        bin_index = min(int((value - min_val) / bin_size), self.num_bins - 1)
        fraction_equal = self.bins[bin_index] / len(self.data)
        return fraction_equal
