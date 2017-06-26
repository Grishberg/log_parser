# parser
class ResultFilePrinter:
    def __init__(self, log_columns_info):
        self._log_columns_info = log_columns_info

    def write(self, file_name):
        out = ''
        for column_name, calues_array in self._log_columns_info._log_columns._columns.iteritems():
            out += column_name + ':\n'
            out += 'avg = ' + str(self._log_columns_info._columns_sums[column_name]) +', '
            percentiles = self._log_columns_info._percentiles[column_name]
            out += 'perc50 = ' + str(percentiles[0]) + ', '
            out += 'perc75 = ' + str(percentiles[1]) + ', '
            out += 'perc90 = ' + str(percentiles[2]) + '\n'
        self._write_to_file(file_name, out)

    def _write_to_file(self, file_name, out):
        f = open(file_name, 'wb')
        f.write(out)
        f.close()

class LogColumnsInfo:
    def __init__(self, log_columns):
        self._log_columns = log_columns
        self._test_case_count = len(self._log_columns._columns.itervalues().next())
        self._columns_sums = {}
        self._percentiles = {}
        self._calculate_metrics()

    def _calculate_metrics(self):
        for key, values_array in self._log_columns._columns.iteritems():
            self._columns_sums[key] = self._calculate_sum_for_column(values_array)
            self._percentiles[key] = self._calculate_percentiles(values_array)

    def _calculate_sum_for_column(self, values_array):
        return float(sum(values_array)) / float(len(values_array))

    def _calculate_percentiles(self, values_array):
        values_array.sort()
        mid = values_array[len(values_array) / 2]
        perc75 = int(round((len(values_array) - 1) * 0.75))
        perc90 = int(round((len(values_array) -1) * 0.9))
        return mid, values_array[perc75], values_array[perc90]


class LogColumns:
    def __init__(self, file_name):
        self._columns = {}
        self._new_line_column_name = None
        self._folder_name = "logs"
        self.process_log(file_name)

    def _parse_line(self, line):
        lst = line.split(':')
        column_name = lst[2].strip()
        value = int(lst[3][:-3].strip())
        return column_name, value

    def process_log(self, file_name):
        test_cases_count = 0
        lines = self._read_lines_from_file(file_name)
        for line in lines:
            column_name, value = self._parse_line(line)
            array_for_column = self._get_values_array_for_name(column_name)
            array_for_column.append(value)

            if self._is_new_test_case(column_name):
                test_cases_count += 1
        return self._columns

    def _get_values_array_for_name(self, column_name):
        array_for_column = self._columns.get(column_name, None)
        if array_for_column is None:
            array_for_column = []
            self._columns[column_name] = array_for_column
        return array_for_column

    def _is_new_test_case(self, column_name):
        if self._new_line_column_name is None:
            self._new_line_column_name = column_name
        return column_name.find(self._new_line_column_name) >= 0

    def _read_lines_from_file(self, file_name):
        f = open(self._folder_name + "/" + file_name, "rb")
        buf = f.read()
        f.close()
        return buf.split("\n")


log = LogColumns('log_test.log')
metrics = LogColumnsInfo(log)
printer = ResultFilePrinter(metrics)
printer.write('out.csv')
print metrics._columns_sums
print metrics._percentiles
