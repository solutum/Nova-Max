def read_lines_from_file(filename, start_line, num_lines):
	lines = []
	with open(filename, 'r') as file:
		# Пропустити перші (start_line - 1) рядків
		for _ in range(start_line - 1):
			next(file)
		# Прочитати наступні num_lines рядків
		for _ in range(num_lines):
			line = file.readline().strip()
			if not line:
				break
			lines.append(line)
	return lines


def write_list_to_file(data_list, file_name):
	with open(file_name, 'a') as file:
		line = ', '.join(map(str, data_list)) + '\n'
		file.write(line)


def prepare_sdr_data(sdr_data):
	prepared_data = []

	# Розділення першого елемента datetime на дві частини
	date_part, time_part = sdr_data[0]['datetime'].split(' ')
	# time_part = time_part[:-7]

	dbi_list = [entry['dbi'] for entry in sdr_data]

	# Отримання першого та останнього значення frequency
	first_frequency = float(sdr_data[0]['frequency']) * 10
	last_frequency = float(sdr_data[-1]['frequency']) * 10

	prepared_data.append(date_part)
	prepared_data.append(time_part)
	prepared_data.append(int(first_frequency))
	prepared_data.append(int(last_frequency))
	prepared_data.append(5)
	prepared_data.append(1)
	prepared_data = prepared_data + dbi_list

	return prepared_data

	