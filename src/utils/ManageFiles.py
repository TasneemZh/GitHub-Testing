import csv
import json


class ManageFiles:
    writer = None
    writer_name = None
    constants = {}

    @staticmethod
    def read_from_json(file_name):
        config_file = open("./" + file_name + ".json")
        return json.load(config_file)

    def read_from_csv(self, file_name, storage_type):
        input_list = []
        with open("./resources/files/" + file_name + ".csv", "rt") as file:
            reader = csv.reader(file)
            next(reader) if storage_type != "dictionary" else None
            match storage_type:
                case "unpack":
                    for row in reader:
                        input_list.append([row[0], row[1], row[2], row[3], row[4], row[5], row[6]])
                case "dictionary":
                    for row in reader:
                        self.constants[row[0]] = row[1]
                case "list":
                    for row in reader:
                        input_list.append([row[0], row[1], row[2]])
                case _:
                    raise RuntimeError("Unsupported storage type!")
            return input_list

    def get_constant_value(self, constant_name):
        return self.constants.get(constant_name)

    def open_writer_csv(self, file_name, headers_name):
        with open("./resources/files/" + file_name + ".csv", "w", newline='') as file:
            self.writer_name = file_name
            self.writer = csv.writer(file)
            self.writer.writerow(headers_name)

    def write_to_csv(self, csv_data):
        with open("./resources/files/" + self.writer_name + ".csv", "a", newline='') as file:
            self.writer = csv.writer(file)
            self.writer.writerow(csv_data)
